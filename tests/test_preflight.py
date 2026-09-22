"""Kiểm tệp preflight, tức bằng chứng môi trường của sinh viên thật sự chạy.

Phép kiểm này tồn tại vì rủi ro lớn nhất của học phần không phải là bài khó, mà
là sinh viên không dựng nổi môi trường và phát hiện ra điều đó quá muộn. Bài S2
là bài đầu tiên thật sự cần Docker chạy được, nên nếu máy có vấn đề thì phải lộ
ra ở đây chứ không phải ở buổi S7.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from conftest import doc_bang_chung

BAT_BUOC = {
    "kien truc CPU": "kiến trúc CPU",
    "phien ban Python": "phiên bản Python",
    "phien ban Docker": "phiên bản Docker",
    "docker daemon": "trạng thái docker daemon",
    "dia trong": "dung lượng đĩa trống",
}


@pytest.fixture(scope="module")
def noi_dung(goc: Path) -> str:
    return doc_bang_chung(goc, "preflight.txt")


def test_ghi_du_cac_muc(noi_dung: str) -> None:
    """Bốn mục đầu là điều kiện chạy được; mục đĩa trống có mặt vì ảnh của bài này
    mang theo trình dịch và Lynis, nên nó nặng hơn ảnh của buổi trước."""
    thieu = [ten for khoa, ten in BAT_BUOC.items() if khoa not in noi_dung]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."


def test_docker_co_mat(noi_dung: str) -> None:
    dong = [d for d in noi_dung.splitlines() if d.startswith("phien ban Docker")]
    assert dong, "Preflight không có dòng phiên bản Docker."
    assert "KHONG CO" not in dong[0], (
        "Máy chưa cài Docker. Xem mục 4 của hướng dẫn cài đặt. Nếu không cài được, "
        "báo giảng viên chậm nhất hai ngày trước buổi S3, đừng đợi tới hạn nộp."
    )


def test_docker_daemon_chay(noi_dung: str) -> None:
    dong = [d for d in noi_dung.splitlines() if d.startswith("docker daemon")]
    assert dong, "Preflight không có dòng trạng thái docker daemon."
    assert "KHONG CHAY" not in dong[0], (
        "Docker đã cài nhưng daemon chưa chạy, nên không một phép đo nào của bài này "
        "thực hiện được. Trên Windows và macOS thì mở Docker Desktop và đợi biểu "
        "tượng cá voi chuyển sang trạng thái đang chạy. Trên Linux thì chạy "
        "`sudo systemctl start docker`."
    )
