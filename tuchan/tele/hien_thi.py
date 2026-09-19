"""Đổi một KetQua thành thứ Telegram hiển thị được.

Bố cục: tin nhắn đầu (nếu có tranh/video) chỉ mang caption ngắn — Telegram giới hạn
caption của media ở 1024 ký tự, còn chữ của câu chuyện thì đi ở các tin sau, cắt theo
đoạn cho trọn ý. Hàng nút bấm (inline keyboard) gắn vào tin cuối.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from ..he.ketqua import KetQua

GIOI_HAN = 3600        # Telegram cho 4096; chừa chỗ cho tag HTML
GIOI_CAPTION = 950      # caption kèm ảnh/video


@dataclass
class Trang:
    """Một tin nhắn Telegram: text (HTML), kèm phương tiện và hàng nút nếu có."""
    html: str = ""
    anh: str | None = None      # tên tệp trong assets/tranh
    phim: str | None = None     # tên tệp trong assets/thanh_anh
    hang: list[list[tuple[str, str]]] = field(default_factory=list)


def dinh_dang(van: str) -> str:
    """*markdown kiểu engine* → HTML của Telegram."""
    van = van.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    van = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", van, flags=re.S)
    van = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", van, flags=re.S)
    van = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", van)
    return van


def tach(html: str, gioi_han: int = GIOI_HAN) -> list[str]:
    if len(html) <= gioi_han:
        return [html]
    trang: list[str] = []
    con = html
    while len(con) > gioi_han:
        cat = con.rfind("\n\n", 0, gioi_han)
        if cat < gioi_han // 2:
            cat = con.rfind("\n", 0, gioi_han)
        if cat < gioi_han // 2:
            cat = con.rfind(". ", 0, gioi_han)
        if cat <= 0:
            cat = gioi_han
        trang.append(con[:cat].strip())
        con = con[cat:].strip()
    if con:
        trang.append(con)
    return [t for t in trang if t]


def duong_dan_anh(ten: str | None) -> Path | None:
    if not ten:
        return None
    p = config.DUONG_DAN_TRANH / ten
    return p if p.exists() else None


def duong_dan_phim(ten: str | None) -> Path | None:
    if not ten:
        return None
    p = config.DUONG_DAN_THANH_ANH / ten
    return p if p.exists() else None


def xuat(kq: KetQua, hang: list[list[tuple[str, str]]] | None = None) -> list[Trang]:
    """KetQua → danh sách Trang, phương tiện đứng trước, nút bấm nằm cuối."""
    dau = ""
    if kq.tieu_de:
        dau = f"<b>❖ {dinh_dang(kq.tieu_de)}</b>\n\n"
    pages = tach(dau + dinh_dang(kq.toan_van))
    pages = [p for p in pages if p.strip()] or [dau or "…"]
    if kq.chu_thich:
        pages[-1] += "\n\n<i>" + dinh_dang(kq.chu_thich) + "</i>"

    ket: list[Trang] = []
    duong_anh = duong_dan_anh(kq.anh)
    duong_phim = duong_dan_phim(kq.thanh_anh)
    if duong_anh is not None or duong_phim is not None:
        # caption gọn: mỗi khoảnh khắc lớn có một cái khung tranh riêng, chữ để dành cho trang sau
        cap = f"<b>❖ {dinh_dang(kq.tieu_de or '…')}</b>" if kq.tieu_de else ""
        ket.append(Trang(html=cap[:GIOI_CAPTION],
                         anh=kq.anh if duong_anh is not None else None,
                         phim=kq.thanh_anh if duong_phim is not None else None))
    ket.extend(Trang(html=p) for p in pages)
    if hang:
        ket[-1].hang = hang
    return ket


def nut(*hangs: tuple[tuple[str, str], ...]) -> list[list[tuple[str, str]]]:
    """Hàng nút dạng [(label, callback_data), ...] — dùng chung cho mọi giao diện."""
    return [list(h) for h in hangs]
