"""
API routes for photobooth application
"""
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models.image_processor import ImageProcessor
from datetime import datetime
import os
import uuid

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


@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Photobooth API is running'
    })

