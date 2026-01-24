
import cv2
import numpy as np
from PIL import Image
import os

# Path to DNN model files
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'dnn_models')
PROTOTXT_PATH = os.path.join(MODEL_DIR, 'deploy.prototxt')
CAFFEMODEL_PATH = os.path.join(MODEL_DIR, 'res10_300x300_ssd_iter_140000.caffemodel')


class FaceDetector:


    _instance = None
    _net = None

    def __new__(cls):
        """Singleton pattern để tránh load model nhiều lần"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load DNN model từ file"""
        if not os.path.exists(PROTOTXT_PATH):
            raise FileNotFoundError(f"Prototxt file not found: {PROTOTXT_PATH}")
        if not os.path.exists(CAFFEMODEL_PATH):
            raise FileNotFoundError(f"Caffemodel file not found: {CAFFEMODEL_PATH}")

        self._net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, CAFFEMODEL_PATH)
        # Prefer CPU for compatibility
        self._net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self._net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect_faces(self, image, confidence_threshold=0.5):

        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
            # PIL is RGB, convert to BGR for OpenCV
            if len(img_array.shape) == 3:
                # Handle RGBA by converting to RGB first
                if img_array.shape[2] == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                if img_array.shape[2] == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_array = image.copy()

        h, w = img_array.shape[:2]

        # Create blob from image
        # Mean subtraction values for face detection model
        blob = cv2.dnn.blobFromImage(
            img_array,
            scalefactor=1.0,
            size=(300, 300),
            mean=(104.0, 177.0, 123.0),
            swapRB=False,
            crop=False
        )

        # Forward pass
        self._net.setInput(blob)
        detections = self._net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > confidence_threshold:
                # Get bounding box coordinates (normalized 0-1)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype(int)

                # Ensure coordinates are within image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                face_w = x2 - x1
                face_h = y2 - y1

                # Skip invalid detections
                if face_w <= 0 or face_h <= 0:
                    continue

                faces.append({
                    'bbox': (x1, y1, face_w, face_h),
                    'confidence': float(confidence),
                    'center': (x1 + face_w // 2, y1 + face_h // 2),
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                })

        # Sort by confidence descending
        faces.sort(key=lambda x: x['confidence'], reverse=True)
        return faces

    def detect_largest_face(self, image, confidence_threshold=0.5):

        faces = self.detect_faces(image, confidence_threshold)
        if not faces:
            return None

        # Find largest face by area
        largest = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        return largest

    def get_face_region(self, image, face, padding=0.3):

        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        x, y, w, h = face['bbox']
        img_w, img_h = image.size

        # Calculate padding
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        # Expand region with padding
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(img_w, x + w + pad_w)
        y2 = min(img_h, y + h + pad_h)

        return image.crop((x1, y1, x2, y2))

    def auto_crop_portrait(self, image, target_ratio=3/4, padding=0.4):

        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        face = self.detect_largest_face(image)
        if not face:
            return image

        img_w, img_h = image.size
        x, y, w, h = face['bbox']
        cx, cy = face['center']

        # Calculate crop dimensions based on face size
        face_size = max(w, h)

        # Crop width should be face_size * (1 + 2*padding)
        crop_w = int(face_size * (1 + 2 * padding))
        crop_h = int(crop_w * target_ratio)

        # Ensure minimum size
        crop_w = max(crop_w, 200)
        crop_h = max(crop_h, int(200 * target_ratio))

        # Ensure crop doesn't exceed image
        crop_w = min(crop_w, img_w)
        crop_h = min(crop_h, img_h)

        # Position face at 1/3 from top (rule of thirds)
        face_y_target = crop_h // 3

        # Calculate crop origin
        crop_x = cx - crop_w // 2
        crop_y = cy - face_y_target

        # Adjust if out of bounds
        crop_x = max(0, min(crop_x, img_w - crop_w))
        crop_y = max(0, min(crop_y, img_h - crop_h))

        return image.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

    def get_face_mask(self, image, face, feather=10):

        if isinstance(image, Image.Image):
            img_w, img_h = image.size
        else:
            img_h, img_w = image.shape[:2]

        x, y, w, h = face['bbox']
        cx, cy = face['center']

        # Create elliptical mask for face
        mask = np.zeros((img_h, img_w), dtype=np.float32)

        # Expand face region slightly for mask
        mask_w = int(w * 1.2)
        mask_h = int(h * 1.3)  # Taller to include forehead

        # Create ellipse mask
        y_coords, x_coords = np.ogrid[:img_h, :img_w]

        # Ellipse equation: ((x-cx)/a)^2 + ((y-cy)/b)^2 <= 1
        a = mask_w / 2
        b = mask_h / 2

        ellipse = ((x_coords - cx) / a) ** 2 + ((y_coords - cy) / b) ** 2
        mask[ellipse <= 1] = 1.0

        # Apply Gaussian blur for feathering
        if feather > 0:
            mask = cv2.GaussianBlur(mask, (0, 0), feather)

        # Normalize to 0-255
        mask = (mask * 255).astype(np.uint8)

        return Image.fromarray(mask, mode='L')

    def draw_faces(self, image, faces=None, color=(0, 255, 0), thickness=2):

        if isinstance(image, Image.Image):
            img_array = np.array(image)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_array = image.copy()

        if faces is None:
            faces = self.detect_faces(image)

        for face in faces:
            x, y, w, h = face['bbox']
            conf = face['confidence']

            # Draw rectangle
            cv2.rectangle(img_array, (x, y), (x + w, y + h), color, thickness)

            # Draw confidence
            label = f"{conf:.2f}"
            cv2.putText(img_array, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

        # Convert back to PIL
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    def get_face_positions_for_stickers(self, image, sticker_type='hat'):
        """
        Get optimal positions for placing stickers on detected faces.

        Supported sticker types:
        - hat: Mũ - đặt trên đầu
        - glasses: Kính - đặt ở mắt
        - ears: Tai thỏ - đặt trên đầu
        - mustache: Râu - đặt dưới mũi
        - noel_hat: Nón Noel - đặt trên đầu, nghiêng
        - bow: Nơ - đặt trên đầu, bên phải
        """
        faces = self.detect_faces(image)
        positions = []

        for face in faces:
            x, y, w, h = face['bbox']
            cx, cy = face['center']

            if sticker_type == 'hat':
                # Mũ - đặt trên đầu, căn giữa
                pos = {
                    'x': cx,
                    'y': y - int(h * 0.15),  # Trên đầu
                    'scale': w / 100,
                    'anchor': 'bottom-center'
                }
            elif sticker_type == 'noel_hat':
                # Nón Noel - đặt trên đầu, hơi nghiêng về bên phải
                pos = {
                    'x': cx + int(w * 0.1),  # Lệch phải một chút
                    'y': y - int(h * 0.25),  # Trên đầu cao hơn
                    'scale': w / 80,
                    'anchor': 'bottom-center',
                    'rotation': -15  # Nghiêng sang phải
                }
            elif sticker_type == 'glasses':
                # Kính - đặt ở vị trí mắt (khoảng 1/3 từ trên xuống)
                pos = {
                    'x': cx,
                    'y': y + int(h * 0.35),
                    'scale': w / 80,
                    'anchor': 'center'
                }
            elif sticker_type == 'ears':
                # Tai thỏ - đặt trên đầu
                pos = {
                    'x': cx,
                    'y': y - int(h * 0.2),
                    'scale': w / 70,
                    'anchor': 'bottom-center'
                }
            elif sticker_type == 'mustache':
                # Râu - đặt dưới mũi (khoảng 2/3 từ trên xuống)
                pos = {
                    'x': cx,
                    'y': y + int(h * 0.68),
                    'scale': w / 100,
                    'anchor': 'center'
                }
            elif sticker_type == 'bow':
                # Nơ - đặt trên đầu, bên phải
                pos = {
                    'x': cx + int(w * 0.35),  # Bên phải đầu
                    'y': y - int(h * 0.05),  # Trên đầu
                    'scale': w / 120,
                    'anchor': 'center'
                }
            else:
                # Default: center of face
                pos = {
                    'x': cx,
                    'y': cy,
                    'scale': w / 100,
                    'anchor': 'center'
                }

            pos['face_bbox'] = (x, y, w, h)
            pos['confidence'] = face['confidence']
            positions.append(pos)

        return positions


# Singleton instance for easy import
_detector = None

def get_detector():
    """Get singleton FaceDetector instance"""
    global _detector
    if _detector is None:
        _detector = FaceDetector()
    return _detector


def detect_faces(image, confidence_threshold=0.5):
    """Convenience function to detect faces"""
    return get_detector().detect_faces(image, confidence_threshold)


def detect_largest_face(image, confidence_threshold=0.5):
    """Convenience function to detect largest face"""
    return get_detector().detect_largest_face(image, confidence_threshold)


def auto_crop_portrait(image, target_ratio=3/4, padding=0.4):
    """Convenience function to auto crop portrait"""
    return get_detector().auto_crop_portrait(image, target_ratio, padding)

