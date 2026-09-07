"""Thang bậc tu hành: từ kẻ phàm phu hít lấy hơi sương, tới bậc Chân Tiên.

Mười cảnh giới lớn, sáu mươi mốt bậc nhỏ. Mỗi bậc nhỏ là một lần xung quan,
mỗi cảnh giới lớn là một cửa tử — và mỗi cửa tử có một loại khảo nghiệm riêng của nó.

Trong thế giới này không ai nói "ta cấp mấy". Người ta nhìn khí tức mà đoán,
nhìn cách kẻ khác cúi đầu mà biết. Con số dưới đây chỉ là xương cốt giấu dưới da thịt.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CanhGioi:
    ma: str
    ten: str
    so_tang: int
    ten_tang: tuple[str, ...]
    tu_vi_moi_tang: int  # lượng đạo hạnh cần cho mỗi tầng
    tho_nguyen: int  # thọ nguyên tối đa, năm
    khi_the: str  # một câu tả khí tức để người ngoài nhìn vào
    than_the: str  # thân thể biến đổi ra sao
    cam_ngo: str  # cảm nhận thiên địa
    the_gioi: str  # địa vị trong nhân gian
    tranh: str = ""  # tranh minh hoạ nếu có


# Năm bậc nhỏ dùng chung cho phần lớn cảnh giới
TANG_NGU = ("sơ kỳ", "trung kỳ", "hậu kỳ", "đỉnh phong", "đại viên mãn")
TANG_PHO_THONG = TANG_NGU  # giữ tên cũ cho tương thích
TRONG_KIEP = ("nhất trọng", "nhị trọng", "tam trọng", "tứ trọng", "ngũ trọng",
              "lục trọng", "thất trọng", "bát trọng", "cửu trọng")
TIEN_VI = ("Địa Tiên", "Thiên Tiên", "Kim Tiên", "Đại La")

BANG_CANH_GIOI: tuple[CanhGioi, ...] = (
    CanhGioi(
        ma="luyen_khi",
        ten="Luyện Khí",
        so_tang=13,
        ten_tang=tuple(f"tầng {i}" for i in range(1, 14)),
        tu_vi_moi_tang=120,
        tho_nguyen=100,
        khi_the="hơi thở còn vẩn bụi trần, đứng giữa chợ không ai buồn nhìn lại",
        than_the="gân cốt săn hơn kẻ phàm, một quyền có thể làm nứt đá xanh, đi bộ ba ngày không mỏi",
        cam_ngo="linh khí trong trời đất tựa sương mỏng, phải nín thở gom góp từng chút một",
        the_gioi="trong mắt tông môn lớn, chỉ là hạt cát dưới chân núi",
        tranh="luyen_khi.png",
    ),
    CanhGioi(
        ma="truc_co",
        ten="Trúc Cơ",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=780,
        tho_nguyen=200,
        khi_the="khí tức trầm như giếng cổ, người phàm đứng gần tự dưng thấy lạnh gáy",
        than_the="tạp chất trong xương tuỷ đã rửa sạch, da thịt ẩn ẩn ánh ngọc, đao thường khó phạm",
        cam_ngo="linh khí không còn là sương mà là nước, hít một hơi là cả ngực đầy",
        the_gioi="đủ tư cách làm khách khanh một huyện, đủ tư cách chết trong một cuộc tranh chấp nhỏ",
    ),
    CanhGioi(
        ma="ket_dan",
        ten="Kết Đan",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=3600,
        tho_nguyen=500,
        khi_the="đứng yên mà áo tự động, quanh người có mùi đan hương rất nhạt",
        than_the="trong đan điền một viên kim đan xoay chậm, mỗi vòng xoay là một hơi thở của trời",
        cam_ngo="có thể ngự khí mà bay trăm dặm, mưa rơi trên đầu tự tách ra hai bên",
        the_gioi="một phương chân nhân, xuống núi thì thành chủ, quay đầu thì thành hoạ",
        tranh="ket_dan.png",
    ),
    CanhGioi(
        ma="nguyen_anh",
        ten="Nguyên Anh",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=16000,
        tho_nguyen=1200,
        khi_the="ánh mắt nhìn qua khiến kẻ Trúc Cơ nghẹn thở, đất dưới chân không dám vỡ",
        than_the="kim đan đã vỡ, trong đó ngồi một anh nhi mang khuôn mặt của chính ngươi, thân xác chỉ còn là áo khoác",
        cam_ngo="thần thức trải ra như lưới, cách mười dặm nghe được tiếng kiến bò",
        the_gioi="một cái tên đủ để cả một tông môn trung đẳng nghiêng mình",
    ),
    CanhGioi(
        ma="hoa_than",
        ten="Hóa Thần",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=66000,
        tho_nguyen=3000,
        khi_the="đến gần thì trời đất tự nhiên im tiếng, chim thú nằm rạp",
        than_the="nguyên anh hòa vào thần niệm, thân này tan cũng chưa chắc chết",
        cam_ngo="một niệm khởi lên, gió mây trong trăm dặm đổi chiều",
        the_gioi="lời nói ra là quy củ của một vùng, không ai dám gọi thẳng tên",
    ),
    CanhGioi(
        ma="luyen_hu",
        ten="Luyện Hư",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=260000,
        tho_nguyen=8000,
        khi_the="thân ảnh khi mờ khi tỏ, kẻ nhìn lâu sẽ chảy máu mắt",
        than_the="đang luyện cái hư vô làm xương, bước một bước xé một tấc không gian",
        cam_ngo="thấy rõ những sợi tơ vô hình chằng chịt gọi là quy tắc",
        the_gioi="đã ra khỏi vòng tranh chấp thế tục, chỉ còn tranh với đồng đạo và với trời",
    ),
    CanhGioi(
        ma="hop_the",
        ten="Hợp Thể",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=1050000,
        tho_nguyen=20000,
        khi_the="thân là pháp, pháp là thân, đứng đâu thì nơi đó thành lãnh vực",
        than_the="thần hồn và nhục thân hợp làm một khối, đao chém vào chỉ nghe tiếng chuông",
        cam_ngo="thiên địa đối với ngươi đã bớt lạnh nhạt, nhưng chưa từng dịu dàng",
        the_gioi="một trụ cột của cả một châu, sống chết của vạn người treo trên một ý niệm",
    ),
    CanhGioi(
        ma="dai_thua",
        ten="Đại Thừa",
        so_tang=5,
        ten_tang=TANG_NGU,
        tu_vi_moi_tang=4200000,
        tho_nguyen=50000,
        khi_the="không còn khí tức, vì cả bầu trời trên đầu ngươi chính là khí tức của ngươi",
        than_the="mỗi tấc da thịt đều chứa một tiểu thiên địa đang xoay",
        cam_ngo="nghe được tiếng kiếp số đang gõ cửa, từng nhịp một, rất kiên nhẫn",
        the_gioi="ngươi đã là truyền thuyết mà đám hậu bối chép trong ngọc giản",
    ),
    CanhGioi(
        ma="do_kiep",
        ten="Độ Kiếp",
        so_tang=9,
        ten_tang=TRONG_KIEP,
        tu_vi_moi_tang=9500000,
        tho_nguyen=100000,
        khi_the="trên đầu vĩnh viễn có một đám mây không tan, người trong thiên hạ tránh xa ngươi ba dặm",
        than_the="thân thể bị lôi hoả rửa đi rửa lại, mỗi lần rách nát là một lần bền hơn",
        cam_ngo="trời không còn là chỗ dựa, trời là kẻ thù",
        the_gioi="một chân đã đặt ngoài nhân gian, chân còn lại vẫn dính máu",
        tranh="do_kiep.png",
    ),
    CanhGioi(
        ma="chan_tien",
        ten="Chân Tiên",
        so_tang=4,
        ten_tang=TIEN_VI,
        tu_vi_moi_tang=88000000,
        tho_nguyen=10**7,
        khi_the="phàm nhân nhìn thấy ngươi chỉ nhớ được một vệt sáng và một cơn buồn ngủ",
        than_the="xác phàm đã bỏ lại dưới núi từ lâu, cái đứng đây là đạo đã thành hình",
        cam_ngo="thiên địa nói chuyện với ngươi bằng thứ ngôn ngữ mà chữ nghĩa không chép nổi",
        the_gioi="tên ngươi trở thành một thời đại",
    ),
)

CHI_SO_THEO_MA = {cg.ma: i for i, cg in enumerate(BANG_CANH_GIOI)}
TOI_DA = len(BANG_CANH_GIOI) - 1
TONG_SO_BAC = sum(cg.so_tang for cg in BANG_CANH_GIOI)


def canh_gioi(chi_so: int) -> CanhGioi:
    return BANG_CANH_GIOI[max(0, min(TOI_DA, chi_so))]


def ten_canh_gioi(chi_so: int, tang: int) -> str:
    cg = canh_gioi(chi_so)
    t = max(1, min(cg.so_tang, tang))
    if cg.ma == "chan_tien":
        return f"{cg.ten} · {cg.ten_tang[t - 1]}"
    if cg.ma == "do_kiep":
        return f"{cg.ten} {cg.ten_tang[t - 1]}"
    return f"{cg.ten} {cg.ten_tang[t - 1]}"


def tu_vi_can_thiet(chi_so: int, tang: int) -> int:
    """Đạo hạnh cần tích để đầy một tầng."""
    cg = canh_gioi(chi_so)
    he_so = 1.0 + 0.14 * (tang - 1)
    return int(cg.tu_vi_moi_tang * he_so)


def la_dinh_canh(chi_so: int, tang: int) -> bool:
    return tang >= canh_gioi(chi_so).so_tang


def suc_manh_nen(chi_so: int, tang: int) -> float:
    """Sức mạnh nền, dùng cho tính toán nội bộ khi so đọ. Người chơi không thấy."""
    goc = 8.0 ** chi_so
    return goc * (1.0 + 1.65 * (tang - 1) / max(1, canh_gioi(chi_so).so_tang - 1))


def bac_tuyet_doi(chi_so: int, tang: int) -> int:
    """Đếm xem đã đi qua bao nhiêu bậc kể từ lúc nhập đạo."""
    return sum(cg.so_tang for cg in BANG_CANH_GIOI[:chi_so]) + tang


def khoang_cach_cach_bac(a_chi_so: int, b_chi_so: int) -> int:
    return a_chi_so - b_chi_so


# ─────────────────────── tiểu cảnh giới ───────────────────────

MO_TA_TIEU_CANH = {
    "so": "Chân khí ở bậc này còn thưa, chạy trong kinh mạch nghe như nước rót vào bình rỗng.",
    "trung": "Chân khí đã kín một nửa châu thân. Ngươi bắt đầu quen với cái nặng của nó, và quên rằng trước kia mình không có.",
    "hau": "Chân khí đặc tới mức có trọng lượng. Đứng lâu một chỗ thì đất dưới chân hơi lún xuống.",
    "dinh": "Đã tới đỉnh của bậc này. Mỗi lần vận công, ngươi nghe rõ một tiếng vọng — ấy là bức tường phía trước đang dội lại.",
    "vien": "Đại viên mãn. Không còn gì để tích thêm nữa; từ đây trở đi, giữ lại tức là hao đi.",
}


def khoa_tieu_canh(chi_so: int, tang: int) -> str:
    cg = canh_gioi(chi_so)
    if cg.so_tang <= 1:
        return "vien"
    ti = (tang - 1) / (cg.so_tang - 1)
    if ti >= 0.999:
        return "vien"
    if ti >= 0.75:
        return "dinh"
    if ti >= 0.5:
        return "hau"
    if ti >= 0.25:
        return "trung"
    return "so"


def mo_ta_tang(chi_so: int, tang: int) -> str:
    return MO_TA_TIEU_CANH[khoa_tieu_canh(chi_so, tang)]


# ─────────────────────── khảo nghiệm khi lên cảnh giới ───────────────────────

@dataclass(frozen=True)
class KhaoNghiem:
    ma: str
    ten: str
    loai: str  # tay_tuy | ngung_dan | tam_ma | tam_tai | pha_hu | hop_dao | thien_kiep | phi_thang
    dieu_bao: str
    mo_ta: str
    so_dot: int = 1  # số đợt phải chịu
    can_dan: str = ""  # đan dược nên có trong tay
    tu_vong: float = 0.0  # xác suất chết nếu hỏng nặng


# khoá = chỉ số cảnh giới ĐÍCH (kết quả sau khi đột phá)
KHAO_NGHIEM: dict[int, KhaoNghiem] = {
    1: KhaoNghiem(
        ma="tay_tuy", ten="Tẩy Tuỷ Phạt Mao", loai="tay_tuy",
        dieu_bao="Đêm ngươi định xung quan, da đầu ngứa ran, và móng tay tự dài ra thêm một phần.",
        mo_ta=(
            "Trúc cơ không phải là thêm khí — là **thay xác**. Tạp chất tích trong tuỷ từ đời cha ông "
            "phải bị ép ra qua từng lỗ chân lông. Người ta nói cơn đau ấy giống như bị lột da khi còn tỉnh, "
            "và người nói câu đó đã trải qua rồi."
        ),
        can_dan="truc_co_dan", tu_vong=0.0,
    ),
    2: KhaoNghiem(
        ma="ngung_dan", ten="Ngưng Đan", loai="ngung_dan",
        dieu_bao="Trong ba ngày trước đó, mọi thứ ngươi ăn đều nhạt như nước. Thân thể đang tự dọn chỗ.",
        mo_ta=(
            "Chân khí phải nén lại thành một điểm. Nén được thì thành đan; nén hỏng thì đan vỡ, "
            "và người vỡ theo. Điều tàn nhẫn nhất của cửa ải này không phải chuyện sống chết — "
            "mà là **phẩm chất viên đan kết ra sẽ theo ngươi suốt đời còn lại**."
        ),
        can_dan="ket_dan_dan", tu_vong=0.05,
    ),
    3: KhaoNghiem(
        ma="tam_ma", ten="Tâm Ma Kiếp", loai="tam_ma",
        dieu_bao="Mấy hôm nay ngươi hay mơ thấy người đã chết. Trong mơ họ không trách gì, chỉ nhìn.",
        mo_ta=(
            "Kim đan vỡ ra để sinh nguyên anh — trong khoảnh khắc ấy thần hồn không có gì che chắn. "
            "Tâm ma sẽ tới, mang khuôn mặt của thứ ngươi sợ nhất, hoặc thứ ngươi thèm nhất. "
            "Không ai đánh thắng tâm ma bằng pháp thuật. Chỉ có **đạo tâm**."
        ),
        can_dan="dinh_than_dan", so_dot=3, tu_vong=0.08,
    ),
    4: KhaoNghiem(
        ma="tam_tai", ten="Tam Tai Chi Kiếp", loai="tam_tai",
        dieu_bao="Giếng nước cạn. Cây trong sân trút lá giữa mùa hè. Trời đất đang dọn chỗ cho một cơn thịnh nộ.",
        mo_ta=(
            "Ba tai lần lượt giáng xuống: **phong tai** xé thần hồn, **hoả tai** đốt tạp niệm, "
            "**lôi tai** đánh thẳng vào nguyên anh. Qua được ba tai thì nguyên anh hoá thần; "
            "không qua được thì tro cũng chẳng còn."
        ),
        can_dan="hoa_than_dan", so_dot=3, tu_vong=0.14,
    ),
    5: KhaoNghiem(
        ma="pha_hu", ten="Phá Hư Khảo", loai="pha_hu",
        dieu_bao="Bóng của ngươi in trên vách bắt đầu chậm hơn ngươi nửa nhịp.",
        mo_ta=(
            "Ngươi phải tự tay xé một vết rách trên tấm màn gọi là 'thực tại', chui qua đó, "
            "rồi quay lại mà còn nhớ mình là ai. Nhiều kẻ chui qua được. "
            "Số quay lại mà vẫn nhớ tên mình thì ít hơn nhiều."
        ),
        can_dan="hoa_than_dan", so_dot=2, tu_vong=0.16,
    ),
    6: KhaoNghiem(
        ma="hop_dao", ten="Hợp Đạo Khảo", loai="hop_dao",
        dieu_bao="Ngươi ngồi xuống và không muốn đứng dậy nữa. Cái mệt này không nằm ở thân.",
        mo_ta=(
            "Thần hồn và nhục thân phải nung chảy vào nhau. Trong lúc nung, hai thứ ấy sẽ cãi nhau — "
            "và ngươi là kẻ phải phân xử, dù ngươi chính là cả hai."
        ),
        can_dan="hoan_hon_dan", so_dot=2, tu_vong=0.18,
    ),
    7: KhaoNghiem(
        ma="dai_thua_tam_ma", ten="Đại Thừa Tâm Ma", loai="tam_ma",
        dieu_bao="Ngươi nhớ lại từng gương mặt mình đã bỏ lại phía sau. Chúng xếp hàng, kiên nhẫn, không xô đẩy.",
        mo_ta=(
            "Ở bậc này, tâm ma không doạ ngươi nữa. Nó **thuyết phục** ngươi. "
            "Nó dùng chính lý lẽ của ngươi, chính giọng nói của ngươi, và nó có cả một đời của ngươi làm bằng chứng."
        ),
        can_dan="dinh_than_dan", so_dot=4, tu_vong=0.20,
    ),
    8: KhaoNghiem(
        ma="tieu_thien_kiep", ten="Tiểu Thiên Kiếp", loai="thien_kiep",
        dieu_bao="Một đám mây tụ lại trên đầu ngươi và không chịu trôi đi, dù gió thổi ba ngày.",
        mo_ta=(
            "Từ đây, trời chính thức coi ngươi là chuyện phải giải quyết. "
            "Lôi kiếp giáng xuống không phải để thử ngươi — nó giáng xuống **để xoá ngươi**."
        ),
        can_dan="do_ach_dan", so_dot=5, tu_vong=0.28,
    ),
    9: KhaoNghiem(
        ma="cuu_trong_kiep", ten="Cửu Trọng Đại Kiếp", loai="phi_thang",
        dieu_bao="Cả một vùng trời đổi màu. Chim thú bỏ đi hết. Phàm nhân trong trăm dặm quỳ xuống mà không biết vì sao.",
        mo_ta=(
            "Chín đạo lôi kiếp, mỗi đạo mạnh gấp đôi đạo trước. Đạo thứ chín, sử sách chép là "
            "**thứ chưa từng có ai chép lại được** — vì kẻ chịu nó hoặc đã thành tiên, hoặc đã thành tro."
        ),
        can_dan="do_ach_dan", so_dot=9, tu_vong=0.42,
    ),
}


def khao_nghiem_cua(canh_gioi_dich: int) -> KhaoNghiem | None:
    return KHAO_NGHIEM.get(canh_gioi_dich)


# ─────────────────────── kim đan phẩm chất ───────────────────────

MO_TA_DAN_PHAM = {
    1: ("nhất phẩm", "Kim đan màu vàng đục, bề mặt rỗ như vỏ cam, xoay chậm và lệch. Loại đan này gọi là 'đủ dùng' — chỉ vậy thôi."),
    2: ("nhị phẩm", "Kim đan vàng xỉn, có vài vết vân xám. Xoay đều, nhưng nghe kỹ thì thấy tiếng ma sát."),
    3: ("tam phẩm", "Kim đan vàng sáng, tròn trịa. Phẩm chất trung bình của một đệ tử tông môn được nuôi tử tế."),
    4: ("tứ phẩm", "Kim đan ánh lên sắc hổ phách, mặt nhẵn không một vết. Trưởng lão nhìn qua sẽ gật đầu một cái."),
    5: ("ngũ phẩm", "Kim đan trong như mật ong để lâu năm, xoay êm tới mức ngươi phải nín thở mới nghe thấy."),
    6: ("lục phẩm", "Kim đan trong suốt, bên trong có một điểm sáng nhỏ đứng yên bất động — ấy là đạo ý đã kết."),
    7: ("thất phẩm", "Kim đan phát ra ánh sáng mờ soi rõ kinh mạch. Loại này trăm năm mới có một viên trong một tông môn."),
    8: ("bát phẩm", "Kim đan tự sinh phù văn trên bề mặt, không ai khắc mà có. Cả một châu chỉ đếm được vài kẻ."),
    9: ("cửu phẩm", "Kim đan trong veo như một giọt nước đọng, và khi nó xoay, trong đan điện ngươi nghe tiếng chuông ngân — "
                    "chín phẩm kim đan. Người mang nó, nếu không chết yểu, cuối cùng sẽ đứng ở nơi rất cao."),
}


def ten_dan_pham(pham: int) -> str:
    return MO_TA_DAN_PHAM.get(max(0, min(9, pham)), ("", ""))[0]


def mo_ta_dan_pham(pham: int) -> str:
    if pham <= 0:
        return ""
    return MO_TA_DAN_PHAM[max(1, min(9, pham))][1]


def he_so_dan_pham(pham: int) -> float:
    """Kim đan phẩm cao thì tu nhanh hơn và đánh nặng tay hơn. Người chơi chỉ thấy qua mô tả."""
    if pham <= 0:
        return 1.0
    return 1.0 + 0.035 * pham


# Cách người trong giang hồ gọi nhau
def xung_ho(chi_so: int, gioi_tinh: str) -> str:
    nam = gioi_tinh.lower().startswith("n") and not gioi_tinh.lower().startswith("nữ")
    if chi_so <= 0:
        return "đạo hữu"
    if chi_so == 1:
        return "sư huynh" if nam else "sư tỷ"
    if chi_so == 2:
        return "chân nhân"
    if chi_so == 3:
        return "lão tổ"
    if chi_so <= 5:
        return "tiền bối"
    return "đại năng"
