"""Hệ thống Kỹ Năng / Bí Thuật / Công Pháp cho Tu Tiên Chiến Đấu."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KyNang:
    ma: str
    ten: str
    he: str  # "Kiếm", "Hỏa", "Lôi", "Mộc", "Kim", "Băng", "Ma", "Đạo"
    icon: str
    loai: str  # "sat_thuong", "phong_ngu", "tri_lieu", "buff"
    canh_gioi: int  # Cảnh giới tối thiểu để học (0: Luyện Khí, 1: Trúc Cơ, 2: Kết Đan, 3: Nguyên Anh)
    canh_gioi_ten: str
    mp: int  # Chân khí tiêu hao
    he_so_sat_thuong: float  # Hệ số công kích (ví dụ: 1.4x ATK)
    sat_thuong_co_dinh: int  # Sát thương cộng thêm
    he_so_hoi_phuc: float = 0.0  # Hệ số hồi phục HP (cho chiêu trị liệu)
    he_so_la_chan: float = 0.0  # Tạo giáp ảo hấp thu sát thương
    tang_bao_kich: float = 0.0  # Tăng tỷ lệ bạo kích (%)
    hoi_chieu: int = 1  # Số hiệp hồi chiêu
    mo_ta: str = ""
    gia_linh_thach: int = 50  # Giá mở khóa ban đầu
    gia_tu_vi: int = 100  # Giá mở khóa / nâng cấp ban đầu


DANH_SACH_KY_NANG: dict[str, KyNang] = {
    # ── Bậc 1: Luyện Khí Kỳ ──
    "kiem_khi_tram": KyNang(
        ma="kiem_khi_tram",
        ten="Kiếm Khí Trảm",
        he="Kiếm",
        icon="🗡️",
        loai="sat_thuong",
        canh_gioi=0,
        canh_gioi_ten="Luyện Khí",
        mp=20,
        he_so_sat_thuong=1.35,
        sat_thuong_co_dinh=35,
        tang_bao_kich=5.0,
        hoi_chieu=1,
        mo_ta="Dồn chân khí vào đầu mũi kiếm chém ra luồng kiếm khí sắc bén xé gió.",
        gia_linh_thach=0,
        gia_tu_vi=0,
    ),
    "kim_cuong_ho_the": KyNang(
        ma="kim_cuong_ho_the",
        ten="Kim Cương Hộ Thể",
        he="Kim",
        icon="🛡️",
        loai="phong_ngu",
        canh_gioi=0,
        canh_gioi_ten="Luyện Khí",
        mp=25,
        he_so_sat_thuong=0.6,
        sat_thuong_co_dinh=15,
        he_so_la_chan=0.35,
        hoi_chieu=2,
        mo_ta="Tụ kim khí bao bọc thân thể tạo thành kim cương hộ thể, hấp thu sát thương.",
        gia_linh_thach=0,
        gia_tu_vi=0,
    ),
    "liet_diem_chuong": KyNang(
        ma="liet_diem_chuong",
        ten="Liệt Diễm Chưởng",
        he="Hỏa",
        icon="🔥",
        loai="sat_thuong",
        canh_gioi=0,
        canh_gioi_ten="Luyện Khí",
        mp=30,
        he_so_sat_thuong=1.5,
        sat_thuong_co_dinh=50,
        tang_bao_kich=8.0,
        hoi_chieu=1,
        mo_ta="Chưởng pháp mang theo liệt hỏa rừng rực, thiêu đốt nguyên khí đối thủ.",
        gia_linh_thach=60,
        gia_tu_vi=120,
    ),
    "thanh_moc_hoi_xuan": KyNang(
        ma="thanh_moc_hoi_xuan",
        ten="Thanh Mộc Hồi Xuân",
        he="Mộc",
        icon="🌿",
        loai="tri_lieu",
        canh_gioi=0,
        canh_gioi_ten="Luyện Khí",
        mp=25,
        he_so_sat_thuong=0.0,
        sat_thuong_co_dinh=0,
        he_so_hoi_phuc=0.3,
        hoi_chieu=2,
        mo_ta="Dẫn mộc linh chi khí vào đan điền, nhanh chóng hồi phục 30% sinh mệnh.",
        gia_linh_thach=80,
        gia_tu_vi=150,
    ),

    # ── Bậc 2: Trúc Cơ Kỳ ──
    "han_bang_kiem_khi": KyNang(
        ma="han_bang_kiem_khi",
        ten="Hàn Băng Kiếm Khí",
        he="Băng",
        icon="❄️",
        loai="sat_thuong",
        canh_gioi=1,
        canh_gioi_ten="Trúc Cơ",
        mp=40,
        he_so_sat_thuong=1.75,
        sat_thuong_co_dinh=120,
        tang_bao_kich=12.0,
        hoi_chieu=2,
        mo_ta="Kiếm khí thấu xương làm đông cứng chân nguyên đối thủ, bạo kích cực cao.",
        gia_linh_thach=200,
        gia_tu_vi=400,
    ),
    "cuu_thien_loi": KyNang(
        ma="cuu_thien_loi",
        ten="Cửu Thiên Lôi Lạc",
        he="Lôi",
        icon="⚡",
        loai="sat_thuong",
        canh_gioi=1,
        canh_gioi_ten="Trúc Cơ",
        mp=50,
        he_so_sat_thuong=2.1,
        sat_thuong_co_dinh=180,
        tang_bao_kich=15.0,
        hoi_chieu=2,
        mo_ta="Dẫn thiên kiếp lôi đình giáng xuống oanh kích, gây sát thương bộc phá khổng lồ.",
        gia_linh_thach=300,
        gia_tu_vi=600,
    ),
    "huyen_quy_thuan": KyNang(
        ma="huyen_quy_thuan",
        ten="Huyền Quy Hộ Thuẫn",
        he="Kim",
        icon="🛡️",
        loai="phong_ngu",
        canh_gioi=1,
        canh_gioi_ten="Trúc Cơ",
        mp=45,
        he_so_sat_thuong=0.5,
        sat_thuong_co_dinh=50,
        he_so_la_chan=0.55,
        hoi_chieu=3,
        mo_ta="Tạo nên một tầng hộ giáp Huyền Quy bất hoại, hấp thu hơn một nửa sát thương nhận vào.",
        gia_linh_thach=250,
        gia_tu_vi=500,
    ),
    "ma_dao_cuong_no": KyNang(
        ma="ma_dao_cuong_no",
        ten="Ma Đạo Cuồng Nộ",
        he="Ma",
        icon="🩸",
        loai="buff",
        canh_gioi=1,
        canh_gioi_ten="Trúc Cơ",
        mp=35,
        he_so_sat_thuong=2.4,
        sat_thuong_co_dinh=220,
        tang_bao_kich=25.0,
        hoi_chieu=3,
        mo_ta="Vận dụng ma đạo bí pháp, cuồng bạo kích phát tiềm năng tạo đòn chí mạng x2.4 sát thương.",
        gia_linh_thach=400,
        gia_tu_vi=800,
    ),

    # ── Bậc 3: Kim Đan Kỳ ──
    "van_kiem_quy_tong": KyNang(
        ma="van_kiem_quy_tong",
        ten="Vạn Kiếm Quy Tông",
        he="Kiếm",
        icon="⚔️",
        loai="sat_thuong",
        canh_gioi=2,
        canh_gioi_ten="Kim Đan",
        mp=70,
        he_so_sat_thuong=2.8,
        sat_thuong_co_dinh=450,
        tang_bao_kich=20.0,
        hoi_chieu=3,
        mo_ta="Tuyệt học đỉnh cao kiếm đạo, hàng vạn thanh kiếm ảnh xé toạc không gian trấn áp càn khôn.",
        gia_linh_thach=800,
        gia_tu_vi=1800,
    ),
    "thai_cuc_chuong": KyNang(
        ma="thai_cuc_chuong",
        ten="Thái Cực Bát Quái",
        he="Đạo",
        icon="☯️",
        loai="phong_ngu",
        canh_gioi=2,
        canh_gioi_ten="Kim Đan",
        mp=65,
        he_so_sat_thuong=1.8,
        sat_thuong_co_dinh=300,
        he_so_hoi_phuc=0.25,
        he_so_la_chan=0.4,
        hoi_chieu=3,
        mo_ta="Lấy nhu thắng cương, chuyển hóa chân khí đất trời, vừa gây sát thương vừa tạo thuẫn và hồi máu.",
        gia_linh_thach=1000,
        gia_tu_vi=2200,
    ),

    # ── Bậc 4: Nguyên Anh Kỳ ──
    "tram_tien_kiem": KyNang(
        ma="tram_tien_kiem",
        ten="Trảm Tiên Nhất Kiếm",
        he="Kiếm",
        icon="🌟",
        loai="sat_thuong",
        canh_gioi=3,
        canh_gioi_ten="Nguyên Anh",
        mp=100,
        he_so_sat_thuong=3.6,
        sat_thuong_co_dinh=1000,
        tang_bao_kich=35.0,
        hoi_chieu=4,
        mo_ta="Một kiếm trảm tiên, nghịch chuyển thiên đạo, sát thương hủy thiên diệt địa.",
        gia_linh_thach=2500,
        gia_tu_vi=5000,
    ),
    "diet_the_than_loi": KyNang(
        ma="diet_the_than_loi",
        ten="Diệt Thế Thần Lôi",
        he="Lôi",
        icon="⚡",
        loai="sat_thuong",
        canh_gioi=3,
        canh_gioi_ten="Nguyên Anh",
        mp=120,
        he_so_sat_thuong=4.2,
        sat_thuong_co_dinh=1400,
        tang_bao_kich=40.0,
        hoi_chieu=4,
        mo_ta="Triệu hoán thần lôi diệt thế, biến vạn dặm thành tro bụi, sát thương vô địch.",
        gia_linh_thach=3500,
        gia_tu_vi=8000,
    ),
}


def lay_ky_nang(ma: str) -> KyNang | None:
    return DANH_SACH_KY_NANG.get(ma)


def ky_nang_theo_canh_gioi(canh_gioi: int) -> list[KyNang]:
    return [kn for kn in DANH_SACH_KY_NANG.values() if kn.canh_gioi <= canh_gioi]
