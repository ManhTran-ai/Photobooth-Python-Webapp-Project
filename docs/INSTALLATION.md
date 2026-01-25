# 📦 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY PHOTOBOOTH WEBAPP

## 📋 Mục Lục
1. [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
2. [Cài đặt Python](#-cài-đặt-python)
3. [Clone Repository](#-clone-repository)
4. [Tạo Virtual Environment](#-tạo-virtual-environment)
5. [Cài đặt thư viện](#-cài-đặt-thư-viện)
6. [Chạy ứng dụng](#-chạy-ứng-dụng)
7. [Truy cập ứng dụng](#-truy-cập-ứng-dụng)
8. [Xử lý lỗi thường gặp](#-xử-lý-lỗi-thường-gặp)

---

## 💻 Yêu cầu hệ thống

| Yêu cầu | Chi tiết |
|---------|----------|
| **Hệ điều hành** | Windows 10/11, macOS, Linux |
| **Python** | 3.10 hoặc 3.11 (khuyến nghị 3.11) |
| **RAM** | Tối thiểu 4GB, khuyến nghị 8GB |
| **Disk** | Tối thiểu 2GB trống |
| **Webcam** | Có webcam để sử dụng chức năng chụp ảnh |

---

## 🐍 Cài đặt Python

### Windows

1. Tải Python từ [python.org](https://www.python.org/downloads/)
2. Chọn phiên bản **Python 3.11.x**
3. Khi cài đặt, **✅ QUAN TRỌNG**: Tick chọn "Add Python to PATH"
4. Click "Install Now"

Kiểm tra cài đặt thành công:
```powershell
python --version
# Output: Python 3.11.x
```

### macOS

```bash
# Sử dụng Homebrew
brew install python@3.11

# Kiểm tra
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Kiểm tra
python3.11 --version
```

---

## 📥 Clone Repository

### Cách 1: Sử dụng Git

```bash
# Clone repository
git clone https://github.com/ManhTran-ai/Photobooth-Python-Webapp-Project.git

# Di chuyển vào thư mục project
cd Photobooth-Python-Webapp-Project
```

### Cách 2: Tải ZIP

1. Vào trang GitHub repository
2. Click nút **Code** → **Download ZIP**
3. Giải nén file ZIP
4. Mở terminal/cmd và di chuyển vào thư mục đã giải nén

---

## 🔧 Tạo Virtual Environment

Virtual environment giúp cách ly các thư viện của project, tránh xung đột với các project khác.

### Windows (PowerShell hoặc CMD)

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# PowerShell:
.\venv\Scripts\Activate.ps1

# Hoặc CMD:
.\venv\Scripts\activate.bat
```

**Lưu ý**: Nếu gặp lỗi "execution policy" trên PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS / Linux

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate
```

✅ Khi kích hoạt thành công, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

---

## 📚 Cài đặt thư viện

Sau khi đã kích hoạt virtual environment:

```bash
# Cài đặt tất cả thư viện từ requirements.txt
pip install -r requirements.txt
```

### ⏱️ Thời gian cài đặt

Quá trình cài đặt có thể mất **5-15 phút** tùy thuộc vào tốc độ mạng, do các thư viện AI/ML khá nặng (TensorFlow ~500MB).

### Cài đặt từng bước (nếu gặp lỗi)

Nếu gặp lỗi khi cài đặt toàn bộ, thử cài từng phần:

```bash
# 1. Core Framework
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SQLAlchemy==3.1.1

# 2. Image Processing
pip install Pillow==10.1.0 opencv-python==4.8.1.78 numpy==1.24.3

# 3. Machine Learning (có thể bỏ qua nếu không cần AI features)
pip install tensorflow==2.15.0
pip install annoy==1.17.2
pip install mediapipe==0.10.8
pip install rembg==2.0.50

# 4. Utilities
pip install python-dotenv==1.0.0 qrcode==7.4.2
```

---

## 🚀 Chạy ứng dụng

### Bước 1: Đảm bảo virtual environment đã được kích hoạt

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### Bước 2: Chạy ứng dụng

```bash
python app.py
```

### Output thành công

```
TensorFlow not available - DNN features will use fallback methods
Database initialized successfully!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

---

## 🌐 Truy cập ứng dụng

Mở trình duyệt web và truy cập:

| URL | Mô tả |
|-----|-------|
| http://localhost:5000 | Trang chủ |
| http://localhost:5000/capture | Chụp ảnh |
| http://localhost:5000/gallery | Thư viện ảnh |

### Cho phép truy cập Webcam

Khi lần đầu truy cập trang `/capture`, trình duyệt sẽ hỏi quyền truy cập camera. Click **"Allow"** để cho phép.

---

## ❌ Xử lý lỗi thường gặp

### Lỗi 1: "pip không được nhận dạng"

```bash
# Thử sử dụng python -m pip
python -m pip install -r requirements.txt
```

### Lỗi 2: "No module named 'cv2'"

```bash
pip install opencv-python
```

### Lỗi 3: "TensorFlow installation failed"

TensorFlow yêu cầu Python 3.8-3.11. Nếu đang dùng Python 3.12+:

```bash
# Cách 1: Cài đặt Python 3.11
# Cách 2: Bỏ qua TensorFlow (AI features sẽ không hoạt động)
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SQLAlchemy==3.1.1
pip install Pillow==10.1.0 opencv-python==4.8.1.78 numpy==1.24.3
```

### Lỗi 4: "Port 5000 already in use"

```bash
# Chạy trên port khác
python app.py --port 5001

# Hoặc sửa file app.py, đổi port=5000 thành port=5001
```

### Lỗi 5: "CORS error" trên trình duyệt

Đảm bảo đang truy cập qua `http://localhost:5000` thay vì `http://127.0.0.1:5000`

### Lỗi 6: Webcam không hoạt động

1. Kiểm tra webcam có kết nối đúng không
2. Thử trình duyệt Chrome hoặc Firefox (mới nhất)
3. Đảm bảo không có ứng dụng khác đang sử dụng webcam
4. Kiểm tra quyền truy cập camera trong Settings của trình duyệt

---

## 📁 Cấu trúc thư mục sau khi cài đặt

```
Photobooth-Python-Webapp-Project/
├── venv/                  # Virtual environment (tự tạo)
├── instance/
│   └── photobooth.db      # Database SQLite (tự tạo khi chạy)
├── static/
│   └── uploads/           # Thư mục lưu ảnh (tự tạo khi chạy)
├── app.py                 # File chạy chính
├── config.py              # Cấu hình
├── requirements.txt       # Danh sách thư viện
└── ...
```

---

## ✅ Checklist cài đặt

- [ ] Python 3.10/3.11 đã cài đặt
- [ ] Đã clone/tải repository
- [ ] Đã tạo virtual environment
- [ ] Đã kích hoạt virtual environment
- [ ] Đã cài đặt requirements.txt
- [ ] Chạy `python app.py` thành công
- [ ] Truy cập http://localhost:5000 thành công
- [ ] Webcam hoạt động trên trang /capture

---

## 🔄 Cập nhật code mới

Khi có bản cập nhật mới từ repository:

```bash
# Pull code mới
git pull origin main

# Cập nhật thư viện (nếu requirements.txt thay đổi)
pip install -r requirements.txt
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề không giải quyết được:

1. Tạo **Issue** trên GitHub repository
2. Mô tả chi tiết lỗi và environment (OS, Python version)
3. Đính kèm screenshot hoặc error log

---

*Hướng dẫn cài đặt - Photobooth Python Webapp Project*
*Cập nhật: Tháng 1/2026*

