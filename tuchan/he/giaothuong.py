"""Chợ tu chân và chuyện trao tay."""

from __future__ import annotations

import random

from .. import config
from ..data import vatpham
from ..vanphong import mo_ta_linh_thach
from .ketqua import KetQua

# Những thứ chợ nhỏ dưới núi có bán
HANG_CO_BAN = (
    "hoang_tinh_thao", "thanh_lan_hoa", "huyet_tinh_chi", "hac_thiet",
    "thanh_dong_tinh", "hoi_khi_dan", "liem_thuong_dan", "thanh_cuong_kiem",
    "truyen_tong_phu", "yeu_dan",
)

LOI_CHU_QUAN = (
    "Chủ quầy là một lão bà lưng còng, tay lúc nào cũng đang phân loại rễ cây. "
    "Bà không chào ngươi, chỉ hất cằm về phía mấy cái nong phơi đầy dược liệu.",
    "Người bán hàng là một hán tử một mắt, tay trái đeo găng da không bao giờ tháo. "
    "Hắn nhìn khí tức của ngươi trước, nhìn túi tiền của ngươi sau.",
    "Quầy hàng chỉ là một tấm chiếu trải trên đất, nhưng thứ bày trên đó thì không rẻ. "
    "Chủ nhân ngồi xếp bằng, mắt nhắm, và ngươi biết chắc là lão không ngủ.",
)


def gia_mua(vp, he_so: float = 1.0) -> int:
    return max(1, int(vp.gia * 1.25 * he_so))


def gia_ban(vp, he_so: float = 1.0) -> int:
    return max(1, int(vp.gia * 0.55 * he_so))


def _mo_ta_gia(so: int) -> str:
    if so < 20:
        return "vài viên linh thạch lẻ"
    if so < 120:
        return "một xâu linh thạch"
    if so < 800:
        return "một túi linh thạch nặng tay"
    if so < 6000:
        return "một số linh thạch đủ khiến người ngoài liếc nhìn"
    return "một khoản mà phàm nhân cả đời không đếm tới"


async def xem_hang(kho, ts, hs: dict | None = None, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    he_so = hs.get("gia_ca", 1.0)
    kq = KetQua(tieu_de="Chợ tu chân dưới núi")
    kq.them(
        "Chợ họp ở khoảng đất trống trước miếu Thổ Địa, mỗi tháng ba phiên. "
        "Người bán ngồi hai hàng, người mua đi ở giữa, và không ai hỏi lai lịch của ai."
    )
    kq.them(rng.choice(LOI_CHU_QUAN))
    if he_so > 1.2:
        kq.them("Dạo này giá cả đắt đỏ tới mức vô lý. Ai cũng biết vì sao, nhưng không ai nói ra.")
    elif he_so < 0.9:
        kq.them("Hàng ế đầy nong. Người bán chào mời rát cổ — thời buổi này linh thạch khó kiếm hơn dược liệu.")

    dong = []
    for ma in HANG_CO_BAN:
        vp = vatpham.lay(ma)
        if not vp:
            continue
        dong.append(f"• **{vp.ten}** — {_mo_ta_gia(gia_mua(vp, he_so))} *({gia_mua(vp, he_so)} linh thạch)*")
    kq.them("\n".join(dong))
    kq.them(mo_ta_linh_thach(ts.linh_thach))
    kq.them("*Muốn mua thì gọi tên món hàng. Muốn bán thì đưa vật ra — người ta trả rẻ, nhưng người ta trả ngay.*")
    return kq


def tim_hang(ten: str) -> str | None:
    ten = (ten or "").strip().lower()
    if not ten:
        return None
    for ma, vp in vatpham.DANH_MUC.items():
        if ten == ma or ten == vp.ten.lower():
            return ma
    for ma, vp in vatpham.DANH_MUC.items():
        if ten in vp.ten.lower():
            return ma
    return None


async def mua(kho, ts, ten_hang: str, so_luong: int = 1, hs: dict | None = None) -> KetQua:
    hs = hs or {}
    he_so = hs.get("gia_ca", 1.0)
    ma = tim_hang(ten_hang)
    if ma is None or ma not in HANG_CO_BAN:
        return KetQua(
            tieu_de="Chợ không có thứ đó",
            van=["Ngươi hỏi tới ba quầy. Người ta lắc đầu, có kẻ còn cười. "
                 "Thứ ngươi muốn không bày ở chợ này — muốn có thì phải tự đi mà lấy."],
            thanh_cong=False)
    so_luong = max(1, min(99, so_luong))
    vp = vatpham.lay(ma)
    tong = gia_mua(vp, he_so) * so_luong
    if ts.linh_thach < tong:
        return KetQua(
            tieu_de="Không đủ linh thạch",
            van=[f"Ngươi dốc túi ra đếm. Thiếu. Chủ quầy thu **{vp.ten}** lại, "
                 "cẩn thận phủi bụi trên đó, rồi đặt vào chỗ cũ — động tác ấy còn khó chịu hơn một câu chê."],
            thanh_cong=False)
    ts.linh_thach -= tong
    await kho.them_vat(ts.user_id, ma, so_luong)
    await kho.luu(ts)
    return KetQua(
        tieu_de="Mua bán xong",
        van=[
            f"Ngươi đếm ra {_mo_ta_gia(tong)} đặt lên chiếu. Chủ quầy đưa **{vp.ten}**"
            + (f" ×{so_luong}" if so_luong > 1 else "") + " bằng cả hai tay — không phải vì kính trọng, mà vì hàng dễ vỡ.",
            vp.mo_ta,
            mo_ta_linh_thach(ts.linh_thach),
        ])


async def ban(kho, ts, ten_hang: str, so_luong: int = 1, hs: dict | None = None) -> KetQua:
    hs = hs or {}
    he_so = hs.get("gia_ca", 1.0)
    ma = tim_hang(ten_hang)
    if ma is None:
        return KetQua(tieu_de="Không rõ ngươi muốn bán gì", van=["Ngươi lôi ra một thứ, rồi tự thấy nó chẳng đáng."],
                      thanh_cong=False)
    so_luong = max(1, min(99, so_luong))
    if not await kho.bot_vat(ts.user_id, ma, so_luong):
        return KetQua(tieu_de="Không đủ hàng", van=[f"Ngươi không có đủ **{vatpham.ten(ma)}** để bán."],
                      thanh_cong=False)
    vp = vatpham.lay(ma)
    tong = gia_ban(vp, he_so) * so_luong
    ts.linh_thach += tong
    if ts.phap_bao == ma and await kho.dem_vat(ts.user_id, ma) <= 0:
        ts.phap_bao = ""
    await kho.luu(ts)
    return KetQua(
        tieu_de="Bán xong",
        van=[
            f"Ngươi đặt **{vp.ten}**{f' ×{so_luong}' if so_luong > 1 else ''} lên chiếu. "
            "Chủ quầy cầm lên, xoay hai vòng, chê ba câu, rồi trả giá — thấp, như mọi khi. Ngươi gật đầu, vì ngươi cần tiền.",
            f"Đổi lại: {_mo_ta_gia(tong)}.",
            mo_ta_linh_thach(ts.linh_thach),
        ])


async def trao_tay(kho, nguoi_cho, nguoi_nhan, ten_hang: str, so_luong: int = 1) -> KetQua:
    ma = tim_hang(ten_hang)
    if ma is None:
        return KetQua(tieu_de="Không có vật ấy", van=["Ngươi lục túi mà không thấy thứ mình vừa nói tới."],
                      thanh_cong=False)
    so_luong = max(1, min(99, so_luong))
    if not await kho.bot_vat(nguoi_cho.user_id, ma, so_luong):
        return KetQua(tieu_de="Không đủ", van=[f"Ngươi không có đủ **{vatpham.ten(ma)}**."], thanh_cong=False)
    await kho.them_vat(nguoi_nhan.user_id, ma, so_luong)
    if nguoi_cho.phap_bao == ma and await kho.dem_vat(nguoi_cho.user_id, ma) <= 0:
        nguoi_cho.phap_bao = ""
        await kho.luu(nguoi_cho)
    vp = vatpham.lay(ma)
    return KetQua(
        tieu_de="Trao vật",
        van=[
            f"**{nguoi_cho.ten}** đưa **{vp.ten}**{f' ×{so_luong}' if so_luong > 1 else ''} cho **{nguoi_nhan.ten}**. "
            "Không giấy tờ, không người làm chứng — trong giang hồ, vật đã rời tay thì đừng nghĩ tới chuyện đòi lại.",
            f"*{vp.mo_ta}*",
            "Có kẻ trao vật để kết giao. Có kẻ trao vật để mua một ân tình sẽ dùng tới về sau. "
            "Chỉ hai người trong cuộc mới biết hôm nay là loại nào.",
        ])


async def tang_linh_thach(kho, nguoi_cho, nguoi_nhan, so: int) -> KetQua:
    so = max(1, int(so))
    if nguoi_cho.linh_thach < so:
        return KetQua(tieu_de="Không đủ linh thạch", van=["Ngươi dốc túi ra và thấy mình nghèo hơn mình tưởng."],
                      thanh_cong=False)
    nguoi_cho.linh_thach -= so
    nguoi_nhan.linh_thach += so
    await kho.luu(nguoi_cho)
    await kho.luu(nguoi_nhan)
    return KetQua(
        tieu_de="Đưa linh thạch",
        van=[f"**{nguoi_cho.ten}** đẩy {_mo_ta_gia(so)} qua bàn. **{nguoi_nhan.ten}** cầm lấy, "
             "và cả hai đều không nói lời nào — có những chuyện nói ra thì hỏng."])
