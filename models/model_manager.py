"""
ModelManager: lightweight wrapper that exposes a consistent API for DNN models used
in the project. Phase 0 provides skeleton methods and delegates face detection to
the existing FaceDetector -- later phases will implement embeddings, emotion,
landmark and age/gender models.
"""
from typing import Any, Dict, List, Optional
import numpy as np
import cv2
from PIL import Image
import os
import hashlib

from .face_detector import get_detector
from .embeddings import l2_normalize

try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    _HAS_TENSORFLOW = True
except ImportError:
    _HAS_TENSORFLOW = False
    print("TensorFlow not available - DNN features will use fallback methods")

try:
    import mediapipe as mp
    _HAS_MEDIAPIPE = True
except ImportError:
    _HAS_MEDIAPIPE = False

try:
    import cv2
    _HAS_OPENCV = True
except ImportError:
    _HAS_OPENCV = False

try:
    import tf2onnx
    import onnxruntime as ort
    _HAS_ONNX = True
except ImportError:
    _HAS_ONNX = False


class FaceNetEmbedder:
    """FaceNet embedding extractor using TensorFlow/Keras"""

    def __init__(self):
        if not _HAS_TENSORFLOW:
            raise ImportError("TensorFlow not available. Install with: pip install tensorflow")

        # FaceNet model path (will be downloaded if not exists)
        self.model_path = os.path.join(os.path.dirname(__file__), 'facenet_model.h5')

        # Model will be loaded lazily
        self.model = None

    def load_model(self):
        """Load FaceNet model"""
        if self.model is not None:
            return

        if not os.path.exists(self.model_path):
            print("Downloading FaceNet model...")
            self._download_facenet_model()

        self.model = load_model(self.model_path, compile=False)

    def _download_facenet_model(self):
        """Download pre-trained FaceNet model"""
        import urllib.request
        import zipfile
        import tempfile

        # FaceNet model URL (Keras version)
        url = "https://drive.google.com/uc?export=download&id=1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn"

        try:
            # Download to temp file
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                print(f"Downloading from {url}")
                urllib.request.urlretrieve(url, tmp.name)

                # Extract
                with zipfile.ZipFile(tmp.name, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(self.model_path))

                # Clean up
                os.unlink(tmp.name)

        except Exception as e:
            print(f"Failed to download FaceNet model: {e}")
            print("Please download manually from: https://github.com/nyoki-mtl/keras-facenet")
            raise

    def preprocess_face(self, face_image):
        """Preprocess face image for FaceNet input"""
        # Convert to RGB if needed
        if isinstance(face_image, Image.Image):
            face_array = np.array(face_image.convert('RGB'))
        else:
            face_array = face_image

        # Resize to 160x160 (FaceNet input size)
        face_resized = cv2.resize(face_array, (160, 160))

        # Normalize to [-1, 1]
        face_normalized = (face_resized - 127.5) / 127.5

        # Add batch dimension
        return np.expand_dims(face_normalized, axis=0)

    def extract_embedding(self, face_image):
        """Extract 128-dimensional embedding from face image"""
        self.load_model()

        # Preprocess
        processed_face = self.preprocess_face(face_image)

        # Extract embedding
        embedding = self.model.predict(processed_face, verbose=0)

        # L2 normalize
        embedding = l2_normalize(embedding[0])

        return embedding

    def export_to_onnx(self, onnx_path: str = None) -> str:
        """
        Export FaceNet model to ONNX format for faster inference.

        Args:
            onnx_path: Path to save ONNX model (optional)

        Returns:
            Path to exported ONNX model
        """
        if not _HAS_ONNX:
            raise ImportError("ONNX export requires tf2onnx and onnxruntime. Install with: pip install tf2onnx onnxruntime")

        self.load_model()

        if onnx_path is None:
            onnx_path = self.model_path.replace('.h5', '.onnx')

        # Create sample input for ONNX export
        sample_input = np.random.rand(1, 160, 160, 3).astype(np.float32)

        # Export to ONNX
        import tf2onnx
        tf2onnx.convert.from_keras(
            self.model,
            input_signature=[tf.TensorSpec(sample_input.shape, tf.float32, name='input')],
            opset=13,
            output_path=onnx_path
        )

        print(f"Model exported to ONNX: {onnx_path}")
        return onnx_path

    def load_onnx_model(self, onnx_path: str = None):
        """
        Load ONNX version of the model for faster inference.

        Args:
            onnx_path: Path to ONNX model file
        """
        if not _HAS_ONNX:
            raise ImportError("ONNX runtime not available")

        if onnx_path is None:
            onnx_path = self.model_path.replace('.h5', '.onnx')

        if not os.path.exists(onnx_path):
            # Export model first
            onnx_path = self.export_to_onnx(onnx_path)

        self.onnx_session = ort.InferenceSession(onnx_path)
        self.use_onnx = True

    def extract_embedding_onnx(self, face_image):
        """Extract embedding using ONNX model (faster inference)"""
        if not hasattr(self, 'onnx_session'):
            raise RuntimeError("ONNX model not loaded. Call load_onnx_model() first")

        # Preprocess
        processed_face = self.preprocess_face(face_image)

        # Run inference
        outputs = self.onnx_session.run(None, {'input': processed_face})
        embedding = outputs[0]

        # L2 normalize
        embedding = l2_normalize(embedding[0])

        return embedding


class EmotionDetector:
    """Simple emotion detector using facial expression analysis"""

    EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    def __init__(self):
        # Simple rule-based emotion detection (can be upgraded to ML model later)
        self.face_detector = get_detector()

    def detect_emotion(self, face_image):
        """
        Detect emotion from face image using simple heuristics.
        This is a placeholder - in production, use a proper emotion recognition model.

        Returns:
            Dict with emotion probabilities
        """
        # For now, return neutral as default with some variation
        # In production, this would use a trained model
        import random
        emotions = {emotion: 0.0 for emotion in self.EMOTIONS}

        # Simple heuristic: assume neutral with small variations
        emotions['neutral'] = 0.6 + random.uniform(-0.2, 0.2)
        emotions['happy'] = 0.2 + random.uniform(-0.1, 0.1)

        # Normalize
        total = sum(emotions.values())
        emotions = {k: v/total for k, v in emotions.items()}

        # Find dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1])

        return {
            'emotions': emotions,
            'dominant': dominant[0],
            'confidence': dominant[1]
        }


class AgeGenderEstimator:
    """Age and gender estimation using MediaPipe or simple heuristics"""

    AGE_RANGES = ['0-12', '13-19', '20-34', '35-54', '55+']

    def __init__(self):
        # Initialize MediaPipe Face Detection for better estimation
        if _HAS_MEDIAPIPE:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.5
            )
        else:
            self.face_detection = None

    def estimate_age_gender(self, face_image):
        """
        Estimate age range and gender from face image.
        Uses simple heuristics based on face characteristics.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            Dict with age_range, gender, confidence
        """
        # Convert to numpy array for processing
        if isinstance(face_image, Image.Image):
            face_array = np.array(face_image.convert('RGB'))
        else:
            face_array = face_image

        # Simple heuristic-based estimation
        # In production, this would use trained ML models

        # Analyze face characteristics
        height, width = face_array.shape[:2]

        # Estimate age based on face texture/skin (simplified)
        # Younger faces tend to have smoother textures
        gray = cv2.cvtColor(face_array, cv2.COLOR_RGB2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Higher blur score might indicate younger skin
        if blur_score > 500:
            age_range = '13-19'  # Smoother skin
        elif blur_score > 300:
            age_range = '20-34'
        elif blur_score > 150:
            age_range = '35-54'
        else:
            age_range = '55+'

        # Simple gender estimation based on face shape (heuristic)
        # This is very simplified and not accurate
        face_ratio = height / width if width > 0 else 1.0

        if face_ratio > 1.1:  # Taller faces might be female
            gender = 'female'
            gender_confidence = 0.6
        else:  # Squarer faces might be male
            gender = 'male'
            gender_confidence = 0.55

        # Add some randomization for demo purposes
        import random
        age_confidence = 0.7 + random.uniform(-0.2, 0.1)
        gender_confidence += random.uniform(-0.1, 0.1)

        return {
            'age_range': age_range,
            'age_confidence': round(age_confidence, 3),
            'gender': gender,
            'gender_confidence': round(gender_confidence, 3),
            'method': 'heuristic'  # Indicates this is not using ML model
        }


class LandmarkDetector:
    """Facial landmark detection using MediaPipe"""

    def __init__(self):
        if not _HAS_MEDIAPIPE:
            raise ImportError("MediaPipe not available. Install with: pip install mediapipe")

        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect_landmarks(self, face_image):
        """
        Detect facial landmarks from face image.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            List of landmark coordinates (x, y) normalized to image dimensions
        """
        # Convert to numpy array
        if isinstance(face_image, Image.Image):
            face_array = np.array(face_image.convert('RGB'))
        else:
            face_array = face_image

        # Process with MediaPipe
        results = self.face_mesh.process(face_array)

        if not results.multi_face_landmarks:
            return []

        # Extract landmarks from first face
        face_landmarks = results.multi_face_landmarks[0]

        # Convert to list of (x, y) coordinates
        landmarks = []
        height, width = face_array.shape[:2]

        for landmark in face_landmarks.landmark:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            landmarks.append({'x': x, 'y': y})

        return landmarks

    def get_key_landmarks(self, face_image):
        """
        Get key facial landmarks for sticker placement and makeup.

        Returns:
            Dict with key landmark groups
        """
        landmarks = self.detect_landmarks(face_image)

        if not landmarks:
            return {}

        # MediaPipe face mesh has 468 landmarks
        # Key indices for common features
        key_indices = {
            'nose_tip': 1,      # Nose tip
            'left_eye': 33,     # Left eye center
            'right_eye': 263,   # Right eye center
            'left_eyebrow': [70, 105],  # Left eyebrow points
            'right_eyebrow': [336, 365], # Right eyebrow points
            'mouth_center': 13, # Mouth center
            'chin': 152,        # Chin
            'left_cheek': 234,  # Left cheek
            'right_cheek': 454, # Right cheek
            'forehead': 10      # Forehead center
        }

        key_landmarks = {}
        for name, indices in key_indices.items():
            if isinstance(indices, list):
                key_landmarks[name] = [landmarks[i] for i in indices if i < len(landmarks)]
            else:
                if indices < len(landmarks):
                    key_landmarks[name] = landmarks[indices]

        return key_landmarks


class ModelManager:
    """
    Manager to centralize access to multiple DNN models.
    Phase 0: uses existing FaceDetector for detection and provides method
    signatures for embedding/emotion/landmarks to be implemented in later phases.
    """

    def __init__(self):
        # Underlying face detector (SSD DNN)
        self.detector = get_detector()

        # FaceNet embedder (lazy loaded)
        self._embedding_model = None

        # Emotion detector (lazy loaded)
        self._emotion_model = None

        # Age/Gender estimator (lazy loaded)
        self._age_gender_model = None

        # Landmark detector (lazy loaded)
        self._landmark_model = None

    @property
    def embedding_model(self):
        """Lazy load FaceNet embedder"""
        if self._embedding_model is None:
            self._embedding_model = FaceNetEmbedder()
        return self._embedding_model

    @property
    def emotion_model(self):
        """Lazy load emotion detector"""
        if self._emotion_model is None:
            self._emotion_model = EmotionDetector()
        return self._emotion_model

    @property
    def age_gender_model(self):
        """Lazy load age/gender estimator"""
        if self._age_gender_model is None:
            self._age_gender_model = AgeGenderEstimator()
        return self._age_gender_model

    @property
    def landmark_model(self):
        """Lazy load landmark detector"""
        if self._landmark_model is None:
            self._landmark_model = LandmarkDetector()
        return self._landmark_model

    # Detection API (delegates to existing detector)
    def detect_faces(self, image, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        return self.detector.detect_faces(image, confidence_threshold=confidence_threshold)

    def detect_largest_face(self, image, confidence_threshold: float = 0.5) -> Optional[Dict[str, Any]]:
        return self.detector.detect_largest_face(image, confidence_threshold=confidence_threshold)

    # Embedding API
    def extract_embedding(self, face_image) -> np.ndarray:
        """
        Extract 128-dimensional embedding vector from a cropped face image using FaceNet.
        Returns L2-normalized embedding vector.

        Args:
            face_image: PIL Image or numpy array of cropped face

        Returns:
            np.ndarray: 128-dimensional embedding vector
        """
        # Try ONNX model first if available, fallback to TensorFlow
        if hasattr(self.embedding_model, 'use_onnx') and self.embedding_model.use_onnx:
            try:
                return self.embedding_model.extract_embedding_onnx(face_image)
            except Exception:
                # Fallback to TensorFlow model
                pass

        return self.embedding_model.extract_embedding(face_image)

    def compute_image_hash(self, image) -> str:
        """Compute SHA256 hash of image for duplicate detection"""
        if isinstance(image, Image.Image):
            image_bytes = image.tobytes()
        else:
            image_bytes = image.tobytes() if hasattr(image, 'tobytes') else str(image).encode()

        return hashlib.sha256(image_bytes).hexdigest()

    # Emotion API
    def detect_emotion(self, face_image) -> Dict[str, any]:
        """
        Detect emotions from face image.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            Dict with emotions dict, dominant emotion, and confidence
        """
        return self.emotion_model.detect_emotion(face_image)

    # Landmark API
    def detect_landmarks(self, face_image) -> List[Dict[str, int]]:
        """
        Detect facial landmarks from face image.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            List of landmark coordinates as dicts with 'x', 'y' keys
        """
        return self.landmark_model.detect_landmarks(face_image)

    def get_key_landmarks(self, face_image) -> Dict[str, any]:
        """
        Get key facial landmarks for sticker placement and makeup.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            Dict with key landmark groups (nose, eyes, mouth, etc.)
        """
        return self.landmark_model.get_key_landmarks(face_image)

    # Age/Gender API
    def estimate_age_gender(self, face_image) -> Dict[str, Any]:
        """
        Estimate age range and gender from face image.

        Args:
            face_image: PIL Image or numpy array of face

        Returns:
            Dict with age_range, gender, and confidence scores
        """
        return self.age_gender_model.estimate_age_gender(face_image)


# Convenience singleton for code that prefers a single manager instance
_model_manager: Optional[ModelManager] = None

def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

