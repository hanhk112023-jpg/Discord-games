"""Nhân vật: sinh ra, được nhìn ngắm, và đôi khi chết đi."""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import (canh_gioi, mo_ta_dan_pham, mo_ta_tang, ten_canh_gioi,
                        ten_dan_pham, xung_ho)
from ..data import congthuc as dl_congthuc
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..data import xuatthan as dl_xuatthan
from ..db import TuSi
from ..vanphong import (liet_ke_tui, mo_ta_dao_hanh, mo_ta_dao_tam,
                        mo_ta_danh_vong, mo_ta_linh_thach, mo_ta_phap_bao,
                        mo_ta_sat_nghiep, mo_ta_than_the, mo_ta_tho_nguyen)
from .ketqua import KetQua

NGOAI_HINH = (
    "Ngươi gầy, xương gò má cao, mắt sâu — dáng của kẻ ăn không đủ no trong nhiều năm.",
    "Ngươi có đôi bàn tay chai sạn và một cái sẹo mờ chạy dọc cẳng tay trái, vết cũ, không ai hỏi.",
    "Tóc ngươi buộc cao bằng một dải vải thô. Áo ngươi bạc màu nhưng sạch — ngươi vẫn giặt nó mỗi tối.",
    "Ngươi bước đi lặng lẽ, thói quen của kẻ từng phải tránh mặt người khác để sống.",
    "Trên sống mũi ngươi có một vết chai nhỏ, dấu của những năm cúi đầu đọc sách dưới ánh đèn dầu.",
)


async def tao_nhan_vat(kho, user_id: int, guild_id: int, ten: str, gioi_tinh: str,
                       ma_xuat_than: str, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    if await kho.lay_tu_si(user_id):
        return KetQua(tieu_de="Ngươi đã có một đời để sống",
                      van=["Danh tính của ngươi đã nằm trong sổ. Sống cho hết cái đã có, "
                           "rồi hẵng nghĩ tới chuyện làm người khác."],
                      thanh_cong=False)
    xt = dl_xuatthan.lay(ma_xuat_than) or dl_xuatthan.lay("pham_nhan")
    ten = (ten or "Vô Danh").strip()[:24]
    gt = "nữ" if gioi_tinh.strip().lower().startswith(("n\u1eef", "nu", "f", "g")) and gioi_tinh.strip().lower() != "nam" else "nam"

    ts = TuSi(
        user_id=user_id, guild_id=guild_id, ten=ten, gioi_tinh=gt, xuat_than=xt.ma,
        canh_gioi=0, tang=1, tu_vi=0, tu_chat=xt.tu_chat, can_cot=xt.can_cot,
        dao_tam=xt.dao_tam, than_the=100, linh_thach=xt.linh_thach,
        nhap_dao_luc=int(time.time()),
    )
    await kho.tao_tu_si(ts)
    for ma, sl in xt.hanh_trang.items():
        await kho.them_vat(user_id, ma, sl)

    kq = KetQua(tieu_de=f"Nhập đạo — {ten}", anh="bia_tien_do.png", mau=config.MAU_LINH)
    kq.them(xt.mo_ta)
    kq.them(rng.choice(NGOAI_HINH))
    kq.them(f"**Linh căn:** {xt.linh_can}.")
    kq.them(
        "Ngươi tìm được một quyển sách rách nửa, học lỏm được cách thở. Đêm đầu tiên ngồi xuống, "
        "ngươi ngồi tới sáng mà chẳng thấy gì. Đêm thứ ba mươi, ngươi cảm nhận được một sợi khí "
        "mảnh như tơ chạy qua ngực mình — và ngươi khóc, không hiểu vì sao."
    )
    kq.them(f"*“{xt.loi_the}”*")
    kq.them(
        f"Từ hôm nay, trong sổ sinh tử của thế gian có thêm một cái tên: **{ten}**, "
        f"{ten_canh_gioi(0, 1)}. Con đường phía trước dài tới mức nói ra thì ngươi sẽ không tin — "
        "nên chẳng ai nói với ngươi cả."
    )
    if xt.hanh_trang:
        kq.them("Tất cả những gì ngươi mang theo: **"
                + ", ".join(f"{vatpham.ten(m)}{f' ×{n}' if n > 1 else ''}" for m, n in xt.hanh_trang.items())
                + "**.")
    await kho.chep(user_id, "nhap_dao", f"{ten} nhập đạo, xuất thân {xt.ten}.")
    return kq


async def xem_nhan_vat(kho, ts, hs: dict | None = None) -> KetQua:
    cg = canh_gioi(ts.canh_gioi)
    xt = dl_xuatthan.lay(ts.xuat_than)
    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    cs = ts.tinh_chi_so()
    tb = ts.lay_trang_bi()
    ch = ts.lay_cuong_hoa()

    kq = KetQua(tieu_de=f"Hồ sơ tu sĩ — {ts.ten}", anh=cg.tranh or "bia_tien_do.png")

    kq.them(f"👤 **Đạo hiệu:** {ts.ten} | **Môn phái:** {mp.ten if mp else 'Tán Tu'}")
    kq.them(f"🌀 **Cảnh giới:** **{ten_canh_gioi(ts.canh_gioi, ts.tang)}** ({cg.ten})")
    pt = min(100.0, round(ts.tu_vi / max(1, cs['tu_vi_can']) * 100, 1))
    kq.them(f"✨ **Tu vi:** `{ts.tu_vi:,} / {cs['tu_vi_can']:,}` ({pt}%) | ⚡ **Tốc độ:** `+{cs['tu_vi_sec']} tu vi/s`")
    kq.them(f"⚔️ **LỰC CHIẾN:** **{cs['luc_chien']:,}**")

    kq.them(
        f"📊 **BẢNG THUỘC TÍNH CHIẾN ĐẤU:**\n"
        f"• ❤️ Khí Huyết (HP): `{cs['hp']:,} / {cs['hp_max']:,}`\n"
        f"• 🔷 Chân Khí (MP): `{cs['mp']:,} / {cs['mp_max']:,}`\n"
        f"• 🗡️ Công Kích: `{cs['cong']:,}`\n"
        f"• 🛡️ Phòng Ngự: `{cs['thu']:,}`\n"
        f"• 💥 Bạo Kích: `{cs['bao_kich']}%`\n"
        f"• 💨 Thân Pháp: `{cs['toc_do']}`\n"
        f"• 🧘 Căn Cốt: `{ts.can_cot}` | Tư Chất: `{ts.tu_chat}` | Đạo Tâm: `{ts.dao_tam}`"
    )

    # Trang bị
    slot_names = {"vu_khi": "Vũ Khí", "giap": "Chiến Giáp", "phap_bao": "Pháp Bảo", "ngoc_boi": "Ngọc Bội"}
    ds_tb = []
    for s_k, s_v in slot_names.items():
        ma = tb.get(s_k)
        if ma and vatpham.lay(ma):
            vp = vatpham.lay(ma)
            cap = ch.get(ma, 0)
            cap_str = f" (+{cap})" if cap > 0 else ""
            ds_tb.append(f"• **{s_v}:** {vp.ten}{cap_str}")
        else:
            ds_tb.append(f"• **{s_v}:** *(Trống)*")
    kq.them("🛡️ **TRANG BỊ ĐANG MANG:**\n" + "\n".join(ds_tb))

    kq.them(
        f"💎 **Tài phú:** `{ts.linh_thach:,}` Linh Thạch | **Danh vọng:** `{ts.danh_vong:,}`\n"
        f"🏆 **Chiến tích:** Thắng `{ts.so_tran_thang}` trận | Thua `{ts.so_tran_thua}` trận | Vượt Tháp tầng `{ts.thap_tang()}`"
    )

    if ts.dang_bi_thuong:
        kq.them(f"⚠️ **Trạng thái:** Bị thương nhẹ, vận khí điều tức còn `{ts.con_bao_lau_duong_thuong}` giây để hồi phục!")
    else:
        kq.them("💚 **Trạng thái:** Khí huyết sung mãn, sẵn sàng xuất chiến!")

    return kq


async def chuyen_the(kho, ts, ten_moi: str, ma_xuat_than: str, rng: random.Random | None = None) -> KetQua:
    """Kẻ đã chết có thể chọn đầu thai — giữ lại chút dư âm của kiếp trước."""
    rng = rng or random.Random()
    if not ts.da_chet:
        return KetQua(tieu_de="Ngươi vẫn còn sống", van=["Kẻ còn thở thì chưa được phép đi đường vòng."],
                      thanh_cong=False)
    danh_cu = ts.danh_vong
    ten_cu = ts.ten
    canh_cu = ten_canh_gioi(ts.canh_gioi, ts.tang)
    user_id, guild_id = ts.user_id, ts.guild_id
    await kho.xoa_tu_si(user_id)
    kq = await tao_nhan_vat(kho, user_id, guild_id, ten_moi, ts.gioi_tinh, ma_xuat_than, rng)
    if not kq.thanh_cong:
        return kq
    ts_moi = await kho.lay_tu_si(user_id)
    thua = int(danh_cu * 0.1)
    ts_moi.danh_vong += thua
    ts_moi.dao_tam = min(100, ts_moi.dao_tam + 5)
    await kho.luu(ts_moi)
    kq.tieu_de = "Chuyển thế"
    kq.van.insert(0, (
        f"**{ten_cu}** đã chết ở {canh_cu}. Người ta không dựng bia, chỉ có mấy kẻ từng chạm mặt "
        "còn nhắc lại đôi câu, rồi cũng thôi."
    ))
    kq.them(
        "Có thứ gì đó của kiếp trước theo ngươi sang. Không phải tu vi — tu vi đã tan theo tro. "
        "Chỉ là một cảm giác rất mờ: rằng ngươi đã từng đi con đường này, và đã từng ngã ở đâu đó phía trước."
    )
    return kq
