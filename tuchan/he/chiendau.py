"""Giao đấu — kể lại một trận đánh bằng chữ, không bằng con số.

Máy tính vẫn phải tính, nhưng phép tính nằm dưới lớp da. Người chơi chỉ thấy:
ai áp đảo ai, ai lùi, ai đổ máu, ai còn đứng.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..canhgioi import (canh_gioi, he_so_dan_pham, suc_manh_nen,
                        ten_canh_gioi)
from ..data import vatpham


@dataclass
class BenThamChien:
    ten: str
    canh_gioi: int
    tang: int
    xung: str = "hắn"  # đại từ khi kể
    phap_bao: str = ""
    he_so_chien: float = 1.0
    can_cot: float = 1.0
    dao_tam: int = 60
    than_the: int = 100
    thu_doan: tuple[str, ...] = ()
    la_nguoi_choi: bool = False
    hung_hang: float = 1.0
    cong_phap: str = ""
    dan_pham: int = 0  # phẩm chất kim đan, nếu đã kết đan

    @property
    def ten_phap_bao(self) -> str:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.ten if vp else ""

    @property
    def loai_vu_khi(self) -> str:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.loai_vu_khi if vp else ""

    @property
    def uy_luc_phap_bao(self) -> float:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.uy_luc if vp else 0.0

    def suc_chien(self) -> float:
        s = suc_manh_nen(self.canh_gioi, self.tang)
        s *= 1.0 + self.uy_luc_phap_bao
        s *= self.he_so_chien
        s *= 0.75 + 0.25 * self.can_cot
        s *= 0.55 + 0.45 * max(0, min(100, self.than_the)) / 100.0
        s *= 0.88 + 0.24 * max(0, min(100, self.dao_tam)) / 100.0
        if self.canh_gioi >= 2 and self.dan_pham:
            s *= he_so_dan_pham(self.dan_pham)
        return max(0.01, s)


@dataclass
class TranDau:
    thang: BenThamChien
    thua: BenThamChien
    van: list[str] = field(default_factory=list)
    ap_dao: float = 0.5  # 0.5 = ngang tài, 1.0 = nghiền nát
    chi_mang: bool = False  # kẻ thua suýt chết / chết
    ton_thuong_ke_thua: int = 30
    so_hiep: int = 0


# ───────────────────────── kho câu ─────────────────────────

MO_TRAN = (
    "{a} không nói một lời thừa. Khí tức trong người dâng lên, cỏ dưới chân rạp xuống thành một vòng tròn.",
    "Hai bên cách nhau mười bước. Không ai bước trước, nhưng không khí giữa hai người đã bắt đầu méo đi.",
    "{b} nhìn {a} từ đầu tới chân, rồi chậm rãi xoay cổ tay một vòng. Đó là cách nói 'được' mà không cần mở miệng.",
    "Gió ngừng. Trong khoảnh khắc ấy, cả hai đều nghe rất rõ tiếng tim mình.",
    "{a} hít một hơi. Bụi trên mặt đất run lên rồi lặng đi — chân khí đã trải kín một vùng.",
)

AP_DAO_MANH = (
    "{a} bước tới một bước. Chỉ một bước, mà khoảng cách mười trượng biến mất. {b} còn chưa kịp đổi thế tấn thì đã bị đánh bật ra sau, cày một rãnh dài trên nền đất.",
    "{vk_a} quét ngang. {b} giơ tay đỡ, và cả cánh tay tê dại tới tận vai; xương cổ tay kêu một tiếng khô khốc.",
    "{a} không né, cũng không đỡ. {a} chịu trọn một đòn của {b}, rồi giáng trả một chưởng khiến {b} ộc máu.",
    "{b} vừa vận công thì thấy chân khí trong người tán loạn — khí thế của {a} đè xuống như một tấm bia đá đặt lên ngực.",
    "Ba chiêu. Chỉ ba chiêu, và {b} đã không còn giữ nổi thế công. Đến chiêu thứ tư thì {b} chỉ còn đỡ.",
    "{a} tiến, {b} lùi. {a} lại tiến, {b} lại lùi. Đến bước thứ bảy thì sau lưng {b} là vách đá.",
)

AP_DAO_NHE = (
    "{a} chiếm được tiên cơ. {vk_a} đi trước nửa nhịp, và trong đánh nhau, nửa nhịp là cả một mạng người.",
    "{b} đỡ được, nhưng đỡ một cách vất vả. Mồ hôi chảy vào mắt, {b} không dám đưa tay lên lau.",
    "{a} đánh liền năm chiêu, chiêu nào cũng nhắm vào chỗ {b} vừa hở ra. {b} lùi hai bước, thở gấp.",
    "Một vệt máu vẽ lên không trung. {b} lảo đảo, đưa tay quệt khoé miệng, rồi nhìn xuống bàn tay mình một cách bình thản đến lạ.",
    "{a} đổi bộ pháp, vòng ra sau lưng {b}. {b} xoay người kịp, nhưng vạt áo đã bị xé toạc một mảng.",
)

GIANG_CO = (
    "Hai bên đấm cùng lúc, hai nắm tay chạm nhau giữa không trung. Tiếng nổ trầm đục, cả hai cùng lùi ba bước, cùng thở dốc.",
    "{vk_a} và đòn của {b} khoá vào nhau. Trong một khắc, không ai nhúc nhích được, chỉ có mặt đất dưới chân họ nứt ra từng đường.",
    "{a} đánh mười chiêu, {b} đỡ chín chiêu, chiêu thứ mười thì cả hai cùng dính đòn. Không ai kêu một tiếng.",
    "Chân khí hai bên va nhau tạo thành sóng, quét bụi bay lên mù mịt. Khi bụi lắng, cả hai vẫn đứng, áo đều rách.",
    "Đây không còn là đấu pháp. Đây là hai kẻ cùng cắn răng xem ai buông tay trước.",
)

PHAN_KICH = (
    "Nhưng {b} chờ đúng khoảnh khắc ấy. {b} bỏ mặc một đòn vào vai mình để đổi lấy một cú thúc chỏ vào yết hầu {a}.",
    "{b} đột nhiên không lùi nữa. {b} bước tới — vào trong tầm đánh của {a} — và mọi chiêu thức của {a} bỗng thành thừa thãi.",
    "Máu trên mặt {b} chảy xuống cằm. {b} cười. Rồi {b} phản kích một đòn khiến {a} phải nhảy ngược ra sau.",
    "{b} làm một việc không ai ngờ: {b} ném binh khí đi. Tay không, {b} chộp lấy cổ tay {a}, và {a} nghe xương mình kêu.",
)

DUNG_PHAP_BAO = (
    "{a} thả {vk_a} ra. Vật ấy bay lên, xoay một vòng, và ánh sáng của nó soi rõ vẻ mặt {b}.",
    "{vk_a} rời tay {a}, hoá thành một vệt sáng dài đâm xuống. {b} lăn người tránh, mặt đất chỗ đó thủng một lỗ sâu bằng cả cánh tay.",
    "{a} bắt quyết. {vk_a} rung lên, phù văn trên thân nó sáng lên từng chữ một, chậm rãi, như đang đếm ngược.",
)

CHIEU_CUOI_THANG_LON = (
    "Đòn cuối cùng đến khi {b} vừa hụt hơi. {a} không giữ lại chút nào. {b} bay ngược ra sau, đập vào một thân cây, và cây gãy.",
    "{a} vung tay. Không có tiếng động lớn nào cả — chỉ có {b} khuỵu xuống, rồi đổ nghiêng, mắt vẫn mở.",
    "{a} thu chiêu trước khi nó chạm tới cổ {b}. Đó không phải lòng nhân từ. Đó chỉ là {a} không muốn bẩn tay.",
    "Một tiếng 'rắc'. {b} nằm đó, thở, nhưng không dậy nổi nữa. Trận này, kết thúc rồi.",
)

CHIEU_CUOI_SAT_SAO = (
    "Cả hai cùng gục xuống một gối. Nhưng {a} đứng dậy trước — sớm hơn đúng một nhịp thở. Trong giang hồ, thắng thua chỉ cần chừng đó.",
    "{b} còn giơ tay lên, muốn đánh thêm một chiêu nữa. Bàn tay ấy run, rồi buông xuống. {b} nhìn {a}, gật đầu một cái rất khẽ.",
    "Đòn cuối trúng cả hai. {a} lảo đảo nhưng không ngã. {b} ngã, và nằm đó nhìn trời, thở ra một hơi rất dài.",
    "Không ai biết chiêu nào là chiêu quyết định. Chỉ biết khi bụi tan, {a} vẫn đứng, còn {b} thì không.",
)

CHET_HUT = (
    "{b} nằm đó, máu chảy thành vũng, hơi thở đứt quãng. Nếu không có chút vận may cuối cùng ấy, hôm nay đã là ngày giỗ của {b}.",
    "Đòn ấy chỉ chệch đi nửa tấc. Nửa tấc ấy là ranh giới giữa một vết thương và một nấm mồ.",
)


# ───────────── lối đánh riêng của từng loại binh khí ─────────────
# Mỗi món khí giới đánh một kiểu; người xem trận nhìn cách ra đòn là biết ngươi cầm gì.

CHIEU_THEO_VU_KHI: dict[str, tuple[str, ...]] = {
    "kiem": (
        "{a} rút kiếm. Không có hoa mỹ nào cả — một đường thẳng, đi từ dưới lên, "
        "nhắm đúng chỗ {b} vừa đưa tay lên đỡ.",
        "{vk_a} điểm ba cái liên tiếp vào cùng một điểm trên hộ thể của {b}. "
        "Điểm thứ ba thì lớp linh quang ấy vỡ ra như men sứ.",
        "{a} không đâm, không chém. {a} **đặt** mũi kiếm vào giữa hai chiêu của {b} — "
        "và cả pho chiêu thức của {b} tự nghẽn lại ở đó.",
    ),
    "dao": (
        "{vk_a} bổ xuống bằng cả trọng lượng thân người. {b} đỡ ngang, và hai gối {b} lún xuống đất nửa tấc.",
        "{a} chém một nhát rộng, cố ý để hở sườn. {b} lao vào chỗ hở — đúng như {a} muốn — "
        "và nhát đao thứ hai đã chờ sẵn ở đó.",
        "Đao đi đường vòng cung, sát mặt đất, hất cả một mảng bụi đá tạt vào mắt {b} trước khi lưỡi đao tới.",
    ),
    "thuong": (
        "{vk_a} đâm thẳng, rút về, đâm thẳng. Cùng một đường, cùng một điểm, mỗi lần một nhanh hơn. "
        "{b} đỡ được hai lần đầu.",
        "{a} xoay thương, cán thương quét ngang chân {b}. {b} nhảy lên, và mũi thương đã đợi ở trên.",
        "Thương dài hơn đao kiếm một trượng, và cái một trượng ấy là toàn bộ vấn đề của {b} trong trận này.",
    ),
    "phi_kiem": (
        "{a} búng ngón tay. {vk_a} vụt đi, xuyên qua chỗ {b} vừa đứng, vòng lại từ sau lưng.",
        "Ba luồng kiếm quang chia ba hướng, khoá kín đường lui. {b} chỉ còn cách tiến lên — "
        "mà tiến lên là điều {a} đang chờ.",
        "{vk_a} bay lượn quanh {b} như một con ong dữ. {b} chém trúng nó một cái, và cả cánh tay {b} tê dại "
        "vì phản chấn của thần thức {a} truyền qua.",
    ),
    "cung": (
        "{a} kéo dây cung. Không nghe tiếng bật, chỉ thấy vai {b} nở ra một bông hoa đỏ.",
        "Mũi tên thứ nhất bị {b} chém rơi. Mũi thứ hai đi theo đúng vệt mũi thứ nhất, và {b} không kịp chém lần hai.",
        "{a} lùi, vừa lùi vừa bắn. Trong trận này, khoảng cách chính là binh khí thật sự của {a}.",
    ),
    "ti": (
        "Không ai thấy {vk_a} đâu cả. Chỉ thấy trên má {b} bỗng hiện một đường đỏ mảnh, rồi máu mới chảy ra.",
        "{a} khẽ giật cổ tay. Cành cây sau lưng {b} đứt lìa, rơi xuống — và {b} chợt hiểu mình đang đứng giữa một cái lồng.",
        "Sợi tơ siết lấy cổ tay {b}. {b} giằng ra, đổi lấy một vệt cắt sâu tới xương.",
    ),
    "chuy": (
        "{vk_a} giáng xuống. {b} tránh, và chỗ đất ấy lún thành một cái hố nông, đá vụn bắn lên tới ngang ngực.",
        "Không có chiêu thức gì cả. {a} vung, {b} đỡ, và xương cánh tay {b} kêu một tiếng rất khó chịu.",
    ),
    "phu": (
        "Phù giấy bay ra, tự cháy giữa không trung, và ngọn lửa ấy đổi hình thành một cánh tay chộp lấy {b}.",
        "{a} dán một đạo phù lên chính lòng bàn tay mình rồi đẩy tới. Không khí trước mặt {b} đặc lại như hồ.",
    ),
    "giap": (
        "{b} đánh trúng {a} một đòn thật. Đòn ấy trượt đi trên {vk_a} như nước trượt trên lá sen.",
        "{a} không thèm né. {a} bước xuyên qua chiêu thức của {b}, để đòn đánh nện thẳng vào người mình, "
        "rồi túm lấy cổ áo {b}.",
    ),
    "chuong": (
        "{vk_a} rung một tiếng. Chỉ một tiếng — nhưng {b} loạng choạng, tai ù đi, và trong đầu {b} có gì đó vừa nứt.",
        "Tiếng chuông thứ hai, thứ ba nối nhau. {b} vận công bịt tai, nhưng âm ba không đi qua tai, "
        "nó đi thẳng vào thần hồn.",
    ),
    "an": (
        "{a} đưa {vk_a} lên rồi đóng xuống không trung. Cả một vùng đất trước mặt {b} sụt xuống nửa thước.",
        "Ấn quang đè xuống vai {b}. {b} gồng lên chống đỡ, hai chân lún dần vào nền đá.",
    ),
    "phuong": (
        "{a} phất {vk_a}. Từ trong đó tràn ra sương đen, và trong sương có tiếng người khóc — "
        "không phải một người, mà rất nhiều.",
        "Bóng đen quấn lấy chân {b}, kéo xuống. {b} chém đứt chúng, nhưng chỗ bị chạm vào thì lạnh buốt tới tận xương.",
    ),
    "but": (
        "{a} viết một chữ giữa không trung. Chữ ấy sáng lên rồi ập xuống, và {b} bỗng thấy thân thể mình nặng gấp mười.",
        "Ngòi bút đi trên hư không như đi trên giấy. Nét cuối vừa dứt, gió quanh {b} ngừng hẳn — "
        "cả không khí cũng không chịu vào phổi {b} nữa.",
    ),
    "quat": (
        "{vk_a} xoè ra. Năm gương mặt trên nan quạt cùng mở miệng, và {b} nghe thấy chính giọng mình đang cầu xin.",
        "Một cái phất tay. Gió âm quét qua, và những chỗ nó chạm tới thì cỏ hoá tro, còn máu trên mặt {b} đông cứng lại.",
    ),
    "dinh": (
        "{vk_a} phóng to giữa không trung, úp xuống. {b} lăn ra khỏi bóng của nó vào đúng khoảnh khắc cuối.",
        "Đốm lửa xanh trong lòng đỉnh liếm ra một cái. Nó không cháy da thịt — nó cháy thẳng vào chân khí của {b}.",
    ),
    "kinh": (
        "Mặt gương chớp một cái. Chiêu thức của {b} bị hắt ngược trở lại, và {b} phải tự đỡ đòn của chính mình.",
        "{a} nghiêng {vk_a} đi một góc rất nhỏ. Chỉ thế thôi, mà hướng của cả trận đấu đổi chiều.",
    ),
    "dai": (
        "Phiến đá đen hạ xuống một tấc. Chỉ một tấc, mà {b} quỳ sụp một gối — không phải vì bị đánh, "
        "mà vì có thứ gì đó bảo {b} phải quỳ.",
        "{a} đứng yên. Trảm đài xoay chậm trên đầu {a}, và bóng của nó phủ lên {b} như một bản án đã tuyên.",
    ),
}

TAY_KHONG = (
    "{a} không dùng binh khí. {a} chỉ bước vào, cùi chỏ đi trước, và tiếng va chạm nghe như đá đập vào đá.",
    "Nắm tay {a} và chưởng phong của {b} chạm nhau. {b} là kẻ rụt tay về trước.",
)


def _vk(b: BenThamChien) -> str:
    ten = b.ten_phap_bao
    if ten:
        return ten
    return "bàn tay trần của " + b.ten


def _dien(mau: str, a: BenThamChien, b: BenThamChien) -> str:
    return mau.format(a=a.ten, b=b.ten, vk_a=_vk(a), vk_b=_vk(b))


def giao_dau(
    a: BenThamChien,
    b: BenThamChien,
    rng: random.Random | None = None,
    boi_canh: str = "",
    so_hiep: int | None = None,
) -> TranDau:
    rng = rng or random.Random()
    sa, sb = a.suc_chien(), b.suc_chien()
    chenh = sa / (sa + sb)

    van: list[str] = []
    if boi_canh:
        van.append(boi_canh)
    van.append(_dien(rng.choice(MO_TRAN), a, b))

    hiep = so_hiep or rng.randint(3, 5)
    diem_a = 0.0
    for i in range(hiep):
        # mỗi hiệp là một lần gieo, kẻ yếu vẫn có cửa
        va = sa * rng.uniform(0.62, 1.42) * (1.0 + 0.10 * (a.hung_hang - 1))
        vb = sb * rng.uniform(0.62, 1.42) * (1.0 + 0.10 * (b.hung_hang - 1))
        ti = va / (va + vb)
        diem_a += ti - 0.5

        ke_tren, ke_duoi = (a, b) if ti >= 0.5 else (b, a)
        do_lech = abs(ti - 0.5)

        if do_lech < 0.06:
            cau = rng.choice(GIANG_CO)
        elif do_lech < 0.16:
            cau = rng.choice(AP_DAO_NHE)
        else:
            rieng = CHIEU_THEO_VU_KHI.get(ke_tren.loai_vu_khi, ())
            gieo = rng.random()
            if rieng and gieo < 0.55:
                cau = rng.choice(rieng)
            elif not ke_tren.ten_phap_bao and gieo < 0.35:
                cau = rng.choice(TAY_KHONG)
            elif ke_tren.ten_phap_bao and gieo < 0.78:
                cau = rng.choice(DUNG_PHAP_BAO)
            else:
                cau = rng.choice(AP_DAO_MANH)
        van.append(_dien(cau, ke_tren, ke_duoi))

        # thủ đoạn riêng của yêu thú / ma tu
        if ke_tren.thu_doan and rng.random() < 0.5:
            van.append(
                f"{ke_tren.ten} {rng.choice(list(ke_tren.thu_doan))}."
            )

        # đòn phản kích bất ngờ
        if i == hiep - 2 and rng.random() < 0.32:
            van.append(_dien(rng.choice(PHAN_KICH), ke_tren, ke_duoi))
            diem_a += (0.10 if ke_duoi is a else -0.10)

    thang, thua = (a, b) if diem_a >= 0 else (b, a)
    ap_dao = min(1.0, 0.5 + abs(diem_a) / max(1, hiep) * 1.6)

    if ap_dao > 0.72:
        van.append(_dien(rng.choice(CHIEU_CUOI_THANG_LON), thang, thua))
    else:
        van.append(_dien(rng.choice(CHIEU_CUOI_SAT_SAO), thang, thua))

    ton_thuong = int(18 + 62 * (ap_dao - 0.5) * 2 + rng.randint(-6, 8))
    ton_thuong = max(8, min(96, ton_thuong))
    chi_mang = ap_dao > 0.9 and rng.random() < 0.55
    if chi_mang:
        van.append(_dien(rng.choice(CHET_HUT), thang, thua))
        ton_thuong = min(99, ton_thuong + 15)

    return TranDau(
        thang=thang, thua=thua, van=van, ap_dao=ap_dao,
        chi_mang=chi_mang, ton_thuong_ke_thua=ton_thuong, so_hiep=hiep,
    )


# ───────────────────────── lời bình sau trận ─────────────────────────

def loi_binh(td: TranDau, nguoi_choi: BenThamChien) -> str:
    thang = td.thang is nguoi_choi
    if thang and td.ap_dao > 0.8:
        return ("Ngươi đứng giữa bãi chiến, hơi thở còn chưa loạn. Chênh lệch lớn tới mức "
                "trận này không dạy ngươi được gì — trừ một điều: cảm giác được làm kẻ mạnh.")
    if thang and td.ap_dao > 0.62:
        return ("Ngươi thắng, và thắng gọn. Nhưng khi lau vết máu trên khoé môi, ngươi biết "
                "chỉ cần một chiêu đi chệch là kết cục đã khác.")
    if thang:
        return ("Ngươi thắng — thắng bằng nửa nhịp thở và một chút vận may. "
                "Đêm nay ngươi sẽ nằm nghĩ lại chiêu thứ ba, và toát mồ hôi lạnh.")
    if td.ap_dao > 0.85:
        return ("Ngươi thua, thua đến mức không có gì để biện bạch. Nằm dưới đất nhìn lên, "
                "ngươi hiểu ra khoảng cách giữa hai bậc cảnh giới không phải là con số — mà là một bức tường.")
    if td.ap_dao > 0.62:
        return ("Ngươi thua. Không nhục nhã, nhưng thua vẫn là thua. "
                "Cơn đau trong lồng ngực sẽ nhắc ngươi điều đó suốt mấy ngày tới.")
    return ("Ngươi thua trong gang tấc. Chỉ một nhịp chậm hơn, chỉ một hơi ngắn hơn. "
            "Loại thất bại này ăn vào xương, và nó dạy nhiều hơn mười lần thắng dễ.")
