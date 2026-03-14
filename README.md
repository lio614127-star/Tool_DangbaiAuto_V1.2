# Douyin Downloader Tool

Tool tải video Douyin tự động với giao diện người dùng (GUI) đơn giản và dễ sử dụng.

## ✨ Tính năng

- Tải video Douyin không logo/watermark.
- Giao diện trực quan được xây dựng bằng CustomTkinter.
- Tự động hóa trình duyệt bằng Playwright.
- Quản lý lịch sử tải xuống.

## 🚀 Cài đặt

1. **Clone repository:**
   ```bash
   git clone <link-repo-cua-ban>
   cd Tool_DangbaiAuto
   ```

2. **Cài đặt môi trường ảo (khuyến nghị):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Linux/macOS
   # hoặc
   .\venv\Scripts\activate  # Trên Windows
   ```

3. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cài đặt Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## 💻 Cách sử dụng

Chạy ứng dụng bằng lệnh:
```bash
python main.py
```

## 📦 Đóng gói thành executable (.exe)

Sử dụng script `build.py` để đóng gói ứng dụng:
```bash
python build.py
```
File `.exe` sau khi đóng gói sẽ nằm trong thư mục `dist/`.

## 📝 Yêu cầu hệ thống

- Python 3.8 trở lên.
- Kết nối internet.

## ⚖️ Giấy phép

Dự án này được tạo ra cho mục đích học tập và nghiên cứu cá nhân.
