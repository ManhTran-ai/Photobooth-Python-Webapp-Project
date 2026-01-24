# Photobooth-Python-Webapp-Project

This project is a webapp that uses a webcam in real time to take photobooth-style photos, allowing for editing as desired, storing and managing images.

## ✨ AI-Powered Features (Latest Update)

The photobooth now includes advanced AI capabilities powered by deep neural networks:

### 🤖 Face Recognition
- **User Recognition**: Identify returning customers automatically
- **Personalized Experience**: Store face embeddings with user consent
- **Fast Search**: Annoy-based approximate nearest neighbor search
- **Privacy-First**: Explicit opt-in required for face storage

### 😊 Emotion Detection
- **Real-time Analysis**: Detect emotions from facial expressions
- **Smart Suggestions**: Recommend filters based on detected mood
- **7 Emotions**: Happy, sad, surprised, angry, fear, disgust, neutral

### 👤 Age & Gender Estimation
- **Demographic Insights**: Estimate age range and gender
- **Personalized Content**: Age-appropriate filter recommendations
- **Analytics Ready**: Track customer demographics

### 🎯 Facial Landmark Detection
- **Precise Positioning**: 468 facial landmarks using MediaPipe
- **Smart Sticker Placement**: Optimal positioning for hats, glasses, etc.
- **Virtual Makeup**: Landmark-based facial enhancements

### 🎨 Personalized Suggestions
- **AI Recommendations**: Filters and templates based on face analysis
- **Multi-factor Analysis**: Combines emotion, age, gender for suggestions
- **Template Optimization**: Suggest layouts based on user characteristics

### ⚡ Performance Optimizations
- **ONNX Export**: Faster inference with ONNX runtime
- **Lazy Loading**: Models load on-demand to save memory
- **Async Processing**: Background processing for heavy tasks
- **Caching**: Embedding index for fast recognition
