# 📸 Photobooth Python Webapp - Phân Tích Project & Phân Chia Công Việc

## 📋 Tổng Quan Project

**Tên Project:** Photobooth Python Webapp  
**Mô tả:** Ứng dụng web chụp ảnh photobooth với AI, cho phép người dùng chụp 4 ảnh, áp dụng filter, sticker, và tạo collage.  
**Công nghệ sử dụng:**
- **Backend:** Flask (Python)
- **Frontend:** HTML/CSS/JavaScript
- **Database:** SQLite với SQLAlchemy
- **AI/ML:** TensorFlow, OpenCV, MediaPipe, Annoy
- **Image Processing:** Pillow, OpenCV

---

## 🏗️ Cấu Trúc Project

```
├── app.py                    # Flask application factory
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── models/                   # Core business logic
│   ├── database.py          # Database models (Session, Photo, User, FaceEmbedding)
│   ├── face_detector.py     # DNN Face detection
│   ├── filter_engine.py     # 30+ Image filters
│   ├── template_engine.py   # Collage template renderer
│   ├── image_processor.py   # Image manipulation utilities
│   ├── model_manager.py     # AI model management (FaceNet, emotions)
│   ├── embedding_index.py   # Annoy-based face search
│   ├── suggestion_engine.py # AI-based filter/template suggestions
│   └── embeddings.py        # Face embedding utilities
├── routes/
│   ├── api.py               # REST API endpoints (2000+ lines)
│   └── views.py             # HTML page routes
├── templates/               # Jinja2 HTML templates
│   ├── base.html, index.html, capture.html, session.html, gallery.html
├── static/
│   ├── css/style.css
│   ├── js/
│   │   ├── capture.js       # Camera capture logic
│   │   ├── session.js       # Filter selection UI
│   │   └── session_collage.js # Collage preview & export
│   ├── templates/           # Collage assets
│   │   ├── stickers/, decorations/, assets/, previews/
│   └── uploads/             # User uploaded images
├── tests/                   # Unit tests
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

---

## 📊 Phân Tích Chức Năng Chi Tiết

### **MODULE 1: Core Backend & Database** 
**Files:** `app.py`, `config.py`, `models/database.py`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| Flask App Factory | Khởi tạo app, blueprints, database | ⭐⭐ |
| Session Model | Quản lý phiên chụp 4 ảnh | ⭐⭐ |
| Photo Model | Lưu trữ thông tin ảnh (original, processed, thumbnail) | ⭐⭐ |
| User Model | Lưu thông tin người dùng cho face recognition | ⭐⭐⭐ |
| FaceEmbedding Model | Lưu face vectors cho nhận diện | ⭐⭐⭐ |
| FilterApplied Model | Theo dõi lịch sử filter | ⭐⭐ |

---

### **MODULE 2: Image Processing & Filters**
**Files:** `models/filter_engine.py`, `models/image_processor.py`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| **Basic Filters** | none, grayscale, sepia, brightness, contrast | ⭐⭐ |
| **Photobooth Filters** | soft_skin, pastel_glow, sakura, sparkle, rainbow_leak, heart_bokeh, polaroid, comic_pastel, cool_mint, warm_peach | ⭐⭐⭐ |
| **Artistic Filters** | cartoon, pencil_sketch, oil_painting | ⭐⭐⭐ |
| **Instagram Filters** | nashville, valencia, xpro2, walden, kelvin | ⭐⭐⭐ |
| **Effect Filters** | blur, edge_detection, vintage, cool_tone, warm_tone | ⭐⭐ |
| **AI Beauty Filters** | smart_beauty, face_glow, portrait_pro (face-aware) | ⭐⭐⭐⭐ |
| Image Flip/Mirror | Flip horizontal cho front camera | ⭐ |
| Thumbnail Creation | Tạo thumbnail từ ảnh gốc | ⭐⭐ |
| Image Preprocessing | Chuẩn bị ảnh cho model input | ⭐⭐ |
| Blur/Light Detection | Phát hiện ảnh mờ hoặc thiếu sáng | ⭐⭐ |

---

### **MODULE 3: Face Detection & AI Features**
**Files:** `models/face_detector.py`, `models/model_manager.py`, `models/embedding_index.py`, `models/suggestion_engine.py`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| DNN Face Detection | Detect faces sử dụng Caffe model | ⭐⭐⭐ |
| Detect Largest Face | Tìm khuôn mặt lớn nhất trong ảnh | ⭐⭐ |
| Face Region Extraction | Crop vùng khuôn mặt với padding | ⭐⭐ |
| Auto Crop Portrait | Tự động crop theo rule of thirds | ⭐⭐⭐ |
| Face Mask Generation | Tạo mask ellipse cho face region | ⭐⭐⭐ |
| **FaceNet Embedder** | Trích xuất 128-dim face embedding | ⭐⭐⭐⭐ |
| ONNX Export | Export model sang ONNX format | ⭐⭐⭐⭐ |
| **Annoy Index** | Approximate nearest neighbor search | ⭐⭐⭐⭐ |
| Face Recognition | Nhận diện người dùng qua face | ⭐⭐⭐⭐ |
| **Emotion Detection** | Phát hiện 7 loại cảm xúc | ⭐⭐⭐⭐ |
| Age/Gender Estimation | Ước tính độ tuổi và giới tính | ⭐⭐⭐⭐ |
| Facial Landmarks | 468 điểm mặt với MediaPipe | ⭐⭐⭐⭐ |
| **Filter Suggestions** | Gợi ý filter dựa trên emotion/age/gender | ⭐⭐⭐ |
| **Template Suggestions** | Gợi ý template dựa trên đặc điểm | ⭐⭐⭐ |
| Sticker Positioning | Tính toán vị trí đặt sticker (hat, glasses, ears) | ⭐⭐⭐ |

---

### **MODULE 4: Template Engine & Collage**
**Files:** `models/template_engine.py`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| Template Metadata | Định nghĩa layout templates (1x4, 2x2, classic_strip, etc.) | ⭐⭐ |
| Create Collage | Tạo collage từ nhiều ảnh | ⭐⭐⭐ |
| Photo Placement | Đặt ảnh vào các slot template | ⭐⭐⭐ |
| Fill Modes | duplicate, placeholder, center | ⭐⭐ |
| Color Customization | Thay đổi màu background/accent/border | ⭐⭐ |
| Decoration Placement | Đặt sticker/decoration lên collage | ⭐⭐⭐ |
| Anchor Points | Vị trí đặt sticker tự động | ⭐⭐⭐ |
| SVG Rasterization | Convert SVG decorations sang PNG | ⭐⭐⭐ |
| Rounded Corners | Bo góc ảnh | ⭐⭐ |
| Resize & Crop | Resize ảnh fit slot với crop | ⭐⭐⭐ |

---

### **MODULE 5: REST API Endpoints**
**Files:** `routes/api.py` (2073 lines)

| Endpoint | Method | Chức năng | Độ phức tạp |
|----------|--------|-----------|-------------|
| `/api/health` | GET | Health check | ⭐ |
| `/api/upload` | POST | Upload ảnh đơn | ⭐⭐ |
| `/api/images/<folder>/<filename>` | GET | Serve ảnh | ⭐ |
| `/api/sessions` | POST | Tạo session mới | ⭐⭐ |
| `/api/capture` | POST | Chụp ảnh vào session | ⭐⭐⭐ |
| `/api/sessions/<id>/photos` | GET | Lấy ảnh trong session | ⭐⭐ |
| `/api/filters` | GET | Danh sách filters | ⭐⭐ |
| `/api/apply-filter` | POST | Áp dụng filter cho session | ⭐⭐⭐ |
| `/api/templates` | GET | Danh sách templates | ⭐⭐ |
| `/api/collage` | POST | Tạo collage | ⭐⭐⭐⭐ |
| `/api/face-detect` | POST | Detect faces | ⭐⭐⭐ |
| `/api/auto-crop` | POST | Auto crop portrait | ⭐⭐⭐ |
| `/api/sticker-positions` | POST | Lấy vị trí sticker | ⭐⭐⭐ |
| `/api/face-debug` | POST | Debug face detection | ⭐⭐ |
| `/api/face-analyze` | POST | Phân tích emotion/age/gender | ⭐⭐⭐⭐ |
| `/api/face-suggestions` | POST | Gợi ý filter/template | ⭐⭐⭐ |
| `/api/users` | POST/GET | Quản lý users | ⭐⭐⭐ |
| `/api/users/<id>/embeddings` | POST | Lưu face embedding | ⭐⭐⭐⭐ |
| `/api/recognize` | POST | Nhận diện face | ⭐⭐⭐⭐ |

---

### **MODULE 6: Frontend - Camera Capture**
**Files:** `templates/capture.html`, `static/js/capture.js`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| Camera Access | Xin quyền và khởi tạo webcam | ⭐⭐⭐ |
| Video Preview | Hiển thị video realtime (mirrored) | ⭐⭐ |
| Countdown Timer | Đếm ngược trước khi chụp | ⭐⭐ |
| Photo Capture | Chụp ảnh từ video stream | ⭐⭐⭐ |
| Flash Effect | Hiệu ứng flash khi chụp | ⭐⭐ |
| Preview Modal | Xem trước ảnh vừa chụp | ⭐⭐ |
| Confirm/Retake | Xác nhận hoặc chụp lại | ⭐⭐ |
| Progress Tracking | Hiển thị tiến độ 1/4 - 4/4 | ⭐⭐ |
| Thumbnail Preview | Hiển thị thumbnails đã chụp | ⭐⭐ |
| Error Handling | Xử lý lỗi camera permissions | ⭐⭐⭐ |
| Session Creation | Tự động tạo session khi bắt đầu | ⭐⭐ |

---

### **MODULE 7: Frontend - Filter Selection & Collage**
**Files:** `templates/session.html`, `static/js/session.js`, `static/js/session_collage.js`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| Filter Cards | Hiển thị grid các filters | ⭐⭐ |
| Category Tabs | Phân loại filter theo category | ⭐⭐ |
| Filter Preview | Xem trước filter trên ảnh | ⭐⭐⭐ |
| Comparison Slider | So sánh before/after | ⭐⭐⭐ |
| Filter Application | Áp dụng filter commit | ⭐⭐ |
| **Template Selection** | Chọn layout 1x4/2x2 | ⭐⭐ |
| **SVG Preview** | Render preview bằng SVG | ⭐⭐⭐ |
| **Sticker Placement** | Drag & drop stickers | ⭐⭐⭐⭐ |
| Auto Sticker | Tự động đặt sticker vào frame | ⭐⭐⭐ |
| **Color Picker** | Chọn màu frame | ⭐⭐ |
| **Export Collage** | Xuất ảnh collage cuối cùng | ⭐⭐⭐ |
| AI Beauty Buttons | Nút áp dụng smart beauty/face glow/portrait pro | ⭐⭐⭐ |
| Auto Accessories | Gắn phụ kiện dựa trên face detection | ⭐⭐⭐⭐ |
| Download Feature | Tải ảnh về máy | ⭐⭐ |

---

### **MODULE 8: Testing & Scripts**
**Files:** `tests/`, `scripts/`

| Chức năng | Mô tả | Độ phức tạp |
|-----------|-------|-------------|
| API Tests | Test các API endpoints | ⭐⭐⭐ |
| Face Detection Tests | Test nhận diện khuôn mặt | ⭐⭐⭐ |
| Filter Tests | Test các bộ lọc | ⭐⭐ |
| Template Engine Tests | Test tạo collage | ⭐⭐⭐ |
| Demo DNN Features | Script demo các tính năng AI | ⭐⭐⭐ |
| Generate Filter Previews | Tạo preview thumbnails cho filters | ⭐⭐ |
| Generate Template Previews | Tạo preview thumbnails cho templates | ⭐⭐ |
| Manage Embeddings | Script quản lý face embeddings | ⭐⭐⭐ |
| Remove Background | Script xóa background | ⭐⭐⭐ |

---

## 👥 Phân Chia Công Việc Cho 4 Thành Viên

### **📊 Tổng Kết Khối Lượng Công Việc**

| Mảng | Số Files | Dòng Code (ước tính) | Độ phức tạp trung bình |
|------|----------|---------------------|------------------------|
| Core Backend & Database | 3 | ~400 | ⭐⭐⭐ |
| Image Processing & Filters | 2 | ~1100 | ⭐⭐⭐ |
| Face Detection & AI | 5 | ~1500 | ⭐⭐⭐⭐ |
| Template Engine | 1 | ~700 | ⭐⭐⭐ |
| REST API | 1 | ~2100 | ⭐⭐⭐ |
| Frontend Capture | 2 | ~600 | ⭐⭐⭐ |
| Frontend Session/Collage | 3 | ~1900 | ⭐⭐⭐⭐ |
| Testing & Scripts | 8 | ~800 | ⭐⭐⭐ |

---

## 🎯 PHÂN CÔNG CÔNG VIỆC CHO 4 NGƯỜI

### **👨‍💻 NGƯỜI 1: Backend Core & Database**
**Tên vai trò:** Backend Developer / Database Manager

#### Phạm vi công việc:
| File/Module | Nhiệm vụ chi tiết |
|-------------|-------------------|
| `app.py` | Quản lý Flask app factory, blueprints registration |
| `config.py` | Quản lý configuration, environment variables |
| `models/database.py` | Thiết kế và quản lý tất cả database models |
| `routes/api.py` (Core APIs) | - `/api/health` <br> - `/api/upload` <br> - `/api/images` <br> - `/api/sessions` (CRUD) <br> - `/api/capture` |
| `utils/` folder | Tất cả utility functions (helpers, validators, decorators) |

#### Chi tiết chức năng phụ trách:
1. **Database Models:**
   - Session model: Quản lý phiên chụp ảnh
   - Photo model: Lưu trữ metadata ảnh
   - User model: Thông tin người dùng
   - FaceEmbedding model: Lưu face vectors
   - FilterApplied model: Lịch sử filter

2. **Core API Endpoints:**
   - Health check endpoint
   - Image upload/serve endpoints
   - Session management (create, get, update, delete)
   - Photo capture endpoint (nhận ảnh từ camera)

3. **Configuration & Utils:**
   - Environment configuration (dev/prod)
   - File path management
   - Input validation
   - Error handling decorators
   - Async worker utilities

#### Ước tính khối lượng:
- ~600 dòng code Python
- 5-6 endpoints API
- 5 database models
- ~25% tổng công việc

---

### **👨‍💻 NGƯỜI 2: Image Processing & Filters**
**Tên vai trò:** Image Processing Specialist

#### Phạm vi công việc:
| File/Module | Nhiệm vụ chi tiết |
|-------------|-------------------|
| `models/filter_engine.py` | Toàn bộ 30+ filters với OpenCV/Pillow |
| `models/image_processor.py` | Image manipulation utilities |
| `routes/api.py` (Filter APIs) | - `/api/filters` <br> - `/api/apply-filter` |
| `scripts/generate_filter_previews.py` | Tạo preview cho filters |
| `tests/test_filters.py` | Unit tests cho filters |

#### Chi tiết chức năng phụ trách:
1. **Basic Filters (5):**
   - none, grayscale, sepia, brightness, contrast

2. **Photobooth Filters (10):**
   - soft_skin, pastel_glow, sakura, sparkle
   - rainbow_leak, heart_bokeh, polaroid
   - comic_pastel, cool_mint, warm_peach

3. **Artistic Filters (3):**
   - cartoon, pencil_sketch, oil_painting

4. **Instagram-style Filters (5):**
   - nashville, valencia, xpro2, walden, kelvin

5. **Effect Filters (5):**
   - blur, edge_detection, vintage, cool_tone, warm_tone

6. **AI Beauty Filters (3):**
   - smart_beauty (làm mịn da vùng mặt)
   - face_glow (làm sáng vùng mặt)
   - portrait_pro (tổng hợp nhiều hiệu ứng)

7. **Image Processor Functions:**
   - flip_horizontal (mirror cho front camera)
   - create_thumbnail
   - preprocess_for_model
   - is_blurry (detect blur)
   - is_low_light (detect ánh sáng yếu)

#### Ước tính khối lượng:
- ~1100 dòng code Python
- 30+ filter implementations
- 2 API endpoints
- ~25% tổng công việc

---

### **👨‍💻 NGƯỜI 3: AI/ML Features & Face Detection**
**Tên vai trò:** AI/ML Engineer

#### Phạm vi công việc:
| File/Module | Nhiệm vụ chi tiết |
|-------------|-------------------|
| `models/face_detector.py` | DNN Face detection với Caffe model |
| `models/model_manager.py` | FaceNet, Emotion, Age/Gender models |
| `models/embedding_index.py` | Annoy-based face search |
| `models/suggestion_engine.py` | AI-based suggestions |
| `models/embeddings.py` | Embedding utilities |
| `models/dnn_models/` | Model files management |
| `routes/api.py` (AI APIs) | - `/api/face-detect` <br> - `/api/auto-crop` <br> - `/api/sticker-positions` <br> - `/api/face-analyze` <br> - `/api/face-suggestions` <br> - `/api/recognize` <br> - `/api/users/embeddings` |
| `tests/test_face_detection.py` | Tests cho face detection |
| `scripts/manage_embeddings.py` | Script quản lý embeddings |
| `scripts/demo_dnn_features.py` | Demo AI features |

#### Chi tiết chức năng phụ trách:
1. **Face Detection:**
   - DNN-based face detection (Caffe model)
   - Detect largest face
   - Face region extraction với padding
   - Auto crop portrait (rule of thirds)
   - Face mask generation

2. **Face Recognition:**
   - FaceNet embedding extraction (128-dim)
   - Annoy index for fast search
   - User recognition system
   - Embedding management (add, search, delete)

3. **Face Analysis:**
   - Emotion detection (7 emotions)
   - Age estimation
   - Gender estimation
   - Facial landmarks (MediaPipe - 468 points)

4. **AI Suggestions:**
   - Filter suggestions based on emotion/age/gender
   - Template suggestions
   - Sticker positioning (hat, glasses, ears, mustache)

5. **Model Optimization:**
   - ONNX export for faster inference
   - Lazy loading models
   - Model caching

#### Ước tính khối lượng:
- ~2000 dòng code Python
- 8+ API endpoints
- 5 AI modules
- ~25% tổng công việc

---

### **👨‍💻 NGƯỜI 4: Frontend & Template/Collage System**
**Tên vai trò:** Frontend Developer / UI Specialist

#### Phạm vi công việc:
| File/Module | Nhiệm vụ chi tiết |
|-------------|-------------------|
| `models/template_engine.py` | Collage template renderer |
| `routes/views.py` | HTML page routes |
| `routes/api.py` (Collage APIs) | - `/api/templates` <br> - `/api/collage` |
| `templates/*.html` | Tất cả HTML templates |
| `static/js/capture.js` | Camera capture interface |
| `static/js/session.js` | Filter selection UI |
| `static/js/session_collage.js` | Collage preview & export |
| `static/css/style.css` | CSS styling |
| `static/templates/` | Template assets, stickers, decorations |
| `scripts/generate_template_previews.py` | Tạo preview cho templates |
| `tests/test_template_engine.py` | Tests cho template engine |

#### Chi tiết chức năng phụ trách:
1. **Template Engine (Python):**
   - Template metadata definitions (1x4, 2x2, classic_strip, etc.)
   - Create collage function
   - Photo placement với resize & crop
   - Fill modes (duplicate, placeholder, center)
   - Color customization
   - Decoration/sticker placement
   - SVG rasterization
   - Anchor points system

2. **Camera Capture Page:**
   - Camera access & permissions
   - Video preview (mirrored)
   - Countdown timer
   - Photo capture from video
   - Flash effect
   - Preview modal (confirm/retake)
   - Progress tracking (1/4 - 4/4)
   - Session creation flow

3. **Filter & Collage Page:**
   - Filter cards grid
   - Category tabs
   - Filter preview & comparison slider
   - Template selection (1x4/2x2)
   - SVG-based collage preview
   - Drag & drop sticker placement
   - Color picker for frame
   - AI beauty buttons
   - Auto accessories (face-based)
   - Export & download collage

4. **HTML Templates:**
   - base.html (layout)
   - index.html (landing)
   - capture.html (camera)
   - session.html (filter & collage)
   - gallery.html (ảnh đã lưu)

5. **CSS Styling:**
   - Responsive design
   - Component styles
   - Animations & effects

#### Ước tính khối lượng:
- ~700 dòng Python (template_engine)
- ~2500 dòng JavaScript
- ~500 dòng HTML/CSS
- 2 API endpoints
- ~25% tổng công việc

---

## 📈 Sơ Đồ Tương Tác Giữa Các Module

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Người 4)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐ │
│  │ capture.js  │  │ session.js  │  │ session_collage.js       │ │
│  │ (Camera)    │  │ (Filters)   │  │ (Collage Preview/Export) │ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬─────────────┘ │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REST API (routes/api.py)                    │
│  ┌────────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│  │ Người 1:       │ │ Người 2:     │ │ Người 3:               │ │
│  │ /sessions      │ │ /filters     │ │ /face-detect           │ │
│  │ /capture       │ │ /apply-filter│ │ /face-analyze          │ │
│  │ /images        │ │              │ │ /recognize             │ │
│  └────────┬───────┘ └──────┬───────┘ └────────────┬───────────┘ │
│           │                │                      │             │
│  ┌────────┴────────────────┴──────────────────────┴───────────┐ │
│  │                    /templates, /collage (Người 4)          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MODELS (Business Logic)                  │
│  ┌────────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│  │ Người 1:       │ │ Người 2:     │ │ Người 3:               │ │
│  │ database.py    │ │ filter_      │ │ face_detector.py       │ │
│  │ (Session,Photo)│ │ engine.py    │ │ model_manager.py       │ │
│  │                │ │ image_       │ │ embedding_index.py     │ │
│  │                │ │ processor.py │ │ suggestion_engine.py   │ │
│  └────────────────┘ └──────────────┘ └────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Người 4: template_engine.py                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Công Việc Chi Tiết

### **Người 1: Backend Core & Database**
- [ ] Review và hiểu cấu trúc app.py
- [ ] Quản lý config.py và environment variables
- [ ] Implement/maintain Session model
- [ ] Implement/maintain Photo model  
- [ ] Implement/maintain User model
- [ ] Implement/maintain FaceEmbedding model
- [ ] Implement/maintain FilterApplied model
- [ ] API: /api/health endpoint
- [ ] API: /api/upload endpoint
- [ ] API: /api/images serve endpoint
- [ ] API: /api/sessions CRUD
- [ ] API: /api/capture endpoint
- [ ] Implement utils/helpers.py
- [ ] Implement utils/validators.py
- [ ] Implement utils/decorators.py
- [ ] Implement utils/async_worker.py
- [ ] Viết tests cho database models
- [ ] Documentation cho API endpoints

### **Người 2: Image Processing & Filters**
- [ ] Implement filter_engine.py structure
- [ ] Basic filters: none, grayscale, sepia
- [ ] Basic filters: brightness, contrast
- [ ] Photobooth: soft_skin, pastel_glow
- [ ] Photobooth: sakura, sparkle, rainbow_leak
- [ ] Photobooth: heart_bokeh, polaroid, comic_pastel
- [ ] Photobooth: cool_mint, warm_peach
- [ ] Artistic: cartoon, pencil_sketch, oil_painting
- [ ] Instagram: nashville, valencia, xpro2
- [ ] Instagram: walden, kelvin
- [ ] Effects: blur, edge_detection, vintage
- [ ] Effects: cool_tone, warm_tone
- [ ] AI Beauty: smart_beauty (face-aware)
- [ ] AI Beauty: face_glow, portrait_pro
- [ ] image_processor.py: flip_horizontal
- [ ] image_processor.py: create_thumbnail
- [ ] image_processor.py: preprocess_for_model
- [ ] image_processor.py: is_blurry, is_low_light
- [ ] API: /api/filters endpoint
- [ ] API: /api/apply-filter endpoint
- [ ] Script: generate_filter_previews.py
- [ ] Tests: test_filters.py
- [ ] Documentation cho filters

### **Người 3: AI/ML & Face Detection**
- [ ] face_detector.py: DNN model loading
- [ ] face_detector.py: detect_faces function
- [ ] face_detector.py: detect_largest_face
- [ ] face_detector.py: get_face_region
- [ ] face_detector.py: auto_crop_portrait
- [ ] face_detector.py: get_face_mask
- [ ] model_manager.py: FaceNetEmbedder class
- [ ] model_manager.py: Emotion detection
- [ ] model_manager.py: Age/Gender estimation
- [ ] model_manager.py: ONNX export
- [ ] embedding_index.py: Annoy index
- [ ] embedding_index.py: search, add, remove
- [ ] suggestion_engine.py: filter suggestions
- [ ] suggestion_engine.py: template suggestions
- [ ] embeddings.py: utility functions
- [ ] API: /api/face-detect endpoint
- [ ] API: /api/auto-crop endpoint
- [ ] API: /api/sticker-positions endpoint
- [ ] API: /api/face-debug endpoint
- [ ] API: /api/face-analyze endpoint
- [ ] API: /api/face-suggestions endpoint
- [ ] API: /api/users endpoints
- [ ] API: /api/recognize endpoint
- [ ] Tests: test_face_detection.py
- [ ] Script: manage_embeddings.py
- [ ] Script: demo_dnn_features.py
- [ ] Documentation cho AI features

### **Người 4: Frontend & Collage System**
- [ ] template_engine.py: Template metadata
- [ ] template_engine.py: create_collage function
- [ ] template_engine.py: photo placement
- [ ] template_engine.py: fill modes
- [ ] template_engine.py: color customization
- [ ] template_engine.py: decoration placement
- [ ] template_engine.py: anchor points
- [ ] views.py: index, capture, session, gallery routes
- [ ] API: /api/templates endpoint
- [ ] API: /api/collage endpoint
- [ ] base.html: layout template
- [ ] index.html: landing page
- [ ] capture.html: camera page
- [ ] session.html: filter & collage page
- [ ] gallery.html: gallery page
- [ ] capture.js: camera access
- [ ] capture.js: countdown, capture, flash
- [ ] capture.js: preview modal
- [ ] capture.js: progress tracking
- [ ] session.js: filter cards, categories
- [ ] session.js: filter preview, comparison
- [ ] session_collage.js: template selection
- [ ] session_collage.js: SVG preview
- [ ] session_collage.js: sticker drag & drop
- [ ] session_collage.js: color picker
- [ ] session_collage.js: export collage
- [ ] style.css: responsive design
- [ ] style.css: components, animations
- [ ] Manage static/templates/ assets
- [ ] Script: generate_template_previews.py
- [ ] Tests: test_template_engine.py
- [ ] Documentation cho frontend

---


