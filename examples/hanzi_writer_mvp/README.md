# PolyBiz AI - Hanzi Writer MVP

## 🎯 Mục đích
Ứng dụng luyện viết chữ Hán với Air Writing (viết trong không khí qua webcam) + Character Animation + Spaced Repetition System.

## 🚀 Cách chạy

### WSL Ubuntu (Recommended)
```bash
cd ~/projects/fb-voicebot/polybiz-ai/examples/hanzi_writer_mvp
python3 -m http.server 8080
# Mở browser: http://localhost:8080
```

### Windows PowerShell
```powershell
cd C:\path\to\polybiz-ai\examples\hanzi_writer_mvp
python -m http.server 8080
```

### VS Code Live Server
1. Cài extension "Live Server"
2. Click chuột phải vào `index.html` → "Open with Live Server"

---

## ✨ Tính năng

### 📚 Quản lý từ vựng
| Nguồn | Mô tả |
|-------|-------|
| HSK 1-4 | Từ vựng theo trình độ |
| Bộ thủ | 人, 口, 女, 心, 手, 水, 火, 木, 金, 土 |
| Chuyên ngành | Kinh doanh, IT, Y tế, Pháp luật, Tài chính |
| Đặc biệt | Dễ nhầm lẫn, Số đếm, Thời gian, Màu sắc, Gia đình |
| Nhập tùy chọn | Paste đoạn văn → tự trích xuất chữ Hán |
| Import | CSV/Google Sheet, Anki deck export |
| Yêu thích | Lưu/tải danh sách yêu thích |

### 🎯 Air Writing (BETA)
- **Giữ phím SPACE** hoặc nút "Giữ để vẽ" để vẽ
- **Thả ra** để nhấc bút
- **Xòe tay** để xóa (bóp ngón cái-trỏ điều chỉnh kích thước)
- Grid 米字格 với chữ mẫu mờ
- Hướng dẫn khoảng cách tay-camera

### 📊 SRS - Spaced Repetition
- Theo dõi lịch sử luyện tập (localStorage)
- Phân loại: 🔴 Cần ôn tập | 🟡 Đang học | 🟢 Đã thuộc
- Đề xuất ôn tập thông minh
- Streak tracking

### 🔊 Text-to-Speech
- Phát âm chữ Hán khi hoàn thành Quiz
- Dùng Web Speech API (miễn phí)
- Bật/tắt trong panel Thống kê

---

## 🎮 Hướng dẫn sử dụng

### 1. Chọn từ vựng
- Tab "Có sẵn": Chọn HSK, bộ thủ, chuyên ngành...
- Tab "Nhập tùy chọn": Paste đoạn văn tiếng Trung
- Tab "Import": Upload CSV hoặc Anki export

### 2. Bắt đầu luyện
- Chọn số chữ muốn luyện (1-100)
- Click "🚀 Bắt đầu luyện"
- Dùng ⬅️ Trước / Sau ➡️ để chuyển chữ

### 3. Luyện viết
- **Animation**: Xem stroke order
- **Quiz Mode**: Vẽ bằng chuột/touch
- **Air Writing**: Vẽ bằng tay qua webcam

### 4. Theo dõi tiến độ
- Xem thống kê ở panel "Thống kê & Đề xuất ôn tập"
- Click vào chữ yếu để luyện lại

---

## 🖥️ Yêu cầu phần cứng

| Cấu hình | CPU | RAM | Webcam | Giá laptop |
|----------|-----|-----|--------|------------|
| Minimum (Quiz only) | Celeron/A4 | 2GB | - | 3-5 triệu |
| Recommended | i3/Ryzen 3 | 4GB | 720p | 7-10 triệu |
| Optimal | i5/Ryzen 5 | 8GB | 1080p | 12-15 triệu |

---

## 📈 Đọc kết quả test

| Grade | FPS | Đánh giá |
|-------|-----|----------|
| A | ≥30 | Tuyệt vời, dùng full tính năng |
| B | 20-29 | Tốt, đôi khi lag nhẹ |
| C | 15-19 | Tạm được, nên tắt Air Writing |
| D | <15 | Yếu, chỉ dùng Animation cơ bản |

---

## 📝 Ghi chú
- Memory API chỉ hoạt động trên Chrome
- Air Writing cần HTTPS hoặc localhost
- Dữ liệu SRS lưu trong localStorage của browser
- Nếu camera không bật, kiểm tra quyền truy cập

---

## 🔄 Changelog

### v0.3.0 (Dec 24, 2024)
- ✅ Word List Manager với nhiều nguồn nhập
- ✅ SRS tracking + đề xuất ôn tập
- ✅ TTS phát âm khi hoàn thành
- ✅ Pinch-to-resize eraser
- ✅ Session navigation (prev/next)

### v0.2.0 (Dec 24, 2024)
- ✅ Space key control thay gesture
- ✅ Grid 米字格 với chữ mẫu
- ✅ Undo functionality
- ✅ Distance guidance

### v0.1.0 (Dec 24, 2024)
- ✅ Hanzi Writer integration
- ✅ MediaPipe hand tracking
- ✅ Basic air writing
