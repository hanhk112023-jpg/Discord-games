"""Yêu vương — những kẻ không sống để bị giết một cách yên ổn.

Khác yêu thú thường gặp trên đường: mỗi con dưới đây có cả một vùng đất làm lãnh địa,
có thuộc hạ, có tiếng tăm, và có đủ trí tuệ để nhớ mặt kẻ đã làm nó chảy máu.
Chúng không thuộc về ai — giết được là của mình.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BossVuong:
    ma: str
    ten: str
    hieu: str            # danh xưng thiên hạ gọi
    canh_gioi: int
    tang: int
    so_tuot: int         # "độ dày": một kẻ đúng bậc phải tốn chừng ấy nhát mới hạ nổi
    mo_ta: str
    xuat_the: str        # cảnh nó hiện thế
    thu_doan: tuple[str, ...] = ()
    chien_loi: dict[str, int] = field(default_factory=dict)   # ma vật phẩm -> phần nghìn khi lục xác
    hung_hang: float = 1.25
    tho: float = 1.0     # nhân sức chiến
    huyet_le: int = 45   # phút nó nán lại chiến trường trước khi rút
    dia_danh: str = ""   # mã địa danh liên quan (chỉ để kể chuyện)
    loi_de: str = ""     # câu nó "nói" khi thấy ngươi


BOSS: dict[str, BossVuong] = {}


def _b(b: BossVuong) -> None:
    BOSS[b.ma] = b


_b(BossVuong(
    ma="thiet_nha_tru_vuong", ten="Thiết Nha Trư Vương",
    hieu="Chúa bầy heo rừng núi Thanh Khê",
    canh_gioi=0, tang=12, so_tuot=6, hung_hang=1.15, tho=0.95, huyet_le=35,
    dia_danh="thanh_khe_son",
    mo_ta="Nặng gần nghìn cân, răng nanh dài chĩa ngược lên tận mắt. Ba đám thợ săn vào rừng "
           "mỗi mùa, chỉ tiếng vó nó là đi ra.",
    xuat_the="Sương đêm chưa tan, cả dải Thanh Khê Sơn rung lên theo một nhịp đều đặn. "
             "Chim chóc bay tổ hàng đàn. Thiết Nha Trư Vương vừa đứng dậy khỏi vũng lầy — "
             "và nó không thích bị loài người đánh thức.",
    loi_de="Nó hếch mõm ngửi ngươi, rồi gầm một tiếng ngắn. Tiếng gầm ấy không đe doạ. Nó thông báo.",
    thu_doan=("lao cả khối thịt vào như một cơn sạt lở",
              "vung cặp răng nanh hất người lên không",
              "dậm chân, mặt đất nứt ra theo hình nan quạt",
              "lăn tròn đè nghiến theo đường chéo"),
    chien_loi={"yeu_dan": 500, "huyet_tinh_chi": 300, "hoang_tinh_thao": 600,
               "linh_thach_ha": 900, "hac_thiet": 250},
))

_b(BossVuong(
    ma="xich_diem_xa_vuong", ten="Xích Diệm Xà Vương",
    hieu="Con lửa chín đầu dưới đầm Hắc Phong",
    canh_gioi=1, tang=3, so_tuot=9, hung_hang=1.3, tho=1.1, huyet_le=45,
    dia_danh="hac_phong_lam",
    mo_ta="Thân đỏ như than hồng để nguội, dài mười trượng. Nước đầm sôi sùng sục mỗi lần nó trở mình; "
           "cả một vùng rừng cháy đã ba lần, không lần nào là do lửa trên bờ.",
    xuat_the="Mặt đầm Hắc Phong tự nhiên sôi. Một cột nước dựng đứng giữa đầm, rồi tách ra thành "
             "chín cái đầu, mỗi cái nhìn theo một hướng. Khói trắng bay lên, mang mùi lưu hoàng.",
    loi_de="Chín cái đầu cùng rít lên một lúc. Chín cái bóng cùng đổ lên người ngươi.",
    thu_doan=("phun một luồng lửa liếm dài mười trượng",
              "siết thân quanh chân ngươi kéo dần vào nước sôi",
              "vẩy đuôi quét — mặt đầm dựng lên thành tường nước",
              "chín đầu nhả lửa cùng lúc theo hình rẻ quạt"),
    chien_loi={"yeu_dan": 600, "u_dam_lien": 220, "thanh_dong_tinh": 250,
               "lac_lo_tinh_kim": 140, "linh_thach_ha": 1400, "hoang_tinh_thao": 300},
))

_b(BossVuong(
    ma="bach_cot_tinh_ton", ten="Bạch Cốt Tinh Tôn",
    hieu="Kẻ đứng dậy từ Vạn Cốt Nhai",
    canh_gioi=2, tang=1, so_tuot=11, hung_hang=1.35, tho=1.2, huyet_le=45,
    dia_danh="van_cot_nhai",
    mo_ta="Xương trắng xếp thành một tôn tượng cao ba trượng, mắt là hai đốm lửa xanh. "
           "Nó không gầm — nó chỉ giơ tay, và xương chất thành núi trước mặt.",
    xuat_the="Gió ở Vạn Cốt Nhai đổi hướng. Rồi cả bãi xương bắt đầu rền — không phải động đất, "
             "là tiếng chúng tự xếp chồng lên nhau. Bạch Cốt Tinh Tôn đã ngủ đủ rồi.",
    loi_de="Hai đốm lửa xanh quay lại nhìn ngươi. Ngươi nghe thấy một giọng nói, "
           "mà không tai nào của ngươi bắt được.",
    thu_doan=("gọi xương dưới chân dựng thành chông",
              "nắm lấy binh khí của ngươi bằng những ngón xương bám kín",
              "hoả xanh lan lên kinh mạch",
              "tan thành nghìn mảnh rồi ráp lại ngay sau lưng ngươi"),
    chien_loi={"am_hon_sa": 550, "yeu_thu_noi_dan": 350, "long_van_ngoc": 90,
               "co_tich_tan_do": 150, "linh_thach_ha": 2600},
))

_b(BossVuong(
    ma="u_thuy_giao_long", ten="U Thuỷ Giao Long",
    hieu="Con giao long đã một lần hoá",
    canh_gioi=3, tang=2, so_tuot=13, hung_hang=1.4, tho=1.3, huyet_le=50,
    dia_danh="u_dam_trach",
    mo_ta="Sừng đã mọc, vảy đã hoá long, nhưng mệnh trời chưa cho thăng — nó kẹt lại nửa đường, "
           "và cái kẹt ấy ủ thành hận ý. Cả đầm U Đàm là của nó; từng con cá dưới đầm cũng biết điều đó.",
    xuat_the="Nước đầm U Đàm rút đi một nửa trong nửa canh giờ — rút xuống dưới, không rút sang ngang. "
             "Rồi mặt nước nứt ra. U Thuỷ Giao Long nhô đầu lên, nhìn trời như nhìn một kẻ thù cũ.",
    loi_de="Nó cuộn mình nhìn ngươi, không vội. Ở bậc của nó, ăn một kẻ chưa kết đan không cần đứng dậy gấp.",
    thu_doan=("nuốt một hơi nước rồi phun thành mũi lao",
              "quấn lấy ngươi kéo xuống đáy tăm tối",
              "vẩy sắc như dao, quét ngang ba mươi bước",
              "gầm — nước quanh ngươi đặc lại thành búa"),
    chien_loi={"giao_can": 800, "u_dam_lien": 500, "long_van_ngoc": 260,
               "yeu_vuong_cot": 140, "linh_thach_ha": 5000, "cuu_diep_linh_lan": 120},
))

_b(BossVuong(
    ma="huyet_ma_ton", ten="Huyết Ma Tôn",
    hieu="Ma đầu ba trăm năm chưa chết",
    canh_gioi=4, tang=2, so_tuot=15, hung_hang=1.55, tho=1.35, huyet_le=50,
    dia_danh="hac_phong_lam",
    mo_ta="Ba trăm trước các đại tông môn liên thủ vây giết, nhưng không tìm thấy xác. "
           "Nay một con sông đỏ ngầu chảy ngược, và người ta hiểu: ngài ấy đã về.",
    xuat_the="Đêm nay trăng đỏ. Không phải tại mây. Chín con sông quanh Hắc Phong Lâm cùng đổi màu "
             "trong một khắc, cá nổi trắng bụng, đầu quay hết vào bờ — như chạy trốn một thứ gì đó dưới đáy.",
    loi_de="*“Lũ hậu bối các ngươi tu cái gì mà khí tức nhạt thếch.”* Giọng hắn êm, "
           "và máu trong người ngươi đứng lại một nhịp.",
    thu_doan=("hút một hơi máu từ ngoài trăm trượng",
              "hoá thành sương đỏ, đòn của ngươi đánh vào khoảng không",
              "nuốt một phần thần thức của ngươi rồi nhai chậm rãi",
              "mỉm cười — và pháp bảo của ngươi im lìm không còn nghe lệnh nữa"),
    chien_loi={"am_hon_sa": 700, "lac_lo_tinh_kim": 500, "hoa_tinh_thach": 400,
               "huyet_bo_de": 60, "yeu_vuong_cot": 320, "linh_thach_ha": 9000},
))

_b(BossVuong(
    ma="thap_van_loi_thu", ten="Thập Vạn Lôi Thú",
    hieu="Con thú đẻ ra từ sét",
    canh_gioi=5, tang=2, so_tuot=17, hung_hang=1.5, tho=1.45, huyet_le=55,
    dia_danh="lac_tinh_hoang_nguyen",
    mo_ta="Lông mượt như lông hồ ly mà do tôi bằng sét. Nó chạy trên mây, ăn sét, ngủ trong giông. "
           "Mỗi lần nó tỉnh, những kẻ sắp đột phá phải dời núi mà đi — sét của nó không phân biệt ai.",
    xuat_the="Trời không mưa, nhưng cả Lạc Tinh Hoang Nguyên ướt sũng — ướt vì sét đọng sẵn trong không trung. "
             "Một bóng thú sải mình trên tầng mây thứ ba, mỗi bước nó đi là một tiếng ầm ầm cuối trời.",
    loi_de="Nó nhìn ngươi bằng đôi mắt một màu trắng. Ngươi thấy tóc mình dựng đứng, "
           "và ngửi thấy mùi khét của chính mình.",
    thu_doan=("gom sét cả một vùng rồi quất ra thành roi",
              "chạy trên không, đạp mây nổ thành tiếng",
              "rống — mọi kim loại trên người ngươi nóng rẫy",
              "hoá thành một luồng điện xuyên thẳng qua mọi lớp hộ thể"),
    chien_loi={"thien_loi_moc": 700, "tinh_ha_sa": 250,
               "hoa_tinh_thach": 300, "yeu_vuong_cot": 350,
               "cuu_thien_huyen_thiet": 90, "linh_thach_ha": 15000},
))

_b(BossVuong(
    ma="cuu_u_ma_vuong", ten="Cửu U Ma Vương",
    hieu="Thứ bị nhốt dưới Hàn Uyên",
    canh_gioi=7, tang=1, so_tuot=22, hung_hang=1.7, tho=1.6, huyet_le=60,
    dia_danh="cuu_u_han_uyen",
    mo_ta="Không ai kể lại được hình hài nó — những kẻ từng nhìn xuống đáy Cửu U Hàn Uyên "
           "về tới bờ thì đều không còn muốn nói chuyện nữa. Người ta gọi nó là Ma Vương cho gọn, "
           "vì không tìm được từ nào nhẹ hơn.",
    xuat_the="Nước Cửu U Hàn Uyên đứng lại giữa dòng. Không đóng băng — đứng lại. "
             "Rồi từ dưới đáy, một bàn tay đen như mực bám lấy mép vực, và cả thung lũng nghiêng đi ba tấc.",
    loi_de="Nó chưa lên hẳn. Nhưng ngươi đã nghe thấy tên mình được gọi — bằng chính giọng của ngươi.",
    thu_doan=("kéo bóng của ngươi xuống vực thay cho nó",
              "nói một câu, và câu ấy ở lại trong đầu ngươi vĩnh viễn",
              "móc một ký ức của ngươi ra, xem, rồi không trả lại",
              "để ngươi đánh trúng — rồi cười, vì đòn ấy đang quay về tìm chủ"),
    chien_loi={"am_hon_sa": 900, "cuu_thien_huyen_thiet": 450, "tinh_ha_sa": 600,
               "yeu_vuong_cot": 900, "thien_tam_qua": 180, "linh_thach_ha": 40000,
               "van_nien_ngoc_toai": 120},
))

DANH_SACH: list[BossVuong] = list(BOSS.values())


def lay(ma: str) -> BossVuong | None:
    return BOSS.get(ma)


def theo_bac(bac_cao_nhat: int) -> list[BossVuong]:
    """Chỉ gọi được kẻ không quá sức bậc cao nhất đang có mặt — gọi ẩu thì cả vùng chịu tang."""
    ra = [b for b in DANH_SACH if b.canh_gioi <= bac_cao_nhat + 1]
    return ra or [min(DANH_SACH, key=lambda x: x.canh_gioi)]


def chon_ngau_nhien(bac_cao_nhat: int, rng) -> BossVuong:
    ung_vien = theo_bac(bac_cao_nhat)
    trong_so = [1.0 / (1.0 + max(0, bac_cao_nhat + 1 - b.canh_gioi) ** 2) for b in ung_vien]
    return rng.choices(ung_vien, weights=trong_so, k=1)[0]
