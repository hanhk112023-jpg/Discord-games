"""Thiên cơ — vận trời, vận người, và những hệ số ẩn không ai được thấy."""

from __future__ import annotations

import random
import time

from ..data import sukien


def rng_cho(user_id: int | None = None) -> random.Random:
    """Mỗi lần gieo một quẻ mới. Không ai đoán được trời."""
    return random.Random()


async def he_so_the_gioi(kho, guild_id: int) -> dict[str, float]:
    """Tổng hợp ảnh hưởng của mọi thiên biến đang diễn ra."""
    he_so = {
        "tu_luyen": 1.0, "nguy_hiem": 1.0, "dan_thanh": 1.0,
        "khi_thanh": 1.0, "gia_ca": 1.0, "ky_ngo": 1.0,
        "danh_vong": 1.0, "sat_khi": 1.0, "dao_tam": 1.0,
    }
    try:
        dang = await kho.thien_bien_dang_dien(guild_id)
    except Exception:
        dang = []
    for ma in dang:
        sk = sukien.lay(ma)
        if not sk:
            continue
        for k, v in sk.anh_huong.items():
            he_so[k] = he_so.get(k, 1.0) * v
    he_so["_dang_dien"] = dang  # type: ignore[assignment]
    return he_so


def van_khi(rng: random.Random, dao_tam: int, danh_vong: int = 0) -> float:
    """Vận khí của một hành động: 0.6 tới ~1.45. Đạo tâm vững thì ít gặp hoạ vô cớ."""
    goc = rng.gauss(1.0, 0.16)
    goc += (dao_tam - 60) / 900.0
    goc += min(0.05, danh_vong / 20000.0)
    return max(0.58, min(1.5, goc))


def thanh_bai(rng: random.Random, ti_le: float) -> bool:
    return rng.random() < max(0.01, min(0.985, ti_le))


def roi_do(rng: random.Random, bang: dict[str, int], he_so: float = 1.0) -> list[str]:
    """bang: mã vật phẩm -> phần nghìn. Trả về danh sách vật rơi ra."""
    ra: list[str] = []
    for ma, phan_nghin in bang.items():
        if rng.random() < min(0.95, phan_nghin / 1000.0 * he_so):
            ra.append(ma)
    return ra
