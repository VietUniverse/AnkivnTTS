<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Anki-icon.svg" alt="Anki Logo" width="120" />
  <h1>🎙️ AnkiVN TTS</h1>
  <p><b>Hệ thống Text-to-Speech Đa Lõi - Siêu Tốc & Chuyên Nghiệp Nhất cho Anki</b></p>
  <p>
    <a href="https://ankiweb.net/shared/info/1388060198">
      <img src="https://img.shields.io/badge/AnkiWeb-1388060198-blue?style=for-the-badge&logoColor=white" alt="AnkiWeb">
    </a>
    <img src="https://img.shields.io/badge/License-Free-green?style=for-the-badge" alt="License">
    <img src="https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge" alt="Python">
  </p>
</div>

<hr>

## 🚀 Tính Năng Cốt Lõi (Core Features)

Phần mềm tích hợp kiến trúc **Đa luồng (Multi-threading)** tiên tiến cùng 4 động cơ sinh âm thanh hoạt động ưu việt ở cả hai trạng thái Online và Offline:

1. 🌐 **Edge TTS Neural:** Trực tiếp kết nối mạng với chuẩn Microsoft Neural. Hỗ trợ hơn 200+ giọng đọc AI cực kì mượt mà toàn cầu.
2. ⚡ **Google TTS:** Tốc độ tải "bàn thờ", siêu nhẹ, fallback hoàn hảo khi mạng yếu.
3. 💻 **Windows SAPI5:** Tạo file Offline tốc siêu tốc bằng cách sử dụng các giọng sẵn có trên hệ điều hành Windows 11 (như Microsoft An).
4. 🤖 **Piper Offline Neural:** Phương thức phát âm AI Offline thượng lưu. Cho phép cắm file `piper.exe` và `Model.onnx` cá nhân ngay trên giao diện mà không làm cồng kềnh Add-on.

### ⚡ Cấu trúc Đa luồng & Smart Workflow
- **Multi-Threading:** Download và xử lý **5 file âm thanh cùng lúc**, tăng tốc độ tạo thẻ lên 500% so với các công cụ TTS thông thường.
- **Workflow Queue (Hàng đợi tác vụ):** Xử lý đồng thời 3-5 ngôn ngữ (Anh, Pháp, Đức...) trên hàng ngàn Thẻ chỉ với 1 cú click!
- **Smart Sanitizer:** Tự động loại bỏ thẻ đục lỗ `{{c1::từ vựng}}`, bỏ qua ngoặc giải thích `(...)`.

---

## ⚙️ Hướng dẫn Cài đặt (Installation)

1. Mở phần mềm **Anki**, chọn thanh menu `Tools` (Công cụ) >  `Add-ons` (Tiện ích).
2. Chọn **Get Add-ons...** (Tải tiện ích...) 
3. Nhập mã Code thần thánh phía dưới:
> ### 🎈 Mã Cài đặt Ankiweb: `1388060198`
4. Khởi động lại Anki của bạn.

---

## 📚 Hướng dẫn Sử dụng Chi tiết (Detailed User Guide)

### 📌 MỨC ĐỘ 1: TẠO ÂM THANH CƠ BẢN (1 NGÔN NGỮ)
1. Mở cửa sổ **Duyệt thẻ (Browser)** của Anki.
2. Bôi đen các Thẻ (Notes) bạn muốn thêm âm thanh.
3. Trên thanh công cụ, chọn **AnkiVN TTS** -> **Add Audio...**.
4. **Cấu hình trên giao diện:**
   - **Source Field:** Chọn cột trích xuất văn bản (Ví dụ: `English_Word`).
   - **Destination Field:** Chọn cột đổ âm thanh vào (Ví dụ: `Audio`).
   - **Engine & Voice:** Chọn Động cơ yêu thích (Ví dụ: _Edge TTS - en-US-GuyNeural_).
   - Tinh chỉnh Tốc độ (Speed), Cao độ (Pitch) theo ý muốn.
5. Bấm vào nút **"🔽 Thêm Tác Vụ Ghi Âm 🔽"**. Giao diện sẽ thả cấu hình của bạn xuống Bảng Danh sách ở dưới.
6. Bấm **"Chạy tất cả Tác vụ"** và cảm nhận tốc độ nạp âm thanh!

---

### 📌 MỨC ĐỘ 2: TỰ ĐỘNG HÓA ĐA NGÔN NGỮ (POLYGLOT WORKFLOW)
*(Tính năng Đỉnh cao: Trộn lẫn thẻ tiếng Anh, Pháp, Đức, Ý vào nhau và sinh âm thanh cùng 1 lúc không chệch đi đâu được)*

Giả sử bạn có 1 Template (Note Type) học Ngoại ngữ chứa 3 vùng chữ: **English Word**, **French Word** và **Vietnamese Meaning**. Thay vì làm 3 lần độc lập, hãy thao tác Đa luồng:

1. Tại Browser, bôi đen `Ctrl + A` toàn bộ Card bộ sưu tập của bạn.
2. Mở cửa sổ **AnkiVN TTS**:
   * Cài đặt Source: `English Word` -> Dest: `English Audio` (Giọng English). **Bấm 🔽 Thêm Tác vụ**.
   * Cài đặt Source: `French Word` -> Dest: `French Audio` (Giọng French). **Bấm 🔽 Thêm Tác vụ**.
   * Cài đặt Source: `Vietnamese Meaning` -> Dest: `Vietnamese Audio` (Giọng Microsoft Hoài My). **Bấm 🔽 Thêm Tác vụ**.
3. Lúc này, **Bảng Danh Sách Tác vụ (Workflow)** ở dưới đã có 3 dòng chờ xử lý.
4. Nhìn lên trên cùng, bấm nút **Lưu (Save)** ở mục **Preset**, đặt tên là *"Full Combo Ngôn Ngữ"*. (Từ giờ trở đi, 3 cấu hình này đã được lưu vĩnh viễn, lần sau không cần làm lại!)
5. Bấm **"Chạy tất cả Tác vụ"**. Addon sẽ lục lọi qua tất cả các note. Nếu nó tìm thấy thẻ tiếng Pháp, nó tự động đổ đúng âm tiếng Pháp cho cột tương ứng và bỏ qua các cột trống. Cực kỳ thông minh!

---

### 📌 MỨC ĐỘ 3: SỬ DỤNG PIPER KẾT XUẤT OFFLINE (KHÔNG CẦN WIFI)
Piper là hệ thống AI giọng nói siêu thực hoạt động tuyệt đối không cần Internet. Để dùng Piper mà Add-on không bị nặng cấu hình:
1. Bạn tự tải phần mềm lõi `piper.exe` và 1 file trí tuệ `.onnx` (model âm thanh) về máy tính.
2. Mở AnkiVN TTS, chọn **Engine: Piper Offline**.
3. Cửa sổ phụ sẽ hiện ra! Hãy dán đường link thư mục chứa `piper.exe` và `model.onnx` trên máy bạn vào hai ô trống.
4. Bấm **Thêm Tác vụ** và sinh âm thanh bình thường! Add-on có cơ chế mã hoá cực thông minh, mỗi khi bạn đổi đường link Model sang giọng khác, Add-on sẽ nhận diện và tạo file tts rời chuyên biệt không bao giờ bị nghe trùng lặp!

---
*Được phát triển bởi Cộng đồng Anki VN - Tối ưu 100% dành cho người Học.*
