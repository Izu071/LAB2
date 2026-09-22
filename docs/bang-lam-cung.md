# Bảng làm cứng, lab S2

Tên: *Trương Minh Quân* · Mã số sinh viên: *31241020887* · Ngày nộp: *22/09/2026*

Mỗi dòng là một thay đổi bạn đã làm, không phải một thay đổi bạn định làm. Cần ít
nhất bốn dòng, và trong đó ít nhất một dòng dẫn về kỹ thuật T1548.001 của ATT&CK
v19.2 và ít nhất một dòng dẫn về một mã trong CWE 4.20.

Ba cột nặng nhẹ khác nhau. Cột thứ nhất dễ nhất, vì nó chỉ đòi bạn đọc tài liệu.
Cột thứ hai đòi bạn nghĩ như người phải trực hệ thống ấy sáu tháng nữa. Cột thứ ba
đòi bạn nghĩ như người tấn công vẫn còn đường vào sau khi bạn đã vá, và nó là cột
hay bị bỏ trống nhất.

| Thay đổi đã làm                                                                                      | Chặn được điều gì, dẫn ATT&CK/CWE                                                                                                       | Làm hỏng điều gì (thao tác thủ công/tuần)                                                              | Thứ vẫn còn qua được                                                                                              |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `user: sv` (UID 10001) trong `docker-compose.yml`, bỏ chạy bằng root                                 | CWE-250 — tiến trình không còn chạy với quyền root mặc định                                                                             | Nếu cần cài thêm gói lúc runtime phải rebuild image thay vì `exec` vào sửa trực tiếp                   | Nếu image base bị compromise ở supply chain (chưa ghim digest), user `sv` vẫn kế thừa lỗ hổng của image           |
| `cap_drop: ALL` + `cap_add: NET_BIND_SERVICE`, `no-new-privileges: true`                             | CWE-1188 — giảm tập capability mặc định; chặn T1548.001 — Setuid                                                                        | Nếu dịch vụ cần bind thêm cổng đặc quyền khác phải sửa lại `cap_add`                                   | `NET_BIND_SERVICE` vẫn được giữ lại — nếu tiến trình bị chiếm quyền vẫn có thể bind cổng `<1024`                  |
| `read_only: true` cho root filesystem, chỉ chừa volume `/var/log/css-s02`                            | Chặn ghi đè tệp cấu hình ở bước attack, liên quan CWE-732                                                                               | Mọi thay đổi cấu hình runtime phải qua rebuild/mount lại, không sửa nóng trong container               | Thư mục log vẫn ghi được — nếu ứng dụng cho phép ghi tùy ý đường dẫn, đây vẫn là điểm ghi còn mở                  |
| Bỏ setuid `/usr/local/bin/doc-bimat` (`chmod 0755`), `cau-hinh.yaml` → `0644`, `bi-mat.txt` → `0600` | T1548.001 trực tiếp — chương trình không còn tự nâng quyền root; CWE-732 — tệp cấu hình không còn quyền ghi cho người ngoài owner/group | Nếu `doc-bimat` thực sự cần đọc `bi-mat.txt` hợp lệ về sau, phải thiết kế lại qua group thay vì setuid | Nếu tài khoản `sv` bị chiếm (ví dụ RCE trong `dich-vu.py`), kẻ tấn công vẫn đọc được mọi tệp mà `sv` có quyền đọc |


## Một câu về thứ bạn quyết định không làm

Có ít nhất một biện pháp bạn cân nhắc rồi bỏ, vì nó đắt hơn phần rủi ro nó cắt
được. Viết ra biện pháp ấy và lý do bỏ. Nguyên lý thứ bảy của học phần nói an toàn
là bài toán kinh tế, và một bài nộp không có dòng nào bị bỏ là một bài chưa cân
nhắc gì.

*Em cân nhắc rồi bỏ việc đổi `doc-bimat` sang một chương trình dùng `sudo` có cấu hình giới hạn thay vì chỉ gỡ bit setuid, vì lợi ích thêm được (giữ khả năng đọc tệp bí mật cho một tài khoản bảo trì trong tương lai) không bù nổi chi phí: bài lab hiện tại không có nhu cầu vận hành nào thật sự cần đọc `bi-mat.txt` ngoài hai phép thử tấn công đã đóng gói, nên dựng thêm một cơ chế `sudo` chỉ làm tăng diện tích tấn công (thêm một tệp cấu hình `/etc/sudoers.d` cần bảo vệ) mà không cắt được rủi ro nào đang tồn tại trong phạm vi bài.
*
