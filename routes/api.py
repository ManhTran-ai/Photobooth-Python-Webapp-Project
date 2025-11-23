"""
API routes for photobooth application
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from models.image_processor import ImageProcessor
from models.filter_engine import FilterEngine
from models.database import db, Session, Photo, FilterApplied
from datetime import datetime
import os
import uuid
import base64
import io
from PIL import Image

api_bp = Blueprint('api', __name__)


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
        
        return jsonify({
            'success': True,
            'photos': [{
                'id': photo.id,
                'photo_number': photo.photo_number,
                'original_url': f'/api/images/originals/{photo.original_filename}',
                'processed_url': f'/api/images/processed/{photo.processed_filename}',
                'thumbnail_url': f'/api/images/thumbnails/{photo.thumbnail_filename}'
            } for photo in photos]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get photos: {str(e)}'}), 500


@api_bp.route('/filters', methods=['GET'])
def get_filters():
    """Get list of available filters"""
    try:
        filters = FilterEngine.get_available_filters()
        return jsonify({
            'success': True,
            'filters': filters
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get filters: {str(e)}'}), 500


@api_bp.route('/apply-filter', methods=['POST'])
def apply_filter():
    """
    Apply a filter to all photos in a session
    Expects JSON with:
    - session_id: string (UUID)
    - filter_name: string
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        filter_name = data.get('filter_name')
        
        if not session_id or not filter_name:
            return jsonify({'error': 'Missing session_id or filter_name'}), 400
        
        # Verify session exists
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get all photos for the session
        photos = Photo.query.filter_by(session_id=session_id).order_by(Photo.photo_number).all()
        
        if not photos:
            return jsonify({'error': 'No photos found in session'}), 404
        
        processed_images = []
        
        # Apply filter to each photo
        for photo in photos:
            # Load original image
            original_path = os.path.join(
                current_app.config['ORIGINALS_FOLDER'],
                photo.original_filename
            )
            
            if not os.path.exists(original_path):
                continue
            
            # Load image
            image = Image.open(original_path)
            
            # Apply filter
            filtered_image = FilterEngine.apply_filter(image, filter_name)
            
            # Generate new filename for processed version
            name_parts = photo.original_filename.rsplit('.', 1)
            processed_filename = f"{name_parts[0]}_{filter_name}.jpg"
            
            # Save processed image
            processed_path = os.path.join(
                current_app.config['PROCESSED_FOLDER'],
                processed_filename
            )
            ImageProcessor.save_image(filtered_image, processed_path)
            
            # Create and save thumbnail
            thumbnail_image = ImageProcessor.create_thumbnail(filtered_image.copy())
            thumbnail_filename = f"{name_parts[0]}_{filter_name}.jpg"
            thumbnail_path = os.path.join(
                current_app.config['THUMBNAILS_FOLDER'],
                thumbnail_filename
            )
            ImageProcessor.save_image(thumbnail_image, thumbnail_path)
            
            # Update photo record
            photo.processed_filename = processed_filename
            photo.thumbnail_filename = thumbnail_filename
            photo.applied_filter = filter_name
            
            processed_images.append({
                'photo_id': photo.id,
                'photo_number': photo.photo_number,
                'original_url': f'/api/images/originals/{photo.original_filename}',
                'processed_url': f'/api/images/processed/{processed_filename}',
                'thumbnail_url': f'/api/images/thumbnails/{thumbnail_filename}'
            })
        
        # Record filter application
        filter_applied = FilterApplied(
            session_id=session_id,
            filter_name=filter_name
        )
        db.session.add(filter_applied)
        
        # Update session status
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'processed_images': processed_images,
            'filter_name': filter_name
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

