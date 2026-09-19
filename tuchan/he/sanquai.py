"""Săn quái dã ngoại & Trấn Yêu Tháp — cốt lõi chiến đấu và cày cuốc tu tiên."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from .. import config
from ..canhgioi import ten_canh_gioi
from ..data import vatpham
from . import chiendau
from .ketqua import KetQua
from .phieuluu import ben_tu_nguoi_choi


@dataclass
class QuaiVat:
    ma: str
    ten: str
    khu_vuc: str
    canh_gioi: int
    tang: int
    hp: int
    cong: int
    thu: int
    bao_kich: float
    toc_do: int
    exp: int
    linh_thach: int
    mo_ta: str
    anh: str = ""
    roi_do: list[tuple[str, float]] = field(default_factory=list)  # (ma_vat_pham, ty_le_0_to_1)
    ky_nang: list[str] = field(default_factory=list)


DANH_SACH_QUAI: dict[str, QuaiVat] = {
    # ── Khu 1: Thanh Khê Sơn (Luyện Khí sơ kỳ) ──
    "tho_ngoc": QuaiVat(
        ma="tho_ngoc", ten="Ngọc Thố Tinh", khu_vuc="thanh_khe_son",
        canh_gioi=0, tang=2, hp=360, cong=45, thu=18, bao_kich=6.0, toc_do=52,
        exp=80, linh_thach=25, mo_ta="Thỏ rừng hấp thu linh khí, di chuyển mau lẹ.",
        roi_do=[("hoang_tinh_thao", 0.45), ("linh_thach_ha", 0.50)],
        ky_nang=["Phổ Thông Tấn Công", "Thố Tinh Cước"],
    ),
    "xich_mao_lang": QuaiVat(
        ma="xich_mao_lang", ten="Xích Mao Lang", khu_vuc="thanh_khe_son",
        canh_gioi=0, tang=4, hp=580, cong=68, thu=28, bao_kich=8.0, toc_do=58,
        exp=140, linh_thach=40, mo_ta="Sói lửa lông đỏ hung hãn, vuốt sắc như dao găm.",
        roi_do=[("yeu_dan", 0.35), ("thanh_cuong_kiem", 0.15), ("hoi_khi_dan", 0.25)],
        ky_nang=["Phổ Thông Tấn Công", "Móng Vuốt Xé Rách"],
    ),
    "thiet_bi_tru": QuaiVat(
        ma="thiet_bi_tru", ten="Thiết Bì Trư", khu_vuc="thanh_khe_son",
        canh_gioi=0, tang=7, hp=920, cong=95, thu=50, bao_kich=7.0, toc_do=48,
        exp=220, linh_thach=60, mo_ta="Lợn rừng da sắt dày cộp, lao tới như xe đồng.",
        roi_do=[("hac_thiet", 0.50), ("thanh_lan_hoa", 0.35), ("o_thiet_dao", 0.15)],
        ky_nang=["Phổ Thông Tấn Công", "Thiết Đầu Húc"],
    ),
    "thach_giap_thu": QuaiVat(
        ma="thach_giap_thu", ten="Thạch Giáp Thú", khu_vuc="thanh_khe_son",
        canh_gioi=0, tang=11, hp=1450, cong=125, thu=75, bao_kich=8.0, toc_do=50,
        exp=350, linh_thach=90, mo_ta="Yêu thú mai đá kiên cố, một đòn nứt núi đá.",
        roi_do=[("hac_thiet", 0.60), ("thanh_dong_tinh", 0.30), ("bo_nguyen_dan", 0.20)],
        ky_nang=["Phổ Thông Tấn Công", "Thạch Bổng Trọng Kích"],
    ),

    # ── Khu 2: Hắc Phong Lâm (Trúc Cơ) ──
    "thanh_dieu": QuaiVat(
        ma="thanh_dieu", ten="Thanh Diêu Điểu", khu_vuc="hac_phong_lam",
        canh_gioi=1, tang=1, hp=2400, cong=190, thu=105, bao_kich=10.0, toc_do=75,
        exp=550, linh_thach=140, mo_ta="Chim ưng khổng lồ sải cánh xé rách gió mây.",
        roi_do=[("giao_can", 0.35), ("lieu_diep_phi_dao", 0.20), ("thanh_lan_hoa", 0.40)],
        ky_nang=["Phổ Thông Tấn Công", "Phong Nhận Trảm"],
    ),
    "doc_vi_hat": QuaiVat(
        ma="doc_vi_hat", ten="Độc Vĩ Cự Hạt", khu_vuc="hac_phong_lam",
        canh_gioi=1, tang=2, hp=3200, cong=240, thu=135, bao_kich=12.0, toc_do=68,
        exp=750, linh_thach=180, mo_ta="Bọ cạp khổng lồ mang nọc độc ăn mòn hộ giáp.",
        roi_do=[("yeu_dan", 0.45), ("ngu_loi_phu_luc", 0.22), ("liem_thuong_dan", 0.30)],
        ky_nang=["Phổ Thông Tấn Công", "Độc Vĩ Thứ"],
    ),
    "hac_lan_giao": QuaiVat(
        ma="hac_lan_giao", ten="Hắc Lân Giao", khu_vuc="hac_phong_lam",
        canh_gioi=1, tang=4, hp=4500, cong=310, thu=170, bao_kich=11.0, toc_do=72,
        exp=1050, linh_thach=240, mo_ta="Giao long vảy đen đầm sâu, khí thế đè người.",
        roi_do=[("thanh_lan_phu", 0.18), ("giao_can", 0.50), ("u_dam_lien", 0.25)],
        ky_nang=["Phổ Thông Tấn Công", "Hắc Thuỷ Xung"],
    ),
    "thi_ma": QuaiVat(
        ma="thi_ma", ten="Thi Ma Cổ Tướng", khu_vuc="hac_phong_lam",
        canh_gioi=1, tang=5, hp=5800, cong=380, thu=205, bao_kich=13.0, toc_do=65,
        exp=1400, linh_thach=320, mo_ta="Tướng quân chết ngàn năm hoá thi thể ma vương.",
        roi_do=[("tung_van_kiem", 0.20), ("liet_diem_dao", 0.18), ("truc_co_dan", 0.25)],
        ky_nang=["Phổ Thông Tấn Công", "Thi Khí Ma Chưởng"],
    ),

    # ── Khu 3: Vạn Cốt Nhai (Kết Đan) ──
    "huyet_nhan_vuon": QuaiVat(
        ma="huyet_nhan_vuon", ten="Huyết Nhãn Viên", khu_vuc="van_cot_nhai",
        canh_gioi=2, tang=1, hp=9500, cong=560, thu=310, bao_kich=14.0, toc_do=80,
        exp=2200, linh_thach=500, mo_ta="Vượn ma mắt đỏ ngập tràn sát khí.",
        roi_do=[("hu_khong_thach", 0.35), ("pha_quan_thuong", 0.18), ("bach_van_sam", 0.40)],
        ky_nang=["Phổ Thông Tấn Công", "Huyết Nhãn Liệt Trảm"],
    ),
    "hac_bao_ma_tu": QuaiVat(
        ma="hac_bao_ma_tu", ten="Hắc Bào Ma Tu", khu_vuc="van_cot_nhai",
        canh_gioi=2, tang=3, hp=14000, cong=740, thu=390, bao_kich=16.0, toc_do=84,
        exp=3200, linh_thach=750, mo_ta="Ma tu tà đạo chuyên săn người cướp đan.",
        roi_do=[("am_hon_sa", 0.40), ("cuu_khuc_lien_hoan", 0.15), ("dinh_than_dan", 0.30)],
        ky_nang=["Phổ Thông Tấn Công", "U Hồn Phệ Cốt"],
    ),
    "cot_tuong": QuaiVat(
        ma="cot_tuong", ten="Bạch Cốt Thống Lĩnh", khu_vuc="van_cot_nhai",
        canh_gioi=2, tang=5, hp=20000, cong=980, thu=490, bao_kich=17.0, toc_do=78,
        exp=4500, linh_thach=1100, mo_ta="Thống lĩnh xương trắng đứng đầu Vạn Cốt Nhai.",
        roi_do=[("huyen_thiet_trong_kiem", 0.18), ("lac_lo_tinh_kim", 0.30), ("ket_dan_dan", 0.25)],
        ky_nang=["Phổ Thông Tấn Công", "Vạn Cốt Huyết Kiếm"],
    ),

    # ── Khu 4: U Đàm Trạch (Nguyên Anh) ──
    "co_thi_tuong": QuaiVat(
        ma="co_thi_tuong", ten="Cổ Thi Chiến Tướng", khu_vuc="u_dam_trach",
        canh_gioi=3, tang=2, hp=32000, cong=1650, thu=820, bao_kich=18.0, toc_do=90,
        exp=7500, linh_thach=1800, mo_ta="Thi hài chiến tướng thời thượng cổ thức tỉnh.",
        roi_do=[("long_van_ngoc", 0.30), ("kim_tam_ti", 0.18), ("cuu_diep_linh_lan", 0.35)],
        ky_nang=["Phổ Thông Tấn Công", "Thượng Cổ Chiến Ý"],
    ),
    "doc_giac_cu_mang": QuaiVat(
        ma="doc_giac_cu_mang", ten="Độc Giác Cự Mãng", khu_vuc="u_dam_trach",
        canh_gioi=3, tang=5, hp=68000, cong=3100, thu=1550, bao_kich=20.0, toc_do=95,
        exp=14000, linh_thach=3500, mo_ta="Mãng xà một sừng độc tính ngập trời.",
        roi_do=[("tu_loi_an", 0.20), ("ngu_phong_phi_kiem", 0.18), ("tay_tuy_dan", 0.30)],
        ky_nang=["Phổ Thông Tấn Công", "Cửu Độc Diệt Tuyệt"],
    ),
}

KHU_VUC = {
    "thanh_khe_son": {
        "ten": "Thanh Khê Sơn",
        "canh_gioi_yeu_cau": 0,
        "canh_gioi_ten": "Luyện Khí",
        "mo_ta": "Dãy núi phủ rừng rậm, nơi khởi đầu thích hợp nhất cho đệ tử mới nhập đạo.",
        "quai": ["tho_ngoc", "xich_mao_lang", "thiet_bi_tru", "thach_giap_thu"],
    },
    "hac_phong_lam": {
        "ten": "Hắc Phong Lâm",
        "canh_gioi_yeu_cau": 1,
        "canh_gioi_ten": "Trúc Cơ",
        "mo_ta": "Rừng thông đen gió hú rít ngày đêm, yêu khí nồng nặc.",
        "quai": ["thanh_dieu", "doc_vi_hat", "hac_lan_giao", "thi_ma"],
    },
    "van_cot_nhai": {
        "ten": "Vạn Cốt Nhai",
        "canh_gioi_yeu_cau": 2,
        "canh_gioi_ten": "Kết Đan",
        "mo_ta": "Vực thẳm ngập tràn hài cốt tu sĩ, nơi ma tu hoành hành.",
        "quai": ["huyet_nhan_vuon", "hac_bao_ma_tu", "cot_tuong"],
    },
    "u_dam_trach": {
        "ten": "U Đàm Trạch",
        "canh_gioi_yeu_cau": 3,
        "canh_gioi_ten": "Nguyên Anh",
        "mo_ta": "Vùng đầm lầy đen ngàn dặm, hung hiểm cùng cực.",
        "quai": ["co_thi_tuong", "doc_giac_cu_mang"],
    },
}


def ben_tu_quai(q: QuaiVat) -> chiendau.BenThamChien:
    return chiendau.BenThamChien(
        ten=q.ten,
        canh_gioi=q.canh_gioi,
        tang=q.tang,
        hp=q.hp,
        hp_max=q.hp,
        mp=200,
        mp_max=200,
        cong=q.cong,
        thu=q.thu,
        bao_kich=q.bao_kich,
        toc_do=q.toc_do,
        ky_nang=q.ky_nang,
        hung_hang=1.1,
    )


async def san_quai(kho, ts, ma_quai: str, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    q = DANH_SACH_QUAI.get(ma_quai)
    if not q:
        return KetQua(tieu_de="Không tìm thấy mục tiêu", van=["Yêu thú này không có mặt ở khu vực."], thanh_cong=False)

    kv = KHU_VUC.get(q.khu_vuc, {})
    if ts.canh_gioi < kv.get("canh_gioi_yeu_cau", 0):
        return KetQua(tieu_de="Cảnh giới chưa đủ",
                      van=[f"Khu vực **{kv.get('ten')}** yêu cầu tối thiểu cảnh giới **{kv.get('canh_gioi_ten')}**!"],
                      thanh_cong=False)

    a = ben_tu_nguoi_choi(ts)
    b = ben_tu_quai(q)

    tran = chiendau.giao_dau(a, b, rng)
    thang = tran.thang is a

    kq = KetQua(tieu_de=f"Săn Quái — {q.ten}", mau=config.MAU_KIM if thang else config.MAU_HUYET)
    for c in tran.van:
        kq.them(c)

    kq.du_lieu["thang"] = thang
    kq.du_lieu["hiep_dau"] = tran.hiep_dau

    if thang:
        ts.so_tran_thang += 1
        ts.tu_vi += q.exp
        ts.linh_thach += q.linh_thach
        ts.than_the = max(30, ts.than_the - min(25, tran.ton_thuong_ke_thua))

        phan_thuong = [f"📈 +{q.exp:,} Tu vi", f"💎 +{q.linh_thach:,} Linh thạch"]

        for ma_item, ti_le in q.roi_do:
            if rng.random() < ti_le:
                await kho.them_vat(ts.user_id, ma_item, 1)
                vp = vatpham.lay(ma_item)
                phan_thuong.append(f"🎁 Nhặt được: **{vp.ten}**")

        kq.them("🎉 **CHIẾN LỢI PHẨM THU HOẠCH:**\n" + "\n".join(f"• {pt}" for pt in phan_thuong))
        cs = ts.tinh_chi_so()
        can = cs["tu_vi_can"]
        pt = min(100.0, round(ts.tu_vi / max(1, can) * 100, 1))
        kq.them(f"📊 **Tiến độ cảnh giới:** `{ts.tu_vi:,} / {can:,}` ({pt}%)")
    else:
        ts.so_tran_thua += 1
        ts.than_the = max(25, ts.than_the - 30)
        ts.thuong_toi = int(time.time()) + 10
        kq.them("⚠️ **Ngươi bị trọng thương!** Hãy điều tức 10 giây hoặc dùng đan dược trị thương để tiếp tục.")

    await kho.luu(ts)
    return kq


# ───────────────────────── TRẤN YÊU THÁP ─────────────────────────

def quai_thap(tang: int) -> QuaiVat:
    cg = min(9, (tang - 1) // 10)
    bac_tang = ((tang - 1) % 10) + 1
    hp = int(450 + 200 * tang + 80 * (tang ** 1.6))
    cong = int(45 + 22 * tang + 12 * (tang ** 1.5))
    thu = int(18 + 12 * tang + 6 * (tang ** 1.5))
    exp = int(120 + 75 * tang + 15 * (tang ** 1.4))
    lt = int(35 + 25 * tang)

    ten_thu_ve = f"Thủ Vệ Trấn Tháp Tầng {tang}"
    if tang % 10 == 0:
        ten_thu_ve = f"★ Ma Vương Tầng {tang} ★"
    elif tang % 5 == 0:
        ten_thu_ve = f"Thống Lĩnh Tầng {tang}"

    roi_do = [("linh_thach_ha", 0.8)]
    if tang >= 5:
        roi_do.append(("hoi_khi_dan", 0.5))
    if tang >= 10:
        roi_do.append(("truc_co_dan", 0.4))
    if tang >= 20:
        roi_do.append(("thanh_lan_phu", 0.3))
    if tang >= 30:
        roi_do.append(("ket_dan_dan", 0.35))

    return QuaiVat(
        ma=f"thap_{tang}",
        ten=ten_thu_ve,
        khu_vuc="tran_yeu_thap",
        canh_gioi=cg,
        tang=bac_tang,
        hp=hp,
        cong=cong,
        thu=thu,
        bao_kich=round(7.0 + tang * 0.3, 1),
        toc_do=int(50 + tang * 1.5),
        exp=exp,
        linh_thach=lt,
        mo_ta=f"Thủ hộ cấm chế tại tầng thứ {tang} của Trấn Yêu Tháp.",
        roi_do=roi_do,
        ky_nang=["Phổ Thông Tấn Công", "Trấn Tháp Thần Quyền", "Lôi Điện Ba Động"],
    )


async def vuot_thap(kho, ts, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    tang_hien_tai = ts.thap_tang()

    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Chưa thể khiêu chiến",
                      van=[f"Thương thế chưa lành, còn {ts.con_bao_lau_duong_thuong} giây nữa mới có thể bước vào Trấn Yêu Tháp."],
                      thanh_cong=False)

    q = quai_thap(tang_hien_tai)
    a = ben_tu_nguoi_choi(ts)
    b = ben_tu_quai(q)

    tran = chiendau.giao_dau(a, b, rng)
    thang = tran.thang is a

    kq = KetQua(tieu_de=f"Trấn Yêu Tháp — Tầng {tang_hien_tai}", mau=config.MAU_KIM if thang else config.MAU_HUYET)
    for c in tran.van:
        kq.them(c)

    kq.du_lieu["thang"] = thang
    kq.du_lieu["tang"] = tang_hien_tai
    kq.du_lieu["hiep_dau"] = tran.hiep_dau

    if thang:
        ts.dat_thap_tang(tang_hien_tai + 1)
        ts.tu_vi += q.exp * 2
        ts.linh_thach += q.linh_thach * 2
        ts.than_the = max(35, ts.than_the - min(20, tran.ton_thuong_ke_thua))

        phan_thuong = [f"📈 +{q.exp * 2:,} Tu vi", f"💎 +{q.linh_thach * 2:,} Linh thạch"]

        for ma_item, ti_le in q.roi_do:
            if rng.random() < ti_le:
                await kho.them_vat(ts.user_id, ma_item, 1)
                vp = vatpham.lay(ma_item)
                phan_thuong.append(f"🎁 Nhận bảo vật: **{vp.ten}**")

        kq.them(
            f"🎉 **ĐÃ VƯỢT QUA TẦNG {tang_hien_tai}!**\n"
            f"Cánh cổng phong ấn tầng {tang_hien_tai + 1} đã rộng mở!\n\n"
            "🏆 **PHẦN THƯỞNG PHÁ THÁP:**\n" + "\n".join(f"• {pt}" for pt in phan_thuong)
        )
    else:
        ts.than_the = max(20, ts.than_the - 35)
        ts.thuong_toi = int(time.time()) + 10
        kq.them(f"⚠️ **Khiêu chiến tầng {tang_hien_tai} thất bại!** Hãy nâng cấp trang bị, tu luyện tăng cường lực chiến rồi quay lại thử sức.")

    await kho.luu(ts)
    return kq
