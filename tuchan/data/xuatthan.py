"""Xuất thân — cái gánh mà người ta mang theo suốt đường tu."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class XuatThan:
    ma: str
    ten: str
    mo_ta: str
    linh_can: str
    loi_the: str
    tu_chat: float  # hệ số hấp thu linh khí
    can_cot: float  # hệ số thân thể / chiến đấu
    dao_tam: int
    linh_thach: int
    hanh_trang: dict[str, int] = field(default_factory=dict)


DANH_SACH: dict[str, XuatThan] = {}


def _x(x: XuatThan) -> None:
    DANH_SACH[x.ma] = x


_x(XuatThan(
    ma="pham_nhan", ten="Phàm nhân",
    mo_ta=(
        "Ngươi sinh ra trong một thôn không có tên trên bản đồ. Cha ngươi chết vì lao dịch, "
        "mẹ ngươi chết vì đói. Năm mười ba tuổi ngươi thấy một người mặc áo trắng bay qua nóc nhà, "
        "và từ đó ngươi không ngủ ngon được nữa."
    ),
    linh_can="Ngũ hành tạp linh căn — thứ mà tông môn lớn liếc một cái rồi quay đi",
    loi_the="Ta không muốn làm bùn dưới chân người khác.",
    tu_chat=0.90, can_cot=1.00, dao_tam=62, linh_thach=15,
    hanh_trang={"hoang_tinh_thao": 2},
))
_x(XuatThan(
    ma="con_nha_vo", ten="Con nhà võ",
    mo_ta=(
        "Cha ngươi là võ sư một trấn nhỏ, cả đời đấm vào bao cát và cả đời quỳ trước quan phủ. "
        "Ông dạy ngươi rằng nắm đấm giải quyết được nhiều thứ, rồi chết dưới một nhát kiếm "
        "của kẻ không thèm rút kiếm ra hết."
    ),
    linh_can="Linh căn đục, nhưng gân cốt hơn người",
    loi_the="Ta sẽ đấm được cái thứ đã giết cha ta.",
    tu_chat=0.85, can_cot=1.28, dao_tam=68, linh_thach=25,
    hanh_trang={"thanh_cuong_kiem": 1, "hoang_tinh_thao": 1},
))
_x(XuatThan(
    ma="the_gia", ten="Tiểu thư / công tử thế gia",
    mo_ta=(
        "Ngươi lớn lên giữa trầm hương và gấm vóc, được đút cho đan dược từ lúc chưa biết đi. "
        "Nhưng gia tộc suy rồi — đêm đó lửa cháy tới rường nhà, và ngươi chạy ra khỏi cổng "
        "với một túi linh thạch cùng cái họ không còn ai dám gọi."
    ),
    linh_can="Song linh căn được tẩy tuỷ từ nhỏ, sạch nhưng mỏng",
    loi_the="Ta phải sống đủ lâu để dựng lại tấm biển đã cháy.",
    tu_chat=1.15, can_cot=0.88, dao_tam=55, linh_thach=180,
    hanh_trang={"hoi_khi_dan": 2, "linh_thach_ha": 0},
))
_x(XuatThan(
    ma="tan_tu", ten="Tán tu lang bạt",
    mo_ta=(
        "Ngươi không nhớ mình bao nhiêu tuổi. Ngươi nhớ mình đã ngủ trong bao nhiêu miếu hoang, "
        "đã ăn bao nhiêu con chuột nướng, đã chạy khỏi bao nhiêu kẻ mạnh hơn. "
        "Cái ngươi giỏi nhất không phải là đánh, mà là sống sót."
    ),
    linh_can="Tạp linh căn, nhưng kinh nghiệm bù lại phần nào",
    loi_the="Chết thì dễ. Ta chọn cái khó.",
    tu_chat=0.95, can_cot=1.10, dao_tam=75, linh_thach=40,
    hanh_trang={"hoang_tinh_thao": 3, "hac_thiet": 2},
))
_x(XuatThan(
    ma="dao_dong", ten="Đạo đồng quét sân",
    mo_ta=(
        "Mười năm ngươi quét lá trước Tàng Kinh Các, không ai dạy ngươi một chữ. "
        "Nhưng lá rơi thì có tiếng, và trong tiếng lá rơi ngươi nghe lỏm được vài câu khẩu quyết "
        "mà các sư huynh đọc oang oang vì tưởng ngươi điếc."
    ),
    linh_can="Đơn linh căn thuộc Mộc — hiếm, nhưng chẳng ai buồn kiểm tra cho ngươi",
    loi_the="Chỗ của ta không phải ở dưới bậc thềm.",
    tu_chat=1.25, can_cot=0.92, dao_tam=70, linh_thach=8,
    hanh_trang={"thanh_lan_hoa": 2, "hoan_hinh_ngoc_gian": 1},
))
_x(XuatThan(
    ma="mo_coi_chien_tranh", ten="Cô nhi thời loạn",
    mo_ta=(
        "Ngươi bò ra từ dưới một đống xác. Người ta nói ngươi mang vận xúi quẩy, "
        "vì bất cứ ai cưu mang ngươi đều gặp hoạ. Ngươi đã tin điều đó rất lâu — "
        "cho tới khi ngươi hiểu ra rằng cái đi theo ngươi không phải xui, mà là một cái gì khác."
    ),
    linh_can="Linh căn dị biến, âm khí quấn quanh xương sống",
    loi_the="Nếu trời đã đánh dấu ta, thì ta sẽ đánh dấu lại.",
    tu_chat=1.05, can_cot=1.05, dao_tam=48, linh_thach=0,
    hanh_trang={"am_hon_sa": 1},
))


def lay(ma: str) -> XuatThan | None:
    return DANH_SACH.get(ma)
