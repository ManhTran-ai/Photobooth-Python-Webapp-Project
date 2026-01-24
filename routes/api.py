"""
API routes for photobooth application
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app, url_for
from werkzeug.utils import secure_filename
from models.image_processor import ImageProcessor
from models.filter_engine import FilterEngine
from models.database import db, Session, Photo, FilterApplied, User, FaceEmbedding
from models.template_engine import TemplateEngine
from models.model_manager import get_model_manager
from models.embedding_index import get_embedding_index
from models.embeddings import serialize_embedding, deserialize_embedding
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
      - sticker_paths: list of sticker file paths for anchor-based placement
      - anchor_mode: bool (default False) - if True, place stickers using anchor points
      - sticker_indices: list of sticker indices (starting from 1) for anchor point selection
                        - Indices 1-15: use Option 1 anchor points
                        - Indices 16-31: use Option 2 anchor points
    """
    try:
        data = request.get_json() or {}
        template_name = data.get('template', 'classic_strip')
        fill_mode = data.get('fill_mode', 'duplicate')
        colors = data.get('colors') or {}
        decorations = data.get('decorations') or []
        use_processed = data.get('use_processed', True)  # Default: sử dụng ảnh đã xử lý
        sticker_paths = data.get('sticker_paths', [])
        anchor_mode = data.get('anchor_mode', False)
        sticker_indices = data.get('sticker_indices', [])  # Danh sách chỉ số sticker (1-31)

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

        # Process sticker paths for anchor mode
        processed_stickers = []
        if anchor_mode and sticker_paths:
            for path in sticker_paths:
                if not path:
                    continue
                # Normalize path
                norm = path.replace('\\', '/').lstrip('/')
                allowed_prefixes = ('templates/stickers/', 'static/templates/stickers/')
                if not any(norm.startswith(pref) for pref in allowed_prefixes):
                    continue
                rel = norm[len('static/'):] if norm.startswith('static/') else norm
                abs_path = os.path.join(current_app.static_folder, rel)
                if os.path.exists(abs_path):
                    processed_stickers.append(abs_path)

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

        output_path = template_engine.create_collage(
            image_paths, template_name,
            colors=colors,
            decorations=processed_decorations,
            fill_mode=fill_mode,
            sticker_paths=processed_stickers,
            anchor_mode=anchor_mode,
            sticker_indices=sticker_indices
        )
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


@api_bp.route('/stickers/processed', methods=['GET'])
def get_processed_sticker():
    """
    Return processed sticker PNG with transparent background.
    Query params:
      - name: filename under static/templates (e.g., hat.png)
    Saves processed file under static/templates/processed/<name> and returns URL.
    """
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'Missing sticker name'}), 400

        # Normalize name to prevent path traversal
        name = os.path.basename(name)

        # Stickers are now stored directly in static/templates/
        templates_dir = os.path.join(current_app.static_folder, 'templates')
        src_path = os.path.join(templates_dir, name)

        # Fallback to stickers subdirectory if not found
        if not os.path.exists(src_path):
            stickers_dir = os.path.join(templates_dir, 'stickers')
            src_path = os.path.join(stickers_dir, name)

        if not os.path.exists(src_path):
            return jsonify({'error': f'Sticker not found: {name}'}), 404

        processed_dir = os.path.join(templates_dir, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        processed_path = os.path.join(processed_dir, name)

        # If already processed, return URL
        if os.path.exists(processed_path):
            rel = os.path.relpath(processed_path, current_app.static_folder)
            return jsonify({'processed_url': url_for('static', filename=rel.replace("\\", "/"))})

        # Process sticker: remove background using TemplateEngine helper
        try:
            img = Image.open(src_path).convert('RGBA')
            processed_img = TemplateEngine._remove_sticker_background(img)
            # Save processed PNG
            processed_img.save(processed_path, 'PNG')
            rel = os.path.relpath(processed_path, current_app.static_folder)
            return jsonify({'processed_url': url_for('static', filename=rel.replace("\\", "/"))})
        except Exception as e:
            # If processing fails, fall back to original static path
            rel = os.path.relpath(src_path, current_app.static_folder)
            return jsonify({'processed_url': url_for('static', filename=rel.replace("\\", "/")), 'warning': str(e)})

    except Exception as e:
        return jsonify({'error': f'Failed to process sticker: {str(e)}'}), 500


@api_bp.route('/apply-sticker', methods=['POST'])
def apply_sticker_to_photo():
    """
    Apply sticker overlay to a photo based on face detection.

    Request JSON:
    - filename: image filename in processed folder
    - sticker_type: 'hat', 'glasses', 'ears', 'mustache'
    - save: if True, save the result (default: False for preview)

    Returns:
    - success: bool
    - result_url: URL of the processed image (base64 if preview, file URL if saved)
    - positions: list of face positions where stickers were applied
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        data = request.get_json() or {}
        filename = data.get('filename')
        sticker_type = data.get('sticker_type', 'hat')
        save_result = data.get('save', False)

        if not filename:
            return jsonify({'error': 'Missing filename'}), 400

        # Load the photo
        filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': f'Image not found: {filename}'}), 404

        image = Image.open(filepath).convert('RGBA')

        # Get sticker file - mapping các loại phụ kiện
        sticker_map = {
            'hat': 'hat-2.png',
            'glasses': 'glasses.png',
            'ears': 'rabbit_ears.png',
            'mustache': 'mustache.png',
            'noel_hat': 'noel-hat.png',
            'bow': 'No.png'
        }
        sticker_name = sticker_map.get(sticker_type, 'hat-2.png')

        # Try to find sticker in templates folder
        templates_dir = os.path.join(current_app.static_folder, 'templates')
        sticker_path = os.path.join(templates_dir, sticker_name)

        if not os.path.exists(sticker_path):
            return jsonify({'error': f'Sticker not found: {sticker_name}'}), 404

        sticker = Image.open(sticker_path).convert('RGBA')

        # Detect faces and get positions
        positions = detector.get_face_positions_for_stickers(image, sticker_type)

        if not positions:
            return jsonify({
                'success': True,
                'warning': 'No faces detected in image',
                'positions': []
            })

        # Apply sticker to each detected face
        result_image = image.copy()
        applied_positions = []

        for pos in positions:
            # Calculate sticker size based on face
            face_width = pos['face_bbox'][2]

            # Size multiplier based on sticker type
            size_multipliers = {
                'hat': 1.4,       # Mũ rộng hơn mặt
                'glasses': 1.1,   # Kính vừa với mặt
                'ears': 1.6,      # Tai thỏ rộng
                'mustache': 0.5,  # Râu nhỏ hơn
                'noel_hat': 1.5,  # Nón Noel rộng
                'bow': 0.6        # Nơ nhỏ gọn
            }
            multiplier = size_multipliers.get(sticker_type, 1.0)
            target_width = int(face_width * multiplier)

            # Maintain aspect ratio
            sticker_ratio = sticker.height / sticker.width
            target_height = int(target_width * sticker_ratio)

            # Resize sticker
            resized_sticker = sticker.resize((target_width, target_height), Image.LANCZOS)

            # Calculate paste position (centered on anchor point)
            paste_x = pos['x'] - target_width // 2
            paste_y = pos['y'] - target_height // 2

            # Adjust for anchor type
            anchor = pos.get('anchor', 'center')
            if anchor == 'bottom-center':
                paste_y = pos['y'] - target_height

            # Ensure position is within bounds
            paste_x = max(0, min(paste_x, result_image.width - target_width))
            paste_y = max(0, min(paste_y, result_image.height - target_height))

            # Paste sticker with transparency
            result_image.paste(resized_sticker, (paste_x, paste_y), resized_sticker)

            applied_positions.append({
                'x': pos['x'],
                'y': pos['y'],
                'width': target_width,
                'height': target_height,
                'confidence': pos['confidence']
            })

        # Convert result to RGB for saving/preview
        result_rgb = Image.new('RGB', result_image.size, (255, 255, 255))
        result_rgb.paste(result_image, mask=result_image.split()[3] if result_image.mode == 'RGBA' else None)

        if save_result:
            # Save to processed folder with sticker suffix
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_sticker_{sticker_type}{ext}"
            output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
            result_rgb.save(output_path, 'JPEG', quality=95)

            return jsonify({
                'success': True,
                'filename': output_filename,
                'result_url': f'/api/images/processed/{output_filename}',
                'positions': applied_positions
            })
        else:
            # Return as base64 for preview
            buffer = io.BytesIO()
            result_rgb.save(buffer, format='JPEG', quality=90)
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'result_base64': f'data:image/jpeg;base64,{base64_image}',
                'positions': applied_positions
            })

    except Exception as e:
        return jsonify({'error': f'Apply sticker failed: {str(e)}'}), 500


@api_bp.route('/apply-sticker-session', methods=['POST'])
def apply_sticker_to_session():
    """
    Apply sticker to all photos in a session based on face detection.

    Request JSON:
    - session_id: session ID
    - sticker_type: 'hat', 'glasses', 'ears', 'mustache'
    - save: if True, save and update session photos (default: True)

    Returns:
    - success: bool
    - results: list of results for each photo
    """
    try:
        from models.face_detector import get_detector
        detector = get_detector()

        data = request.get_json() or {}
        session_id = data.get('session_id')
        sticker_type = data.get('sticker_type', 'hat')
        save_result = data.get('save', True)

        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400

        # Get session photos
        session = Session.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        photos = Photo.query.filter_by(session_id=session_id).order_by(Photo.photo_number).all()
        if not photos:
            return jsonify({'error': 'No photos in session'}), 404

        # Get sticker - mapping các loại phụ kiện
        sticker_map = {
            'hat': 'hat-2.png',
            'glasses': 'glasses.png',
            'ears': 'rabbit_ears.png',
            'mustache': 'mustache.png',
            'noel_hat': 'noel-hat.png',
            'bow': 'No.png'
        }
        sticker_name = sticker_map.get(sticker_type, 'hat-2.png')

        templates_dir = os.path.join(current_app.static_folder, 'templates')
        sticker_path = os.path.join(templates_dir, sticker_name)

        if not os.path.exists(sticker_path):
            return jsonify({'error': f'Sticker not found: {sticker_name}'}), 404

        sticker = Image.open(sticker_path).convert('RGBA')

        results = []

        for photo in photos:
            filename = photo.processed_filename or photo.original_filename
            filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)

            if not os.path.exists(filepath):
                results.append({
                    'photo_id': photo.id,
                    'success': False,
                    'error': 'File not found'
                })
                continue

            try:
                image = Image.open(filepath).convert('RGBA')
                positions = detector.get_face_positions_for_stickers(image, sticker_type)

                if not positions:
                    results.append({
                        'photo_id': photo.id,
                        'success': True,
                        'warning': 'No faces detected',
                        'faces': 0
                    })
                    continue

                # Apply sticker to each face
                result_image = image.copy()

                for pos in positions:
                    face_width = pos['face_bbox'][2]
                    size_multipliers = {
                        'hat': 1.4, 'glasses': 1.1, 'ears': 1.6,
                        'mustache': 0.5, 'noel_hat': 1.5, 'bow': 0.6
                    }
                    target_width = int(face_width * size_multipliers.get(sticker_type, 1.0))
                    sticker_ratio = sticker.height / sticker.width
                    target_height = int(target_width * sticker_ratio)

                    resized_sticker = sticker.resize((target_width, target_height), Image.LANCZOS)

                    paste_x = pos['x'] - target_width // 2
                    paste_y = pos['y'] - target_height // 2

                    if pos.get('anchor') == 'bottom-center':
                        paste_y = pos['y'] - target_height

                    paste_x = max(0, min(paste_x, result_image.width - target_width))
                    paste_y = max(0, min(paste_y, result_image.height - target_height))

                    result_image.paste(resized_sticker, (paste_x, paste_y), resized_sticker)

                # Save result
                if save_result:
                    result_rgb = Image.new('RGB', result_image.size, (255, 255, 255))
                    if result_image.mode == 'RGBA':
                        result_rgb.paste(result_image, mask=result_image.split()[3])
                    else:
                        result_rgb.paste(result_image)
                    result_rgb.save(filepath, 'JPEG', quality=95)

                results.append({
                    'photo_id': photo.id,
                    'success': True,
                    'faces': len(positions),
                    'filename': filename
                })

            except Exception as e:
                results.append({
                    'photo_id': photo.id,
                    'success': False,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'sticker_type': sticker_type,
            'results': results,
            'total_photos': len(photos),
            'photos_with_faces': sum(1 for r in results if r.get('faces', 0) > 0)
        })

    except Exception as e:
        return jsonify({'error': f'Apply sticker to session failed: {str(e)}'}), 500


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


# ============== FACE RECOGNITION API ENDPOINTS ==============

@api_bp.route('/face-embed', methods=['POST'])
def create_face_embedding():
    """
    Create and store face embedding for recognition (opt-in feature).
    Requires user consent for privacy.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'
    - JSON with 'user_label' (optional, auto-generated if not provided)
    - JSON with 'display_name' (optional)

    Query params:
    - consent: 'true' (required for privacy compliance)

    Returns:
    - user_id, embedding_id, user_label
    """
    try:
        # Check consent
        consent = request.args.get('consent', 'false').lower() == 'true'
        if not consent:
            return jsonify({'error': 'User consent required for face recognition'}), 400

        model_manager = get_model_manager()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Extract embedding
        embedding = model_manager.extract_embedding(face_region)

        # Get or create user
        user_label = None
        display_name = None

        if request.is_json:
            data = request.get_json()
            user_label = data.get('user_label')
            display_name = data.get('display_name')

        if not user_label:
            # Auto-generate unique label
            import uuid
            user_label = f"user_{uuid.uuid4().hex[:8]}"

        # Check if user exists
        user = User.query.filter_by(label=user_label).first()
        if not user:
            user = User(
                label=user_label,
                display_name=display_name
            )
            db.session.add(user)
            db.session.flush()  # Get user.id

        # Create embedding record
        serialized_embedding = serialize_embedding(embedding)
        image_hash = model_manager.compute_image_hash(face_region)

        # Check for duplicate embedding
        existing = FaceEmbedding.query.filter_by(
            user_id=user.id,
            image_hash=image_hash
        ).first()

        if existing:
            return jsonify({
                'success': True,
                'message': 'Embedding already exists',
                'user_id': user.id,
                'user_label': user.label,
                'embedding_id': existing.id
            })

        embedding_record = FaceEmbedding(
            user_id=user.id,
            embedding_vector=serialized_embedding,
            confidence=largest_face['confidence'],
            image_hash=image_hash
        )

        db.session.add(embedding_record)
        db.session.commit()

        # Add to Annoy index
        index = get_embedding_index()
        index.add_embedding(user.id, embedding)

        return jsonify({
            'success': True,
            'user_id': user.id,
            'user_label': user.label,
            'display_name': user.display_name,
            'embedding_id': embedding_record.id,
            'message': 'Face embedding created successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create embedding: {str(e)}'}), 500


@api_bp.route('/recognize', methods=['POST'])
def recognize_face():
    """
    Recognize face in image by comparing with stored embeddings.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Query params:
    - threshold: similarity threshold (default 0.6)
    - top_k: number of results to return (default 1)

    Returns:
    - matches: list of matched users with similarity scores
    """
    try:
        model_manager = get_model_manager()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Extract embedding
        embedding = model_manager.extract_embedding(face_region)

        # Search in index
        index = get_embedding_index()
        threshold = float(request.args.get('threshold', 0.6))
        top_k = int(request.args.get('top_k', 1))

        # Load index if not loaded
        if index.index is None:
            # Load embeddings from DB
            embeddings_data = []
            embedding_records = FaceEmbedding.query.all()
            for record in embedding_records:
                embeddings_data.append({
                    'user_id': record.user_id,
                    'embedding_vector': deserialize_embedding(record.embedding_vector)
                })
            index.load_or_create_index(embeddings_data)

        # Search
        search_results = index.search(embedding, top_k=top_k)

        # Filter by threshold and get user info
        matches = []
        for user_id, distance in search_results:
            similarity = 1.0 - distance  # Convert distance to similarity
            if similarity >= threshold:
                user = User.query.get(user_id)
                if user:
                    matches.append({
                        'user_id': user.id,
                        'user_label': user.label,
                        'display_name': user.display_name,
                        'similarity': round(similarity, 4),
                        'distance': round(distance, 4)
                    })

        return jsonify({
            'success': True,
            'face_detected': True,
            'matches': matches,
            'match_count': len(matches),
            'threshold': threshold
        })

    except Exception as e:
        return jsonify({'error': f'Recognition failed: {str(e)}'}), 500


@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of all users with face embeddings (admin endpoint)"""
    try:
        users = User.query.all()
        result = []

        for user in users:
            result.append({
                **user.to_dict(),
                'embeddings': [emb.to_dict() for emb in user.embeddings]
            })

        return jsonify({
            'success': True,
            'users': result,
            'total_users': len(result)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get users: {str(e)}'}), 500


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user and all their face embeddings (privacy compliance)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Delete from index
        index = get_embedding_index()
        index.remove_user(user_id)

        # Delete from DB (cascade will handle embeddings)
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'User {user.label} and all embeddings deleted'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500


@api_bp.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    """
    Detect emotion from face in image.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Returns:
    - emotions: dict of emotion probabilities
    - dominant: most likely emotion
    - confidence: confidence score
    """
    try:
        model_manager = get_model_manager()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Convert to RGB if needed (remove alpha channel)
        if face_region.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', face_region.size, (255, 255, 255))
            background.paste(face_region, mask=face_region.split()[-1])  # Use alpha as mask
            face_region = background
        elif face_region.mode != 'RGB':
            face_region = face_region.convert('RGB')

        # Detect emotion
        emotion_result = model_manager.detect_emotion(face_region)

        return jsonify({
            'success': True,
            'face_detected': True,
            'emotions': emotion_result['emotions'],
            'dominant_emotion': emotion_result['dominant'],
            'confidence': round(emotion_result['confidence'], 4)
        })

    except Exception as e:
        return jsonify({'error': f'Emotion detection failed: {str(e)}'}), 500


@api_bp.route('/estimate-age-gender', methods=['POST'])
def estimate_age_gender():
    """
    Estimate age range and gender from face in image.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Returns:
    - age_range: estimated age range (e.g., '20-34')
    - gender: estimated gender ('male'/'female')
    - confidence scores for both estimates
    """
    try:
        model_manager = get_model_manager()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Convert to RGB if needed (remove alpha channel)
        if face_region.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', face_region.size, (255, 255, 255))
            background.paste(face_region, mask=face_region.split()[-1])  # Use alpha as mask
            face_region = background
        elif face_region.mode != 'RGB':
            face_region = face_region.convert('RGB')

        # Estimate age and gender
        age_gender_result = model_manager.estimate_age_gender(face_region)

        return jsonify({
            'success': True,
            'face_detected': True,
            'age_range': age_gender_result['age_range'],
            'age_confidence': age_gender_result['age_confidence'],
            'gender': age_gender_result['gender'],
            'gender_confidence': age_gender_result['gender_confidence'],
            'method': age_gender_result.get('method', 'unknown')
        })

    except Exception as e:
        return jsonify({'error': f'Age/gender estimation failed: {str(e)}'}), 500


@api_bp.route('/detect-landmarks', methods=['POST'])
def detect_landmarks():
    """
    Detect facial landmarks from face in image.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'
    - Query param 'key_only=true' to return only key landmarks

    Returns:
    - landmarks: list of landmark coordinates
    - key_landmarks: dict of key facial features (optional)
    """
    try:
        model_manager = get_model_manager()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Detect landmarks
        key_only = request.args.get('key_only', 'false').lower() == 'true'

        response = {
            'success': True,
            'face_detected': True
        }

        if key_only:
            key_landmarks = model_manager.get_key_landmarks(face_region)
            response['key_landmarks'] = key_landmarks
            response['landmark_count'] = len(key_landmarks)
        else:
            landmarks = model_manager.detect_landmarks(face_region)
            response['landmarks'] = landmarks
            response['landmark_count'] = len(landmarks)

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Landmark detection failed: {str(e)}'}), 500


@api_bp.route('/sticker-fit', methods=['POST'])
def get_sticker_fit():
    """
    Calculate optimal sticker placement using facial landmarks.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'
    - JSON with 'sticker_type' (hat, glasses, ears, mustache, custom)
    - JSON with 'custom_position' dict (optional for custom stickers)

    Returns:
    - position: optimal x,y coordinates
    - scale: recommended scale factor
    - rotation: recommended rotation angle
    - confidence: placement confidence score
    """
    try:
        model_manager = get_model_manager()

        # Get request data
        data = request.get_json() or {}
        sticker_type = data.get('sticker_type', 'hat')
        custom_position = data.get('custom_position')

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif 'filename' in data:
            filename = data['filename']
            filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
            if os.path.exists(filepath):
                image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Detect face
        faces = model_manager.detect_faces(image)
        if not faces:
            return jsonify({'error': 'No face detected in image'}), 400

        # Use largest face
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        face_region = model_manager.detector.get_face_region(image, largest_face)

        # Get facial landmarks
        key_landmarks = model_manager.get_key_landmarks(face_region)

        if not key_landmarks:
            # Fallback to bbox-based positioning if landmarks fail
            return _calculate_fallback_position(image, largest_face, sticker_type)

        # Calculate position based on sticker type and landmarks
        position = _calculate_sticker_position(key_landmarks, sticker_type, largest_face, custom_position)

        return jsonify({
            'success': True,
            'face_detected': True,
            'sticker_type': sticker_type,
            'position': position,
            'landmarks_used': len(key_landmarks)
        })

    except Exception as e:
        return jsonify({'error': f'Sticker fit calculation failed: {str(e)}'}), 500


@api_bp.route('/personalized-suggestions', methods=['POST'])
def get_personalized_suggestions():
    """
    Get comprehensive personalized suggestions based on face analysis.

    Accepts:
    - Form data with 'image' file
    - OR JSON with 'filename'

    Returns:
    - emotion analysis and suggestions
    - age/gender analysis and suggestions
    - recommended filters and templates
    """
    try:
        from models.suggestion_engine import get_suggestion_engine

        model_manager = get_model_manager()
        suggestion_engine = get_suggestion_engine()

        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(io.BytesIO(file.read()))
        elif request.is_json:
            data = request.get_json()
            filename = data.get('filename')
            if filename:
                filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
                if os.path.exists(filepath):
                    image = Image.open(filepath)

        if image is None:
            return jsonify({'error': 'No valid image provided'}), 400

        # Get comprehensive analysis
        analysis = suggestion_engine.get_personalized_suggestions(image)

        # Add face detection info
        faces = model_manager.detect_faces(image)
        analysis['face_count'] = len(faces)

        if faces:
            analysis['face_confidence'] = faces[0]['confidence']

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'error': f'Personalized suggestions failed: {str(e)}'}), 500


@api_bp.route('/model-status', methods=['GET'])
def get_model_status():
    """Get status of loaded models and system health"""
    try:
        model_manager = get_model_manager()
        status = {
            'face_detector': 'loaded',
            'embedding_model': 'not_loaded',  # Will be loaded lazily
            'emotion_model': 'loaded',  # Simple rule-based, always available
            'landmark_model': 'not_loaded',  # MediaPipe, loaded lazily
            'age_gender_model': 'loaded'  # Heuristic-based, always available
        }

        # Check TensorFlow availability
        try:
            import tensorflow as tf
            status['tensorflow_available'] = True
            status['embedding_model'] = 'available'
        except ImportError:
            status['tensorflow_available'] = False
            status['embedding_model'] = 'unavailable'

        # Check MediaPipe availability
        try:
            import mediapipe as mp
            status['mediapipe_available'] = True
            status['landmark_model'] = 'available'
        except ImportError:
            status['mediapipe_available'] = False

        # Get embedding stats
        try:
            from models.embedding_index import get_embedding_index
            index = get_embedding_index()
            if index.index:
                status['embedding_index'] = {
                    'users': index.get_user_count(),
                    'embeddings': index.get_embedding_count(),
                    'loaded': True
                }
            else:
                status['embedding_index'] = {'loaded': False}
        except Exception:
            status['embedding_index'] = {'loaded': False, 'error': 'Index not available'}

        return jsonify({
            'success': True,
            'status': status,
            'message': 'Some DNN features require TensorFlow/MediaPipe installation for full functionality'
        })

    except Exception as e:
        return jsonify({'error': f'Model status check failed: {str(e)}'}), 500


def _calculate_sticker_position(key_landmarks, sticker_type, face_bbox, custom_position=None):
    """
    Calculate optimal sticker position using facial landmarks.

    Args:
        key_landmarks: Dict of key facial landmarks
        sticker_type: Type of sticker (hat, glasses, etc.)
        face_bbox: Face bounding box (x, y, w, h)
        custom_position: Custom position override

    Returns:
        Dict with position, scale, rotation, confidence
    """
    x, y, w, h = face_bbox['bbox']

    if sticker_type == 'hat':
        # Place hat above forehead
        if 'forehead' in key_landmarks:
            base_x = key_landmarks['forehead']['x']
            base_y = key_landmarks['forehead']['y']
        else:
            # Fallback to top of face bbox
            base_x = x + w // 2
            base_y = y

        position = {
            'x': base_x,
            'y': base_y - int(h * 0.2),  # Above face
            'scale': w / 80.0,  # Scale relative to face width
            'rotation': 0,
            'anchor': 'bottom-center',
            'confidence': 0.9
        }

    elif sticker_type == 'glasses':
        # Place glasses at eye level
        if 'left_eye' in key_landmarks and 'right_eye' in key_landmarks:
            left_eye = key_landmarks['left_eye']
            right_eye = key_landmarks['right_eye']
            eye_center_x = (left_eye['x'] + right_eye['x']) // 2
            eye_center_y = (left_eye['y'] + right_eye['y']) // 2
            base_x, base_y = eye_center_x, eye_center_y
        else:
            # Fallback to middle of face
            base_x = x + w // 2
            base_y = y + int(h * 0.35)

        position = {
            'x': base_x,
            'y': base_y,
            'scale': w / 60.0,
            'rotation': 0,
            'anchor': 'center',
            'confidence': 0.85
        }

    elif sticker_type == 'ears':
        # Place ear accessories on sides of head
        base_x = x + w // 2
        base_y = y + int(h * 0.1)

        position = {
            'x': base_x,
            'y': base_y,
            'scale': w / 50.0,
            'rotation': 0,
            'anchor': 'bottom-center',
            'confidence': 0.8
        }

    elif sticker_type == 'mustache':
        # Place mustache below nose
        if 'nose_tip' in key_landmarks:
            base_x = key_landmarks['nose_tip']['x']
            base_y = key_landmarks['nose_tip']['y']
        elif 'mouth_center' in key_landmarks:
            base_x = key_landmarks['mouth_center']['x']
            base_y = key_landmarks['mouth_center']['y'] - int(h * 0.1)
        else:
            base_x = x + w // 2
            base_y = y + int(h * 0.65)

        position = {
            'x': base_x,
            'y': base_y,
            'scale': w / 100.0,
            'rotation': 0,
            'anchor': 'top-center',
            'confidence': 0.85
        }

    elif sticker_type == 'custom' and custom_position:
        # Use custom position
        position = {
            'x': custom_position.get('x', x + w // 2),
            'y': custom_position.get('y', y + h // 2),
            'scale': custom_position.get('scale', 1.0),
            'rotation': custom_position.get('rotation', 0),
            'anchor': custom_position.get('anchor', 'center'),
            'confidence': 0.7
        }

    else:
        # Default position at face center
        position = {
            'x': x + w // 2,
            'y': y + h // 2,
            'scale': w / 100.0,
            'rotation': 0,
            'anchor': 'center',
            'confidence': 0.6
        }

    return position


def _calculate_fallback_position(image, face_bbox, sticker_type):
    """
    Fallback sticker positioning using face bbox when landmarks fail.
    """
    x, y, w, h = face_bbox['bbox']

    # Use existing logic from face_detector
    from models.face_detector import get_detector
    detector = get_detector()

    positions = detector.get_face_positions_for_stickers(image, sticker_type)

    if positions:
        pos = positions[0]  # Use first face
        return jsonify({
            'success': True,
            'face_detected': True,
            'sticker_type': sticker_type,
            'position': {
                'x': pos['x'],
                'y': pos['y'],
                'scale': pos['scale'],
                'rotation': 0,
                'anchor': pos['anchor'],
                'confidence': 0.6  # Lower confidence for fallback
            },
            'fallback': True
        })
    else:
        return jsonify({
            'success': True,
            'face_detected': True,
            'sticker_type': sticker_type,
            'position': {
                'x': x + w // 2,
                'y': y + h // 2,
                'scale': 1.0,
                'rotation': 0,
                'anchor': 'center',
                'confidence': 0.5
            },
            'fallback': True
        })





