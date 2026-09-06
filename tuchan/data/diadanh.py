"""Địa danh — nơi để đi, để tìm, để chết."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DiaDanh:
    ma: str
    ten: str
    canh_gioi_toi_thieu: int
    nguy_hiem: float  # 0..1
    mo_ta: str
    canh_vat: tuple[str, ...]  # những câu tả cảnh rời rạc, bốc ngẫu nhiên
    duoc_lieu: tuple[str, ...]
    vat_lieu: tuple[str, ...]
    dich_thu: tuple[str, ...]
    trong_so: dict[str, float]  # duoc | lieu | dich | ky_ngo | co_tich | hu_khong
    tranh: str = ""


DANH_SACH: dict[str, DiaDanh] = {}


def _dd(d: DiaDanh) -> None:
    DANH_SACH[d.ma] = d


_dd(DiaDanh(
    ma="thanh_khe_son", ten="Thanh Khê Sơn", canh_gioi_toi_thieu=0, nguy_hiem=0.18,
    mo_ta=(
        "Ngọn núi thấp phía sau trấn Thạch Khẩu, dân chài vẫn lên đây kiếm củi. "
        "Linh khí mỏng như hơi thở người ốm, nhưng với kẻ mới nhập đạo thì đây đã là cả một kho báu."
    ),
    canh_vat=(
        "Suối chảy qua khe đá, nước lạnh đến buốt răng. Ngươi cúi xuống uống một ngụm và thấy mặt mình gầy đi nhiều.",
        "Một cây tùng già bị sét đánh cụt ngọn vẫn cố mọc thêm một nhánh về phía đông.",
        "Trên tảng đá bằng có khắc mấy chữ đã mòn: 'Ngồi đây, đợi người.' Không rõ đợi ai, không rõ đã bao lâu.",
        "Sương xuống sớm. Tiếng chim gõ kiến vang lên đều đặn, rồi ngừng bặt — như thể có gì khiến nó im.",
    ),
    duoc_lieu=("hoang_tinh_thao", "hoang_tinh_thao", "thanh_lan_hoa"),
    vat_lieu=("hac_thiet",),
    dich_thu=("xich_mao_lang", "thach_giap_thu"),
    trong_so={"duoc": 34, "lieu": 18, "dich": 22, "canh": 16, "ky_ngo": 8, "co_tich": 2},
))
_dd(DiaDanh(
    ma="hac_phong_lam", ten="Hắc Phong Lâm", canh_gioi_toi_thieu=0, nguy_hiem=0.38,
    mo_ta=(
        "Rừng thông đen trải dài ba trăm dặm, giữa ban ngày cũng tối như chạng vạng. "
        "Người ta bảo trong rừng có thứ đi bằng hai chân nhưng không phải người. "
        "Thợ săn vào rừng thường đi ba người, và thường về hai."
    ),
    canh_vat=(
        "Sương mù bò sát mặt đất, cuốn quanh mắt cá chân ngươi rồi tan ra một cách miễn cưỡng.",
        "Ngươi đi ngang một cái cây có khắc dấu — dấu của người dẫn đường. Nhưng dấu ấy chỉ về hướng ngươi vừa tới.",
        "Có tiếng bước chân đi song song với ngươi bên trái, cách chừng mười trượng. Ngươi dừng, nó cũng dừng.",
        "Một bộ hài cốt mặc áo tu sĩ ngồi tựa gốc thông, tay vẫn giữ tư thế bắt quyết. Trên xương ngón có một vết răng.",
    ),
    duoc_lieu=("hoang_tinh_thao", "thanh_lan_hoa", "huyet_tinh_chi"),
    vat_lieu=("hac_thiet", "yeu_dan"),
    dich_thu=("xich_mao_lang", "thi_ma", "tan_tu_cuop_duong"),
    trong_so={"duoc": 28, "lieu": 16, "dich": 32, "canh": 15, "ky_ngo": 7, "co_tich": 2},
    tranh="hac_phong_lam.png",
))
_dd(DiaDanh(
    ma="van_thach_nhai", ten="Vân Thạch Nhai", canh_gioi_toi_thieu=0, nguy_hiem=0.45,
    mo_ta=(
        "Vách đá dựng đứng cao nghìn trượng, mây vắt ngang lưng chừng như một dải khăn tang. "
        "Trên vách mọc thứ sâm trắng mà một củ đủ nuôi cả nhà phàm nhân ba đời. "
        "Dưới chân vách là một bãi đá lởm chởm, và không ai buồn dọn xương ở đó."
    ),
    canh_vat=(
        "Gió trên vách thổi ngược từ dưới lên, đẩy vạt áo ngươi bay ngược về phía trời.",
        "Ngươi bám vào một mấu đá, và mấu đá ấy vỡ ra trong tay. Ngươi treo trên một cánh tay suốt mười nhịp thở.",
        "Từ dưới vực vọng lên tiếng gì đó rất giống tiếng người gọi tên ngươi. Ngươi biết là không phải.",
    ),
    duoc_lieu=("bach_van_sam", "thanh_lan_hoa", "huyet_tinh_chi"),
    vat_lieu=("thanh_dong_tinh", "hac_thiet"),
    dich_thu=("thanh_dieu", "tan_tu_cuop_duong"),
    trong_so={"duoc": 32, "lieu": 18, "dich": 24, "canh": 14, "ky_ngo": 9, "co_tich": 3},
))
_dd(DiaDanh(
    ma="u_dam_trach", ten="U Đàm Trạch", canh_gioi_toi_thieu=1, nguy_hiem=0.55,
    mo_ta=(
        "Đầm lầy nước đen rộng không thấy bờ, mặt nước phẳng lì không một gợn. "
        "Sen U Đàm nở về đêm, và người ta nói mỗi bông sen là một người chết đuối chưa siêu thoát. "
        "Ai hái sen ở đây đều phải để lại một thứ gì đó."
    ),
    canh_vat=(
        "Bùn hút lấy chân ngươi, mỗi bước rút lên đều kêu một tiếng như tiếng thở dài.",
        "Trên mặt nước đen, ngươi thấy bóng mình. Nhưng bóng ấy quay đầu trước ngươi một nhịp.",
        "Đom đóm bay thành hàng dài, đều tăm tắp, như một đoàn đưa tang.",
    ),
    duoc_lieu=("u_dam_lien", "huyet_tinh_chi", "bach_van_sam"),
    vat_lieu=("giao_can", "am_hon_sa"),
    dich_thu=("hac_lan_giao", "thi_ma"),
    trong_so={"duoc": 30, "lieu": 18, "dich": 30, "canh": 12, "ky_ngo": 7, "co_tich": 3},
))
_dd(DiaDanh(
    ma="lac_tinh_hoang_nguyen", ten="Lạc Tinh Hoang Nguyên", canh_gioi_toi_thieu=1, nguy_hiem=0.60,
    mo_ta=(
        "Một vùng đất chết trải dài, đất nứt thành vảy, không có cây nào cao quá đầu gối. "
        "Ba trăm năm trước có thứ gì đó rơi từ trời xuống đây. Người ta đã đào, đã tranh, đã giết nhau — "
        "và rồi bỏ đi, để lại những hố đào há miệng như những cái mồm."
    ),
    canh_vat=(
        "Ban đêm, mặt đất còn ấm. Ngươi nằm xuống và nghe thấy dưới lớp đất có gì đó đang kêu ro ro rất khẽ.",
        "Một hố đào cũ, dưới đáy có cuốc, có xẻng, có cả một bàn tay khô còn nắm chặt cán cuốc.",
        "Gió cát thổi qua làm lộ ra một mảng kim loại lấp lánh, rồi lại phủ kín trong chớp mắt.",
    ),
    duoc_lieu=("huyet_tinh_chi", "bach_van_sam"),
    vat_lieu=("lac_lo_tinh_kim", "hu_khong_thach", "thanh_dong_tinh"),
    dich_thu=("huyet_nhan_vuon", "hac_bao_ma_tu", "ky_si_vo_danh"),
    trong_so={"duoc": 18, "lieu": 34, "dich": 30, "canh": 10, "ky_ngo": 6, "co_tich": 2},
))
_dd(DiaDanh(
    ma="thien_chung_dong", ten="Thiên Chung Động", canh_gioi_toi_thieu=1, nguy_hiem=0.50,
    mo_ta=(
        "Một động thiên nhiên trong lòng núi, trần động treo đầy nhũ đá như răng thú. "
        "Cứ mỗi canh giờ, trong động lại vang lên một tiếng ngân dài như chuông đồng — "
        "không ai tìm được cái chuông ấy ở đâu."
    ),
    canh_vat=(
        "Tiếng chuông vang lên. Ngươi thấy trong lồng ngực mình có cái gì đó ngân theo, và thấy sợ.",
        "Vách động khắc đầy chữ cổ, chồng lên nhau qua nhiều đời, như thể ai đến cũng muốn để lại một câu.",
        "Nước nhỏ từ nhũ đá xuống một vũng nhỏ, trong vũng có mấy đồng linh thạch đã mờ hết linh khí.",
    ),
    duoc_lieu=("van_nien_ngoc_toai", "u_dam_lien"),
    vat_lieu=("hu_khong_thach", "thanh_dong_tinh", "hac_thiet"),
    dich_thu=("thi_ma", "thach_giap_thu", "co_thi_tuong"),
    trong_so={"duoc": 22, "lieu": 26, "dich": 26, "canh": 12, "ky_ngo": 8, "co_tich": 6},
))
_dd(DiaDanh(
    ma="van_cot_nhai", ten="Vạn Cốt Nhai", canh_gioi_toi_thieu=2, nguy_hiem=0.78,
    mo_ta=(
        "Nơi đây từng là chiến trường của hai tông môn đã diệt vong. Xương chất thành gò, "
        "gò lâu ngày thành đồi, đồi lâu ngày mọc cỏ. Cỏ ở Vạn Cốt Nhai có màu tím nhạt "
        "và mọc rất tốt."
    ),
    canh_vat=(
        "Ngươi bước lên một chỗ đất mềm. Cúi xuống nhìn, đó không phải đất.",
        "Một thanh kiếm cắm thẳng đứng, gỉ hết, nhưng phù văn trên chuôi vẫn còn sáng rất yếu.",
        "Oán khí bốc lên thành sương tím. Trong sương có tiếng người, rất nhiều người, nói cùng một lúc, "
        "và tất cả đều đang xin tha.",
    ),
    duoc_lieu=("cuu_diep_linh_lan", "u_dam_lien", "van_nien_ngoc_toai"),
    vat_lieu=("am_hon_sa", "lac_lo_tinh_kim", "long_van_ngoc"),
    dich_thu=("co_thi_tuong", "hac_bao_ma_tu", "huyet_nhan_vuon"),
    trong_so={"duoc": 22, "lieu": 24, "dich": 34, "canh": 9, "ky_ngo": 6, "co_tich": 5},
))
_dd(DiaDanh(
    ma="cuu_u_han_uyen", ten="Cửu U Hàn Uyên", canh_gioi_toi_thieu=3, nguy_hiem=0.88,
    mo_ta=(
        "Vực sâu dưới đáy Bắc Hải, nước lạnh đến mức Nguyên Anh tu sĩ cũng phải vận công liên tục. "
        "Dưới đáy vực có ánh sáng — thứ ánh sáng không nên có ở nơi sâu như vậy."
    ),
    canh_vat=(
        "Áp lực nước đè lên hộ thể linh quang của ngươi, mỗi khắc một nặng thêm một phần.",
        "Ngươi bơi ngang qua một cái xác khổng lồ đã hoá đá, dài không thấy đầu, không thấy đuôi.",
        "Ánh sáng dưới đáy tắt đi trong một nhịp thở, rồi sáng lại. Nó vừa chớp mắt.",
    ),
    duoc_lieu=("van_nien_ngoc_toai", "thien_tam_qua", "cuu_diep_linh_lan"),
    vat_lieu=("long_van_ngoc", "lac_lo_tinh_kim", "hu_khong_thach"),
    dich_thu=("hac_lan_giao", "co_thi_tuong", "hac_bao_ma_tu"),
    trong_so={"duoc": 26, "lieu": 24, "dich": 32, "canh": 8, "ky_ngo": 6, "co_tich": 4},
))


def lay(ma: str) -> DiaDanh | None:
    return DANH_SACH.get(ma)


def cho_phep(canh_gioi: int) -> list[DiaDanh]:
    ra = [d for d in DANH_SACH.values() if d.canh_gioi_toi_thieu <= canh_gioi]
    return ra or [DANH_SACH["thanh_khe_son"]]


def tim_theo_ten(chuoi: str) -> DiaDanh | None:
    chuoi = (chuoi or "").strip().lower()
    if not chuoi:
        return None
    for d in DANH_SACH.values():
        if chuoi == d.ma or chuoi in d.ten.lower():
            return d
    return None
