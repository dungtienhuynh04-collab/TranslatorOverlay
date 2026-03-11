# Game Translator Overlay - Pro

Ứng dụng **Game Translator Overlay - Pro** là một công cụ giúp bạn dịch hội thoại/text từ màn hình (đặc biệt là khi chơi game) theo thời gian thực. Ứng dụng sử dụng một mô hình ngôn ngữ lớn (LLM - Vision) chạy nội bộ thông qua **LM Studio** để quét màn hình, nhận diện chữ và dịch sang ngôn ngữ mong muốn hoàn toàn tự động khi có thay đổi trên màn hình.

## ✨ Tính năng nổi bật

- 🌍 **Dịch Thuật Thời Gian Thực**: Tự động chụp vùng màn hình chỉ định và dịch ngay khi phát hiện có thay đổi hội thoại mới. Tiết kiệm tối đa số lần gọi API nhờ thuật toán nhận diện % pixel thay đổi.
- 🎨 **Giao diện Trải nghiệm Cao (UI/UX)**:
  - Khung Chụp: Thiết kế kéo thả trực quan như các công cụ Crop ảnh chuyên nghiệp.
  - Khung Kết Quả: Hỗ trợ thanh kéo, điều chỉnh độ mờ nền (Opacity), và lựa chọn hiển thị văn bản (Cuộn Scroll hoặc Tự động thu nhỏ Auto-fit).
  - Khả năng **Click xuyên qua (Click-through)** Khung KQ để không làm cản trở khi chơi game.
- 🌓 **Tùy biến Giao diện (Theme)**: Chuyển đổi linh hoạt giữa giao diện Sáng / Tối.
- 🌐 **Đa ngôn ngữ**: Giao diện (UI) hỗ trợ cả Tiếng Việt và Tiếng Anh.
- ⚙️ **Bảo lưu Cài đặt (Settings Memory)**: Toàn bộ cấu hình hệ thống, Prompt và URL của bạn được lưu trữ ở file `settings.json`.
- 🔍 **Chạy ngầm toàn diện**: Ứng dụng tích hợp System Tray (Khay hệ thống) giúp ẩn xuống góc màn hình và tiếp tục quét ngầm.
- 📝 **Theo dõi (Logs)**: Tab Logs kiểm soát chi tiết tiến trình gửi/nhận yêu cầu tới LM Studio.

## 🚀 Yêu cầu hệ thống

1. **Python 3.10+**
2. **LM Studio**: Bạn cần cài đặt [LM Studio](https://lmstudio.ai/) và tải một mô hình **Vision LLM** (ví dụ: `LLaVA`, `Qwen-VL`, v.v.).

## 🛠 Hướng dẫn Cài đặt cấu hình

### Cách 1: Chạy trực tiếp từ mã nguồn

1. Clone Repository này về máy của bạn:
   ```bash
   git clone https://github.com/your-username/GameTranslatorOverlay.git
   cd GameTranslatorOverlay
   ```
2. Tạo môi trường ảo (Virtual Environment) và kích hoạt:
   ```bash
   python -m venv venv
   # Kích hoạt trên Windows:
   .\venv\Scripts\activate
   ```
3. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
4. Khởi chạy ứng dụng:
   ```bash
   python main.py
   ```

### Cách 2: Biên dịch ra file `.exe` độc lập
Nếu bạn muốn đóng gói thanh file cài chạy luôn không cần cài Python, hãy dùng lệnh:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "src;src" --name "GameTranslatorOverlay" main.py
```
*File chạy sẽ nằm trong thư mục `dist/GameTranslatorOverlay/GameTranslatorOverlay.exe`.*

## ⚙️ Hướng dẫn sử dụng cùng LM Studio

1. **Bật LM Studio** lên, tìm một model có hỗ trợ Vision (ví dụ tìm từ khóa `vision` trong khung tìm kiếm) và tải về.
2. Di chuyển sang tab **Local Server (↔️)** ở cột bên trái LM Studio.
3. Chọn Model vừa tải ở trên cùng, điều chỉnh thông số RAM sao cho phù hợp với máy tính.
4. Bật **Start Server**. Ghi nhớ cổng chạy (Mặc định thường là `http://localhost:1234/v1`).
5. **Mở Game Translator Overlay** lên:
   - Trong Tab **Cấu hình**, điều chỉnh **URL API** cho giống trong LM Studio. (App sẽ tự bù `/v1` nếu bạn quên gõ).
   - Mở Khung Chụp và kéo đè lên khung chat/hội thoại trong game.
   - Mở Khung Kết Quả và kéo ra một góc dễ nhìn.
   - Nhấn **Bắt Đầu Dịch**!

## Lược đồ Cấu trúc File

```
📦GameTranslatorOverlay
 ┣ 📂src
 ┃ ┣ 📜capture_overlay.py  # Code giao diện vùng chọn màn hình
 ┃ ┣ 📜display_overlay.py  # Code giao diện kết quả trả về
 ┃ ┣ 📜llm_service.py      # Background worker xử lý nhận diện & gọi LM Studio
 ┃ ┗ 📜main_window.py      # Tích hợp UI chính, Themes và Đa ngôn ngữ.
 ┣ 📜main.py               # Entry-point và thiết lập System Tray
 ┣ 📜requirements.txt      # Khởi chạy thiết lập thư viện 
 ┗ 📜README.md
```

## 📜 Giấy phép (License)
Dự án được phân phối dưới giấy phép MIT. Xem thêm tại file `LICENSE`.
