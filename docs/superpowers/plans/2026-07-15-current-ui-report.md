# Current UI Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo `bao_cao_UI/Bao_cao_UI_hien_tai.docx` mô tả đủ 19 trang UI hiện tại, mỗi trang có ảnh chụp riêng và nội dung tiếng Việt đã kiểm chứng.

**Architecture:** Giữ `bao_cao_UI/UI.docx` làm tài liệu tham chiếu và chắt lọc cấu trúc vào `.codex_tmp/ui-report/artifact.md`. Chạy frontend cục bộ, chụp 19 route với dữ liệu thử không nhạy cảm, sau đó dùng một builder `python-docx` để tạo tài liệu mới kế thừa khổ trang, lề, trang bìa và bảng thành viên. Xuất DOCX sang PDF/PNG để kiểm tra trực quan từng trang và lặp lại khi có lỗi.

**Tech Stack:** React/Vite, trình duyệt cục bộ, Python 3.11, python-docx, Microsoft Word PDF export hoặc LibreOffice renderer khi khả dụng, Poppler `pdftoppm`.

## Global Constraints

- Không sửa `bao_cao_UI/UI.docx`; SHA-256 phải còn là `880B015CC1D11E869FA2A04C900F6AF9D5B07DF57246811FA7AE69521060BBE8`.
- Báo cáo có đúng 19 mục trang và tối thiểu 19 ảnh chụp tương ứng.
- Mỗi mục có route, mục đích, thành phần chính, cách sử dụng và trạng thái quan trọng.
- Nội dung chỉ mô tả hành vi có bằng chứng trong mã nguồn hoặc UI chạy thực tế.
- Không để token, mật khẩu hoặc thông tin cá nhân thật trong ảnh hay tài liệu.
- Tệp cuối phải được kiểm tra nội dung có cấu trúc và kiểm tra trực quan toàn bộ trang.

---

### Task 1: Chắt lọc báo cáo mẫu

**Files:**
- Read: `bao_cao_UI/UI.docx`
- Create: `.codex_tmp/ui-report/artifact.md`
- Create: `.codex_tmp/ui-report/template-reference-render/`

**Interfaces:**
- Consumes: DOCX tham chiếu và đặc tả tại `docs/superpowers/specs/2026-07-15-current-ui-report-design.md`.
- Produces: hợp đồng template gồm hình học trang, kiểu chữ, bảng thành viên, ảnh và slot nội dung.

- [ ] **Step 1:** Ghi SHA-256, số section, số trang, kích thước trang, lề, style, bảng và ảnh vào `artifact.md`.
- [ ] **Step 2:** Xuất tài liệu mẫu sang PDF/PNG bằng renderer khả dụng và xem toàn bộ trang ở 100%.
- [ ] **Step 3:** Xác nhận file mẫu không đổi bằng `Get-FileHash -Algorithm SHA256 bao_cao_UI/UI.docx`.

### Task 2: Chuẩn bị dữ liệu và chụp 19 trang

**Files:**
- Read: `frontend/src/App.jsx`
- Read: `frontend/src/pages/*.jsx`
- Read: `frontend/src/api/*.js`
- Create: `.codex_tmp/ui-report/screenshots/*.png`
- Create: `.codex_tmp/ui-report/screenshot-manifest.json`

**Interfaces:**
- Consumes: 19 route trong đặc tả và giao diện chạy tại `http://localhost:3000`.
- Produces: manifest `{route, title, image, state, viewport}` và một PNG riêng cho từng trang.

- [ ] **Step 1:** Chạy `npm run build` trong `frontend` để xác nhận UI build thành công.
- [ ] **Step 2:** Chạy Vite ở chế độ nền và xác nhận `http://localhost:3000` phản hồi.
- [ ] **Step 3:** Thiết lập dữ liệu thử và mock phản hồi API cần thiết trong phiên trình duyệt, không ghi bí mật thật.
- [ ] **Step 4:** Chụp 19 route ở viewport desktop thống nhất, cuộn/chọn trạng thái để nội dung chính hiện rõ.
- [ ] **Step 5:** Kiểm tra manifest có đủ 19 route, file PNG tồn tại và mỗi ảnh có kích thước hợp lệ.

### Task 3: Viết nội dung và dựng DOCX

**Files:**
- Create: `.codex_tmp/ui-report/build_ui_report.py`
- Create: `bao_cao_UI/Bao_cao_UI_hien_tai.docx`

**Interfaces:**
- Consumes: `artifact.md`, `screenshot-manifest.json`, mã nguồn trang và ảnh PNG.
- Produces: DOCX hoàn chỉnh với bìa, bảng nhóm, phần dùng chung, 19 mục trang và bảng route.

- [ ] **Step 1:** Tạo cấu trúc dữ liệu 19 trang trong builder, ghi rõ route, mục đích, thành phần, cách dùng và trạng thái.
- [ ] **Step 2:** Sao chép khổ trang/lề và tái tạo trang bìa, bảng thành viên từ template; định nghĩa style Heading 1/2/3, Normal và Caption nhất quán.
- [ ] **Step 3:** Chèn phần tổng quan, thành phần dùng chung và 19 mục; chèn mỗi ảnh cùng chú thích và page break có kiểm soát.
- [ ] **Step 4:** Thêm bảng tổng hợp route với chiều rộng cột cụ thể, header lặp lại và ô có padding.
- [ ] **Step 5:** Chạy builder và kiểm tra bằng python-docx: 19 route, ít nhất 19 inline shape, bảng thành viên và bảng route đều tồn tại.

### Task 4: Render, kiểm tra và sửa tài liệu

**Files:**
- Read: `bao_cao_UI/Bao_cao_UI_hien_tai.docx`
- Create: `.codex_tmp/ui-report/final-render/page-*.png`
- Create: `.codex_tmp/ui-report/final-render/Bao_cao_UI_hien_tai.pdf`

**Interfaces:**
- Consumes: DOCX từ Task 3.
- Produces: kết quả QA trực quan và tệp Word cuối đã sửa.

- [ ] **Step 1:** Chạy audit section/style/image và kiểm tra không có placeholder, đường dẫn nội bộ hoặc dữ liệu nhạy cảm.
- [ ] **Step 2:** Xuất DOCX sang PDF/PNG và xem toàn bộ trang ở 100%.
- [ ] **Step 3:** Sửa mọi lỗi cắt chữ, tràn ảnh, trang trắng, tiêu đề cô lập hoặc bảng quá chật; render lại sau mỗi đợt sửa.
- [ ] **Step 4:** Kiểm tra lần cuối: file mở được, đủ 19 mục/ảnh, SHA-256 template không đổi và `git status` không chứa thay đổi ngoài phạm vi.

