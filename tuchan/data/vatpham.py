"""Vạn vật trong túi càn khôn: dược liệu, vật liệu, đan dược, pháp bảo, kỳ vật."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VatPham:
    ma: str
    ten: str
    loai: str  # duoc_lieu | vat_lieu | dan_duoc | phap_bao | ky_vat | ngoc_gian
    pham: int  # 1 đến 9 phẩm
    mo_ta: str
    gia: int = 0  # giá tham khảo ở chợ tu chân, tính bằng linh thạch hạ phẩm
    hieu_qua: dict = field(default_factory=dict)
    uy_luc: float = 0.0  # với pháp bảo
    canh_gioi_toi_thieu: int = 0

    @property
    def ten_pham(self) -> str:
        return f"{self.pham} phẩm"


def _vp(*a, **kw) -> VatPham:
    return VatPham(*a, **kw)


DANH_MUC: dict[str, VatPham] = {}


def _dang_ky(items: list[VatPham]) -> None:
    for v in items:
        DANH_MUC[v.ma] = v


# ─────────────────────────── DƯỢC LIỆU ───────────────────────────
_dang_ky([
    _vp("hoang_tinh_thao", "Hoàng Tinh Thảo", "duoc_lieu", 1,
        "Cỏ dại mọc ven khe suối, lá vàng như đồng cũ. Nhai sống có vị chát, nuốt xuống thì bụng ấm lên một lúc.",
        gia=6),
    _vp("thanh_lan_hoa", "Thanh Lan Hoa", "duoc_lieu", 1,
        "Hoa nhỏ màu xanh nhạt, nở về đêm, thơm mùi nước mưa. Kẻ luyện đan dùng để dẫn dược tính.",
        gia=10),
    _vp("huyet_tinh_chi", "Huyết Tinh Chi", "duoc_lieu", 2,
        "Nấm linh chi đỏ sẫm mọc trên xác thú, bẻ ra chảy nước như máu loãng. Cầm máu, nối gân.",
        gia=45),
    _vp("bach_van_sam", "Bạch Vân Sâm", "duoc_lieu", 3,
        "Củ sâm trắng mọc trên vách đá cao nơi mây thường vắt ngang, hình dáng như đứa trẻ co ro.",
        gia=160),
    _vp("u_dam_lien", "U Đàm Liên", "duoc_lieu", 4,
        "Sen mọc dưới đầm nước đen, cánh trong suốt. Người ta bảo nó hút âm khí của người chết đuối mà sống.",
        gia=520),
    _vp("cuu_diep_linh_lan", "Cửu Diệp Linh Lan", "duoc_lieu", 5,
        "Chín lá, chín trăm năm mới đủ chín lá. Hái nhầm lúc thì linh khí tan ngay trong tay.",
        gia=2100),
    _vp("thien_tam_qua", "Thiên Tâm Quả", "duoc_lieu", 6,
        "Quả đỏ như than hồng, đập một nhịp mỗi canh giờ. Nghe nói cây mẹ chỉ kết quả khi có người chết dưới gốc.",
        gia=9000),
    _vp("van_nien_ngoc_toai", "Vạn Niên Ngọc Tuỷ", "duoc_lieu", 7,
        "Tuỷ đá kết trong lòng núi vạn năm, lạnh đến mức cầm lâu thì bàn tay hoá đen.",
        gia=36000),
])

# ─────────────────────────── VẬT LIỆU LUYỆN KHÍ ───────────────────────────
_dang_ky([
    _vp("hac_thiet", "Hắc Thiết", "vat_lieu", 1,
        "Sắt đen thô nặng tay, gõ vào kêu đục. Món khởi đầu của mọi lò rèn nơi trấn nhỏ.", gia=12),
    _vp("thanh_dong_tinh", "Thanh Đồng Tinh", "vat_lieu", 2,
        "Tinh đồng ánh lục, đủ mềm để chịu phù văn mà không nứt.", gia=60),
    _vp("hu_khong_thach", "Hư Không Thạch", "vat_lieu", 4,
        "Đá xám nhẹ bẫng, ném lên không rơi xuống ngay. Trong đó có một khoảng trống không thuộc về đời này.", gia=700),
    _vp("lac_lo_tinh_kim", "Lạc Lô Tinh Kim", "vat_lieu", 5,
        "Kim loại rơi từ trời xuống trong một đêm sao băng, còn giữ hơi nóng của khoảng không.", gia=2800),
    _vp("giao_can", "Giao Cân", "vat_lieu", 3,
        "Gân của giao long non, dai như dây thép, ngâm nước không mục.", gia=240),
    _vp("yeu_dan", "Yêu Đan", "vat_lieu", 3,
        "Viên đan trong bụng yêu thú, còn hơi tanh. Vừa là thuốc, vừa là mồi lửa cho lò.", gia=300),
    _vp("am_hon_sa", "Âm Hồn Sa", "vat_lieu", 4,
        "Cát mịn màu tro, đổ ra bàn tự gom thành hình người rồi tan. Chính tà đều thèm.", gia=850),
    _vp("long_van_ngoc", "Long Văn Ngọc", "vat_lieu", 6,
        "Ngọc có vân như vảy rồng. Áp vào tai nghe thấy tiếng gầm rất xa.", gia=12000),
])

# ─────────────────────────── ĐAN DƯỢC ───────────────────────────
_dang_ky([
    _vp("hoi_khi_dan", "Hồi Khí Đan", "dan_duoc", 1,
        "Viên đan xám nhỏ bằng hạt đậu, nuốt vào thấy một luồng ấm chạy dọc sống lưng.",
        gia=40, hieu_qua={"tu_vi": 90}),
    _vp("bo_nguyen_dan", "Bổ Nguyên Đan", "dan_duoc", 2,
        "Đan tròn màu mật ong, mùi ngọt gắt. Nuốt xong mồ hôi ra đen như mực — ấy là tạp chất bị đẩy đi.",
        gia=200, hieu_qua={"tu_vi": 600}),
    _vp("truc_co_dan", "Trúc Cơ Đan", "dan_duoc", 3,
        "Đan trắng đục, bề mặt có một vân nứt. Trong ngàn kẻ Luyện Khí, hơn nửa chết già vì không mua nổi một viên.",
        gia=1500, hieu_qua={"dot_pha": 0.22, "chi_dung_cho": 0}),
    _vp("ket_dan_dan", "Kết Đan Đan", "dan_duoc", 5,
        "Đan vàng nhạt, đặt trong lòng bàn tay tự xoay chậm theo chiều kim đồng hồ.",
        gia=14000, hieu_qua={"dot_pha": 0.20, "chi_dung_cho": 1}),
    _vp("liem_thuong_dan", "Liễm Thương Đan", "dan_duoc", 2,
        "Đan xanh rêu, đắng đến tê lưỡi. Xương gãy nối lại trong ba ngày, nhưng chỗ nối sẽ nhức mỗi khi trở trời.",
        gia=180, hieu_qua={"tri_thuong": 55}),
    _vp("hoan_hon_dan", "Hoàn Hồn Đan", "dan_duoc", 4,
        "Kéo người từ mép cửa quỷ về. Chỉ kéo được một lần, lần sau quỷ sẽ nắm chặt hơn.",
        gia=2600, hieu_qua={"tri_thuong": 100, "dao_tam": 3}),
    _vp("dinh_than_dan", "Định Thần Đan", "dan_duoc", 3,
        "Ngậm dưới lưỡi, tạp niệm lắng xuống như bùn lắng đáy chum.",
        gia=600, hieu_qua={"dao_tam": 8}),
    _vp("tay_tuy_dan", "Tẩy Tuỷ Đan", "dan_duoc", 4,
        "Rửa tuỷ đổi cốt. Người uống phải chịu ba canh giờ đau như bị lột da, xong thì thân nhẹ như lá.",
        gia=3400, hieu_qua={"tu_vi": 4200, "can_cot": 2}),
])

# ─────────────────────────── PHÁP BẢO ───────────────────────────
_dang_ky([
    _vp("thanh_cuong_kiem", "Thanh Cương Kiếm", "phap_bao", 1,
        "Kiếm sắt thô, lưỡi mài đến trắng. Không có phù văn nào, chỉ có vết mẻ của kẻ chủ trước.",
        gia=90, uy_luc=0.10),
    _vp("hac_van_phi_dao", "Hắc Vân Phi Đao", "phap_bao", 2,
        "Đao nhỏ bằng bàn tay, thả ra hoá thành một vệt khói đen, cắt xong mới nghe tiếng gió.",
        gia=850, uy_luc=0.26, canh_gioi_toi_thieu=1),
    _vp("thanh_lan_phu", "Thanh Lân Phù Giáp", "phap_bao", 3,
        "Áo giáp vảy xanh mỏng như lụa, mặc vào nghe tiếng nước chảy rất khẽ bên tai.",
        gia=3200, uy_luc=0.30, canh_gioi_toi_thieu=1),
    _vp("cuu_khuc_lien_hoan", "Cửu Khúc Liên Hoàn Toả", "phap_bao", 4,
        "Chín vòng xích nối nhau, ném ra thì trói cả không gian, kẻ bị trói nghe tiếng chín người tụng kinh.",
        gia=11000, uy_luc=0.42, canh_gioi_toi_thieu=2),
    _vp("phach_thien_chuy", "Phách Thiên Chuỳ", "phap_bao", 5,
        "Chuỳ đồng đen nặng nghìn cân, vung một cái thì gió bị chẻ làm đôi, mặt đất nứt theo hình rễ cây.",
        gia=42000, uy_luc=0.58, canh_gioi_toi_thieu=2),
    _vp("u_minh_phan", "U Minh Phướn", "phap_bao", 6,
        "Phướn đen thêu tên người chết. Mỗi lần dùng, một cái tên mờ đi — và một cái tên mới hiện ra.",
        gia=160000, uy_luc=0.75, canh_gioi_toi_thieu=3),
    _vp("thai_hu_kinh", "Thái Hư Kính", "phap_bao", 7,
        "Gương đồng không soi mặt người, chỉ soi thấy chỗ sơ hở trong đạo pháp của kẻ đối diện.",
        gia=600000, uy_luc=0.92, canh_gioi_toi_thieu=4),
])

# ─────────────────────────── KỲ VẬT / NGỌC GIẢN ───────────────────────────
_dang_ky([
    _vp("linh_thach_ha", "Linh Thạch Hạ Phẩm", "ky_vat", 1,
        "Viên đá xanh nhạt, áp vào trán thấy mát. Tiền bạc của người tu hành.", gia=1),
    _vp("co_tich_tan_do", "Tàn Đồ Cổ Tích", "ky_vat", 3,
        "Mảnh da thú vẽ nửa tấm bản đồ, mép cháy sém. Nửa còn lại nằm trong tay ai đó — hoặc trong bụng ai đó.",
        gia=1800),
    _vp("truyen_tong_phu", "Truyền Tống Phù", "ky_vat", 3,
        "Bùa giấy vàng, bóp vỡ thì thân xác bị kéo đi ba trăm dặm. Dùng xong thường nôn mửa.",
        gia=900),
    _vp("hoan_hinh_ngoc_gian", "Ngọc Giản Cũ", "ngoc_gian", 2,
        "Ngọc giản sứt mẻ, thần thức quét vào thấy chữ nhảy múa. Có thể chứa một đan phương hoặc một khẩu quyết.",
        gia=500),
    _vp("yeu_thu_noi_dan", "Nội Đan Yêu Thú", "vat_lieu", 4,
        "Nội đan của con thú đã tu thành hình người trong mộng. Nuốt thì tăng tu vi, nhưng tính khí sẽ đổi.",
        gia=5200, hieu_qua={"tu_vi": 3000, "sat_nghiep": 2}),
])


def lay(ma: str) -> VatPham | None:
    return DANH_MUC.get(ma)


def ten(ma: str) -> str:
    v = DANH_MUC.get(ma)
    return v.ten if v else ma


def theo_loai(loai: str) -> list[VatPham]:
    return [v for v in DANH_MUC.values() if v.loai == loai]
