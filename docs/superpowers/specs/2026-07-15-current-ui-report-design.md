# Đặc tả báo cáo giao diện LancerAI hiện tại

## Mục tiêu

Tạo một báo cáo Word mới dựa trên `bao_cao_UI/UI.docx`, mô tả đầy đủ giao diện đang được triển khai trong `frontend/`. Báo cáo dùng tiếng Việt, giữ tinh thần trình bày của tài liệu mẫu nhưng chuẩn hóa câu chữ, cấu trúc và hình ảnh.

## Phạm vi

Báo cáo phải có một mục và một ảnh chụp riêng cho từng bề mặt giao diện sau:

1. Landing (`/`)
2. Đăng nhập (`/login`)
3. Đăng ký (`/signup`)
4. Giới thiệu (`/about`)
5. Dashboard (`/dashboard`)
6. CV và phỏng vấn (`/candidate`)
7. Hồ sơ ứng viên (`/profile`)
8. Cài đặt tài khoản (`/settings`)
9. Tải CV (`/cv-upload`)
10. Kết quả trích xuất CV (`/cv-extraction-result`)
11. Tối ưu CV (`/cv-optimization`)
12. Lịch sử CV (`/cv-review`)
13. So khớp việc làm (`/job-matching`)
14. Gợi ý việc làm (`/job-recommendations`)
15. Thiết lập phỏng vấn (`/interview`)
16. Phòng phỏng vấn (`/chat`)
17. Báo cáo phỏng vấn (`/interview-report`)
18. Ngân hàng câu hỏi (`/question-bank`)
19. Danh sách báo cáo (`/reports`)

## Cấu trúc tài liệu

1. Trang bìa “UI PROTOTYPE”.
2. Bảng thông tin Nhóm 6 và thành viên, giữ nguyên dữ liệu từ tài liệu mẫu.
3. Giới thiệu ngắn về mục tiêu UI và hành trình người dùng chính.
4. Thành phần giao diện dùng chung:
   - thanh điều hướng và menu tài khoản;
   - hệ thống bố cục, tiêu đề trang và panel;
   - nút hành động, thẻ chỉ số và trạng thái;
   - trạng thái tải, lỗi, rỗng và cảnh báo;
   - nguyên tắc responsive và khả năng sử dụng.
5. Các trang được nhóm theo chức năng nhưng mỗi trang vẫn là một mục độc lập.
6. Bảng tổng hợp route, quyền truy cập và vai trò của từng trang.

## Mẫu nội dung cho mỗi trang

Mỗi mục trang phải có:

- Tên trang và route.
- Mục đích.
- Thành phần chính.
- Cách sử dụng và điều hướng tiếp theo.
- Trạng thái giao diện quan trọng, nếu có.
- Một ảnh chụp giao diện hiện tại với chú thích hình.

Nội dung chỉ mô tả hành vi có bằng chứng trong mã nguồn hoặc giao diện chạy thực tế. Không khẳng định các tích hợp chưa được triển khai; ví dụ đăng nhập mạng xã hội chỉ được mô tả là thành phần trình bày nếu chưa có luồng xác thực tương ứng.

## Hình ảnh

- Mỗi trang có ảnh riêng, ưu tiên kích thước desktop thống nhất.
- Với trang yêu cầu đăng nhập hoặc dữ liệu, dùng trạng thái hợp lệ có thể tái tạo; nếu dịch vụ phụ thuộc chưa sẵn sàng, chụp trạng thái rỗng/lỗi có chủ đích và mô tả đúng trạng thái đó.
- Không đưa dữ liệu nhạy cảm, token, mật khẩu hoặc thông tin cá nhân thật vào ảnh.
- Ảnh phải rõ, không bị cắt nội dung chính và có chú thích nhất quán.

## Phong cách và định dạng

- Giữ tài liệu mẫu làm chuẩn về khổ trang, lề, trang bìa và bảng thành viên.
- Chuẩn hóa hệ thống tiêu đề để tạo phân cấp rõ ràng.
- Dùng câu ngắn, thuật ngữ nhất quán và tiếng Việt tự nhiên.
- Giữ ảnh cùng chú thích; hạn chế để tiêu đề bị tách khỏi nội dung sang trang kế tiếp.
- Không thay đổi tệp `bao_cao_UI/UI.docx`; xuất sang một tệp mới trong cùng thư mục.

## Kiểm tra hoàn thành

- Đủ 19 mục trang và 19 ảnh tương ứng.
- Mỗi mục có đủ các trường nội dung đã quy định.
- Route và hành vi khớp với `frontend/src/App.jsx` và component trang liên quan.
- Không còn nội dung cũ sai với UI hiện tại.
- Tệp DOCX cuối được render và kiểm tra trực quan từng trang; không có chữ/ảnh bị cắt, chồng lấn hoặc lỗi font.
- Tài liệu mẫu giữ nguyên mã băm SHA-256 `880B015CC1D11E869FA2A04C900F6AF9D5B07DF57246811FA7AE69521060BBE8`.
