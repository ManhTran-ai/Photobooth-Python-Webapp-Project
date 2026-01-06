# Photobooth Algorithms Documentation

## Mục lục
1. [Face Detection với OpenCV DNN](#face-detection-với-opencv-dnn)
2. [Smart Beauty Filters](#smart-beauty-filters)
3. [Auto Face Crop](#auto-face-crop)
4. [Face-based Sticker Placement](#face-based-sticker-placement)
5. [Background Engine](#background-engine)

---

## Face Detection với OpenCV DNN

### Tổng quan
Photobooth sử dụng **OpenCV DNN module** với **SSD (Single Shot MultiBox Detector)** và backbone **ResNet-10** để nhận diện khuôn mặt trong thời gian thực.

### Lý do chọn DNN thay vì YOLO

| Tiêu chí | DNN (OpenCV SSD) | YOLO |
|----------|------------------|------|
| **Model size** | ~10MB | >100MB |
| **Speed (CPU)** | 30-50ms | 50-100ms |
| **Accuracy (frontal)** | ~95% | ~93% |
| **Dependencies** | Chỉ OpenCV | PyTorch/Ultralytics |
| **Use case** | Face-specific | General objects |

**Kết luận**: DNN phù hợp hơn cho Photobooth vì:
- Chỉ cần detect faces (không cần detect objects khác)
- Model nhẹ, không cần GPU
- Độ chính xác cao cho frontal faces (typical photobooth scenario)

### Kiến trúc Model

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

### Algorithm Chi tiết

#### 1. Preprocessing
```python
blob = cv2.dnn.blobFromImage(
    image,
    scalefactor=1.0,        # Không scale pixel values
    size=(300, 300),        # Model input size
    mean=(104.0, 177.0, 123.0),  # BGR mean subtraction
    swapRB=False,           # Không swap channels
    crop=False              # Không crop
)
```

**Giải thích**:
- `size=(300, 300)`: Model được train với input 300x300
- `mean=(104, 177, 123)`: Giá trị trung bình của ImageNet dataset (BGR format)
- Mean subtraction giúp normalize input, cải thiện convergence

#### 2. Forward Pass
```python
net.setInput(blob)
detections = net.forward()
# detections shape: (1, 1, N, 7)
# 7 values: [batch_id, class_id, confidence, x1, y1, x2, y2]
```

#### 3. Post-processing
```python
for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence > threshold:
        # Scale coordinates back to original image size
        box = detections[0, 0, i, 3:7] * [w, h, w, h]
```

### Độ phức tạp

- **Time Complexity**: O(n) với n là số pixels
- **Space Complexity**: O(1) (fixed model size)
- **Actual Performance**: ~30-50ms trên CPU (Intel i5)

---

## Smart Beauty Filters

### Tổng quan
Smart Beauty Filters sử dụng face detection để áp dụng các hiệu ứng làm đẹp **chỉ lên vùng khuôn mặt**, giữ nguyên background và các chi tiết khác.

### 1. Smart Beauty Filter

#### Algorithm
```
1. Detect faces using DNN
2. For each face:
   a. Create elliptical mask covering face region
   b. Apply Gaussian blur to feather mask edges
   c. Apply bilateral filter to entire image
   d. Blend: result = original * (1-mask) + smooth * mask
3. Apply subtle brightness boost (+3%)
```

#### Bilateral Filter
Bilateral filter là key algorithm cho skin smoothing:

```python
smooth = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
```

**Công thức**:
$$I_{filtered}(x) = \frac{1}{W_p} \sum_{x_i \in \Omega} I(x_i) \cdot f_r(||I(x_i) - I(x)||) \cdot g_s(||x_i - x||)$$

Trong đó:
- $f_r$: Range kernel (Gaussian trên intensity)
- $g_s$: Spatial kernel (Gaussian trên distance)
- $W_p$: Normalization factor

**Ưu điểm**:
- Smooths similar colors (skin)
- Preserves edges (eyes, mouth, nose)

#### Face Mask Generation
```python
# Elliptical mask
ellipse = ((x - cx)/a)^2 + ((y - cy)/b)^2 <= 1

# Feathering with Gaussian blur
mask = cv2.GaussianBlur(mask, (0, 0), sigma=15)
```

### 2. Face Glow Filter

#### Algorithm
```
1. Detect largest face
2. Calculate radial gradient from face center:
   glow = 1 - (distance / glow_radius)
   glow = glow^0.5  # Soft falloff
3. Add glow to image (additive blending)
4. Enhance saturation (+8%) and brightness (+2%)
```

#### Radial Gradient Formula
```python
dist = sqrt((x - cx)^2 + (y - cy)^2)
glow = clip(1 - dist/radius, 0, 1)
glow = glow ** 0.5  # Square root for softer falloff
```

### 3. Portrait Pro Filter

#### Algorithm (Multi-step)
```
Step 1: Smart Skin Smoothing
   - Bilateral filter với mask chỉ vùng mặt
   - Blend 70% smooth + 30% original

Step 2: Warm Color Grading
   - Red channel: +3%
   - Blue channel: -3%
   
Step 3: Contrast Enhancement
   - Local contrast boost trong vùng mặt
   - Formula: result = image + (image - mean) * 0.1 * mask

Step 4: Final Color Grading
   - Saturation: +5%
   - Brightness: +2%
```

---

## Auto Face Crop

### Mục đích
Tự động crop ảnh để center khuôn mặt, sử dụng **Rule of Thirds** để đặt mặt ở vị trí đẹp nhất.

### Algorithm

```
1. Detect largest face
2. Calculate crop dimensions based on face size:
   crop_width = face_size * (1 + 2*padding)
   crop_height = crop_width * target_ratio
   
3. Position face at 1/3 from top (Rule of Thirds):
   face_y_target = crop_height / 3
   
4. Calculate crop origin:
   crop_x = face_center_x - crop_width/2
   crop_y = face_center_y - face_y_target
   
5. Adjust bounds to stay within image
6. Crop and return
```

### Rule of Thirds
```
+-----+-----+-----+
|     |  ●  |     |  ← Face positioned here (1/3 from top)
+-----+-----+-----+
|     |     |     |
+-----+-----+-----+
|     |     |     |
+-----+-----+-----+
```

### Parameters
- `target_ratio`: Height/Width ratio (default: 4/3 for portrait)
- `padding`: Extra space around face (default: 40%)

---

## Face-based Sticker Placement

### Mục đích
Tự động tính toán vị trí đặt sticker (mũ, kính, râu, tai thỏ...) dựa trên vị trí khuôn mặt.

### Algorithm

```python
def get_sticker_position(face, sticker_type):
    x, y, w, h = face['bbox']
    cx, cy = face['center']
    
    if sticker_type == 'hat':
        return {
            'x': cx,
            'y': y - h*0.3,  # Above head
            'scale': w/100,
            'anchor': 'bottom-center'
        }
    elif sticker_type == 'glasses':
        return {
            'x': cx,
            'y': y + h*0.35,  # Eye level
            'scale': w/80,
            'anchor': 'center'
        }
    elif sticker_type == 'ears':
        return {
            'x': cx,
            'y': y - h*0.1,  # Top of head
            'scale': w/60,
            'anchor': 'bottom-center'
        }
    elif sticker_type == 'mustache':
        return {
            'x': cx,
            'y': y + h*0.7,  # Below nose
            'scale': w/120,
            'anchor': 'center'
        }
```

### Face Proportions Used
```
+------------------+
|      HAT         |  y - 30% height
+------------------+
|      EARS        |  y - 10% height
+------------------+
|     GLASSES      |  y + 35% height (eye level)
+------------------+
|    MUSTACHE      |  y + 70% height
+------------------+
```

---

## Performance Benchmarks

### Face Detection Speed
| Image Size | Detection Time (CPU) |
|------------|---------------------|
| 640x480    | ~25ms               |
| 1280x720   | ~40ms               |
| 1920x1080  | ~60ms               |

### Smart Beauty Filter Speed
| Filter | Time (640x480) | Time (1920x1080) |
|--------|----------------|------------------|
| smart_beauty | ~80ms | ~200ms |
| face_glow | ~50ms | ~120ms |
| portrait_pro | ~120ms | ~300ms |

---

## API Endpoints

### POST /api/face-detect
Detect faces trong ảnh.

**Request**:
```json
{
  "filename": "photo.jpg"
}
```

**Response**:
```json
{
  "success": true,
  "count": 2,
  "faces": [
    {
      "bbox": {"x": 100, "y": 80, "width": 150, "height": 180},
      "confidence": 0.9823,
      "center": {"x": 175, "y": 170}
    }
  ]
}
```

### POST /api/auto-crop
Auto crop ảnh focus vào khuôn mặt.

### POST /api/sticker-positions
Lấy vị trí gợi ý để đặt sticker.

---

## Background Engine

### Tổng quan
Background Engine cho phép thay đổi/xóa background của ảnh và thay thế bằng các loại background khác nhau.

### Các phương pháp tách người khỏi background

#### 1. GrabCut Algorithm (Default)
```python
cv2.grabCut(image, mask, rect, bgdModel, fgdModel, iterations, mode)
```

**Cách hoạt động**:
1. Khởi tạo với rectangle chứa foreground (người)
2. Sử dụng GMM (Gaussian Mixture Model) để model foreground/background
3. Iterative refinement dựa trên graph cut optimization
4. Output: mask phân biệt người vs background

**Ưu điểm**: Chính xác cao cho ảnh có contrast rõ ràng
**Nhược điểm**: Chậm hơn các phương pháp khác (~100-200ms)

#### 2. Face-based Mask
```python
# Detect face -> Mở rộng vùng để bao body
body_region = face_bbox * expansion_factor
mask = create_ellipse_mask(body_region)
```

**Cách hoạt động**:
1. Detect khuôn mặt bằng DNN
2. Mở rộng vùng detect để bao gồm body (4x face height xuống dưới)
3. Tạo ellipse mask mềm

**Ưu điểm**: Nhanh (~50ms), dựa trên face detection đã có
**Nhược điểm**: Không chính xác bằng GrabCut

#### 3. Simple Oval Mask
```python
mask = create_oval_mask(image_size, center, axes)
```

**Cách hoạt động**: Tạo mask hình oval ở giữa ảnh
**Ưu điểm**: Rất nhanh (~5ms)
**Nhược điểm**: Không adapt theo hình dạng người

### Các loại Background

#### 1. Solid Colors
```python
bg = Image.new('RGB', size, color)
result = Image.composite(foreground, bg, mask)
```

#### 2. Gradient Backgrounds
```python
# Vertical gradient
for y in range(height):
    ratio = y / height
    color = interpolate(color1, color2, ratio)
    gradient[y, :] = color
```

**Các loại gradient**:
- `vertical`: Trên xuống dưới
- `horizontal`: Trái sang phải
- `diagonal`: Chéo
- `radial`: Từ tâm ra ngoài

#### 3. Blur Background (Bokeh Effect)
```python
blurred = image.filter(GaussianBlur(radius))
result = Image.composite(original, blurred, person_mask)
```

Tạo hiệu ứng bokeh như camera DSLR - người nét, background mờ.

#### 4. Pattern Backgrounds
```python
# Dots pattern
for y in range(0, height, spacing):
    for x in range(0, width, spacing):
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
```

**Các loại pattern**:
- `dots`: Chấm bi polka
- `stripes`: Sọc dọc
- `grid`: Lưới
- `hearts`: Trái tim
- `stars`: Ngôi sao

### API Endpoints

#### GET /api/backgrounds
Lấy danh sách backgrounds có sẵn.

#### POST /api/apply-background
Áp dụng background cho một ảnh.

#### POST /api/sessions/{id}/apply-background
Áp dụng background cho tất cả ảnh trong session.

### Performance

| Method | Time (640x480) |
|--------|----------------|
| GrabCut mask | ~150ms |
| Face-based mask | ~60ms |
| Simple mask | ~5ms |
| Apply solid bg | ~20ms |
| Apply gradient | ~30ms |
| Apply blur | ~50ms |
| Apply pattern | ~40ms |

---

## References

1. [OpenCV DNN Face Detector](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)
2. [SSD: Single Shot MultiBox Detector](https://arxiv.org/abs/1512.02325)
3. [Bilateral Filter](https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/MANDUCHI1/Bilateral_Filtering.html)
4. [Rule of Thirds in Photography](https://en.wikipedia.org/wiki/Rule_of_thirds)
5. [GrabCut Algorithm](https://docs.opencv.org/master/d8/d83/tutorial_py_grabcut.html)

