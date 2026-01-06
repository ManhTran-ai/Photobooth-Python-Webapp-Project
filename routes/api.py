"""
API routes for photobooth application
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app, url_for
from werkzeug.utils import secure_filename
from models.image_processor import ImageProcessor
from models.filter_engine import FilterEngine
from models.database import db, Session, Photo, FilterApplied
from models.template_engine import TemplateEngine
from datetime import datetime
import os
import uuid
import base64
import io
from PIL import Image

api_bp = Blueprint('api', __name__)

# instantiate a TemplateEngine; output_dir will be adjusted per app config if needed
template_engine = TemplateEngine()


@api_bp.route('/upload', methods=['POST'])
def upload_photo():
    """
    Handle photo upload, processing, and storage
    Expects form data with:
    - photo: image file
    - filter: filter name (optional, defaults to 'none')
    - flip: 'true' or 'false' (optional, defaults to 'true' for front camera)
    """
    try:
        # Check if file was uploaded
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get filter name (default to 'none')
        filter_name = request.form.get('filter', 'none')
        
        # Get flip setting (default to True for front camera)
        flip = request.form.get('flip', 'true').lower() == 'true'
        
        # Read image data
        image_data = file.read()
        
        # Process image with Python
        processed_image = ImageProcessor.process_uploaded_image(
            image_data, 
            filter_name=filter_name, 
            flip_if_front_camera=flip
        )
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f'{timestamp}_{unique_id}.jpg'
        
        # Get app context for folder paths
        from flask import current_app
        
        # Save original
        original_path = os.path.join(
            current_app.config['ORIGINALS_FOLDER'], 
            filename
        )
        ImageProcessor.save_image(
            ImageProcessor.process_uploaded_image(image_data, 'none', False),
            original_path
        )
        
        # Save processed
        processed_path = os.path.join(
            current_app.config['PROCESSED_FOLDER'], 
            filename
        )
        ImageProcessor.save_image(processed_image, processed_path)
        
        # Save thumbnail
        thumbnail_image = ImageProcessor.create_thumbnail(processed_image.copy())
        thumbnail_path = os.path.join(
            current_app.config['THUMBNAILS_FOLDER'], 
            filename
        )
        ImageProcessor.save_image(thumbnail_image, thumbnail_path)
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded and processed successfully',
            'filename': filename,
            'original_url': f'/api/images/originals/{filename}',
            'processed_url': f'/api/images/processed/{filename}',
            'thumbnail_url': f'/api/images/thumbnails/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@api_bp.route('/images/<folder>/<filename>')
def serve_image(folder, filename):
    """
    Serve images from different folders (originals, processed, thumbnails)
    """
    from flask import current_app
    
    valid_folders = ['originals', 'processed', 'thumbnails']
    if folder not in valid_folders:
        return jsonify({'error': 'Invalid folder'}), 400
    
    folder_path = current_app.config[f'{folder.upper()}_FOLDER']
    return send_from_directory(folder_path, filename)


@api_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new 4-photo session"""
    try:
        session_id = str(uuid.uuid4())
        
        new_session = Session(
            id=session_id,
            status='capturing'
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create session: {str(e)}'}), 500


@api_bp.route('/capture', methods=['POST'])
def capture_photo():
    """
    Capture a photo in a session
    Expects form data with:
    - image: image file (blob)
    - session_id: string (UUID)
    - photo_number: int (1-4)
    """
    try:
        # Validate required fields
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        session_id = request.form.get('session_id')
        photo_number = request.form.get('photo_number')
        
        if not session_id or not photo_number:
            return jsonify({'error': 'Missing session_id or photo_number'}), 400
        
        # Verify session exists
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        photo_number = int(photo_number)
        if photo_number < 1 or photo_number > 4:
            return jsonify({'error': 'Photo number must be between 1 and 4'}), 400
        
        # Get image file
        file = request.files['image']
        image_data = file.read()
        
        # Process image (flip for front camera)
        original_image = ImageProcessor.process_uploaded_image(image_data, 'none', False)
        processed_image = ImageProcessor.process_uploaded_image(image_data, 'none', True)  # Flip for front camera
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        base_filename = f'{timestamp}_{unique_id}_{photo_number}.jpg'
        
        # Save original
        original_path = os.path.join(
            current_app.config['ORIGINALS_FOLDER'], 
            base_filename
        )
        ImageProcessor.save_image(original_image, original_path)
        
        # Save processed (flipped)
        processed_path = os.path.join(
            current_app.config['PROCESSED_FOLDER'], 
            base_filename
        )
        ImageProcessor.save_image(processed_image, processed_path)
        
        # Create and save thumbnail
        thumbnail_image = ImageProcessor.create_thumbnail(processed_image.copy())
        thumbnail_path = os.path.join(
            current_app.config['THUMBNAILS_FOLDER'], 
            base_filename
        )
        ImageProcessor.save_image(thumbnail_image, thumbnail_path)
        
        # Create a template-slot-sized preview for faster client preview
        try:
            templates_json = os.path.join(current_app.static_folder, 'templates', 'templates.json')
            slot_size = (540, 400)
            if os.path.exists(templates_json):
                import json
                with open(templates_json, 'r', encoding='utf-8') as fh:
                    tmpl_data = json.load(fh)
                # find max photo_size among templates
                max_w, max_h = 0, 0
                for t in tmpl_data.values():
                    ps = t.get('photo_size')
                    if ps and isinstance(ps, list) and len(ps) >= 2:
                        max_w = max(max_w, int(ps[0]))
                        max_h = max(max_h, int(ps[1]))
                if max_w and max_h:
                    slot_size = (max_w, max_h)
            # Use TemplateEngine resize_and_crop to preserve crop behavior
            engine = TemplateEngine()
            slot_image = engine._resize_and_crop(processed_image.copy(), slot_size)
            name_root, ext = base_filename.rsplit('.', 1)
            slot_filename = f"{name_root}_slot.jpg"
            slot_path = os.path.join(current_app.config['PROCESSED_FOLDER'], slot_filename)
            ImageProcessor.save_image(slot_image, slot_path)
            slot_url = f'/api/images/processed/{slot_filename}'
        except Exception:
            slot_url = None
        
        # Save to database
        photo = Photo(
            session_id=session_id,
            photo_number=photo_number,
            original_filename=base_filename,
            processed_filename=base_filename,
            thumbnail_filename=base_filename
        )
        
        db.session.add(photo)
        
        # Update session status if all photos captured
        photo_count = Photo.query.filter_by(session_id=session_id).count()
        if photo_count >= 4:
            session.status = 'filtering'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'photo_id': photo.id,
            'file_path': base_filename,
            'original_url': f'/api/images/originals/{base_filename}',
            'processed_url': f'/api/images/processed/{base_filename}',
            'thumbnail_url': f'/api/images/thumbnails/{base_filename}',
            'slot_url': slot_url,
            'photo_number': photo_number
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Capture failed: {str(e)}'}), 500


@api_bp.route('/sessions/<session_id>/photos', methods=['GET'])
def get_session_photos(session_id):
    """Get all photos for a session"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        photos = Photo.query.filter_by(session_id=session_id).order_by(Photo.photo_number).all()
        
        result_photos = []
        for photo in photos:
            name_root, ext = photo.original_filename.rsplit('.', 1)
            slot_filename = f"{name_root}_{photo.photo_number}_slot.jpg"
            # older slot naming may be name_root_slot.jpg, so check both
            possible_slot1 = f"{name_root}_slot.jpg"
            possible_slot2 = slot_filename
            slot_url = None
            for fname in (possible_slot2, possible_slot1):
                if os.path.exists(os.path.join(current_app.config['PROCESSED_FOLDER'], fname)):
                    slot_url = url_for('api.serve_image', folder='processed', filename=fname)
                    break

            result_photos.append({
                'id': photo.id,
                'photo_number': photo.photo_number,
                'original_url': f'/api/images/originals/{photo.original_filename}',
                'processed_url': f'/api/images/processed/{photo.processed_filename}',
                'thumbnail_url': f'/api/images/thumbnails/{photo.thumbnail_filename}',
                'slot_url': slot_url
            })

        return jsonify({'success': True, 'photos': result_photos})
    except Exception as e:
        return jsonify({'error': f'Failed to get photos: {str(e)}'}), 500


@api_bp.route('/filters', methods=['GET'])
def get_filters():
    """Get list of available filters"""
    try:
        filters = FilterEngine.get_available_filters()
        enriched_filters = []

        for item in filters:
            example_path = item.get('example_thumbnail')
            example_url = None

            if example_path:
                absolute_path = os.path.join(current_app.static_folder, example_path)
                if os.path.exists(absolute_path):
                    example_url = url_for('static', filename=example_path)

            enriched_filters.append({
                **item,
                'example_thumbnail': example_url
            })

        return jsonify({
            'success': True,
            'filters': enriched_filters
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get filters: {str(e)}'}), 500


@api_bp.route('/templates', methods=['GET'])
def get_templates():
    """Return available template metadata and preview URLs"""
    try:
        templates = template_engine.get_available_templates()
        enriched = {}
        for name, meta in templates.items():
            preview_path = os.path.join(current_app.static_folder, 'templates', 'previews', f"{name}_preview.png")
            preview_url = None
            if os.path.exists(preview_path):
                preview_url = url_for('static', filename=os.path.join('templates', 'previews', f"{name}_preview.png"))
            enriched[name] = {**meta, 'preview': preview_url}
        return jsonify({'success': True, 'templates': enriched})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/collage', methods=['POST'])
def create_collage():
    """
    Create collage synchronously.
    Accepts JSON:
      - session_id or image_ids
      - template
      - colors (dict)
      - decorations (list of {'path','x','y','scale','color'}). 'path' can be server static path.
      - fill_mode: duplicate|placeholder|center
      - use_processed: bool (default True) - use processed images if available
    """
    try:
        data = request.get_json() or {}
        template_name = data.get('template', 'classic_strip')
        fill_mode = data.get('fill_mode', 'duplicate')
        colors = data.get('colors') or {}
        decorations = data.get('decorations') or []
        use_processed = data.get('use_processed', True)  # Default: sử dụng ảnh đã xử lý

        image_paths = []
        if 'session_id' in data:
            session_id = data['session_id']
            photos = Photo.query.filter_by(session_id=session_id).order_by(Photo.photo_number).all()
            for p in photos:
                # Ưu tiên sử dụng ảnh đã xử lý filter nếu có
                if use_processed and p.processed_filename:
                    abspath = os.path.join(current_app.config['PROCESSED_FOLDER'], p.processed_filename)
                    if os.path.exists(abspath):
                        image_paths.append(abspath)
                        continue
                # Fallback về ảnh gốc
                abspath = os.path.join(current_app.config['ORIGINALS_FOLDER'], p.original_filename)
                if os.path.exists(abspath):
                    image_paths.append(abspath)
        elif 'image_ids' in data:
            ids = data['image_ids']
            photos = Photo.query.filter(Photo.id.in_(ids)).order_by(Photo.photo_number).all()
            for p in photos:
                # Ưu tiên sử dụng ảnh đã xử lý filter nếu có
                if use_processed and p.processed_filename:
                    abspath = os.path.join(current_app.config['PROCESSED_FOLDER'], p.processed_filename)
                    if os.path.exists(abspath):
                        image_paths.append(abspath)
                        continue
                # Fallback về ảnh gốc
                abspath = os.path.join(current_app.config['ORIGINALS_FOLDER'], p.original_filename)
                if os.path.exists(abspath):
                    image_paths.append(abspath)
        else:
            return jsonify({'error': 'Provide session_id or image_ids'}), 400

        # Ensure template engine uses app collage folder
        template_engine.output_dir = current_app.config.get('COLLAGES_FOLDER', template_engine.output_dir)

        # Decorations: if the client provides decoration name, convert to static path
        processed_decorations = []
        for deco in decorations:
            path = deco.get('path')
            # Only allow decorations from our static templates/decorations directory
            if not path:
                continue
            if not os.path.isabs(path):
                # normalize path; allow decorations from templates/decorations or templates/stickers
                norm = path.replace('\\', '/').lstrip('/')
                allowed_prefixes = ('templates/decorations/', 'templates/stickers/', 'static/templates/decorations/', 'static/templates/stickers/')
                if not any(norm.startswith(pref) for pref in allowed_prefixes):
                    return jsonify({'error': 'Invalid decoration path'}), 400
                # if path already starts with 'static/', strip it to produce path relative to static folder
                if norm.startswith('static/'):
                    rel = norm[len('static/'):]
                else:
                    rel = norm
                abs_path = os.path.join(current_app.static_folder, rel)
            else:
                abs_path = path

            # Verify file exists and is under static folder
            try:
                abs_path = os.path.abspath(abs_path)
                if not abs_path.startswith(os.path.abspath(current_app.static_folder)):
                    return jsonify({'error': 'Decoration path not allowed'}), 400
                if not os.path.exists(abs_path):
                    return jsonify({'error': f'Decoration file not found: {path}'}), 400
            except Exception:
                return jsonify({'error': 'Invalid decoration path'}), 400

            # sanitize numeric values
            try:
                x = int(float(deco.get('x', 0)))
                y = int(float(deco.get('y', 0)))
                scale = float(deco.get('scale', 1.0))
            except Exception:
                return jsonify({'error': 'Invalid decoration coordinates/scale'}), 400

            processed_decorations.append({
                'path': abs_path,
                'x': x,
                'y': y,
                'scale': scale,
                'color': deco.get('color')
            })

        output_path = template_engine.create_collage(image_paths, template_name, colors=colors, decorations=processed_decorations, fill_mode=fill_mode)
        # make url relative to static folder if possible
        try:
            relative = os.path.relpath(output_path, current_app.static_folder)
            collage_url = url_for('static', filename=relative.replace("\\", "/"))
        except Exception:
            collage_url = output_path

        return jsonify({'success': True, 'collage_url': collage_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/apply-filter', methods=['POST'])
def apply_filter():
    """
    Apply a filter to photos in a session
    Expects JSON with:
    - session_id: string (UUID)
    - filter_name: string
    - photo_ids: list[int] (optional, defaults to all session photos)
    - commit: bool (optional, defaults to False). When True, persist results.
    """
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        filter_name = data.get('filter_name')
        photo_ids = data.get('photo_ids')
        commit = data.get('commit', False)
        
        if not session_id or not filter_name:
            return jsonify({'error': 'Missing session_id or filter_name'}), 400
        
        available_filters = {f['name'] for f in FilterEngine.get_available_filters()}
        if filter_name not in available_filters:
            return jsonify({'error': 'Invalid filter specified'}), 400
        
        if photo_ids is not None:
            if not isinstance(photo_ids, list):
                return jsonify({'error': 'photo_ids must be a list of integers'}), 400
            try:
                photo_ids = [int(pid) for pid in photo_ids]
            except (TypeError, ValueError):
                return jsonify({'error': 'photo_ids must be a list of integers'}), 400
        
        # Verify session exists
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Determine photos to process
        photo_query = Photo.query.filter_by(session_id=session_id)
        if photo_ids:
            photo_query = photo_query.filter(Photo.id.in_(photo_ids))
        
        photos = photo_query.order_by(Photo.photo_number).all()
        
        if not photos:
            return jsonify({'error': 'No photos found for processing'}), 404
        
        processed_images = []
        thumbnails = []
        
        for photo in photos:
            original_path = os.path.join(
                current_app.config['ORIGINALS_FOLDER'],
                photo.original_filename
            )
            
            if not os.path.exists(original_path):
                continue
            
            with Image.open(original_path) as image:
                filtered_image = FilterEngine.apply_filter(image.copy(), filter_name)
            
            name_root, ext = photo.original_filename.rsplit('.', 1)
            processed_filename = f"{name_root}_{filter_name}.jpg"
            processed_path = os.path.join(
                current_app.config['PROCESSED_FOLDER'],
                processed_filename
            )
            ImageProcessor.save_image(filtered_image, processed_path)
            
            thumbnail_image = ImageProcessor.create_thumbnail(filtered_image.copy())
            thumbnail_filename = f"{name_root}_{filter_name}.jpg"
            thumbnail_path = os.path.join(
                current_app.config['THUMBNAILS_FOLDER'],
                thumbnail_filename
            )
            ImageProcessor.save_image(thumbnail_image, thumbnail_path)
            
            processed_url = url_for('api.serve_image', folder='processed', filename=processed_filename)
            thumbnail_url = url_for('api.serve_image', folder='thumbnails', filename=thumbnail_filename)
            original_url = url_for('api.serve_image', folder='originals', filename=photo.original_filename)
            
            processed_images.append({
                'photo_id': photo.id,
                'photo_number': photo.photo_number,
                'original_url': original_url,
                'processed_url': processed_url,
                'thumbnail_url': thumbnail_url
            })
            thumbnails.append(thumbnail_url)
            
            if commit:
                photo.processed_filename = processed_filename
                photo.thumbnail_filename = thumbnail_filename
                photo.applied_filter = filter_name
        
        if commit:
            filter_applied = FilterApplied(
                session_id=session_id,
                filter_name=filter_name
            )
            db.session.add(filter_applied)
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            db.session.commit()
        else:
            db.session.expire_all()
        
        return jsonify({
            'success': True,
            'processed_images': processed_images,
            'thumbnails': thumbnails,
            'filter_name': filter_name,
            'committed': commit
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to apply filter: {str(e)}'}), 500


@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Photobooth API is running'
    })


# ============== FACE DETECTION API ENDPOINTS ==============

@api_bp.route('/face-detect', methods=['POST'])
def detect_faces_api():
    """
    Detect faces in an image

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'image_url' (relative path like /api/images/processed/xxx.jpg)
    - OR JSON with 'filename' (just filename, assumes processed folder)

    Returns:
    - faces: List of detected faces with bbox, confidence, center
    - count: Number of faces detected
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        image = None

        # Option 1: File upload
        if 'image' in request.files:
            file = request.files['image']
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))

        # Option 2: JSON with filename/url
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            image_url = data.get('image_url')

            if filename:
                # Look in processed folder
                filepath = os.path.join(
                    current_app.config['PROCESSED_FOLDER'],
                    filename
                )
                if os.path.exists(filepath):
                    image = Image.open(filepath)
            elif image_url:
                # Parse URL to get filename
                parts = image_url.split('/')
                if len(parts) >= 2:
                    folder = parts[-2]  # e.g., 'processed'
                    fname = parts[-1]
                    folder_key = f'{folder.upper()}_FOLDER'
                    if folder_key in current_app.config:
                        filepath = os.path.join(
                            current_app.config[folder_key],
                            fname
                        )
                        if os.path.exists(filepath):
                            image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect faces
        confidence = request.args.get('confidence', 0.5, type=float)
        faces = detector.detect_faces(image, confidence_threshold=confidence)

        # Format response
        faces_response = []
        for face in faces:
            faces_response.append({
                'bbox': {
                    'x': face['bbox'][0],
                    'y': face['bbox'][1],
                    'width': face['bbox'][2],
                    'height': face['bbox'][3]
                },
                'confidence': round(face['confidence'], 4),
                'center': {
                    'x': face['center'][0],
                    'y': face['center'][1]
                }
            })

        return jsonify({
            'success': True,
            'count': len(faces_response),
            'faces': faces_response
        })

    except Exception as e:
        return jsonify({'error': f'Face detection failed: {str(e)}'}), 500


@api_bp.route('/auto-crop', methods=['POST'])
def auto_crop_portrait():
    """
    Auto crop image to center on face with portrait ratio

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Query params:
    - ratio: target height/width ratio (default 1.33 = 4:3 portrait)
    - padding: padding around face (default 0.4)
    - save: if 'true', save to processed folder

    Returns:
    - Cropped image as base64 or URL if saved
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        image = None
        original_filename = None

        # Get image from request
        if 'image' in request.files:
            file = request.files['image']
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))
            original_filename = secure_filename(file.filename)
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(
                    current_app.config['PROCESSED_FOLDER'],
                    filename
                )
                if os.path.exists(filepath):
                    image = Image.open(filepath)
                    original_filename = filename

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Get parameters
        ratio = request.args.get('ratio', 1.33, type=float)
        padding = request.args.get('padding', 0.4, type=float)
        save = request.args.get('save', 'false').lower() == 'true'

        # Auto crop
        cropped = detector.auto_crop_portrait(image, target_ratio=ratio, padding=padding)

        if save and original_filename:
            # Save cropped image
            cropped_filename = f'cropped_{original_filename}'
            cropped_path = os.path.join(
                current_app.config['PROCESSED_FOLDER'],
                cropped_filename
            )
            cropped.save(cropped_path, 'JPEG', quality=90)

            return jsonify({
                'success': True,
                'filename': cropped_filename,
                'url': f'/api/images/processed/{cropped_filename}'
            })
        else:
            # Return as base64
            buffer = io.BytesIO()
            cropped.save(buffer, format='JPEG', quality=90)
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'image_base64': base64_image,
                'width': cropped.width,
                'height': cropped.height
            })

    except Exception as e:
        return jsonify({'error': f'Auto crop failed: {str(e)}'}), 500


@api_bp.route('/sticker-positions', methods=['POST'])
def get_sticker_positions():
    """
    Get suggested sticker positions based on face detection

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Query params:
    - sticker_type: 'hat', 'glasses', 'ears', 'mustache' (default 'hat')

    Returns:
    - positions: List of suggested positions for each detected face
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        image = None

        # Get image
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(
                    current_app.config['PROCESSED_FOLDER'],
                    filename
                )
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        sticker_type = request.args.get('sticker_type', 'hat')

        positions = detector.get_face_positions_for_stickers(image, sticker_type)

        # Format response
        positions_response = []
        for pos in positions:
            positions_response.append({
                'x': pos['x'],
                'y': pos['y'],
                'scale': round(pos['scale'], 3),
                'anchor': pos['anchor'],
                'face_bbox': {
                    'x': pos['face_bbox'][0],
                    'y': pos['face_bbox'][1],
                    'width': pos['face_bbox'][2],
                    'height': pos['face_bbox'][3]
                },
                'confidence': round(pos['confidence'], 4)
            })

        return jsonify({
            'success': True,
            'sticker_type': sticker_type,
            'count': len(positions_response),
            'positions': positions_response
        })

    except Exception as e:
        return jsonify({'error': f'Sticker position detection failed: {str(e)}'}), 500


@api_bp.route('/face-debug', methods=['POST'])
def face_debug():
    """
    Debug endpoint: Draw face detection boxes on image

    Accepts: Form data with 'image' file
    Returns: Image with face boxes drawn as base64
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        image = Image.open(io.BytesIO(file.read()))

        # Detect and draw
        result = detector.draw_faces(image)

        # Return as base64
        buffer = io.BytesIO()
        result.save(buffer, format='JPEG', quality=90)
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        faces = detector.detect_faces(image)

        return jsonify({
            'success': True,
            'image_base64': base64_image,
            'faces_detected': len(faces)
        })

    except Exception as e:
        return jsonify({'error': f'Face debug failed: {str(e)}'}), 500




