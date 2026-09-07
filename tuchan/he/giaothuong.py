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
    "truyen_tong_phu", "yeu_dan", "o_thiet_dao", "lieu_diep_phi_dao",
)

# Chợ ngoài ai cũng vào được. Gian trong thì phải có khí tức tới bậc mới thấy cửa.
HANG_GIAN_TRONG: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (1, "Cuối dãy có một cái lều bạt, chủ lều là đạo nhân gầy nhom mắt lồi. "
        "Lều ấy chỉ mở cho kẻ đã trúc cơ — người thường đi ngang cũng không nhìn thấy nó.",
     ("ngu_loi_phu_luc", "thanh_tam_dan", "tuc_cot_dan", "truc_co_dan", "bang_phach")),
    (2, "Sau lều bạt là một gian nhà đá không cửa sổ. Người trong đó không bán cho kẻ chưa kết đan, "
        "và cũng không giải thích vì sao.",
     ("tung_van_kiem", "liet_diem_dao", "pha_quan_thuong", "truy_nguyet_cung",
      "cuong_the_dan", "pha_chuong_dan", "an_tuc_dan", "ket_dan_dan", "hoa_tinh_thach")),
    (3, "Dưới hầm gian nhà đá còn một tầng nữa. Đèn ở đó cháy bằng thứ dầu không có mùi, "
        "và người bán hàng ngồi sau một tấm rèm the, cả buổi không nhúc nhích.",
     ("huyen_thiet_trong_kiem", "kim_tam_ti", "tu_loi_an", "cuu_u_hon_chung",
      "kim_cang_dan", "ngung_than_dan", "cuu_chuyen_hoi_xuan", "nguyen_anh_dan",
      "tu_phu_linh_chi", "thien_loi_moc")),
    (5, "Và có một cái chợ nữa, không họp ở dưới núi. Nó họp ở giữa mây, ba năm một lần, "
        "và chỉ những kẻ đã hoá thần mới nhận được thiếp mời — thiếp là một mảnh giấy trắng, không chữ.",
     ("ngu_phong_phi_kiem", "huyet_ha_ma_dao", "can_khon_but", "do_ach_dan",
      "hoa_than_dan", "dien_tho_dan", "long_huyet_thao", "tinh_ha_sa",
      "cuu_thien_huyen_thiet")),
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

    for bac, dan_nhap, hang in HANG_GIAN_TRONG:
        if ts.canh_gioi < bac:
            continue
        muc = []
        for ma in hang:
            vp = vatpham.lay(ma)
            if not vp:
                continue
            muc.append(f"• **{vp.ten}** — {_mo_ta_gia(gia_mua(vp, he_so))} *({gia_mua(vp, he_so)} linh thạch)*")
        if muc:
            kq.them(dan_nhap + "\n" + "\n".join(muc))

    kq.them(mo_ta_linh_thach(ts.linh_thach))
    kq.them("*Muốn mua thì gọi tên món hàng. Muốn bán thì đưa vật ra — người ta trả rẻ, nhưng người ta trả ngay.*")
    return kq


def hang_ban_cho(ts) -> tuple[str, ...]:
    """Chợ ngoài ai cũng mua được; gian trong chỉ mở cho kẻ đủ bậc."""
    bo = list(HANG_CO_BAN)
    for bac, _loi, hang in HANG_GIAN_TRONG:
        if ts.canh_gioi >= bac:
            bo.extend(hang)
    return tuple(dict.fromkeys(bo))


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
    co_ban = hang_ban_cho(ts)
    if ma is not None and ma not in co_ban:
        vp_kia = vatpham.lay(ma)
        moi_cho = any(ma in hang for bac, _l, hang in HANG_GIAN_TRONG if ts.canh_gioi < bac)
        if moi_cho and vp_kia:
            return KetQua(
                tieu_de="Ngươi chưa đủ tư cách hỏi",
                van=[f"Ngươi nhắc tới **{vp_kia.ten}**. Người bán ngẩng lên nhìn ngươi một lượt — "
                     "từ đôi giày cho tới khí tức — rồi cúi xuống làm việc của mình, "
                     "coi như vừa rồi không có ai nói gì cả."],
                thanh_cong=False)
    if ma is None or ma not in co_ban:
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
