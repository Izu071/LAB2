"""Kiểm chính tệp cấu hình bạn nộp, chứ không kiểm lời bạn kể về nó.

Năm phép kiểm dưới đây đọc docker-compose.yml. Bốn phép đầu hỏi bạn đã thu hẹp
dịch vụ tới đâu; phép thứ năm hỏi bạn có còn nằm trong phạm vi được phép của học
phần hay không, và nó áp cho mọi dịch vụ trong tệp chứ không riêng dịch vụ chính.

Một tệp cấu hình đúng mà bài không chạy thì các phép kiểm ở test_bang_chung.py
bắt được, nên hai nhóm phép kiểm này không thay nhau được: nhóm này đọc ý định,
nhóm kia đọc kết quả.
"""
from __future__ import annotations

NANG_LUC_CHO_PHEP = {"NET_BIND_SERVICE"}


def _chuan_hoa(ten: str) -> str:
    ten = str(ten).strip().upper()
    return ten[4:] if ten.startswith("CAP_") else ten


def _danh_sach(khoi: dict, khoa: str) -> list[str]:
    gia_tri = khoi.get(khoa) or []
    if isinstance(gia_tri, str):
        return [gia_tri]
    return [str(x) for x in gia_tri]


def test_dich_vu_khong_chay_bang_root(dich_vu: dict) -> None:
    """Câu hỏi mở đầu buổi học là dịch vụ này có cần quyền root không, và đây là
    chỗ bạn trả lời bằng một dòng cấu hình thay vì bằng một ý kiến."""
    nguoi_chay = str(dich_vu.get("user", "")).strip()
    assert nguoi_chay, (
        "Dịch vụ dichvu chưa khai người chạy, nên nó chạy bằng root theo mặc định "
        "của ảnh. Thêm chỉ thị user cho dịch vụ, dùng đúng tài khoản đã có sẵn "
        "trong ảnh là sv, uid 10001."
    )
    assert nguoi_chay.split(":")[0] not in ("0", "root"), (
        "Dịch vụ vẫn chạy bằng root, chỉ là khai tường minh hơn. Đổi sang tài khoản "
        "không đặc quyền."
    )


def test_bo_het_nang_luc_va_chi_them_lai_cai_can(dich_vu: dict) -> None:
    """Bỏ hết rồi thêm lại đúng cái cần là thứ tự đúng. Thứ tự ngược lại, tức bỏ
    dần những cái trông có vẻ nguy hiểm, để lại một tập không ai nói được vì sao
    nó có mặt."""
    bo = {_chuan_hoa(x) for x in _danh_sach(dich_vu, "cap_drop")}
    them = {_chuan_hoa(x) for x in _danh_sach(dich_vu, "cap_add")}

    assert "ALL" in bo, (
        "Dịch vụ chưa bỏ trọn tập năng lực mặc định. Khai cap_drop với ALL, rồi mới "
        "thêm lại đúng năng lực dịch vụ cần."
    )
    thua = them - NANG_LUC_CHO_PHEP
    assert not thua, (
        "Đề bài chỉ cho phép thêm lại {}. Bạn đang thêm {}, và mỗi năng lực thừa là "
        "một phần quyền root bạn vừa cấp lại mà không có lý do trong bảng nộp."
        .format(sorted(NANG_LUC_CHO_PHEP), sorted(thua))
    )


def test_chan_leo_quyen_qua_setuid(dich_vu: dict) -> None:
    """Đây là dòng chặn kỹ thuật T1548.001 của ATT&CK v19.2, và nó chặn cho cả cây
    tiến trình con chứ không riêng tiến trình đầu."""
    tuy_chon = [str(x).replace(" ", "").lower() for x in _danh_sach(dich_vu, "security_opt")]
    assert any(x.startswith("no-new-privileges") and x.endswith("true") for x in tuy_chon), (
        "Dịch vụ chưa đặt no-new-privileges. Thiếu nó thì một tệp setuid trong ảnh "
        "vẫn nâng được quyền của tiến trình con, và phép thử thứ nhất của "
        "`make attack` vẫn chạy thành công sau khi bạn đã vá."
    )


def test_he_tep_goc_chi_doc_va_van_ghi_duoc_nhat_ky(dich_vu: dict) -> None:
    """Hai vế của cùng một yêu cầu. Khóa hệ tệp mà quên chừa chỗ ghi nhật ký thì
    dịch vụ chết, và buổi S7 mất dữ liệu đầu vào của nó."""
    assert dich_vu.get("read_only") is True, (
        "Hệ tệp gốc của dịch vụ vẫn ghi được. Đặt read_only cho dịch vụ, rồi mở "
        "riêng đúng những đường dẫn cần ghi."
    )
    duong_ghi = _danh_sach(dich_vu, "volumes") + list((dich_vu.get("tmpfs") or []))
    assert any("/var/log/css-s02" in str(x) for x in duong_ghi), (
        "Không thấy lối ghi nào cho /var/log/css-s02. Hệ tệp chỉ đọc mà không chừa "
        "chỗ cho nhật ký thì dịch vụ không ghi được dòng nào, và bài S7 lấy chính "
        "tệp nhật ký này làm dữ liệu."
    )


def test_khong_vuot_rang_buoc_cuong_che(compose: dict) -> None:
    """Phép kiểm này không đo kỹ năng làm cứng. Nó cưỡng chế phạm vi cho phép ở
    SCOPE.md, nên nó áp cho mọi dịch vụ trong tệp, kể cả container kiểm định."""
    loi: list[str] = []
    for ten, khoi in (compose.get("services") or {}).items():
        khoi = khoi or {}

        if khoi.get("privileged"):
            loi.append("{}: đặt privileged, thứ vô hiệu hóa gần hết ranh giới của container".format(ten))
        if str(khoi.get("network_mode", "")).strip() == "host":
            loi.append("{}: dùng network_mode host, tức bỏ mạng riêng của lab".format(ten))
        if str(khoi.get("pid", "")).strip() == "host":
            loi.append("{}: dùng pid host, tức nhìn thẳng vào tiến trình của máy bạn".format(ten))

        for tuy_chon in _danh_sach(khoi, "security_opt"):
            gon = str(tuy_chon).replace(" ", "").lower()
            if "unconfined" in gon:
                loi.append("{}: tắt một cơ chế cách ly bằng {}".format(ten, tuy_chon))

        for cong in _danh_sach(khoi, "ports"):
            if not str(cong).startswith("127.0.0.1:"):
                loi.append(
                    "{}: ánh xạ cổng {} ra mọi giao diện mạng. Mọi cổng phải bắt đầu "
                    "bằng 127.0.0.1: để dịch vụ chỉ nghe trên máy bạn".format(ten, cong)
                )

        thua = {_chuan_hoa(x) for x in _danh_sach(khoi, "cap_add")} - NANG_LUC_CHO_PHEP
        if thua:
            loi.append("{}: thêm năng lực ngoài danh sách đề bài cho phép: {}".format(ten, sorted(thua)))

    assert not loi, (
        "Cấu hình vượt phạm vi cho phép của học phần:\n  " + "\n  ".join(loi)
        + "\nĐây là lỗi chặn chứ không phải lỗi trừ điểm: đọc lại SCOPE.md."
    )
