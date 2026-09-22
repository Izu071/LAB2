#!/bin/sh
# Phép chứng minh một bước của bài S2, chạy trong container của chính bạn.
#
# Hai phép thử, mỗi phép một mã thoát, không phép nào nối sang phép nào. Mức tấn
# công cho phép của học phần dừng ở đây: chứng minh một cấu hình sai cụ thể dẫn
# tới truy cập trái phép, rồi bắt buộc vá và chứng minh vá xong nó thất bại.
#
# Phép 1 gọi chương trình setuid để đọc tệp bí mật mà quyền tệp chỉ cho root đọc.
# Phép 2 ghi thêm một dòng vào tệp cấu hình của dịch vụ.
set -u

echo "nguoi_chay=$(id -un) uid=$(id -u)"

/usr/local/bin/doc-bimat >/dev/null 2>&1
ma1=$?
echo "phep_1_doc_bi_mat_qua_setuid=$ma1"

if echo "# dong nay do phep thu 2 ghi vao" >>/etc/css-s02/cau-hinh.yaml 2>/dev/null; then
    ma2=0
else
    ma2=1
fi
echo "phep_2_ghi_de_tep_cau_hinh=$ma2"

echo "doc_ky_ket_qua: ma thoat 0 nghia la phep thu thanh cong, tuc cau hinh dang cho phep."
