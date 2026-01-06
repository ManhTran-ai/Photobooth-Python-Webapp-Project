"""
Test Face Detection Module
Kiểm tra các chức năng của FaceDetector class
"""
import pytest
import os
import sys
from PIL import Image
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFaceDetector:
    """Test suite for FaceDetector"""

    @pytest.fixture
    def detector(self):
        """Get FaceDetector instance"""
        from models.face_detector import get_detector
        return get_detector()

    @pytest.fixture
    def sample_image(self):
        """Create a simple test image (blank image for basic tests)"""
        return Image.new('RGB', (640, 480), color='white')

    @pytest.fixture
    def sample_face_image(self, tmp_path):
        """
        For real face detection tests, you would need actual face images.
        This is a placeholder - replace with actual test image path.
        """
        # Check if we have test images
        test_images_dir = os.path.join(
            os.path.dirname(__file__),
            'test_images'
        )
        if os.path.exists(test_images_dir):
            for fname in os.listdir(test_images_dir):
                if fname.endswith(('.jpg', '.png')):
                    return Image.open(os.path.join(test_images_dir, fname))

        # Return a blank image if no test images available
        return Image.new('RGB', (640, 480), color='white')

    def test_model_loads_successfully(self, detector):
        """Test that DNN model loads without errors"""
        assert detector is not None
        assert detector._net is not None

    def test_singleton_pattern(self):
        """Test that FaceDetector uses singleton pattern"""
        from models.face_detector import FaceDetector
        detector1 = FaceDetector()
        detector2 = FaceDetector()
        assert detector1 is detector2

    def test_detect_faces_returns_list(self, detector, sample_image):
        """Test that detect_faces returns a list"""
        faces = detector.detect_faces(sample_image)
        assert isinstance(faces, list)

    def test_detect_faces_with_numpy_array(self, detector):
        """Test that detect_faces works with numpy arrays"""
        import cv2
        # Create a simple numpy image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (255, 255, 255)  # White image

        faces = detector.detect_faces(img)
        assert isinstance(faces, list)

    def test_detect_largest_face_returns_dict_or_none(self, detector, sample_image):
        """Test that detect_largest_face returns dict or None"""
        face = detector.detect_largest_face(sample_image)
        assert face is None or isinstance(face, dict)

    def test_face_dict_structure(self, detector):
        """Test that face dict has expected keys when face is found"""
        # This test would require an actual face image
        # For now, we just verify the method runs without error
        img = Image.new('RGB', (300, 300), color='beige')
        faces = detector.detect_faces(img)

        # If faces found, verify structure
        for face in faces:
            assert 'bbox' in face
            assert 'confidence' in face
            assert 'center' in face
            assert len(face['bbox']) == 4
            assert len(face['center']) == 2

    def test_auto_crop_portrait_returns_image(self, detector, sample_image):
        """Test that auto_crop_portrait returns a PIL Image"""
        result = detector.auto_crop_portrait(sample_image)
        assert isinstance(result, Image.Image)

    def test_get_face_mask_returns_grayscale(self, detector, sample_image):
        """Test that get_face_mask returns grayscale image"""
        # Create a fake face dict
        fake_face = {
            'bbox': (100, 100, 150, 150),
            'center': (175, 175),
            'confidence': 0.9
        }

        mask = detector.get_face_mask(sample_image, fake_face)
        assert isinstance(mask, Image.Image)
        assert mask.mode == 'L'  # Grayscale

    def test_draw_faces_returns_image(self, detector, sample_image):
        """Test that draw_faces returns a PIL Image"""
        result = detector.draw_faces(sample_image)
        assert isinstance(result, Image.Image)

    def test_confidence_threshold_filtering(self, detector):
        """Test that confidence threshold filters results"""
        img = Image.new('RGB', (300, 300), color='white')

        # High threshold should return fewer or equal faces than low threshold
        faces_high = detector.detect_faces(img, confidence_threshold=0.9)
        faces_low = detector.detect_faces(img, confidence_threshold=0.1)

        assert len(faces_high) <= len(faces_low)

    def test_get_sticker_positions(self, detector, sample_image):
        """Test sticker position calculation"""
        positions = detector.get_face_positions_for_stickers(sample_image, 'hat')
        assert isinstance(positions, list)

        # Test different sticker types don't raise errors
        for sticker_type in ['hat', 'glasses', 'ears', 'mustache']:
            positions = detector.get_face_positions_for_stickers(
                sample_image,
                sticker_type
            )
            assert isinstance(positions, list)


class TestFaceDetectorConvenienceFunctions:
    """Test convenience functions in face_detector module"""

    def test_detect_faces_function(self):
        """Test module-level detect_faces function"""
        from models.face_detector import detect_faces

        img = Image.new('RGB', (300, 300), color='white')
        result = detect_faces(img)
        assert isinstance(result, list)

    def test_detect_largest_face_function(self):
        """Test module-level detect_largest_face function"""
        from models.face_detector import detect_largest_face

        img = Image.new('RGB', (300, 300), color='white')
        result = detect_largest_face(img)
        assert result is None or isinstance(result, dict)

    def test_auto_crop_portrait_function(self):
        """Test module-level auto_crop_portrait function"""
        from models.face_detector import auto_crop_portrait

        img = Image.new('RGB', (300, 300), color='white')
        result = auto_crop_portrait(img)
        assert isinstance(result, Image.Image)


class TestSmartBeautyFilters:
    """Test Smart Beauty filters that use face detection"""

    def test_smart_beauty_filter(self):
        """Test smart_beauty filter"""
        from models.filter_engine import FilterEngine

        img = Image.new('RGB', (300, 300), color='beige')
        result = FilterEngine.apply_filter(img, 'smart_beauty')

        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'

    def test_face_glow_filter(self):
        """Test face_glow filter"""
        from models.filter_engine import FilterEngine

        img = Image.new('RGB', (300, 300), color='beige')
        result = FilterEngine.apply_filter(img, 'face_glow')

        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'

    def test_portrait_pro_filter(self):
        """Test portrait_pro filter"""
        from models.filter_engine import FilterEngine

        img = Image.new('RGB', (300, 300), color='beige')
        result = FilterEngine.apply_filter(img, 'portrait_pro')

        assert isinstance(result, Image.Image)
        assert result.mode == 'RGB'

    def test_smart_filters_in_available_list(self):
        """Test that smart filters are in available filters list"""
        from models.filter_engine import FilterEngine

        filters = FilterEngine.get_available_filters()
        filter_names = [f['name'] for f in filters]

        assert 'smart_beauty' in filter_names
        assert 'face_glow' in filter_names
        assert 'portrait_pro' in filter_names

    def test_ai_beauty_category(self):
        """Test that smart filters have ai_beauty category"""
        from models.filter_engine import FilterEngine

        filters = FilterEngine.get_available_filters()
        ai_filters = [f for f in filters if f['category'] == 'ai_beauty']

        assert len(ai_filters) == 3
        names = [f['name'] for f in ai_filters]
        assert 'smart_beauty' in names
        assert 'face_glow' in names
        assert 'portrait_pro' in names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

