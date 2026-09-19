"""Vòng tuần tra của thế giới — chạy nền, không chờ ai gõ lệnh.

Ba việc mỗi nhịp: chiến trường (boss hết hạn thì dọn, chưa có boss thì gieo quẻ gọi
kẻ thức tỉnh), trời (dọn thiên biến quá hạn, thi thoảng trời tự đổi sắc), và những lời
thách PK treo quá hẹn thì cho tan. Tin loan đi theo danh thiếp đã ghi — ai từng bấm
vào bot một lần thì trời còn nhớ đường tới người đó.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time

from .. import config
from ..he import dauboss as he_boss
from ..he import thienbien as he_troi
from ..he import pk as he_pk
from .hien_thi import dinh_dang

log = logging.getLogger("tien.vong")

NHIP = 5 * 60                      # giây giữa các vòng
XAC_SUAT_TROI = 0.07              # mỗi nhịp, ~14%/nửa canh giờ như bên Discord
_tro_last = [0]


async def vong_tron_doi(core, bot=None) -> None:
    """Hằng hà sa số việc nhỏ, làm đều thì thành luật trời."""
    nhip = max(30, int(NHIP * getattr(config, "HE_SO_GIAY", 1.0)))
    await asyncio.sleep(20)  # để bot kịp đứng vững đã
    while True:
        try:
            await mot_nhip(core)
        except Exception:  # pragma: no cover
            log.exception("Vòng tuần tra vấp đá")
        await asyncio.sleep(nhip)


async def mot_nhip(core) -> list[str]:
    """Một vòng: trả về các dòng đã loan (để test)."""
    loan: list[str] = []

    # ── chiến trường ──
    for dong in await he_boss.don_dep(core.kho, core.guild, core.rng):
        loan.append(dong)

    # ── trời ──
    for dong in await he_troi.don_dep(core.kho, core.guild):
        loan.append(dong)
    now = int(time.time())
    if now - _tro_last[0] >= 1800 and random.random() < XAC_SUAT_TROI * 2:
        _tro_last[0] = now
        kq = await he_troi.khoi_su_kien(core.kho, core.guild, None, core.rng)
        if kq.thanh_cong:
            for v in kq.van[:1]:
                loan.append(v)

    # ── lời thách PK quá hẹn ──
    qua_han = await he_pk.ru_het_han(core.kho)
    for x in qua_han:
        loan.append(f"Lời thách của **{x['a_ten']}** dành cho {x['b_ten']} "
                    "treo quá hẹn, coi như khước từ. Giang hồ không chờ ai cả.")

    for dong in loan:
        await _phat(core, dong)
    return loan


async def _phat(core, dong: str) -> None:
    html = dinh_dang(dong)
    da_gui: set = set()
    for _uid, chat in await core.kho.danh_thiep_all():
        if chat in da_gui:
            continue
        da_gui.add(chat)
        try:
            from .hien_thi import Trang
            await core.lo.gui(chat, Trang(html=html))
        except Exception:
            pass
