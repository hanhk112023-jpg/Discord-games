"""Thang bậc tu hành: từ kẻ phàm phu hít lấy hơi sương, tới bậc Chân Tiên.

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

    @property
    def ten_day_du(self) -> str:
        return self.ten


TANG_PHO_THONG = ("sơ kỳ", "trung kỳ", "hậu kỳ", "đại viên mãn")

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
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=900,
        tho_nguyen=200,
        khi_the="khí tức trầm như giếng cổ, người phàm đứng gần tự dưng thấy lạnh gáy",
        than_the="tạp chất trong xương tuỷ đã rửa sạch, da thịt ẩn ẩn ánh ngọc, đao thường khó phạm",
        cam_ngo="linh khí không còn là sương mà là nước, hít một hơi là cả ngực đầy",
        the_gioi="đủ tư cách làm khách khanh một huyện, đủ tư cách chết trong một cuộc tranh chấp nhỏ",
        tranh="",
    ),
    CanhGioi(
        ma="ket_dan",
        ten="Kết Đan",
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=4200,
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
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=19000,
        tho_nguyen=1200,
        khi_the="ánh mắt nhìn qua khiến kẻ Trúc Cơ nghẹn thở, đất dưới chân không dám vỡ",
        than_the="kim đan đã vỡ, trong đó ngồi một anh nhi mang khuôn mặt của chính ngươi, thân xác chỉ còn là áo khoác",
        cam_ngo="thần thức trải ra như lưới, cách mười dặm nghe được tiếng kiến bò",
        the_gioi="một cái tên đủ để cả một tông môn trung đẳng nghiêng mình",
        tranh="",
    ),
    CanhGioi(
        ma="hoa_than",
        ten="Hóa Thần",
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=80000,
        tho_nguyen=3000,
        khi_the="đến gần thì trời đất tự nhiên im tiếng, chim thú nằm rạp",
        than_the="nguyên anh hòa vào thần niệm, thân này tan cũng chưa chắc chết",
        cam_ngo="một niệm khởi lên, gió mây trong trăm dặm đổi chiều",
        the_gioi="lời nói ra là quy củ của một vùng, không ai dám gọi thẳng tên",
        tranh="",
    ),
    CanhGioi(
        ma="luyen_hu",
        ten="Luyện Hư",
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=320000,
        tho_nguyen=8000,
        khi_the="thân ảnh khi mờ khi tỏ, kẻ nhìn lâu sẽ chảy máu mắt",
        than_the="đang luyện cái hư vô làm xương, bước một bước xé một tấc không gian",
        cam_ngo="thấy rõ những sợi tơ vô hình chằng chịt gọi là quy tắc",
        the_gioi="đã ra khỏi vòng tranh chấp thế tục, chỉ còn tranh với đồng đạo và với trời",
        tranh="",
    ),
    CanhGioi(
        ma="hop_the",
        ten="Hợp Thể",
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=1300000,
        tho_nguyen=20000,
        khi_the="thân là pháp, pháp là thân, đứng đâu thì nơi đó thành lãnh vực",
        than_the="thần hồn và nhục thân hợp làm một khối, đao chém vào chỉ nghe tiếng chuông",
        cam_ngo="thiên địa đối với ngươi đã bớt lạnh nhạt, nhưng chưa từng dịu dàng",
        the_gioi="một trụ cột của cả một châu, sống chết của vạn người treo trên một ý niệm",
        tranh="",
    ),
    CanhGioi(
        ma="dai_thua",
        ten="Đại Thừa",
        so_tang=4,
        ten_tang=TANG_PHO_THONG,
        tu_vi_moi_tang=5200000,
        tho_nguyen=50000,
        khi_the="không còn khí tức, vì cả bầu trời trên đầu ngươi chính là khí tức của ngươi",
        than_the="mỗi tấc da thịt đều chứa một tiểu thiên địa đang xoay",
        cam_ngo="nghe được tiếng kiếp số đang gõ cửa, từng nhịp một, rất kiên nhẫn",
        the_gioi="ngươi đã là truyền thuyết mà đám hậu bối chép trong ngọc giản",
        tranh="",
    ),
    CanhGioi(
        ma="do_kiep",
        ten="Độ Kiếp",
        so_tang=4,
        ten_tang=("nhất trọng", "nhị trọng", "tam trọng", "cửu tử nhất sinh"),
        tu_vi_moi_tang=21000000,
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
        so_tang=1,
        ten_tang=("bất diệt",),
        tu_vi_moi_tang=10**9,
        tho_nguyen=10**7,
        khi_the="phàm nhân nhìn thấy ngươi chỉ nhớ được một vệt sáng và một cơn buồn ngủ",
        than_the="xác phàm đã bỏ lại dưới núi từ lâu, cái đứng đây là đạo đã thành hình",
        cam_ngo="thiên địa nói chuyện với ngươi bằng thứ ngôn ngữ mà chữ nghĩa không chép nổi",
        the_gioi="tên ngươi trở thành một thời đại",
        tranh="",
    ),
)

CHI_SO_THEO_MA = {cg.ma: i for i, cg in enumerate(BANG_CANH_GIOI)}
TOI_DA = len(BANG_CANH_GIOI) - 1


def canh_gioi(chi_so: int) -> CanhGioi:
    return BANG_CANH_GIOI[max(0, min(TOI_DA, chi_so))]


def ten_canh_gioi(chi_so: int, tang: int) -> str:
    cg = canh_gioi(chi_so)
    t = max(1, min(cg.so_tang, tang))
    if cg.ma == "chan_tien":
        return cg.ten
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
    return goc * (1.0 + 0.55 * (tang - 1) / max(1, canh_gioi(chi_so).so_tang - 1) * 3)


def khoang_cach_cach_bac(a_chi_so: int, b_chi_so: int) -> int:
    return a_chi_so - b_chi_so


# Cách người trong giang hồ gọi nhau
def xung_ho(chi_so: int, gioi_tinh: str) -> str:
    nam = gioi_tinh.lower().startswith("n") and not gioi_tinh.lower().startswith("nữ")
    if chi_so <= 0:
        return "đạo hữu" if nam else "đạo hữu"
    if chi_so == 1:
        return "sư huynh" if nam else "sư tỷ"
    if chi_so == 2:
        return "chân nhân" if nam else "chân nhân"
    if chi_so == 3:
        return "lão tổ" if nam else "lão tổ"
    if chi_so <= 5:
        return "tiền bối"
    return "đại năng"
