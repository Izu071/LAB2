#!/usr/bin/env bash
# Thay thẻ phiên bản bằng digest thật, cho lab S2.
#
# Vì sao có tệp này. Một thẻ như debian:bookworm-slim trỏ sang ảnh khác bất cứ
# lúc nào mà không ai báo, nên bài bạn chạy hôm nay và bài bộ chấm chạy tuần sau
# có thể đứng trên hai hệ điều hành khác nhau. Digest là băm nội dung, nên nó chỉ
# về đúng một ảnh và mãi mãi về đúng ảnh ấy.
#
# Máy soạn bài không kéo được ảnh nên không lấy được digest thật, và một chuỗi
# sha256 gõ tay là một chuỗi bịa. Tập lệnh này chạy trên máy CÓ MẠNG, hỏi sổ đăng
# ký, rồi sửa thẳng vào tệp. Nó không bao giờ tự sinh ra một digest.
#
#   bash ghim-digest.sh            xem trước, không sửa gì
#   bash ghim-digest.sh --sua      sửa thật, có giữ bản sao .bak
#
# Mã thoát: 0 xong, 1 có dòng không giải được, 2 sai tham số hoặc thiếu docker.

set -euo pipefail

GOC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEP=("$GOC/docker-compose.yml" "$GOC/dich-vu/Dockerfile")

# Ảnh dựng tại chỗ từ ./dich-vu. Chúng không nằm trong sổ đăng ký nào nên không
# có digest để hỏi, và bỏ qua chúng là đúng chứ không phải là nhân nhượng.
ANH_DUNG_TAI_CHO='^css-s02-'

SUA=0
case "${1:-}" in
  "")      SUA=0 ;;
  --sua)   SUA=1 ;;
  *)       echo "Dùng: bash ghim-digest.sh [--sua]" >&2; exit 2 ;;
esac

if ! command -v docker >/dev/null 2>&1; then
  echo "Không có docker trên máy này. Chạy tập lệnh trên máy có mạng và có docker." >&2
  exit 2
fi

lay_digest() {
  local ref="$1" d=""
  d="$(docker buildx imagetools inspect --format '{{.Manifest.Digest}}' "$ref" 2>/dev/null || true)"
  if [[ -z "$d" ]]; then
    docker pull --quiet "$ref" >/dev/null 2>&1 || return 1
    d="$(docker image inspect --format '{{index .RepoDigests 0}}' "$ref" 2>/dev/null || true)"
    d="${d##*@}"
  fi
  [[ "$d" == sha256:* ]] || return 1
  printf '%s' "$d"
}

hong=0
sua_duoc=0

for tep in "${TEP[@]}"; do
  [[ -f "$tep" ]] || { echo "Không thấy $tep" >&2; exit 2; }
  echo "== $tep"

  # Lấy mọi tham chiếu ảnh dạng ten:the, ở cả dòng FROM lẫn dòng image.
  refs="$(grep -Eo '^[[:space:]]*(FROM|image:)[[:space:]]+[^[:space:]]+' "$tep" \
          | awk '{print $2}' | sort -u || true)"

  [[ -n "$refs" ]] || { echo "  (không có dòng ảnh nào)"; continue; }

  while IFS= read -r ref; do
    [[ -n "$ref" ]] || continue
    if [[ "$ref" == *"@sha256:"* ]]; then
      echo "  ĐÃ GHIM   $ref"
      continue
    fi
    if [[ "$ref" =~ $ANH_DUNG_TAI_CHO ]]; then
      echo "  BỎ QUA    $ref (ảnh dựng tại chỗ, không có trong sổ đăng ký)"
      continue
    fi

    if ! digest="$(lay_digest "$ref")"; then
      echo "  KHÔNG GIẢI ĐƯỢC  $ref. Kiểm mạng và tên ảnh, đừng gõ tay digest." >&2
      hong=$((hong + 1))
      continue
    fi

    ten="${ref%%:*}"
    moi="$ten@$digest"
    truoc="$(grep -c -F -- "$ref" "$tep" || true)"
    echo "  $ref"
    echo "    -> $moi  ($truoc dòng)"

    if (( SUA == 1 )); then
      cp -f "$tep" "$tep.bak"
      # Thay đúng chuỗi, không dùng biểu thức chính quy, để không trúng nhầm chỗ.
      python3 - "$tep" "$ref" "$moi" <<'PYEOF'
import sys
tep, cu, moi = sys.argv[1], sys.argv[2], sys.argv[3]
with open(tep, encoding="utf-8") as f:
    noi_dung = f.read()
so = noi_dung.count(cu)
if so == 0:
    sys.stderr.write("phep thay the truot dich: khong thay {!r} trong {}\n".format(cu, tep))
    raise SystemExit(1)
with open(tep, "w", encoding="utf-8") as f:
    f.write(noi_dung.replace(cu, moi))
print("    đã thay {} chỗ".format(so))
PYEOF
      sau="$(grep -c -F -- "$ref" "$tep" || true)"
      if [[ "$sau" != "0" ]]; then
        echo "    PHÉP THAY THẾ TRƯỢT ĐÍCH, còn $sau dòng mang thẻ cũ." >&2
        hong=$((hong + 1))
      else
        sua_duoc=$((sua_duoc + 1))
      fi
    fi
  done <<< "$refs"
done

echo
if (( SUA == 0 )); then
  echo "Đây là lượt xem trước, chưa sửa gì. Chạy lại với --sua để ghi vào tệp."
else
  echo "Đã ghim $sua_duoc tham chiếu. Bản cũ giữ ở các tệp .bak."
  echo "Sau khi ghim: xóa dòng chú thích CHUA_GHIM_DIGEST tương ứng, dựng lại bằng"
  echo "make down && make up, rồi chạy make verify."
fi
if (( hong > 0 )); then
  echo "Còn $hong dòng chưa ghim được. Đây là lỗi chặn, không phải cảnh báo." >&2
  exit 1
fi
exit 0
