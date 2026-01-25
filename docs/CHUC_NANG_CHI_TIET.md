# 📸 MÔ TẢ CHI TIẾT CÁC CHỨC NĂNG - PHOTOBOOTH WEB APPLICATION

> Tài liệu này mô tả đầy đủ tất cả các chức năng của project, bao gồm luồng xử lý, logic hoạt động và công nghệ sử dụng.

---

## 📋 TỔNG QUAN CÁC CHỨC NĂNG

Project Photobooth Web Application bao gồm **9 nhóm chức năng chính**:

| STT | Nhóm chức năng | Mô tả ngắn |
|-----|----------------|------------|
| 1 | Chụp ảnh Photobooth | Chụp 4 ảnh từ webcam theo phiên |
| 2 | Áp dụng Filter | 15+ bộ lọc hình ảnh chuyên nghiệp |
| 3 | Tạo Collage/Template | Ghép ảnh thành khung template |
| 4 | Nhận diện khuôn mặt | Face Detection với DNN |
| 5 | Gắn phụ kiện lên khuôn mặt | Stickers tự động theo vị trí mặt |
| 6 | Làm đẹp thông minh (AI Beauty) | Filter chỉ tác động vùng mặt |
| 7 | Nhận diện người dùng | Face Recognition với FaceNet |


---

## 1. CHỨC NĂNG CHỤP ẢNH PHOTOBOOTH

### 1.1. Mô tả
Cho phép người dùng chụp một phiên 4 ảnh liên tiếp từ webcam, giống như booth chụp ảnh truyền thống. Mỗi ảnh được lưu dưới 3 phiên bản: gốc, đã xử lý và thumbnail.

### 1.2. Luồng xử lý

```
[User truy cập /capture]
        │
        ▼
[JavaScript yêu cầu quyền camera]
        │
        ▼
[WebRTC getUserMedia() - stream video]
        │
        ▼
[User nhấn "Bắt đầu" → POST /api/sessions]
        │
        ▼
[Server tạo Session (UUID) → lưu DB → trả về session_id]
        │
        ▼
[User nhấn "Chụp" → Countdown 3-2-1]
        │
        ▼
[Canvas capture frame từ video stream]
        │
        ▼
[Hiệu ứng Flash (CSS animation)]
        │
        ▼
[canvas.toBlob() → FormData → POST /api/capture]
        │
        ▼
[Server xử lý ảnh:]
  ├── Đọc image data từ request
  ├── Chuyển đổi sang RGB (Pillow)
  ├── Flip horizontal (sửa mirror effect)
  ├── Lưu ảnh gốc → /uploads/originals/
  ├── Lưu ảnh đã xử lý → /uploads/processed/
  ├── Tạo thumbnail (200x200) → /uploads/thumbnails/
  └── Insert record vào bảng photos
        │
        ▼
[Trả về JSON với URLs của ảnh]
        │
        ▼
[Client hiển thị preview → Confirm/Retake]
        │
        ▼
[Lặp lại cho đến khi đủ 4 ảnh]
        │
        ▼
[Cập nhật session.status = 'filtering']
        │
        ▼
[Redirect đến /session/{session_id}]
```

### 1.3. Logic chi tiết

**Phía Client (capture.js):**
- Sử dụng `navigator.mediaDevices.getUserMedia()` để truy cập webcam
- Video stream được mirror (scaleX(-1)) để giống soi gương
- Countdown sử dụng `setInterval()` với hiển thị overlay
- Frame capture bằng `canvas.getContext('2d').drawImage(video, 0, 0)`
- Chuyển đổi canvas thành blob: `canvas.toBlob(callback, 'image/jpeg', 0.95)`

**Phía Server (api.py):**
- Tạo filename unique: `{timestamp}_{uuid}_{photo_number}.jpg`
- Xử lý ảnh với `ImageProcessor.process_uploaded_image()`
- Lưu 3 phiên bản với chất lượng JPEG 90%

### 1.4. Công nghệ sử dụng
- **WebRTC API**: Truy cập camera từ browser
- **HTML5 Canvas**: Capture và xử lý frame
- **Flask**: API endpoints
- **Pillow (PIL)**: Xử lý ảnh (flip, convert, resize)
- **SQLAlchemy**: Lưu thông tin vào database

### 1.5. API Endpoints liên quan
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| POST | `/api/sessions` | Tạo session mới |
| POST | `/api/capture` | Upload và lưu ảnh |
| GET | `/api/sessions/{id}/photos` | Lấy danh sách ảnh của session |
| GET | `/api/images/{folder}/{filename}` | Serve file ảnh |

---

## 2. CHỨC NĂNG ÁP DỤNG FILTER

### 2.1. Mô tả
Cung cấp hơn 15 bộ lọc hình ảnh chuyên nghiệp, từ filter cơ bản (grayscale, sepia) đến filter phức tạp (cartoon, AI beauty).

### 2.2. Danh sách Filter

**Nhóm Basic:**
| Filter | Thuật toán |
|--------|------------|
| `grayscale` | Chuyển RGB → Grayscale bằng công thức luminosity |
| `sepia` | Áp dụng ma trận màu sepia: R=0.393r+0.769g+0.189b |
| `brightness` | `ImageEnhance.Brightness().enhance(1.2)` |
| `contrast` | `ImageEnhance.Contrast().enhance(1.3)` |

**Nhóm Photobooth:**
| Filter | Thuật toán |
|--------|------------|
| `soft_skin` | Bilateral filter 2 lần + brightness boost |
| `pastel_glow` | Color enhance + Gaussian blur + Screen blend |
| `sakura` | Pink tint + random ellipses (cánh hoa) |
| `sparkle` | Brightness + random star overlays |
| `rainbow_leak` | Gradient overlay RGB + additive blend |
| `heart_bokeh` | Heart-shaped polygon overlays |
| `polaroid` | Warm tone + vignette + white border |

**Nhóm Artistic:**
| Filter | Thuật toán |
|--------|------------|
| `cartoon` | Bilateral filter + Adaptive threshold (edges) + bitwise AND |
| `pencil_sketch` | Grayscale → Invert → Gaussian blur → Divide blend |
| `oil_painting` | cv2.xphoto.oilPainting() hoặc multiple bilateral |
| `comic_pastel` | Bilateral + Canny edges + Color quantization |

**Nhóm Instagram-style:**
| Filter | Thuật toán |
|--------|------------|
| `nashville` | High contrast + warm saturation + sepia |
| `valencia` | Brightness up + warm tone |
| `xpro2` | High contrast + cool tone + vignette |
| `walden` | Vintage tone + warm sepia |
| `kelvin` | Strong warm orange tone |

### 2.3. Luồng xử lý

```
[User chọn filter trên UI]
        │
        ▼
[POST /api/apply-filter với {session_id, filter_name}]
        │
        ▼
[Server load tất cả ảnh của session]
        │
        ▼
[Loop qua từng ảnh:]
  ├── Mở ảnh gốc từ /originals/
  ├── Gọi FilterEngine.apply_filter(image, filter_name)
  │         │
  │         ▼
  │   [Filter Engine dispatch đến method tương ứng]
  │   [Xử lý ảnh với OpenCV/Pillow]
  │         │
  │         ▼
  ├── Lưu ảnh đã filter → /processed/
  ├── Tạo thumbnail mới → /thumbnails/
  └── Cập nhật photo.applied_filter trong DB
        │
        ▼
[Trả về JSON với URLs ảnh mới]
        │
        ▼
[Client cập nhật hiển thị]
```

### 2.4. Logic Bilateral Filter (Làm mịn da)

Bilateral filter là thuật toán quan trọng, được sử dụng trong nhiều filter:

```python
smooth = cv2.bilateralFilter(image, d=9, sigmaColor=85, sigmaSpace=85)
```

- **d=9**: Kích thước vùng lân cận (diameter)
- **sigmaColor=85**: Độ lệch chuẩn về màu sắc - pixel có màu khác biệt lớn sẽ không bị ảnh hưởng
- **sigmaSpace=85**: Độ lệch chuẩn về không gian - pixel xa hơn sẽ ít ảnh hưởng

**Kết quả:** Làm mịn vùng đồng màu (da) nhưng giữ sharp các cạnh (mắt, mũi, miệng).

### 2.5. Công nghệ sử dụng
- **OpenCV**: cv2.bilateralFilter, cv2.Canny, cv2.adaptiveThreshold
- **Pillow**: ImageEnhance, ImageFilter, ImageDraw
- **NumPy**: Ma trận xử lý pixel, blend operations

### 2.6. API Endpoints
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET | `/api/filters` | Lấy danh sách filter có sẵn |
| POST | `/api/apply-filter` | Áp dụng filter cho session |
| POST | `/api/sessions/{id}/preview-filter` | Preview filter (không lưu) |

---

## 3. CHỨC NĂNG TẠO COLLAGE/TEMPLATE

### 3.1. Mô tả
Ghép 4 ảnh đã chụp thành một khung collage theo các template có sẵn. Hỗ trợ thêm stickers, decorations và tùy chỉnh màu sắc.

### 3.2. Các Template có sẵn

| Template | Layout | Kích thước | Mô tả |
|----------|--------|------------|-------|
| `1x4` | Dọc | 420x1300 | Photo strip cơ bản |
| `2x2` | Lưới | 900x940 | Grid 2 hàng 2 cột |
| `classic_strip` | Dọc | 640x1850 | Strip với viền đen |
| `grid_modern` | Lưới | 1200x1200 | Grid hiện đại, gap nhỏ |
| `pastel_pink` | Dọc | 640x1850 | Nền hồng, góc bo tròn |

### 3.3. Luồng xử lý

```
[User chọn template và options]
        │
        ▼
[POST /api/collage với {session_id, template, stickers, decorations}]
        │
        ▼
[Server load 4 ảnh đã filter của session]
        │
        ▼
[TemplateEngine.create_collage():]
  │
  ├── Tạo canvas với size từ template config
  │
  ├── Fill background (solid color hoặc gradient)
  │
  ├── Loop qua 4 vị trí trong template:
  │     ├── Load ảnh từ file
  │     ├── Resize và crop để fit photo_size
  │     ├── Thêm rounded corners (nếu có)
  │     ├── Thêm border (nếu có)
  │     ├── Thêm shadow (nếu có)
  │     └── Paste vào canvas tại position[i]
  │
  ├── Thêm stickers với anchor points (nếu anchor_mode=True)
  │     ├── Load sticker PNG
  │     ├── Random rotation và scale
  │     └── Paste tại anchor points
  │
  ├── Thêm decorations (nếu có)
  │     ├── Load decoration file (PNG/SVG)
  │     ├── Apply scale và position
  │     └── Paste với alpha blending
  │
  └── Save canvas → /uploads/collages/
        │
        ▼
[Trả về collage_url]
```

### 3.4. Logic Resize và Crop

```python
def _resize_and_crop(self, image, target_size):
    # Tính tỷ lệ
    img_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]
    
    # Resize để cover target (không để trống)
    if img_ratio > target_ratio:
        # Ảnh rộng hơn → resize theo height
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)
    else:
        # Ảnh cao hơn → resize theo width
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
    
    image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # Crop center
    left = (new_width - target_size[0]) // 2
    top = (new_height - target_size[1]) // 2
    return image.crop((left, top, left + target_size[0], top + target_size[1]))
```

### 3.5. Anchor Points cho Stickers

Mỗi template có các anchor points được tính toán sẵn để đặt stickers không che ảnh:

```python
# Ví dụ anchor points cho template 4x1
ANCHOR_POINTS_4x1_OPTION1 = [
    (105, 45),    # Góc trên trái
    (269, 340),   # Giữa các ảnh
    (15, 150),    # Bên trái
    (410, 485),   # Bên phải
    ...
]
```

### 3.6. Công nghệ sử dụng
- **Pillow**: Image.new, paste, resize, crop
- **CairoSVG**: Render SVG stickers thành PNG
- **NumPy**: Gradient generation

### 3.7. API Endpoints
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET | `/api/templates` | Lấy danh sách templates |
| POST | `/api/collage` | Tạo collage từ session |

---

## 4. CHỨC NĂNG NHẬN DIỆN KHUÔN MẶT (FACE DETECTION)

### 4.1. Mô tả
Sử dụng Deep Neural Network để phát hiện vị trí khuôn mặt trong ảnh. Đây là chức năng nền tảng cho nhiều tính năng AI khác.

### 4.2. Model sử dụng

**SSD (Single Shot MultiBox Detector) với ResNet-10:**
- File model: `res10_300x300_ssd_iter_140000.caffemodel`
- File config: `deploy.prototxt`
- Input size: 300x300 pixels
- Output: Bounding boxes + Confidence scores

### 4.3. Luồng xử lý

```
[Input: PIL Image hoặc file path]
        │
        ▼
[Chuyển đổi PIL → NumPy → BGR (OpenCV format)]
        │
        ▼
[Preprocessing:]
  ├── Resize về 300x300
  └── Mean subtraction (104, 177, 123)
        │
        ▼
[cv2.dnn.blobFromImage()]
        │
        ▼
[Forward pass qua neural network]
        │
        ▼
[Output: tensor shape (1, 1, N, 7)]
  └── 7 values: batch_id, class_id, confidence, x1, y1, x2, y2
        │
        ▼
[Post-processing:]
  ├── Filter by confidence threshold (default 0.5)
  ├── Scale coordinates về kích thước ảnh gốc
  └── Return list of face dicts
```

### 4.4. Code Implementation

```python
def detect_faces(self, image, confidence_threshold=0.5):
    # Preprocessing
    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0),
        swapRB=False,
        crop=False
    )
    
    # Forward pass
    self._net.setInput(blob)
    detections = self._net.forward()
    
    # Post-processing
    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            x1, y1, x2, y2 = box.astype(int)
            faces.append({
                'bbox': (x1, y1, x2-x1, y2-y1),  # (x, y, width, height)
                'confidence': float(confidence),
                'center': (x1 + (x2-x1)//2, y1 + (y2-y1)//2)
            })
    
    return faces
```

### 4.5. Các phương thức hỗ trợ

| Method | Chức năng |
|--------|-----------|
| `detect_faces()` | Detect tất cả khuôn mặt |
| `detect_largest_face()` | Detect khuôn mặt lớn nhất |
| `get_face_region()` | Crop vùng mặt với padding |
| `auto_crop_portrait()` | Tự động crop theo Rule of Thirds |
| `get_face_mask()` | Tạo mask ellipse cho vùng mặt |
| `draw_faces()` | Vẽ bounding boxes lên ảnh (debug) |

### 4.6. Công nghệ sử dụng
- **OpenCV DNN Module**: cv2.dnn.readNetFromCaffe
- **Pre-trained Caffe Model**: ResNet-10 SSD
- **Singleton Pattern**: Load model một lần duy nhất

### 4.7. API Endpoints
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| POST | `/api/face-detect` | Detect faces trong ảnh |
| POST | `/api/auto-crop` | Auto crop portrait |
| POST | `/api/face-debug` | Vẽ boxes lên ảnh (debug) |

---

## 5. CHỨC NĂNG GẮN PHỤ KIỆN LÊN KHUÔN MẶT

### 5.1. Mô tả
Tự động phát hiện vị trí khuôn mặt và gắn các phụ kiện (mũ, kính, râu, tai thỏ...) vào đúng vị trí tương ứng.

### 5.2. Các loại phụ kiện hỗ trợ

| Sticker Type | Vị trí đặt | Size Multiplier |
|--------------|------------|-----------------|
| `hat` | Trên đầu, căn giữa | 1.4x face width |
| `noel_hat` | Trên đầu, nghiêng phải 15° | 1.5x face width |
| `glasses` | Vị trí mắt (1/3 từ trên) | 1.1x face width |
| `ears` | Trên đầu (tai thỏ) | 1.6x face width |
| `mustache` | Dưới mũi (2/3 từ trên) | 0.5x face width |
| `bow` | Trên đầu, bên phải | 0.6x face width |

### 5.3. Luồng xử lý

```
[POST /api/apply-sticker với {filename, sticker_type}]
        │
        ▼
[Load ảnh từ /processed/]
        │
        ▼
[FaceDetector.get_face_positions_for_stickers(image, type)]
        │
        ├── Detect tất cả faces
        │
        └── Với mỗi face, tính toán:
              ├── x, y: Vị trí đặt sticker
              ├── scale: Tỷ lệ resize sticker
              └── anchor: Điểm neo (center/bottom-center)
        │
        ▼
[Load sticker PNG với alpha channel]
        │
        ▼
[Loop qua mỗi face position:]
  ├── Tính target_width = face_width × multiplier
  ├── Tính target_height (giữ tỷ lệ)
  ├── Resize sticker
  ├── Tính paste_x, paste_y dựa trên anchor
  ├── Đảm bảo không vượt bounds
  └── Paste sticker với alpha blending
        │
        ▼
[Lưu kết quả hoặc trả về base64 preview]
```

### 5.4. Logic tính vị trí sticker

```python
def get_face_positions_for_stickers(self, image, sticker_type='hat'):
    faces = self.detect_faces(image)
    positions = []
    
    for face in faces:
        x, y, w, h = face['bbox']
        cx, cy = face['center']
        
        if sticker_type == 'hat':
            pos = {
                'x': cx,                    # Căn giữa theo face
                'y': y - int(h * 0.15),     # Trên đầu 15%
                'scale': w / 100,
                'anchor': 'bottom-center'   # Neo ở đáy sticker
            }
        elif sticker_type == 'glasses':
            pos = {
                'x': cx,
                'y': y + int(h * 0.35),     # 35% từ trên xuống (vị trí mắt)
                'scale': w / 80,
                'anchor': 'center'
            }
        # ... các loại khác
        
        positions.append(pos)
    
    return positions
```

### 5.5. Xử lý sticker background

Nhiều sticker có nền checkered (ô vuông đen xám). Hệ thống tự động xóa nền này:

```python
def _remove_checkered_background(image, tolerance=20):
    # Kiểm tra màu xám (R ≈ G ≈ B)
    # Xác định các dải màu checkered (128-170, 185-215)
    # Set alpha = 0 cho các pixel checkered
```

### 5.6. Công nghệ sử dụng
- **Face Detection**: OpenCV DNN
- **Image Compositing**: Pillow paste với alpha mask
- **Background Removal**: rembg library (optional)

### 5.7. API Endpoints
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| POST | `/api/sticker-positions` | Lấy vị trí gợi ý cho sticker |
| POST | `/api/apply-sticker` | Gắn sticker lên một ảnh |
| POST | `/api/apply-sticker-session` | Gắn sticker lên tất cả ảnh của session |
| GET | `/api/stickers/processed` | Lấy sticker đã xóa nền |

---

## 6. CHỨC NĂNG LÀM ĐẸP THÔNG MINH (AI BEAUTY)

### 6.1. Mô tả
Các filter làm đẹp thông minh chỉ tác động lên vùng khuôn mặt, giữ nguyên background và các chi tiết khác. Tự nhiên hơn filter thông thường.

### 6.2. Các AI Beauty Filters

**Smart Beauty (`smart_beauty`):**
- Detect faces
- Tạo elliptical mask mềm cho vùng mặt
- Áp dụng bilateral filter chỉ trong mask
- Blend với ảnh gốc: `result = original × (1-mask) + smooth × mask`
- Tăng brightness 3%

**Face Glow (`face_glow`):**
- Detect largest face
- Tạo radial gradient từ tâm mặt
- Glow radius = face_width × 1.5
- Soft falloff: `glow = (1 - dist/radius)^0.5`
- Additive blend glow lên ảnh
- Tăng saturation và brightness

**Portrait Pro (`portrait_pro`):**
- Kết hợp nhiều kỹ thuật:
  1. Smart skin smoothing (70% strength)
  2. Warm color grading (Red +3%, Blue -3%)
  3. Local contrast boost trong vùng mặt
  4. Final color grading (saturation +5%, brightness +2%)

### 6.3. Luồng xử lý Smart Beauty

```
[Input Image]
        │
        ▼
[FaceDetector.detect_faces()]
        │
        ▼
[Với mỗi face:]
  ├── get_face_mask() → elliptical mask
  ├── GaussianBlur mask (feather=15) → mềm viền
  │
  └── [Tạo smooth version:]
        cv2.bilateralFilter(image, 9, 75, 75) × 2
        │
        ▼
[Blend:]
  result = original × (1 - mask) + smooth × mask
        │
        ▼
[Brightness boost × 1.03]
        │
        ▼
[Output Image]
```

### 6.4. Face Mask Generation

```python
def get_face_mask(self, image, face, feather=10):
    x, y, w, h = face['bbox']
    cx, cy = face['center']
    
    # Tạo ellipse mask
    mask_w = int(w * 1.2)    # Rộng hơn face 20%
    mask_h = int(h * 1.3)    # Cao hơn face 30% (bao gồm trán)
    
    # Ellipse equation: ((x-cx)/a)² + ((y-cy)/b)² ≤ 1
    a = mask_w / 2
    b = mask_h / 2
    
    y_coords, x_coords = np.ogrid[:h, :w]
    ellipse = ((x_coords - cx) / a)**2 + ((y_coords - cy) / b)**2
    mask[ellipse <= 1] = 1.0
    
    # Feathering với Gaussian blur
    mask = cv2.GaussianBlur(mask, (0, 0), feather)
    
    return mask
```

### 6.5. Công nghệ sử dụng
- **Face Detection**: OpenCV DNN
- **Bilateral Filter**: cv2.bilateralFilter
- **Mask Operations**: NumPy array operations
- **Alpha Blending**: Weighted sum of arrays

---

## 7. CHỨC NĂNG NHẬN DIỆN NGƯỜI DÙNG (FACE RECOGNITION)

### 7.1. Mô tả
Cho phép lưu và nhận diện khuôn mặt người dùng quay lại. Sử dụng FaceNet để trích xuất embedding và Annoy để tìm kiếm nhanh.

### 7.2. Kiến trúc hệ thống

```
[Face Image]
        │
        ▼
[FaceNet Model (TensorFlow)]
        │
        ▼
[128-D Embedding Vector]
        │
        ├──[Lưu mới]──► Database (FaceEmbedding table)
        │                      │
        │                      ▼
        │               Annoy Index (rebuild)
        │
        └──[Tìm kiếm]──► Annoy Index
                               │
                               ▼
                        [Nearest Neighbors]
                               │
                               ▼
                        [User matches với similarity > threshold]
```

### 7.3. Luồng Đăng ký (Create Embedding)

```
[POST /api/face-embed với consent=true]
        │
        ▼
[Load ảnh, detect largest face]
        │
        ▼
[Crop face region với padding]
        │
        ▼
[FaceNet preprocessing:]
  ├── Resize về 160×160
  └── Normalize pixel values về [-1, 1]
        │
        ▼
[FaceNet forward pass → 128-D vector]
        │
        ▼
[L2 normalize vector]
        │
        ▼
[Serialize → LargeBinary → Database]
        │
        ▼
[Add to Annoy index → rebuild]
```

### 7.4. Luồng Nhận diện (Recognition)

```
[POST /api/recognize]
        │
        ▼
[Extract embedding từ ảnh mới]
        │
        ▼
[Annoy index.search(embedding, top_k)]
        │
        ▼
[Với mỗi kết quả:]
  ├── distance → similarity = 1 - distance
  ├── Filter by threshold (default 0.6)
  └── Lookup user info từ DB
        │
        ▼
[Return matches với similarity scores]
```

### 7.5. Annoy Index

**Annoy (Approximate Nearest Neighbors Oh Yeah)** của Spotify:
- Build binary tree structure
- Search time: O(log n) thay vì O(n)
- Trade-off: accuracy vs speed (configurable via num_trees)

```python
class EmbeddingIndex:
    def __init__(self, embedding_dim=128):
        self.index = AnnoyIndex(embedding_dim, 'angular')
    
    def build(self, embeddings_data):
        for i, data in enumerate(embeddings_data):
            self.index.add_item(i, data['embedding_vector'])
        self.index.build(10)  # 10 trees
    
    def search(self, query, top_k=5):
        return self.index.get_nns_by_vector(query, top_k, include_distances=True)
```

### 7.6. Privacy Compliance
- Yêu cầu `consent=true` để lưu embedding
- API xóa user và tất cả embeddings: `DELETE /api/users/{id}`

### 7.7. Công nghệ sử dụng
- **FaceNet**: TensorFlow/Keras model
- **Annoy**: Spotify's ANN library
- **SQLAlchemy**: Store embeddings as LargeBinary

### 7.8. API Endpoints
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| POST | `/api/face-embed?consent=true` | Tạo embedding mới |
| POST | `/api/recognize` | Nhận diện người dùng |
| GET | `/api/users` | Lấy danh sách users |
| DELETE | `/api/users/{id}` | Xóa user và embeddings |

---

## 8. CHỨC NĂNG PHÁT HIỆN CẢM XÚC (EMOTION DETECTION)

### 8.1. Mô tả
Phân tích biểu cảm khuôn mặt và phân loại thành 7 cảm xúc cơ bản: happy, sad, surprise, angry, fear, disgust, neutral.

### 8.2. Luồng xử lý

```
[POST /api/detect-emotion]
        │
        ▼
[Detect largest face]
        │
        ▼
[Crop face region]
        │
        ▼
[Emotion model preprocessing:]
  ├── Convert to grayscale (hoặc RGB tùy model)
  ├── Resize về input size của model
  └── Normalize pixel values
        │
        ▼
[Model inference → 7 probability scores]
        │
        ▼
[Output:]
  {
    'emotions': {
      'happy': 0.85,
      'neutral': 0.10,
      ...
    },
    'dominant': 'happy',
    'confidence': 0.85
  }
```

### 8.3. 7 Cảm xúc cơ bản

| Emotion | Mô tả |
|---------|-------|
| `happy` | Vui vẻ, mỉm cười |
| `sad` | Buồn bã |
| `surprise` | Ngạc nhiên |
| `angry` | Giận dữ |
| `fear` | Sợ hãi |
| `disgust` | Ghê tởm |
| `neutral` | Trung tính, không biểu cảm |

### 8.4. API Endpoint
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| POST | `/api/detect-emotion` | Phát hiện cảm xúc |

---

## 9. CHỨC NĂNG GỢI Ý THÔNG MINH (AI SUGGESTIONS)

### 9.1. Mô tả
Dựa trên đặc điểm phát hiện được (cảm xúc, tuổi, giới tính), hệ thống gợi ý filter và template phù hợp nhất.

### 9.2. Mapping Rules

**Emotion → Filter:**
```python
EMOTION_FILTER_MAP = {
    'happy': ['pastel_glow', 'sakura', 'sparkle', 'heart_bokeh'],
    'sad': ['sepia', 'vintage', 'warm_tone', 'soft_skin'],
    'surprise': ['rainbow_leak', 'comic_pastel', 'cartoon'],
    'angry': ['cool_tone', 'grayscale', 'edge_detection'],
    'neutral': ['portrait_pro', 'smart_beauty', 'none']
}
```

**Age Range → Filter:**
```python
AGE_FILTER_MAP = {
    '13-19': ['sparkle', 'rainbow_leak', 'cartoon', 'heart_bokeh'],
    '20-34': ['pastel_glow', 'sakura', 'polaroid', 'smart_beauty'],
    '35-54': ['sepia', 'vintage', 'soft_skin', 'warm_tone'],
    '55+': ['sepia', 'vintage', 'grayscale', 'warm_tone']
}
```

### 9.3. Scoring Algorithm

```python
def suggest_filters(emotion, age_range, gender, top_k=3):
    filter_scores = {}
    
    # Emotion weight = 3 (highest)
    if emotion:
        for f in EMOTION_FILTER_MAP[emotion]:
            filter_scores[f] = filter_scores.get(f, 0) + 3
    
    # Age weight = 2
    if age_range:
        for f in AGE_FILTER_MAP[age_range]:
            filter_scores[f] = filter_scores.get(f, 0) + 2
    
    # Gender weight = 1
    if gender:
        for f in GENDER_FILTER_MAP[gender]:
            filter_scores[f] = filter_scores.get(f, 0) + 1
    
    # Sort by score và return top_k
    sorted_filters = sorted(filter_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_filters[:top_k]
```

### 9.4. Luồng xử lý

```
[POST /api/suggestions]
        │
        ▼
[Detect face → Extract features:]
  ├── Emotion detection
  ├── Age estimation
  └── Gender estimation
        │
        ▼
[SuggestionEngine.get_personalized_suggestions()]
        │
        ▼
[Output:]
  {
    'emotion': 'happy',
    'suggested_filters': [
      {'filter_name': 'sparkle', 'score': 6, 'reason': 'suits happy mood'},
      {'filter_name': 'sakura', 'score': 5, 'reason': 'popular with 20-34'}
    ],
    'suggested_templates': [
      {'template_name': 'pastel_pink', 'score': 3, 'reason': 'modern and vibrant'}
    ]
  }
```

### 9.5. Công nghệ sử dụng
- **Emotion Detection Model**
- **Age/Gender Estimation Model**
- **Rule-based Scoring**: Weighted sum của các yếu tố

---

## 📊 TỔNG KẾT CÔNG NGHỆ

| Tầng | Công nghệ |
|------|-----------|
| **Web Framework** | Flask 3.0 |
| **Database** | SQLite + SQLAlchemy ORM |
| **Image Processing** | OpenCV 4.8, Pillow 10.1, NumPy |
| **Deep Learning** | TensorFlow 2.15, OpenCV DNN |
| **Face Detection** | SSD + ResNet-10 (Caffe model) |
| **Face Recognition** | FaceNet (128-D embeddings) |
| **ANN Search** | Annoy (Spotify) |
| **Facial Landmarks** | MediaPipe (468 points) |
| **Frontend** | HTML5, CSS3, JavaScript ES6+ |
| **Camera Access** | WebRTC API |

---

## 📁 CẤU TRÚC FILE QUAN TRỌNG

```
models/
├── face_detector.py      # Face Detection với DNN
├── filter_engine.py      # 15+ Image Filters
├── template_engine.py    # Collage/Template Creation
├── model_manager.py      # DNN Model Management
├── suggestion_engine.py  # AI Suggestions
├── embedding_index.py    # Annoy Index for Face Recognition
└── image_processor.py    # Basic Image Processing

routes/
├── api.py               # RESTful API Endpoints
└── views.py             # HTML Page Routes

static/js/
├── capture.js           # Camera Capture Logic
├── session.js           # Filter Selection UI
└── session_collage.js   # Collage Creation UI
```

---

*Tài liệu cập nhật: Tháng 1/2026*
