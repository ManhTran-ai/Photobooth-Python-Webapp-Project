"""
Image processing module for photobooth
Handles image manipulation including flipping and filtering
"""
from PIL import Image, ImageEnhance, ImageFilter
import io
import os


class ImageProcessor:
    """Handle image processing operations"""

    @staticmethod
    def flip_horizontal(image):
        """
        Flip image horizontally (fix mirroring for front camera)
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image object flipped horizontally
        """
        # Use Transpose enum for newer Pillow versions, fallback to constant
        try:
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        except AttributeError:
            # Fallback for older Pillow versions
            return image.transpose(Image.FLIP_LEFT_RIGHT)

    @staticmethod
    def apply_filter(image, filter_name, flip_if_front_camera=False):
        """
        Apply filter to image and optionally flip for front camera

        Args:
            image: PIL Image object
            filter_name: Name of filter to apply (currently only 'none' is supported)
            flip_if_front_camera: If True, flip image horizontally before applying filter

        Returns:
            PIL Image object with filter applied (currently only flip is supported)
        """
        # Flip if front camera (to fix mirroring)
        if flip_if_front_camera:
            image = ImageProcessor.flip_horizontal(image)

        # For now, only 'none' filter is supported (flip only)
        # Filter processing is handled by FilterEngine class
        return image


    @staticmethod
    def save_image(image, filepath, quality=90):
        """
        Save image to filepath
        
        Args:
            image: PIL Image object
            filepath: Path where to save the image
            quality: JPEG quality (1-100)
            
        Returns:
            str: Path where image was saved
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert to RGB if saving as JPEG
        if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(filepath, 'JPEG', quality=quality)
        else:
            image.save(filepath)
        
        return filepath

    @staticmethod
    def create_thumbnail(image, size=(200, 200)):
        """
        Create thumbnail from image
        
        Args:
            image: PIL Image object
            size: Tuple (width, height) for thumbnail size
            
        Returns:
            PIL Image object (thumbnail)
        """
        # Use Resampling enum for newer Pillow versions, fallback to LANCZOS constant
        try:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        except AttributeError:
            # Fallback for older Pillow versions
            image.thumbnail(size, Image.LANCZOS)
        return image

    @staticmethod
    def process_uploaded_image(image_data, filter_name='none', flip_if_front_camera=True):
        """
        Process uploaded image: apply flip and filter
        
        Args:
            image_data: Bytes of image data
            filter_name: Name of filter to apply
            flip_if_front_camera: If True, flip image horizontally
            
        Returns:
            PIL Image object
        """
        # Load image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply processing
        processed_image = ImageProcessor.apply_filter(image, filter_name, flip_if_front_camera)
        
        return processed_image

