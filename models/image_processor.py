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
            filter_name: Name of filter to apply ('none', 'sepia', 'grayscale', 'vintage', 'bright', 'contrast')
            flip_if_front_camera: If True, flip image horizontally before applying filter
            
        Returns:
            PIL Image object with filter applied
        """
        # Flip if front camera (to fix mirroring)
        if flip_if_front_camera:
            image = ImageProcessor.flip_horizontal(image)

        # Apply filter
        if filter_name == 'none':
            return image
        elif filter_name == 'sepia':
            return ImageProcessor._apply_sepia(image)
        elif filter_name == 'grayscale':
            return ImageProcessor._apply_grayscale(image)
        elif filter_name == 'vintage':
            return ImageProcessor._apply_vintage(image)
        elif filter_name == 'bright':
            return ImageProcessor._apply_bright(image)
        elif filter_name == 'contrast':
            return ImageProcessor._apply_contrast(image)
        else:
            return image

    @staticmethod
    def _apply_sepia(image):
        """Apply sepia filter"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply sepia tone
        width, height = image.size
        pixels = image.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
        
        return image

    @staticmethod
    def _apply_grayscale(image):
        """Apply grayscale filter"""
        return image.convert('L').convert('RGB')

    @staticmethod
    def _apply_vintage(image):
        """Apply vintage filter"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply contrast, brightness, and saturation adjustments
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.9)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.8)
        
        # Apply slight sepia
        return ImageProcessor._apply_sepia(image)

    @staticmethod
    def _apply_bright(image):
        """Apply bright filter"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        return image

    @staticmethod
    def _apply_contrast(image):
        """Apply contrast filter"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
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

