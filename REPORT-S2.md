# Báo cáo Lab S2 — Làm cứng một dịch vụ trên hệ điều hành

**Học phần:** An toàn hệ thống máy tính · Buổi 2 · Bài cá nhân **Họ và tên:** Trương Minh Quân **Mã số sinh viên:** 31241020887 **Ngày nộp:** 22/09/2026

---

## 1. Mục tiêu và bối cảnh

Lab S2 giao một dịch vụ Python đang chạy trong container Debian với cấu hình rộng tay theo mặc định của người đóng gói, yêu cầu thu hẹp quyền của nó rồi đo lại bằng bốn cặp số trước và sau khi làm cứng. Thay vì trả lời câu hỏi "dịch vụ này có cần quyền root không", bài lab buộc trả lời ba câu hỏi cụ thể hơn: tiến trình cần quyền nào, trên tài nguyên nào, và trong khoảng thời gian nào.

Sản phẩm nộp gồm cấu hình đã sửa (`docker-compose.yml`, `dich-vu/Dockerfile`), bốn cặp số đo (`docs/do-luong.yaml`), một bảng ba cột (`docs/bang-lam-cung.md`), và toàn bộ bằng chứng trong `evidence/S02/`.

## 2. Trạng thái khởi đầu — bốn chỗ sai

| Chỗ sai | Nằm ở tệp |
| --- | --- |
| Tiến trình chạy bằng root, giữ toàn bộ tập năng lực mặc định của container | `docker-compose.yml`, `dich-vu/Dockerfile` |
| Hệ tệp gốc ghi được, đường leo quyền qua tệp setuid chưa bị chặn | `docker-compose.yml` |
| Tệp cấu hình `cau-hinh.yaml` để chế độ `666`, mọi tài khoản trong container đều ghi đè được | `dich-vu/Dockerfile` |
| Chương trình `/usr/local/bin/doc-bimat` mang bit setuid của root | `dich-vu/Dockerfile` |

Hai phép thử ở bước `make attack` (chạy dưới tài khoản `sv`, uid 10001) xác nhận cả bốn lỗ hổng này khai thác được trên trạng thái khởi đầu:

- Phép 1 — đọc `/etc/css-s02/bi-mat.txt` qua chương trình setuid `doc-bimat`: **thành công** (mã thoát 0).
- Phép 2 — ghi đè `/etc/css-s02/cau-hinh.yaml`: **thành công** (mã thoát 0).

## 3. Các biện pháp làm cứng đã áp dụng

### 3.1. `docker-compose.yml` — dịch vụ `dichvu`

```yaml
user: "sv"
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
```

- **Bỏ chạy bằng root:** chỉ thị `user: "sv"` buộc tiến trình chạy bằng tài khoản không đặc quyền, uid 10001, thay vì root mặc định.
- **Thu hẹp tập năng lực:** `cap_drop: ALL` bỏ toàn bộ tập năng lực mặc định của container, `cap_add: NET_BIND_SERVICE` chỉ thêm lại đúng một năng lực cần để lắng nghe cổng dưới 1024.
- **Chặn leo quyền qua setuid:** `no-new-privileges:true` chặn toàn bộ cây tiến trình con giành thêm đặc quyền qua bit setuid/setgid, bất kể quyền tệp nhị phân bên trong ảnh.
- **Hệ tệp gốc chỉ đọc:** `read_only: true` khóa toàn bộ hệ tệp gốc, `tmpfs: /tmp` cấp một vùng ghi tạm trong bộ nhớ cho nhu cầu runtime không cần bền vững, và volume `nhat-ky:/var/log/css-s02` (đã khai báo sẵn) là chỗ ghi được duy nhất còn lại, đúng như yêu cầu của bài — không khóa được thư mục nhật ký thì dịch vụ không khởi động, khóa hết thì phép thử ghi đè cấu hình vẫn thành công.

### 3.2. `dich-vu/Dockerfile`

- Bỏ bit setuid của `doc-bimat`: `chmod 0755` thay vì `4755`, nên chương trình không còn tự nâng quyền lên root khi chạy.
- Sửa quyền tệp cấu hình: `cau-hinh.yaml` chuyển từ `666` (mặc định gốc, ai cũng ghi đè được) về `0644`, chỉ còn chủ sở hữu ghi được, nhóm và người khác chỉ đọc.
- Tệp bí mật `bi-mat.txt` giữ nguyên `0600`, chỉ root đọc/ghi được.

## 4. Bốn cặp số đo trước và sau

| Chỉ số | Trước | Sau | Nguồn bằng chứng |
| --- | --- | --- | --- |
| Số năng lực của tiến trình dịch vụ (dòng `Current` của `capsh`) | 14 | 0 | `evidence/S02/capsh-truoc.txt`, `capsh-sau.txt` |
| Chỉ số làm cứng Lynis (`Hardening index`) | 57 | 57 | `evidence/S02/lynis-truoc.txt`, `lynis-sau.txt` |
| Mã thoát thí nghiệm stack protector (`ghi-ten.c`, cùng một chuỗi tràn bộ đệm) | 139 (không bảo vệ, `-fno-stack-protector`) | 134 (có bảo vệ, `-fstack-protector-all`) | `evidence/S02/stack-protector.txt` |
| Hai phép thử tấn công (mã thoát, 0 = thành công) | Phép 1 = 0, Phép 2 = 0 (cả hai thành công) | Phép 1 = 1, Phép 2 = 1 (cả hai thất bại) | `evidence/S02/attack-truoc.txt`, `attack-sau.txt` |

Cổng dịch vụ nghe sau khi làm cứng: **8080** (ánh xạ `127.0.0.1:8080:80`), giữ nguyên cổng trong container là 80 nhưng dựa vào `cap_add: NET_BIND_SERVICE` để bind được cổng đặc quyền mà không cần chạy bằng root.

Bằng chứng runtime khác đi kèm:

- `dich-vu-truoc.txt` → `dich-vu-sau.txt`: đường dẫn `/bi-mat` chuyển từ mã `200` (đọc được) sang mã `403` (bị từ chối), trong khi đường dẫn gốc `/` vẫn trả `200` cả hai lần — dịch vụ còn sống và mất đúng quyền cần mất.
- `quyen-tep-truoc.txt` → `quyen-tep.txt`: `cau-hinh.yaml` từ `666` xuống `644`; `doc-bimat` từ `4755` (mang setuid) xuống `755` (hết setuid); `bi-mat.txt` giữ nguyên `600`.
- `nhat-ky.txt`: có đủ bốn loại sự kiện `khoi_dong`, `yeu_cau`, `leo_quyen`, `tu_choi`, trong đó dòng `leo_quyen` ghi `uid=10001 euid=0` xác nhận đúng thời điểm bước 4 (`make attack`) khai thác setuid thành công trên trạng thái khởi đầu.

### Giải thích chỉ số Lynis không đổi

Lynis quét hệ tệp bên trong ảnh nên chỉ nhìn thấy thay đổi về quyền tệp và bit setuid, không nhìn thấy `cap_drop`, `no-new-privileges` hay `read_only` — ba biện pháp nặng nhất của bài, vì chúng là chỉ thị của Docker Compose chứ không phải trạng thái bên trong hệ tệp ảnh. Giữa hai lần quét, các control tính điểm hardening của Lynis (PAM password strength, fail2ban, auditd, sysstat, malware scanner, AppArmor/SELinux, umask, legal banner, file integrity) vẫn ở trạng thái thiếu như lần đầu; khác biệt duy nhất là một cảnh báo CVE theo snapshot gói tại thời điểm quét, không phải control tính điểm. Vì vậy chỉ số đứng yên ở 57 là kết quả hợp lệ, không phải dấu hiệu làm cứng thất bại.

## 5. Bảng làm cứng — ba cột

| Thay đổi đã làm | Chặn được điều gì, dẫn ATT&CK/CWE | Làm hỏng điều gì (thao tác thủ công/tuần) | Thứ vẫn còn qua được |
| --- | --- | --- | --- |
| `user: sv` (UID 10001) trong `docker-compose.yml`, bỏ chạy bằng root | CWE-250 — tiến trình không còn chạy với quyền root mặc định | Nếu cần cài thêm gói lúc runtime phải rebuild image thay vì `exec` vào sửa trực tiếp | Nếu image base bị compromise ở supply chain (chưa ghim digest), user `sv` vẫn kế thừa lỗ hổng của image |
| `cap_drop: ALL` + `cap_add: NET_BIND_SERVICE`, `no-new-privileges: true` | CWE-1188 — giảm tập capability mặc định; chặn T1548.001 — Setuid | Nếu dịch vụ cần bind thêm cổng đặc quyền khác phải sửa lại `cap_add` | `NET_BIND_SERVICE` vẫn được giữ lại — nếu tiến trình bị chiếm quyền vẫn có thể bind cổng `<1024` |
| `read_only: true` cho root filesystem, chỉ chừa volume `/var/log/css-s02` | Chặn ghi đè tệp cấu hình ở bước attack, liên quan CWE-732 | Mọi thay đổi cấu hình runtime phải qua rebuild/mount lại, không sửa nóng trong container | Thư mục log vẫn ghi được — nếu ứng dụng cho phép ghi tùy ý đường dẫn, đây vẫn là điểm ghi còn mở |
| Bỏ setuid `/usr/local/bin/doc-bimat` (`chmod 0755`), `cau-hinh.yaml` → `0644`, `bi-mat.txt` → `0600` | T1548.001 trực tiếp — chương trình không còn tự nâng quyền root; CWE-732 — tệp cấu hình không còn quyền ghi cho người ngoài owner/group | Nếu `doc-bimat` thực sự cần đọc `bi-mat.txt` hợp lệ về sau, phải thiết kế lại qua group thay vì setuid | Nếu tài khoản `sv` bị chiếm (ví dụ RCE trong `dich-vu.py`), kẻ tấn công vẫn đọc được mọi tệp mà `sv` có quyền đọc |

## 6. Biện pháp đã cân nhắc rồi bỏ

Đã cân nhắc rồi bỏ việc đổi `doc-bimat` sang một chương trình dùng `sudo` có cấu hình giới hạn thay vì chỉ gỡ bit setuid, vì lợi ích thêm được (giữ khả năng đọc tệp bí mật cho một tài khoản bảo trì trong tương lai) không bù nổi chi phí: bài lab hiện tại không có nhu cầu vận hành nào thật sự cần đọc `bi-mat.txt` ngoài hai phép thử tấn công đã đóng gói, nên dựng thêm một cơ chế `sudo` chỉ làm tăng diện tích tấn công (thêm một tệp cấu hình `/etc/sudoers.d` cần bảo vệ) mà không cắt được rủi ro nào đang tồn tại trong phạm vi bài.

## 7. Kết quả bộ kiểm tự động

`make verify` chạy đúng 16 phép kiểm mà GitHub Actions dùng để chấm. Chạy cục bộ trên trạng thái hiện tại của repo (`pytest tests/ -v`), cả 16 phép đều đạt:

| Nhóm | Số phép kiểm | Kết quả |
| --- | --- | --- |
| Môi trường (`preflight.txt`) | 3 | PASSED |
| Cấu hình (`docker-compose.yml`) | 5 | PASSED |
| Bằng chứng (`evidence/S02/`) | 8 | PASSED |

Ba phép kiểm cuối bảng chấm (đếm số từ giải thích Lynis, đủ dòng bảng làm cứng, hai mã thoát khớp nhau) chỉ kiểm được hình thức; phần đúng-sai về nội dung lý luận do người chấm đọc theo `rubric.md`.

## 8. Kết luận

Cả bốn lỗ hổng ban đầu (chạy bằng root, tập năng lực mặc định, hệ tệp ghi được, setuid root) đều đã được vá và chứng minh bằng cặp số đo trước/sau cộng với việc hai phép thử tấn công chuyển từ thành công sang thất bại. Đường vào còn lại rõ nhất sau khi vá là quyền `NET_BIND_SERVICE` vẫn giữ trên tiến trình và việc ảnh nền chưa ghim theo digest, cả hai đã nêu ở cột thứ ba của bảng làm cứng.