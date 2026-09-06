"""Thiên biến: trời đổi, và không ai hỏi ý ngươi."""

from __future__ import annotations

import random

from .. import config
from ..data import sukien as dl_sukien
from .ketqua import KetQua


async def khoi_su_kien(kho, guild_id: int, ma: str | None = None,
                       rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    sk = dl_sukien.lay(ma) if ma else None
    if ma and sk is None:
        sk = dl_sukien.tim_theo_ten(ma)
    if sk is None:
        dang = set(await kho.thien_bien_dang_dien(guild_id))
        con_lai = [s for s in dl_sukien.DANH_SACH.values() if s.ma not in dang]
        if not con_lai:
            return KetQua(tieu_de="Trời đã đủ loạn",
                          van=["Thiên địa hiện đang có quá nhiều biến động. Đợi cho lắng bớt đã."],
                          thanh_cong=False)
        sk = rng.choice(con_lai)
    await kho.khoi_thien_bien(guild_id, sk.ma, sk.gio)
    kq = KetQua(tieu_de=sk.ten, mau=config.MAU_KIM, anh="bia_tien_do.png")
    kq.them(sk.dieu_bao)
    kq.them(f"**{sk.ten}.** {sk.mo_ta}")
    kq.them(
        "Kẻ nhanh chân thì được phần. Kẻ chậm chân thì được bài học. "
        "Kẻ xui thì được cả hai, theo thứ tự ngược lại."
    )
    return kq


async def xem_thien_bien(kho, guild_id: int) -> KetQua:
    dang = await kho.thien_bien_dang_dien(guild_id)
    if not dang:
        return KetQua(
            tieu_de="Thiên tượng",
            van=["Ngươi ngửa mặt nhìn trời hồi lâu. Mây trôi như mọi ngày, gió cũng thế. "
                 "Thiên địa đang yên — nghĩa là nó đang tích cho một lần không yên."])
    kq = KetQua(tieu_de="Thiên tượng", mau=config.MAU_KIM)
    for ma in dang:
        sk = dl_sukien.lay(ma)
        if sk:
            kq.them(f"**{sk.ten}.** {sk.mo_ta}")
    kq.them("Trong lúc này, mọi việc ngươi làm đều mang màu của trời.")
    return kq


async def don_dep(kho, guild_id: int) -> list[str]:
    """Trả về những câu kể khi sự kiện kết thúc."""
    ket = []
    for ma in await kho.don_thien_bien(guild_id):
        sk = dl_sukien.lay(ma)
        if sk:
            ket.append(f"**{sk.ten}** đã qua. {sk.khi_tan}")
    return ket
