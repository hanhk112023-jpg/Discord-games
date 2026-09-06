"""Phiêu lưu: bước ra khỏi cửa động, và để trời quyết định phần còn lại."""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import ten_canh_gioi
from ..data import congthuc as dl_congthuc
from ..data import diadanh as dl_diadanh
from ..data import dichthu as dl_dichthu
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..vanphong import khac_gio
from . import chiendau
from .ketqua import KetQua
from .thienco import roi_do, van_khi

# ───────────────────────── dựng bên tham chiến ─────────────────────────

def ben_tu_nguoi_choi(ts) -> chiendau.BenThamChien:
    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    return chiendau.BenThamChien(
        ten=ts.ten,
        canh_gioi=ts.canh_gioi,
        tang=ts.tang,
        phap_bao=ts.phap_bao,
        he_so_chien=(mp.he_so_chien if mp else 1.0),
        can_cot=ts.can_cot,
        dao_tam=ts.dao_tam,
        than_the=ts.than_the,
        la_nguoi_choi=True,
        cong_phap=(mp.cong_phap if mp else ""),
    )


def ben_tu_dich(d) -> chiendau.BenThamChien:
    return chiendau.BenThamChien(
        ten=d.ten,
        canh_gioi=d.canh_gioi,
        tang=d.tang,
        he_so_chien=1.0 * d.tho,
        can_cot=1.0,
        dao_tam=60,
        than_the=100,
        thu_doan=d.thu_doan,
        hung_hang=d.hung_hang,
    )


async def dau_voi_dich(kho, ts, d, rng: random.Random, hs: dict, boi_canh: str = "",
                       cho_chay: bool = True) -> KetQua:
    """Một trận sinh tử với yêu thú / ma tu. Trả về KetQua đã ghi mọi hậu quả."""
    a = ben_tu_nguoi_choi(ts)
    b = ben_tu_dich(d)
    td = chiendau.giao_dau(a, b, rng)

    kq = KetQua(tieu_de=f"Chạm mặt {d.ten}", mau=config.MAU_HUYET)
    if boi_canh:
        kq.them(boi_canh)
    kq.them(d.lam_quen)
    kq.them(d.mo_ta)
    for c in td.van:
        kq.them(c)

    thang = td.thang is a
    kq.du_lieu["thang"] = thang
    kq.du_lieu["ap_dao"] = td.ap_dao
    if thang:
        ts.so_tran_thang += 1
        ts.danh_vong += max(1, int(3 * (1 + d.canh_gioi) * (1.2 if d.loai == "ma_tu" else 1.0)))
        if d.loai in ("ma_tu", "tan_tu"):
            ts.sat_nghiep += 1
        thu = int(ten_theo_muc(d) * van_khi(rng, ts.dao_tam))
        ts.tu_vi += thu
        ton = int(td.ton_thuong_ke_thua * 0.35 * rng.uniform(0.5, 1.0))
        ts.than_the = max(5, ts.than_the - ton)
        rot = roi_do(rng, d.chien_loi, hs.get("ky_ngo", 1.0))
        kq.them(chiendau.loi_binh(td, a))
        if rot:
            ten_vat = []
            for ma in rot:
                sl = 1
                if ma == "linh_thach_ha":
                    sl = rng.randint(8, 40) * (1 + d.canh_gioi)
                    ts.linh_thach += sl
                    ten_vat.append(f"một nắm linh thạch")
                    continue
                await kho.them_vat(ts.user_id, ma, sl)
                ten_vat.append(vatpham.ten(ma))
            kq.them(
                "Ngươi lục soát chiến trường. Thu được: **" + ", ".join(ten_vat) + "**. "
                + ("Chiến lợi phẩm dính máu, nhưng linh thạch thì không phân biệt máu của ai."
                   if d.loai in ("ma_tu", "tan_tu") else
                   "Ngươi lóc lấy phần dùng được, phần còn lại để cho quạ.")
            )
        else:
            kq.them("Trên người kẻ bại trận chẳng có gì đáng lấy. Có những trận đánh chỉ để lại vết thương.")
    else:
        ts.so_tran_thua += 1
        ts.than_the = max(1, ts.than_the - td.ton_thuong_ke_thua)
        ts.thuong_toi = int(time.time()) + int(
            config.DUONG_THUONG_TOI_DA * (0.35 + 0.65 * td.ap_dao)
        )
        # mất mát
        tui = await kho.tui(ts.user_id)
        mat = []
        if tui and rng.random() < 0.55:
            ma = rng.choice(list(tui.keys()))
            sl = min(tui[ma], rng.randint(1, 2))
            await kho.them_vat(ts.user_id, ma, -sl)
            mat.append(vatpham.ten(ma))
        if ts.linh_thach > 0 and rng.random() < 0.5:
            mat_lt = int(ts.linh_thach * rng.uniform(0.15, 0.45))
            ts.linh_thach -= mat_lt
            mat.append("một phần linh thạch")
        kq.them(chiendau.loi_binh(td, a))
        if mat:
            kq.them(
                "Khi tỉnh lại, túi càn khôn đã bị lục. Mất: **" + ", ".join(mat) + "**. "
                "Ngươi nằm nghe tiếng gió, và học được rằng thua trận thì mất nhiều hơn là mất mặt."
            )
        # cửa tử
        chet = td.chi_mang and d.canh_gioi > ts.canh_gioi and rng.random() < 0.22
        if chet:
            ts.da_chet = 1
            kq.them(
                "**Ngươi không kịp bò ra khỏi chỗ đó.**\n\n"
                f"{d.ten} không vội. Nó chờ tới khi ngươi ngừng cựa quậy. "
                "Trên đường tu, cái chết không có nhạc đệm, không có lời trăng trối kịp nói ra — "
                "chỉ có một chỗ đất ẩm, một cơn lạnh dâng từ chân lên, và rồi thôi."
            )
        else:
            kq.them(
                f"Ngươi lê được thân xác đi khỏi đó. Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa "
                "mới dám vận công lại. Sống, đôi khi, đã là một chiến quả."
            )
    await kho.luu(ts)
    return kq


def ten_theo_muc(d) -> int:
    """Đạo hạnh thu được khi hạ một kẻ địch."""
    from ..canhgioi import tu_vi_can_thiet
    return max(5, int(tu_vi_can_thiet(d.canh_gioi, max(1, d.tang)) * 0.09))


# ───────────────────────── khám phá ─────────────────────────

KY_NGO = (
    "ngoc_gian", "co_nhan", "linh_thach", "suoi_linh", "co_tich_do", "thi_the",
)


async def kham_pha(kho, ts, rng: random.Random | None = None, hs: dict | None = None,
                   ma_dia_danh: str | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    con = await kho.con_cho(ts.user_id, "khampha")
    if con > 0:
        return KetQua(tieu_de="Chân còn mỏi",
                      van=[f"Ngươi vừa lặn lội về, giày còn bám bùn. Nghỉ {khac_gio(con)} đã."],
                      thanh_cong=False)
    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Không đi nổi",
                      van=[f"Với thương thế này mà ra ngoài thì chỉ tổ làm mồi. "
                           f"Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa."],
                      thanh_cong=False)

    dd = dl_diadanh.lay(ma_dia_danh) if ma_dia_danh else None
    if dd is None:
        dd = rng.choice(dl_diadanh.cho_phep(ts.canh_gioi))
    if dd.canh_gioi_toi_thieu > ts.canh_gioi:
        return KetQua(
            tieu_de="Chưa đủ tư cách",
            van=[f"**{dd.ten}** không phải chỗ cho kẻ ở bậc của ngươi. "
                 "Người ta không cấm ngươi đi — chỉ là chưa ai ở bậc ngươi đi rồi mà về kể lại."],
            thanh_cong=False)

    kq = KetQua(tieu_de=dd.ten, anh=dd.tranh or None)
    kq.them(f"**{dd.ten}.** {dd.mo_ta}")
    kq.them(rng.choice(list(dd.canh_vat)))

    ts_nguy = dd.nguy_hiem * hs.get("nguy_hiem", 1.0)
    trong_so = dict(dd.trong_so)
    trong_so["dich"] *= max(0.4, hs.get("nguy_hiem", 1.0))
    trong_so["ky_ngo"] *= max(0.4, hs.get("ky_ngo", 1.0))
    loai = rng.choices(list(trong_so.keys()), weights=list(trong_so.values()), k=1)[0]

    if loai == "duoc":
        ma = rng.choice(list(dd.duoc_lieu))
        sl = 1 + (1 if rng.random() < 0.3 else 0)
        await kho.them_vat(ts.user_id, ma, sl)
        vp = vatpham.lay(ma)
        kq.them(
            f"Ngươi đi chậm, mắt quét từng bụi cỏ như một kẻ mót lúa. Rồi ngươi thấy nó: **{vp.ten}**"
            + (f" — {sl} nhánh." if sl > 1 else ".")
        )
        kq.them(vp.mo_ta + " Ngươi cắt cuống bằng dao ngọc, gói vào lá, cất kỹ.")
    elif loai == "lieu":
        ma = rng.choice(list(dd.vat_lieu))
        await kho.them_vat(ts.user_id, ma, 1)
        vp = vatpham.lay(ma)
        kq.them(f"Dưới một lớp đất mỏng, ngươi moi lên được một mẩu **{vp.ten}**. {vp.mo_ta}")
    elif loai == "canh":
        kq.them(rng.choice([c for c in dd.canh_vat]))
        thu = int(30 * (1 + ts.canh_gioi) * van_khi(rng, ts.dao_tam) * 0.3)
        ts.tu_vi += thu
        kq.them(
            "Chuyến này không nhặt được gì. Nhưng ngươi ngồi lại một lúc, nhìn trời sẫm dần, "
            "và trong lòng có thứ gì đó lắng xuống. Đường tu không phải lúc nào cũng đo bằng vật."
        )
    elif loai == "ky_ngo":
        kq_ky = await _ky_ngo(kho, ts, rng, dd, hs)
        for c in kq_ky.van:
            kq.them(c)
        kq.mau = kq_ky.mau
    elif loai == "co_tich":
        kq.them(
            "Sau một vách đá phủ dây leo, ngươi thấy một khe hở đủ cho người lách vào. "
            "Bên trong là bậc thang đá dẫn xuống. Bụi trên bậc dày cả tấc — đã rất lâu không ai bước."
        )
        await kho.them_vat(ts.user_id, "co_tich_tan_do", 1)
        kq.them(
            "Ngươi chỉ dám đi xuống mười bậc rồi quay lên: khí tức bên dưới không phải thứ ngươi kham nổi lúc này. "
            "Nhưng ngươi có mang theo được một thứ — **Tàn Đồ Cổ Tích** giắt trên vách, mép đã cháy sém."
        )
    else:  # dich
        d = dl_dichthu.lay(rng.choice(list(dd.dich_thu)))
        chenh = d.canh_gioi - ts.canh_gioi
        if chenh >= 1 and rng.random() < 0.45:
            kq.them(
                f"{d.lam_quen}\n\nKhí tức của nó đè xuống khiến hai đầu gối ngươi mềm nhũn. "
                "Ngươi lùi lại, từng bước một, không quay lưng, không thở mạnh."
            )
            if rng.random() < 0.7:
                kq.them(
                    "Ngươi thoát được. Về tới chỗ an toàn, ngươi mới thấy lòng bàn tay mình ướt đẫm. "
                    "Bỏ chạy không vinh quang, nhưng nghĩa địa thì đầy những kẻ vinh quang."
                )
                ts.than_the = max(10, ts.than_the - rng.randint(2, 8))
            else:
                kq.them("Nhưng nó đã ngửi thấy ngươi. **Chạy không kịp nữa.**")
                kq2 = await dau_voi_dich(kho, ts, d, rng, hs)
                for c in kq2.van[2:]:
                    kq.them(c)
                kq.mau = config.MAU_HUYET
        else:
            kq2 = await dau_voi_dich(kho, ts, d, rng, hs)
            for c in kq2.van:
                kq.them(c)
            kq.mau = config.MAU_HUYET

    await kho.dat_cho(ts.user_id, "khampha", config.NGUOI_LANH["khampha"])
    await kho.luu(ts)
    return kq


async def _ky_ngo(kho, ts, rng: random.Random, dd, hs: dict) -> KetQua:
    kq = KetQua(mau=config.MAU_KIM)
    loai = rng.choice(KY_NGO)
    if loai == "ngoc_gian":
        chua_biet = [m for m in dl_congthuc.TAT_CA if m not in await kho.so_tay(ts.user_id)]
        if chua_biet:
            ma = rng.choice(chua_biet)
            ct = dl_congthuc.lay(ma)
            await kho.hoc_cong_thuc(ts.user_id, ma)
            kq.them(
                "Trong hốc đá có một mảnh ngọc giản xám, nứt một đường chạy dọc. "
                "Ngươi áp thần thức vào — chữ trong đó nhảy múa, mờ đi rồi hiện lại, "
                "như một kẻ hấp hối cố nói cho hết câu."
            )
            kq.them(
                f"Đó là **{ct.ten}**. {ct.lai_lich} {ct.mo_ta}\n\n"
                "Ngươi khắc nó vào trí nhớ, rồi ngồi im rất lâu. Có những thứ nhặt được ngoài đường "
                "còn đáng giá hơn cả một đời cày cuốc."
            )
        else:
            ts.linh_thach += rng.randint(50, 200)
            kq.them("Một ngọc giản vỡ nát, chữ đã tan hết. Ngươi chỉ nhặt được mấy viên linh thạch rơi cạnh đó.")
    elif loai == "co_nhan":
        kq.them(
            "Bên gốc cây, một lão nhân áo rách đang nướng cá. Lão không ngẩng đầu, chỉ nói: "
            "*“Ngồi xuống. Cá đủ hai người.”*"
        )
        kq.them(
            "Các ngươi ăn hết con cá mà chẳng nói được mấy câu. Trước khi đi, lão gõ ngón tay lên trán ngươi một cái. "
            "*“Chỗ này của ngươi nghẽn. Tại vì ngươi sợ. Sợ thì không sao, nhưng đừng giả vờ là không sợ.”*"
        )
        ts.dao_tam = min(100, ts.dao_tam + rng.randint(4, 9))
        ts.tu_vi += int(300 * (1 + ts.canh_gioi) * 0.4)
        kq.them("Khi ngươi quay lại nhìn, chỗ ấy chỉ còn đống tro và một mảnh xương cá. Không có dấu chân nào cả.")
    elif loai == "linh_thach":
        so = rng.randint(60, 400) * (1 + ts.canh_gioi)
        ts.linh_thach += so
        kq.them(
            "Dưới rễ một cây đã đổ, có một cái túi da mục. Trong túi là linh thạch — "
            "loại hạ phẩm, đã mờ đi ít nhiều, nhưng còn dùng được."
        )
        kq.them(
            "Ngươi nhìn quanh. Cách đó ba bước là một bộ hài cốt nằm sấp, tay vươn về phía cái túi. "
            "Ngươi cúi đầu một cái, rồi cầm túi đi."
        )
    elif loai == "suoi_linh":
        thu = int(500 * (1 + ts.canh_gioi) * van_khi(rng, ts.dao_tam) * 0.5)
        ts.tu_vi += thu
        ts.than_the = min(100, ts.than_the + 15)
        kq.them(
            "Sau một khe đá hẹp là một mạch suối nhỏ, nước trong tới mức nhìn thấy từng hạt cát dưới đáy. "
            "Linh khí ở đây đậm gấp mấy lần bên ngoài — đây là một linh nhãn, tuy nhỏ."
        )
        kq.them(
            "Ngươi ngâm mình trong đó tới khi da tay nhăn lại. Khi bước ra, thân thể nhẹ bẫng, "
            "vết thương cũ trên vai cũng bớt nhức. Ngươi ghi nhớ đường về đây — "
            "và cũng biết rằng chỗ này sẽ không giữ được lâu nếu có kẻ khác biết."
        )
    elif loai == "co_tich_do":
        await kho.them_vat(ts.user_id, "truyen_tong_phu", 1)
        kq.them(
            "Trên xác một tu sĩ đã khô quắt, ngươi tìm được một lá **Truyền Tống Phù** còn nguyên. "
            "Hắn chết trong tư thế đang móc bùa ra khỏi ngực — chỉ chậm một khắc."
        )
        kq.them("Ngươi cất lá bùa vào chỗ dễ lấy nhất trong người. Bài học ấy, ngươi học không mất gì.")
    else:  # thi the
        kq.them(
            "Một xác tu sĩ nằm vắt ngang tảng đá, chết chưa lâu, máu còn chưa đen hẳn. "
            "Túi càn khôn của hắn đã bị lấy, nhưng trong ủng còn giấu một thứ."
        )
        ma = rng.choice(list(dd.duoc_lieu) + list(dd.vat_lieu))
        await kho.them_vat(ts.user_id, ma, 1)
        ts.dao_tam = max(5, ts.dao_tam - 2)
        kq.them(
            f"**{vatpham.ten(ma)}.** Ngươi cầm lấy, và tay ngươi không run — điều đó khiến ngươi hơi sợ chính mình. "
            "Kẻ giết hắn có thể còn quanh đây. Ngươi đi rất nhanh, và không chôn hắn."
        )
    return kq


# ───────────────────────── tìm dược ─────────────────────────

async def tim_duoc(kho, ts, rng: random.Random | None = None, hs: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    con = await kho.con_cho(ts.user_id, "timduoc")
    if con > 0:
        return KetQua(tieu_de="Chưa vội",
                      van=[f"Sườn núi vừa bị ngươi lật tung, cây cỏ cần thời gian. Đợi {khac_gio(con)}."],
                      thanh_cong=False)
    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Nằm yên đã",
                      van=["Bò dậy hái thuốc với cái thân này thì thuốc hái được chưa chắc đủ chữa cho chính ngươi."],
                      thanh_cong=False)

    dd = rng.choice(dl_diadanh.cho_phep(ts.canh_gioi))
    kq = KetQua(tieu_de="Hái thuốc")
    kq.them(
        f"Ngươi mang theo giỏ trúc và con dao ngọc nhỏ, lần theo sườn **{dd.ten}**. "
        "Hái thuốc là việc của kẻ nhẫn nại: cúi lưng cả buổi, mỏi tới mức không thẳng người lên được, "
        "để đổi lấy vài nhánh cỏ mà đan sư sẽ đốt hết trong một canh giờ."
    )
    so = rng.choices([0, 1, 2, 3], weights=[12, 45, 30, 13], k=1)[0]
    so = int(so * hs.get("ky_ngo", 1.0)) or so
    thu = []
    for _ in range(so):
        ma = rng.choice(list(dd.duoc_lieu))
        await kho.them_vat(ts.user_id, ma, 1)
        thu.append(vatpham.ten(ma))
    if thu:
        dem: dict[str, int] = {}
        for t in thu:
            dem[t] = dem.get(t, 0) + 1
        kq.them("Cuối buổi, trong giỏ có: **" + ", ".join(f"{k}{f' ×{v}' if v > 1 else ''}" for k, v in dem.items()) + "**.")
    else:
        kq.them(
            "Cả buổi chiều, giỏ vẫn rỗng. Chỗ nào tốt thì người ta đã vặt sạch từ đời nào, "
            "chỗ nào còn thì ngươi chưa đủ sức tới. Ngươi ngồi bệt xuống, cười một tiếng khô khốc."
        )

    if rng.random() < 0.16 * hs.get("nguy_hiem", 1.0):
        d = dl_dichthu.lay(rng.choice(list(dd.dich_thu)))
        kq.them("Rồi ngươi nghe tiếng sau lưng.")
        kq2 = await dau_voi_dich(kho, ts, d, rng, hs)
        for c in kq2.van:
            kq.them(c)
        kq.mau = config.MAU_HUYET

    await kho.dat_cho(ts.user_id, "timduoc", config.NGUOI_LANH["timduoc"])
    await kho.luu(ts)
    return kq


# ───────────────────────── đấu kỵ sĩ ─────────────────────────

async def duy_ky_si(kho, ts, rng: random.Random | None = None, hs: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    con = await kho.con_cho(ts.user_id, "duykysi")
    if con > 0:
        return KetQua(tieu_de="Chưa tới lượt",
                      van=[f"Vết bầm lần trước còn chưa tan. Đợi {khac_gio(con)} rồi hẵng tìm người mà đánh."],
                      thanh_cong=False)
    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Đứng còn không vững",
                      van=["Đi tỉ thí với thân thể này chỉ có một kết cục, và kết cục đó không thú vị."],
                      thanh_cong=False)

    d = dl_dichthu.ngau_nhien_theo_muc(ts.canh_gioi, rng)
    boi_canh = rng.choice([
        "Trên một bãi đá bằng phẳng cạnh quan đạo, nơi các tán tu vẫn hay dừng chân để đo sức nhau.",
        "Giữa một khoảng rừng thưa, lá khô dày tới mắt cá chân — bước một bước là kêu một tiếng.",
        "Dưới chân một cây cầu đá cũ, nước chảy xiết bên dưới, tiếng nước át cả tiếng thở.",
    ])
    kq = await dau_voi_dich(kho, ts, d, rng, hs, boi_canh=boi_canh)
    kq.tieu_de = "Tỉ thí"
    await kho.dat_cho(ts.user_id, "duykysi", config.NGUOI_LANH["duykysi"])
    return kq
