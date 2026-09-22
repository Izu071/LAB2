# Lab S2. Làm cứng một dịch vụ trên hệ điều hành

**Học phần An toàn hệ thống máy tính · Buổi 2 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: trước giờ buổi S3. Nộp trễ dưới 24 giờ nhận 75 phần trăm số điểm chấm được, trễ từ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0. Mức trừ tăng dần theo thời gian để một sự cố máy móc trong đêm cuối không làm mất trắng cả bài, nhưng cũng không ai được lợi khi nộp sau người khác vài ngày.

## Mục tiêu

Sinh viên nhận một dịch vụ đang chạy với cấu hình rộng, thu hẹp quyền của nó, rồi đo lại bằng bốn cặp số trước và sau.

Mục 2.2 của giáo trình đã chỉ ra rằng câu hỏi "dịch vụ này có cần quyền root không" chỉ có hai câu trả lời, và cả hai đều dẫn tới cấu hình sai. Bài lab thay câu hỏi đó bằng ba câu hỏi trả lời được: tiến trình cần những quyền nào, trên những tài nguyên nào, và trong khoảng thời gian nào. Sản phẩm nộp gồm một tệp cấu hình máy đọc được, bốn cặp số đo, và một bảng ba cột ghi lại cả phần đã chặn được lẫn phần còn chưa chặn được.

Cột thứ ba của bảng, "thứ vẫn còn qua được", là phần được chấm nặng nhất. Người vận hành hệ thống cần biết đường vào nào còn mở sau khi đã vá, và một bảng chỉ liệt kê những gì đã chặn không cho họ biết điều đó.

## Môi trường

Một dịch vụ viết bằng Python chạy trong container Debian, kèm một container kiểm định chạy Lynis trên cùng ảnh. Trạng thái khởi đầu sai ở bốn chỗ, và cả bốn chỗ đều là giá trị mặc định do người đóng gói chọn sẵn.

| Chỗ sai của trạng thái khởi đầu | Nằm ở tệp |
|---|---|
| Tiến trình chạy bằng root, giữ toàn bộ tập năng lực mặc định của container | `docker-compose.yml`, `dich-vu/Dockerfile` |
| Hệ tệp gốc ghi được, và đường leo quyền qua tệp setuid chưa bị chặn | `docker-compose.yml` |
| Tệp cấu hình để chế độ 666, mọi tài khoản trong container đều ghi đè được | `dich-vu/Dockerfile` |
| Chương trình `/usr/local/bin/doc-bimat` mang bit setuid của root | `dich-vu/Dockerfile` |

Lab không chạy `systemd`, `auditd`, `AppArmor` hay `OpenSCAP` bên trong container. `systemd` cần làm tiến trình số 1 của hệ thống, còn ba công cụ kia phụ thuộc vào nhân của máy chủ, nên kết quả sẽ khác nhau giữa máy Windows, máy macOS và máy Linux trong cùng một lớp. Bốn công cụ này được dạy ở phần lý thuyết và có trong ngân hàng câu hỏi.

Phần lưu vết của buổi này dùng nhật ký của chính dịch vụ. Buổi S7 sẽ yêu cầu tìm lại một số sự kiện trong tệp nhật ký này, trong đó có lần leo quyền qua tệp setuid ở bước 4.

## Các bước

Làm theo đúng thứ tự dưới đây. Bốn phép đo đều là phép đo trước và sau khi làm cứng, nên đo sai thứ tự thì cặp số không còn chứng minh được điều gì.

1. **Nhận mã nguồn.** Buổi S2 phát lab dưới dạng tệp nén trên LMS; giải nén và làm ngay trên máy. Sau khi lớp nộp đủ tài khoản GitHub, mỗi sinh viên nhận một kho riêng tư `CSS-26C-Repo`. Khi đó chép toàn bộ thư mục lab vào `bai-nop/S2/` của kho ấy rồi commit, vì bộ chấm trong GitHub Actions chạy các phép kiểm của buổi S2 bên trong đúng thư mục này.
2. `make preflight`. Lệnh ghi kiến trúc CPU, RAM, dung lượng đĩa trống, phiên bản Docker và Python vào `evidence/S02/preflight.txt`. Ảnh của bài này có trình dịch C và Lynis nên nặng hơn ảnh buổi S1; dòng dung lượng đĩa giúp phát hiện sớm máy không đủ chỗ.
3. `make up`. Dịch vụ khởi động ở trạng thái ban đầu và số đo lần thứ nhất được ghi lại. Chạy lại lệnh này sẽ không ghi đè số đo lần thứ nhất. Muốn đo lại từ đầu thì xóa thư mục `evidence/S02` và làm lại từ bước 2.
4. `make attack`. Hai phép thử chạy dưới tài khoản `sv` trong container của chính sinh viên. Phép thứ nhất gọi chương trình setuid để đọc tệp bí mật mà chỉ root được đọc; phép thứ hai ghi thêm một dòng vào tệp cấu hình của dịch vụ. Ở bước này cả hai phép thử phải thành công, vì đó là bằng chứng cấu hình ban đầu hở thật. Phép thứ nhất đồng thời ghi một dòng `su_kien=leo_quyen` vào nhật ký dịch vụ, với `uid` là 10001 và `euid` là 0.
5. `make stack-protector`. Tệp `ghi-ten.c` được dịch hai lần, hai lần chỉ khác nhau ở một cờ của trình dịch, rồi cả hai bản chạy với cùng một chuỗi dài hơn vùng đệm. Làm bước này trước khi làm cứng, vì trình dịch cần ghi tệp tạm lên hệ tệp.
6. **Phần làm cứng.** Sửa `docker-compose.yml` và `dich-vu/Dockerfile` để đạt sáu kết quả dưới đây. Đề bài chỉ nêu kết quả cần đạt, không cho sẵn dòng cấu hình, vì việc tìm đúng tên chỉ thị trong tài liệu gốc là một phần của bài.
   1. Dịch vụ chạy dưới tài khoản không đặc quyền có sẵn trong ảnh, tên `sv`, uid 10001.
   2. Tiến trình bỏ toàn bộ tập năng lực mặc định, rồi chỉ thêm lại năng lực thật sự cần. Được thêm lại nhiều nhất một năng lực là `NET_BIND_SERVICE`, và chỉ khi có lý do để giữ cổng dưới 1024.
   3. Đường leo quyền qua tệp setuid bị chặn cho toàn bộ cây tiến trình con.
   4. Hệ tệp gốc ở chế độ chỉ đọc, nhưng vẫn còn đúng một chỗ ghi được cho `/var/log/css-s02`. Khóa luôn thư mục nhật ký thì dịch vụ không khởi động được; không khóa hệ tệp gốc thì phép thử thứ hai ở bước 4 vẫn thành công sau khi đã vá.
   5. Tệp cấu hình không còn quyền ghi cho ai ngoài chủ sở hữu và nhóm.
   6. Chương trình `doc-bimat` không còn mang bit setuid trong ảnh.
7. `make defend`. Container được dựng lại theo cấu hình đã sửa, số đo lần thứ hai được ghi lại, và hai phép thử ở bước 4 chạy lại. Lần này cả hai phải thất bại. Không xóa volume nhật ký giữa bước 4 và bước 7, vì dòng `leo_quyen` ghi ở bước 4 nằm trong volume đó.
8. Điền `docs/do-luong.yaml` và `docs/bang-lam-cung.md`. Mỗi con số phải lấy từ một tệp trong `evidence/S02`, vì bộ kiểm đối chiếu số khai báo với tệp bằng chứng.
9. `make export-evidence`, rồi `make verify`.
10. Đẩy lên nhánh `main` của kho cá nhân.

## Sản phẩm nộp

```
docker-compose.yml          cấu hình đã làm cứng
dich-vu/Dockerfile          phần sửa quyền tệp và bit setuid
docs/do-luong.yaml          bốn cặp số đo, điền theo bản mẫu có sẵn
docs/bang-lam-cung.md       bảng ba cột, tối thiểu bốn dòng
evidence/S02/               toàn bộ tệp do các mục tiêu trong Makefile sinh ra, kèm SHA256SUMS
```

Thời điểm nộp tính theo dấu thời gian commit trên GitHub.

Tệp `evidence/S02/nhat-ky.txt` cần được commit cùng bài nộp. Buổi S7 dùng tệp này làm dữ liệu đầu vào. Sinh viên làm mất tệp sẽ dùng bộ dữ liệu thay thế do giảng viên phát ở buổi S7, và bài S7 khi đó được ghi chú là chạy trên dữ liệu thay thế.

## Các phép kiểm của máy chấm

`make verify` chạy đúng mười sáu phép kiểm mà GitHub Actions chạy khi chấm, không thêm phép nào, nên sinh viên tự kiểm được trước khi nộp.

| Nhóm | Phép kiểm | Đạt khi |
|---|---|---|
| Môi trường | ba phép trên `preflight.txt` | ghi đủ các mục, Docker có mặt và daemon đang chạy |
| Cấu hình | dịch vụ không chạy bằng root | có chỉ thị người chạy, và uid khác 0 |
| Cấu hình | bỏ hết năng lực rồi thêm lại năng lực cần | `cap_drop` có `ALL`, phần thêm lại nằm trong danh sách đề bài cho phép |
| Cấu hình | chặn leo quyền qua setuid | có `no-new-privileges` với giá trị đúng |
| Cấu hình | hệ tệp gốc chỉ đọc và vẫn ghi được nhật ký | có chế độ chỉ đọc, và có một chỗ ghi cho `/var/log/css-s02` |
| Cấu hình | không vượt ràng buộc cưỡng chế | không `privileged`, không dùng mạng của máy chủ, không tắt cơ chế cách ly, mọi cổng ánh xạ về `127.0.0.1` |
| Bằng chứng | tập năng lực thật sự giảm | tập trên dòng `Current` của `capsh` lần sau nhỏ hơn lần trước, và số khai báo khớp tệp |
| Bằng chứng | dịch vụ còn chạy và đã mất quyền đọc tệp bí mật | đường dẫn gốc trả 200, đường dẫn `/bi-mat` trả 403 |
| Bằng chứng | đường leo quyền đã bị chặn | hai phép thử thành công trước khi vá và thất bại sau khi vá |
| Bằng chứng | quyền tệp và bit setuid | tệp cấu hình hết quyền ghi cho người ngoài, tệp bí mật kín, `doc-bimat` hết setuid |
| Bằng chứng | nhật ký có đủ bốn loại sự kiện | có `khoi_dong`, `yeu_cau`, `leo_quyen`, `tu_choi` |
| Bằng chứng | Lynis đo hai lần và có giải thích | hai chỉ số khớp hai tệp Lynis, phần giải thích dài từ 20 từ trở lên |
| Bằng chứng | hai lần dịch cho hai mã thoát | hai mã khác nhau, và khớp số khai báo |
| Bằng chứng | bảng làm cứng đủ dòng và có dẫn mã | ít nhất bốn dòng điền đủ ô, có dẫn T1548.001 và một mã CWE của buổi |

Ba phép kiểm cuối bảng chỉ kiểm được hình thức. Máy đếm được số từ trong phần giải thích chỉ số Lynis, đếm được số dòng của bảng và phát hiện ô trống, so được hai mã thoát, nhưng không đánh giá được lời giải thích có đúng hay không. Phần đó do người chấm đọc theo `rubric.md`, nên qua được máy chấm chưa có nghĩa là đạt điểm phần người chấm.

Chỉ số Lynis còn một giới hạn cần biết trước khi đo. Lynis quét hệ tệp bên trong ảnh, nên nó thấy thay đổi về quyền tệp và bit setuid, nhưng không thấy `cap_drop`, `no-new-privileges` hay chế độ chỉ đọc, tức ba thay đổi quan trọng nhất của bài. Vì vậy chỉ số đứng yên sau khi làm đúng là kết quả hợp lệ, và phần giải thích khoảng cách này được tính điểm theo rubric.

## Tiêu chí đạt

Máy chấm báo xanh, và bảng làm cứng có ít nhất một dòng ở cột thứ ba chỉ ra một đường vào còn lại sau khi đã vá.

## Khi gặp khó khăn

Đọc `SCOPE.md` trước khi làm bước 4. Bài có phần tấn công, và phạm vi ghi trong tệp đó là điều kiện bắt buộc của bài.

Dịch vụ không khởi động sau khi làm cứng: xem `docker compose logs dichvu`. Phần lớn trường hợp rơi vào một trong hai nguyên nhân, hoặc chưa chừa chỗ ghi cho thư mục nhật ký, hoặc vẫn giữ cổng 80 sau khi đã bỏ hết năng lực.

Máy không chạy được Docker: báo giảng viên chậm nhất hai ngày trước buổi S3, kèm tệp `evidence/S02/preflight.txt`. Có phương án thay thế, nhưng phương án đó cần thời gian chuẩn bị.
#   L A B 2  
 