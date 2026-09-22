#!/bin/sh
# Gọi hai đường dẫn của dịch vụ và in mã trạng thái HTTP.
#
# Phép thử này trả lời câu hỏi mà mọi lần làm cứng đều phải trả lời: dịch vụ còn
# làm được việc của nó hay không. Một cấu hình an toàn tuyệt đối mà dịch vụ chết
# thì không phải là một cấu hình an toàn, nó là một sự cố.
set -u
# Cổng lấy từ chính tệp cấu hình của dịch vụ, để phép thử không lệch khỏi thứ
# dịch vụ đang nghe khi bạn đổi cổng trong lúc làm cứng.
if [ "$#" -ge 1 ]; then
    CONG="$1"
else
    CONG="$(sed -n 's/^cong:[[:space:]]*//p' /etc/css-s02/cau-hinh.yaml | head -n 1)"
    CONG="${CONG:-80}"
fi
python3 - "$CONG" <<'PYEOF'
import sys
import urllib.error
import urllib.request

cong = sys.argv[1]
for duong_dan in ("/", "/bi-mat"):
    dia_chi = "http://127.0.0.1:{}{}".format(cong, duong_dan)
    try:
        with urllib.request.urlopen(dia_chi, timeout=5) as tra_loi:
            ma = tra_loi.status
    except urllib.error.HTTPError as loi:
        ma = loi.code
    except OSError as loi:
        print("duong_dan={} ma=KHONG_KET_NOI chi_tiet={}".format(duong_dan, loi))
        continue
    print("duong_dan={} ma={}".format(duong_dan, ma))
PYEOF
