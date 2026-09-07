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
    loai_vu_khi: str = ""  # kiem | dao | thuong | phi_kiem | cung | ti | phu | giap |
                           # chuong | an | phuong | but | quat | dinh | chuy | kinh | dai
    ghi_chu: str = ""      # một câu về lai lịch, hiện khi hỏi kỹ

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
        gia=90, uy_luc=0.10, loai_vu_khi="kiem"),
    _vp("hac_van_phi_dao", "Hắc Vân Phi Đao", "phap_bao", 2,
        "Đao nhỏ bằng bàn tay, thả ra hoá thành một vệt khói đen, cắt xong mới nghe tiếng gió.",
        gia=850, uy_luc=0.26, canh_gioi_toi_thieu=1, loai_vu_khi="phi_kiem"),
    _vp("thanh_lan_phu", "Thanh Lân Phù Giáp", "phap_bao", 3,
        "Áo giáp vảy xanh mỏng như lụa, mặc vào nghe tiếng nước chảy rất khẽ bên tai.",
        gia=3200, uy_luc=0.30, canh_gioi_toi_thieu=1, loai_vu_khi="giap"),
    _vp("cuu_khuc_lien_hoan", "Cửu Khúc Liên Hoàn Toả", "phap_bao", 4,
        "Chín vòng xích nối nhau, ném ra thì trói cả không gian, kẻ bị trói nghe tiếng chín người tụng kinh.",
        gia=11000, uy_luc=0.42, canh_gioi_toi_thieu=2, loai_vu_khi="ti"),
    _vp("phach_thien_chuy", "Phách Thiên Chuỳ", "phap_bao", 5,
        "Chuỳ đồng đen nặng nghìn cân, vung một cái thì gió bị chẻ làm đôi, mặt đất nứt theo hình rễ cây.",
        gia=42000, uy_luc=0.58, canh_gioi_toi_thieu=2, loai_vu_khi="chuy"),
    _vp("u_minh_phan", "U Minh Phướn", "phap_bao", 6,
        "Phướn đen thêu tên người chết. Mỗi lần dùng, một cái tên mờ đi — và một cái tên mới hiện ra.",
        gia=160000, uy_luc=0.75, canh_gioi_toi_thieu=3, loai_vu_khi="phuong"),
    _vp("thai_hu_kinh", "Thái Hư Kính", "phap_bao", 7,
        "Gương đồng không soi mặt người, chỉ soi thấy chỗ sơ hở trong đạo pháp của kẻ đối diện.",
        gia=600000, uy_luc=0.92, canh_gioi_toi_thieu=4, loai_vu_khi="kinh"),
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


# ─────────────────────── BINH KHÍ (mở rộng) ───────────────────────
# Mỗi món có một lối đánh riêng; lối đánh ấy sẽ hiện ra trong lời kể trận đấu.
_dang_ky([
    _vp("o_thiet_dao", "Ô Thiết Đao", "phap_bao", 1,
        "Đao sắt đen bản dày, sống đao dày bằng ngón tay. Không đẹp, nhưng chém xuống thì không cần chém lần hai.",
        gia=110, uy_luc=0.12, loai_vu_khi="dao",
        ghi_chu="Loại đao mà lính thú biên quan vẫn dùng, rẻ tới mức không ai buồn ăn cắp."),
    _vp("lieu_diep_phi_dao", "Liễu Diệp Phi Đao", "phap_bao", 1,
        "Chín lưỡi đao mỏng như lá liễu, đeo trong ống tay áo. Đánh gần thì vô dụng, đánh xa thì hiểm.",
        gia=140, uy_luc=0.13, loai_vu_khi="phi_kiem",
        ghi_chu="Nghề của kẻ không định đánh lâu."),
    _vp("ngu_loi_phu_luc", "Ngũ Lôi Phù Lục", "phap_bao", 2,
        "Một xấp phù giấy vàng, mực chu sa còn tươi. Đốt một tờ thì gọi được một đạo sét nhỏ — "
        "nhỏ thôi, nhưng sét vẫn là sét.",
        gia=780, uy_luc=0.22, canh_gioi_toi_thieu=1, loai_vu_khi="phu",
        ghi_chu="Vẽ được thì rẻ, mua thì đắt. Đám phù tu sống bằng cái chênh lệch ấy."),
    _vp("tung_van_kiem", "Tùng Văn Kiếm", "phap_bao", 2,
        "Thân kiếm có vân như vỏ tùng già, cầm vào thấy mát tay. Kiếm này chuộng chữ 'chính', không chuộng chữ 'nhanh'.",
        gia=900, uy_luc=0.24, canh_gioi_toi_thieu=1, loai_vu_khi="kiem",
        ghi_chu="Chế thức của Thanh Vân Môn, phát cho đệ tử nội môn sau kỳ khảo hạch."),
    _vp("liet_diem_dao", "Liệt Diễm Đao", "phap_bao", 2,
        "Lưỡi đao đỏ như than nung, chém vào không khí để lại một vệt nóng còn cong queo hồi lâu.",
        gia=1100, uy_luc=0.28, canh_gioi_toi_thieu=1, loai_vu_khi="dao",
        ghi_chu="Rèn trong miệng hoả sơn đã ngủ, tôi bằng máu thú."),
    _vp("pha_quan_thuong", "Phá Quân Thương", "phap_bao", 3,
        "Trường thương dài một trượng hai, mũi thương chỉ có một đường rãnh — rãnh để máu chảy ra cho khỏi bám.",
        gia=3600, uy_luc=0.33, canh_gioi_toi_thieu=1, loai_vu_khi="thuong",
        ghi_chu="Di vật của một viên tướng chết đứng, tay vẫn nắm thương."),
    _vp("truy_nguyet_cung", "Truy Nguyệt Cung", "phap_bao", 3,
        "Cung sừng giao long, dây bằng gân yêu thú. Kéo hết dây thì tay run, nhưng tên bắn ra không nghe thấy tiếng.",
        gia=4200, uy_luc=0.31, canh_gioi_toi_thieu=1, loai_vu_khi="cung",
        ghi_chu="Người chế ra nó bắn rụng một con Thanh Diêu Điểu ở khoảng cách ba dặm, rồi gác cung, không bắn nữa."),
    _vp("huyen_thiet_trong_kiem", "Huyền Thiết Trọng Kiếm", "phap_bao", 4,
        "Kiếm nặng bảy trăm cân, không mũi không lưỡi. Nó không cắt — nó **đập**.",
        gia=13000, uy_luc=0.44, canh_gioi_toi_thieu=2, loai_vu_khi="kiem",
        ghi_chu="Kẻ dùng được nó thường không cần học chiêu thức nào cả."),
    _vp("kim_tam_ti", "Bách Độc Kim Tàm Ti", "phap_bao", 4,
        "Một sợi tơ vàng mảnh hơn tóc, thả ra thì mất hút trong không khí. Người bị nó cắt thường chưa kịp biết.",
        gia=15000, uy_luc=0.46, canh_gioi_toi_thieu=2, loai_vu_khi="ti",
        ghi_chu="Nuôi trong ống ngọc, mỗi tháng phải cho ăn một giọt tinh huyết."),
    _vp("ngu_quy_am_la_phien", "Ngũ Quỷ Âm La Phiến", "phap_bao", 4,
        "Quạt xương phủ lụa đen, mở ra thì năm gương mặt hiện lên trên nan quạt, mỗi mặt một kiểu đau đớn.",
        gia=16000, uy_luc=0.48, canh_gioi_toi_thieu=2, loai_vu_khi="quat",
        ghi_chu="Món của ma đạo. Chính đạo thấy thì trước hỏi tội, sau mới hỏi tên."),
    _vp("tu_loi_an", "Tử Lôi Ấn", "phap_bao", 5,
        "Ấn đồng vuông vức, mặt ấn khắc chữ 'Lôi'. Đóng xuống một cái thì cả một vùng nghe tiếng sấm dưới đất.",
        gia=48000, uy_luc=0.60, canh_gioi_toi_thieu=2, loai_vu_khi="an",
        ghi_chu="Vật trấn phái đã thất truyền của một tông môn không còn tồn tại."),
    _vp("cuu_u_hon_chung", "Cửu U Hồn Chung", "phap_bao", 5,
        "Chuông đồng nhỏ bằng nắm tay, rung lên thì thần thức kẻ địch rung theo. Ai nghe đủ chín tiếng thì không tỉnh lại nữa.",
        gia=52000, uy_luc=0.62, canh_gioi_toi_thieu=2, loai_vu_khi="chuong",
        ghi_chu="Bên trong chuông có khắc chín cái tên. Không ai biết đó là chín ai."),
    _vp("ngu_phong_phi_kiem", "Ngự Phong Phi Kiếm", "phap_bao", 5,
        "Phi kiếm ba thước, nhẹ như một hơi thở. Xuất kiếm rồi thì kiếm quang mới tới, tiếng gió tới sau cùng.",
        gia=56000, uy_luc=0.64, canh_gioi_toi_thieu=3, loai_vu_khi="phi_kiem",
        ghi_chu="Luyện bằng Lạc Lô Tinh Kim, nuôi trong đan điền ba mươi năm mới ra khỏi vỏ."),
    _vp("huyet_ha_ma_dao", "Huyết Hà Ma Đao", "phap_bao", 6,
        "Đao đỏ sẫm, chém càng nhiều thì càng sắc. Nó khát, và nó không giấu chuyện đó.",
        gia=180000, uy_luc=0.78, canh_gioi_toi_thieu=3, loai_vu_khi="dao",
        ghi_chu="Chủ nhân đời trước của nó chết vì chính nó, vào một đêm không có ai để chém."),
    _vp("thanh_loan_vu_y", "Thanh Loan Vũ Y", "phap_bao", 6,
        "Áo dệt bằng lông chim loan xanh, mặc vào nhẹ như không mặc gì. Đao chém tới thì lông áo dựng lên đỡ lấy.",
        gia=190000, uy_luc=0.72, canh_gioi_toi_thieu=3, loai_vu_khi="giap",
        ghi_chu="Một tiên tử đã mặc nó suốt ba trăm năm, rồi cởi ra để lại trước cửa động, không nói vì sao."),
    _vp("can_khon_but", "Càn Khôn Bút", "phap_bao", 6,
        "Bút lông sói, ngòi bút chưa từng khô mực. Viết chữ 'Phong' thì nổi gió, viết chữ 'Đình' thì kẻ địch đứng lại.",
        gia=220000, uy_luc=0.80, canh_gioi_toi_thieu=4, loai_vu_khi="but",
        ghi_chu="Của một nho sinh tu đạo, cả đời chỉ viết bốn chữ mà đủ trấn một phương."),
    _vp("tam_muoi_dinh", "Tam Muội Chân Hoả Đỉnh", "phap_bao", 7,
        "Đỉnh ba chân bằng đồng cổ, trong lòng đỉnh có một đốm lửa xanh không bao giờ tắt. Vừa là đan lô, vừa là hung khí.",
        gia=700000, uy_luc=0.95, canh_gioi_toi_thieu=4, loai_vu_khi="dinh",
        ghi_chu="Đan sư dùng nó để luyện đan. Kẻ khác dùng nó để luyện người."),
    _vp("tram_tien_dai", "Trảm Tiên Đài", "phap_bao", 8,
        "Một phiến đá đen vuông vức lơ lửng, mặt đá nhẵn tới mức soi thấy mặt người — và mặt người soi trong đó luôn cúi xuống.",
        gia=2600000, uy_luc=1.20, canh_gioi_toi_thieu=5, loai_vu_khi="dai",
        ghi_chu="Tên của nó không phải nói quá. Đã có tiên bị chém trên đài này."),
    _vp("hon_don_chung", "Hỗn Độn Chung", "phap_bao", 9,
        "Không rõ chất liệu, không rõ tuổi. Chuông chưa từng kêu. Người ta nói tiếng đầu tiên của nó sẽ là tiếng cuối cùng của một thời đại.",
        gia=99000000, uy_luc=1.60, canh_gioi_toi_thieu=7, loai_vu_khi="chuong",
        ghi_chu="Được nhắc tới đúng ba lần trong toàn bộ thư tịch còn sót lại, và cả ba lần đều là lời đồn."),
])

# ─────────────────────── LINH ĐAN (mở rộng) ───────────────────────
_dang_ky([
    _vp("thanh_tam_dan", "Thanh Tâm Đan", "dan_duoc", 2,
        "Đan xanh nhạt, ngậm vào thấy mát từ lưỡi xuống tới bụng. Giải độc, và giải cả mấy thứ độc không nằm trong thân.",
        gia=260, hieu_qua={"dao_tam": 5, "tri_thuong": 15}),
    _vp("cuong_the_dan", "Cường Thể Đan", "dan_duoc", 3,
        "Đan nâu sẫm, cứng như đá, phải nhai. Nhai xong thì hàm mỏi ba ngày, nhưng xương thì chắc thêm một đời.",
        gia=900, hieu_qua={"can_cot": 3, "tri_thuong": 20}),
    _vp("pha_chuong_dan", "Phá Chướng Đan", "dan_duoc", 3,
        "Đan xám tro, uống vào thấy trong kinh mạch có tiếng nứt rất khẽ — ấy là chỗ bế tắc đang bị đục thủng.",
        gia=1200, hieu_qua={"dot_pha_tang": 0.14}),
    _vp("an_tuc_dan", "Ẩn Tức Đan", "dan_duoc", 3,
        "Nuốt vào thì khí tức tan ra như khói loãng. Trong một quãng, ngươi đứng giữa đường mà không ai buồn nhìn.",
        gia=1400, hieu_qua={"an_tuc": 7200}),
    _vp("nguyen_anh_dan", "Nguyên Anh Đan", "dan_duoc", 6,
        "Đan tím sẫm, bề mặt có vân xoáy như một cơn lốc thu nhỏ. Cầm lâu thì đầu ngón tay tê dại.",
        gia=90000, hieu_qua={"dot_pha": 0.18, "chi_dung_cho": 2}),
    _vp("hoa_than_dan", "Hóa Thần Đan", "dan_duoc", 7,
        "Đan trắng như sương, nhẹ tới mức đặt trên lòng bàn tay mà không cảm thấy trọng lượng.",
        gia=420000, hieu_qua={"dot_pha": 0.16, "chi_dung_cho": 3}),
    _vp("do_ach_dan", "Độ Ách Đan", "dan_duoc", 7,
        "Đan đen tuyền, nuốt xuống thì da thịt nổi lên một lớp ánh kim rất mỏng. Nó không cứu ngươi khỏi lôi kiếp — "
        "nó chỉ giúp ngươi chịu thêm được một đạo nữa.",
        gia=520000, hieu_qua={"ho_kiep": 0.25, "tri_thuong": 30}),
    _vp("kim_cang_dan", "Kim Cang Hộ Thể Đan", "dan_duoc", 5,
        "Đan vàng xám nặng tay. Trong nửa ngày sau khi uống, đòn đánh vào người ngươi nghe như đánh vào chuông đá.",
        gia=28000, hieu_qua={"ho_kiep": 0.12, "tri_thuong": 40, "can_cot": 1}),
    _vp("cuu_chuyen_hoi_xuan", "Cửu Chuyển Hồi Xuân Đan", "dan_duoc", 6,
        "Chín lần luyện, chín lần phong. Đan này kéo được kẻ chỉ còn một hơi tàn ngồi dậy — nhưng chỉ một lần trong đời mỗi người.",
        gia=120000, hieu_qua={"tri_thuong": 100, "tu_vi": 8000, "dao_tam": 5}),
    _vp("dien_tho_dan", "Diên Thọ Đan", "dan_duoc", 6,
        "Đan màu ngà, thơm mùi cỏ non. Nó không cho ngươi mạnh thêm, nó chỉ cho ngươi **thời gian** — "
        "thứ mà tới bậc này ngươi mới hiểu là đắt nhất.",
        gia=150000, hieu_qua={"tho_nguyen": 120, "dao_tam": 3}),
    _vp("huyet_bo_de", "Huyết Bồ Đề", "dan_duoc", 5,
        "Không phải đan luyện ra, mà là một khối kết tinh đỏ sẫm moi từ trong óc yêu thú già. Tăng tu vi rất nhanh, "
        "và để lại trong ngươi một thứ gì đó không phải của ngươi.",
        gia=36000, hieu_qua={"tu_vi": 26000, "sat_nghiep": 5, "dao_tam": -8}),
    _vp("tuc_cot_dan", "Tục Cốt Đan", "dan_duoc", 4,
        "Xương gãy nát tới mấy cũng nối lại được, chỉ có điều lúc nối thì ngươi tỉnh táo hoàn toàn.",
        gia=6000, hieu_qua={"tri_thuong": 80}),
    _vp("ngung_than_dan", "Ngưng Thần Đan", "dan_duoc", 5,
        "Đan bạc, ngậm dưới lưỡi trong lúc độ kiếp. Thần hồn nhờ nó mà không tán đi trong lúc thân xác rách nát.",
        gia=32000, hieu_qua={"dao_tam": 14, "ho_kiep": 0.08}),
])

# ─────────────────────── DƯỢC LIỆU & VẬT LIỆU BẬC CAO ───────────────────────
_dang_ky([
    _vp("tu_phu_linh_chi", "Tử Phủ Linh Chi", "duoc_lieu", 5,
        "Linh chi tím mọc trong hang có sét đánh, tán nấm có vân như phủ đệ nhìn từ trên cao.", gia=4200),
    _vp("long_huyet_thao", "Long Huyết Thảo", "duoc_lieu", 6,
        "Cỏ mọc nơi giao long từng chết, thân cỏ đỏ và ấm, bẻ ra nghe một tiếng thở dài rất nhỏ.", gia=15000),
    _vp("bang_phach", "Băng Phách", "duoc_lieu", 4,
        "Khối băng không tan, bên trong đóng một con bướm trắng còn nguyên vẹn từ thượng cổ.", gia=2600),
    _vp("thien_loi_moc", "Thiên Lôi Mộc", "vat_lieu", 6,
        "Lõi cây bị sét đánh chín lần mà không cháy. Cầm trong tay thì tóc gáy dựng lên.", gia=26000),
    _vp("hoa_tinh_thach", "Hoả Tinh Thạch", "vat_lieu", 5,
        "Đá đỏ nóng âm ỉ, thả vào nước thì nước sôi mà đá không nguội.", gia=6800),
    _vp("yeu_vuong_cot", "Yêu Vương Cốt", "vat_lieu", 6,
        "Một khúc xương của yêu thú đã hoá hình, trên xương còn vết răng của thứ đã giết nó.", gia=31000),
    _vp("tinh_ha_sa", "Tinh Hà Sa", "vat_lieu", 7,
        "Cát bạc lấy từ lòng một thiên thạch, đổ ra lòng bàn tay thì trôi ngược lên trời.", gia=88000),
    _vp("cuu_thien_huyen_thiet", "Cửu Thiên Huyền Thiết", "vat_lieu", 8,
        "Sắt đen từ tầng trời thứ chín, nặng tới mức một khối bằng nắm tay làm sập cả cái bàn đá.", gia=460000),
])


def lay(ma: str) -> VatPham | None:
    return DANH_MUC.get(ma)


def ten(ma: str) -> str:
    v = DANH_MUC.get(ma)
    return v.ten if v else ma


def theo_loai(loai: str) -> list[VatPham]:
    return [v for v in DANH_MUC.values() if v.loai == loai]
