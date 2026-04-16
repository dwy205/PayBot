# [Project] AI Milk Tea Bot - Casso Entry Test 2026

## 1. Thông tin chung
* [cite_start]**Công ty:** CASSO COMPANY LIMITED 
* [cite_start]**Vị trí:** Intern Software Engineer 2026 
* [cite_start]**Thời hạn hoàn thành:** 72 giờ kể từ khi nhận đề 

---

## 2. Bối cảnh dự án
Mẹ bạn mở quán trà sữa bán tại cửa hàng và online qua tin nhắn. Tuy nhiên, lượng đơn tăng cao khiến việc trả lời bị chậm, thiếu thông tin và gây nhầm lẫn

[cite_start]**Mục tiêu:** Xây dựng một AI Bot (bản sao AI của mẹ) để tự động hóa quy trình đặt hàng[cite: 15].

---

## 3. Yêu cầu kỹ thuật & Tính năng
### Nhiệm vụ chính
* [cite_start]**Nền tảng:** Hoạt động trên Telegram[cite: 15].
* [cite_start]**Cốt lõi:** Ứng dụng các mô hình ngôn ngữ lớn (LLM) để giao tiếp[cite: 15].
* **Chức năng:**
    * [cite_start]Tư vấn món dựa trên menu (file CSV kèm theo)[cite: 11, 15].
    * [cite_start]Hỗ trợ đặt món và tính tiền cho khách[cite: 15].
    * [cite_start]Tổng hợp thông tin đơn hàng sau khi thanh toán để chuẩn bị món và giao hàng[cite: 16].

### Khuyến khích (Cộng điểm)
* [cite_start]Sử dụng **payOS** để tạo QR thanh toán và xác nhận thanh toán tự động[cite: 26].
* [cite_start]Deploy lên server để Ban giám khảo có thể testing trực tiếp[cite: 22].

---

## 4. Danh mục nộp bài (Deliverables)
[cite_start]Bài nộp gửi về **hr@cas.so** bao gồm[cite: 18]:

1. [cite_start]**Video demo:** Link Google Drive hoặc Youtube[cite: 19].
2. [cite_start]**Mã nguồn:** Link Repo (Github, GitLab,...)[cite: 20].
3. [cite_start]**Tài liệu phân tích giải pháp:** File PDF[cite: 21].
4. [cite_start]**Link Bot:** Tên Bot đã deploy (nếu có)[cite: 22].

---

## 5. Lưu ý quan trọng
* [cite_start]**Đánh giá:** Thang điểm dựa trên khả năng vận hành hiệu quả thực tế[cite: 24].
* [cite_start]**Hỗ trợ:** Có thể yêu cầu BTC cấp OpenAI API Key nếu cần[cite: 25].
* [cite_start]**Vibe code:** Cho phép dùng AI hỗ trợ viết code nhưng phải hiểu và kiểm soát được mã nguồn[cite: 27].

---

## 6. Cách chạy bot (bản đã implement)

### Công nghệ dùng
- Python + `python-telegram-bot`
- LLM API (OpenAI hoặc Gemini) để:
  - tư vấn món theo ngữ cảnh menu
  - trích xuất ý định đặt món từ tin nhắn tự nhiên
- payOS API để tạo link/QR thanh toán thật và kiểm tra trạng thái thanh toán

### Tính năng đã có
- Đọc menu từ `Menu.csv`
- `/menu`: flow nút bấm chọn món theo từng bước:
  - chọn danh mục
  - chọn món
  - chọn size
  - chọn topping
- Chat tự nhiên để:
  - tư vấn món
  - đặt món (tên món, size M/L, số lượng, topping)
- `/cart`: xem giỏ và tổng tiền
- `/checkout`: tạo mã QR payOS theo tổng tiền
- Chỉ cho phép nhập thông tin giao hàng sau khi giao dịch đã được xác nhận thanh toán
- Xuất tóm tắt đơn hàng để quán chuẩn bị món/giao hàng

### Cài đặt
1. Tạo virtual environment (khuyến nghị)
2. Cài dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Tạo file `.env` từ `.env.example` và điền:
   - `TELEGRAM_BOT_TOKEN`
   - `LLM_PROVIDER` (`openai` hoặc `gemini`)
   - Nếu dùng OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL`
   - Nếu dùng Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`
   - `PAYOS_CLIENT_ID`
   - `PAYOS_API_KEY`
   - `PAYOS_CHECKSUM_KEY`
   - `PAYOS_RETURN_URL`
   - `PAYOS_CANCEL_URL`
   - (tuỳ chọn) `STORE_NAME`

### Chạy bot
```bash
python bot.py
```

### Deploy Telegram bot (polling)
1. Đưa code lên Github.
2. Tạo service Python trên Render/Railway.
3. Set Start Command: `python bot.py`.
4. Thêm toàn bộ biến môi trường trong `.env.example`.
5. Deploy xong, bot sẽ online 24/7 và nhận tin nhắn Telegram.

### Gợi ý test nhanh trên Telegram
1. `/start`
2. `/menu`
3. Nhắn: `Dat 2 tra chanh leo size L them tran chau den`
4. `/cart`
5. `/checkout`
6. Gửi: `Nguyen Van A | 0909000111 | 12 Le Loi, Q1`

### Cấu trúc file chính
- `bot.py`: entrypoint và Telegram handlers
- `menu_service.py`: đọc/tìm menu
- `llm_service.py`: gọi OpenAI cho tư vấn + parse order
- `order_service.py`: quản lý giỏ hàng/tính tổng/tóm tắt đơn
- `config.py`: đọc biến môi trường