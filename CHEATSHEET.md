# Thẻ tham chiếu, lab S2

Mười hai lệnh, mỗi lệnh một dòng nghĩa và một dòng hậu quả nếu gõ sai. Thẻ này thay việc tra lại tài liệu giữa buổi, không thay việc đọc README.

| Lệnh | Nghĩa | Gõ sai thì sao |
|---|---|---|
| `make preflight` | Ghi thông tin máy vào `evidence/S02/preflight.txt` | Không có tệp này thì ba phép kiểm đầu đỏ |
| `make up` | Dựng dịch vụ ở trạng thái khởi đầu, đo lần thứ nhất | Chạy sau khi đã sửa cấu hình thì số đo lần thứ nhất không còn là trạng thái khởi đầu, phải xóa `evidence/S02` làm lại |
| `make attack` | Hai phép thử dưới người dùng `sv` | Chạy sau khi đã vá thì cả hai thất bại, và bộ kiểm báo bạn chạy sai thứ tự |
| `make stack-protector` | Dịch `ghi-ten.c` hai lần, ghi hai mã thoát | Chạy sau khi đã đặt hệ tệp chỉ đọc thì trình dịch không ghi được tệp tạm |
| `make defend` | Dựng lại theo cấu hình đã sửa, đo lần thứ hai | Quên chạy thì mọi phép kiểm về bằng chứng lần thứ hai đều đỏ |
| `make verify` | Chạy đúng bộ kiểm mà bộ chấm chạy | Không có gì hỏng, chạy bao nhiêu lần cũng được |
| `make export-evidence` | Lấy nhật ký ra khỏi container, ghi `SHA256SUMS` | Quên chạy thì thiếu `nhat-ky.txt`, và buổi S7 thiếu dữ liệu |
| `make down` | Xóa container, mạng, ổ lưu; giữ `evidence/S02` | Chạy trước `export-evidence` thì mất nhật ký, phải làm lại từ `make up` |
| `docker compose logs dichvu` | Đọc nhật ký khởi động của dịch vụ | Lệnh chỉ đọc, không hỏng gì |
| `docker compose exec -u sv dichvu capsh --print` | Xem tập năng lực thật của tiến trình | Bỏ `-u sv` thì bạn đang xem tiến trình của root, không phải của dịch vụ |
| `docker compose exec dichvu stat -c '%a %U %n' <tệp>` | Xem quyền và chủ sở hữu một tệp | Xem trên máy bạn thay vì trong container thì đọc nhầm tệp |
| `bash ghim-digest.sh` | Xem trước việc thay thẻ bằng digest, chưa sửa gì | Thêm `--sua` mới ghi vào tệp, và có giữ bản `.bak` |
