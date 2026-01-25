# 📸 PHOTOBOOTH PYTHON WEBAPP
## Bài Thuyết Trình Đồ Án

---

# 📋 NỘI DUNG THUYẾT TRÌNH

1. Giới thiệu Project
2. Các chức năng chính
3. Công nghệ sử dụng
4. Kiến trúc hệ thống
5. Luồng xử lý chức năng
6. Phân công công việc
7. Demo & Kết luận

**⏱️ Thời lượng: ~15 phút**

---

# 🎯 SLIDE 1: GIỚI THIỆU PROJECT

## Photobooth Python Webapp

### Mô tả
Ứng dụng web chụp ảnh photobooth tích hợp AI, cho phép người dùng:
- Chụp bộ 4 ảnh liên tiếp qua webcam
- Áp dụng 30+ bộ lọc ảnh chuyên nghiệp
- Tự động nhận diện khuôn mặt & gợi ý filter
- Tạo collage với nhiều template đẹp mắt
- Thêm sticker và decoration
- Xuất ảnh chất lượng cao

### Đối tượng sử dụng
- Quán cà phê, sự kiện, tiệc cưới
- Studio ảnh tự động
- Ứng dụng cá nhân

---

# ✨ SLIDE 2: CÁC CHỨC NĂNG CHÍNH

## 1️⃣ Chụp ảnh (Camera Capture)
- Truy cập webcam trực tiếp trên trình duyệt
- Đếm ngược 3-2-1 trước khi chụp
- Hiệu ứng flash khi chụp
- Xem trước và chụp lại nếu cần
- Chụp liên tiếp 4 ảnh/session

## 2️⃣ Bộ lọc ảnh (30+ Filters)
| Loại | Filters |
|------|---------|
| Basic | Grayscale, Sepia, Brightness, Contrast |
| Photobooth | Soft Skin, Pastel Glow, Sakura, Sparkle |
| Artistic | Cartoon, Pencil Sketch, Oil Painting |
| Instagram | Nashville, Valencia, XPro2, Walden |
| AI Beauty | Smart Beauty, Face Glow, Portrait Pro |

---

# ✨ SLIDE 3: CÁC CHỨC NĂNG CHÍNH (tiếp)

## 3️⃣ AI Face Detection & Analysis
- **Nhận diện khuôn mặt** với DNN (Deep Neural Network)
- **Phân tích cảm xúc** (7 loại: happy, sad, surprise, angry, fear, disgust, neutral)
- **Ước tính tuổi & giới tính**
- **Gợi ý filter thông minh** dựa trên phân tích khuôn mặt
- **Nhận diện người dùng** qua face embedding

## 4️⃣ Template & Collage
- Template layouts: 1x4 (dọc), 2x2 (lưới)
- Tùy chỉnh màu khung
- Drag & drop stickers
- Tự động đặt phụ kiện (mũ, kính, tai thỏ...)
- Xuất ảnh PNG chất lượng cao

---

# 🛠️ SLIDE 4: CÔNG NGHỆ SỬ DỤNG

## Backend
| Công nghệ | Mục đích |
|-----------|----------|
| **Python 3.10+** | Ngôn ngữ chính |
| **Flask 3.0** | Web framework |
| **SQLAlchemy** | ORM cho database |
| **SQLite** | Cơ sở dữ liệu |

## Image Processing
| Thư viện | Mục đích |
|----------|----------|
| **Pillow 10.1** | Xử lý ảnh cơ bản |
| **OpenCV 4.8** | Xử lý ảnh nâng cao, filters |
| **NumPy** | Tính toán ma trận |

---

# 🤖 SLIDE 5: CÔNG NGHỆ AI/ML

## Mô hình AI sử dụng

| Model | Chức năng | Format |
|-------|-----------|--------|
| **SSD MobileNet** | Face Detection | Caffe (.caffemodel) |
| **FaceNet** | Face Embedding (128-dim) | Keras/TensorFlow |
| **MediaPipe** | Facial Landmarks (468 điểm) | TensorFlow Lite |
| **DeepFace** | Emotion/Age/Gender | TensorFlow |

## Thư viện ML
| Thư viện | Mục đích |
|----------|----------|
| **TensorFlow 2.15** | Deep Learning framework |
| **MediaPipe 0.10** | Face mesh & landmarks |
| **Annoy** | Approximate Nearest Neighbor (face search) |
| **ONNX Runtime** | Model inference tối ưu |

---

# 🏗️ SLIDE 6: KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Camera Page │  │ Filter Page │  │ Collage Export  │  │
│  │ (capture.js)│  │ (session.js)│  │(session_collage)│  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
└─────────┼────────────────┼──────────────────┼───────────┘
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    REST API (Flask)                      │
│  /sessions  /capture  /filters  /face-detect  /collage  │
└─────────────────────────────────────────────────────────┘
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC                        │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Database │  │ FilterEngine │  │ FaceDetector/AI   │  │
│  │ (SQLite) │  │ (30+ filters)│  │ (DNN Models)      │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │              TemplateEngine (Collage)             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

# 🔄 SLIDE 7: LUỒNG XỬ LÝ - CHỤP ẢNH

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Browser  │    │  API     │    │ Database │
│  Action  │    │ (JS)     │    │ (Flask)  │    │ (SQLite) │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Click Start   │               │               │
     │──────────────>│               │               │
     │               │ POST /sessions│               │
     │               │──────────────>│ Create Session│
     │               │               │──────────────>│
     │               │   session_id  │               │
     │               │<──────────────│               │
     │               │               │               │
     │ Click Capture │               │               │
     │──────────────>│               │               │
     │               │ Countdown 3-2-1               │
     │               │ Capture frame │               │
     │               │ POST /capture │               │
     │               │──────────────>│ Save image    │
     │               │               │──────────────>│
     │               │  photo_url    │               │
     │               │<──────────────│               │
     │               │               │               │
     │ (Repeat x4)   │               │               │
```

---

# 🎨 SLIDE 8: LUỒNG XỬ LÝ - ÁP DỤNG FILTER

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Browser  │    │  API     │    │ Filter   │
│          │    │          │    │          │    │ Engine   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Select Filter │               │               │
     │──────────────>│               │               │
     │               │ POST /apply-filter            │
     │               │──────────────>│               │
     │               │               │ Load original │
     │               │               │ image         │
     │               │               │──────────────>│
     │               │               │               │
     │               │               │ Apply filter  │
     │               │               │ (OpenCV/PIL)  │
     │               │               │<──────────────│
     │               │               │               │
     │               │               │ Save processed│
     │               │               │ Create thumb  │
     │               │  preview_urls │               │
     │               │<──────────────│               │
     │ Show preview  │               │               │
     │<──────────────│               │               │
```

---

# 🤖 SLIDE 9: LUỒNG XỬ LÝ - AI FACE DETECTION

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Image   │    │   API    │    │   Face   │    │ Suggestion│
│  Input   │    │          │    │ Detector │    │  Engine   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Upload image  │               │               │
     │──────────────>│               │               │
     │               │ Convert to    │               │
     │               │ numpy array   │               │
     │               │──────────────>│               │
     │               │               │               │
     │               │               │ DNN Forward   │
     │               │               │ Pass (Caffe)  │
     │               │               │               │
     │               │  faces[]      │               │
     │               │  (bbox,       │               │
     │               │   confidence) │               │
     │               │<──────────────│               │
     │               │               │               │
     │               │ Analyze emotion/age/gender    │
     │               │──────────────────────────────>│
     │               │                               │
     │               │  suggested_filters[]          │
     │               │<──────────────────────────────│
     │  AI suggestions                               │
     │<──────────────│               │               │
```

---

# 🖼️ SLIDE 10: LUỒNG XỬ LÝ - TẠO COLLAGE

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Browser  │    │  API     │    │ Template │
│          │    │ (SVG)    │    │          │    │ Engine   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Select template (1x4/2x2)     │               │
     │──────────────>│               │               │
     │               │ Render SVG    │               │
     │               │ preview       │               │
     │               │               │               │
     │ Add stickers  │               │               │
     │ Change colors │               │               │
     │──────────────>│               │               │
     │               │ Update SVG    │               │
     │               │               │               │
     │ Click Export  │               │               │
     │──────────────>│ POST /collage │               │
     │               │──────────────>│               │
     │               │               │ Load photos   │
     │               │               │ Apply template│
     │               │               │ Add stickers  │
     │               │               │──────────────>│
     │               │               │               │
     │               │               │  PNG file     │
     │               │               │<──────────────│
     │               │  collage_url  │               │
     │               │<──────────────│               │
     │ Download PNG  │               │               │
     │<──────────────│               │               │
```

---

# 👥 SLIDE 11: PHÂN CÔNG CÔNG VIỆC

## Bảng Phân Công 4 Thành Viên

| Thành viên | Vai trò | Modules phụ trách |
|------------|---------|-------------------|
| **Người 1** | Backend Core | Database, Sessions, Core APIs, Utils |
| **Người 2** | Image Processing | 30+ Filters, Image Processor |
| **Người 3** | AI/ML Engineer | Face Detection, Recognition, Suggestions |
| **Người 4** | Frontend/Collage | UI, Templates, Collage System |

---

# 👨‍💻 SLIDE 12: CHI TIẾT CÔNG VIỆC

## Người 1: Backend Core & Database (~25%)
- ✅ Flask app factory, configuration
- ✅ Database models (Session, Photo, User, FaceEmbedding)
- ✅ Core APIs: `/sessions`, `/capture`, `/upload`, `/images`
- ✅ Utils: validators, helpers, decorators
- 📁 Files: `app.py`, `config.py`, `models/database.py`, `utils/`

## Người 2: Image Processing (~25%)
- ✅ 30+ image filters (OpenCV + Pillow)
- ✅ AI Beauty filters (face-aware processing)
- ✅ Image utilities (thumbnail, flip, blur detection)
- ✅ APIs: `/filters`, `/apply-filter`
- 📁 Files: `models/filter_engine.py`, `models/image_processor.py`

---

# 👨‍💻 SLIDE 13: CHI TIẾT CÔNG VIỆC (tiếp)

## Người 3: AI/ML Features (~25%)
- ✅ DNN Face Detection (Caffe model)
- ✅ FaceNet embedding (128-dim vectors)
- ✅ Emotion/Age/Gender analysis
- ✅ Annoy index for face search
- ✅ Smart suggestions engine
- ✅ APIs: `/face-detect`, `/face-analyze`, `/recognize`
- 📁 Files: `models/face_detector.py`, `model_manager.py`, `embedding_index.py`

## Người 4: Frontend & Collage (~25%)
- ✅ HTML templates (capture, session, gallery)
- ✅ Camera capture interface (JS)
- ✅ Filter selection UI
- ✅ Collage preview (SVG) & export
- ✅ Template engine (Pillow)
- 📁 Files: `templates/`, `static/js/`, `models/template_engine.py`

---

# 📊 SLIDE 14: THỐNG KÊ DỰ ÁN

## Code Statistics

| Metric | Số lượng |
|--------|----------|
| **Tổng số files Python** | 15+ |
| **Tổng dòng code Python** | ~5,000 |
| **Tổng dòng code JavaScript** | ~2,500 |
| **Số API endpoints** | 20+ |
| **Số image filters** | 30+ |
| **Số database models** | 5 |

## Dependencies
| Category | Count |
|----------|-------|
| Core packages | 5 |
| Image processing | 3 |
| Machine Learning | 5 |
| Utilities | 3 |

---

# 🎬 SLIDE 15: DEMO & KẾT LUẬN

## Demo Application
1. **Chụp ảnh:** Truy cập `/capture`, chụp 4 ảnh
2. **Chọn filter:** Duyệt và áp dụng filter yêu thích
3. **AI suggestions:** Xem gợi ý filter dựa trên khuôn mặt
4. **Tạo collage:** Chọn template, thêm sticker
5. **Export:** Tải ảnh PNG chất lượng cao

## Kết luận
- ✅ Ứng dụng photobooth hoàn chỉnh với AI
- ✅ Giao diện thân thiện, dễ sử dụng
- ✅ 30+ bộ lọc chuyên nghiệp
- ✅ Tích hợp face detection & recognition
- ✅ Hỗ trợ nhiều template collage

## Hướng phát triển
- 🔮 Thêm video recording
- 🔮 Mobile app (React Native)
- 🔮 Cloud deployment
- 🔮 Real-time face filters

---

# 🙏 CẢM ƠN ĐÃ LẮNG NGHE!

## Q&A - Hỏi Đáp

**GitHub:** [Repository Link]

**Team Members:**
- Người 1 - Backend Core
- Người 2 - Image Processing  
- Người 3 - AI/ML
- Người 4 - Frontend/Collage

---

# 📎 PHỤ LỤC: CẤU TRÚC THƯ MỤC

```
Photobooth-Python-Webapp/
├── app.py                 # Flask app factory
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── models/
│   ├── database.py        # DB models
│   ├── face_detector.py   # Face detection
│   ├── filter_engine.py   # 30+ filters
│   ├── template_engine.py # Collage creator
│   ├── model_manager.py   # AI models
│   └── suggestion_engine.py
├── routes/
│   ├── api.py             # REST endpoints
│   └── views.py           # Page routes
├── templates/             # HTML files
├── static/
│   ├── js/                # JavaScript
│   ├── css/               # Styles
│   └── templates/         # Assets
└── tests/                 # Unit tests
```

---

*Presentation created for Photobooth Python Webapp Project*
*January 2026*
