"""Kiếp nạn — thứ trời đặt sẵn ở mỗi cửa ải lớn.

Mỗi cảnh giới có một loại khảo nghiệm riêng: rửa tuỷ, ngưng đan, tâm ma, tam tai,
phá hư, hợp đạo, thiên kiếp, và cuối cùng là chín đạo lôi kiếp.
Qua được thì đổi đời. Không qua được thì cũng đổi đời — theo hướng khác.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from .. import config
from ..canhgioi import (KhaoNghiem, canh_gioi, khao_nghiem_cua, mo_ta_dan_pham,
                        ten_dan_pham)


@dataclass
class KetKiep:
    qua: bool
    van: list[str] = field(default_factory=list)
    ton_than: int = 0  # tổn hại thân thể
    ton_tam: int = 0  # tổn hại đạo tâm
    thuong_gio: float = 0.0  # phần của thời gian dưỡng thương tối đa
    tu_vong: bool = False
    dan_pham: int = 0  # chỉ dùng cho ngưng đan
    can_cot_them: float = 0.0
    cong_them: float = 0.0  # cộng vào tỉ lệ đột phá nếu vượt kiếp đẹp


# ─────────────────────── ngân hàng câu ───────────────────────

TAM_MA_CANH = (
    ("Sư phụ ngươi hiện ra, ngồi đúng cái dáng ngày xưa, tay vẫn cầm chén trà mẻ miệng. "
     "Ông nhìn ngươi rất lâu rồi hỏi: *“Con đường này, con đi vì con, hay vì để chứng minh cho ai đó đã chết?”*"),
    ("Ngươi thấy mình đang đứng trong căn nhà cũ. Mẹ ngươi quay lưng lại, đang thổi lửa. "
     "Bà nói, giọng bình thản: *“Về ăn cơm đi con. Tu làm gì cho khổ.”* "
     "Và mùi khói bếp ấy — mùi ấy thật tới mức ngươi suýt quỳ xuống."),
    ("Kẻ ngươi đã giết đứng đó, không oán hận, chỉ hỏi một câu rất khẽ: "
     "*“Ngươi còn nhớ tên ta không?”* Ngươi mở miệng, và ngươi nhận ra là ngươi không nhớ."),
    ("Ngươi thấy chính mình — nhưng là một phiên bản đã thành công. Áo bào, khí tức, kẻ hầu quỳ hai hàng. "
     "Hắn nhìn ngươi bằng ánh mắt người ta nhìn con chó ghẻ, rồi nói: *“Ta đã chọn đúng. Còn ngươi thì chưa.”*"),
    ("Không có gì cả. Chỉ có bóng tối, và trong bóng tối là giọng của chính ngươi, nói đúng những điều "
     "ngươi vẫn nghĩ vào lúc ba giờ sáng: rằng ngươi tầm thường, rằng ngươi đã phí cả đời, "
     "rằng có dừng lại bây giờ cũng chẳng ai để ý."),
    ("Người ngươi thương nhất bước ra, còn nguyên vẹn, còn thở. Nàng — hoặc chàng — chìa tay: "
     "*“Bỏ hết đi. Ta chờ ngươi lâu lắm rồi.”* Và ngươi biết đây là giả. Ngươi biết. Nhưng tay ngươi vẫn nhấc lên."),
)

TAM_MA_THANG = (
    "Ngươi không cãi. Ngươi chỉ nhìn nó, và thừa nhận: đúng, ta sợ điều đó thật. "
    "Tâm ma khựng lại — nó chỉ mạnh khi bị chối bỏ. Hình bóng nhoè ra như mực gặp nước.",
    "Ngươi cắn nát đầu lưỡi. Vị máu tanh kéo ngươi về. Cảnh trong đầu vỡ ra từng mảnh như gương rơi xuống đá.",
    "Ngươi mỉm cười, và nói với nó: *“Ngươi nói đúng. Nhưng ta vẫn đi.”* "
    "Đó không phải là thắng bằng lý lẽ — đó là thắng bằng cách không cần lý lẽ nữa.",
)

TAM_MA_THUA = (
    "Ngươi bước tới. Ngươi biết là giả, và ngươi vẫn bước tới. Khi tỉnh lại, mặt ngươi đầy nước, "
    "và trong lồng ngực có một chỗ trống mới, không lấp được bằng bất cứ đan dược nào.",
    "Ngươi trả lời nó — và ngay khi ngươi mở miệng biện bạch, ngươi đã thua. "
    "Tâm ma không cần thắng cuộc tranh luận, nó chỉ cần ngươi coi nó là đối thủ ngang hàng.",
)

TAM_TAI = (
    ("Phong tai", "Gió tới trước. Không phải gió thổi vào da — gió thổi **xuyên qua** da, "
     "cắt thẳng vào thần hồn. Nguyên anh của ngươi co rúm lại như đứa trẻ trong bão."),
    ("Hoả tai", "Rồi lửa. Lửa không cháy trên người, nó cháy **trong** người, đốt sạch mọi tạp niệm — "
     "kể cả những tạp niệm mà ngươi vẫn tưởng là bản thân mình."),
    ("Lôi tai", "Cuối cùng là sét. Một đạo, thẳng đứng, không báo trước. Nó đánh vào giữa đỉnh đầu "
     "và chạy suốt xuống gót chân, và trong khoảnh khắc ấy ngươi thấy toàn bộ đời mình cùng lúc."),
)

LOI_KIEP_DOT = (
    "Đạo thứ {i}: sét trắng, thẳng và gọn như một nhát chém của kẻ không hề do dự. "
    "Ngươi giơ tay đỡ, và cánh tay ấy tê tới tận vai.",
    "Đạo thứ {i}: sét xanh, đánh xuống rồi tách ra thành trăm nhánh nhỏ bò trên mặt đất tìm ngươi. "
    "Chỗ nào nó bò qua, đá cũng chảy ra thành thuỷ tinh.",
    "Đạo thứ {i}: sét tím, chậm rãi, gần như lười biếng. Nhưng khi nó chạm tới, ngươi nghe rõ tiếng xương sườn mình gãy.",
    "Đạo thứ {i}: sét đỏ, mang theo mùi khét. Nó không đánh vào thân — nó đánh vào **cái tên** của ngươi, "
    "và trong một khắc ngươi quên mất mình là ai.",
    "Đạo thứ {i}: sét đen. Nó không phát sáng. Nó chỉ khiến mọi thứ xung quanh tối đi, và khi ngươi thấy được trở lại "
    "thì đã nằm dưới đất, miệng đầy máu.",
    "Đạo thứ {i}: bầu trời không đánh nữa — nó **đè xuống**. Cả một tầng mây hạ thấp, nghiến lấy vai ngươi. "
    "Ngươi chống hai tay xuống đất, và đất nứt thành hình mạng nhện.",
)

LOI_KIEP_CHIU_DUOC = (
    "Ngươi đứng dậy. Tóc cháy sém, áo không còn, da thịt nứt toác — nhưng ngươi đứng dậy, "
    "và ngẩng mặt lên nhìn thẳng vào đám mây đó.",
    "Máu chảy vào mắt. Ngươi không lau. Ngươi đếm: còn mấy đạo nữa.",
    "Ngươi cười. Không phải vì vui — vì ngươi vừa nhận ra mình vẫn còn thở, và điều đó buồn cười tới mức không nhịn được.",
)


# ─────────────────────── xử lý từng loại kiếp ───────────────────────

def _tay_tuy(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    kq.van.append(
        "Ngươi cởi áo, ngồi vào chậu nước lạnh, và bắt đầu ép. Tạp chất ra theo mồ hôi: "
        "đầu tiên là màu vàng, rồi màu nâu, rồi màu đen như dầu hắc. Nước trong chậu đặc lại và bốc mùi "
        "tới mức con chó hoang ngoài cửa động bỏ chạy."
    )
    diem = rng.random() + (ts.can_cot - 1.0) * 0.4 + (ts.than_the - 70) / 300
    if diem > 0.62:
        kq.can_cot_them = round(rng.uniform(0.05, 0.14), 3)
        kq.cong_them = 0.08
        kq.van.append(
            "Tới canh giờ thứ sáu, ngươi nghe một tiếng 'rắc' rất dài chạy dọc sống lưng — "
            "ấy là **phạt mao tẩy tuỷ** đã tới tận cốt. Khi ngươi bước ra khỏi chậu, "
            "da ngươi hồng hào như trẻ sơ sinh, và ngươi cao hơn trước nửa tấc."
        )
    else:
        kq.ton_than = rng.randint(8, 18)
        kq.van.append(
            "Ngươi ép được phần lớn, nhưng còn sót. Chỗ sót ấy đọng lại trong tuỷ, "
            "và về sau mỗi khi trời trở lạnh, khớp gối ngươi sẽ nhắc lại chuyện hôm nay."
        )
    return kq


def _ngung_dan(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    kq.van.append(
        "Chân khí trong đan điền bắt đầu xoáy. Càng xoáy càng chặt, càng chặt càng nóng. "
        "Ngươi phải giữ nó đúng ở một điểm — lệch một sợi tóc thì đan lệch tâm, "
        "và đan lệch tâm thì cả đời sau này không tròn lại được."
    )
    # phẩm chất kim đan
    diem = rng.gauss(0, 1) * 1.3
    diem += (ts.dao_tam - 60) / 22.0
    diem += (ts.tu_chat - 1.0) * 3.2
    diem += min(2.0, ts.that_bai_lien * 0.35)
    diem += hs.get("tu_luyen", 1.0) - 1.0
    pham = max(1, min(9, int(round(4.2 + diem))))
    kq.dan_pham = pham
    kq.cong_them = 0.03 * pham - 0.06

    if pham <= 2:
        kq.van.append(
            "Sau cùng, khí cũng tụ lại thành một viên. Nhưng khi nó xoay vòng đầu tiên, ngươi nghe tiếng ma sát — "
            "khô, lệch, như bánh xe long trục."
        )
    elif pham <= 5:
        kq.van.append(
            "Viên đan tụ lại và xoay. Đều đặn. Không có gì đặc biệt, cũng không có gì để chê. "
            "Phần lớn tu sĩ trong thiên hạ dừng ở đây, và phần lớn thiên hạ cũng chỉ tới thế."
        )
    else:
        kq.van.append(
            "Khoảnh khắc viên đan thành hình, cả gian động phủ sáng lên một lượt rồi tối lại. "
            "Ngoài kia, mấy con chim đang ngủ trên cành đồng loạt bay lên."
        )
    kq.van.append(f"**{ten_dan_pham(pham).capitalize()} kim đan.** {mo_ta_dan_pham(pham)}")
    kq.van.append(
        "Từ hôm nay, phẩm chất viên đan này sẽ đi theo ngươi tới cuối đường: "
        "nó quyết định ngươi tu nhanh hay chậm, đánh nặng hay nhẹ, và về sau — "
        "khi đứng trước cửa Nguyên Anh — nó quyết định ngươi có được phép gõ cửa hay không."
    )
    return kq


def _tam_ma(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    hong = 0
    for dot in range(kn.so_dot):
        kq.van.append(f"**Ma cảnh thứ {dot + 1}.** " + rng.choice(TAM_MA_CANH))
        nguong = 0.30 + (ts.dao_tam - 60) / 150.0 + hs.get("dao_tam", 1.0) - 1.0
        nguong += 0.05 * ts.so_kiep_da_qua
        if rng.random() < min(0.92, max(0.15, nguong)):
            kq.van.append(rng.choice(TAM_MA_THANG))
        else:
            hong += 1
            kq.van.append(rng.choice(TAM_MA_THUA))
            kq.ton_tam += rng.randint(6, 14)
    if hong == 0:
        kq.cong_them = 0.12
        kq.van.append(
            "Ma cảnh tan hết. Ngươi ngồi đó, mồ hôi lạnh ướt đẫm lưng áo, "
            "nhưng trong lòng sạch sẽ tới mức đáng sợ. Đạo tâm sau kiếp này rắn hơn trước rất nhiều."
        )
    elif hong >= max(2, kn.so_dot - 1):
        kq.qua = False
        kq.ton_than = rng.randint(20, 40)
        kq.thuong_gio = 0.8
        kq.van.append(
            "Ngươi thua. Tâm ma không giết ngươi — nó chỉ ở lại. Từ nay, trong mỗi lần tĩnh toạ, "
            "sẽ có một giọng nói ngồi cùng ngươi, rất kiên nhẫn, đợi tới lần sau."
        )
        if rng.random() < kn.tu_vong:
            kq.tu_vong = True
            kq.van.append(
                "**Và ngươi không ra khỏi ma cảnh nữa.**\n\n"
                "Thân xác vẫn ngồi đó, thở, ấm. Nhưng người trong đó đã đi đâu mất rồi. "
                "Mấy tháng sau, đám đệ tử tìm thấy ngươi vẫn ngồi trong tư thế cũ, "
                "trên mặt là một nụ cười rất hiền — và đó mới là thứ khiến họ sợ."
            )
    else:
        kq.van.append(
            "Ngươi ra khỏi ma cảnh, nhưng không sạch. Có một mảnh của nó bám lại, nhỏ thôi, "
            "như một hạt cát trong giày — chưa đau, nhưng đi lâu thì sẽ đau."
        )
    return kq


def _tam_tai(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    hong = 0
    ho = ts.buff_ho_kiep
    for ten, mo_ta in TAM_TAI:
        kq.van.append(f"**{ten}.** {mo_ta}")
        suc = 0.42 + (ts.than_the - 60) / 260.0 + (ts.dao_tam - 60) / 260.0 + ho
        suc += 0.04 * ts.dan_pham
        if rng.random() < min(0.93, suc):
            kq.van.append(rng.choice(LOI_KIEP_CHIU_DUOC))
            kq.ton_than += rng.randint(6, 14)
        else:
            hong += 1
            kq.ton_than += rng.randint(18, 30)
            kq.van.append(
                f"{ten} xuyên thẳng qua hộ thể linh quang. Ngươi bị hất văng đi, và trong một khoảnh khắc dài "
                "tới mức không đo được, ngươi không còn cảm thấy thân thể mình ở đâu nữa."
            )
    if hong >= 2:
        kq.qua = False
        kq.thuong_gio = 1.0
        kq.van.append(
            "Ba tai qua đi, để lại một kẻ nằm giữa vòng tròn cháy đen. Ngươi còn sống — "
            "nhưng nguyên anh đã rạn, và cửa Hóa Thần vừa khép lại ngay trước mũi ngươi."
        )
        if rng.random() < kn.tu_vong:
            kq.tu_vong = True
            kq.van.append("**Rồi hơi thở cuối cùng cũng tắt.** Tro của ngươi bay lên, hoà vào đúng đám mây vừa giết ngươi.")
    else:
        kq.cong_them = 0.10
        kq.van.append(
            "Ba tai đi qua thân ngươi như ba lưỡi dao gọt một khúc gỗ. Cái còn lại sau khi gọt "
            "mới là thứ trời muốn thấy."
        )
    return kq


def _pha_hu(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    kq.van.append(
        "Ngươi đưa tay ra, nắm lấy một chỗ trống trong không khí, và **kéo**. "
        "Không gian rách ra một đường đen, mép vết rách rung lên như mép một vết thương."
    )
    diem = 0.45 + (ts.dao_tam - 60) / 200.0 + (ts.tu_chat - 1) * 0.4 + ts.buff_ho_kiep
    if rng.random() < min(0.92, diem):
        kq.cong_them = 0.10
        kq.van.append(
            "Ngươi bước qua. Bên kia không có gì cả — không phải bóng tối, mà là **không có gì**, "
            "và ngươi đứng trong cái không có gì ấy đủ lâu để hiểu ra rằng mình cũng chỉ là một thứ tạm bợ. "
            "Rồi ngươi quay lại. Ngươi vẫn nhớ tên mình. Đó là toàn bộ điều kiện để qua ải này."
        )
    else:
        kq.qua = False
        kq.ton_tam = rng.randint(10, 22)
        kq.ton_than = rng.randint(15, 30)
        kq.thuong_gio = 0.7
        kq.van.append(
            "Ngươi bước qua, và bên kia có thứ gì đó **nhìn lại**. Ngươi rút tay về, đóng vết rách, "
            "và ngồi thở suốt ba ngày. Có mấy đoạn ký ức từ hôm ấy ngươi không tìm lại được nữa."
        )
    return kq


def _hop_dao(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    kq = KetKiep(qua=True)
    kq.van.append(kn.mo_ta)
    for i in range(kn.so_dot):
        kq.van.append(
            ["Thần hồn nói: *“Bỏ cái xác đi, nó chỉ làm ta chậm lại.”* "
             "Nhục thân đáp lại bằng một cơn đau chạy dọc xương sống.",
             "Hai thứ ấy giằng nhau trong người ngươi suốt bảy ngày. Ngươi không ăn, không ngủ, "
             "và thi thoảng lại nói chuyện một mình bằng hai giọng khác nhau."][i % 2]
        )
    diem = 0.44 + (ts.dao_tam - 60) / 180.0 + (ts.can_cot - 1) * 0.5 + ts.buff_ho_kiep
    if rng.random() < min(0.9, diem):
        kq.cong_them = 0.12
        kq.van.append(
            "Cuối cùng ngươi không phân xử nữa — ngươi **bắt cả hai im lặng**. Và trong sự im lặng đó, "
            "chúng tự chảy vào nhau. Khi ngươi mở mắt, ngươi không còn phân biệt được đâu là hồn, đâu là xác."
        )
    else:
        kq.qua = False
        kq.ton_than = rng.randint(20, 36)
        kq.ton_tam = rng.randint(8, 16)
        kq.thuong_gio = 0.85
        kq.van.append(
            "Chúng không chịu hoà. Ngươi ép, và cái ép ấy làm nứt cả hai. "
            "Ngươi tỉnh lại với cảm giác lạ lùng rằng thân thể này không hoàn toàn thuộc về mình nữa."
        )
    return kq


def _thien_kiep(rng: random.Random, ts, hs: dict, kn: KhaoNghiem, so_dot: int | None = None,
                nhan: str = "") -> KetKiep:
    kq = KetKiep(qua=True)
    if kn.mo_ta:
        kq.van.append(kn.mo_ta)
    dot = so_dot or kn.so_dot
    ho = ts.buff_ho_kiep
    hong = 0
    for i in range(1, dot + 1):
        mau = LOI_KIEP_DOT[min(len(LOI_KIEP_DOT) - 1, (i - 1) * len(LOI_KIEP_DOT) // max(1, dot))]
        kq.van.append(mau.format(i=i))
        suc = 0.52 + (ts.than_the - 60) / 300.0 + (ts.dao_tam - 60) / 320.0 + ho
        suc += 0.035 * ts.dan_pham + 0.02 * ts.so_kiep_da_qua
        suc -= 0.045 * (i - 1)  # mỗi đạo một nặng hơn
        if rng.random() < min(0.95, max(0.08, suc)):
            if i % 2 == 1 or i == dot:
                kq.van.append(rng.choice(LOI_KIEP_CHIU_DUOC))
            kq.ton_than += rng.randint(5, 12)
        else:
            hong += 1
            kq.ton_than += rng.randint(16, 28)
            kq.van.append(
                "Hộ thể linh quang vỡ như vỏ trứng. Đạo sét ấy đi thẳng vào thân, "
                "và ngươi nghe thấy tiếng thịt mình cháy trước khi thấy đau."
            )
            if hong >= 3:
                break
    if hong >= 3:
        kq.qua = False
        kq.thuong_gio = 1.0
        kq.van.append(
            "Ngươi không đứng dậy nổi nữa. Đám mây trên đầu tản đi rất chậm, như một kẻ bỏ đi "
            "sau khi đã nói xong điều cần nói."
        )
        if rng.random() < kn.tu_vong:
            kq.tu_vong = True
            kq.van.append(
                "**Và đó là đạo sét cuối cùng ngươi thấy.**\n\n"
                "Chỗ ngươi đứng chỉ còn một hố cháy tròn vành vạnh, đáy hố phẳng như gương. "
                "Trăm năm sau, người ta vẫn gọi chỗ ấy bằng tên ngươi — mà không ai còn nhớ ngươi từng làm gì."
            )
    else:
        kq.cong_them = 0.08 + 0.02 * dot
        kq.van.append(
            "Đạo cuối cùng tan đi. Bầu trời sáng trở lại, sạch sẽ, vô tội, như thể vừa rồi chẳng có chuyện gì. "
            "Ngươi đứng giữa vòng đất cháy, toàn thân không còn một mảnh áo lành, và ngươi vẫn đứng."
        )
    return kq


def _phi_thang(rng: random.Random, ts, hs: dict, kn: KhaoNghiem) -> KetKiep:
    """Cửu Trọng Đại Kiếp — cửa cuối. Qua được thì không còn là người nữa."""
    kq = _thien_kiep(rng, ts, hs, kn, so_dot=9)
    if not kq.qua:
        kq.van.append(
            "Thiên môn không mở. Nó chưa từng mở cho ai vội vàng. "
            "Ngươi nằm giữa vùng đất cháy, nhìn đám mây tản dần, và hiểu ra rằng mình sẽ phải sống thêm "
            "vài trăm năm nữa chỉ để làm lại đúng cái đêm hôm nay."
        )
        return kq
    kq.van.append(
        "Sau đạo thứ chín, trời im lặng rất lâu. Rồi trên đỉnh đầu ngươi, mây tách ra làm hai, "
        "và phía sau đám mây không phải là bầu trời — mà là một khoảng sáng có bậc thang."
    )
    kq.van.append(
        "Ngươi ngoảnh lại nhìn nhân gian một lần cuối: ngọn núi ngươi từng nhặt củi, con đường ngươi từng "
        "chạy trốn, mấy nấm mộ ngươi đã đắp bằng chính hai tay này. Tất cả nhỏ đi, nhỏ đi, "
        "cho tới khi chỉ còn là một vết mực trên tờ giấy."
    )
    kq.van.append(
        "Rồi ngươi bước lên. Không có nhạc trời, không có tiên nữ rải hoa — mấy thứ ấy là chuyện người đời bịa ra "
        "để tự an ủi. Chỉ có tiếng bước chân ngươi trên bậc thang, đều đặn, và một cảm giác rất lạ: "
        "**nhẹ**. Lần đầu tiên kể từ ngày nhập đạo, ngươi thấy nhẹ."
    )
    kq.can_cot_them = 0.2
    return kq


# ─────────────────────── cửa vào ───────────────────────

async def vuot_kiep(kho, ts, rng: random.Random, hs: dict, canh_gioi_dich: int) -> KetKiep:
    """Chạy khảo nghiệm tương ứng với cảnh giới sắp bước vào."""
    kn = khao_nghiem_cua(canh_gioi_dich)
    if kn is None:
        return KetKiep(qua=True)

    bo = {
        "tay_tuy": _tay_tuy, "ngung_dan": _ngung_dan, "tam_ma": _tam_ma,
        "tam_tai": _tam_tai, "pha_hu": _pha_hu, "hop_dao": _hop_dao,
        "thien_kiep": _thien_kiep, "phi_thang": _phi_thang,
    }
    ham = bo.get(kn.loai, _thien_kiep)
    kq = ham(rng, ts, hs, kn)
    kq.van.insert(0, f"**{kn.ten}.** {kn.dieu_bao}")
    if ts.buff_ho_kiep > 0:
        kq.van.insert(1, (
            "Dược lực trong người ngươi dâng lên đúng lúc — lớp ánh kim mỏng phủ kín da thịt. "
            "Đan dược hộ thể không cứu được mạng ngươi, nhưng nó mua thêm cho ngươi vài nhịp thở, "
            "và ở chỗ này, vài nhịp thở là tất cả."
        ))
    ts.so_kiep_da_qua += 1
    return kq


async def do_loi_kiep_tang(kho, ts, rng: random.Random, hs: dict, trong: int) -> KetKiep:
    """Trong cảnh giới Độ Kiếp, mỗi lần lên một tầng là một trọng lôi kiếp."""
    gia = KhaoNghiem(
        ma=f"loi_kiep_{trong}", ten=f"Lôi kiếp trọng thứ {trong}", loai="thien_kiep",
        dieu_bao=("Đám mây trên đầu ngươi — cái đám mây đã không tan suốt bao năm nay — "
                  "bắt đầu xoáy. Nó nhớ ngươi."),
        mo_ta="", so_dot=max(1, min(4, 1 + trong // 3)),
        tu_vong=0.05 + 0.035 * trong,
    )
    kq = _thien_kiep(rng, ts, hs, gia)
    kq.van.insert(0, f"**{gia.ten}.** {gia.dieu_bao}")
    ts.so_kiep_da_qua += 1
    return kq


def ap_dung(ts, kq: KetKiep) -> None:
    """Ghi hậu quả của kiếp nạn lên thân người."""
    if kq.ton_than:
        ts.than_the = max(1, ts.than_the - kq.ton_than)
    if kq.ton_tam:
        ts.dao_tam = max(3, ts.dao_tam - kq.ton_tam)
    if kq.can_cot_them:
        ts.can_cot = round(ts.can_cot + kq.can_cot_them, 3)
    if kq.dan_pham:
        ts.dan_pham = kq.dan_pham
    if kq.thuong_gio:
        ts.thuong_toi = int(time.time()) + int(config.DUONG_THUONG_TOI_DA * kq.thuong_gio)
    if kq.tu_vong:
        ts.da_chet = 1
    ts.buff_ho_kiep = 0.0
