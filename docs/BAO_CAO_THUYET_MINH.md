# BÁO CÁO ĐỒ ÁN MÔN LẬP TRÌNH PYTHON
# **Ứng Dụng Photobooth Web với Trí Tuệ Nhân Tạo**

---

## PHẦN 1: GIỚI THIỆU TỔNG QUAN

### 1.1. Đặt vấn đề

Trong thời đại công nghệ số hiện nay, nhu cầu chụp ảnh và chia sẻ hình ảnh trên mạng xã hội ngày càng tăng cao. Các quán café, sự kiện, tiệc cưới thường có những booth chụp ảnh để khách hàng có thể lưu giữ kỷ niệm. Tuy nhiên, việc thuê một booth chụp ảnh chuyên nghiệp thường tốn kém và không phải ai cũng có điều kiện tiếp cận.

Xuất phát từ nhu cầu thực tế đó, đồ án này hướng đến việc xây dựng một ứng dụng web cho phép người dùng có thể chụp ảnh photobooth ngay trên trình duyệt, với đầy đủ các tính năng như bộ lọc hình ảnh, tạo collage và thậm chí tích hợp trí tuệ nhân tạo để nhận diện khuôn mặt.

### 1.2. Mục tiêu đồ án

Đồ án đặt ra các mục tiêu cụ thể như sau:

**Thứ nhất**, xây dựng một ứng dụng web hoàn chỉnh sử dụng ngôn ngữ Python và framework Flask. Ứng dụng phải có khả năng chạy trên trình duyệt web, không yêu cầu người dùng cài đặt phần mềm bổ sung.

**Thứ hai**, tích hợp các thuật toán xử lý ảnh sử dụng thư viện OpenCV và Pillow để cung cấp hơn 15 bộ lọc hình ảnh chuyên nghiệp, từ các filter cơ bản như đen trắng, sepia cho đến các filter phức tạp như làm đẹp da bằng AI.

**Thứ ba**, ứng dụng Deep Learning để nhận diện khuôn mặt trong ảnh, từ đó có thể áp dụng các hiệu ứng thông minh chỉ lên vùng mặt hoặc gợi ý filter phù hợp với đặc điểm người dùng.

**Thứ tư**, thiết kế giao diện người dùng thân thiện, trực quan và responsive để có thể sử dụng trên nhiều thiết bị khác nhau.

### 1.3. Đối tượng sử dụng

Ứng dụng hướng đến ba nhóm đối tượng chính. Nhóm đầu tiên là các cá nhân muốn chụp ảnh photobooth tại nhà mà không cần đến các booth chuyên nghiệp. Nhóm thứ hai là các quán café, nhà hàng, sự kiện muốn có một giải pháp booth chụp ảnh với chi phí thấp. Nhóm cuối cùng là sinh viên và những người đang học tập, nghiên cứu về xử lý ảnh và trí tuệ nhân tạo.

---

## PHẦN 2: CÔNG NGHỆ SỬ DỤNG

### 2.1. Công nghệ Backend

**Flask Framework** là nền tảng chính của ứng dụng. Flask là một micro web framework được viết bằng Python, nổi tiếng với sự đơn giản và linh hoạt. Đồ án sử dụng Flask phiên bản 3.0.0, phiên bản mới nhất với nhiều cải tiến về hiệu suất và bảo mật. Flask được chọn vì tính nhẹ nhàng, dễ học và có hệ sinh thái extension phong phú.

**Flask-SQLAlchemy** phiên bản 3.1.1 được sử dụng làm ORM (Object-Relational Mapping) để tương tác với cơ sở dữ liệu. Thay vì viết các câu lệnh SQL thuần túy, SQLAlchemy cho phép làm việc với database thông qua các đối tượng Python, giúp code dễ đọc và bảo trì hơn.

**OpenCV** phiên bản 4.8.1 là thư viện xử lý ảnh hàng đầu, được sử dụng cho các tác vụ phức tạp như nhận diện khuôn mặt bằng Deep Neural Network, áp dụng các bộ lọc nghệ thuật và xử lý ảnh theo thời gian thực. OpenCV cung cấp module DNN cho phép chạy các mô hình deep learning mà không cần cài đặt framework nặng như PyTorch.

**Pillow** phiên bản 10.1.0 là thư viện xử lý ảnh cơ bản của Python, được sử dụng cho các tác vụ như đọc/ghi file ảnh, resize, crop, điều chỉnh độ sáng và tương phản. Pillow hoạt động tốt kết hợp với OpenCV để tạo ra pipeline xử lý ảnh hoàn chỉnh.

**NumPy** phiên bản 1.24.3 là thư viện tính toán khoa học, đóng vai trò nền tảng cho mọi thao tác xử lý ảnh. Trong xử lý ảnh, mỗi hình ảnh được biểu diễn dưới dạng mảng NumPy đa chiều, và các phép biến đổi được thực hiện thông qua các phép toán ma trận.

**TensorFlow** phiên bản 2.15.0 được sử dụng cho các tính năng AI nâng cao như trích xuất face embedding bằng mô hình FaceNet. TensorFlow là framework deep learning phổ biến của Google, cung cấp khả năng chạy các mô hình neural network phức tạp.

**MediaPipe** phiên bản 0.10.8 là thư viện của Google chuyên về computer vision, được sử dụng để detect 468 điểm landmark trên khuôn mặt. Thông tin này hữu ích cho việc đặt sticker chính xác lên mắt, mũi, miệng hoặc áp dụng makeup ảo.

**Annoy** phiên bản 1.17.2 là thư viện Approximate Nearest Neighbor của Spotify, được sử dụng để tìm kiếm nhanh các face embedding tương tự trong database. Khi có hàng nghìn khuôn mặt đã lưu, Annoy giúp tìm kiếm trong thời gian O(log n) thay vì O(n).

### 2.2. Công nghệ Frontend

**HTML5** được sử dụng để xây dựng cấu trúc các trang web. Đồ án tận dụng các tính năng mới của HTML5 như Canvas API để capture hình ảnh từ video stream và các semantic elements để cải thiện SEO và accessibility.

**CSS3** được sử dụng để thiết kế giao diện với các kỹ thuật hiện đại như Flexbox, Grid Layout, CSS Variables và animations. Giao diện được thiết kế theo phong cách responsive để hiển thị tốt trên mọi kích thước màn hình.

**JavaScript ES6+** là ngôn ngữ lập trình phía client, xử lý toàn bộ logic tương tác người dùng. Đồ án sử dụng các tính năng modern JavaScript như async/await, classes, arrow functions và modules. JavaScript đảm nhận việc truy cập webcam thông qua WebRTC API, gửi request đến server và cập nhật giao diện động.

**WebRTC** (Web Real-Time Communication) là công nghệ cho phép truy cập camera và microphone trực tiếp từ trình duyệt. Thông qua API getUserMedia(), ứng dụng có thể stream video từ webcam của người dùng mà không cần plugin hay phần mềm bổ sung.

### 2.3. Cơ sở dữ liệu

Đồ án sử dụng **SQLite** làm hệ quản trị cơ sở dữ liệu. SQLite được chọn vì tính đơn giản, không cần cài đặt server riêng và phù hợp với ứng dụng vừa và nhỏ. Database được lưu dưới dạng một file duy nhất, dễ dàng backup và di chuyển. Trong môi trường production, có thể dễ dàng chuyển sang PostgreSQL hoặc MySQL mà không cần thay đổi code nhờ SQLAlchemy ORM.

---

## PHẦN 3: KIẾN TRÚC HỆ THỐNG

### 3.1. Mô hình MVC

Ứng dụng được xây dựng theo mô hình MVC (Model-View-Controller), một design pattern phổ biến trong phát triển web giúp tách biệt các thành phần của ứng dụng.

**Model** là tầng dữ liệu, chứa các class đại diện cho các bảng trong database và business logic. Trong đồ án, các model được định nghĩa trong thư mục models bao gồm Session, Photo, User và FaceEmbedding. Ngoài ra, các engine xử lý như ImageProcessor, FilterEngine, FaceDetector cũng thuộc tầng Model.

**View** là tầng giao diện, chịu trách nhiệm hiển thị dữ liệu cho người dùng. Đồ án sử dụng Jinja2 template engine tích hợp sẵn trong Flask để render các trang HTML. Các template được lưu trong thư mục templates với file base.html làm layout chung và các file như index.html, capture.html, session.html cho từng trang cụ thể.

**Controller** là tầng điều khiển, xử lý request từ người dùng và điều phối giữa Model và View. Trong Flask, controller được triển khai thông qua các route functions. Đồ án tổ chức routes thành hai Blueprint: api_bp cho các RESTful API endpoints và views_bp cho các trang HTML.

### 3.2. Design Patterns sử dụng

**Singleton Pattern** được áp dụng cho class FaceDetector. Do việc load model DNN tốn thời gian và bộ nhớ, pattern này đảm bảo model chỉ được load một lần duy nhất và được tái sử dụng cho tất cả các request. Cách triển khai là override phương thức __new__ để kiểm tra và trả về instance đã tồn tại.

**Factory Pattern** được sử dụng trong hàm create_app() để tạo Flask application. Pattern này cho phép tạo app với các configuration khác nhau như development, production hay testing mà không cần thay đổi code.

**Blueprint Pattern** là cách Flask tổ chức code thành các module độc lập. Mỗi blueprint có thể có routes, templates và static files riêng. Đồ án có hai blueprints: api_bp được mount tại /api/ xử lý tất cả API requests, views_bp được mount tại root / phục vụ các trang HTML.

**Strategy Pattern** được thể hiện trong FilterEngine. Mỗi filter là một strategy riêng với cùng interface là nhận vào một image và trả về image đã được xử lý. Điều này cho phép dễ dàng thêm filter mới mà không ảnh hưởng đến code hiện có.

### 3.3. Luồng dữ liệu

Khi người dùng truy cập ứng dụng, request đầu tiên đến Flask server. Server kiểm tra URL và dispatch đến route function tương ứng thông qua URL routing của Flask. Route function có thể truy vấn database thông qua SQLAlchemy models, gọi các processing functions và cuối cùng trả về response.

Với các trang HTML, response là một rendered template. Với các API endpoints, response là JSON data. Dữ liệu ảnh được lưu trữ trên filesystem trong thư mục static/uploads với cấu trúc phân chia thành originals, processed, thumbnails và collages.

---

## PHẦN 4: CÁC CHỨC NĂNG CHÍNH

### 4.1. Chức năng chụp ảnh Photobooth

Đây là chức năng cốt lõi của ứng dụng, cho phép người dùng chụp một phiên 4 ảnh giống như booth chụp ảnh truyền thống.

Khi người dùng vào trang capture, ứng dụng sẽ yêu cầu quyền truy cập webcam thông qua WebRTC API. Nếu người dùng cho phép, video stream từ camera sẽ được hiển thị trên màn hình. Video được mirror (lật ngang) để người dùng thấy mình như đang soi gương, tạo cảm giác tự nhiên khi chụp.

Khi nhấn nút chụp, ứng dụng sẽ hiển thị đếm ngược 3 giây để người dùng chuẩn bị. Sau đó, frame hiện tại từ video được capture vào HTML5 Canvas và hiệu ứng flash trắng được hiển thị để mô phỏng đèn flash thật. Hình ảnh sau đó được chuyển thành blob và gửi lên server.

Server nhận ảnh, xử lý (flip lại cho đúng chiều) và lưu thành 3 phiên bản: ảnh gốc trong thư mục originals, ảnh đã xử lý trong processed và ảnh thumbnail nhỏ trong thumbnails. Thông tin ảnh được lưu vào database và URL được trả về cho client để hiển thị preview.

Người dùng có thể xem preview và quyết định giữ ảnh hoặc chụp lại. Quy trình lặp lại cho đến khi đủ 4 ảnh thì chuyển sang bước chọn filter.

### 4.2. Chức năng bộ lọc hình ảnh

Ứng dụng cung cấp hơn 15 bộ lọc hình ảnh được chia thành nhiều danh mục khác nhau.

**Nhóm Basic** bao gồm các filter cơ bản như none (giữ nguyên), grayscale (đen trắng), sepia (màu nâu cổ điển), brightness (tăng độ sáng) và contrast (tăng độ tương phản). Đây là những filter đơn giản, xử lý nhanh và phù hợp với mọi loại ảnh.

**Nhóm Photobooth** là các filter được thiết kế đặc biệt cho ảnh chân dung. Filter soft_skin làm mịn da bằng bilateral filter. Filter pastel_glow tạo hiệu ứng ánh sáng nhẹ nhàng với tông màu pastel. Filter sakura thêm các cánh hoa anh đào rơi. Filter sparkle thêm các điểm lấp lánh. Filter rainbow_leak tạo hiệu ứng ánh sáng cầu vồng. Filter heart_bokeh thêm các hình trái tim mờ ảo. Filter polaroid tạo hiệu ứng ảnh Polaroid cổ điển.

**Nhóm Artistic** gồm các filter nghệ thuật. Filter cartoon chuyển ảnh thành phong cách hoạt hình bằng cách detect edges và giảm số màu. Filter pencil_sketch tạo hiệu ứng vẽ chì. Filter oil_painting mô phỏng tranh sơn dầu. Filter comic_pastel kết hợp phong cách comic với tông màu pastel.

**Nhóm Instagram** mô phỏng các filter nổi tiếng trên Instagram. Filter nashville tạo tông màu ấm với ánh tím nhẹ. Filter valencia tăng exposure và giảm saturation. Filter xpro2 tạo vignette mạnh với tông màu ấm ở giữa và lạnh ở viền. Filter walden tăng exposure và thêm tông vàng. Filter kelvin tăng saturation và độ ấm.

**Nhóm AI Beauty** là các filter thông minh sử dụng face detection. Filter smart_beauty chỉ làm mịn vùng da mặt, giữ nguyên background và các chi tiết khác. Filter face_glow thêm hiệu ứng phát sáng từ tâm khuôn mặt. Filter portrait_pro kết hợp nhiều kỹ thuật làm đẹp chuyên nghiệp.

Người dùng có thể preview filter trước khi apply. Khi chọn một filter, server sẽ xử lý một phiên bản preview nhỏ để hiển thị nhanh. Khi confirm, server xử lý tất cả 4 ảnh với filter đã chọn.

### 4.3. Chức năng tạo Collage

Sau khi chọn filter, người dùng có thể tạo collage từ 4 ảnh đã chụp với nhiều template khác nhau.

Template **1x4** sắp xếp 4 ảnh theo chiều dọc tạo thành dải ảnh strip giống photo booth truyền thống. Đây là layout phổ biến nhất cho photobooth.

Template **2x2** sắp xếp 4 ảnh thành lưới 2 hàng 2 cột, tạo bố cục cân đối và hiện đại.

Template **classic_strip** tương tự 1x4 nhưng có thêm viền đen và kích thước lớn hơn, phù hợp để in ra giấy.

Template **grid_modern** là phiên bản hiện đại của 2x2 với khoảng cách giữa các ảnh nhỏ hơn và không có viền.

Template **pastel_pink** có nền màu hồng pastel với góc bo tròn cho các ảnh, tạo cảm giác dễ thương và nữ tính.

Ngoài ra, người dùng có thể thêm stickers và decorations vào collage. Các sticker được đặt tại các anchor points đã được tính toán sẵn để không che mất ảnh quan trọng. Hệ thống hỗ trợ cả file PNG và SVG cho stickers.

### 4.4. Tính năng trí tuệ nhân tạo

**Face Detection** là tính năng nền tảng, sử dụng mô hình SSD (Single Shot MultiBox Detector) với backbone ResNet-10. Model này được train đặc biệt cho việc detect khuôn mặt với độ chính xác khoảng 95% cho frontal faces. Mô hình được load một lần duy nhất khi khởi động và được tái sử dụng cho tất cả requests nhờ Singleton pattern.

**Face Recognition** cho phép nhận diện người dùng quay lại. Khi người dùng đồng ý lưu khuôn mặt, hệ thống sử dụng FaceNet để trích xuất vector embedding 128 chiều đại diện cho khuôn mặt đó. Vector này được lưu vào database. Lần sau khi người dùng chụp ảnh, hệ thống so sánh embedding mới với các embedding đã lưu để nhận diện.

**Emotion Detection** phân tích biểu cảm khuôn mặt và phân loại thành 7 cảm xúc: vui, buồn, ngạc nhiên, giận dữ, sợ hãi, ghê tởm và trung tính. Thông tin này được sử dụng để gợi ý filter phù hợp với tâm trạng người dùng.

**Smart Suggestions** là engine gợi ý kết hợp nhiều yếu tố. Dựa trên cảm xúc phát hiện được, tuổi và giới tính ước tính, hệ thống sẽ đề xuất các filter và template phù hợp nhất. Ví dụ, nếu phát hiện người dùng đang vui, hệ thống sẽ gợi ý các filter tươi sáng như sparkle hay sakura.

---

## PHẦN 5: CẤU TRÚC THƯ MỤC VÀ TỔ CHỨC CODE

### 5.1. Thư mục gốc

File **app.py** là điểm khởi đầu của ứng dụng, chứa hàm create_app() theo Application Factory pattern. Hàm này khởi tạo Flask app, cấu hình database, đăng ký blueprints và tạo các thư mục cần thiết.

File **config.py** chứa các class configuration cho các môi trường khác nhau. Class Config là base class với các cấu hình chung. DevelopmentConfig enable debug mode. ProductionConfig tắt debug và tăng cường bảo mật.

File **requirements.txt** liệt kê tất cả dependencies của project với version cụ thể để đảm bảo reproducibility.

### 5.2. Thư mục models

Đây là nơi chứa toàn bộ business logic của ứng dụng.

File **database.py** định nghĩa các SQLAlchemy models. Class Session đại diện cho một phiên chụp ảnh với ID là UUID. Class Photo đại diện cho một ảnh đơn lẻ, liên kết với Session. Class User lưu thông tin người dùng cho face recognition. Class FaceEmbedding lưu vector embedding của khuôn mặt.

File **image_processor.py** chứa class ImageProcessor với các static methods cho xử lý ảnh cơ bản như flip_horizontal, save_image, create_thumbnail và process_uploaded_image.

File **filter_engine.py** chứa class FilterEngine với hơn 15 private methods, mỗi method implement một filter cụ thể. Method apply_filter là entry point, nhận tên filter và dispatch đến method tương ứng.

File **face_detector.py** chứa class FaceDetector với Singleton pattern. Class này load model DNN một lần và cung cấp các methods như detect_faces, detect_largest_face, auto_crop_portrait và get_face_mask.

File **template_engine.py** chứa class TemplateEngine xử lý việc tạo collage. Class này có dictionary TEMPLATES định nghĩa các template với size, positions và style. Method create_collage nhận danh sách ảnh và tên template, trả về path đến collage đã tạo.

File **model_manager.py** là wrapper quản lý các DNN models. Class này implement lazy loading để chỉ load model khi cần, tiết kiệm bộ nhớ. Các models bao gồm FaceNet cho embedding, emotion detection model và age/gender estimation model.

File **suggestion_engine.py** chứa class SuggestionEngine với các mapping từ đặc điểm người dùng đến filter/template phù hợp. Methods suggest_filters và suggest_templates trả về danh sách gợi ý với điểm số và lý do.

File **embedding_index.py** chứa class EmbeddingIndex wrap thư viện Annoy. Class này quản lý việc build index, save/load index và search nearest neighbors.

### 5.3. Thư mục routes

File **api.py** định nghĩa Blueprint api_bp với tất cả RESTful API endpoints. Các endpoints chính bao gồm POST /sessions để tạo session mới, POST /capture để upload ảnh, GET /filters để lấy danh sách filter, POST /apply-filter để áp dụng filter và POST /create-collage để tạo collage.

File **views.py** định nghĩa Blueprint views_bp với các routes render HTML pages. Route / render trang chủ, /capture render trang chụp ảnh, /session/<id> render trang chọn filter và /gallery render trang thư viện ảnh.

### 5.4. Thư mục templates

Các file HTML sử dụng Jinja2 template syntax. File **base.html** là layout chung với header, footer và các blocks để child templates override. File **index.html** là landing page với giới thiệu và hướng dẫn sử dụng. File **capture.html** chứa video element và các controls cho việc chụp ảnh. File **session.html** hiển thị grid ảnh và danh sách filter cards.

### 5.5. Thư mục static

Thư mục **css** chứa file style.css với toàn bộ CSS của ứng dụng, được tổ chức theo component-based approach.

Thư mục **js** chứa các JavaScript files. File capture.js chứa class PhotoCapture xử lý camera access và capture logic. File session.js chứa class FilterSelectionPage xử lý filter preview và apply.

Thư mục **uploads** chứa các ảnh user upload, được chia thành originals, processed, thumbnails và collages.

Thư mục **templates** (trong static, khác với templates ở root) chứa assets cho collage như stickers, decorations và file templates.json định nghĩa metadata.

---

## PHẦN 6: LUỒNG XỬ LÝ CHI TIẾT

### 6.1. Luồng tạo session và chụp ảnh

Khi người dùng truy cập trang chủ và nhấn "Bắt đầu phiên chụp", trình duyệt sẽ chuyển đến trang capture. JavaScript trong trang này ngay lập tức gọi navigator.mediaDevices.getUserMedia() để yêu cầu quyền truy cập camera. Nếu người dùng cho phép, video stream được gán vào element video và bắt đầu hiển thị.

Khi người dùng nhấn nút chụp lần đầu tiên, JavaScript gửi request POST đến /api/sessions để tạo session mới. Server tạo một UUID mới, lưu vào database với status là "capturing" và trả về session_id. Client lưu session_id này để sử dụng cho các request tiếp theo.

Tiếp theo là quá trình capture từng ảnh. JavaScript hiển thị countdown overlay với số đếm từ 3 xuống 1. Sau khi đếm xong, canvas.drawImage(video, 0, 0) được gọi để capture frame hiện tại vào canvas. Hiệu ứng flash được trigger bằng cách thêm class CSS tạo animation trắng rồi fade out.

Canvas được convert thành blob bằng canvas.toBlob() và đóng gói vào FormData cùng với session_id và photo_number. Request POST được gửi đến /api/capture. Server nhận file, đọc vào PIL Image, xử lý (convert RGB, flip horizontal) và lưu thành 3 files. Thông tin được insert vào bảng photos với foreign key đến session.

Server trả về JSON chứa các URLs của ảnh. Client nhận response và hiển thị preview modal cho người dùng. Nếu người dùng nhấn confirm, photo được giữ lại và chuyển sang chụp ảnh tiếp theo. Nếu nhấn retake, ảnh bị xóa và cho phép chụp lại.

Sau khi đủ 4 ảnh, session status được cập nhật thành "filtering" và client redirect đến trang /session/<session_id>.

### 6.2. Luồng chọn và áp dụng filter

Trang session load lên với session_id từ URL. JavaScript gọi hai API song song: GET /api/sessions/<id>/photos để lấy danh sách ảnh đã chụp và GET /api/filters để lấy danh sách filter có sẵn.

Ảnh được hiển thị trong grid 2x2 hoặc list tùy layout. Filter cards được render với thumbnail preview, tên và mô tả. Khi người dùng click vào một filter card, JavaScript thực hiện preview bằng cách gửi request POST /api/sessions/<id>/preview-filter với filter_name.

Server nhận request, load ảnh đầu tiên của session và áp dụng filter bằng FilterEngine.apply_filter(). Ảnh preview được lưu vào thư mục tạm và URL được trả về. Client hiển thị ảnh preview để người dùng xem trước hiệu ứng.

Để tối ưu performance, client cache các preview đã fetch. Khi người dùng chọn lại filter đã preview trước đó, ảnh được lấy từ cache thay vì gọi API lại.

Khi người dùng confirm filter selection, JavaScript gửi POST /api/sessions/<id>/apply-filter. Server lấy tất cả 4 ảnh của session, áp dụng filter cho từng ảnh, lưu phiên bản mới vào processed folder và cập nhật database với tên filter đã apply.

### 6.3. Luồng tạo collage

Sau khi apply filter, người dùng chuyển sang bước tạo collage. Giao diện hiển thị các template options với preview. Người dùng chọn template và optionally thêm stickers.

Khi submit, JavaScript gửi POST /api/sessions/<id>/create-collage với template_name, sticker_paths và các options khác. Server thực hiện các bước sau:

Đầu tiên, TemplateEngine được khởi tạo và lấy template config từ dictionary TEMPLATES. Config chứa thông tin về size canvas, positions cho từng ảnh, photo_size và style.

Tiếp theo, server tạo canvas mới với size từ template và fill background color. Sau đó loop qua 4 ảnh, mỗi ảnh được resize và crop để fit vào photo_size sử dụng method _resize_and_crop. Ảnh sau đó được paste vào canvas tại position tương ứng.

Nếu có stickers, server load từng sticker image, apply random rotation và scale, rồi paste vào các anchor points đã định nghĩa trong template.

Cuối cùng, canvas được save thành file PNG trong thư mục collages với tên unique. URL được trả về cho client để display và download.

---

## PHẦN 7: CÁC THUẬT TOÁN QUAN TRỌNG

### 7.1. Face Detection với OpenCV DNN

Thuật toán nhận diện khuôn mặt sử dụng kiến trúc SSD (Single Shot MultiBox Detector) với backbone ResNet-10. Đây là một mạng neural network đã được huấn luyện sẵn trên dataset khuôn mặt.

Quá trình xử lý bắt đầu với preprocessing. Ảnh input có thể có kích thước bất kỳ được resize về 300x300 pixels, là kích thước input của model. Sau đó thực hiện mean subtraction với giá trị (104, 177, 123) theo format BGR. Bước này chuẩn hóa input theo cách model đã được train.

Tiếp theo là forward pass qua mạng neural. Input đi qua các convolutional layers của ResNet-10 để extract features. Các SSD detection layers sau đó dự đoán bounding boxes và confidence scores tại nhiều scales khác nhau.

Output của mạng là tensor có shape (1, 1, N, 7) trong đó N là số detections. Mỗi detection gồm 7 giá trị: batch_id, class_id, confidence, và 4 tọa độ bounding box đã normalize về [0,1].

Post-processing bao gồm lọc các detections có confidence dưới threshold (thường là 0.5), scale tọa độ về kích thước ảnh gốc, và áp dụng non-maximum suppression nếu cần để loại bỏ overlapping boxes.

So với YOLO, SSD với ResNet-10 có ưu điểm là model nhẹ hơn nhiều (10MB vs 100MB+), chạy nhanh hơn trên CPU, và độ chính xác cao hơn cho frontal faces. Điều này phù hợp với use case photobooth khi người dùng thường nhìn thẳng vào camera.

### 7.2. Bilateral Filter cho làm mịn da

Bilateral filter là thuật toán lọc ảnh đặc biệt có khả năng làm mịn vùng đồng màu (như da) trong khi vẫn giữ sharp các cạnh (như mắt, mũi, miệng).

Filter hoạt động bằng cách với mỗi pixel, tính weighted average của các pixels lân cận. Trọng số được tính dựa trên hai yếu tố: khoảng cách không gian (spatial) và độ khác biệt màu sắc (range).

Spatial weight giảm dần theo khoảng cách từ pixel trung tâm, giống như Gaussian blur thông thường. Range weight giảm dần khi màu sắc của pixel lân cận khác biệt nhiều so với pixel trung tâm.

Kết quả là những pixels có màu tương tự (trên cùng vùng da) sẽ được blend mạnh với nhau tạo hiệu ứng mịn. Những pixels ở edge (như ranh giới giữa da và mắt) có màu khác biệt nên weight thấp, giữ được độ sharp.

Trong code, bilateral filter được gọi với cv2.bilateralFilter(image, d=9, sigmaColor=85, sigmaSpace=85). Tham số d là diameter của neighborhood. sigmaColor và sigmaSpace điều chỉnh độ mạnh của range và spatial filtering.

### 7.3. Face Embedding với FaceNet

FaceNet là mạng neural network chuyển khuôn mặt thành vector 128 chiều gọi là embedding. Hai khuôn mặt của cùng một người sẽ có embeddings gần nhau trong không gian 128 chiều, trong khi hai người khác nhau sẽ có embeddings xa nhau.

Preprocessing cho FaceNet bao gồm crop vùng mặt từ ảnh gốc, resize về 160x160 pixels, và normalize pixel values từ [0,255] về [-1,1].

Forward pass qua mạng FaceNet trả về vector 128 số thực. Vector này được L2 normalize để có độ dài bằng 1, giúp việc so sánh ổn định hơn.

So sánh hai embeddings bằng Euclidean distance. Nếu distance nhỏ hơn threshold (thường là 0.6), hai khuôn mặt được coi là cùng một người. Distance lớn hơn 1.0 chắc chắn là hai người khác nhau.

### 7.4. Approximate Nearest Neighbor với Annoy

Khi database có nhiều face embeddings, việc so sánh brute-force O(n) với mỗi query trở nên chậm. Annoy (Approximate Nearest Neighbors Oh Yeah) giải quyết vấn đề này bằng cách build một index structure.

Annoy chia không gian vector thành các vùng nhỏ bằng cách lặp lại việc chọn hai points ngẫu nhiên và vẽ hyperplane chia đôi giữa chúng. Kết quả là một cây nhị phân (binary tree) với mỗi leaf chứa một số ít vectors.

Khi search, Annoy traverse tree từ root, tại mỗi node chọn child dựa trên query vector nằm bên nào của hyperplane. Điều này cho phép tìm approximate nearest neighbors trong O(log n).

Để tăng accuracy, Annoy build nhiều trees (thường là 10) và merge kết quả từ tất cả trees. Có thể tune số trees và số candidates để balance giữa speed và accuracy.

---

## PHẦN 8: CƠ SỞ DỮ LIỆU

### 8.1. Thiết kế schema

Database gồm 5 bảng chính với các quan hệ rõ ràng.

Bảng **sessions** lưu thông tin về mỗi phiên chụp ảnh. Primary key là id kiểu UUID string, đảm bảo uniqueness mà không cần auto-increment. Các cột khác bao gồm created_at (thời điểm tạo), completed_at (thời điểm hoàn thành), và status với các giá trị có thể là capturing, filtering, hoặc completed.

Bảng **photos** lưu thông tin từng ảnh đơn lẻ. Primary key là id integer auto-increment. Foreign key session_id liên kết đến bảng sessions với relationship one-to-many (một session có nhiều photos). Cột photo_number từ 1-4 xác định thứ tự ảnh trong session. Các cột filename lưu tên file cho original, processed và thumbnail versions.

Bảng **filters_applied** track lịch sử áp dụng filter cho mỗi session. Điều này hữu ích cho analytics và cho phép undo nếu cần. Foreign key session_id liên kết đến sessions.

Bảng **users** lưu thông tin người dùng cho tính năng face recognition. Cột label là identifier unique cho mỗi user. Các cột metadata như age_range, gender được populate từ AI analysis.

Bảng **face_embeddings** lưu các vector embedding của khuôn mặt. Foreign key user_id liên kết đến users với relationship one-to-many (một user có thể có nhiều embeddings từ nhiều góc chụp khác nhau). Cột embedding_vector là LargeBinary chứa serialized numpy array.

### 8.2. ORM với SQLAlchemy

SQLAlchemy cho phép định nghĩa schema bằng Python classes. Mỗi class kế thừa db.Model và định nghĩa các columns bằng db.Column(). Relationships được định nghĩa bằng db.relationship() với backref để tạo reverse relationship.

Các methods to_dict() trong mỗi model convert object thành dictionary, tiện cho việc trả về JSON response từ API.

Migrations và schema changes có thể được quản lý bằng Flask-Migrate (Alembic wrapper), tuy nhiên trong đồ án này sử dụng db.create_all() đơn giản để tạo tables.

---

## PHẦN 9: API DOCUMENTATION

### 9.1. Sessions API

**POST /api/sessions** tạo session mới. Không cần request body. Response trả về session_id dạng UUID và success message.

**GET /api/sessions/{session_id}/photos** lấy danh sách ảnh trong session. Response chứa array photos với mỗi item gồm id, photo_number, và các URLs cho original, processed, thumbnail.

### 9.2. Photos API

**POST /api/capture** upload ảnh mới. Request body là multipart/form-data với image file, session_id và photo_number. Response trả về photo_id và các URLs.

**GET /api/images/{folder}/{filename}** serve ảnh từ filesystem. Folder có thể là originals, processed, thumbnails hoặc collages.

### 9.3. Filters API

**GET /api/filters** lấy danh sách tất cả filters. Response chứa array với mỗi filter gồm name, display_name, category, description và example_thumbnail URL.

**POST /api/sessions/{session_id}/preview-filter** preview filter trên một ảnh. Request body chứa filter_name. Response trả về URL của ảnh preview.

**POST /api/sessions/{session_id}/apply-filter** áp dụng filter cho tất cả ảnh trong session. Request body chứa filter_name. Response trả về danh sách URLs mới của các ảnh đã filter.

### 9.4. Collage API

**POST /api/sessions/{session_id}/create-collage** tạo collage từ 4 ảnh. Request body chứa template_name và optional sticker_paths. Response trả về URL của collage đã tạo.

---

## PHẦN 10: KẾT LUẬN

### 10.1. Kết quả đạt được

Đồ án đã hoàn thành việc xây dựng một ứng dụng web photobooth đầy đủ chức năng. Người dùng có thể chụp ảnh trực tiếp từ trình duyệt, chọn từ hơn 15 bộ lọc chuyên nghiệp, tạo collage với nhiều template và tải về máy.

Tính năng AI được tích hợp thành công với face detection đạt độ chính xác khoảng 95%. Các filter làm đẹp thông minh chỉ tác động lên vùng mặt tạo kết quả tự nhiên hơn các filter toàn ảnh.

Kiến trúc code được tổ chức tốt theo MVC pattern với clear separation of concerns. API được thiết kế RESTful, dễ dàng mở rộng và tích hợp với các ứng dụng khác.

### 10.2. Kiến thức Python đã áp dụng

Đồ án đã vận dụng nhiều kiến thức Python quan trọng. Lập trình hướng đối tượng được thể hiện qua các classes như ImageProcessor, FilterEngine, FaceDetector với proper encapsulation và inheritance.

Các design patterns như Singleton, Factory, Strategy được áp dụng đúng context. Flask framework với blueprints, templates, và extension ecosystem được sử dụng hiệu quả.

Xử lý ảnh với NumPy arrays, OpenCV và Pillow cho thấy khả năng làm việc với data structures phức tạp. Integration với TensorFlow cho deep learning models mở rộng kiến thức sang lĩnh vực AI/ML.

### 10.3. Hướng phát triển

Trong tương lai, ứng dụng có thể được mở rộng với real-time filter preview trên video stream trước khi chụp. Deployment lên cloud với Docker containers và CI/CD pipeline sẽ giúp ứng dụng production-ready.

Phát triển mobile app với React Native tận dụng lại backend API sẽ mở rộng đối tượng người dùng. Tích hợp social sharing và payment gateway cho premium filters là các hướng monetization khả thi.

---

**Sinh viên thực hiện:** [Họ và tên]  
**Mã số sinh viên:** [MSSV]  
**Lớp:** [Tên lớp]  
**Giảng viên hướng dẫn:** [Họ và tên GV]  
**Môn học:** Lập trình Python  
**Năm học:** 2025-2026
