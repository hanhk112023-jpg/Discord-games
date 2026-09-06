"""Đan phương và khí phương — những trang giấy đáng giá hơn mạng người."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CongThuc:
    ma: str
    ten: str
    loai: str  # "dan" | "khi"
    nguyen_lieu: dict[str, int]
    thanh_pham: str
    so_luong: tuple[int, int] = (1, 1)
    do_kho: float = 0.35  # 0 dễ, 1 gần như bất khả
    canh_gioi_toi_thieu: int = 0
    lai_lich: str = ""
    mo_ta: str = ""


DAN_PHUONG: dict[str, CongThuc] = {}
KHI_PHUONG: dict[str, CongThuc] = {}


def _d(ct: CongThuc) -> None:
    (DAN_PHUONG if ct.loai == "dan" else KHI_PHUONG)[ct.ma] = ct


_d(CongThuc(
    ma="ct_hoi_khi", ten="Hồi Khí Đan phương", loai="dan",
    nguyen_lieu={"hoang_tinh_thao": 3, "thanh_lan_hoa": 1},
    thanh_pham="hoi_khi_dan", so_luong=(1, 3), do_kho=0.20,
    lai_lich="Chép tay, truyền khắp các trấn nhỏ, ai cũng có mà chẳng ai quý.",
    mo_ta="Lửa nhỏ, ba lần đảo dược, chờ khói chuyển từ trắng sang xanh thì đóng lò.",
))
_d(CongThuc(
    ma="ct_liem_thuong", ten="Liễm Thương Đan phương", loai="dan",
    nguyen_lieu={"huyet_tinh_chi": 2, "hoang_tinh_thao": 4},
    thanh_pham="liem_thuong_dan", so_luong=(1, 2), do_kho=0.30,
    lai_lich="Của một lang y già trong quân, đổi lấy nửa vò rượu.",
    mo_ta="Máu nấm phải ép trước khi vào lò, nếu không dược tính sẽ cắn nhau.",
))
_d(CongThuc(
    ma="ct_bo_nguyen", ten="Bổ Nguyên Đan phương", loai="dan",
    nguyen_lieu={"bach_van_sam": 1, "thanh_lan_hoa": 3, "yeu_dan": 1},
    thanh_pham="bo_nguyen_dan", so_luong=(1, 2), do_kho=0.40, canh_gioi_toi_thieu=0,
    lai_lich="Đan phương phổ thông của các tông môn trung đẳng.",
    mo_ta="Yêu đan phải bỏ vào sau cùng, khi đáy lò đã đỏ như mặt trời lặn.",
))
_d(CongThuc(
    ma="ct_dinh_than", ten="Định Thần Đan phương", loai="dan",
    nguyen_lieu={"u_dam_lien": 1, "thanh_lan_hoa": 2},
    thanh_pham="dinh_than_dan", so_luong=(1, 2), do_kho=0.45,
    lai_lich="Đổi từ một hoà thượng câm ở Vọng Hải Tự.",
    mo_ta="Không được nghĩ ngợi khi luyện. Tâm loạn thì đan thành độc.",
))
_d(CongThuc(
    ma="ct_truc_co", ten="Trúc Cơ Đan phương", loai="dan",
    nguyen_lieu={"bach_van_sam": 2, "u_dam_lien": 1, "huyet_tinh_chi": 3, "yeu_dan": 2},
    thanh_pham="truc_co_dan", so_luong=(1, 1), do_kho=0.62, canh_gioi_toi_thieu=0,
    lai_lich="Bản chép lại từ Thanh Vân Môn, thiếu mất hai dòng chú giải.",
    mo_ta="Bảy ngày bảy đêm không rời lò. Nhiều kẻ luyện tới ngày thứ sáu thì gục.",
))
_d(CongThuc(
    ma="ct_tay_tuy", ten="Tẩy Tuỷ Đan phương", loai="dan",
    nguyen_lieu={"cuu_diep_linh_lan": 1, "van_nien_ngoc_toai": 1, "huyet_tinh_chi": 4},
    thanh_pham="tay_tuy_dan", so_luong=(1, 1), do_kho=0.70, canh_gioi_toi_thieu=1,
    lai_lich="Trong một cổ tích dưới đáy hồ, khắc trên xương sườn của ai đó.",
    mo_ta="Ngọc tuỷ phải giữ lạnh tới khoảnh khắc cuối, chớ để hơi người làm nó ấm lên.",
))
_d(CongThuc(
    ma="ct_ket_dan", ten="Kết Đan Đan phương", loai="dan",
    nguyen_lieu={"thien_tam_qua": 1, "cuu_diep_linh_lan": 2, "van_nien_ngoc_toai": 1, "yeu_thu_noi_dan": 1},
    thanh_pham="ket_dan_dan", so_luong=(1, 1), do_kho=0.80, canh_gioi_toi_thieu=1,
    lai_lich="Chỉ trưởng lão đan đường mới được đọc. Ngươi có nó, tức là có người đã chết.",
    mo_ta="Thiên Tâm Quả đập một nhịp mỗi canh giờ; phải hạ hoả đúng vào nhịp thứ chín.",
))
_d(CongThuc(
    ma="ct_hoan_hon", ten="Hoàn Hồn Đan phương", loai="dan",
    nguyen_lieu={"thien_tam_qua": 1, "u_dam_lien": 2, "am_hon_sa": 1},
    thanh_pham="hoan_hon_dan", so_luong=(1, 1), do_kho=0.72, canh_gioi_toi_thieu=1,
    lai_lich="Nửa chính nửa tà. Cầm nó trong tay thì đừng khoe với người cùng đạo.",
    mo_ta="Khi khói bốc lên có hình mặt người thì đừng nhìn thẳng.",
))

# ─────────────────── KHÍ PHƯƠNG ───────────────────
_d(CongThuc(
    ma="kp_thanh_cuong", ten="Thanh Cương Kiếm đồ", loai="khi",
    nguyen_lieu={"hac_thiet": 4},
    thanh_pham="thanh_cuong_kiem", do_kho=0.22,
    lai_lich="Bản vẽ dán trên vách lò rèn của trấn Thạch Khẩu.",
    mo_ta="Nung đỏ, gấp bảy lần, tôi trong nước giếng lúc gà chưa gáy.",
))
_d(CongThuc(
    ma="kp_hac_van", ten="Hắc Vân Phi Đao đồ", loai="khi",
    nguyen_lieu={"thanh_dong_tinh": 3, "hac_thiet": 5, "yeu_dan": 1},
    thanh_pham="hac_van_phi_dao", do_kho=0.42, canh_gioi_toi_thieu=0,
    lai_lich="Của một tán tu chết bên đường, trong tay còn nắm chặt bản vẽ.",
    mo_ta="Khắc phù văn khi kim loại còn mềm, tay run một cái là hỏng cả mẻ.",
))
_d(CongThuc(
    ma="kp_thanh_lan", ten="Thanh Lân Phù Giáp đồ", loai="khi",
    nguyen_lieu={"giao_can": 3, "thanh_dong_tinh": 4, "hu_khong_thach": 1},
    thanh_pham="thanh_lan_phu", do_kho=0.55, canh_gioi_toi_thieu=1,
    lai_lich="Huyền Vũ Tông ban cho đệ tử có công.",
    mo_ta="Từng vảy phải xếp ngược chiều nước chảy, nếu không giáp sẽ tự cắn lấy chủ.",
))
_d(CongThuc(
    ma="kp_cuu_khuc", ten="Cửu Khúc Liên Hoàn Toả đồ", loai="khi",
    nguyen_lieu={"lac_lo_tinh_kim": 2, "hu_khong_thach": 3, "giao_can": 4},
    thanh_pham="cuu_khuc_lien_hoan", do_kho=0.66, canh_gioi_toi_thieu=2,
    lai_lich="Khắc trong một hang đá, bên cạnh là chín bộ xương xếp thành vòng tròn.",
    mo_ta="Mỗi vòng xích là một câu chú. Đọc sai một chữ, xích sẽ trói chính ngươi.",
))
_d(CongThuc(
    ma="kp_phach_thien", ten="Phách Thiên Chuỳ đồ", loai="khi",
    nguyen_lieu={"lac_lo_tinh_kim": 4, "long_van_ngoc": 1, "am_hon_sa": 2},
    thanh_pham="phach_thien_chuy", do_kho=0.78, canh_gioi_toi_thieu=2,
    lai_lich="Di vật của một lão ma đầu đã bị chôn dưới Vạn Cốt Nhai.",
    mo_ta="Lò phải đặt nơi có sấm. Không có sấm thì đợi, có kẻ đợi ba mươi năm.",
))

TAT_CA: dict[str, CongThuc] = {**DAN_PHUONG, **KHI_PHUONG}


def lay(ma: str) -> CongThuc | None:
    return TAT_CA.get(ma)
