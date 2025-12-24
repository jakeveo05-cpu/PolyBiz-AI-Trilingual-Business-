# PolyBiz AI - Hanzi Writer MVP

## 🎯 Mục đích
Test hiệu năng Air Writing + Character Animation để xác định yêu cầu phần cứng tối thiểu.

## 🚀 Cách chạy

### Option 1: Live Server (VS Code)
1. Cài extension "Live Server" trong VS Code
2. Click chuột phải vào `index.html` → "Open with Live Server"

### Option 2: Python HTTP Server
```bash
cd polybiz-ai/examples/hanzi_writer_mvp
python -m http.server 8080
# Mở browser: http://localhost:8080
```

### Option 3: Node.js
```bash
npx serve polybiz-ai/examples/hanzi_writer_mvp
```

## 📊 Các tính năng test

| Tính năng | Mô tả | Yêu cầu |
|-----------|-------|---------|
| Hanzi Animation | Hiển thị stroke order | Nhẹ |
| Quiz Mode | Luyện viết bằng chuột/touch | Nhẹ |
| Air Writing | Viết bằng ngón tay + webcam | Nặng |

## 🖥️ Yêu cầu phần cứng dự kiến

### Minimum (Chỉ Animation + Quiz)
- CPU: Intel Celeron / AMD A4
- RAM: 2GB
- Browser: Chrome 80+
- Giá laptop: ~3-5 triệu VND

### Recommended (Full features + Air Writing)
- CPU: Intel i3 / AMD Ryzen 3
- RAM: 4GB
- Webcam: 720p
- Browser: Chrome 90+
- Giá laptop: ~7-10 triệu VND

### Optimal (Mượt mà)
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB
- Webcam: 1080p
- Giá laptop: ~12-15 triệu VND

## 📈 Cách đọc kết quả test

| Grade | FPS | Đánh giá |
|-------|-----|----------|
| A | ≥30 | Tuyệt vời, dùng full tính năng |
| B | 20-29 | Tốt, đôi khi lag nhẹ |
| C | 15-19 | Tạm được, nên tắt Air Writing |
| D | <15 | Yếu, chỉ dùng Animation cơ bản |

## 🎮 Hướng dẫn sử dụng

1. **Animation**: Click "▶️ Animation" để xem stroke order
2. **Quiz**: Click "✍️ Quiz Mode" rồi dùng chuột vẽ theo
3. **Air Writing**: 
   - Click "📹 Bật Camera"
   - Giơ tay trước webcam
   - Chụm ngón cái + ngón trỏ để vẽ
   - Tách ra để dừng vẽ

## 📝 Ghi chú
- Memory API chỉ hoạt động trên Chrome
- Air Writing cần HTTPS hoặc localhost
- Nếu camera không bật, kiểm tra quyền truy cập
