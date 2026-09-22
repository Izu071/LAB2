#!/bin/sh
# Dịch cùng một tệp nguồn hai lần, khác nhau đúng một cờ, rồi chạy cả hai với
# cùng một chuỗi đầu vào dài hơn vùng đệm.
#
# Thí nghiệm này không dạy cách khai thác. Nó dạy một điều hẹp hơn và dùng được
# lâu hơn: một cờ trình dịch đổi hẳn hậu quả của cùng một lỗi trong cùng một
# đoạn mã, còn bản thân lỗi thì không tệp cấu hình nào ở mục 2.3 và 2.4 chạm tới.
set -u
NGUON=/usr/local/src/ghi-ten.c
CHUOI="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
THU_MUC="$(mktemp -d)"

echo "lenh_dich_khong_bao_ve=gcc -O0 -fno-stack-protector"
gcc -O0 -fno-stack-protector -o "$THU_MUC/khong-bao-ve" "$NGUON" 2>/dev/null
"$THU_MUC/khong-bao-ve" "$CHUOI" >/dev/null 2>&1
echo "ma_thoat_khong_bao_ve=$?"

echo "lenh_dich_co_bao_ve=gcc -O0 -fstack-protector-all"
gcc -O0 -fstack-protector-all -o "$THU_MUC/co-bao-ve" "$NGUON" 2>/dev/null
"$THU_MUC/co-bao-ve" "$CHUOI" >/dev/null 2>&1
echo "ma_thoat_co_bao_ve=$?"

rm -rf "$THU_MUC"
echo "doc_ky_ket_qua: hai ma thoat khac nhau nghia la co bao ve doi hau qua cua cung mot loi."
