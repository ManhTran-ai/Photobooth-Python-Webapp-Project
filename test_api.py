#!/usr/bin/env python3
"""Test script for DNN API endpoints"""

import requests
import json
from PIL import Image
import io

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_model_status():
    """Test model status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/model-status")
        print(f"Model status: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Model status failed: {e}")
        return False

def test_emotion_detection():
    """Test emotion detection with a sample image"""
    try:
        # Load a test image
        img_path = "static/templates/previews/basic_preview.png"
        with open(img_path, 'rb') as f:
            files = {'image': ('test.png', f, 'image/png')}

            response = requests.post(f"{BASE_URL}/api/detect-emotion", files=files)
            print(f"Emotion detection: {json.dumps(response.json(), indent=2)}")
            return True
    except Exception as e:
        print(f"Emotion detection failed: {e}")
        return False

def test_age_gender_estimation():
    """Test age/gender estimation"""
    try:
        img_path = "static/templates/previews/basic_preview.png"
        with open(img_path, 'rb') as f:
            files = {'image': ('test.png', f, 'image/png')}

            response = requests.post(f"{BASE_URL}/api/estimate-age-gender", files=files)
            print(f"Age/Gender estimation: {json.dumps(response.json(), indent=2)}")
            return True
    except Exception as e:
        print(f"Age/Gender estimation failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing DNN API endpoints...\n")

    if not test_health():
        print("Server not running!")
        exit(1)

    test_model_status()
    print()
    test_emotion_detection()
    print()
    test_age_gender_estimation()

    print("\nAPI testing complete!")