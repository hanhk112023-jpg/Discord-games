"""Việc tông môn giao — không phải "nhiệm vụ", chỉ là việc phải làm.

Trong thế giới này không ai đưa cho ngươi một tấm bảng có dấu chấm than.
Một vị chấp sự già gọi ngươi lại, nói vài câu, rồi quay đi. Làm hay không là chuyện của ngươi.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ViecMon:
    ma: str
    loai: str  # thu_thap | tru_diet | tuan_hanh
    ten: str
    nguoi_giao: str
    loi_dan: str  # lời vị chấp sự nói ra
    canh_gioi_toi_thieu: int = 0
    vat_can: dict[str, int] = field(default_factory=dict)
    dich: str = ""
    so_chang: int = 3
    cong_hien: int = 40
    linh_thach: int = 60
    thuong_them: tuple[str, ...] = ()
    canh_chang: tuple[str, ...] = ()  # cảnh cho từng chặng tuần hành
    ket: str = ""


DANH_SACH: dict[str, ViecMon] = {}


def _v(v: ViecMon) -> None:
    DANH_SACH[v.ma] = v


_v(ViecMon(
    ma="hai_thao_duoc_vien",
    loai="thu_thap", ten="Bổ vào dược viên",
    nguoi_giao="Chấp sự Trần, người trông dược viên, tay trái thiếu hai ngón",
    loi_dan=(
        "'Dược viên vừa mất một luống vì sương muối. Ngươi đi kiếm về cho ta ít Hoàng Tinh Thảo "
        "với vài đoá Thanh Lan Hoa. Đừng hái nhầm loại có nhựa trắng, năm ngoái có đứa hái nhầm, "
        "giờ nó nằm ở dưới kia.' Lão chỉ tay xuống chân núi, rồi không nói thêm gì nữa."
    ),
    vat_can={"hoang_tinh_thao": 5, "thanh_lan_hoa": 2},
    cong_hien=45, linh_thach=80,
))
_v(ViecMon(
    ma="gom_hac_thiet",
    loai="thu_thap", ten="Gom sắt cho lò rèn",
    nguoi_giao="Lão thợ rèn họ Ngụy, cả người ám khói, nói câu nào cũng như quát",
    loi_dan=(
        "'Lò của ta nguội ba hôm rồi! Đám tiểu tử chân truyền thì cần kiếm mới, mà sắt thì không tự bò tới. "
        "Kiếm cho ta mớ Hắc Thiết. Đừng lấy loại lẫn cát — ta ngửi là biết.'"
    ),
    vat_can={"hac_thiet": 6},
    cong_hien=40, linh_thach=70,
))
_v(ViecMon(
    ma="nop_yeu_dan",
    loai="thu_thap", ten="Yêu đan cho đan đường",
    nguoi_giao="Đan đồng áo xám, chừng mười lăm tuổi, mắt thâm quầng vì thức đêm canh lò",
    loi_dan=(
        "'Sư phụ tôi cần yêu đan để dẫn hoả. Ba viên là đủ. Nếu... nếu huynh kiếm được, "
        "xin đừng nói với ai là tôi nhờ. Sư phụ bảo tự tôi phải đi.' Nó cúi đầu rất thấp."
    ),
    vat_can={"yeu_dan": 3},
    cong_hien=70, linh_thach=140, thuong_them=("ct_hoi_khi",),
))
_v(ViecMon(
    ma="tru_lang_quan",
    loai="tru_diet", ten="Bầy sói phía sườn tây",
    nguoi_giao="Một tá điền của tông môn, quỳ ở cổng ngoài suốt buổi sáng mới có người ra tiếp",
    loi_dan=(
        "'Bầy sói lông đỏ xuống đồng ba đêm liền. Nhà tôi mất hai con trâu, nhà bên mất thằng bé. "
        "Chúng tôi không dám xin nhiều... chỉ xin tiên sư giết con đầu đàn.' "
        "Ông ta dập đầu, trán chạm đất kêu một tiếng khô khốc."
    ),
    dich="xich_mao_lang", cong_hien=60, linh_thach=110,
))
_v(ViecMon(
    ma="tru_thi_ma",
    loai="tru_diet", ten="Cái thứ trong mộ địa cũ",
    nguoi_giao="Trưởng lão Chấp Pháp, mặt lạnh, không mời ngươi ngồi",
    loi_dan=(
        "'Mộ địa phía đông có xác không chịu nằm. Đã ba đệ tử ngoại môn đi, một về, "
        "và cái đứa về được thì bây giờ chỉ ngồi cười. Ngươi liệu sức mình. "
        "Nếu chết, tông môn sẽ khắc tên ngươi lên bậc đá. Đó là tất cả những gì ta hứa được.'"
    ),
    canh_gioi_toi_thieu=0, dich="thi_ma", cong_hien=120, linh_thach=260,
    thuong_them=("liem_thuong_dan",),
))
_v(ViecMon(
    ma="tru_ma_tu",
    loai="tru_diet", ten="Kẻ áo đen ở Lạc Tinh",
    nguoi_giao="Chưởng môn phái người truyền lời, không gặp mặt",
    loi_dan=(
        "'Có một tên ma tu đang hút tinh huyết dân phu đào tinh thạch ngoài hoang nguyên. "
        "Hắn cẩn thận, mỗi đêm chỉ lấy một người, để không ai kịp gọi cứu viện. "
        "Tông môn cần cái đầu của hắn treo ở cổng, đủ ba ngày.'"
    ),
    canh_gioi_toi_thieu=1, dich="hac_bao_ma_tu", cong_hien=320, linh_thach=900,
    thuong_them=("hoan_hon_dan",),
))
_v(ViecMon(
    ma="tuan_son",
    loai="tuan_hanh", ten="Tuần sơn ba canh",
    nguoi_giao="Đội trưởng tuần sơn, một hán tử Trúc Cơ có vết chém cũ chạy ngang mặt",
    loi_dan=(
        "'Đi với ta ba canh giờ. Không cần ngươi đánh đấm gì, chỉ cần ngươi mở mắt ra mà nhìn. "
        "Núi này lớn, và không phải chỗ nào cũng thuộc về chúng ta.'"
    ),
    so_chang=3, cong_hien=80, linh_thach=150,
    canh_chang=(
        "Canh đầu, sương phủ kín đường tuần. Các ngươi đi qua Vọng Nguyệt Đài, nơi có một đệ tử "
        "ngoại môn đang quỳ chịu phạt từ đêm qua. Đội trưởng liếc nhìn, không nói gì, cũng không cho phép ngươi nói.",
        "Canh hai, tới ranh giới phía bắc. Trên tảng đá mốc giới, có người dùng vật sắc khắc lại "
        "một chữ khác đè lên huy hiệu tông môn. Vết khắc còn mới. Đội trưởng lấy tay chùi, "
        "rồi lặng lẽ đặt bàn tay lên chuôi đao.",
        "Canh ba, mưa xuống. Các ngươi đứng dưới một mái đá, nhìn nước chảy thành sợi. "
        "Đội trưởng bỗng nói, không nhìn ngươi: 'Ta tuần sơn hai mươi năm rồi. Ngươi biết ta học được gì không? "
        "Cái đáng sợ không phải là thứ ở ngoài núi.' Ông ta không nói tiếp.",
    ),
    ket="Trở về cổng núi khi trời vừa hửng. Đội trưởng ghi tên ngươi vào sổ, gạch một nét, thế là xong.",
))
_v(ViecMon(
    ma="ho_tong_duoc",
    loai="tuan_hanh", ten="Hộ tống xe dược xuống trấn",
    nguoi_giao="Quản sự ngoại vụ, cầm sổ, đọc tên ngươi sai hai lần",
    loi_dan=(
        "'Ba xe dược liệu xuống trấn Thạch Khẩu. Đường không xa nhưng năm nay không yên. "
        "Mất một xe thì trừ công hiến, mất cả ba thì ngươi khỏi cần quay về.'"
    ),
    so_chang=3, cong_hien=90, linh_thach=200,
    canh_chang=(
        "Xe lăn bánh lúc gà gáy lần hai. Người phu xe già kể chuyện con trai ông đã nhập ngoại môn năm ngoái, "
        "kể mãi một chuyện, và ngươi không nỡ ngắt lời.",
        "Qua khúc rừng hẹp, đàn quạ trên cây bay lên cùng một lúc, dù không có gió. "
        "Ngươi bảo dừng xe. Chờ mười nhịp thở. Không có gì xảy ra. Người phu xe cười ngươi nhát gan, "
        "nhưng tay ông ta run.",
        "Tới cầu đá cuối cùng, có ba kẻ mặt bịt kín ngồi vắt vẻo trên thành cầu. Chúng nhìn khí tức của ngươi, "
        "nhìn thêm một lúc nữa, rồi nhảy xuống bỏ đi mà không nói câu nào. Hôm nay, ngươi chưa phải giết ai.",
    ),
    ket="Xe vào cổng trấn khi trời tối. Quản sự ký nhận, đóng dấu, và không cảm ơn ngươi một tiếng nào.",
))


def cho_phep(canh_gioi: int, mon_phai: str | None = None) -> list[ViecMon]:
    return [v for v in DANH_SACH.values() if v.canh_gioi_toi_thieu <= canh_gioi]


def lay(ma: str) -> ViecMon | None:
    return DANH_SACH.get(ma)
