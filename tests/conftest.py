"""Đường dẫn gốc và các hàm đọc dùng chung cho bộ kiểm công khai của lab S2.

Gốc lấy từ biến môi trường LAB_ROOT nếu có, nếu không thì lấy thư mục cha của
thư mục tests. Biến ấy tồn tại vì kho nội bộ chạy chính bộ kiểm này lên hai bản
mẫu, một bản đạt và một bản trượt, để biết bộ chấm có bắt được lỗi hay không.
Sinh viên không cần đặt biến ấy bao giờ.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

try:
    import yaml
except ImportError:  # pragma: no cover
    pytest.skip("Thiếu PyYAML, cài bằng: pip3 install pyyaml", allow_module_level=True)


def _goc() -> Path:
    duong_dan = os.environ.get("LAB_ROOT")
    if duong_dan:
        return Path(duong_dan).resolve()
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def goc() -> Path:
    return _goc()


@pytest.fixture(scope="session")
def compose(goc: Path) -> dict:
    tep = goc / "docker-compose.yml"
    if not tep.exists():
        pytest.fail("Không thấy docker-compose.yml ở gốc kho bài nộp.")
    try:
        du_lieu = yaml.safe_load(tep.read_text(encoding="utf-8"))
    except yaml.YAMLError as loi:
        pytest.fail(
            "docker-compose.yml không phân giải được nên không phép kiểm nào sau đó "
            "còn ý nghĩa. Lỗi YAML: {}".format(loi)
        )
    if not isinstance(du_lieu, dict) or "services" not in du_lieu:
        pytest.fail("docker-compose.yml không có khối services.")
    return du_lieu


@pytest.fixture(scope="session")
def dich_vu(compose: dict) -> dict:
    services = compose["services"]
    if "dichvu" not in services:
        pytest.fail(
            "Không thấy dịch vụ tên dichvu trong docker-compose.yml. Đừng đổi tên "
            "dịch vụ, vì bộ chấm và các tập lệnh đo đều gọi theo tên đó."
        )
    return services["dichvu"] or {}


@pytest.fixture(scope="session")
def do_luong(goc: Path) -> dict:
    tep = goc / "docs" / "do-luong.yaml"
    if not tep.exists():
        pytest.fail("Không thấy docs/do-luong.yaml. Điền bản mẫu có sẵn trong kho.")
    du_lieu = yaml.safe_load(tep.read_text(encoding="utf-8"))
    if not isinstance(du_lieu, dict):
        pytest.fail("docs/do-luong.yaml rỗng hoặc không phải một bảng khóa và giá trị.")
    return du_lieu


def doc_bang_chung(goc: Path, ten: str) -> str:
    """Đọc một tệp trong evidence/S02, và nói rõ lệnh nào sinh ra nó khi thiếu."""
    lenh_sinh_ra = {
        "preflight.txt": "make preflight",
        "capsh-truoc.txt": "make up",
        "quyen-tep-truoc.txt": "make up",
        "dich-vu-truoc.txt": "make up",
        "lynis-truoc.txt": "make up",
        "attack-truoc.txt": "make attack",
        "capsh-sau.txt": "make defend",
        "quyen-tep.txt": "make defend",
        "dich-vu-sau.txt": "make defend",
        "lynis-sau.txt": "make defend",
        "attack-sau.txt": "make defend",
        "stack-protector.txt": "make stack-protector",
        "nhat-ky.txt": "make export-evidence",
    }
    tep = goc / "evidence" / "S02" / ten
    if not tep.exists():
        pytest.fail(
            "Không thấy evidence/S02/{}. Tệp này do lệnh `{}` sinh ra; chạy lệnh đó "
            "rồi commit tệp cùng bài nộp.".format(ten, lenh_sinh_ra.get(ten, "make up"))
        )
    return tep.read_text(encoding="utf-8", errors="replace")


def so_nguyen(du_lieu: dict, khoa: str) -> int:
    gia_tri = du_lieu.get(khoa)
    if gia_tri is None:
        pytest.fail(
            "docs/do-luong.yaml chưa điền khóa {}. Bản mẫu ghi rõ lấy con số ấy ở "
            "tệp bằng chứng nào.".format(khoa)
        )
    try:
        return int(gia_tri)
    except (TypeError, ValueError):
        pytest.fail(
            "Khóa {} trong docs/do-luong.yaml phải là một số nguyên, đang là {!r}."
            .format(khoa, gia_tri)
        )
    raise AssertionError  # không tới được, giữ cho công cụ kiểm kiểu yên tâm
