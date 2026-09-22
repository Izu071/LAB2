#!/bin/sh
# Ghi lại quyền của bốn tệp mà bài lab quan tâm, theo dạng máy đọc được.
#
# Cột thứ nhất là quyền theo hệ tám, và một số bốn chữ số bắt đầu bằng 4 nghĩa là
# tệp còn mang bit setuid.
set -u
for t in /etc/css-s02/cau-hinh.yaml /etc/css-s02/bi-mat.txt \
         /usr/local/bin/doc-bimat /var/log/css-s02; do
    if [ -e "$t" ]; then
        stat -c '%a %U %G %n' "$t"
    else
        echo "KHONG_TON_TAI $t"
    fi
done
echo "-- nang luc gan tren tep --"
getcap -r /usr/local/bin /usr/bin 2>/dev/null || echo "(khong co tep nao mang nang luc)"
