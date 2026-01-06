"""
Filter Engine with 15+ professional filters
Uses OpenCV and Pillow for image processing
"""
import cv2
import numpy as np
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps


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
        elif filter_name == 'soft_skin':
            result = FilterEngine._apply_soft_skin(image)
        elif filter_name == 'pastel_glow':
            result = FilterEngine._apply_pastel_glow(image)
        elif filter_name == 'sakura':
            result = FilterEngine._apply_sakura(image)
        elif filter_name == 'sparkle':
            result = FilterEngine._apply_sparkle(image)
        elif filter_name == 'rainbow_leak':
            result = FilterEngine._apply_rainbow_leak(image)
        elif filter_name == 'heart_bokeh':
            result = FilterEngine._apply_heart_bokeh(image)
        elif filter_name == 'polaroid':
            result = FilterEngine._apply_polaroid(image)
        elif filter_name == 'comic_pastel':
            result = FilterEngine._apply_comic_pastel(img_cv)
        elif filter_name == 'cool_mint':
            result = FilterEngine._apply_cool_mint(image)
        elif filter_name == 'warm_peach':
            result = FilterEngine._apply_warm_peach(image)
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
        elif filter_name == 'smart_beauty':
            result = FilterEngine._apply_smart_beauty(image)
        elif filter_name == 'face_glow':
            result = FilterEngine._apply_face_glow(image)
        elif filter_name == 'portrait_pro':
            result = FilterEngine._apply_portrait_pro(image)
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
    
    # HELPERS
    @staticmethod
    def _screen_blend(base_img, blur_img):
        """Screen blend two PIL images of the same size"""
        base_arr = np.asarray(base_img).astype(np.float32)
        blur_arr = np.asarray(blur_img).astype(np.float32)
        blended = 255 - ((255 - base_arr) * (255 - blur_arr) / 255)
        return Image.fromarray(np.clip(blended, 0, 255).astype('uint8'))

    @staticmethod
    def _vignette_mask(size, strength=0.6):
        """Create a radial vignette mask"""
        width, height = size
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x, y)
        radius = np.sqrt(xv**2 + yv**2)
        mask = 1 - np.clip(radius * strength, 0, 1)
        mask = (mask * 255).astype('uint8')
        return Image.fromarray(mask, mode='L')

    @staticmethod
    def _apply_tint(image, rgb_multiplier):
        """Apply per-channel multiplier tint"""
        arr = np.array(image).astype(np.float32)
        arr *= np.array(rgb_multiplier, dtype=np.float32)
        arr = np.clip(arr, 0, 255).astype('uint8')
        return Image.fromarray(arr)

    # PHOTObooth FILTERS
    @staticmethod
    def _apply_soft_skin(image):
        """Smooth skin and gently brighten"""
        cv_img = FilterEngine._pil_to_cv2(image)
        smooth = cv2.bilateralFilter(cv_img, 9, 85, 85)
        smooth = cv2.bilateralFilter(smooth, 9, 85, 85)
        pil_img = FilterEngine._cv2_to_pil(smooth)
        pil_img = ImageEnhance.Brightness(pil_img).enhance(1.06)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(0.96)
        return pil_img

    @staticmethod
    def _apply_pastel_glow(image):
        """Pastel tint with bloom/screen glow"""
        base = image.convert('RGB')
        base = ImageEnhance.Color(base).enhance(1.08)
        base = ImageEnhance.Brightness(base).enhance(1.05)
        blur = base.filter(ImageFilter.GaussianBlur(radius=8))
        glow = FilterEngine._screen_blend(base, blur)
        return FilterEngine._apply_tint(glow, (1.03, 0.98, 1.05))

    @staticmethod
    def _apply_sakura(image):
        """Soft pink hue with subtle falling petals"""
        tinted = FilterEngine._apply_tint(image, (1.05, 0.97, 1.03))
        base = tinted.convert('RGBA')
        overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rng = random.Random(7)
        width, height = base.size
        for _ in range(40):
            x = rng.randint(0, width)
            y = rng.randint(0, height)
            size = rng.randint(12, 28)
            color = (255, rng.randint(170, 205), rng.randint(190, 220), rng.randint(35, 70))
            draw.ellipse((x, y, x + size, y + size * 0.6), fill=color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(2))
        result = Image.alpha_composite(base, overlay)
        return result.convert('RGB')

    @staticmethod
    def _apply_sparkle(image):
        """Bright pastel base with soft sparkles"""
        base = ImageEnhance.Brightness(image).enhance(1.05).convert('RGBA')
        overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rng = random.Random(13)
        width, height = base.size
        for _ in range(55):
            x = rng.randint(0, width)
            y = rng.randint(0, height)
            size = rng.randint(6, 14)
            alpha = rng.randint(90, 170)
            color = (255, rng.randint(230, 255), rng.randint(200, 240), alpha)
            # simple star cross
            draw.line((x - size, y, x + size, y), fill=color, width=2)
            draw.line((x, y - size, x, y + size), fill=color, width=2)
            draw.ellipse((x - size // 2, y - size // 2, x + size // 2, y + size // 2), fill=color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(0.8))
        blended = Image.alpha_composite(base, overlay)
        return blended.convert('RGB')

    @staticmethod
    def _apply_rainbow_leak(image):
        """Rainbow light leak from edge"""
        base = image.convert('RGBA')
        width, height = base.size
        gradient = np.linspace(0, 1, width, dtype=np.float32)
        colors = np.array([
            [255, 120, 180],
            [255, 200, 140],
            [140, 200, 255]
        ], dtype=np.float32)
        mix = gradient[:, None]  # shape (w,1)
        color_interp = colors[0] * (1 - mix) + colors[-1] * mix
        overlay = np.zeros((height, width, 4), dtype=np.float32)
        for i in range(width):
            overlay[:, i, :3] = color_interp[i]
            overlay[:, i, 3] = 90 * gradient[i] + 30
        overlay_img = Image.fromarray(np.clip(overlay, 0, 255).astype('uint8'), mode='RGBA')
        result = Image.alpha_composite(base, overlay_img)
        result = ImageEnhance.Brightness(result).enhance(1.03)
        return result.convert('RGB')

    @staticmethod
    def _apply_heart_bokeh(image):
        """Heart-shaped soft bokeh overlay"""
        base = ImageEnhance.Brightness(image).enhance(1.04).convert('RGBA')
        overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rng = random.Random(19)
        width, height = base.size
        for _ in range(45):
            x = rng.randint(0, width)
            y = rng.randint(0, height)
            size = rng.randint(16, 38)
            alpha = rng.randint(30, 70)
            color = (255, rng.randint(170, 210), rng.randint(190, 230), alpha)
            # draw simple heart using polygon
            shape = [
                (x, y + size),
                (x - size, y + size // 3),
                (x - size // 2, y - size // 3),
                (x, y + size // 5),
                (x + size // 2, y - size // 3),
                (x + size, y + size // 3),
            ]
            draw.polygon(shape, fill=color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(3))
        blended = Image.alpha_composite(base, overlay)
        return blended.convert('RGB')

    @staticmethod
    def _apply_polaroid(image):
        """Faded warm tone with vignette and frame"""
        faded = ImageEnhance.Contrast(image).enhance(0.9)
        faded = ImageEnhance.Brightness(faded).enhance(1.03)
        warm = FilterEngine._apply_tint(faded, (1.05, 1.02, 0.95))
        vignette = FilterEngine._vignette_mask(warm.size, strength=0.9)
        vignette_img = ImageOps.colorize(vignette, black="#000000", white="#ffffff").convert('RGB')
        vignette_img = ImageEnhance.Brightness(vignette_img).enhance(0.6)
        base_arr = np.array(warm).astype(np.float32)
        vig_arr = np.array(vignette_img).astype(np.float32) / 255
        combined = base_arr * (0.6 + 0.4 * vig_arr)
        framed = Image.fromarray(np.clip(combined, 0, 255).astype('uint8'))
        # subtle border
        frame_width = max(8, min(warm.size) // 40)
        return ImageOps.expand(framed, border=frame_width, fill="#f7f7f2")

    @staticmethod
    def _apply_comic_pastel(cv2_image):
        """Pastel comic look with gentle edges"""
        smooth = cv2.bilateralFilter(cv2_image, 9, 120, 120)
        color = cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB)
        color = np.clip(color * np.array([1.05, 1.0, 1.1]), 0, 255).astype(np.uint8)
        edges = cv2.Canny(smooth, 60, 120)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
        edges_inv = cv2.bitwise_not(edges)
        edges_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2RGB)
        combined = cv2.bitwise_and(color, edges_colored)
        pil = Image.fromarray(combined)
        pil = ImageEnhance.Color(pil).enhance(1.05)
        return pil

    @staticmethod
    def _apply_cool_mint(image):
        """Cool mint tone with soft contrast"""
        arr = np.array(image).astype(np.float32)
        arr[:, :, 1] *= 1.07  # green
        arr[:, :, 2] *= 1.05  # blue
        arr[:, :, 0] *= 0.97  # red
        arr = np.clip(arr, 0, 255).astype('uint8')
        img = Image.fromarray(arr)
        img = ImageEnhance.Contrast(img).enhance(0.96)
        img = ImageEnhance.Brightness(img).enhance(1.04)
        return img

    @staticmethod
    def _apply_warm_peach(image):
        """Warm peach tone with gentle grain"""
        arr = np.array(image).astype(np.float32)
        arr[:, :, 0] *= 1.06
        arr[:, :, 1] *= 1.02
        arr[:, :, 2] *= 0.96
        rng = np.random.default_rng(21)
        noise = rng.normal(0, 6, arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype('uint8')
        img = Image.fromarray(arr)
        img = ImageEnhance.Brightness(img).enhance(1.02)
        img = ImageEnhance.Color(img).enhance(1.05)
        return img

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
    
    # ============== SMART BEAUTY FILTERS (Face Detection Based) ==============

    @staticmethod
    def _apply_smart_beauty(image):
        """
        Smart Beauty Filter - Chỉ làm mịn da vùng khuôn mặt

        Algorithm:
        1. Detect faces using DNN
        2. Tạo mask mềm cho vùng mặt
        3. Áp dụng bilateral filter chỉ cho vùng mặt
        4. Blend với ảnh gốc để giữ chi tiết background

        Ưu điểm so với soft_skin thông thường:
        - Không làm mờ background
        - Giữ được texture tóc, quần áo
        - Tự nhiên hơn vì chỉ smooth vùng da
        """
        try:
            from models.face_detector import get_detector
            detector = get_detector()
            faces = detector.detect_faces(image, confidence_threshold=0.4)

            if not faces:
                # Fallback to regular soft_skin if no face detected
                return FilterEngine._apply_soft_skin(image)

            # Convert to numpy for processing
            img_array = np.array(image).astype(np.float32)
            result = img_array.copy()

            # Process each face
            for face in faces:
                # Get face mask
                mask = detector.get_face_mask(image, face, feather=15)
                mask_array = np.array(mask).astype(np.float32) / 255.0

                # Expand mask to 3 channels
                mask_3ch = np.stack([mask_array] * 3, axis=-1)

                # Apply bilateral filter to entire image (will be masked)
                cv_img = FilterEngine._pil_to_cv2(image)
                smooth = cv2.bilateralFilter(cv_img, 9, 75, 75)
                smooth = cv2.bilateralFilter(smooth, 9, 75, 75)
                smooth_rgb = cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB).astype(np.float32)

                # Blend: result = original * (1-mask) + smooth * mask
                result = result * (1 - mask_3ch) + smooth_rgb * mask_3ch

            # Brightness boost
            result = np.clip(result * 1.03, 0, 255).astype(np.uint8)
            return Image.fromarray(result)

        except Exception as e:
            print(f"Smart beauty filter error: {e}")
            return FilterEngine._apply_soft_skin(image)

    @staticmethod
    def _apply_face_glow(image):
        """
        Face Glow Filter - Thêm hiệu ứng glow mềm quanh khuôn mặt

        Algorithm:
        1. Detect faces
        2. Tạo radial gradient glow từ tâm mặt
        3. Screen blend glow với ảnh gốc
        4. Tăng nhẹ saturation và brightness

        Hiệu ứng: Khuôn mặt sáng lên, tạo cảm giác tươi tắn
        """
        try:
            from models.face_detector import get_detector
            detector = get_detector()
            face = detector.detect_largest_face(image, confidence_threshold=0.4)

            if not face:
                return FilterEngine._apply_pastel_glow(image)

            img_array = np.array(image).astype(np.float32)
            h, w = img_array.shape[:2]

            cx, cy = face['center']
            face_w = face['bbox'][2]

            # Create radial gradient from face center
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)

            # Glow radius based on face size
            glow_radius = face_w * 1.5

            # Create soft falloff
            glow = np.clip(1 - (dist / glow_radius), 0, 1)
            glow = glow ** 0.5  # Softer falloff
            glow = (glow * 40).astype(np.float32)  # Intensity

            # Add glow to image
            glow_3ch = np.stack([glow] * 3, axis=-1)
            result = np.clip(img_array + glow_3ch, 0, 255)

            # Enhance colors slightly
            result_img = Image.fromarray(result.astype(np.uint8))
            result_img = ImageEnhance.Color(result_img).enhance(1.08)
            result_img = ImageEnhance.Brightness(result_img).enhance(1.02)

            return result_img

        except Exception as e:
            print(f"Face glow filter error: {e}")
            return FilterEngine._apply_pastel_glow(image)

    @staticmethod
    def _apply_portrait_pro(image):
        """
        Portrait Pro Filter - Kết hợp nhiều kỹ thuật chuyên nghiệp

        Algorithm:
        1. Smart skin smoothing (chỉ vùng mặt)
        2. Eye brightening (tăng sáng vùng mắt)
        3. Subtle face contouring
        4. Overall color grading (warm portrait tone)

        Đây là filter cao cấp nhất, tổng hợp nhiều kỹ thuật
        """
        try:
            from models.face_detector import get_detector
            detector = get_detector()
            faces = detector.detect_faces(image, confidence_threshold=0.4)

            if not faces:
                # Fallback: warm tone + soft skin
                img = FilterEngine._apply_soft_skin(image)
                return FilterEngine._apply_warm_tone(img)

            # Step 1: Smart skin smoothing
            img_array = np.array(image).astype(np.float32)
            cv_img = FilterEngine._pil_to_cv2(image)

            # Apply bilateral filter
            smooth = cv2.bilateralFilter(cv_img, 9, 60, 60)
            smooth_rgb = cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB).astype(np.float32)

            # Create combined face mask
            h, w = img_array.shape[:2]
            combined_mask = np.zeros((h, w), dtype=np.float32)

            for face in faces:
                mask = detector.get_face_mask(image, face, feather=20)
                mask_array = np.array(mask).astype(np.float32) / 255.0
                combined_mask = np.maximum(combined_mask, mask_array)

            mask_3ch = np.stack([combined_mask] * 3, axis=-1)

            # Blend smooth skin
            result = img_array * (1 - mask_3ch * 0.7) + smooth_rgb * (mask_3ch * 0.7)

            # Step 2: Subtle warming for portrait look
            # Increase warmth in midtones
            result[:, :, 0] = np.clip(result[:, :, 0] * 1.03, 0, 255)  # Red +3%
            result[:, :, 2] = np.clip(result[:, :, 2] * 0.97, 0, 255)  # Blue -3%

            # Step 3: Contrast enhancement in face region
            mean_brightness = np.mean(result * mask_3ch)
            contrast_boost = result + (result - mean_brightness) * 0.1 * mask_3ch
            result = np.clip(contrast_boost, 0, 255)

            # Step 4: Final color grading
            result_img = Image.fromarray(result.astype(np.uint8))
            result_img = ImageEnhance.Color(result_img).enhance(1.05)
            result_img = ImageEnhance.Brightness(result_img).enhance(1.02)

            return result_img

        except Exception as e:
            print(f"Portrait pro filter error: {e}")
            img = FilterEngine._apply_soft_skin(image)
            return FilterEngine._apply_warm_tone(img)

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
                'name': 'soft_skin',
                'category': 'photobooth',
                'display_name': 'Soft Skin',
                'description': 'Smooth skin with gentle brightness'
            },
            {
                'name': 'pastel_glow',
                'category': 'photobooth',
                'display_name': 'Pastel Glow',
                'description': 'Pastel tint with dreamy glow'
            },
            {
                'name': 'sakura',
                'category': 'photobooth',
                'display_name': 'Sakura',
                'description': 'Pink hue with floating petals'
            },
            {
                'name': 'sparkle',
                'category': 'photobooth',
                'display_name': 'Sparkle',
                'description': 'Bright look with soft sparkles'
            },
            {
                'name': 'rainbow_leak',
                'category': 'photobooth',
                'display_name': 'Rainbow Leak',
                'description': 'Rainbow light leak glow'
            },
            {
                'name': 'heart_bokeh',
                'category': 'photobooth',
                'display_name': 'Heart Bokeh',
                'description': 'Heart-shaped soft bokeh overlay'
            },
            {
                'name': 'polaroid',
                'category': 'photobooth',
                'display_name': 'Polaroid',
                'description': 'Faded warm tone with frame'
            },
            {
                'name': 'comic_pastel',
                'category': 'photobooth',
                'display_name': 'Comic Pastel',
                'description': 'Soft edges with pastel fill'
            },
            {
                'name': 'cool_mint',
                'category': 'photobooth',
                'display_name': 'Cool Mint',
                'description': 'Cool mint tone and soft contrast'
            },
            {
                'name': 'warm_peach',
                'category': 'photobooth',
                'display_name': 'Warm Peach',
                'description': 'Warm peach tone with gentle grain'
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
            },
            # AI-Powered Face Detection Filters
            {
                'name': 'smart_beauty',
                'category': 'ai_beauty',
                'display_name': 'Smart Beauty',
                'description': 'AI skin smoothing - chỉ làm mịn vùng mặt'
            },
            {
                'name': 'face_glow',
                'category': 'ai_beauty',
                'display_name': 'Face Glow',
                'description': 'AI glow effect - tạo ánh sáng mềm quanh mặt'
            },
            {
                'name': 'portrait_pro',
                'category': 'ai_beauty',
                'display_name': 'Portrait Pro',
                'description': 'AI portrait enhancement - làm đẹp chuyên nghiệp'
            }
        ]

        for item in filters:
            item['example_thumbnail'] = f'filter_previews/{item["name"]}.jpg'

        return filters

