# Photobooth API Documentation

## Base URL
```
http://localhost:5000/api
```

---

## Sessions

### POST /api/sessions
Tạo session mới cho 4-photo photobooth.

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "message": "Session created successfully"
}
```

### GET /api/sessions/{session_id}/photos
Lấy danh sách ảnh trong session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "photos": [
    {
      "id": 1,
      "photo_number": 1,
      "original_filename": "xxx.jpg",
      "processed_filename": "xxx.jpg",
      "original_url": "/api/images/originals/xxx.jpg",
      "processed_url": "/api/images/processed/xxx.jpg"
    }
  ]
}
```

---

## Photos

### POST /api/capture
Chụp và lưu ảnh vào session.

**Request (form-data):**
- `image`: File ảnh
- `session_id`: UUID của session
- `photo_number`: 1-4

**Response:**
```json
{
  "success": true,
  "photo_id": 1,
  "filename": "xxx.jpg",
  "processed_url": "/api/images/processed/xxx.jpg",
  "thumbnail_url": "/api/images/thumbnails/xxx.jpg"
}
```

### GET /api/images/{folder}/{filename}
Serve ảnh từ folder (originals, processed, thumbnails).

---

## Filters

### GET /api/filters
Lấy danh sách tất cả filters có sẵn.

**Response:**
```json
{
  "filters": [
    {
      "name": "smart_beauty",
      "category": "ai_beauty",
      "display_name": "Smart Beauty",
      "description": "AI skin smoothing - chỉ làm mịn vùng mặt",
      "example_thumbnail": "filter_previews/smart_beauty.jpg"
    }
  ]
}
```

**Filter Categories:**
- `basic`: none, grayscale, sepia, brightness, contrast
- `photobooth`: soft_skin, pastel_glow, sakura, sparkle, etc.
- `artistic`: cartoon, pencil_sketch, oil_painting
- `instagram`: nashville, valencia, xpro2, walden, kelvin
- `effects`: blur, edge_detection, vintage, cool_tone, warm_tone
- `ai_beauty`: smart_beauty, face_glow, portrait_pro

### POST /api/sessions/{session_id}/apply-filter
Áp dụng filter cho tất cả ảnh trong session.

**Request:**
```json
{
  "filter_name": "smart_beauty",
  "commit": false
}
```

**Response:**
```json
{
  "success": true,
  "processed_images": [...],
  "filter_name": "smart_beauty",
  "committed": false
}
```

---

## Face Detection API 🤖

### POST /api/face-detect
Detect faces trong ảnh.

**Request (form-data):**
- `image`: File ảnh

**hoặc JSON:**
```json
{
  "filename": "xxx.jpg"
}
```

**Query Parameters:**
- `confidence`: Ngưỡng tin cậy (0.0-1.0, default 0.5)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "faces": [
    {
      "bbox": {
        "x": 100,
        "y": 80,
        "width": 150,
        "height": 180
      },
      "confidence": 0.9823,
      "center": {
        "x": 175,
        "y": 170
      }
    }
  ]
}
```

### POST /api/auto-crop
Tự động crop ảnh để center vào khuôn mặt.

**Request (form-data):**
- `image`: File ảnh

**hoặc JSON:**
```json
{
  "filename": "xxx.jpg"
}
```

**Query Parameters:**
- `ratio`: Tỉ lệ height/width (default 1.33 = 4:3)
- `padding`: Padding quanh mặt (default 0.4)
- `save`: "true" để lưu file, "false" để trả về base64

**Response (save=false):**
```json
{
  "success": true,
  "image_base64": "...",
  "width": 400,
  "height": 533
}
```

**Response (save=true):**
```json
{
  "success": true,
  "filename": "cropped_xxx.jpg",
  "url": "/api/images/processed/cropped_xxx.jpg"
}
```

### POST /api/sticker-positions
Lấy vị trí gợi ý để đặt sticker dựa trên face detection.

**Request (form-data):**
- `image`: File ảnh

**hoặc JSON:**
```json
{
  "filename": "xxx.jpg"
}
```

**Query Parameters:**
- `sticker_type`: "hat", "glasses", "ears", "mustache" (default "hat")

**Response:**
```json
{
  "success": true,
  "sticker_type": "hat",
  "count": 1,
  "positions": [
    {
      "x": 175,
      "y": 50,
      "scale": 1.5,
      "anchor": "bottom-center",
      "face_bbox": {
        "x": 100,
        "y": 80,
        "width": 150,
        "height": 180
      },
      "confidence": 0.9823
    }
  ]
}
```

### POST /api/face-debug
Debug endpoint: Vẽ bounding boxes lên ảnh.

**Request (form-data):**
- `image`: File ảnh

**Response:**
```json
{
  "success": true,
  "image_base64": "...",
  "faces_detected": 2
}
```

---

## Collage

### GET /api/templates
Lấy danh sách templates có sẵn.

### POST /api/collage
Tạo collage từ session photos.

**Request:**
```json
{
  "session_id": "uuid",
  "template": "classic_strip",
  "colors": {
    "bg": "#FFFFFF",
    "accent": "#FF69B4"
  },
  "decorations": [
    {
      "path": "static/templates/decorations/heart.svg",
      "x": 100,
      "y": 200,
      "scale": 1.0
    }
  ],
  "fill_mode": "duplicate"
}
```

---

## Health Check

### GET /api/health
Kiểm tra API hoạt động.

**Response:**
```json
{
  "status": "ok",
  "message": "Photobooth API is running"
}
```

---

## Error Responses

Tất cả endpoints trả về error theo format:
```json
{
  "error": "Error message here"
}
```

HTTP Status Codes:
- `400`: Bad Request (thiếu parameters, invalid input)
- `404`: Not Found (session/photo không tồn tại)
- `500`: Internal Server Error

