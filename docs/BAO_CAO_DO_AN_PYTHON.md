# 📸 BÁO CÁO ĐỒ ÁN MÔN LẬP TRÌNH PYTHON
# **Ứng Dụng Photobooth Web với AI**

---

## 📋 MỤC LỤC

1. [Giới thiệu đề tài](#1-giới-thiệu-đề-tài)
2. [Công nghệ sử dụng](#2-công-nghệ-sử-dụng)
3. [Kiến trúc hệ thống](#3-kiến-trúc-hệ-thống)
4. [Các chức năng chính](#4-các-chức-năng-chính)
5. [Cấu trúc thư mục dự án](#5-cấu-trúc-thư-mục-dự-án)
6. [Luồng xử lý (Workflow)](#6-luồng-xử-lý-workflow)
7. [Tương tác Client-Server](#7-tương-tác-client-server)
8. [Các thuật toán quan trọng](#8-các-thuật-toán-quan-trọng)
9. [Cơ sở dữ liệu](#9-cơ-sở-dữ-liệu)
10. [Kết luận và hướng phát triển](#10-kết-luận-và-hướng-phát-triển)

---

## 1. GIỚI THIỆU ĐỀ TÀI

### 1.1 Mô tả dự án
**Photobooth Web Application** là một ứng dụng web cho phép người dùng chụp ảnh photobooth theo phong cách chuyên nghiệp ngay trên trình duyệt. Ứng dụng tích hợp các tính năng AI tiên tiến như:
- Nhận diện khuôn mặt (Face Detection)
- Áp dụng bộ lọc hình ảnh (15+ filters)
- Tạo collage ảnh theo template
- Nhận diện cảm xúc và gợi ý filter thông minh

### 1.2 Mục tiêu
- Xây dựng ứng dụng web hoàn chỉnh sử dụng Python và Flask
- Tích hợp xử lý ảnh với OpenCV và Pillow
- Ứng dụng Deep Learning cho nhận diện khuôn mặt
- Thiết kế giao diện người dùng thân thiện

### 1.3 Đối tượng sử dụng
- Cá nhân muốn chụp ảnh photobooth tại nhà
- Quán café, sự kiện cần booth chụp ảnh
- Sinh viên học tập về xử lý ảnh và AI

---

## 2. CÔNG NGHỆ SỬ DỤNG

### 2.1 Backend (Python)

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| **Flask** | 3.0.0 | Web Framework chính |
| **Flask-SQLAlchemy** | 3.1.1 | ORM cho database |
| **OpenCV** | 4.8.1 | Xử lý ảnh, Face Detection |
| **Pillow** | 10.1.0 | Xử lý ảnh cơ bản |
| **NumPy** | 1.24.3 | Tính toán ma trận |
| **TensorFlow** | 2.15.0 | Deep Learning (FaceNet) |
| **MediaPipe** | 0.10.8 | Facial Landmarks |
| **Annoy** | 1.17.2 | Approximate Nearest Neighbor Search |

### 2.2 Frontend

| Công nghệ | Mục đích |
|-----------|----------|
| **HTML5** | Cấu trúc trang web |
| **CSS3** | Giao diện, animations |
| **JavaScript (ES6+)** | Logic client-side |
| **WebRTC** | Truy cập webcam |

### 2.3 Database
- **SQLite** - Cơ sở dữ liệu nhẹ, phù hợp ứng dụng vừa và nhỏ

---

## 3. KIẾN TRÚC HỆ THỐNG

### 3.1 Mô hình MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Browser (Chrome/Firefox/Safari)                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────────────────┐ │   │
│  │  │ HTML5   │  │ CSS3    │  │ JavaScript (ES6+)    │ │   │
│  │  │ Views   │  │ Styles  │  │ - capture.js         │ │   │
│  │  │         │  │         │  │ - session.js         │ │   │
│  │  └─────────┘  └─────────┘  └──────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            │ HTTP/HTTPS (RESTful API)        │
│                            ↓                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        SERVER                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Flask Application                    │   │
│  │  ┌────────────────┐  ┌─────────────────────────────┐ │   │
│  │  │   Routes       │  │   Blueprints                │ │   │
│  │  │  - api.py      │  │   - api_bp (/api/*)         │ │   │
│  │  │  - views.py    │  │   - views_bp (pages)        │ │   │
│  │  └────────────────┘  └─────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │              Models (Business Logic)            │   │   │
│  │  │  ┌─────────────────┐  ┌───────────────────┐   │   │   │
│  │  │  │ image_processor │  │ filter_engine     │   │   │   │
│  │  │  │ (Xử lý ảnh)     │  │ (15+ bộ lọc)      │   │   │   │
│  │  │  └─────────────────┘  └───────────────────┘   │   │   │
│  │  │  ┌─────────────────┐  ┌───────────────────┐   │   │   │
│  │  │  │ face_detector   │  │ template_engine   │   │   │   │
│  │  │  │ (AI Detection)  │  │ (Tạo collage)     │   │   │   │
│  │  │  └─────────────────┘  └───────────────────┘   │   │   │
│  │  │  ┌─────────────────┐  ┌───────────────────┐   │   │   │
│  │  │  │ model_manager   │  │ suggestion_engine │   │   │   │
│  │  │  │ (DNN Models)    │  │ (AI Suggestions)  │   │   │   │
│  │  │  └─────────────────┘  └───────────────────┘   │   │   │
│  │  └────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Database (SQLite)                        │   │
│  │   Sessions │ Photos │ Users │ FaceEmbeddings          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Design Patterns được sử dụng

| Pattern | Áp dụng | Mục đích |
|---------|---------|----------|
| **Singleton** | FaceDetector | Load model DNN một lần duy nhất |
| **Factory** | create_app() | Tạo Flask app với config khác nhau |
| **Blueprint** | api_bp, views_bp | Tách biệt routes |
| **Strategy** | FilterEngine | Các filter khác nhau cùng interface |

---

## 4. CÁC CHỨC NĂNG CHÍNH

### 4.1 Chụp ảnh Photobooth (4-Photo Session)

```
📷 CAPTURE WORKFLOW
─────────────────────
[Start Session] → [Capture Photo 1] → [Capture Photo 2] 
                         ↓                    ↓
                    [Preview]            [Preview]
                         ↓                    ↓
[Capture Photo 3] → [Capture Photo 4] → [Apply Filter] → [Create Collage]
        ↓                    ↓
   [Preview]            [Preview]
```

**Tính năng:**
- Đếm ngược 3 giây trước khi chụp
- Hiệu ứng flash khi chụp
- Preview và retake từng ảnh
- Tự động lưu ảnh gốc và đã xử lý

### 4.2 Bộ lọc hình ảnh (15+ Filters)

| Danh mục | Filters |
|----------|---------|
| **Basic** | none, grayscale, sepia, brightness, contrast |
| **Photobooth** | soft_skin, pastel_glow, sakura, sparkle, rainbow_leak, heart_bokeh, polaroid |
| **Artistic** | cartoon, pencil_sketch, oil_painting, comic_pastel |
| **Instagram** | nashville, valencia, xpro2, walden, kelvin |
| **AI Beauty** | smart_beauty, face_glow, portrait_pro |

### 4.3 Tạo Collage từ Template

**Các template có sẵn:**
- `1x4` - Dạng strip dọc (Photo strip)
- `2x2` - Dạng lưới vuông
- `classic_strip` - Strip cổ điển với viền
- `grid_modern` - Lưới hiện đại
- `pastel_pink` - Màu hồng pastel với góc bo tròn

### 4.4 Tính năng AI (Advanced)

| Tính năng | Mô tả |
|-----------|-------|
| **Face Detection** | Nhận diện khuôn mặt với OpenCV DNN |
| **Face Recognition** | Nhận diện người dùng với FaceNet embeddings |
| **Emotion Detection** | Phát hiện cảm xúc (7 loại) |
| **Smart Suggestions** | Gợi ý filter dựa trên đặc điểm khuôn mặt |
| **Auto Face Crop** | Tự động crop ảnh theo Rule of Thirds |

---

## 5. CẤU TRÚC THƯ MỤC DỰ ÁN

```
Photobooth-Python-Webapp-Project/
│
├── 📄 app.py                    # Entry point - Application Factory
├── 📄 config.py                 # Cấu hình ứng dụng
├── 📄 requirements.txt          # Dependencies
│
├── 📁 models/                   # Business Logic Layer
│   ├── __init__.py
│   ├── database.py              # SQLAlchemy Models
│   ├── image_processor.py       # Xử lý ảnh cơ bản
│   ├── filter_engine.py         # 15+ bộ lọc
│   ├── face_detector.py         # Face Detection (DNN)
│   ├── template_engine.py       # Tạo collage
│   ├── model_manager.py         # Quản lý DNN models
│   ├── suggestion_engine.py     # AI gợi ý filter
│   ├── embedding_index.py       # Annoy index cho face search
│   └── embeddings.py            # Face embedding utilities
│
├── 📁 routes/                   # Controller Layer
│   ├── __init__.py
│   ├── api.py                   # RESTful API endpoints
│   └── views.py                 # HTML page routes
│
├── 📁 templates/                # View Layer (Jinja2)
│   ├── base.html                # Base template
│   ├── index.html               # Landing page
│   ├── capture.html             # Camera capture
│   ├── session.html             # Filter selection
│   └── gallery.html             # Photo gallery
│
├── 📁 static/                   # Static files
│   ├── css/style.css            # Stylesheet
│   ├── js/                      # JavaScript
│   │   ├── capture.js           # Camera logic
│   │   ├── session.js           # Filter selection
│   │   └── session_collage.js   # Collage creation
│   ├── uploads/                 # User uploads
│   │   ├── originals/
│   │   ├── processed/
│   │   ├── thumbnails/
│   │   └── collages/
│   └── templates/               # Collage assets
│       ├── stickers/
│       ├── decorations/
│       └── templates.json
│
├── 📁 utils/                    # Helper utilities
│   ├── async_worker.py          # Background tasks
│   ├── decorators.py            # Custom decorators
│   ├── helpers.py               # Helper functions
│   └── validators.py            # Input validation
│
├── 📁 tests/                    # Unit tests
│   ├── test_api.py
│   ├── test_filters.py
│   └── test_face_detection.py
│
└── 📁 docs/                     # Documentation
    ├── README.md
    ├── API.md
    └── ALGORITHMS.md
```

---

## 6. LUỒNG XỬ LÝ (WORKFLOW)

### 6.1 Luồng chụp ảnh hoàn chỉnh

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHOTOBOOTH WORKFLOW                           │
└─────────────────────────────────────────────────────────────────┘

[1] USER OPENS WEBSITE
         │
         ▼
┌─────────────────┐
│  Landing Page   │  → Hiển thị giới thiệu, hướng dẫn
│   (index.html)  │
└────────┬────────┘
         │ Click "Bắt đầu"
         ▼
[2] CREATE SESSION
         │
┌────────┴────────┐
│ POST /api/sessions │  → Server tạo UUID mới
└────────┬────────┘     → Lưu vào database
         │              → Return session_id
         ▼
[3] CAMERA CAPTURE PAGE
         │
┌────────┴────────┐
│  capture.html   │  → Kích hoạt WebRTC
│                 │  → Hiển thị video stream
└────────┬────────┘
         │ Click "Chụp" (x4 lần)
         ▼
[4] CAPTURE PHOTO (Repeat 4 times)
         │
         │  ┌─────────────────────────────────────┐
         │  │ Client (capture.js):                │
         │  │ 1. Countdown 3-2-1                  │
         │  │ 2. canvas.drawImage(video)          │
         │  │ 3. canvas.toBlob() → FormData       │
         │  │ 4. POST /api/capture                │
         │  └─────────────────────────────────────┘
         │
         │  ┌─────────────────────────────────────┐
         │  │ Server (api.py):                    │
         │  │ 1. Receive image blob               │
         │  │ 2. ImageProcessor.process_image()   │
         │  │    - Flip horizontal (mirror fix)   │
         │  │    - Convert to RGB                 │
         │  │ 3. Save: original, processed, thumb │
         │  │ 4. Insert Photo record to DB        │
         │  │ 5. Return URLs                      │
         │  └─────────────────────────────────────┘
         │
         ▼ After 4 photos
[5] FILTER SELECTION PAGE
         │
┌────────┴────────┐
│  session.html   │  → Load all photos
│                 │  → Display filter cards
└────────┬────────┘
         │ Select filter
         ▼
[6] PREVIEW FILTER
         │
         │  POST /api/sessions/{id}/preview-filter
         │  Server: FilterEngine.apply_filter()
         │  Return: Filtered image URLs
         │
         │ Confirm selection
         ▼
[7] APPLY FILTER TO ALL PHOTOS
         │
         │  POST /api/sessions/{id}/apply-filter
         │  Server processes all 4 photos
         │
         ▼
[8] CREATE COLLAGE
         │
┌────────┴────────┐
│ Select Template │  → Choose layout (1x4, 2x2, etc.)
│ Add Stickers    │  → Optional decorations
└────────┬────────┘
         │
         │  POST /api/sessions/{id}/create-collage
         │  Server: TemplateEngine.create_collage()
         │
         ▼
[9] DOWNLOAD / SHARE
         │
         │  GET /api/images/collages/{filename}
         │  → Download final collage image
         │
         ▼
        END
```

### 6.2 Sequence Diagram - Capture Photo

```
┌────────┐          ┌────────┐          ┌────────┐          ┌────────┐
│ User   │          │ Browser│          │ Server │          │   DB   │
└───┬────┘          └───┬────┘          └───┬────┘          └───┬────┘
    │                   │                   │                   │
    │  Click "Chụp"     │                   │                   │
    │──────────────────>│                   │                   │
    │                   │                   │                   │
    │                   │ Countdown 3-2-1   │                   │
    │<──────────────────│                   │                   │
    │                   │                   │                   │
    │                   │ Capture frame     │                   │
    │                   │ from video        │                   │
    │                   │────────┐          │                   │
    │                   │        │          │                   │
    │                   │<───────┘          │                   │
    │                   │                   │                   │
    │                   │ POST /api/capture │                   │
    │                   │ {image, session_id}                   │
    │                   │──────────────────>│                   │
    │                   │                   │                   │
    │                   │                   │ Process Image     │
    │                   │                   │────────┐          │
    │                   │                   │        │          │
    │                   │                   │<───────┘          │
    │                   │                   │                   │
    │                   │                   │ INSERT Photo      │
    │                   │                   │──────────────────>│
    │                   │                   │                   │
    │                   │                   │      OK           │
    │                   │                   │<──────────────────│
    │                   │                   │                   │
    │                   │ Response {urls}   │                   │
    │                   │<──────────────────│                   │
    │                   │                   │                   │
    │  Show preview     │                   │                   │
    │<──────────────────│                   │                   │
    │                   │                   │                   │
```

---

## 7. TƯƠNG TÁC CLIENT-SERVER

### 7.1 RESTful API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| **POST** | `/api/sessions` | Tạo session mới |
| **GET** | `/api/sessions/{id}/photos` | Lấy danh sách ảnh |
| **POST** | `/api/capture` | Chụp và lưu ảnh |
| **GET** | `/api/filters` | Lấy danh sách filters |
| **POST** | `/api/sessions/{id}/apply-filter` | Áp dụng filter |
| **POST** | `/api/sessions/{id}/create-collage` | Tạo collage |
| **GET** | `/api/images/{folder}/{filename}` | Lấy ảnh |

### 7.2 API Request/Response Examples

#### Tạo Session
```http
POST /api/sessions
Content-Type: application/json

Response 200 OK:
{
  "success": true,
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Session created successfully"
}
```

#### Chụp ảnh
```http
POST /api/capture
Content-Type: multipart/form-data

Form Data:
- image: [binary file]
- session_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
- photo_number: 1

Response 200 OK:
{
  "success": true,
  "photo_id": 1,
  "original_url": "/api/images/originals/20240125_143052_abc123_1.jpg",
  "processed_url": "/api/images/processed/20240125_143052_abc123_1.jpg",
  "thumbnail_url": "/api/images/thumbnails/20240125_143052_abc123_1.jpg"
}
```

#### Áp dụng Filter
```http
POST /api/sessions/a1b2c3d4/apply-filter
Content-Type: application/json

{
  "filter_name": "sakura"
}

Response 200 OK:
{
  "success": true,
  "photos": [
    {
      "id": 1,
      "processed_url": "/api/images/processed/20240125_143052_abc123_1.jpg"
    }
    // ... more photos
  ]
}
```

### 7.3 Sơ đồ tương tác Client-Server

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIENT-SERVER INTERACTION                         │
└─────────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐                    ┌──────────────────┐
     │     CLIENT       │                    │     SERVER       │
     │   (Browser)      │                    │    (Flask)       │
     └────────┬─────────┘                    └────────┬─────────┘
              │                                       │
              │  1. HTTP GET /capture                 │
              │──────────────────────────────────────>│
              │                                       │ Render capture.html
              │  2. HTML + JS Response                │
              │<──────────────────────────────────────│
              │                                       │
              │  3. WebRTC: getUserMedia()            │
              │  (Camera Access - Local)              │
              │                                       │
              │  4. POST /api/sessions (XHR)          │
              │──────────────────────────────────────>│
              │                                       │ Create session in DB
              │  5. JSON {session_id}                 │
              │<──────────────────────────────────────│
              │                                       │
              │  6. POST /api/capture                 │
              │  (FormData with image blob)           │
              │──────────────────────────────────────>│
              │                                       │ Process image
              │                                       │ Save to filesystem
              │                                       │ Store in database
              │  7. JSON {photo_id, urls}             │
              │<──────────────────────────────────────│
              │                                       │
              │  8. GET /api/images/processed/...     │
              │──────────────────────────────────────>│
              │                                       │ send_from_directory()
              │  9. Image binary                      │
              │<──────────────────────────────────────│
              │                                       │
```

---

## 8. CÁC THUẬT TOÁN QUAN TRỌNG

### 8.1 Face Detection với OpenCV DNN

#### Tại sao chọn DNN thay vì YOLO?

| Tiêu chí | DNN (SSD + ResNet-10) | YOLO |
|----------|----------------------|------|
| Model size | ~10MB | >100MB |
| Speed (CPU) | 30-50ms | 50-100ms |
| Accuracy | ~95% (frontal face) | ~93% |
| Dependencies | Chỉ OpenCV | PyTorch |
| Use case | Face-specific | General objects |

#### Kiến trúc Model

```
Input Image (any size)
        ↓
    Resize (300x300)
        ↓
    Mean Subtraction (104, 177, 123)
        ↓
    ResNet-10 Backbone
        ↓
    SSD Detection Layers
        ↓
    NMS (Non-Maximum Suppression)
        ↓
Output: Bounding Boxes + Confidence Scores
```

#### Code Implementation (face_detector.py)

```python
class FaceDetector:
    _instance = None  # Singleton pattern
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        # Load pre-trained Caffe model
        self._net = cv2.dnn.readNetFromCaffe(
            'deploy.prototxt',
            'res10_300x300_ssd_iter_140000.caffemodel'
        )
    
    def detect_faces(self, image, confidence_threshold=0.5):
        # Preprocessing
        blob = cv2.dnn.blobFromImage(
            image,
            scalefactor=1.0,
            size=(300, 300),
            mean=(104.0, 177.0, 123.0)
        )
        
        # Forward pass
        self._net.setInput(blob)
        detections = self._net.forward()
        
        # Post-processing
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7]
                faces.append({
                    'bbox': box,
                    'confidence': confidence
                })
        return faces
```

### 8.2 Bilateral Filter (Smart Beauty)

Bilateral filter là thuật toán key cho việc làm mịn da:

**Công thức toán học:**

$$I_{filtered}(x) = \frac{1}{W_p} \sum_{x_i \in \Omega} I(x_i) \cdot f_r(||I(x_i) - I(x)||) \cdot g_s(||x_i - x||)$$

Trong đó:
- $f_r$: Range kernel (Gaussian trên intensity) - giữ edges
- $g_s$: Spatial kernel (Gaussian trên distance) - làm mịn
- $W_p$: Normalization factor

**Ưu điểm:**
- Làm mịn vùng da (similar colors)
- Giữ nguyên edges (mắt, mũi, miệng)

```python
@staticmethod
def _apply_soft_skin(image):
    cv_img = FilterEngine._pil_to_cv2(image)
    # Apply bilateral filter 2 lần để tăng hiệu ứng
    smooth = cv2.bilateralFilter(cv_img, 9, 85, 85)
    smooth = cv2.bilateralFilter(smooth, 9, 85, 85)
    return FilterEngine._cv2_to_pil(smooth)
```

### 8.3 Face Embedding với FaceNet

FaceNet chuyển khuôn mặt thành vector 128 chiều để so sánh:

```
Face Image (160x160)
        ↓
    FaceNet CNN
        ↓
    L2 Normalize
        ↓
    128-D Embedding Vector
```

**So sánh khuôn mặt:**
- Euclidean distance < 0.6 → Cùng một người
- Euclidean distance > 1.0 → Khác người

### 8.4 Approximate Nearest Neighbor (Annoy)

Sử dụng **Annoy library** để tìm kiếm face embeddings nhanh:

```python
class EmbeddingIndex:
    def __init__(self, embedding_dim=128):
        self.index = AnnoyIndex(embedding_dim, 'angular')
    
    def search(self, query_embedding, top_k=5):
        # O(log n) thay vì O(n) với brute force
        return self.index.get_nns_by_vector(
            query_embedding, top_k, include_distances=True
        )
```

---

## 9. CƠ SỞ DỮ LIỆU

### 9.1 Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    sessions     │       │     photos      │
├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │───┐   │ id (PK, INT)    │
│ created_at      │   │   │ session_id (FK) │──┐
│ completed_at    │   └──>│ photo_number    │  │
│ status          │       │ original_filename│  │
└─────────────────┘       │ processed_filename│ │
                          │ thumbnail_filename│ │
                          │ applied_filter   │  │
                          │ created_at       │  │
                          └─────────────────┘  │
                                               │
┌─────────────────┐       ┌─────────────────┐  │
│     users       │       │ filters_applied │  │
├─────────────────┤       ├─────────────────┤  │
│ id (PK, INT)    │───┐   │ id (PK, INT)    │  │
│ label           │   │   │ session_id (FK) │──┘
│ display_name    │   │   │ filter_name     │
│ age_range       │   │   │ applied_at      │
│ gender          │   │   └─────────────────┘
│ last_seen       │   │
└─────────────────┘   │
                      │
┌─────────────────┐   │
│ face_embeddings │   │
├─────────────────┤   │
│ id (PK, INT)    │   │
│ user_id (FK)    │───┘
│ embedding_vector│
│ confidence      │
│ image_hash      │
└─────────────────┘
```

### 9.2 SQLAlchemy Models

```python
class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='capturing')
    
    # Relationships
    photos = db.relationship('Photo', backref='session', lazy=True)


class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'))
    photo_number = db.Column(db.Integer, nullable=False)  # 1-4
    original_filename = db.Column(db.String(255))
    processed_filename = db.Column(db.String(255))
    thumbnail_filename = db.Column(db.String(255))
    applied_filter = db.Column(db.String(50))
```

---

## 10. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 10.1 Kết quả đạt được

✅ **Hoàn thành:**
- Ứng dụng web photobooth hoàn chỉnh với Flask
- Tích hợp 15+ bộ lọc ảnh chuyên nghiệp
- Face Detection với OpenCV DNN (~95% accuracy)
- Hệ thống template tạo collage linh hoạt
- RESTful API thiết kế chuẩn
- Giao diện responsive, thân thiện

### 10.2 Kiến thức Python áp dụng

| Kiến thức | Áp dụng trong dự án |
|-----------|---------------------|
| **OOP** | Classes: ImageProcessor, FilterEngine, FaceDetector |
| **Design Patterns** | Singleton, Factory, Strategy, Blueprint |
| **Web Framework** | Flask routing, Jinja2 templates, Blueprints |
| **Database** | SQLAlchemy ORM, migrations |
| **Image Processing** | OpenCV, Pillow, NumPy |
| **Machine Learning** | TensorFlow/Keras, Face Detection DNN |
| **API Design** | RESTful conventions, JSON responses |
| **File I/O** | Image upload, storage, serving |
| **Exception Handling** | Try-except blocks, error responses |
| **Modules & Packages** | Project structure, imports |

### 10.3 Hướng phát triển tương lai

🚀 **Cải tiến:**
1. **Real-time face filters** - Áp dụng filter trực tiếp trên video stream
2. **Cloud deployment** - Deploy lên AWS/GCP với Docker
3. **Mobile app** - Phát triển app native với React Native
4. **Social sharing** - Tích hợp chia sẻ Facebook, Instagram
5. **Payment integration** - Thanh toán cho các filter premium
6. **Multi-language** - Hỗ trợ đa ngôn ngữ

### 10.4 Demo

**Để chạy ứng dụng:**

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Chạy server
python app.py

# 3. Truy cập
http://localhost:5000
```

---

## 📚 TÀI LIỆU THAM KHẢO

1. Flask Documentation - https://flask.palletsprojects.com/
2. OpenCV Documentation - https://docs.opencv.org/
3. Pillow Documentation - https://pillow.readthedocs.io/
4. TensorFlow/Keras - https://www.tensorflow.org/
5. SQLAlchemy ORM - https://www.sqlalchemy.org/
6. FaceNet Paper - Schroff et al. (2015)
7. SSD Detection Paper - Liu et al. (2016)

---

**Sinh viên thực hiện:** [Tên sinh viên]  
**Mã số sinh viên:** [MSSV]  
**Giảng viên hướng dẫn:** [Tên giảng viên]  
**Môn học:** Lập trình Python  
**Năm học:** 2025-2026

---

*Báo cáo được tạo tự động từ phân tích source code của dự án.*
