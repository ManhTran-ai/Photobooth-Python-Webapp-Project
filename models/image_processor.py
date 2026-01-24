"""
Image processing module for photobooth
Handles image manipulation including flipping and filtering
"""
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import numpy as np
import cv2


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


    # -------------------------
    # Phase 0: Preprocessing helpers
    # -------------------------
    @staticmethod
    def preprocess_for_model(image, target_size=(160, 160)):
        """
        Prepare a PIL Image for model input: convert to RGB, resize, and
        return a numpy float32 array normalized to [0,1].
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        img = image.resize((int(target_size[0]), int(target_size[1])), Image.LANCZOS)
        arr = np.asarray(img).astype('float32') / 255.0
        return arr

    @staticmethod
    def is_blurry(image, threshold=100.0):
        """
        Heuristic blur detection using variance of Laplacian.
        Returns True if image is considered blurry.
        """
        # Convert PIL Image to grayscale numpy
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        arr = np.asarray(gray)
        # Use OpenCV Laplacian variance
        try:
            var = cv2.Laplacian(arr, cv2.CV_64F).var()
        except Exception:
            # Fallback: compute simple variance of gradient using numpy
            gy, gx = np.gradient(arr.astype('float32'))
            var = (gx ** 2 + gy ** 2).var()
        return float(var) < float(threshold)

    @staticmethod
    def is_low_light(image, brightness_threshold=80):
        """
        Simple brightness check. Returns True if average brightness is below threshold.
        """
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        arr = np.asarray(gray)
        mean_brightness = arr.mean()
        return mean_brightness < brightness_threshold


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

