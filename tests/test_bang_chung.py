"""Kiểm bằng chứng đo được, tức thứ máy quan sát chứ không phải thứ bạn khai.

Mỗi phép kiểm ở đây đọc một tệp trong evidence/S02 do một mục tiêu của Makefile
sinh ra. Chỗ nào máy không đo được thật thì phép kiểm nói thẳng nó là phép xấp xỉ
và nhường phần còn lại cho người chấm theo rubric.md; không phép nào ở đây giả vờ
đo được chất lượng lập luận.
"""
from __future__ import annotations

import re
from pathlib import Path

from conftest import doc_bang_chung, so_nguyen

NANG_LUC = re.compile(r"cap_[a-z0-9_]+")
CHI_SO_LYNIS = re.compile(r"Hardening index\D{0,20}(\d{1,3})")
MA_CWE_CUA_BUOI = re.compile(r"CWE-(?:250|1188|787|732)\b")
KY_THUAT_ATTACK = "T1548.001"


def _tap_nang_luc(noi_dung: str, ten_tep: str) -> set[str]:
    """Đọc tập năng lực có hiệu lực từ đầu ra của capsh --print.

    capsh viết dòng Current theo hai lối. Lối thường gặp liệt kê từng năng lực;
    lối rút gọn chỉ ghi cờ, ví dụ "Current: =ep", khi tập có hiệu lực trùng với
    trần của tiến trình. Đọc sót lối thứ hai sẽ báo tập rỗng cho một tiến trình
    đang giữ đủ quyền, tức một cáo buộc sai, nên hàm này xử lý cả hai.
    """
    dong_current = ""
    dong_bounding = ""
    for dong in noi_dung.splitlines():
        gon = dong.strip()
        if gon.startswith("Current:") and not dong_current:
            dong_current = gon
        elif gon.startswith("Bounding set") and not dong_bounding:
            dong_bounding = gon
    if not dong_current:
        raise AssertionError(
            "Không thấy dòng Current trong {}. Tệp này phải là đầu ra nguyên vẹn của "
            "capsh --print, đừng chép tay lại.".format(ten_tep)
        )
    tap = set(NANG_LUC.findall(dong_current.lower()))
    if not tap and re.search(r"Current:\s*=\s*[eip]+", dong_current):
        tap = set(NANG_LUC.findall(dong_bounding.lower()))
    return tap


def _ma_thoat(noi_dung: str, khoa: str, ten_tep: str) -> int:
    khop = re.search(re.escape(khoa) + r"=(-?\d+)", noi_dung)
    assert khop, "Không thấy dòng {} trong {}.".format(khoa, ten_tep)
    return int(khop.group(1))


def test_nang_luc_that_su_giam(goc: Path, do_luong: dict) -> None:
    """Bằng chứng trung tâm của buổi học. Trước khi làm cứng, câu hỏi kẻ tấn công
    làm được gì có đáp án là mọi thứ; sau khi làm cứng, đáp án là một danh sách in
    ra được, và danh sách ấy phải ngắn hơn hẳn."""
    truoc = _tap_nang_luc(doc_bang_chung(goc, "capsh-truoc.txt"), "capsh-truoc.txt")
    sau = _tap_nang_luc(doc_bang_chung(goc, "capsh-sau.txt"), "capsh-sau.txt")

    assert len(sau) < len(truoc), (
        "Tập năng lực sau khi làm cứng có {} mục, trước khi làm cứng có {} mục, tức "
        "chưa giảm. Kiểm lại cap_drop trong docker-compose.yml, và nhớ chạy "
        "`make defend` sau khi sửa để số đo lần thứ hai được ghi lại."
        .format(len(sau), len(truoc))
    )
    thua = sau - {"cap_net_bind_service"}
    assert not thua, (
        "Tiến trình còn giữ những năng lực đề bài không cho phép: {}. Chỉ "
        "cap_net_bind_service được giữ lại, và chỉ khi dịch vụ còn nghe cổng dưới "
        "1024.".format(sorted(thua))
    )
    assert so_nguyen(do_luong, "nang_luc_truoc") == len(truoc), (
        "Bạn khai nang_luc_truoc là {} nhưng capsh-truoc.txt đếm được {}."
        .format(do_luong.get("nang_luc_truoc"), len(truoc))
    )
    assert so_nguyen(do_luong, "nang_luc_sau") == len(sau), (
        "Bạn khai nang_luc_sau là {} nhưng capsh-sau.txt đếm được {}."
        .format(do_luong.get("nang_luc_sau"), len(sau))
    )


def test_dich_vu_van_song_va_da_mat_quyen_doc_bi_mat(goc: Path) -> None:
    """Một cấu hình khóa chặt tới mức dịch vụ chết không phải là một cấu hình an
    toàn, nó là một sự cố. Phép kiểm này đòi cả hai vế: dịch vụ còn trả lời, và
    tiến trình dịch vụ đã hết đọc được tệp bí mật."""
    noi_dung = doc_bang_chung(goc, "dich-vu-sau.txt")
    assert re.search(r"duong_dan=/ ma=200", noi_dung), (
        "Sau khi làm cứng, dịch vụ không còn trả 200 ở đường dẫn gốc. Xem "
        "`docker compose logs dichvu`. Hai nguyên nhân thường gặp là quên chừa lối "
        "ghi cho nhật ký, và giữ cổng 80 sau khi đã bỏ hết năng lực."
    )
    assert re.search(r"duong_dan=/bi-mat ma=403", noi_dung), (
        "Đường dẫn /bi-mat chưa trả 403. Trước khi làm cứng nó trả 200, vì dịch vụ "
        "chạy bằng root nên đọc được tệp mà quyền tệp chỉ cho root đọc. Còn 200 "
        "nghĩa là tiến trình vẫn giữ đúng thứ quyền mà bài này bắt bạn bỏ."
    )


def test_duong_leo_quyen_da_bi_chan(goc: Path) -> None:
    """Hai phép thử của `make attack` phải thành công trước khi vá và thất bại sau
    khi vá. Chỉ có cặp trước và sau mới chứng minh được điều gì; một lần chạy lẻ
    thì không."""
    truoc = doc_bang_chung(goc, "attack-truoc.txt")
    sau = doc_bang_chung(goc, "attack-sau.txt")

    for khoa, ten in (
        ("phep_1_doc_bi_mat_qua_setuid", "đọc tệp bí mật qua chương trình setuid"),
        ("phep_2_ghi_de_tep_cau_hinh", "ghi đè tệp cấu hình của dịch vụ"),
    ):
        ma_truoc = _ma_thoat(truoc, khoa, "attack-truoc.txt")
        ma_sau = _ma_thoat(sau, khoa, "attack-sau.txt")
        assert ma_truoc == 0, (
            "Phép thử {} lẽ ra phải THÀNH CÔNG ở trạng thái khởi đầu, nhưng "
            "attack-truoc.txt ghi mã thoát {}. Nhiều khả năng bạn đã sửa cấu hình "
            "rồi mới chạy `make attack`. Xóa evidence/S02, khôi phục trạng thái "
            "khởi đầu, chạy lại theo đúng thứ tự ở README.".format(ten, ma_truoc)
        )
        assert ma_sau != 0, (
            "Phép thử {} vẫn thành công sau khi bạn vá. Nghĩa là đường vào cũ còn "
            "nguyên. Với phép thứ nhất, kiểm no-new-privileges và bit setuid của "
            "/usr/local/bin/doc-bimat; với phép thứ hai, kiểm quyền tệp cấu hình và "
            "chế độ chỉ đọc của hệ tệp gốc.".format(ten)
        )


def test_quyen_tep_va_bit_setuid(goc: Path) -> None:
    """CWE-732 của CWE 4.20, gán quyền sai cho một tài nguyên trọng yếu. Ba dòng
    dưới đây là ba chỗ mà một lệnh chmod viết vội đủ để phá phần còn lại của bài."""
    noi_dung = doc_bang_chung(goc, "quyen-tep.txt")
    quyen: dict[str, str] = {}
    for dong in noi_dung.splitlines():
        phan = dong.split()
        if len(phan) >= 4 and phan[0].isdigit():
            quyen[phan[3]] = phan[0]

    thieu = [t for t in (
        "/etc/css-s02/cau-hinh.yaml",
        "/etc/css-s02/bi-mat.txt",
        "/usr/local/bin/doc-bimat",
    ) if t not in quyen]
    assert not thieu, (
        "quyen-tep.txt không có dòng cho: {}. Chạy lại `make defend`.".format(thieu)
    )

    cau_hinh = quyen["/etc/css-s02/cau-hinh.yaml"]
    assert int(cau_hinh[-1]) & 0o2 == 0, (
        "Tệp cấu hình đang ở chế độ {}, tức mọi người dùng trong container còn ghi "
        "được. Đây là mặc định rộng tay mà mục 2.4 của giáo trình gọi tên, và phép "
        "thử thứ hai của `make attack` khai thác đúng chỗ này.".format(cau_hinh)
    )

    bi_mat = quyen["/etc/css-s02/bi-mat.txt"]
    assert int(bi_mat[-1]) == 0, (
        "Tệp bí mật đang ở chế độ {}, tức người dùng ngoài chủ sở hữu và nhóm còn "
        "đọc hoặc ghi được.".format(bi_mat)
    )

    doc_bimat = quyen["/usr/local/bin/doc-bimat"]
    con_setuid = len(doc_bimat) == 4 and (int(doc_bimat[0]) & 0o4)
    assert not con_setuid, (
        "Chương trình /usr/local/bin/doc-bimat còn mang bit setuid, chế độ {}. "
        "no-new-privileges đã vô hiệu hóa nó lúc chạy, nhưng để nguyên bit ấy trong "
        "ảnh là để lại một đường vào phụ thuộc vào đúng một dòng cấu hình. Bỏ bit "
        "trong dich-vu/Dockerfile.".format(doc_bimat)
    )


def test_nhat_ky_ghi_du_su_kien_da_dinh(goc: Path) -> None:
    """Buổi S7 lấy chính tệp này làm dữ liệu, nên thứ không được ghi hôm nay là thứ
    không truy lại được về sau. Bốn loại sự kiện dưới đây là bốn loại đã định.

    Sự kiện leo_quyen do doc-bimat ghi khi nó chạy với uid hiệu dụng khác uid thật,
    tức khi bit setuid còn hiệu lực. Đây là dòng mà bài S7 yêu cầu tìm lại; thiếu nó
    thì bảng năm sự kiện của S7 mất một dòng trước khi bắt đầu."""
    noi_dung = doc_bang_chung(goc, "nhat-ky.txt")
    thieu = [k for k in ("su_kien=khoi_dong", "su_kien=yeu_cau", "su_kien=leo_quyen",
                         "su_kien=tu_choi")
             if k not in noi_dung]
    assert not thieu, (
        "Nhật ký thiếu các sự kiện {}. Sự kiện leo_quyen chỉ sinh ra khi chạy "
        "`make attack` trên trạng thái khởi đầu. Sự kiện tu_choi chỉ sinh ra sau khi "
        "làm cứng xong, khi hệ điều hành từ chối đọc tệp bí mật. Thứ tự đúng là "
        "`make up`, `make attack`, sửa cấu hình, `make defend`, `make export-evidence`; "
        "đừng xóa volume nhật ký giữa các bước."
        .format(thieu)
    )
    so_dong = len([d for d in noi_dung.splitlines() if "su_kien=" in d])
    assert so_dong >= 3, "Nhật ký chỉ có {} dòng sự kiện, quá ít để đọc.".format(so_dong)


def test_lynis_do_hai_lan_va_giai_thich_chenh_lech(goc: Path, do_luong: dict) -> None:
    """Chỉ số của Lynis là đại lượng thay thế, không phải đại lượng cần tối ưu.

    Vì vậy phép kiểm này KHÔNG đòi chỉ số phải tăng. Nó đòi hai lần đo có thật,
    con số bạn khai khớp với tệp bằng chứng, và bạn giải thích được chênh lệch,
    gồm cả trường hợp chỉ số đứng yên. Chất lượng của lời giải thích thì người
    chấm đọc, theo tiêu chí thứ ba của rubric.md.
    """
    for nhan, ten_tep, khoa in (
        ("trước", "lynis-truoc.txt", "lynis_truoc"),
        ("sau", "lynis-sau.txt", "lynis_sau"),
    ):
        noi_dung = doc_bang_chung(goc, ten_tep)
        khop = CHI_SO_LYNIS.search(noi_dung)
        assert khop, (
            "Không thấy dòng Hardening index trong {}. Tệp phải là đầu ra nguyên vẹn "
            "của Lynis.".format(ten_tep)
        )
        that = int(khop.group(1))
        khai = so_nguyen(do_luong, khoa)
        assert 0 <= khai <= 100, "Khóa {} phải nằm trong khoảng 0 tới 100.".format(khoa)
        assert khai == that, (
            "Bạn khai {} là {} nhưng {} ghi {}. Con số trong bài nộp phải lấy từ tệp "
            "bằng chứng, không lấy từ trí nhớ.".format(khoa, khai, ten_tep, that)
        )

    giai_thich = str(do_luong.get("lynis_giai_thich") or "").strip()
    so_tu = len(giai_thich.split())
    assert so_tu >= 20, (
        "Phần lynis_giai_thich mới có {} từ, cần ít nhất 20. Nói rõ Lynis nhìn thấy "
        "thay đổi nào của bạn, và thay đổi nào nó không nhìn thấy. Đây là phép xấp "
        "xỉ: máy đếm được số từ chứ không đọc được ý, nên đủ dài mà rỗng nghĩa thì "
        "vẫn mất điểm ở phần người chấm.".format(so_tu)
    )


def test_hai_lan_dich_C_cho_hai_ma_thoat(goc: Path, do_luong: dict) -> None:
    """Cùng một tệp nguồn, khác nhau đúng một cờ trình dịch, hai hậu quả khác nhau.

    Bộ kiểm chỉ đòi hai mã thoát khác nhau chứ không đòi một cặp số cụ thể, vì kết
    quả phụ thuộc cách trình dịch xếp khung ngăn xếp. Trong ảnh đã ghim của bài
    này, cặp thường gặp là 7 khi không có bảo vệ và 134 khi có. Nếu máy bạn cho
    một cặp khác thì chính khác biệt ấy là quan sát, và bạn ghi nó vào bảng nộp.
    """
    noi_dung = doc_bang_chung(goc, "stack-protector.txt")
    khong_bao_ve = _ma_thoat(noi_dung, "ma_thoat_khong_bao_ve", "stack-protector.txt")
    co_bao_ve = _ma_thoat(noi_dung, "ma_thoat_co_bao_ve", "stack-protector.txt")

    assert khong_bao_ve != co_bao_ve, (
        "Hai lần dịch cho cùng mã thoát {}, nghĩa là thí nghiệm chưa cho thấy điều "
        "gì. Kiểm lại rằng lần thứ nhất dịch với -fno-stack-protector và lần thứ "
        "hai không, và cả hai chạy với cùng chuỗi đầu vào.".format(khong_bao_ve)
    )
    assert so_nguyen(do_luong, "ma_thoat_khong_bao_ve") == khong_bao_ve, (
        "Số bạn khai không khớp stack-protector.txt."
    )
    assert so_nguyen(do_luong, "ma_thoat_co_bao_ve") == co_bao_ve, (
        "Số bạn khai không khớp stack-protector.txt."
    )


def test_bang_lam_cung_du_dong_va_dan_ma(goc: Path) -> None:
    """Phép xấp xỉ, không phải phép đo thật.

    Máy đếm được số dòng và bắt được ô trống, nhưng nó không đọc được một câu ở
    cột thứ ba là quan sát sắc hay là câu chống chế. Phần ấy người chấm đọc theo
    rubric.md, nên qua được phép kiểm này chưa phải là được điểm phần người chấm.
    """
    tep = goc / "docs" / "bang-lam-cung.md"
    assert tep.exists(), "Không thấy docs/bang-lam-cung.md."
    noi_dung = tep.read_text(encoding="utf-8")

    dong_bang = []
    for dong in noi_dung.splitlines():
        gon = dong.strip()
        if not gon.startswith("|"):
            continue
        o = [x.strip() for x in gon.strip("|").split("|")]
        if len(o) < 4 or set("".join(o)) <= set("-: "):
            continue
        if o[0].lower().startswith("thay đổi đã làm"):
            continue
        dong_bang.append(o)

    day_du = [o for o in dong_bang if all(x and x != "*(điền)*" for x in o[:4])]
    assert len(day_du) >= 4, (
        "Bảng mới có {} dòng điền đủ bốn ô, đề yêu cầu ít nhất 4. Ô hay bị bỏ trống "
        "nhất là ô cuối, tức thứ vẫn còn qua được sau khi đã sửa."
        .format(len(day_du))
    )

    van_ban = "\n".join(" ".join(o) for o in day_du)
    assert KY_THUAT_ATTACK in van_ban, (
        "Không dòng nào dẫn kỹ thuật {} của ATT&CK v19.2. Bài này có đúng một chỗ "
        "chặn nó, và bảng phải nói ra chỗ ấy.".format(KY_THUAT_ATTACK)
    )
    assert MA_CWE_CUA_BUOI.search(van_ban), (
        "Không dòng nào dẫn một mã CWE 4.20 của buổi. Bốn mã đã gắn cho bài lab là "
        "CWE-250, CWE-1188, CWE-787 và CWE-732; dẫn mã nào thì phải đúng chỗ đó."
    )
