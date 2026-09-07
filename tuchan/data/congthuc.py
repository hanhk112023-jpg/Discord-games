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

# ─────────────────── ĐAN PHƯƠNG (mở rộng) ───────────────────
_d(CongThuc(
    ma="ct_thanh_tam", ten="Thanh Tâm Đan phương", loai="dan",
    nguyen_lieu={"thanh_lan_hoa": 4, "bang_phach": 1},
    thanh_pham="thanh_tam_dan", so_luong=(1, 2), do_kho=0.34,
    lai_lich="Chép trên vách một thiền phòng ở Vọng Hải Tự, ai vào cũng đọc được, ít ai nhớ được.",
    mo_ta="Băng phách phải để nguyên khối, tan trong lò chứ không tan trong tay.",
))
_d(CongThuc(
    ma="ct_tuc_cot", ten="Tục Cốt Đan phương", loai="dan",
    nguyen_lieu={"huyet_tinh_chi": 3, "giao_can": 2, "bach_van_sam": 1},
    thanh_pham="tuc_cot_dan", so_luong=(1, 2), do_kho=0.46, canh_gioi_toi_thieu=1,
    lai_lich="Của một lang y quân doanh, đổi lấy việc ngươi không hỏi ông ta từng chữa cho ai.",
    mo_ta="Giao cân phải ninh trước ba canh giờ, tới khi nước trong lò kéo thành sợi.",
))
_d(CongThuc(
    ma="ct_cuong_the", ten="Cường Thể Đan phương", loai="dan",
    nguyen_lieu={"yeu_dan": 3, "huyet_tinh_chi": 2, "hoa_tinh_thach": 1},
    thanh_pham="cuong_the_dan", so_luong=(1, 2), do_kho=0.5, canh_gioi_toi_thieu=1,
    lai_lich="Huyền Vũ Tông truyền cho đệ tử đã đứng đủ trăm ngày dưới thác.",
    mo_ta="Hoả hầu phải giữ đúng một mức từ đầu đến cuối. Lửa dao động thì đan thành đá.",
))
_d(CongThuc(
    ma="ct_pha_chuong", ten="Phá Chướng Đan phương", loai="dan",
    nguyen_lieu={"tu_phu_linh_chi": 1, "u_dam_lien": 2, "yeu_dan": 2},
    thanh_pham="pha_chuong_dan", so_luong=(1, 1), do_kho=0.56, canh_gioi_toi_thieu=1,
    lai_lich="Ghi trong một cuốn sổ tay không đề tên, tìm thấy trong một động phủ có xác người ngồi.",
    mo_ta="Đan này kỵ tạp niệm của chính đan sư. Ai luyện nó lúc đang nóng lòng đột phá thì hỏng chắc.",
))
_d(CongThuc(
    ma="ct_an_tuc", ten="Ẩn Tức Đan phương", loai="dan",
    nguyen_lieu={"am_hon_sa": 1, "u_dam_lien": 1, "thanh_lan_hoa": 3},
    thanh_pham="an_tuc_dan", so_luong=(1, 2), do_kho=0.52, canh_gioi_toi_thieu=1,
    lai_lich="Món nghề của bọn tán tu chuyên đi nhặt của trong cổ tích.",
    mo_ta="Luyện trong bóng tối hoàn toàn. Có ánh sáng thì dược tính lộ ra và tan mất.",
))
_d(CongThuc(
    ma="ct_kim_cang", ten="Kim Cang Hộ Thể Đan phương", loai="dan",
    nguyen_lieu={"van_nien_ngoc_toai": 1, "yeu_vuong_cot": 1, "hoa_tinh_thach": 2},
    thanh_pham="kim_cang_dan", so_luong=(1, 1), do_kho=0.64, canh_gioi_toi_thieu=2,
    lai_lich="Đan phương của một tông môn luyện thể đã bị diệt môn — kẻ diệt họ giữ lại mỗi tờ giấy này.",
    mo_ta="Xương yêu vương phải nghiền khi còn lạnh, nghiền xong phải vào lò ngay.",
))
_d(CongThuc(
    ma="ct_ngung_than", ten="Ngưng Thần Đan phương", loai="dan",
    nguyen_lieu={"tu_phu_linh_chi": 2, "bang_phach": 2, "cuu_diep_linh_lan": 1},
    thanh_pham="ngung_than_dan", so_luong=(1, 1), do_kho=0.66, canh_gioi_toi_thieu=2,
    lai_lich="Trao tay giữa hai người không quen nhau, trong một đêm mưa, không nói một lời.",
    mo_ta="Khi khói trong lò chuyển sang màu bạc thì lập tức đóng nắp, chậm một nhịp là hỏng.",
))
_d(CongThuc(
    ma="ct_nguyen_anh", ten="Nguyên Anh Đan phương", loai="dan",
    nguyen_lieu={"long_huyet_thao": 1, "thien_tam_qua": 2, "tu_phu_linh_chi": 2, "yeu_thu_noi_dan": 2},
    thanh_pham="nguyen_anh_dan", so_luong=(1, 1), do_kho=0.82, canh_gioi_toi_thieu=2,
    lai_lich="Cả một châu chỉ còn ba bản. Hai bản nằm trong tay tông môn, bản thứ ba thì đang ở chỗ ngươi.",
    mo_ta="Bảy mươi hai canh giờ khống hoả không rời. Đan sư nào luyện xong cũng già đi trông thấy.",
))
_d(CongThuc(
    ma="ct_hoa_than", ten="Hóa Thần Đan phương", loai="dan",
    nguyen_lieu={"long_huyet_thao": 3, "tinh_ha_sa": 1, "van_nien_ngoc_toai": 3, "thien_tam_qua": 2},
    thanh_pham="hoa_than_dan", so_luong=(1, 1), do_kho=0.88, canh_gioi_toi_thieu=3,
    lai_lich="Khắc trong lòng một quả chuông cổ, chỉ hiện ra khi có người đánh chuông đúng chín tiếng.",
    mo_ta="Tinh hà sa không được chạm vào bằng tay trần, phải dẫn bằng thần thức.",
))
_d(CongThuc(
    ma="ct_do_ach", ten="Độ Ách Đan phương", loai="dan",
    nguyen_lieu={"thien_loi_moc": 1, "long_huyet_thao": 2, "yeu_vuong_cot": 2, "tinh_ha_sa": 1},
    thanh_pham="do_ach_dan", so_luong=(1, 1), do_kho=0.86, canh_gioi_toi_thieu=3,
    lai_lich="Của một lão quái đã ba lần độ kiếp hụt. Lão đưa nó đi rồi ngồi cười suốt một đêm.",
    mo_ta="Thiên lôi mộc phải chẻ bằng đá, không được dùng kim loại — kim loại dẫn mất cái khí trong đó.",
))
_d(CongThuc(
    ma="ct_dien_tho", ten="Diên Thọ Đan phương", loai="dan",
    nguyen_lieu={"thien_tam_qua": 3, "cuu_diep_linh_lan": 3, "long_huyet_thao": 1},
    thanh_pham="dien_tho_dan", so_luong=(1, 1), do_kho=0.84, canh_gioi_toi_thieu=3,
    lai_lich="Ai cũng nghe nói tới, ít ai tận mắt thấy. Kẻ có nó thường không khoe.",
    mo_ta="Luyện vào ngày sinh của chính mình. Người xưa tin thế, và không ai dám thử cách khác.",
))
_d(CongThuc(
    ma="ct_cuu_chuyen", ten="Cửu Chuyển Hồi Xuân Đan phương", loai="dan",
    nguyen_lieu={"long_huyet_thao": 2, "tu_phu_linh_chi": 3, "thien_tam_qua": 1, "bang_phach": 2},
    thanh_pham="cuu_chuyen_hoi_xuan", so_luong=(1, 1), do_kho=0.80, canh_gioi_toi_thieu=2,
    lai_lich="Chín lần luyện, chín lần phong lò. Người truyền lại đan phương này chết vì không kịp luyện cho mình.",
    mo_ta="Mỗi lần chuyển phải để đan nguội hẳn rồi mới nung lại. Ai vội thì tới lần thứ tư là nổ.",
))

# ─────────────────── KHÍ PHƯƠNG (mở rộng) ───────────────────
_d(CongThuc(
    ma="kp_o_thiet", ten="Ô Thiết Đao đồ", loai="khi",
    nguyen_lieu={"hac_thiet": 6},
    thanh_pham="o_thiet_dao", do_kho=0.24,
    lai_lich="Dán trên vách lò rèn, mép giấy đã bị lửa liếm cháy một góc.",
    mo_ta="Sống đao để dày, lưỡi mài một mặt. Đao của lính, không phải đao của hiệp khách.",
))
_d(CongThuc(
    ma="kp_lieu_diep", ten="Liễu Diệp Phi Đao đồ", loai="khi",
    nguyen_lieu={"hac_thiet": 3, "thanh_dong_tinh": 2},
    thanh_pham="lieu_diep_phi_dao", do_kho=0.30,
    lai_lich="Chín lá đao, chín bản vẽ giống hệt nhau — người vẽ sợ mình quên.",
    mo_ta="Trọng tâm phải nằm ở một phần ba tính từ mũi. Sai một chút thì đao bay xoay tròn.",
))
_d(CongThuc(
    ma="kp_ngu_loi_phu", ten="Ngũ Lôi Phù Lục pháp", loai="khi",
    nguyen_lieu={"hu_khong_thach": 2, "yeu_dan": 2, "thanh_dong_tinh": 1},
    thanh_pham="ngu_loi_phu_luc", do_kho=0.38, canh_gioi_toi_thieu=1,
    lai_lich="Bài học vỡ lòng của phù tu: vẽ hỏng chín trăm tờ rồi tờ thứ chín trăm lẻ một mới cháy đúng cách.",
    mo_ta="Nét cuối phải hạ bút liền một hơi. Ngập ngừng một cái là cả tờ phù thành giấy lộn.",
))
_d(CongThuc(
    ma="kp_tung_van", ten="Tùng Văn Kiếm đồ", loai="khi",
    nguyen_lieu={"thanh_dong_tinh": 4, "hac_thiet": 6, "hu_khong_thach": 1},
    thanh_pham="tung_van_kiem", do_kho=0.44, canh_gioi_toi_thieu=1,
    lai_lich="Chế thức chuẩn của Thanh Vân Môn, mỗi năm phát cho lò rèn một bản mới.",
    mo_ta="Vân tùng trên thân kiếm không phải để đẹp — đó là đường dẫn chân khí.",
))
_d(CongThuc(
    ma="kp_liet_diem", ten="Liệt Diễm Đao đồ", loai="khi",
    nguyen_lieu={"hoa_tinh_thach": 2, "hac_thiet": 8, "yeu_dan": 2},
    thanh_pham="liet_diem_dao", do_kho=0.5, canh_gioi_toi_thieu=1,
    lai_lich="Của một lò rèn dưới chân hoả sơn, cả nhà ba đời rèn đúng một loại đao.",
    mo_ta="Tôi đao bằng máu thú còn ấm. Nước lã sẽ làm lửa trong đao tắt hẳn.",
))
_d(CongThuc(
    ma="kp_pha_quan", ten="Phá Quân Thương đồ", loai="khi",
    nguyen_lieu={"lac_lo_tinh_kim": 1, "giao_can": 3, "hac_thiet": 10},
    thanh_pham="pha_quan_thuong", do_kho=0.58, canh_gioi_toi_thieu=1,
    lai_lich="Bản vẽ trong quân khí giám của một triều đại đã sụp.",
    mo_ta="Cán thương phải bó bằng giao cân ướt, để khô tự siết lại, không dùng keo.",
))
_d(CongThuc(
    ma="kp_truy_nguyet", ten="Truy Nguyệt Cung đồ", loai="khi",
    nguyen_lieu={"giao_can": 5, "yeu_vuong_cot": 1, "thanh_dong_tinh": 3},
    thanh_pham="truy_nguyet_cung", do_kho=0.60, canh_gioi_toi_thieu=1,
    lai_lich="Người chế ra nó không để lại tên, chỉ để lại một câu: 'Đừng bắn khi chưa muốn giết.'",
    mo_ta="Dây cung phải se trong đêm trăng. Se ban ngày thì dây chùng.",
))
_d(CongThuc(
    ma="kp_huyen_thiet", ten="Huyền Thiết Trọng Kiếm đồ", loai="khi",
    nguyen_lieu={"cuu_thien_huyen_thiet": 1, "lac_lo_tinh_kim": 2, "hoa_tinh_thach": 3},
    thanh_pham="huyen_thiet_trong_kiem", do_kho=0.70, canh_gioi_toi_thieu=2,
    lai_lich="Vẽ nguệch ngoạc bằng than trên nền hang, kèm dòng chữ: 'Nặng là được.'",
    mo_ta="Không mài lưỡi. Mài lưỡi là hiểu sai thanh kiếm này.",
))
_d(CongThuc(
    ma="kp_tu_loi_an", ten="Tử Lôi Ấn đồ", loai="khi",
    nguyen_lieu={"thien_loi_moc": 1, "lac_lo_tinh_kim": 3, "long_van_ngoc": 1},
    thanh_pham="tu_loi_an", do_kho=0.76, canh_gioi_toi_thieu=2,
    lai_lich="Của tông môn đã diệt vong. Bản vẽ sống lâu hơn cả cái tông môn ấy.",
    mo_ta="Khắc chữ 'Lôi' vào lúc trời đang có sấm, mỗi tiếng sấm khắc một nét.",
))
_d(CongThuc(
    ma="kp_cuu_u_chung", ten="Cửu U Hồn Chung đồ", loai="khi",
    nguyen_lieu={"am_hon_sa": 4, "yeu_vuong_cot": 2, "lac_lo_tinh_kim": 2},
    thanh_pham="cuu_u_hon_chung", do_kho=0.78, canh_gioi_toi_thieu=2,
    lai_lich="Ma đạo truyền tay nhau, mỗi đời thêm một cái tên khắc vào lòng chuông.",
    mo_ta="Đúc xong đừng thử đánh. Có kẻ thử, và không kể lại được gì.",
))
_d(CongThuc(
    ma="kp_ngu_phong", ten="Ngự Phong Phi Kiếm đồ", loai="khi",
    nguyen_lieu={"lac_lo_tinh_kim": 4, "tinh_ha_sa": 1, "hu_khong_thach": 4},
    thanh_pham="ngu_phong_phi_kiem", do_kho=0.80, canh_gioi_toi_thieu=3,
    lai_lich="Trong ngọc giản của một kiếm tu chết già trên lưng chừng núi, tay vẫn giữ thế bắt quyết.",
    mo_ta="Sau khi thành hình, phải nuôi trong đan điền ba mươi năm. Không có đường tắt cho món này.",
))
_d(CongThuc(
    ma="kp_can_khon_but", ten="Càn Khôn Bút đồ", loai="khi",
    nguyen_lieu={"tinh_ha_sa": 2, "cuu_thien_huyen_thiet": 1, "long_van_ngoc": 2, "thien_loi_moc": 1},
    thanh_pham="can_khon_but", do_kho=0.86, canh_gioi_toi_thieu=4,
    lai_lich="Không phải đồ hình luyện khí, mà là một bài thơ. Đọc đủ chín lần thì tự hiểu cách làm.",
    mo_ta="Ngòi bút không rèn — nó tự mọc ra, nếu ngươi viết đủ nhiều chữ thật lòng.",
))

TAT_CA: dict[str, CongThuc] = {**DAN_PHUONG, **KHI_PHUONG}


def lay(ma: str) -> CongThuc | None:
    return TAT_CA.get(ma)
