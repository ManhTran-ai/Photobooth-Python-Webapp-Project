"""
Filter Engine with 15+ professional filters
Uses OpenCV and Pillow for image processing
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io


class FilterEngine:
    """Professional filter engine with multiple filter categories"""
    
    @staticmethod
    def apply_filter(image, filter_name):
        """
        Apply a filter to a PIL Image
        
        Args:
            image: PIL Image object
            filter_name: Name of the filter to apply
            
        Returns:
            PIL Image object with filter applied
        """
        # Convert PIL to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL to numpy array for OpenCV processing
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Apply filter based on name
        if filter_name == 'none':
            result = image
        elif filter_name == 'grayscale':
            result = FilterEngine._apply_grayscale(image)
        elif filter_name == 'sepia':
            result = FilterEngine._apply_sepia(image)
        elif filter_name == 'brightness':
            result = FilterEngine._apply_brightness(image)
        elif filter_name == 'contrast':
            result = FilterEngine._apply_contrast(image)
        elif filter_name == 'cartoon':
            result = FilterEngine._apply_cartoon(img_cv)
        elif filter_name == 'pencil_sketch':
            result = FilterEngine._apply_pencil_sketch(img_cv)
        elif filter_name == 'oil_painting':
            result = FilterEngine._apply_oil_painting(img_cv)
        elif filter_name == 'nashville':
            result = FilterEngine._apply_nashville(image)
        elif filter_name == 'valencia':
            result = FilterEngine._apply_valencia(image)
        elif filter_name == 'xpro2':
            result = FilterEngine._apply_xpro2(image)
        elif filter_name == 'walden':
            result = FilterEngine._apply_walden(image)
        elif filter_name == 'kelvin':
            result = FilterEngine._apply_kelvin(image)
        elif filter_name == 'blur':
            result = FilterEngine._apply_blur(image)
        elif filter_name == 'edge_detection':
            result = FilterEngine._apply_edge_detection(img_cv)
        elif filter_name == 'vintage':
            result = FilterEngine._apply_vintage(image)
        elif filter_name == 'cool_tone':
            result = FilterEngine._apply_cool_tone(image)
        elif filter_name == 'warm_tone':
            result = FilterEngine._apply_warm_tone(image)
        else:
            result = image
        
        return result
    
    @staticmethod
    def _pil_to_cv2(pil_image):
        """Convert PIL Image to OpenCV format"""
        img_array = np.array(pil_image)
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def _cv2_to_pil(cv2_image):
        """Convert OpenCV image to PIL format"""
        img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
    
    # BASIC FILTERS
    @staticmethod
    def _apply_grayscale(image):
        """Convert to grayscale"""
        return image.convert('L').convert('RGB')
    
    @staticmethod
    def _apply_sepia(image):
        """Apply sepia tone"""
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
    def _apply_brightness(image):
        """Increase brightness"""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.2)
    
    @staticmethod
    def _apply_contrast(image):
        """Increase contrast"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.3)
    
    # ARTISTIC FILTERS
    @staticmethod
    def _apply_cartoon(cv2_image):
        """Apply cartoon effect using bilateral filter and edge detection"""
        # Apply bilateral filter multiple times for cartoon effect
        filtered = cv2.bilateralFilter(cv2_image, 9, 300, 300)
        filtered = cv2.bilateralFilter(filtered, 9, 300, 300)
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # Convert edges to color
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine filtered image with edges
        cartoon = cv2.bitwise_and(filtered, edges_color)
        
        return FilterEngine._cv2_to_pil(cartoon)
    
    @staticmethod
    def _apply_pencil_sketch(cv2_image):
        """Apply pencil sketch effect"""
        gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blur = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        sketch_color = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        return FilterEngine._cv2_to_pil(sketch_color)
    
    @staticmethod
    def _apply_oil_painting(cv2_image):
        """Apply oil painting effect"""
        try:
            # Try using xphoto module if available without shadowing global cv2
            from cv2 import xphoto as cv2_xphoto
            oil = cv2_xphoto.oilPainting(cv2_image, 7, 1)
        except (AttributeError, ImportError):
            # Fallback to bilateral filter for oil painting effect
            oil = cv2.bilateralFilter(cv2_image, 5, 50, 50)
            oil = cv2.bilateralFilter(oil, 5, 50, 50)
        return FilterEngine._cv2_to_pil(oil)
    
    # INSTAGRAM-STYLE FILTERS
    @staticmethod
    def _apply_nashville(image):
        """Instagram Nashville filter - warm, high contrast"""
        enhancer = ImageEnhance.Contrast(image)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        # Add slight sepia
        return FilterEngine._apply_sepia(img)
    
    @staticmethod
    def _apply_valencia(image):
        """Instagram Valencia filter - bright, warm"""
        enhancer = ImageEnhance.Brightness(image)
        img = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.1)
    
    @staticmethod
    def _apply_xpro2(image):
        """Instagram X-Pro II filter - high contrast, cool tones"""
        enhancer = ImageEnhance.Contrast(image)
        img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.9)
        # Add cool tone
        return FilterEngine._apply_cool_tone(img)
    
    @staticmethod
    def _apply_walden(image):
        """Instagram Walden filter - warm, vintage"""
        enhancer = ImageEnhance.Brightness(image)
        img = enhancer.enhance(0.95)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        # Apply warm tone and slight sepia
        img = FilterEngine._apply_warm_tone(img)
        return FilterEngine._apply_sepia(img)
    
    @staticmethod
    def _apply_kelvin(image):
        """Instagram Kelvin filter - warm orange tone"""
        enhancer = ImageEnhance.Color(image)
        img = enhancer.enhance(1.2)
        # Strong warm tone
        return FilterEngine._apply_warm_tone(img)
    
    # EFFECT FILTERS
    @staticmethod
    def _apply_blur(image):
        """Apply blur effect"""
        return image.filter(ImageFilter.GaussianBlur(radius=2))
    
    @staticmethod
    def _apply_edge_detection(cv2_image):
        """Apply edge detection"""
        gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return FilterEngine._cv2_to_pil(edges_color)
    
    @staticmethod
    def _apply_vintage(image):
        """Apply vintage filter"""
        enhancer = ImageEnhance.Contrast(image)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.9)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        return FilterEngine._apply_sepia(img)
    
    @staticmethod
    def _apply_cool_tone(image):
        """Apply cool blue tone"""
        img_array = np.array(image)
        # Increase blue channel, decrease red channel
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 0.9, 0, 255)  # Red
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 1.1, 0, 255)  # Blue
        return Image.fromarray(img_array.astype('uint8'))
    
    @staticmethod
    def _apply_warm_tone(image):
        """Apply warm orange/yellow tone"""
        img_array = np.array(image)
        # Increase red and green channels, decrease blue
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.1, 0, 255)  # Red
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.05, 0, 255)  # Green
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 0.9, 0, 255)  # Blue
        return Image.fromarray(img_array.astype('uint8'))
    
    @staticmethod
    def get_available_filters():
        """Get list of all available filters with metadata"""
        filters = [
            {
                'name': 'none',
                'category': 'basic',
                'display_name': 'Original',
                'description': 'No filter applied'
            },
            {
                'name': 'grayscale',
                'category': 'basic',
                'display_name': 'Grayscale',
                'description': 'Black and white effect'
            },
            {
                'name': 'sepia',
                'category': 'basic',
                'display_name': 'Sepia',
                'description': 'Vintage brown tone'
            },
            {
                'name': 'brightness',
                'category': 'basic',
                'display_name': 'Bright',
                'description': 'Increased brightness'
            },
            {
                'name': 'contrast',
                'category': 'basic',
                'display_name': 'High Contrast',
                'description': 'Enhanced contrast'
            },
            {
                'name': 'cartoon',
                'category': 'artistic',
                'display_name': 'Cartoon',
                'description': 'Animated cartoon style'
            },
            {
                'name': 'pencil_sketch',
                'category': 'artistic',
                'display_name': 'Pencil Sketch',
                'description': 'Hand-drawn sketch effect'
            },
            {
                'name': 'oil_painting',
                'category': 'artistic',
                'display_name': 'Oil Painting',
                'description': 'Classic oil painting style'
            },
            {
                'name': 'nashville',
                'category': 'instagram',
                'display_name': 'Nashville',
                'description': 'Warm, high contrast'
            },
            {
                'name': 'valencia',
                'category': 'instagram',
                'display_name': 'Valencia',
                'description': 'Bright and warm'
            },
            {
                'name': 'xpro2',
                'category': 'instagram',
                'display_name': 'X-Pro II',
                'description': 'High contrast, cool tones'
            },
            {
                'name': 'walden',
                'category': 'instagram',
                'display_name': 'Walden',
                'description': 'Warm vintage look'
            },
            {
                'name': 'kelvin',
                'category': 'instagram',
                'display_name': 'Kelvin',
                'description': 'Warm orange tone'
            },
            {
                'name': 'blur',
                'category': 'effects',
                'display_name': 'Blur',
                'description': 'Soft blur effect'
            },
            {
                'name': 'edge_detection',
                'category': 'effects',
                'display_name': 'Edge Detection',
                'description': 'Highlight edges and contours'
            },
            {
                'name': 'vintage',
                'category': 'effects',
                'display_name': 'Vintage',
                'description': 'Classic vintage style'
            },
            {
                'name': 'cool_tone',
                'category': 'effects',
                'display_name': 'Cool Tone',
                'description': 'Blue/cool color cast'
            },
            {
                'name': 'warm_tone',
                'category': 'effects',
                'display_name': 'Warm Tone',
                'description': 'Orange/warm color cast'
            }
        ]

        for item in filters:
            item['example_thumbnail'] = f'filter_previews/{item["name"]}.jpg'

        return filters

