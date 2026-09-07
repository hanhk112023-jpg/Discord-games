"""Thiên biến — trời đất đổi sắc, và mọi kẻ tu hành đều phải chịu chung."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThienBien:
    ma: str
    ten: str
    mo_ta: str
    dieu_bao: str  # điềm báo lúc bắt đầu
    khi_tan: str  # câu kể lúc sự kiện qua đi
    gio: int  # kéo dài bao lâu (giờ thực)
    anh_huong: dict[str, float] = field(default_factory=dict)
    # khoá ảnh hưởng: tu_luyen, nguy_hiem, dan_thanh, khi_thanh, gia_ca, ky_ngo


DANH_SACH: dict[str, ThienBien] = {}


def _s(s: ThienBien) -> None:
    DANH_SACH[s.ma] = s


_s(ThienBien(
    ma="linh_trieu", ten="Linh Khí Triều Tịch",
    dieu_bao=(
        "Nửa đêm, giếng trong trấn tự dâng nước. Chó không sủa. Trẻ con sốt nhẹ rồi tự khỏi. "
        "Đến rạng sáng, kẻ tu hành nào cũng thấy hô hấp nhẹ bẫng — linh khí trong trời đất đang lên như thuỷ triều."
    ),
    mo_ta="Linh khí dày đặc chưa từng thấy. Ngồi đâu cũng là động phủ, thở một hơi bằng người khác vận công nửa ngày.",
    khi_tan="Thuỷ triều rút. Không khí lại nhạt đi, và ai chưa kịp tận dụng thì chỉ còn biết tiếc.",
    gio=6, anh_huong={"tu_luyen": 1.85, "dan_thanh": 1.15, "ky_ngo": 1.2},
))
_s(ThienBien(
    ma="ma_khi_nhieu", ten="Ma Khí Nhiễu Loạn",
    dieu_bao=(
        "Mặt trăng đêm nay có quầng đỏ. Ở nghĩa địa ngoài trấn, đất mới đắp tự lún xuống. "
        "Các lão tu sĩ khoá cửa động phủ, dán bùa, và không nhận khách."
    ),
    mo_ta="Ma khí tràn khỏi những chỗ đáng lẽ phải khoá kín. Yêu thú hoá điên, thi thể không chịu nằm yên, tâm ma dễ khởi.",
    khi_tan="Ma khí lắng xuống như bụi sau cơn gió. Người ta bắt đầu đếm xem thiếu mất những ai.",
    gio=8, anh_huong={"nguy_hiem": 1.7, "tu_luyen": 0.9, "ky_ngo": 1.35},
))
_s(ThienBien(
    ma="co_tich_khai", ten="Cổ Tích Khai Mở",
    dieu_bao=(
        "Trên vách Vân Thạch Nhai hiện ra một khe nứt hình con mắt, bên trong có ánh sáng vàng đục. "
        "Trong ba ngày, tán tu từ khắp nơi kéo về, ngựa xe chật cả đường núi."
    ),
    mo_ta="Một tòa di tích thượng cổ mở cửa. Kỳ ngộ nhiều gấp bội, nhưng người tranh cũng nhiều gấp bội.",
    khi_tan="Khe nứt khép lại, nuốt theo cả những kẻ chưa kịp ra. Trên vách đá chỉ còn một vệt sẹo mờ.",
    gio=12, anh_huong={"ky_ngo": 2.2, "nguy_hiem": 1.3, "tu_luyen": 1.05},
))
_s(ThienBien(
    ma="hoi_vo", ten="Hội Võ Giang Hồ",
    dieu_bao=(
        "Cờ hiệu của bảy tông môn cắm dọc quan đạo. Đài đấu bằng đá xanh dựng xong trong một đêm. "
        "Ở chợ, người ta cá cược tên của những kẻ sẽ không đi được xuống đài."
    ),
    mo_ta="Hội võ mở ra. Danh vọng đổi bằng máu, và mọi trận đấu đều có người nhìn.",
    khi_tan="Đài đấu dỡ đi. Vết máu trên đá xanh rửa ba lần vẫn còn.",
    gio=10, anh_huong={"nguy_hiem": 1.1, "danh_vong": 1.8},
))
_s(ThienBien(
    ma="dai_han", ten="Đại Hạn Thiên Tai",
    dieu_bao=(
        "Ba tháng không mưa. Sông Thanh Khê cạn tới đáy, lộ ra những thứ mà đáy sông vẫn giấu. "
        "Phàm nhân chết đói dọc đường, và giá một hạt gạo bằng nửa viên linh thạch."
    ),
    mo_ta="Trời đất khô kiệt, linh khí tán loạn. Dược liệu héo, đan lô khó tụ hoả, lòng người thì dễ ác.",
    khi_tan="Cơn mưa đầu tiên rơi xuống. Người ta quỳ giữa đường mà khóc, kể cả những kẻ đã Trúc Cơ.",
    gio=9, anh_huong={"tu_luyen": 0.75, "dan_thanh": 0.8, "gia_ca": 1.6, "nguy_hiem": 1.2},
))
_s(ThienBien(
    ma="tinh_van", ten="Tinh Vẫn Giáng Thế",
    dieu_bao=(
        "Một vệt sáng trắng rạch ngang trời đêm, chậm rãi, gần như trịch thượng. "
        "Nó rơi xuống Lạc Tinh Hoang Nguyên, và tiếng nổ tới ba khắc sau mới vọng đến tai người."
    ),
    mo_ta="Tinh thạch rơi rải khắp hoang nguyên. Vật liệu luyện khí thượng phẩm nằm ngay trên mặt đất — cùng với những kẻ tới nhặt.",
    khi_tan="Hoang nguyên lại vắng. Chỉ còn những hố cháy đen và mấy nấm mộ đắp vội.",
    gio=8, anh_huong={"khi_thanh": 1.5, "nguy_hiem": 1.35, "ky_ngo": 1.3},
))
_s(ThienBien(
    ma="huyet_nguyet", ten="Huyết Nguyệt Đương Không",
    dieu_bao=(
        "Trăng lên, và trăng có màu của máu đã khô. Không một con thú nào kêu. "
        "Người tu ma đạo hôm nay cười nhiều hơn thường lệ."
    ),
    mo_ta="Dưới huyết nguyệt, sát khí nuôi người. Kẻ tà tu mạnh lên, kẻ chính tu thấy đạo tâm chao đảo.",
    khi_tan="Trăng trở lại màu bạc. Có kẻ tỉnh dậy, không nhớ đêm qua tay mình đã làm gì.",
    gio=7, anh_huong={"nguy_hiem": 1.5, "sat_khi": 1.6, "dao_tam": 0.85},
))


def lay(ma: str) -> ThienBien | None:
    return DANH_SACH.get(ma)


def tim_theo_ten(chuoi: str) -> ThienBien | None:
    chuoi = (chuoi or "").strip().lower()
    for s in DANH_SACH.values():
        if chuoi == s.ma or chuoi in s.ten.lower():
            return s
    return None
