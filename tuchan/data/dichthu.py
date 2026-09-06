"""Yêu thú, ma tu, tán tu ác độc — những kẻ ngươi sẽ gặp trên đường."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DichThu:
    ma: str
    ten: str
    loai: str  # yeu_thu | ma_tu | tan_tu | hon_linh
    canh_gioi: int
    tang: int
    mo_ta: str
    lam_quen: str  # câu tả lúc chạm mặt
    thu_doan: tuple[str, ...]  # đòn đánh đặc trưng, dùng cho lời kể trận
    chien_loi: dict[str, int] = field(default_factory=dict)  # ma vật phẩm -> phần nghìn rơi
    hung_hang: float = 1.0
    tho: float = 1.0  # sức chịu đòn


DANH_SACH: dict[str, DichThu] = {}


def _d(d: DichThu) -> None:
    DANH_SACH[d.ma] = d


_d(DichThu(
    ma="xich_mao_lang", ten="Xích Mao Lang", loai="yeu_thu", canh_gioi=0, tang=3,
    mo_ta="Sói lông đỏ, cao ngang thắt lưng người, chạy theo bầy nhưng con đầu đàn luôn xông ra trước.",
    lam_quen="Bụi cỏ tranh rẽ ra. Một con sói lông đỏ bước tới, không sủa, chỉ hạ thấp vai xuống.",
    thu_doan=("lao tới cắn vào cổ tay", "quét đuôi hất bụi vào mắt ngươi", "cắn hụt rồi lùi lại thở khò khè"),
    chien_loi={"yeu_dan": 250, "hoang_tinh_thao": 400}, hung_hang=1.0, tho=0.9,
))
_d(DichThu(
    ma="thach_giap_thu", ten="Thạch Giáp Thú", loai="yeu_thu", canh_gioi=0, tang=8,
    mo_ta="Con thú mai đá, chậm chạp, nhưng vỏ nó từng làm gãy ba thanh kiếm trong một buổi chiều.",
    lam_quen="Tảng đá bên khe suối đột nhiên nhúc nhích, rồi thò ra bốn cái chân ngắn ngủn.",
    thu_doan=("thúc mai đá vào lồng ngực ngươi", "co mình lại chịu trọn một đòn rồi phản kích", "lăn nghiêng chèn ngươi vào vách"),
    chien_loi={"hac_thiet": 600, "yeu_dan": 200}, hung_hang=0.8, tho=1.5,
))
_d(DichThu(
    ma="thanh_dieu", ten="Thanh Diêu Điểu", loai="yeu_thu", canh_gioi=1, tang=1,
    mo_ta="Chim xanh sải cánh hai trượng, móng vuốt cắt được giáp da.",
    lam_quen="Bóng một cánh chim quét qua mặt đất, lớn đến mức ngươi tưởng mây che mất trời.",
    thu_doan=("bổ nhào từ trên cao xuống", "vỗ cánh tạo gió cắt", "kêu một tiếng chói tai làm thần thức ngươi rung lên"),
    chien_loi={"giao_can": 200, "yeu_dan": 350, "thanh_lan_hoa": 300}, hung_hang=1.15, tho=0.85,
))
_d(DichThu(
    ma="hac_lan_giao", ten="Hắc Lân Giao", loai="yeu_thu", canh_gioi=1, tang=3,
    mo_ta="Giao long vảy đen sống dưới đầm sâu, nửa thân còn là rắn, nửa thân đã bắt đầu ra sừng.",
    lam_quen="Mặt nước đen phồng lên một khối, rồi vỡ ra. Mùi tanh đập vào mặt ngươi trước khi ngươi kịp thấy nó.",
    thu_doan=("quấn lấy chân ngươi kéo xuống nước", "phun một cột nước đen như mực", "quật đuôi làm bùn bắn cao ba trượng"),
    chien_loi={"giao_can": 700, "yeu_dan": 500, "u_dam_lien": 150}, hung_hang=1.25, tho=1.3,
))
_d(DichThu(
    ma="thi_ma", ten="Thi Ma", loai="hon_linh", canh_gioi=1, tang=2,
    mo_ta="Xác người tu hành chết mà không chịu nằm yên, móng tay dài quá gối, mắt chỉ còn hai hốc tối.",
    lam_quen="Ngươi ngửi thấy mùi hương trầm đã cũ. Trong bóng tối, một thứ gì đó đang đứng thẳng — nhưng nó không thở.",
    thu_doan=("cào một đường năm vệt lên ngực ngươi", "há miệng hút lấy sinh khí quanh người", "đứng im nhìn ngươi cho tới khi tay ngươi run"),
    chien_loi={"am_hon_sa": 450, "huyet_tinh_chi": 300}, hung_hang=1.1, tho=1.2,
))
_d(DichThu(
    ma="tan_tu_cuop_duong", ten="Tán tu cướp đường", loai="tan_tu", canh_gioi=0, tang=11,
    mo_ta="Áo bào vá chằng vá đụp, mắt láo liên. Hắn không muốn giết ngươi — hắn chỉ muốn túi đồ của ngươi. Nhưng nếu cần thì hắn sẽ giết.",
    lam_quen="'Đạo hữu.' Giọng nói vọng ra từ sau gốc cây. 'Bỏ túi càn khôn xuống, ta cho ngươi đi.'",
    thu_doan=("phóng một nắm ám khí tẩm độc", "đâm tới bằng đoản đao gỉ", "giả vờ bỏ chạy rồi quay lại đâm lén"),
    chien_loi={"linh_thach_ha": 900, "hoi_khi_dan": 250, "hac_thiet": 300}, hung_hang=1.2, tho=0.95,
))
_d(DichThu(
    ma="hac_bao_ma_tu", ten="Hắc Bào Ma Tu", loai="ma_tu", canh_gioi=2, tang=1,
    mo_ta="Kẻ tu ma đạo, tay áo rộng, trong đó nuôi thứ gì không rõ. Người hắn đi qua thì cỏ héo thành một vệt.",
    lam_quen="Hắn không giấu khí tức. Hắn muốn ngươi biết. Cỏ dưới chân ngươi bắt đầu quăn lại từng cọng.",
    thu_doan=("vỗ ra một chưởng đen kịt mang mùi tanh", "thả ra ba con quỷ ảnh cắn vào thần thức", "cười khẽ và bước tới một bước — chỉ một bước mà đã tới trước mặt"),
    chien_loi={"am_hon_sa": 700, "u_dam_lien": 300, "yeu_thu_noi_dan": 150, "linh_thach_ha": 2500}, hung_hang=1.35, tho=1.1,
))
_d(DichThu(
    ma="huyet_nhan_vuon", ten="Huyết Nhãn Viên", loai="yeu_thu", canh_gioi=2, tang=2,
    mo_ta="Vượn khổng lồ mắt đỏ ngầu, đấm một quyền thì cây cổ thụ gãy đôi ở giữa thân.",
    lam_quen="Cả khu rừng im bặt. Rồi một tiếng gầm dội xuống từ tán lá, và mưa lá rụng đầy vai ngươi.",
    thu_doan=("giáng hai nắm đấm xuống như búa tạ", "bứt cả một cây ném thẳng vào ngươi", "đấm vào ngực mình rồi lao tới"),
    chien_loi={"yeu_thu_noi_dan": 350, "bach_van_sam": 250, "long_van_ngoc": 40}, hung_hang=1.3, tho=1.4,
))
_d(DichThu(
    ma="co_thi_tuong", ten="Cổ Thi Tướng", loai="hon_linh", canh_gioi=3, tang=1,
    mo_ta="Xác một võ tướng thời cổ, giáp đã gỉ dính vào da. Nó không nhớ mình là ai, chỉ nhớ mệnh lệnh cuối cùng: giữ cửa.",
    lam_quen="Trong bóng tối của cổ mộ, một tiếng giáp sắt cọ xát. Rất chậm. Rất đều. Nó đang đứng dậy.",
    thu_doan=("bổ xuống một đao mang theo cả trăm năm oán khí", "gầm một tiếng làm mộ đạo rung chuyển", "nắm lấy binh khí của ngươi bằng tay không"),
    chien_loi={"lac_lo_tinh_kim": 300, "long_van_ngoc": 200, "am_hon_sa": 500}, hung_hang=1.4, tho=1.6,
))
_d(DichThu(
    ma="ky_si_vo_danh", ten="Kỵ sĩ vô danh", loai="tan_tu", canh_gioi=1, tang=4,
    mo_ta="Một người cưỡi con thú giáp đen, mặt che kín, không xưng danh. Hắn xuất hiện ở chỗ nào có kẻ tu hành cô độc.",
    lam_quen="Tiếng vó nện trên đá, đều đặn, không vội. Hắn ghìm cương cách ngươi mười bước, và không nói gì cả.",
    thu_doan=("thúc thú lao thẳng vào ngươi", "vung trường thương quét một vòng ngang", "ném xuống một cái nhìn nặng hơn cả đòn đánh"),
    chien_loi={"hac_thiet": 500, "thanh_dong_tinh": 300, "linh_thach_ha": 1200, "hoan_hinh_ngoc_gian": 120},
    hung_hang=1.2, tho=1.15,
))


def lay(ma: str) -> DichThu | None:
    return DANH_SACH.get(ma)


def theo_muc(canh_gioi: int, do_lech: int = 1) -> list[DichThu]:
    ra = [d for d in DANH_SACH.values() if abs(d.canh_gioi - canh_gioi) <= do_lech]
    return ra or list(DANH_SACH.values())


def ngau_nhien_theo_muc(canh_gioi: int, rng: random.Random | None = None) -> DichThu:
    rng = rng or random
    ung_vien = theo_muc(canh_gioi)
    trong_so = []
    for d in ung_vien:
        lech = d.canh_gioi - canh_gioi
        trong_so.append(3.0 if lech == 0 else (1.6 if lech > 0 else 1.2))
    return rng.choices(ung_vien, weights=trong_so, k=1)[0]
