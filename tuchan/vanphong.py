"""Văn phòng — nơi mọi con số được đổi thành chữ.

Nguyên tắc: người chơi không bao giờ đọc thấy một con số nào của bản thân.
Họ chỉ đọc thấy cảm giác, dáng vẻ, và hậu quả.
"""

from __future__ import annotations

import random
from typing import Iterable, Sequence

from .canhgioi import canh_gioi, la_dinh_canh, ten_canh_gioi, tu_vi_can_thiet
from .data import vatpham

# ───────────────────────── thời gian ─────────────────────────

def khac_gio(giay: int) -> str:
    """Đổi giây thành cách nói thời gian của người xưa."""
    if giay <= 0:
        return "ngay bây giờ"
    if giay < 60:
        return "chưa đầy một nhịp trà"
    phut = giay / 60
    if phut < 15:
        return "chừng vài nhịp thở dài"
    if phut < 30:
        return "một khắc"
    if phut < 60:
        return "nửa canh giờ"
    gio = phut / 60
    if gio < 2:
        return "khoảng một canh giờ"
    if gio < 12:
        return f"chừng {int(gio // 2) or 1} canh giờ"
    if gio < 30:
        return "một ngày một đêm"
    ngay = gio / 24
    if ngay < 7:
        return f"chừng {int(ngay)} ngày"
    return f"chừng {int(ngay // 7)} tuần trăng"


def cho_them(giay: int, viec: str = "vận công") -> str:
    return (
        f"Khí huyết trong người còn chưa lắng lại. Hãy đợi thêm {khac_gio(giay)} nữa "
        f"rồi hẵng {viec}. Vội vàng trên đường tu là cách chết nhanh nhất."
    )


# ───────────────────────── tu vi ─────────────────────────

BAC_DAO_HANH = (
    (0.12, "Đạo hạnh trong đan điền còn mỏng như một hơi sương, tan đi lúc nào không hay."),
    (0.30, "Chân khí đã thành dòng, nhưng dòng ấy còn chảy ngập ngừng, gặp chỗ hẹp là ứ lại."),
    (0.52, "Chân khí chảy được một vòng châu thân mà không đứt quãng. Ngươi bắt đầu hiểu vì sao người ta gọi đây là 'công phu'."),
    (0.74, "Trong đan điền, khí đã đặc lại thành từng lớp, nặng và ấm. Ngồi lâu thì đầu ngón tay tê nhẹ."),
    (0.92, "Chân khí đầy tới mức chèn cả vào kinh mạch. Mỗi lần thu công, ngươi nghe trong xương có tiếng rạn rất khẽ."),
    (1.01, "Đã tới cực hạn của tầng này. Khí trong người sôi lên đòi lối ra — cửa ải trước mặt đang mở hé, và nó không chờ lâu."),
)


def mo_ta_dao_hanh(canh_gioi_i: int, tang: int, tu_vi: int) -> str:
    can = tu_vi_can_thiet(canh_gioi_i, tang)
    ti = min(1.0, tu_vi / can) if can else 1.0
    for nguong, cau in BAC_DAO_HANH:
        if ti < nguong:
            return cau
    return BAC_DAO_HANH[-1][1]


def sap_dot_pha(canh_gioi_i: int, tang: int, tu_vi: int) -> bool:
    return tu_vi >= tu_vi_can_thiet(canh_gioi_i, tang)


# ───────────────────────── thân thể, đạo tâm ─────────────────────────

def mo_ta_than_the(than_the: int, dang_bi_thuong: bool, con_lai: int = 0) -> str:
    if dang_bi_thuong:
        return (
            "Ngươi đang mang thương thế. Mỗi lần hít sâu, chỗ xương sườn bên trái lại nhói lên một cái, "
            f"và chân khí đi tới đó thì phải vòng tránh. Còn {khac_gio(con_lai)} nữa mới dám vận công mạnh."
        )
    if than_the >= 95:
        return "Thân thể không một vết xây xát, khí huyết đầy đặn, đi trong gió lạnh cũng thấy ấm."
    if than_the >= 75:
        return "Trên người còn vài vết bầm cũ, không đáng kể, nhưng trở trời thì biết."
    if than_the >= 50:
        return "Gân cốt còn đau âm ỉ từ lần trước. Ngươi giấu được người ngoài, giấu không được chính mình."
    if than_the >= 25:
        return "Nội thương chưa lành hẳn. Sắc mặt ngươi trắng bệch, môi khô, đi được trăm bước thì phải dừng."
    return "Ngươi đang ở mép cửa quỷ. Một cơn gió mạnh cũng đủ làm ngươi ngã, và ngã thì chưa chắc dậy."


def mo_ta_dao_tam(dao_tam: int) -> str:
    if dao_tam >= 90:
        return "Đạo tâm trong suốt như nước giếng mùa đông. Sóng gió bên ngoài không rọi được xuống đáy."
    if dao_tam >= 72:
        return "Đạo tâm vững. Ngươi vẫn nhớ vì sao mình bước lên con đường này, và câu trả lời chưa đổi."
    if dao_tam >= 55:
        return "Đạo tâm còn nguyên, nhưng đã có vết. Đêm khuya đôi lúc ngươi nằm nghĩ chuyện cũ mà không ngủ được."
    if dao_tam >= 35:
        return "Tâm ma đã bám rễ. Trong lúc vận công, thi thoảng ngươi nghe một giọng nói rất giống giọng mình, khuyên ngươi làm điều không nên."
    return "Đạo tâm rạn nứt. Ngươi không còn chắc cái đang ngồi trong xác này là ai — và điều đáng sợ là ngươi đã thôi thấy sợ."


def mo_ta_sat_nghiep(sat: int) -> str:
    if sat <= 0:
        return ""
    if sat < 10:
        return "Tay ngươi đã dính máu, tuy chưa nhiều. Đêm nằm, ngươi vẫn nhớ được mặt từng người."
    if sat < 40:
        return "Sát khí đã bám vào ngươi như mùi khói bám áo. Chó ngoài chợ thấy ngươi thì cụp đuôi."
    return "Sát nghiệp nặng như đá đeo cổ. Ngươi bước tới đâu, chim trên cành im tới đó. Người chính đạo nhìn ngươi bằng con mắt của đao phủ."


def mo_ta_danh_vong(dv: int, sat: int = 0) -> str:
    if dv <= 0:
        return "Trong giang hồ, tên ngươi chưa từng được ai nhắc tới. Đó vừa là nỗi nhục, vừa là tấm áo giáp."
    if dv < 60:
        return "Vài kẻ ở trấn dưới núi đã biết tên ngươi. Họ gật đầu khi ngươi đi qua, và bàn tán khi ngươi đi khuất."
    if dv < 250:
        return "Tên ngươi đã lọt vào tai các tán tu trong vùng. Có người tìm ngươi để kết giao, có người tìm ngươi vì lý do khác."
    if dv < 800:
        return "Đi tới đâu cũng có kẻ nhận ra. Người ta kể chuyện về ngươi, và phân nửa những chuyện ấy ngươi chưa từng làm."
    return ("Tên ngươi đã thành một thứ mà người ta hạ giọng khi nhắc tới. "
            + ("Trẻ con quấy khóc, người lớn doạ bằng tên ngươi." if sat > 30 else "Kẻ hậu bối chép tên ngươi vào ngọc giản để tự răn mình."))


def mo_ta_linh_thach(n: int) -> str:
    if n <= 0:
        return "Trong túi không còn lấy một viên linh thạch. Nghèo tới mức này thì đến yêu thú cũng chê."
    if n < 30:
        return "Trong túi còn vài viên linh thạch lẻ, đủ mua một bữa cơm nóng và một câu chỉ đường."
    if n < 200:
        return "Túi tiền hơi nặng tay. Đủ để mua ít dược liệu thô, chưa đủ để ai nể ngươi."
    if n < 1500:
        return "Linh thạch trong túi càn khôn xếp thành từng xâu. Xuống chợ, ngươi không cần hỏi giá trước."
    if n < 20000:
        return "Số linh thạch ngươi mang đủ để một gia đình phàm nhân sống ba đời không lo đói."
    return "Của cải của ngươi đã tới mức không đếm bằng viên nữa, mà đếm bằng rương. Điều đó tự nó là một mối nguy."


def mo_ta_tho_nguyen(tuoi_da_tu: int, canh_gioi_i: int) -> str:
    cg = canh_gioi(canh_gioi_i)
    if cg.tho_nguyen >= 3000:
        return "Thọ nguyên đối với ngươi đã không còn là chuyện phải đếm."
    return f"Thọ nguyên của kẻ đứng ở bậc này vào khoảng {cg.tho_nguyen} năm — nghe thì dài, nhưng ai đã đi rồi mới biết nó ngắn."


# ───────────────────────── vật phẩm ─────────────────────────

def liet_ke_tui(tui: dict[str, int], loai: str | None = None, toi_da: int = 12) -> str:
    muc = []
    for ma, sl in sorted(tui.items(), key=lambda kv: -kv[1]):
        vp = vatpham.lay(ma)
        if vp is None:
            continue
        if loai and vp.loai != loai:
            continue
        muc.append(f"{vp.ten}{f' ×{sl}' if sl > 1 else ''}")
    if not muc:
        return ""
    if len(muc) > toi_da:
        con = len(muc) - toi_da
        return ", ".join(muc[:toi_da]) + f", và {con} thứ vụn vặt khác"
    return ", ".join(muc)


def mo_ta_phap_bao(ma: str | None) -> str:
    if not ma:
        return "Ngươi chưa có pháp bảo nào đáng gọi tên. Khi đánh nhau, ngươi dựa vào xương thịt và vào may mắn."
    vp = vatpham.lay(ma)
    if vp is None:
        return "Một món pháp bảo cũ, đến tên nó ngươi cũng không rõ."
    return f"{vp.ten} theo bên mình. {vp.mo_ta}"


# ───────────────────────── nhịp văn ─────────────────────────

MO_DAU_TU_LUYEN = (
    "Ngươi tìm một chỗ khuất gió, phủi lớp lá khô, ngồi xuống.",
    "Cửa động khép lại. Ánh sáng cuối cùng biến mất, và ngươi bắt đầu.",
    "Ngươi xếp bằng, tay kết ấn, hơi thở dài dần ra cho tới khi gần như không còn.",
    "Trước mặt là một ngọn đèn dầu. Ngươi nhìn nó cho tới khi ngọn lửa thôi lay động trong mắt mình.",
    "Đêm xuống. Ngoài kia có tiếng côn trùng, rồi tiếng côn trùng cũng xa dần.",
)

KET_TU_LUYEN = (
    "Ngươi mở mắt. Ngọn đèn đã cạn dầu tự bao giờ.",
    "Khi thu công, vai áo đã ướt đẫm sương.",
    "Ngươi thở ra một hơi đục, và trong hơi thở ấy có mùi tanh rất nhạt của tạp chất.",
    "Ngươi đứng dậy. Chân tê dại, nhưng trong xương có cái gì đó khác trước.",
)


def cau(rng: random.Random, kho: Sequence[str]) -> str:
    return rng.choice(list(kho))


def doan(*cac_cau: str) -> str:
    return "\n\n".join(c.strip() for c in cac_cau if c and c.strip())


def nghieng(s: str) -> str:
    return f"*{s}*"


def loi_thoai(nguoi: str, loi: str) -> str:
    return f"**{nguoi}**: *“{loi}”*"


def gach_ngang() -> str:
    return "───────────────"
