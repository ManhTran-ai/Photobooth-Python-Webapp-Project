# 📸 PHOTOBOOTH PYTHON WEBAPP
# Script Thuyết Trình Chi Tiết

---

## SLIDE 1: TRANG BÌA

**Tiêu đề:** PHOTOBOOTH PYTHON WEBAPP - Ứng Dụng Chụp Ảnh Tích Hợp AI

**Phụ đề:** Đồ án môn học

**Thông tin nhóm:**
- Thành viên 1: [Tên] - Backend Core
- Thành viên 2: [Tên] - Image Processing
- Thành viên 3: [Tên] - AI/ML
- Thành viên 4: [Tên] - Frontend/Collage

**Ngày:** Tháng 1/2026

**Lời dẫn:**
> "Xin chào thầy/cô và các bạn. Hôm nay nhóm chúng em xin trình bày đồ án Photobooth Python Webapp - một ứng dụng web chụp ảnh photobooth tích hợp trí tuệ nhân tạo."

---

## SLIDE 2: TỔNG QUAN DỰ ÁN

**Tiêu đề:** Giới Thiệu Dự Án

**Nội dung hiển thị:**
- Tên: Photobooth Python Webapp
- Loại: Ứng dụng web
- Mục đích: Chụp ảnh photobooth với AI

**Hình ảnh gợi ý:** Screenshot giao diện chính của ứng dụng

**Lời dẫn:**
> "Photobooth Python Webapp là một ứng dụng web cho phép người dùng chụp ảnh theo phong cách photobooth truyền thống, nhưng được tích hợp các tính năng AI hiện đại.

> Ứng dụng được xây dựng hoàn toàn bằng Python với Flask framework ở backend, và JavaScript ở frontend. Điểm đặc biệt của dự án là khả năng nhận diện khuôn mặt, phân tích cảm xúc, và tự động gợi ý bộ lọc phù hợp cho người dùng.

> Ứng dụng có thể được triển khai tại các quán cà phê, sự kiện, tiệc cưới, hoặc làm studio ảnh tự động."

---

## SLIDE 3: CÁC CHỨC NĂNG CHÍNH (Phần 1)

**Tiêu đề:** Chức Năng Chính - Chụp Ảnh & Bộ Lọc

**Nội dung hiển thị:**

**1. Chụp ảnh (Camera Capture)**
- Truy cập webcam trực tiếp trên trình duyệt
- Đếm ngược 3-2-1 trước khi chụp
- Hiệu ứng flash
- Chụp liên tiếp 4 ảnh/session

**2. Bộ lọc ảnh (30+ Filters)**
- Basic: Grayscale, Sepia, Brightness
- Photobooth: Soft Skin, Sakura, Sparkle
- Artistic: Cartoon, Pencil Sketch
- Instagram: Nashville, Valencia
- AI Beauty: Smart Beauty, Portrait Pro

**Hình ảnh gợi ý:** Grid hiển thị các filter khác nhau

**Lời dẫn:**
> "Chức năng đầu tiên và cốt lõi là chụp ảnh. Người dùng có thể truy cập webcam trực tiếp trên trình duyệt, không cần cài đặt phần mềm. Hệ thống sẽ đếm ngược 3-2-1 trước khi chụp, kèm hiệu ứng flash giống máy ảnh thật. Mỗi session cho phép chụp 4 ảnh liên tiếp.

> Chức năng thứ hai là hệ thống bộ lọc với hơn 30 filters chuyên nghiệp, được chia thành 5 nhóm: Basic, Photobooth, Artistic, Instagram-style và AI Beauty. Đặc biệt, các filter AI Beauty sử dụng nhận diện khuôn mặt để chỉ làm đẹp vùng da mặt, giữ nguyên background."

---

## SLIDE 4: CÁC CHỨC NĂNG CHÍNH (Phần 2)

**Tiêu đề:** Chức Năng Chính - AI & Collage

**Nội dung hiển thị:**

**3. AI Face Detection & Analysis**
- Nhận diện khuôn mặt (DNN)
- Phân tích cảm xúc (7 loại)
- Ước tính tuổi & giới tính
- Gợi ý filter thông minh

**4. Template & Collage**
- Template: 1x4 (dọc), 2x2 (lưới)
- Tùy chỉnh màu khung
- Drag & drop stickers
- Xuất PNG chất lượng cao

**Hình ảnh gợi ý:** Demo face detection với bounding box và collage output

**Lời dẫn:**
> "Chức năng thứ ba là tích hợp AI. Hệ thống sử dụng Deep Neural Network để nhận diện khuôn mặt trong ảnh, sau đó phân tích cảm xúc với 7 loại: vui, buồn, ngạc nhiên, giận dữ, sợ hãi, ghê tởm và trung tính. Dựa trên kết quả phân tích, hệ thống sẽ tự động gợi ý các filter phù hợp với tâm trạng người dùng.

> Chức năng cuối cùng là tạo collage. Người dùng có thể chọn template 1x4 theo chiều dọc hoặc 2x2 dạng lưới, tùy chỉnh màu khung, kéo thả sticker, và xuất ảnh PNG chất lượng cao để in hoặc chia sẻ."

---

## SLIDE 5: CÔNG NGHỆ SỬ DỤNG - BACKEND

**Tiêu đề:** Công Nghệ Sử Dụng - Backend & Database

**Nội dung hiển thị:**

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| Python | 3.10+ | Ngôn ngữ chính |
| Flask | 3.0 | Web framework |
| SQLAlchemy | 3.1 | ORM |
| SQLite | - | Cơ sở dữ liệu |
| Pillow | 10.1 | Xử lý ảnh |
| OpenCV | 4.8 | Computer Vision |

**Hình ảnh gợi ý:** Logo các công nghệ

**Lời dẫn:**
> "Về công nghệ backend, chúng em sử dụng Python làm ngôn ngữ chính với Flask framework để xây dựng REST API. Đây là lựa chọn phù hợp vì Flask nhẹ, linh hoạt và dễ tích hợp với các thư viện Machine Learning.

> Cơ sở dữ liệu sử dụng SQLite với SQLAlchemy ORM để quản lý các session chụp ảnh, thông tin người dùng và face embeddings.

> Về xử lý ảnh, chúng em kết hợp Pillow cho các thao tác cơ bản và OpenCV cho các thuật toán nâng cao như bilateral filter, edge detection, và cartoon effect."

---

## SLIDE 6: CÔNG NGHỆ SỬ DỤNG - AI/ML

**Tiêu đề:** Công Nghệ Sử Dụng - Mô Hình AI

**Nội dung hiển thị:**

| Mô hình | Chức năng | Đầu ra |
|---------|-----------|--------|
| SSD MobileNet (Caffe) | Face Detection | Bounding box, confidence |
| FaceNet | Face Embedding | Vector 128 chiều |
| MediaPipe | Facial Landmarks | 468 điểm mặt |
| DeepFace | Emotion/Age/Gender | Phân loại |

**Thư viện hỗ trợ:**
- TensorFlow 2.15
- MediaPipe 0.10
- Annoy (Approximate Nearest Neighbor)

**Hình ảnh gợi ý:** Sơ đồ pipeline AI

**Lời dẫn:**
> "Về phần AI và Machine Learning, chúng em sử dụng 4 mô hình chính.

> Thứ nhất là SSD MobileNet với định dạng Caffe để nhận diện khuôn mặt. Mô hình này cho độ chính xác cao và tốc độ xử lý nhanh.

> Thứ hai là FaceNet để trích xuất đặc trưng khuôn mặt thành vector 128 chiều, phục vụ cho việc nhận diện người dùng quay lại.

> Thứ ba là MediaPipe cho facial landmarks với 468 điểm trên khuôn mặt, giúp định vị chính xác vị trí đặt sticker như mũ, kính, tai thỏ.

> Thứ tư là DeepFace để phân tích cảm xúc, tuổi và giới tính.

> Để tìm kiếm nhanh trong database face embeddings, chúng em sử dụng thư viện Annoy với thuật toán Approximate Nearest Neighbor."

---

## SLIDE 7: KIẾN TRÚC HỆ THỐNG

**Tiêu đề:** Kiến Trúc Hệ Thống

**Nội dung hiển thị:**

```
┌─────────────────────────────────────┐
│         FRONTEND (Browser)          │
│  Camera │ Filter UI │ Collage UI    │
└────────────────┬────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────┐
│          FLASK REST API             │
│  /sessions /capture /filters /collage│
└────────────────┬────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│Database│ │ Filter   │ │ AI/ML    │
│(SQLite)│ │ Engine   │ │ Models   │
└────────┘ └──────────┘ └──────────┘
```

**Hình ảnh gợi ý:** Sơ đồ kiến trúc 3 tầng với icons

**Lời dẫn:**
> "Hệ thống được thiết kế theo kiến trúc 3 tầng.

> Tầng Frontend chạy trên trình duyệt, bao gồm giao diện camera để chụp ảnh, giao diện chọn filter, và giao diện tạo collage. Tất cả được xây dựng bằng JavaScript vanilla, không sử dụng framework phức tạp.

> Tầng Backend là Flask REST API với các endpoint chính: /sessions để quản lý phiên chụp, /capture để nhận ảnh, /filters để xử lý bộ lọc, và /collage để tạo ảnh ghép.

> Tầng Data bao gồm SQLite database để lưu trữ metadata, Filter Engine để xử lý ảnh, và các AI Models để nhận diện và phân tích khuôn mặt."

---

## SLIDE 8: LUỒNG XỬ LÝ - CHỤP ẢNH

**Tiêu đề:** Luồng Xử Lý - Chụp Ảnh

**Nội dung hiển thị:**

```
User → Click Start → Tạo Session → Session ID
                          ↓
User → Click Capture → Countdown 3-2-1 → Capture Frame
                          ↓
                    POST /api/capture
                          ↓
              Lưu Original + Thumbnail → Database
                          ↓
                    Trả về URL ảnh
                          ↓
               Lặp lại 4 lần → Hoàn tất Session
```

**Hình ảnh gợi ý:** Flowchart hoặc sequence diagram

**Lời dẫn:**
> "Đây là luồng xử lý khi người dùng chụp ảnh.

> Bước 1: Người dùng click nút Start, hệ thống gọi API tạo session mới và nhận về session ID.

> Bước 2: Khi click Capture, giao diện hiển thị countdown 3-2-1, sau đó capture frame từ video stream.

> Bước 3: Frame ảnh được gửi lên server qua API /capture dưới dạng blob.

> Bước 4: Server lưu ảnh gốc, tạo thumbnail, và cập nhật database.

> Bước 5: Trả về URL ảnh cho frontend hiển thị preview.

> Quy trình này lặp lại 4 lần để hoàn tất một session chụp ảnh."

---

## SLIDE 9: LUỒNG XỬ LÝ - ÁP DỤNG FILTER

**Tiêu đề:** Luồng Xử Lý - Áp Dụng Filter

**Nội dung hiển thị:**

```
User chọn Filter → POST /api/apply-filter
                          ↓
              Load ảnh gốc từ storage
                          ↓
         FilterEngine.apply_filter(image, filter_name)
                          ↓
    ┌─────────────────────┼─────────────────────┐
    ▼                     ▼                     ▼
 OpenCV              Pillow                Face-aware
 (Cartoon,           (Color,               (Smart Beauty,
  Edge)              Enhance)              Portrait Pro)
                          ↓
              Lưu processed image + thumbnail
                          ↓
                  Trả về preview URL
```

**Hình ảnh gợi ý:** Before/After của một vài filters

**Lời dẫn:**
> "Khi người dùng chọn một filter, frontend gửi request đến API apply-filter với session ID và tên filter.

> Server load ảnh gốc từ storage, sau đó gọi FilterEngine để áp dụng filter.

> Tùy loại filter, hệ thống sử dụng các thư viện khác nhau: OpenCV cho các hiệu ứng như cartoon, edge detection; Pillow cho điều chỉnh màu sắc và độ sáng; và kết hợp Face Detection cho các filter AI Beauty chỉ xử lý vùng khuôn mặt.

> Kết quả được lưu lại và trả về URL để frontend hiển thị preview. Người dùng có thể thử nhiều filter khác nhau trước khi quyết định."

---

## SLIDE 10: LUỒNG XỬ LÝ - AI FACE DETECTION

**Tiêu đề:** Luồng Xử Lý - AI Face Detection

**Nội dung hiển thị:**

```
Upload Image → Convert to numpy array
                    ↓
         DNN Forward Pass (Caffe Model)
                    ↓
         Detect faces → Bounding boxes
                    ↓
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
 Emotion        Age/Gender      Face Embedding
 Analysis       Estimation      (FaceNet)
                    ↓
         SuggestionEngine.suggest_filters()
                    ↓
         Trả về: faces[], suggestions[]
```

**Hình ảnh gợi ý:** Ảnh demo với face bounding box và emotion label

**Lời dẫn:**
> "Luồng xử lý AI bắt đầu khi người dùng upload ảnh hoặc chụp ảnh mới.

> Ảnh được convert sang numpy array và đưa qua DNN model để detect faces. Kết quả là các bounding box với độ tin cậy.

> Từ mỗi khuôn mặt phát hiện được, hệ thống thực hiện song song 3 phân tích: phân tích cảm xúc, ước tính tuổi và giới tính, và trích xuất face embedding.

> Suggestion Engine sử dụng kết quả phân tích để gợi ý filter phù hợp. Ví dụ: nếu phát hiện người dùng đang vui, hệ thống sẽ gợi ý các filter tươi sáng như Sparkle, Sakura; nếu phát hiện người trẻ tuổi, sẽ gợi ý các filter trendy như Instagram filters."

---

## SLIDE 11: LUỒNG XỬ LÝ - TẠO COLLAGE

**Tiêu đề:** Luồng Xử Lý - Tạo Collage

**Nội dung hiển thị:**

```
User chọn Template (1x4/2x2) → Render SVG Preview
                    ↓
User tùy chỉnh: màu, stickers, vị trí
                    ↓
Click Export → POST /api/collage
                    ↓
         TemplateEngine.create_collage()
                    ↓
    Load photos → Resize & Crop → Place on canvas
                    ↓
         Add decorations/stickers
                    ↓
         Save PNG → Trả về download URL
```

**Hình ảnh gợi ý:** Giao diện tạo collage và output mẫu

**Lời dẫn:**
> "Luồng tạo collage bắt đầu khi người dùng chọn template.

> Frontend render preview bằng SVG để người dùng có thể thấy ngay kết quả. Người dùng có thể tùy chỉnh màu khung, kéo thả sticker vào vị trí mong muốn.

> Khi click Export, frontend gửi toàn bộ thông tin đến API collage bao gồm: session ID, tên template, màu sắc, và danh sách decorations với vị trí.

> TemplateEngine load các ảnh trong session, resize và crop để fit vào slot của template, sau đó đặt lên canvas. Tiếp theo, render các sticker và decoration. Cuối cùng, save thành file PNG chất lượng cao và trả về URL để người dùng download."

---

## SLIDE 12: PHÂN CÔNG CÔNG VIỆC - TỔNG QUAN

**Tiêu đề:** Phân Công Công Việc Nhóm

**Nội dung hiển thị:**

| STT | Thành viên | Vai trò | Tỷ lệ |
|-----|------------|---------|-------|
| 1 | [Tên 1] | Backend Core & Database | 25% |
| 2 | [Tên 2] | Image Processing & Filters | 25% |
| 3 | [Tên 3] | AI/ML Features | 25% |
| 4 | [Tên 4] | Frontend & Collage System | 25% |

**Hình ảnh gợi ý:** Biểu đồ tròn chia 4 phần bằng nhau

**Lời dẫn:**
> "Dự án được phân chia công việc đều cho 4 thành viên, mỗi người đảm nhận 25% khối lượng công việc.

> Việc phân chia dựa trên chuyên môn và sở thích của từng thành viên, đồng thời đảm bảo các module có sự độc lập tương đối để có thể phát triển song song."

---

## SLIDE 13: PHÂN CÔNG CHI TIẾT - NGƯỜI 1 & 2

**Tiêu đề:** Chi Tiết Công Việc - Backend & Image Processing

**Nội dung hiển thị:**

**Người 1 - Backend Core:**
- Flask app factory, configuration
- Database models (5 models)
- Core APIs: /sessions, /capture, /upload
- Utilities: validators, helpers

**Người 2 - Image Processing:**
- 30+ image filters
- AI Beauty filters (face-aware)
- Image utilities
- APIs: /filters, /apply-filter

**Hình ảnh gợi ý:** Danh sách files mỗi người phụ trách

**Lời dẫn:**
> "Thành viên thứ nhất phụ trách Backend Core, bao gồm: thiết kế Flask application, quản lý configuration, xây dựng 5 database models là Session, Photo, User, FaceEmbedding và FilterApplied. Ngoài ra còn phát triển các API core như tạo session, capture ảnh, và các utility functions.

> Thành viên thứ hai phụ trách Image Processing, bao gồm: phát triển hơn 30 bộ lọc ảnh sử dụng OpenCV và Pillow. Đặc biệt là các filter AI Beauty có tích hợp face detection để chỉ xử lý vùng khuôn mặt. Các API liên quan đến filter cũng do thành viên này phụ trách."

---

## SLIDE 14: PHÂN CÔNG CHI TIẾT - NGƯỜI 3 & 4

**Tiêu đề:** Chi Tiết Công Việc - AI/ML & Frontend

**Nội dung hiển thị:**

**Người 3 - AI/ML Features:**
- DNN Face Detection
- FaceNet embedding
- Emotion/Age/Gender analysis
- Suggestion Engine
- APIs: /face-detect, /face-analyze, /recognize

**Người 4 - Frontend & Collage:**
- HTML templates (5 trang)
- JavaScript: capture.js, session.js, session_collage.js
- Template Engine (Pillow)
- APIs: /templates, /collage

**Hình ảnh gợi ý:** Screenshot các module

**Lời dẫn:**
> "Thành viên thứ ba phụ trách AI/ML, bao gồm: tích hợp mô hình DNN face detection, FaceNet để trích xuất embedding, phân tích cảm xúc, tuổi và giới tính. Thành viên này cũng xây dựng Suggestion Engine để gợi ý filter thông minh và các API liên quan đến AI.

> Thành viên thứ tư phụ trách Frontend và Collage System, bao gồm: thiết kế 5 trang HTML, phát triển JavaScript cho camera, filter selection và collage preview. Ở backend, thành viên này phát triển Template Engine để tạo collage và các API liên quan."

---

## SLIDE 15: THỐNG KÊ DỰ ÁN

**Tiêu đề:** Thống Kê Dự Án

**Nội dung hiển thị:**

| Metric | Số lượng |
|--------|----------|
| Files Python | 15+ |
| Dòng code Python | ~5,000 |
| Dòng code JavaScript | ~2,500 |
| API endpoints | 20+ |
| Image filters | 30+ |
| Database models | 5 |
| AI models | 4 |
| HTML templates | 5 |

**Hình ảnh gợi ý:** Biểu đồ cột hoặc infographic

**Lời dẫn:**
> "Về thống kê dự án, tổng cộng có hơn 15 files Python với khoảng 5000 dòng code, và khoảng 2500 dòng JavaScript.

> Hệ thống cung cấp hơn 20 API endpoints, hơn 30 bộ lọc ảnh, 5 database models, 4 AI models và 5 trang HTML.

> Dự án sử dụng tổng cộng 16 thư viện Python bao gồm Flask, Pillow, OpenCV, TensorFlow, MediaPipe, và các thư viện hỗ trợ khác."

---

## SLIDE 16: DEMO ỨNG DỤNG

**Tiêu đề:** Demo Ứng Dụng

**Nội dung hiển thị:**

**Các bước demo:**
1. Truy cập trang chủ
2. Bắt đầu session chụp ảnh
3. Chụp 4 ảnh với countdown
4. Chọn và áp dụng filter
5. Xem gợi ý AI
6. Tạo collage với template
7. Thêm sticker
8. Export và download

**Hình ảnh gợi ý:** Screenshots từng bước hoặc video demo

**Lời dẫn:**
> "Bây giờ em xin demo ứng dụng.

> [Demo trực tiếp hoặc video]

> Đầu tiên, truy cập trang chủ và click vào nút Bắt đầu chụp ảnh. Hệ thống sẽ xin quyền truy cập camera.

> Sau khi camera sẵn sàng, click Capture để chụp ảnh. Hệ thống sẽ đếm ngược 3-2-1 với hiệu ứng flash.

> Sau khi chụp đủ 4 ảnh, chuyển sang trang chọn filter. Có thể thử nhiều filter và so sánh before/after.

> Hệ thống AI sẽ phân tích khuôn mặt và đưa ra gợi ý filter phù hợp.

> Tiếp theo, chọn template collage, tùy chỉnh màu sắc và thêm sticker.

> Cuối cùng, click Export để tải ảnh về máy."

---

## SLIDE 17: KẾT LUẬN

**Tiêu đề:** Kết Luận

**Nội dung hiển thị:**

**Đã đạt được:**
- ✅ Ứng dụng photobooth hoàn chỉnh
- ✅ 30+ bộ lọc chuyên nghiệp
- ✅ Tích hợp AI face detection & analysis
- ✅ Hệ thống gợi ý thông minh
- ✅ Tạo collage với nhiều template

**Hạn chế:**
- Chưa hỗ trợ mobile native
- Cần kết nối internet
- Model AI cần GPU để tối ưu

**Lời dẫn:**
> "Tổng kết lại, dự án đã hoàn thành các mục tiêu đề ra: xây dựng ứng dụng photobooth hoàn chỉnh với hơn 30 bộ lọc, tích hợp AI để nhận diện và phân tích khuôn mặt, và hệ thống tạo collage linh hoạt.

> Tuy nhiên, dự án vẫn còn một số hạn chế như chưa có ứng dụng mobile native, cần kết nối internet để hoạt động, và các model AI cần GPU để đạt hiệu suất tối ưu."

---

## SLIDE 18: HƯỚNG PHÁT TRIỂN

**Tiêu đề:** Hướng Phát Triển Tương Lai

**Nội dung hiển thị:**

- 🔮 Mobile app (React Native / Flutter)
- 🔮 Real-time face filters (AR)
- 🔮 Video recording & GIF export
- 🔮 Cloud deployment (AWS/GCP)
- 🔮 Print integration (máy in ảnh)
- 🔮 Social sharing

**Hình ảnh gợi ý:** Roadmap hoặc icons các tính năng tương lai

**Lời dẫn:**
> "Về hướng phát triển tương lai, chúng em dự định:

> Thứ nhất, phát triển mobile app bằng React Native hoặc Flutter để người dùng có thể sử dụng trên điện thoại.

> Thứ hai, tích hợp real-time face filters dạng AR, giống như các filter trên Instagram hay TikTok.

> Thứ ba, thêm tính năng quay video và xuất GIF.

> Thứ tư, triển khai lên cloud để có thể scale và phục vụ nhiều người dùng đồng thời.

> Cuối cùng, tích hợp với máy in ảnh để có thể in trực tiếp tại sự kiện."

---

## SLIDE 19: CẢM ƠN & HỎI ĐÁP

**Tiêu đề:** Cảm Ơn Đã Lắng Nghe!

**Nội dung hiển thị:**

**Q&A - Hỏi Đáp**

**Thông tin liên hệ:**
- GitHub: [Link repository]
- Email: [Email nhóm]

**Team:**
- Người 1 - Backend Core
- Người 2 - Image Processing
- Người 3 - AI/ML
- Người 4 - Frontend/Collage

**Lời dẫn:**
> "Đó là toàn bộ nội dung thuyết trình của nhóm chúng em về dự án Photobooth Python Webapp.

> Cảm ơn thầy/cô và các bạn đã lắng nghe. Chúng em xin sẵn sàng trả lời các câu hỏi."

---

# 📝 GHI CHÚ CHO NGƯỜI THUYẾT TRÌNH

## Phân bổ thời gian (~15 phút)

| Phần | Slides | Thời gian |
|------|--------|-----------|
| Giới thiệu | 1-2 | 1 phút |
| Chức năng | 3-4 | 2 phút |
| Công nghệ | 5-6 | 2 phút |
| Kiến trúc | 7 | 1 phút |
| Luồng xử lý | 8-11 | 3 phút |
| Phân công | 12-14 | 2 phút |
| Thống kê | 15 | 1 phút |
| Demo | 16 | 2 phút |
| Kết luận | 17-19 | 1 phút |

## Tips thuyết trình

1. **Chuẩn bị demo:** Test trước camera và kết nối mạng
2. **Backup:** Có video demo dự phòng nếu live demo fail
3. **Phân chia:** Mỗi người trình bày phần mình phụ trách
4. **Tương tác:** Hỏi audience có câu hỏi gì sau mỗi phần lớn
5. **Thời gian:** Để đồng hồ theo dõi, không quá 15 phút

## Câu hỏi dự đoán & Trả lời

**Q: Tại sao chọn Flask thay vì Django?**
> A: Flask nhẹ hơn, linh hoạt hơn cho dự án này. Không cần các tính năng phức tạp của Django như admin panel hay ORM built-in.

**Q: Độ chính xác của face detection?**
> A: SSD MobileNet đạt ~95% accuracy trên các điều kiện ánh sáng tốt. Có thể điều chỉnh confidence threshold.

**Q: Có thể handle bao nhiêu requests đồng thời?**
> A: Với cấu hình hiện tại (single server), khoảng 10-20 concurrent users. Có thể scale với load balancer.

**Q: Tại sao dùng SQLite thay vì PostgreSQL/MySQL?**
> A: SQLite đủ cho prototype và small-scale deployment. Dễ setup, không cần server riêng. Có thể migrate sang PostgreSQL khi cần.

---

*Script thuyết trình cho Photobooth Python Webapp*
*Tháng 1/2026*
