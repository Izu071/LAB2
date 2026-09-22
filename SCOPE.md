# Phạm vi cho phép, lab S2

Phiên bản 1, ngày 18/08/2026. Băm sha256 của chính tệp này nằm trong `evidence/S02/SHA256SUMS` sau khi bạn chạy `make export-evidence`, để bản bạn ký truy ngược được về đúng một phiên bản.

Văn bản chung của học phần vẫn có hiệu lực. Tệp này nói phần riêng của bài S2, và phần riêng ấy đáng đọc kỹ vì đây là bài lab đầu tiên có phần tấn công.

## 1. Bài này cho bạn làm gì

Bài S2 dừng ở **mức chứng minh một bước**: chạy một phép thử đã đóng gói sẵn, một bước, nhằm chứng minh một cấu hình sai cụ thể dẫn tới truy cập trái phép, rồi bắt buộc vá và chứng minh phép thử ấy đã thất bại sau khi vá. Hai phép thử của `make attack` là toàn bộ phần tấn công của bài, và cả hai đều nằm trong `dich-vu/thu-leo-quyen.sh` để bạn đọc trước khi chạy.

Học phần này dạy làm cứng cấu hình hệ điều hành và cô lập tiến trình. Việc biến một lỗi ghi tràn thành chuỗi khai thác chạy được, việc viết shellcode, và việc vượt qua cơ chế phòng vệ thuộc học phần Kiểm thử thâm nhập, học song song trong cùng học kì. Việc mổ một tệp nhị phân độc hại thuộc học phần Phân tích mã độc. Ranh giới này không phải để giữ bí mật với bạn, nó là để hai học phần không dạy trùng nhau và để mỗi bên dạy tới nơi.

## 2. Tài sản trong phạm vi

| Thứ | Định danh |
|---|---|
| Container dịch vụ | `css-s02-dichvu` |
| Container kiểm định | `css-s02-kiem` |
| Mạng | `css-s02-labnet`, bridge riêng của lab |
| Ổ lưu nhật ký | `css-s02-nhat-ky` |
| Cổng | duy nhất một ánh xạ, về `127.0.0.1` trên máy bạn |
| Tài khoản thử | `sv`, uid 10001, trong container của bạn |
| Tệp bí mật thử | `/etc/css-s02/bi-mat.txt`, nội dung là chuỗi thử nghiệm của lab, không phải bí mật thật của ai |

Ngoài bảng này không có gì thuộc phạm vi.

## 3. Bạn được làm

- Chạy `make attack` và `make defend` bao nhiêu lần tùy ý, trên container của chính bạn.
- Đọc và sửa mọi tệp trong kho của bạn, gồm cả các tập lệnh đo trong `dich-vu/`.
- Đọc `/etc/css-s02/bi-mat.txt` trong container của bạn bằng hai phép thử đã đóng gói.
- Dựng lại ảnh, xóa ổ lưu, làm lại từ đầu bao nhiêu lần tùy ý trước hạn nộp.

## 4. Bạn không được làm

- Gửi gói tin tới bất kỳ đích nào ngoài `127.0.0.1` và dải mạng compose của chính lab này.
- Dùng `privileged`, `network_mode: host`, `pid: host`, hoặc tắt seccomp bằng `unconfined`. Bộ kiểm đọc chính tệp compose của bạn và đánh trượt nếu thấy, và đó là lỗi chặn chứ không phải lỗi trừ điểm.
- Thêm năng lực ngoài danh sách đề bài cho phép. Danh sách ấy có đúng một mục.
- Tấn công từ chối dịch vụ dưới mọi hình thức.
- Viết, tải, hoặc chạy mã độc, cửa hậu, kênh điều khiển.
- Bẻ khóa mật khẩu ngoài tập được phát.
- Thao tác trên kho lab của người khác, hoặc trên kho nguồn và kho phát hành của học phần.
- Thử nghiệm trên hạ tầng của UEH, của HCMUT, hoặc của GitHub.
- Công bố công khai bất kỳ phép thử nào được phát trong học phần.

## 5. Dữ liệu

Chỉ dùng dữ liệu do lab phát. Không đưa dữ liệu cá nhân thật của bất kỳ ai vào tệp cấu hình, nhật ký, hay bài nộp, kể cả của chính bạn. Tệp bí mật của lab là một chuỗi thử nghiệm, và nó nằm trong ảnh để bạn có một thứ cụ thể để mất hoặc để giữ.

## 6. Cửa sổ thời gian

Phạm vi này có hiệu lực từ khi bạn nhận kho tới hết hạn nộp, tức trước giờ buổi S3. Sau thời điểm ấy, chạy lại lab để ôn thì vẫn được, nhưng mọi ràng buộc trên vẫn nguyên hiệu lực.

## 7. Nghĩa vụ khôi phục

Bài chỉ được coi là xong khi bạn đã chạy `make defend` và `make verify`, tức đã vá và đã chứng minh vá xong nó thất bại. Chạy `make down` để trả máy về trạng thái sạch; lệnh này xóa container, mạng và ổ lưu của lab, và giữ nguyên `evidence/S02` vì đó là bài nộp của bạn.

## 8. Phần phòng thủ đi kèm

Bài này không cho bạn xem một cấu hình hở rồi bỏ đó. Mỗi phép thử ở bước tấn công đều có một chỗ vá tương ứng, và bộ kiểm đòi đúng cặp trước và sau:

| Phép thử | Chỗ vá tương ứng |
|---|---|
| Đọc tệp bí mật qua chương trình setuid | chặn leo quyền qua setuid trong compose, và bỏ bit setuid trong ảnh |
| Ghi đè tệp cấu hình của dịch vụ | sửa quyền tệp cấu hình, và đặt hệ tệp gốc ở chế độ chỉ đọc |

Nếu bạn thấy mình đang tìm cách đi sâu hơn vào việc khai thác thay vì vá, bạn đã đi lạc sang học phần khác. Đó là dấu hiệu để dừng lại, không phải dấu hiệu để tự hào.

## 9. Khi bạn lỡ vượt phạm vi

Báo trong vòng 24 giờ, trên Discussions của học phần hoặc qua thư điện tử nếu việc cần kín. Ghi lại bạn đã làm gì, lúc nào, và trên máy nào. **Báo cáo trung thực không bị xử lý nặng hơn việc che giấu**, và điều ngược lại thì có. Người trực hệ thống thật cũng làm đúng như vậy, vì thứ tốn kém nhất trong một sự cố là khoảng thời gian không ai biết chuyện gì đã xảy ra.

## 10. Hệ quả học vụ

Theo quy chế học vụ của UEH về liêm chính học thuật, áp cho mọi bài nộp trong học phần.

## 11. Hệ quả pháp lý

Viết ở dạng nguyên tắc. Bản này cố ý không dẫn số hiệu điều luật, vì tới ngày soạn tài liệu người soạn chưa đọc trực tiếp văn bản hợp nhất từ nguồn chính thức, và dẫn sai một điều luật trong một văn bản sinh viên ký là chuyện không được phép làm cho tiện. Số hiệu sẽ được bổ sung sau khi tra trên nguồn chính thức, kèm ngày truy cập.

Ba nguyên tắc dưới đây không phụ thuộc vào việc tra cứu ấy.

**Ranh giới không nằm ở chỗ bạn có gây thiệt hại hay không, mà nằm ở chỗ bạn có được phép hay không.** Truy cập trái phép vào hệ thống thông tin của người khác là hành vi bị pháp luật Việt Nam điều chỉnh, kể cả khi không có thiệt hại và kể cả khi chỉ để thử.

**Sự cho phép phải có trước, phải bằng văn bản, và phải nói rõ phạm vi.** Lời đồng ý miệng của một người bạn không phải là sự cho phép, vì người ấy thường không phải chủ sở hữu hệ thống.

**Kỹ năng bạn học ở đây có ích ở cả hai phía, và trách nhiệm đi kèm là của bạn.** Học phần dạy phần phòng thủ, đúng một lý do: đó là phần bạn được phép làm ở mọi nơi bạn đi làm sau này.

## 12. Ô ký xác nhận

Tôi đã đọc và hiểu văn bản này, và tôi giữ mọi thao tác của bài S2 trong phạm vi đã ghi.

Họ và tên: ................................  Mã số sinh viên: ....................

Ngày: ....../....../2026   Chữ ký: ................................
