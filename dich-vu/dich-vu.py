#!/usr/bin/env python3
"""Dịch vụ trạng thái của lab S2, cố ý viết ngắn để cấu hình là thứ đáng đọc.

Dịch vụ đọc cổng từ tệp cấu hình, phục vụ hai đường dẫn, và ghi nhật ký ba loại
sự kiện đã định. Ba loại ấy không phải trang trí: buổi S7 lấy chính tệp nhật ký
này làm dữ liệu đầu vào, nên thứ không được ghi hôm nay là thứ không truy lại
được về sau.

    /          trả trạng thái, ghi sự kiện yeu_cau
    /bi-mat    thử đọc tệp bí mật, ghi sự kiện tu_choi khi hệ điều hành từ chối
"""
from __future__ import annotations

import json
import os
import pwd
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CAU_HINH = os.environ.get("CSS_CAU_HINH", "/etc/css-s02/cau-hinh.yaml")
BI_MAT = os.environ.get("CSS_BI_MAT", "/etc/css-s02/bi-mat.txt")
NHAT_KY = os.environ.get("CSS_NHAT_KY", "/var/log/css-s02/dich-vu.log")


def doc_cau_hinh(duong_dan: str) -> dict[str, str]:
    """Đọc tệp khóa và giá trị mỗi dòng một cặp.

    Không dùng thư viện phân giải YAML, vì thứ duy nhất cần đọc ở đây là vài
    cặp khóa và giá trị, và thêm một phụ thuộc vào ảnh chỉ để làm việc đó là
    thêm một thứ phải vá về sau.
    """
    cau_hinh: dict[str, str] = {}
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            for dong in f:
                dong = dong.strip()
                if not dong or dong.startswith("#") or ":" not in dong:
                    continue
                khoa, gia_tri = dong.split(":", 1)
                cau_hinh[khoa.strip()] = gia_tri.strip()
    except OSError as loi:
        ghi_nhat_ky("loi_cau_hinh", f"khong doc duoc {duong_dan}: {loi.strerror}")
    return cau_hinh


def ghi_nhat_ky(su_kien: str, chi_tiet: str) -> None:
    dong = "{} su_kien={} uid={} euid={} chi_tiet={}\n".format(
        time.strftime("%Y-%m-%dT%H:%M:%S%z"), su_kien, os.getuid(), os.geteuid(), chi_tiet
    )
    try:
        os.makedirs(os.path.dirname(NHAT_KY), exist_ok=True)
        with open(NHAT_KY, "a", encoding="utf-8") as f:
            f.write(dong)
        # Ở trạng thái khởi đầu dịch vụ chạy dưới root, nên tệp nhật ký sinh ra sẽ
        # thuộc về root. Tệp này nằm trên một volume còn giữ lại sau khi dựng lại,
        # và dịch vụ sau khi làm cứng chạy dưới sv thì không ghi tiếp được vào một
        # tệp của root. Trao tệp cho sv ngay từ đầu để nhật ký không đứt ở giữa bài.
        if os.geteuid() == 0:
            try:
                sv = pwd.getpwnam("sv")
                os.chown(NHAT_KY, sv.pw_uid, sv.pw_gid)
            except (KeyError, OSError):
                pass
    except OSError as loi:
        # Không ghi được nhật ký thì phải kêu ra đầu ra chuẩn, không nuốt lỗi.
        sys.stderr.write("khong ghi duoc nhat ky: {}\n".format(loi.strerror))
    sys.stdout.write(dong)
    sys.stdout.flush()


class Xu_Ly(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, dinh_dang, *doi_so):  # noqa: N802, ARG002
        return  # nhật ký đi qua ghi_nhat_ky, không đi qua stderr mặc định

    def _tra(self, ma: int, than: dict) -> None:
        goi = json.dumps(than, ensure_ascii=False).encode("utf-8")
        self.send_response(ma)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(goi)))
        self.end_headers()
        self.wfile.write(goi)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/bi-mat"):
            try:
                with open(BI_MAT, "r", encoding="utf-8") as f:
                    f.read()
            except PermissionError:
                ghi_nhat_ky("tu_choi", "doc {} bi he dieu hanh tu choi".format(BI_MAT))
                self._tra(403, {"trang_thai": "tu_choi", "tep": BI_MAT})
                return
            except OSError as loi:
                ghi_nhat_ky("tu_choi", "doc {} that bai: {}".format(BI_MAT, loi.strerror))
                self._tra(403, {"trang_thai": "tu_choi", "tep": BI_MAT})
                return
            ghi_nhat_ky("yeu_cau", "doc duoc {} tu tien trinh dich vu".format(BI_MAT))
            self._tra(200, {"trang_thai": "doc_duoc", "tep": BI_MAT})
            return

        ghi_nhat_ky("yeu_cau", "duong_dan={}".format(self.path))
        self._tra(200, {"trang_thai": "song", "uid": os.geteuid()})


def main() -> int:
    cau_hinh = doc_cau_hinh(CAU_HINH)
    try:
        cong = int(cau_hinh.get("cong", "80"))
    except ValueError:
        cong = 80
    ghi_nhat_ky("khoi_dong", "cong={} cau_hinh={}".format(cong, CAU_HINH))
    try:
        may_chu = ThreadingHTTPServer(("0.0.0.0", cong), Xu_Ly)
    except PermissionError:
        ghi_nhat_ky("loi_mo_cong", "cong={} bi tu choi, tien trinh thieu nang luc".format(cong))
        sys.stderr.write(
            "Khong mo duoc cong {}. Cong duoi 1024 doi nang luc CAP_NET_BIND_SERVICE, "
            "hoac doi cong khac trong tep cau hinh.\n".format(cong)
        )
        return 1
    try:
        may_chu.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
