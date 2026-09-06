"""Tông môn: nơi che chở, nơi bóc lột, nơi chôn người."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MonPhai:
    ma: str
    ten: str
    dia_the: str
    tinh_chat: str  # chính / trung lập / tà / ẩn dật
    mo_ta: str
    quy_cu: str
    yeu_cau_canh_gioi: int
    yeu_cau_tang: int
    cong_phap: str
    cong_phap_mo_ta: str
    he_so_tu_luyen: float
    he_so_chien: float
    ban_cong_thuc: tuple[str, ...] = ()
    ban_vat_pham: tuple[str, ...] = ()
    tranh: str = ""


CHUC_VI = ("Tạp Dịch Đệ Tử", "Ngoại Môn Đệ Tử", "Nội Môn Đệ Tử", "Chân Truyền Đệ Tử", "Trưởng Lão")
MOC_CONG_HIEN = (0, 60, 260, 900, 3000)


DANH_SACH: dict[str, MonPhai] = {}


def _mp(mp: MonPhai) -> None:
    DANH_SACH[mp.ma] = mp


_mp(MonPhai(
    ma="thanh_van",
    ten="Thanh Vân Môn",
    dia_the="Bảy ngọn núi nối nhau bên bờ Vân Hải, quanh năm mây trắng vắt ngang lưng chừng",
    tinh_chat="chính đạo",
    mo_ta=(
        "Ngàn bậc đá dẫn lên cổng núi, mỗi bậc đều có tên một đệ tử đã chết khắc ở mép. "
        "Thanh Vân Môn dạy người ta đứng thẳng, và cũng dạy người ta rằng đứng thẳng thì dễ gãy. "
        "Đệ tử mặc áo xanh, sáng quét lá, chiều luyện kiếm, tối chép kinh."
    ),
    quy_cu="Không giết đồng môn. Không cướp của phàm nhân. Không nói dối trước Vấn Tâm Kính.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=3,
    cong_phap="Thanh Vân Trường Xuân Quyết",
    cong_phap_mo_ta="Công pháp thuần chính, tiến chậm mà chắc, ít khi tẩu hoả nhập ma.",
    he_so_tu_luyen=1.12, he_so_chien=1.05,
    ban_cong_thuc=("ct_hoi_khi", "ct_liem_thuong"),
    ban_vat_pham=("thanh_cuong_kiem",),
    tranh="thanh_van_mon.png",
))
_mp(MonPhai(
    ma="huyen_vu",
    ten="Huyền Vũ Tông",
    dia_the="Dựng trên lưng một tảng đá đen khổng lồ giữa đầm lầy Bắc Cương",
    tinh_chat="chính đạo (cứng rắn)",
    mo_ta=(
        "Tông môn của những kẻ thích chịu đòn. Đệ tử Huyền Vũ luyện thân trước luyện khí, "
        "mỗi sáng đứng dưới thác nước lạnh cho tới khi môi tím. Người ngoài bảo họ ngu; "
        "người từng đánh nhau với họ thì không nói gì cả."
    ),
    quy_cu="Đã nhận thì không lùi. Lưng quay về đồng môn, mặt quay về kẻ địch.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=5,
    cong_phap="Huyền Vũ Bất Động Thân",
    cong_phap_mo_ta="Thân thể như mai rùa đen, đau thì có đau, gãy thì khó gãy.",
    he_so_tu_luyen=0.95, he_so_chien=1.22,
    ban_cong_thuc=("kp_thanh_cuong", "ct_liem_thuong"),
    ban_vat_pham=("liem_thuong_dan",),
))
_mp(MonPhai(
    ma="van_duoc",
    ten="Vạn Dược Cốc",
    dia_the="Một thung lũng kín, bốn mùa mù thuốc, chim bay ngang cũng say mà rơi",
    tinh_chat="trung lập",
    mo_ta=(
        "Không tranh bá, chỉ bán thuốc — và ai cũng phải mua thuốc. Đó là cách Vạn Dược Cốc "
        "sống sót qua ba lần đại chiến. Trong cốc, tiếng chày giã dược nghe suốt đêm như tiếng tim đập."
    ),
    quy_cu="Đan phương không ra khỏi cốc. Ai mang ra, cốc sẽ đòi lại — cùng với bàn tay.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=4,
    cong_phap="Bách Thảo Tâm Kinh",
    cong_phap_mo_ta="Lấy dược khí nuôi thân, tu chậm nhưng lò đan hiếm khi nổ.",
    he_so_tu_luyen=1.02, he_so_chien=0.90,
    ban_cong_thuc=("ct_bo_nguyen", "ct_dinh_than"),
    ban_vat_pham=("hoi_khi_dan", "hoi_khi_dan"),
))
_mp(MonPhai(
    ma="liet_hoa",
    ten="Liệt Hoả Kiếm Trai",
    dia_the="Ba gian nhà tranh trên miệng một hoả sơn đã ngủ",
    tinh_chat="chính đạo (cực đoan)",
    mo_ta=(
        "Cả trai chỉ có mười bảy người, và mười bảy thanh kiếm. Họ không nhận đệ tử vì tư chất, "
        "chỉ nhận vì một câu hỏi: 'Ngươi dám chết cho một nhát kiếm không?' "
        "Ai trả lời quá nhanh thì bị đuổi."
    ),
    quy_cu="Kiếm rút ra là phải thấy máu, dù là máu mình.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=8,
    cong_phap="Liệt Hoả Nhất Kiếm",
    cong_phap_mo_ta="Đem cả tính mạng dồn vào một kiếm. Thắng thì rực rỡ, thua thì không còn gì.",
    he_so_tu_luyen=0.98, he_so_chien=1.35,
    ban_cong_thuc=("kp_hac_van",),
    ban_vat_pham=("thanh_cuong_kiem",),
))
_mp(MonPhai(
    ma="u_minh",
    ten="U Minh Quỷ Đạo",
    dia_the="Không ai biết. Người ta chỉ tìm thấy cửa của nó khi sắp chết",
    tinh_chat="ma đạo",
    mo_ta=(
        "Ở đây không có sư phụ, chỉ có kẻ mạnh hơn. Không có sư huynh, chỉ có kẻ chưa chết. "
        "U Minh Quỷ Đạo cho ngươi tu vi nhanh gấp đôi thiên hạ, đổi lại mỗi bước tiến đều có mùi tanh."
    ),
    quy_cu="Không có quy củ. Chỉ có một điều: kẻ phản bội sẽ bị luyện thành phướn.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=6,
    cong_phap="U Minh Thôn Hồn Quyết",
    cong_phap_mo_ta="Nuốt sinh khí kẻ khác làm của mình. Tiến nhanh, tâm ma cũng nhanh.",
    he_so_tu_luyen=1.45, he_so_chien=1.18,
    ban_cong_thuc=("ct_hoan_hon",),
    ban_vat_pham=("am_hon_sa",),
))
_mp(MonPhai(
    ma="vong_hai",
    ten="Vọng Hải Tự",
    dia_the="Một ngôi chùa đá bám trên vách biển, sóng đánh tới bậc thềm",
    tinh_chat="ẩn dật",
    mo_ta=(
        "Tăng nhân ở đây không tụng kinh, chỉ ngồi nhìn biển. Có người ngồi ba mươi năm. "
        "Họ nói: sóng vỗ vạn lần vào một tảng đá, tảng đá không kêu, ấy mới là đạo tâm."
    ),
    quy_cu="Mỗi tháng phải ngồi một đêm không động, không nghĩ, không sợ.",
    yeu_cau_canh_gioi=0, yeu_cau_tang=4,
    cong_phap="Tĩnh Hải Thiền Tâm",
    cong_phap_mo_ta="Đạo tâm vững như đá kè, đột phá ít khi tâm ma quấy nhiễu.",
    he_so_tu_luyen=1.05, he_so_chien=0.98,
    ban_cong_thuc=("ct_dinh_than",),
    ban_vat_pham=("dinh_than_dan",),
))


def lay(ma: str) -> MonPhai | None:
    return DANH_SACH.get(ma)


def chuc_vi_theo_cong_hien(cong_hien: int) -> str:
    chuc = CHUC_VI[0]
    for i, moc in enumerate(MOC_CONG_HIEN):
        if cong_hien >= moc:
            chuc = CHUC_VI[i]
    return chuc


def tim_theo_ten(chuoi: str) -> MonPhai | None:
    chuoi = chuoi.strip().lower()
    if not chuoi:
        return None
    for mp in DANH_SACH.values():
        if chuoi == mp.ma or chuoi in mp.ten.lower():
            return mp
    return None
