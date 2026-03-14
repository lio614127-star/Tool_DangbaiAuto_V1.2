# 📖 Hướng Dẫn Sử Dụng GSD 2 Toàn Tập

GSD 2 (Get Shit Done 2) không chỉ là một công cụ AI hỗ trợ code thông thường; nó là một **Agent tự trị (Autonomous Agent)** được thiết kế để tự động quản lý dự án, viết code, kiểm thử và commit vào Git mà không cần bạn phải giám sát liên tục.

## 1. Khái Niệm Cốt Lõi (Core Concepts)

GSD 2 quản lý công việc theo hệ thống phân cấp chặt chẽ:

*   **Milestone (Mốc quan trọng):** Một phiên bản phần mềm hoàn chỉnh có thể phát hành (thường gồm 4-10 Slices). *Ví dụ: M001 - Hệ thống Đăng nhập.*
*   **Slice (Nhánh tính năng):** Một tính năng hoàn chỉnh từ front-end đến back-end có thể demo được (gồm 1-7 Tasks). *Ví dụ: S01 - API Đăng ký người dùng.*
*   **Task (Tác vụ):** Đơn vị công việc nhỏ nhất, được thiết kế vừa vặn với bộ nhớ (context window) của AI trong 1 phiên làm việc. *Ví dụ: T01 - Tạo bảng User trong Database.*

**Quy tắc bất di bất dịch:** Một Task PHẢI thực hiện xong trong 1 phiên làm việc duy nhất để tránh việc AI bị "quá tải thông tin". Nếu task quá lớn, nó sẽ bị chia nhỏ.

---

## 2. Cài Đặt & Khởi Tạo

### Cài đặt toàn cầu (Global Install)
Cần có Node.js ≥ 20.6.0 (khuyên dùng 22+).
```bash
npm install -g gsd-pi
```

### Đăng nhập & Chọn AI Model
Mở terminal và gõ:
```bash
gsd
```
Trong giao diện CLI, gõ lệnh `/login`. 
GSD hỗ trợ hơn 20 nhà cung cấp (Anthropic, OpenAI, OpenRouter, Gemini, Copilot,...). Nếu bạn dùng Claude Max hoặc Copilot, hệ thống sẽ tự động xác thực qua OAuth. Nếu không, hãy dán API Key của bạn.

---

## 3. Quy Trình Làm Việc (Workflow)

GSD 2 cung cấp hai phong cách làm việc chính: **Từng bước (Step Mode)** và **Tự động hoàn toàn (Auto Mode)**.

### Cách 1: Bắt đầu một dự án mới (Khuyên dùng Step Mode ban đầu)
1. Mở terminal tại một thư mục trống.
2. Gõ lệnh: `gsd`
3. GSD sẽ nhận diện đây là dự án mới và tự động mở luồng **Thảo luận (Discuss Flow)**.
4. Bạn sẽ chat với AI để mô tả: *Dự án này làm gì? Dùng công nghệ gì? Có yêu cầu đặc biệt nào không?*
5. GSD sẽ tự động tạo thư mục ẩn `.gsd/` và sinh ra các file nền tảng:
   * `PROJECT.md` (Tổng quan dự án).
   * `DECISIONS.md` (Các quyết định kiến trúc).
   * `M001-ROADMAP.md` (Bản kế hoạch Milestone đầu tiên).

### Cách 2: Vòng lặp Tự Động (The Auto Loop)
Khi dự án đã có Roadmap, đây là lúc sức mạnh thực sự của GSD 2 tỏa sáng.
Gõ lệnh:
```bash
/gsd auto
```
Lúc này, bạn có thể đi pha cà phê. GSD 2 sẽ tự động chạy qua vòng đời sau cho mỗi Slice:
1. **Research (Nghiên cứu):** Quét mã nguồn, tìm hiểu các file liên quan.
2. **Plan (Lập kế hoạch):** Chia Slice thành các Task nhỏ. Xác định các tiêu chí phải đạt được (Must-haves).
3. **Execute (Thực thi):** Mở một phiên làm việc mới, "sạch sẽ" (fresh context) để code cho từng Task.
4. **Verify (Xác minh):** Tự động chạy lệnh kiểm thử, build code để đảm bảo code hoạt động.
5. **Complete (Hoàn thành):** Tự động tạo nhánh Git riêng (ví dụ: `gsd/M001/S01`), commit code, và gộp (squash merge) vào nhánh `main`.
6. **Reassess (Đánh giá lại):** Xem xét lại Roadmap xem có cần điều chỉnh gì cho Slice tiếp theo không.

### Cách 3: Chế độ Từng Bước (Step Mode)
Nếu bạn chưa yên tâm để AI tự chạy 100%, hãy dùng Step Mode.
Gõ lệnh:
```bash
/gsd
```
(Hoặc `/gsd next`). AI sẽ thực hiện xong đúng **1 đơn vị công việc** (ví dụ: Lập kế hoạch xong 1 Slice), sau đó dừng lại và hiện một bảng thông báo hỏi bạn: *"Tôi vừa làm xong phần này, tiếp theo làm gì?"*. Bạn có thể kiểm tra file nó vừa tạo rồi bấm "Continue".

---

## 4. Các Lệnh Hữu Ích (Commands)

Trong giao diện `gsd`, bạn có thể dùng các lệnh sau:

| Lệnh | Mô tả chức năng |
| :--- | :--- |
| `/gsd auto` | Kích hoạt chế độ tự trị hoàn toàn. |
| `/gsd stop` | Dừng chế độ auto một cách an toàn. |
| `/gsd discuss` | Mở kênh chat để thảo luận kiến trúc (có thể chạy song song lúc đang auto). |
| `/gsd status` | Xem bảng điều khiển tiến độ (Dashboard) chi tiết. |
| `/gsd queue` | Lên lịch cho các Milestone tiếp theo. |
| `/gsd migrate` | Chuyển đổi dự án dùng GSD v1 (.planning) sang chuẩn v2 (.gsd). |
| `/worktree` (`/wt`) | Quản lý Git Worktree (tạo nhánh phụ để AI code mà không ảnh hưởng nhánh bạn đang làm). |
| `Ctrl+Alt+G` | Bật/tắt nhanh Dashboard nổi trên màn hình. |

**Tuyệt chiêu: "2 Màn Hình"**
Mở 2 cửa sổ terminal cho cùng 1 thư mục:
*   Terminal 1: Chạy `/gsd auto` (Để AI tập trung code).
*   Terminal 2: Mở `gsd` và dùng lệnh `/gsd status` (Để bạn xem tiến độ real-time) hoặc `/gsd discuss` (Để bạn thêm yêu cầu mới mà không cần bắt AI dừng code).

---

## 5. Cấu Hình Nâng Cao (Preferences)

Bạn có thể tinh chỉnh cách AI hoạt động bằng cách chỉnh sửa file `~/.gsd/preferences.md` (cấu hình toàn hệ thống) hoặc `.gsd/preferences.md` (cấu hình cho dự án hiện tại). Dùng lệnh `/gsd prefs` để mở.

**Các tùy chọn quan trọng:**

1. **Chọn Model chuyên biệt cho từng giai đoạn:**
   Nên dùng model đắt tiền/thông minh cho việc lập kế hoạch, và model rẻ/nhanh cho việc nghiên cứu.
   ```yaml
   models:
     research: openrouter/deepseek/deepseek-r1 (nhanh/rẻ)
     planning: claude-opus-4-6 (thông minh nhất)
     execution: claude-sonnet-4-6 (code tốt)
   ```
2. **Quản lý ngân sách (Budget Ceiling):**
   Ngăn AI "đốt tiền" quá mức trong chế độ Auto.
   ```yaml
   budget_ceiling: 50.00 # Dừng auto nếu chi phí vượt 50 USD
   ```
3. **Giám sát thời gian (Auto Supervisor):**
   ```yaml
   auto_supervisor:
     soft_timeout_minutes: 20 # Cảnh báo AI sắp hết giờ
     idle_timeout_minutes: 10 # Cảnh báo nếu AI đứng im không làm gì
     hard_timeout_minutes: 30 # Bắt buộc dừng tác vụ
   ```

---

## 6. Tính Năng Đặc Biệt (Khác biệt so với V1)

*   **Không bao giờ bị "Ngáo" Context:** Mỗi Task được thực thi trong một phiên (session) hoàn toàn mới. AI không phải nhớ lại những đoạn chat rác từ hôm qua.
*   **Phục hồi sau sự cố (Crash Recovery):** Nếu mất điện giữa chừng, lần tới chạy `/gsd auto`, hệ thống sẽ tự động đọc file lock, tổng hợp lại nhật ký làm việc và tiếp tục chính xác tại dòng code đang viết dở.
*   **Tích hợp Công cụ (Bundled Tools):** GSD 2 tự động nạp 13 công cụ (như Trình duyệt Playwright để test UI, Tìm kiếm web, chạy lệnh nền, thao tác API Mac) để AI có thể tự mình giải quyết mọi vấn đề.
