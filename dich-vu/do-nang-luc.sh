#!/bin/sh
# In tập năng lực thật của tiến trình đang chạy trong container.
#
# Đây là bằng chứng bạn nộp, không phải lời bạn khai. Dòng Current là tập năng
# lực có hiệu lực; dòng Bounding set là trần mà tiến trình không vượt qua được.
set -u
echo "nguoi_chay=$(id -un) uid=$(id -u)"
capsh --print
