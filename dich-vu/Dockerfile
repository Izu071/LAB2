# Ảnh của dịch vụ, ở TRẠNG THÁI KHỞI ĐẦU cố ý cấu hình rộng tay.
#
# Đọc tệp này trước khi sửa dòng nào. Bốn chỗ dưới đây là bốn quyết định đã có
# người ra thay bạn, và việc của bài lab là xem lại từng quyết định ấy:
#   1. không có chỉ thị USER, nên tiến trình chạy bằng root;
#   2. tệp cấu hình để chế độ 666, nghĩa là ai cũng ghi đè được;
#   3. chương trình doc-bimat mang bit setuid của root;
#   4. dịch vụ nghe cổng 80, một cổng đặc quyền, nên nó lấy quyền root làm điều
#      kiện để chạy được.
#
# CHUA_GHIM_DIGEST: dòng FROM dưới đây ghim theo thẻ, chưa ghim theo digest. Chạy
# ghim-digest.sh trên máy có mạng để thay thẻ bằng digest thật. Không tự gõ một
# chuỗi sha256 vào đây.
FROM debian:bookworm-slim

# Gói cài bằng apt chưa ghim theo phiên bản chính xác, vì kho Debian đổi phiên
# bản vá theo thời gian và người soạn chưa đọc được danh sách phiên bản hiện có
# trên kho tại thời điểm soạn. Ảnh ghi lại phiên bản thật lúc dựng vào
# /etc/css-s02/phien-ban-goi.txt để bài nộp truy ngược được, và việc ghim đủ nằm
# ở phần còn ngờ của lab.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
      python3 \
      gcc \
      libc6-dev \
      libcap2-bin \
      lynis \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --system --uid 10001 --create-home --shell /usr/sbin/nologin sv

WORKDIR /usr/local/src
COPY doc-bimat.c ghi-ten.c ./
RUN gcc -O2 -o /usr/local/bin/doc-bimat doc-bimat.c \
 && chown root:root /usr/local/bin/doc-bimat \
 && chmod 0755 /usr/local/bin/doc-bimat

COPY dich-vu.py /usr/local/bin/dich-vu.py
COPY thu-leo-quyen.sh do-nang-luc.sh do-quyen-tep.sh thu-dich-vu.sh \
     thu-stack-protector.sh /usr/local/bin/
RUN chmod 0755 /usr/local/bin/dich-vu.py /usr/local/bin/*.sh

RUN mkdir -p /etc/css-s02 /var/log/css-s02 \
 && chown sv:sv /var/log/css-s02 \
 && chmod 0755 /var/log/css-s02
COPY cau-hinh.yaml /etc/css-s02/cau-hinh.yaml
RUN printf 'khoa-phien-ban-thu-nghiem-cua-lab-S02\n' > /etc/css-s02/bi-mat.txt \
 && chown root:root /etc/css-s02/bi-mat.txt \
 && chmod 0600 /etc/css-s02/bi-mat.txt \
 && chown root:root /etc/css-s02/cau-hinh.yaml \
 && chmod 0644 /etc/css-s02/cau-hinh.yaml \
 && { echo "ngay dung anh: ghi luc build"; \
      dpkg-query -W -f='${binary:Package} ${Version}\n' python3 gcc libc6-dev libcap2-bin lynis; \
    } > /etc/css-s02/phien-ban-goi.txt

EXPOSE 80
CMD ["python3", "/usr/local/bin/dich-vu.py"]
