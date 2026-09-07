"""Tu luyện: ngồi xuống, thở, và đổi từng ngày của đời mình lấy từng phân đạo hạnh."""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import (BANG_CANH_GIOI, TOI_DA, canh_gioi, he_so_dan_pham,
                        khoa_tieu_canh, la_dinh_canh, mo_ta_tang, ten_canh_gioi,
                        tu_vi_can_thiet)
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..vanphong import KET_TU_LUYEN, MO_DAU_TU_LUYEN, khac_gio, mo_ta_dao_hanh
from .ketqua import KetQua
from . import kiepnan
from .thienco import thanh_bai, van_khi

# ───────────────────────── luyện tập thường ─────────────────────────

CAM_NGO_VUN = (
    "Giữa lúc chân khí chạy qua Đản Trung huyệt, ngươi chợt nhớ tới một câu sư phụ chưa từng nói hết. "
    "Câu ấy hôm nay tự nó nói nốt phần còn lại.",
    "Có một khoảnh khắc rất ngắn, ngươi quên mất mình đang ngồi ở đâu. Khi tỉnh lại, chân khí đã đi thêm được nửa vòng.",
    "Ngoài cửa động, một giọt nước rơi xuống mặt đá. Ngươi nghe thấy nó, và trong tiếng ấy có một đạo lý mà chữ nghĩa không chép được.",
    "Ngươi bỗng hiểu vì sao lão tiền bối kia bảo 'chậm mới là nhanh'. Hiểu xong thì thấy mấy năm vừa rồi mình phí hoài.",
)

TRUC_TRAC = (
    "Chân khí đi tới Đốc mạch thì vấp. Ngươi phải lùi lại, dẫn lại từ đầu, mất toi nửa canh giờ.",
    "Tạp niệm nổi lên: một khuôn mặt cũ, một lời hứa chưa giữ. Ngươi đè nó xuống, nhưng đè thì tốn sức.",
    "Trong người có chỗ nghẽn. Càng ép, càng đau. Cuối cùng ngươi đành thu công sớm.",
)


async def luyen_tap(kho, ts, rng: random.Random | None = None, he_so_the_gioi: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = he_so_the_gioi or {}
    con = await kho.con_cho(ts.user_id, "luyentap")
    if con > 0:
        return KetQua(
            tieu_de="Chưa tới lúc",
            van=[f"Khí huyết vừa mới lắng, kinh mạch còn ê ẩm. Đợi thêm {khac_gio(con)} nữa rồi hẵng ngồi xuống. "
                 "Vội trên đường tu là cách chết chậm mà chắc."],
            thanh_cong=False,
        )
    if ts.dang_bi_thuong:
        return KetQua(
            tieu_de="Thương thế chưa lành",
            van=[f"Vừa nhắm mắt vận công, chỗ nội thương đã nhói lên như có ai cắm kim. "
                 f"Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa mới nên động tới chân khí. "
                 "Có thể dùng đan dược trị thương nếu ngươi không muốn nằm chờ."],
            thanh_cong=False,
        )

    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    hs_mp = mp.he_so_tu_luyen if mp else 1.0
    vk = van_khi(rng, ts.dao_tam, ts.danh_vong)
    can = tu_vi_can_thiet(ts.canh_gioi, ts.tang)
    thu = can * 0.10 * ts.tu_chat * hs_mp * vk * hs.get("tu_luyen", 1.0)

    kq = KetQua(tieu_de="Toạ quan", mau=config.MAU_LINH, anh=canh_gioi(ts.canh_gioi).tranh or None)
    kq.them(rng.choice(MO_DAU_TU_LUYEN))

    if mp:
        kq.them(
            f"Ngươi vận **{mp.cong_phap}**. Khẩu quyết chạy trong đầu như nước chảy trong máng đá cũ — "
            "đã thuộc tới mức không cần nghĩ, mà vẫn phải nghĩ."
        )
    else:
        kq.them(
            "Ngươi không có công pháp chính thống, chỉ có mấy câu khẩu quyết chắp vá nghe lỏm được. "
            "Chân khí đi trong người như nước chảy trên đất phẳng — chậm, tản, và phí."
        )

    if vk > 1.18 and rng.random() < 0.5:
        kq.them(rng.choice(CAM_NGO_VUN))
        thu *= 1.35
    elif vk < 0.82:
        kq.them(rng.choice(TRUC_TRAC))
        thu *= 0.6

    if hs.get("tu_luyen", 1.0) > 1.3:
        kq.them("Hôm nay linh khí trong trời đất dày lạ thường. Hít một hơi mà ngực đầy tới mức phải nén lại.")
    elif hs.get("tu_luyen", 1.0) < 0.85:
        kq.them("Linh khí quanh vùng nhạt như nước lã. Ngươi vét mãi cũng chỉ được chừng ấy.")

    ts.tu_vi += max(1, int(thu))
    ts.than_the = min(100, ts.than_the + 2)
    kq.them(rng.choice(KET_TU_LUYEN))
    kq.them(mo_ta_dao_hanh(ts.canh_gioi, ts.tang, ts.tu_vi))

    if ts.tu_vi >= can:
        kq.them(
            "**Cửa ải trước mặt đã mở hé.** Chân khí trong đan điền chật chội tới mức đau, "
            "cứ chực dâng lên đỉnh đầu. Nếu ngươi thấy mình đã sẵn sàng — *hãy đột phá*. "
            "Nếu chưa, thì cứ nén thêm ít lâu; nén càng lâu, đế càng vững, nhưng nén quá thì kinh mạch chịu không nổi."
        )
        kq.du_lieu["san_sang_dot_pha"] = True

    await kho.dat_cho(ts.user_id, "luyentap", config.NGUOI_LANH["luyentap"])
    await kho.luu(ts)
    return kq


# ───────────────────────── hấp thu thiên địa ─────────────────────────

HOA_THIEN_NHIEN = (
    ("ma_nhiem",
     "Giữa lúc linh khí ồ ạt tràn vào, có một luồng khí lạnh lẫn theo. Nó không giống linh khí — "
     "nó có ý thức. Nó tìm đường vào thần hồn ngươi, và ngươi phải cắn lưỡi để giữ mình tỉnh táo.",
     ),
    ("tau_hoa",
     "Ngươi tham. Ngươi biết là mình tham ngay lúc đang tham. Chân khí vào quá nhanh, kinh mạch phồng lên, "
     "và có chỗ đã rách.",
     ),
    ("ky_si",
     "Ngươi đang hút linh khí thì cả một vùng bỗng loãng đi — có kẻ khác đang hút cùng. "
     "Tiếng vó ngựa vọng tới. Có người không thích chia phần.",
     ),
)


async def hap_thu_thien_dia(kho, ts, rng: random.Random | None = None, he_so_the_gioi: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = he_so_the_gioi or {}
    con = await kho.con_cho(ts.user_id, "thiennhien")
    if con > 0:
        return KetQua(
            tieu_de="Thiên địa chưa mở lòng",
            van=[f"Linh mạch nơi này vừa bị ngươi vét một lần, còn chưa tụ lại. "
                 f"Ít nhất {khac_gio(con)} nữa mới nên thử lần nữa."],
            thanh_cong=False,
        )
    if ts.dang_bi_thuong:
        return KetQua(
            tieu_de="Thân này chưa chịu nổi",
            van=["Với thương thế thế này mà cưỡng ép hấp thu thiên địa linh khí thì chẳng khác gì "
                 "rót nước sôi vào chén nứt. Dưỡng thương trước đã."],
            thanh_cong=False,
        )

    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    vk = van_khi(rng, ts.dao_tam, ts.danh_vong)
    can = tu_vi_can_thiet(ts.canh_gioi, ts.tang)
    thu = can * 0.26 * ts.tu_chat * (mp.he_so_tu_luyen if mp else 1.0) * vk * hs.get("tu_luyen", 1.0)

    kq = KetQua(tieu_de="Dẫn thiên địa nhập thể", mau=config.MAU_LINH, anh="bia_tien_do.png")
    kq.them(
        "Ngươi leo lên chỗ cao nhất có thể leo, chọn giờ Tý, mở toàn bộ khiếu huyệt trên người ra. "
        "Đây không phải cách tu hành mà tông môn nào cũng cho phép: nó nhanh, và nó tham."
    )
    kq.them(
        "Linh khí từ bốn phương tám hướng đổ về, xoáy quanh ngươi thành một cột mờ. "
        "Cỏ dưới chân khô lại. Một con chim bay ngang bị hút lệch đường, đập cánh loạn xạ rồi rơi."
    )

    nguy = 0.30 * hs.get("nguy_hiem", 1.0) * (1.15 if ts.dao_tam < 50 else 1.0)
    gap_dich = None
    if rng.random() < nguy:
        loai, mo_ta = rng.choice(HOA_THIEN_NHIEN)
        kq.them(mo_ta)
        if loai == "ma_nhiem":
            ts.dao_tam = max(5, ts.dao_tam - rng.randint(4, 9))
            thu *= 1.1
            kq.them(
                "Ngươi đẩy được nó ra, nhưng nó để lại một vết. Từ nay trong lúc tĩnh toạ, "
                "thi thoảng ngươi sẽ nghe thấy tiếng ai đó thở ngay sau gáy mình."
            )
        elif loai == "tau_hoa":
            thu *= 0.45
            ton = rng.randint(18, 34)
            ts.than_the = max(5, ts.than_the - ton)
            ts.thuong_toi = int(time.time()) + int(config.DUONG_THUONG_TOI_DA * 0.45)
            kq.them(
                "Ngươi ộc ra một ngụm máu đen, đổ nghiêng người xuống nền đá. "
                "Cột linh khí tan đi, để lại một vùng đất trơ trụi và một kẻ nằm thở dốc giữa đó."
            )
        else:
            gap_dich = "ky_si_vo_danh"
            kq.du_lieu["gap_dich"] = gap_dich
            kq.them(
                "Ngươi thu công vội, đứng dậy quay mặt về phía tiếng vó. Bụi cuốn lên ở cuối con dốc. "
                "*Kẻ đó đang tới — nếu ngươi muốn, có thể nghênh chiến.*"
            )
            thu *= 0.7
    else:
        kq.them(
            "Suốt ba canh giờ, ngươi là một cái miệng há ra giữa trời đất. "
            "Khi thu công, đầu ngón tay ngươi run lên vì no."
        )

    ts.tu_vi += max(1, int(thu))
    kq.them(mo_ta_dao_hanh(ts.canh_gioi, ts.tang, ts.tu_vi))
    if ts.tu_vi >= can:
        kq.them("**Đan điền đã đầy tới miệng.** Cửa ải đang đợi, và nó không đợi mãi.")
        kq.du_lieu["san_sang_dot_pha"] = True

    await kho.dat_cho(ts.user_id, "thiennhien", config.NGUOI_LANH["thiennhien"])
    await kho.luu(ts)
    return kq


# ───────────────────────── đột phá ─────────────────────────

DOT_PHA_CANH_GIOI_MO_TA: dict[int, str] = {
    1: ("Kinh mạch trong người ngươi bị chân khí đâm rách rồi tự nối lại, rách rồi lại nối, "
        "chín lần như thế. Đến lần thứ chín thì ngươi không còn thấy đau nữa — không phải vì hết đau, "
        "mà vì cái thân này đã không còn hoàn toàn là thân phàm.\n\n"
        "Tạp chất trong xương tuỷ theo mồ hôi mà ra, đen như dầu hắc, tanh không chịu nổi. "
        "Khi ngươi mở mắt, ngươi nhìn thấy bụi trong không khí — từng hạt một, đang trôi rất chậm."),
    2: ("Chân khí trong đan điền xoay tròn, càng lúc càng đặc, đặc tới mức nó không còn là khí nữa. "
        "Nó co lại. Nó nén xuống. Và trong một khoảnh khắc mà ngươi tưởng tim mình đã ngừng đập, "
        "nó kết thành một viên đan.\n\n"
        "Viên đan ấy xoay một vòng. Ngươi nghe được tiếng nó — như tiếng một quả chuông rất nhỏ "
        "đánh lên trong lồng ngực mình. Từ hôm nay, ngươi không cần ăn cơm nữa. "
        "Từ hôm nay, ngươi có thể bay."),
    3: ("Kim đan nứt. Ngươi từng nghe nói khoảnh khắc này giống như tự tay đập vỡ thứ mình dành trăm năm để tạo ra — "
        "nghe thì hiểu, làm thì khác.\n\n"
        "Từ trong mảnh vỡ, một anh nhi bé bằng nắm tay ngồi dậy. Nó mở mắt. "
        "Nó có khuôn mặt của ngươi, nhưng bình thản hơn ngươi rất nhiều. "
        "Ngươi nhìn nó, và lần đầu tiên ngươi hiểu: cái thân xác này, từ nay chỉ là một bộ áo."),
    4: ("Nguyên anh rời khỏi thân, đứng giữa hư không, ngẩng đầu nhìn trời. "
        "Thần niệm ngươi trải rộng ra ngoài trăm dặm, rồi ngàn dặm, và ngươi 'thấy' được những thứ "
        "mắt không nhìn được: hơi ấm của một con thú đang ngủ dưới đất, "
        "một hạt mưa chưa rơi, một ý nghĩ ác vừa nảy trong đầu kẻ nào đó rất xa.\n\n"
        "Ngươi thu thần niệm về, và thấy mệt. Không phải mệt thân — mệt vì biết quá nhiều."),
}

DOT_PHA_THAT_BAI_NHE = (
    "Tới bước cuối cùng, chân khí trào ngược. Ngươi cắn răng ép nó xuống, và cửa ải khép lại trước mặt ngươi "
    "như một cánh cửa đá. Không mất gì nhiều, ngoài một cơ hội.",
    "Chỉ còn nửa bước. Nửa bước ấy, ngươi hụt hơi. Chân khí tán đi hơn phân nửa, "
    "và ngươi ngồi đó rất lâu, không nhúc nhích, cũng không muốn nhúc nhích.",
)
DOT_PHA_THAT_BAI_NANG = (
    "Chân khí nổ tung trong kinh mạch. Ngươi ộc máu, người bật ngửa ra sau, đầu đập vào vách đá. "
    "Trong lỗ tai chỉ còn tiếng ù ù, và một vị mặn dâng lên cổ họng, mãi không dứt.",
    "Cửa ải phản phệ. Chân khí như trăm mũi kim đâm ngược từ trong ra, "
    "và ngươi nghe rõ tiếng một sợi kinh mạch nào đó đứt hẳn. Sau lần này, con đường trước mặt sẽ khó hơn.",
)
DOT_PHA_TAU_HOA = (
    "Tâm ma tới đúng lúc yếu nhất. Nó mang khuôn mặt của người ngươi từng phụ, "
    "và nó nói bằng giọng của chính ngươi. Ngươi tỉnh lại sau ba ngày, "
    "trong tay đang nắm chặt một nắm tóc mình vừa bứt ra, và không nhớ vì sao.",
)


def _ti_le_dot_pha(ts, len_canh_gioi: bool, ho_tro_dan: float, hs: dict) -> float:
    goc = 0.72 - 0.045 * ts.canh_gioi
    if len_canh_gioi:
        goc = 0.34 - 0.030 * ts.canh_gioi
    goc += (ts.dao_tam - 60) / 420.0
    goc += min(0.12, ts.that_bai_lien * 0.045)  # thất bại tích thành cảm ngộ
    goc += ho_tro_dan
    goc += ts.buff_pha_chuong
    if ts.canh_gioi >= 2 and ts.dan_pham:
        # viên kim đan năm xưa còn nói chuyện với ngươi ở mọi cửa ải về sau
        goc += (ts.dan_pham - 4) * 0.013
    goc *= 0.9 + 0.2 * (ts.than_the / 100.0)
    goc *= hs.get("dao_tam", 1.0)
    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    if mp and mp.ma in ("vong_hai", "thanh_van"):
        goc += 0.05
    if mp and mp.ma == "u_minh":
        goc -= 0.04
    return max(0.05, min(0.94, goc))


async def dot_pha(kho, ts, rng: random.Random | None = None, he_so_the_gioi: dict | None = None,
                  dung_dan: str | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = he_so_the_gioi or {}
    can = tu_vi_can_thiet(ts.canh_gioi, ts.tang)
    if ts.tu_vi < can:
        return KetQua(
            tieu_de="Chưa tới lúc",
            van=["Đan điền còn chỗ trống, chân khí chưa chật. Cưỡng ép xung quan bây giờ "
                 "chỉ là đem mạng ra đùa. " + mo_ta_dao_hanh(ts.canh_gioi, ts.tang, ts.tu_vi)],
            thanh_cong=False,
        )
    if ts.dang_bi_thuong:
        return KetQua(
            tieu_de="Thân thể chưa lành",
            van=["Xung quan với một thân thương thế là chuyện của kẻ tìm chết. "
                 f"Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa."],
            thanh_cong=False,
        )

    len_canh_gioi = la_dinh_canh(ts.canh_gioi, ts.tang)
    if len_canh_gioi and ts.canh_gioi >= TOI_DA:
        return KetQua(
            tieu_de="Đường đã tận",
            van=["Trên đầu ngươi không còn bậc nào nữa. Cái còn lại không phải là tu, mà là sống — "
                 "và xem thử một kẻ như ngươi sẽ làm gì với một khoảng thời gian dài đến thế."],
            thanh_cong=False,
        )

    # đan dược hỗ trợ
    ho_tro = 0.0
    ten_dan = ""
    if dung_dan:
        vp = vatpham.lay(dung_dan)
        if vp and "dot_pha" in vp.hieu_qua:
            chi_dung = vp.hieu_qua.get("chi_dung_cho")
            if chi_dung is not None and chi_dung != ts.canh_gioi:
                return KetQua(
                    tieu_de="Đan này không hợp",
                    van=[f"{vp.ten} không dành cho kẻ đứng ở bậc của ngươi. Nuốt vào chỉ tổ phí, "
                         "mà phí đan dược là tội mà đan sư nào cũng nguyền rủa."],
                    thanh_cong=False,
                )
            if not await kho.bot_vat(ts.user_id, dung_dan, 1):
                return KetQua(tieu_de="Không có", van=[f"Ngươi lục khắp túi càn khôn mà không tìm ra {vp.ten}."],
                              thanh_cong=False)
            ho_tro = float(vp.hieu_qua["dot_pha"])
            ten_dan = vp.ten

    ti_le = _ti_le_dot_pha(ts, len_canh_gioi, ho_tro, hs)
    ts.so_lan_dot_pha += 1
    dung_pha_chuong = ts.buff_pha_chuong > 0

    kq = KetQua(tieu_de="Xung quan", mau=config.MAU_KIM)
    kq.them(
        "Ngươi chọn một nơi không ai tìm ra, bày trận, cắm bốn ngọn nến, "
        "và ngồi xuống với ý nghĩ rất rõ ràng rằng mình có thể không đứng dậy được nữa."
    )
    if dung_pha_chuong:
        kq.them(
            "Chỗ bế tắc trong kinh mạch ngươi đã bị đục thủng từ trước bằng dược lực — "
            "con đường hôm nay ít nhất cũng đỡ gập ghềnh hơn mọi khi."
        )
    if ten_dan:
        kq.them(f"Ngươi nuốt {ten_dan}. Một luồng nóng chạy thẳng xuống đan điền, và mọi thứ trong người bắt đầu sôi.")
    if len_canh_gioi:
        cg_moi = canh_gioi(ts.canh_gioi + 1)
        kq.them(
            f"Đây không phải một tầng nữa. Đây là **{canh_gioi(ts.canh_gioi).ten} → {cg_moi.ten}** — "
            "một cái ngưỡng mà trong mười người bước tới, chín người quay đầu, "
            "và trong chín người quay đầu ấy có mấy kẻ đã kịp gãy lưng."
        )

    # ── kiếp nạn: cửa ải lớn nào cũng có người gác cửa ──
    kk = None
    if len_canh_gioi:
        kk = await kiepnan.vuot_kiep(kho, ts, rng, hs, ts.canh_gioi + 1)
    elif ts.canh_gioi == 8:  # Độ Kiếp: mỗi trọng một lần lôi kiếp
        kk = await kiepnan.do_loi_kiep_tang(kho, ts, rng, hs, ts.tang)
    if kk is not None:
        for dong in kk.van:
            kq.them(dong)
        if kk.dan_pham:
            kq.anh = "kim_dan.png"
        elif ts.canh_gioi >= 7:
            kq.anh = "do_kiep.png"
        ti_le = min(0.96, ti_le + kk.cong_them)
        if kk.qua and kk.chac_chan:
            ti_le = 1.0  # vượt được cửa này tức là đã qua bậc
        kiepnan.ap_dung(ts, kk)
        ts.buff_pha_chuong = 0.0
        if not kk.qua:
            ts.that_bai_lien += 1
            ts.tu_vi = int(ts.tu_vi * 0.45)
            kq.tieu_de = "Kiếp nạn chưa qua"
            kq.mau = config.MAU_HUYET
            kq.thanh_cong = False
            kq.them(
                "Cửa ải này không mở cho ngươi hôm nay. Ngươi lết về, nằm xuống, "
                "và trong lúc thiêm thiếp còn nghe tiếng gió ngoài kia — nghe như tiếng ai đó đang chờ."
            )
            if ts.da_chet:
                kq.du_lieu["tu_vong"] = True
            await kho.chep(ts.user_id, "kiep_nan", f"Kiếp nạn thất bại trước cửa {canh_gioi(ts.canh_gioi + 1).ten}.")
            await kho.luu(ts)
            return kq

    if thanh_bai(rng, ti_le):
        ts.that_bai_lien = 0
        du = ts.tu_vi - can
        if len_canh_gioi:
            ts.canh_gioi += 1
            ts.tang = 1
            ts.tu_vi = int(du * 0.25)
            cg = canh_gioi(ts.canh_gioi)
            kq.tieu_de = f"Đột phá — {cg.ten}"
            kq.anh = cg.tranh or "bia_tien_do.png"
            kq.them(DOT_PHA_CANH_GIOI_MO_TA.get(
                ts.canh_gioi,
                f"Ngươi bước qua ngưỡng. Thiên địa trong mắt ngươi đổi màu một lần nữa, "
                f"và lần này ngươi không còn tìm được chữ nào để tả nó."))
            kq.them(f"**{cg.ten}.** {cg.than_the.capitalize()}.")
            kq.them(cg.cam_ngo.capitalize() + ".")
            kq.them(
                f"Người ngoài nhìn ngươi từ nay sẽ thấy: {cg.khi_the}. "
                f"Trong nhân gian, {cg.the_gioi}."
            )
            ts.danh_vong += 20 * ts.canh_gioi
            ts.than_the = max(30, ts.than_the - 12)
        else:
            ts.tang += 1
            ts.tu_vi = int(du * 0.35)
            kq.tieu_de = "Thăng một tầng"
            kq.them(
                "Chân khí đâm thủng chỗ bế tắc. Một tiếng 'bựt' rất khẽ vang lên trong người ngươi — "
                "khẽ tới mức chỉ mình ngươi nghe thấy, nhưng nó đủ lớn để đổi cả một quãng đời."
            )
            kq.them(mo_ta_tang(ts.canh_gioi, ts.tang))
            kq.them(
                f"Ngươi đã đứng vững ở **{ten_canh_gioi(ts.canh_gioi, ts.tang)}**. "
                "Không có tiếng vỗ tay nào cả. Chỉ có ngọn nến đã cháy hết, và một cơn đói cồn cào."
            )
            ts.danh_vong += 3
        kq.du_lieu["thanh_cong"] = True
        await kho.chep(ts.user_id, "dot_pha",
                       f"Đột phá thành công, nay là {ten_canh_gioi(ts.canh_gioi, ts.tang)}.")
    else:
        ts.that_bai_lien += 1
        kq.tieu_de = "Xung quan thất bại"
        kq.mau = config.MAU_HUYET
        muc = rng.random()
        mat = 0.0
        if muc < 0.45:
            kq.them(rng.choice(DOT_PHA_THAT_BAI_NHE))
            mat = 0.35
            ts.than_the = max(10, ts.than_the - rng.randint(5, 12))
        elif muc < 0.85:
            kq.them(rng.choice(DOT_PHA_THAT_BAI_NANG))
            mat = 0.6
            ts.than_the = max(5, ts.than_the - rng.randint(22, 40))
            ts.thuong_toi = int(time.time()) + int(config.DUONG_THUONG_TOI_DA * rng.uniform(0.5, 1.0))
        else:
            kq.them(rng.choice(DOT_PHA_TAU_HOA))
            mat = 0.75
            ts.dao_tam = max(3, ts.dao_tam - rng.randint(10, 20))
            ts.than_the = max(3, ts.than_the - rng.randint(30, 50))
            ts.thuong_toi = int(time.time()) + config.DUONG_THUONG_TOI_DA
            if ts.canh_gioi >= 7 and rng.random() < 0.18:
                ts.da_chet = 1
                kq.them(
                    "**Và rồi ngươi không tỉnh lại nữa.**\n\n"
                    "Người ta tìm thấy ngươi bảy ngày sau, vẫn ngồi trong tư thế cũ, thân thể đã hoá tro, "
                    "chỉ còn lại vết cháy hình một người ngồi in trên nền đá. "
                    "Đường tu là thế: đi được bao xa thì đi, ngã ở đâu thì nằm lại đó."
                )
        ts.tu_vi = int(ts.tu_vi * (1 - mat))
        kq.them(
            "Ngươi thất bại. Cửa ải vẫn ở đó, không đi đâu cả — nhưng lần sau nó sẽ nhìn ngươi bằng con mắt khác. "
            + ("Cái đau này, giữ lấy. Nó là thứ duy nhất ngươi thu được hôm nay." if ts.that_bai_lien < 3
               else "Đã mấy lần rồi. Trong lòng ngươi bắt đầu có một câu hỏi mà ngươi không dám hỏi thành lời.")
        )
        await kho.chep(ts.user_id, "dot_pha", "Xung quan thất bại.")

    ts.buff_pha_chuong = 0.0
    await kho.luu(ts)
    return kq
