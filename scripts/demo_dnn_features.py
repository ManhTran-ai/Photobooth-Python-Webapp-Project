#!/usr/bin/env python3
"""
Demo script for DNN features in Photobooth

This script demonstrates the new AI-powered features:
- Face recognition and embedding
- Emotion detection
- Age/gender estimation
- Facial landmark detection
- Personalized suggestions

Usage:
    python demo_dnn_features.py --image path/to/image.jpg
"""

import sys
import os
import argparse
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model_manager import get_model_manager
from models.suggestion_engine import get_suggestion_engine
from models.embedding_index import get_embedding_index


def demo_face_analysis(image_path):
    """Demonstrate face analysis features"""
    print("=== Face Analysis Demo ===")

    # Load image
    try:
        image = Image.open(image_path)
        print(f"Loaded image: {image_path} ({image.size})")
    except Exception as e:
        print(f"Failed to load image: {e}")
        return

    # Initialize models
    model_manager = get_model_manager()
    suggestion_engine = get_suggestion_engine()

    # 1. Face detection
    print("\n1. Face Detection:")
    faces = model_manager.detect_faces(image)
    print(f"   Detected {len(faces)} faces")

    if not faces:
        print("   No faces detected, skipping further analysis")
        return

    # Use largest face for analysis
    largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
    face_region = model_manager.detector.get_face_region(image, largest_face)
    print(".1f"
    # 2. Emotion detection
    print("\n2. Emotion Detection:")
    emotion_result = model_manager.detect_emotion(face_region)
    print(f"   Dominant emotion: {emotion_result['dominant']} ({emotion_result['confidence']:.2f})")
    print(f"   All emotions: {emotion_result['emotions']}")

    # 3. Age/Gender estimation
    print("\n3. Age/Gender Estimation:")
    age_gender_result = model_manager.estimate_age_gender(face_region)
    print(f"   Age range: {age_gender_result['age_range']} ({age_gender_result['age_confidence']:.2f})")
    print(f"   Gender: {age_gender_result['gender']} ({age_gender_result['gender_confidence']:.2f})")
    print(f"   Method: {age_gender_result['method']}")

    # 4. Facial landmarks
    print("\n4. Facial Landmarks:")
    try:
        key_landmarks = model_manager.get_key_landmarks(face_region)
        print(f"   Detected {len(key_landmarks)} key landmarks")
        for name, coords in key_landmarks.items():
            if isinstance(coords, list):
                print(f"   {name}: {len(coords)} points")
            else:
                print(f"   {name}: ({coords['x']}, {coords['y']})")
    except Exception as e:
        print(f"   Landmark detection failed: {e}")

    # 5. Personalized suggestions
    print("\n5. Personalized Suggestions:")
    suggestions = suggestion_engine.get_personalized_suggestions(image)
    print(f"   Emotion: {suggestions.get('emotion', 'unknown')}")
    print(f"   Message: {suggestions.get('message', 'N/A')}")

    if 'suggested_filters' in suggestions:
        print("   Suggested filters:")
        for i, f in enumerate(suggestions['suggested_filters'][:3], 1):
            print(f"     {i}. {f['filter_name']} ({f['score']} pts) - {f['reason']}")

    if 'suggested_templates' in suggestions:
        print("   Suggested templates:")
        for i, t in enumerate(suggestions['suggested_templates'][:2], 1):
            print(f"     {i}. {t['template_name']} ({t['score']} pts) - {t['reason']}")

    # 6. Face embedding (for recognition)
    print("\n6. Face Embedding:")
    try:
        embedding = model_manager.extract_embedding(face_region)
        print(f"   Generated {len(embedding)}-dimensional embedding")

        # Test recognition (if index exists)
        index = get_embedding_index()
        if index.index is not None:
            search_results = index.search(embedding, top_k=3)
            print(f"   Recognition search returned {len(search_results)} candidates")
            for user_id, distance in search_results[:2]:
                similarity = 1.0 - distance
                print(".3f")
        else:
            print("   No recognition index available (run manage_embeddings.py rebuild-index)")

    except Exception as e:
        print(f"   Embedding extraction failed: {e}")

    print("\n=== Demo Complete ===")


def demo_model_management():
    """Demonstrate model management features"""
    print("=== Model Management Demo ===")

    model_manager = get_model_manager()

    # Test model loading
    print("Testing model loading...")
    try:
        # This will load models lazily
        faces = model_manager.detect_faces(Image.new('RGB', (100, 100), color='white'))
        print("✓ Face detector loaded")

        # Test embedding model
        embedding = model_manager.extract_embedding(Image.new('RGB', (160, 160), color='white'))
        print("✓ Embedding model loaded")

        # Test emotion model
        emotion = model_manager.detect_emotion(Image.new('RGB', (100, 100), color='white'))
        print("✓ Emotion model loaded")

        # Test age/gender model
        age_gender = model_manager.estimate_age_gender(Image.new('RGB', (100, 100), color='white'))
        print("✓ Age/gender model loaded")

        print("\nAll models loaded successfully!")

    except Exception as e:
        print(f"Model loading failed: {e}")

    # Test ONNX export (if available)
    try:
        print("\nTesting ONNX export...")
        onnx_path = model_manager.embedding_model.export_to_onnx()
        print(f"✓ ONNX model exported: {onnx_path}")

        # Test ONNX loading
        model_manager.embedding_model.load_onnx_model(onnx_path)
        print("✓ ONNX model loaded for inference")

    except ImportError:
        print("ℹ ONNX not available (install tf2onnx and onnxruntime for optimization)")
    except Exception as e:
        print(f"ONNX export failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='Demo DNN features in Photobooth')
    parser.add_argument('--image', help='Path to image file for analysis')
    parser.add_argument('--models-only', action='store_true', help='Only test model loading')

    args = parser.parse_args()

    if args.models_only:
        demo_model_management()
    elif args.image:
        demo_face_analysis(args.image)
    else:
        print("Please provide --image path/to/image.jpg or use --models-only")
        sys.exit(1)


if __name__ == '__main__':
    main()