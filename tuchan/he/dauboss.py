"""Đại chiến yêu vương — đánh boss là chuyện của nhiều người, và của thời gian.

Cơ chế: một con yêu vương hiện thế, cả thiên hạ cùng đánh. Mỗi lần lao vào là một trận
kể bằng văn; đòn nặng hay nhẹ máy tính hết, người chơi chỉ thấy vết thương của boss
dày thêm. Nó không hồi máu. Nó cũng không chờ. Quá hạn thì nó về hang, mang theo cả thể diện
của những kẻ bất lực.

Không có thanh máu — chỉ có nguyên khí trừ dần dưới lớp da, và bảng ghi công ai ra tay.
"""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import suc_manh_nen, ten_canh_gioi, tu_vi_can_thiet
from ..data import boss as dl_boss
from ..data import vatpham
from ..vanphong import khac_gio
from . import chiendau
from .ketqua import KetQua
from .phieuluu import ben_tu_nguoi_choi
from .thienco import roi_do, van_khi


# ───────────────────────── dựng bên tham chiến ─────────────────────────

def ben_boss(bv: dl_boss.BossVuong) -> chiendau.BenThamChien:
    cg = bv.canh_gioi
    tang = max(1, bv.tang)
    hp_m = int((400 + 150 * tang + 1200 * (cg ** 1.8)) * bv.tho * 1.5)
    cong = int((40 + 18 * tang + 150 * (cg ** 1.8)) * bv.hung_hang * bv.tho)
    thu = int((18 + 11 * tang + 75 * (cg ** 1.8)) * bv.tho)
    return chiendau.BenThamChien(
        ten=bv.ten,
        canh_gioi=bv.canh_gioi,
        tang=bv.tang,
        he_so_chien=bv.tho,
        can_cot=1.25,
        dao_tam=80,
        than_the=100,
        thu_doan=bv.thu_doan,
        hung_hang=bv.hung_hang,
        dan_pham=min(9, bv.canh_gioi + 3) if bv.canh_gioi >= 2 else 0,
        hp=hp_m,
        hp_max=hp_m,
        cong=cong,
        thu=thu,
        bao_kich=round(10.0 + cg * 2.0, 1),
        toc_do=int(55 + 10 * cg + tang * 3),
    )


def huyet_toi_da(bv: dl_boss.BossVuong) -> int:
    """Tổng nguyên khí phải đánh mới hết — quy đổi từ 'số nhát' của kẻ đúng bậc."""
    return max(10, int(suc_manh_nen(bv.canh_gioi, bv.tang) * bv.so_tuot))


def thoi_han_giay(bv: dl_boss.BossVuong) -> int:
    # kể cả khi diễn tập ép thời gian, chiến trường cũng phải mở đủ lâu cho một trận ra hồn
    return max(1800, int(bv.huyet_le * 60 * getattr(config, "HE_SO_GIAY", 1.0)))


def _con_het_han(row: dict, bv: dl_boss.BossVuong) -> bool:
    return int(row["bat_dau"]) + thoi_han_giay(bv) <= int(time.time())


# ───────────────────────── triệu hồi ─────────────────────────

async def chieu_muoi(kho, guild_id: int, rng: random.Random | None = None,
                     ma_boss: str | None = None, ke_goi: int = 0) -> KetQua:
    """Gọi một yêu vương ra chiến trường. ma_boss=None thì tuỳ đất trời."""
    rng = rng or random.Random()
    hien = await kho.boss_lay(guild_id)
    if hien:
        bv_cu = dl_boss.lay(hien["ma"])
        if bv_cu and not _con_het_han(hien, bv_cu):
            return KetQua(
                tieu_de="Chiến trường còn đang đỏ",
                van=[f"**{bv_cu.ten}** vẫn chưa rút về. Giang hồ không đánh hai trận một lúc — "
                     "muốn thì đợi, hoặc tới mà chia công."],
                thanh_cong=False)
        if bv_cu:
            await _bo_chay(kho, guild_id, bv_cu, rng)

    bac, so_nguoi = await kho.dinh_the_gioi(guild_id)
    bv = dl_boss.lay(ma_boss) if ma_boss else dl_boss.chon_ngau_nhien(bac, rng)
    if bv is None:
        return KetQua(tieu_de="Không có kẻ thức tỉnh",
                      van=["Ngươi gọi mãi, chỉ có tiếng vượn đáp."], thanh_cong=False)
    await kho.boss_dat(guild_id, bv.ma, huyet_toi_da(bv), ke_goi)

    kq = KetQua(tieu_de=f"Yêu vương hiện thế — {bv.ten}", mau=config.MAU_HUYET, anh="dau_phap.png")
    kq.them(bv.xuat_the)
    kq.them(f"**{bv.ten}** — *{bv.hieu}*. {bv.mo_ta}")
    kq.them(
        f"Khí tức của nó phủ trọn một vùng; người dưới **{ten_canh_gioi(bv.canh_gioi, bv.tang)}** "
        "mà lại gần thì chân khí tự loãng ra."
    )
    kq.them(
        f"Chiến trường mở trong {khac_gio(thoi_han_giay(bv))}. Nó không chờ ai cả — "
        "quá hạn thì nó về, và những gì ngươi để lại chỉ còn là mấy vết thương không ai nhận."
    )
    if so_nguoi:
        kq.them("*Thiên hạ đang bàn tán. Kẻ nào ra tay trước, kẻ đó đứng đầu bảng công.*")
    kq.du_lieu["boss_ma"] = bv.ma
    kq.du_lieu["thong_bao"] = [f"⛰ **{bv.ten}** — *{bv.hieu}* — đã hiện thế. "
                               f"{khac_gio(thoi_han_giay(bv))} nữa thì nó rút. Ai muốn nổi danh, hôm nay đấy."]
    return kq


# ───────────────────────── xem chiến trường ─────────────────────────

async def hien_trang(kho, guild_id: int) -> KetQua:
    """Cảnh trạng chiến trường + bảng thương tích."""
    hien = await kho.boss_lay(guild_id)
    if not hien:
        kq = KetQua(tieu_de="Chiến trường vắng lặng")
        kq.them("Không có yêu vương nào đang hiện thế. Núi sông trở về nguyên trạng, "
                "chỉ còn dân chúng bàn nhau chuyện đêm qua đất rung.")
        kq.them("*Thiên hạ cứ nửa canh giờ lại gieo quẻ xem có kẻ nào thức tỉnh. "
                "Kẻ sốt ruột có thể tự triệu — nhưng nhớ: gọi thứ gì ra thì chịu trách nhiệm với thứ đó.*")
        kq.du_lieu["co_boss"] = False
        return kq

    bv = dl_boss.lay(hien["ma"])
    if bv is None:
        await kho.boss_xoa(guild_id)
        return KetQua(tieu_de="Không có yêu vương nào đang hiện thế",
                      van=["Sổ chiến trường ghi một cái tên mà không ai tra được. Chuyện cũ quá rồi."],
                      thanh_cong=False)
    if _con_het_han(hien, bv):
        await _bo_chay(kho, guild_id, bv, random.Random())
        return KetQua(tieu_de="Nó về rồi",
                      van=[f"**{bv.ten}** đã rút từ lâu. Vết thương để lại sẽ lành trên da nó, "
                           "và nó sẽ nhớ mặt kẻ đã cắt."],
                      thanh_cong=False)

    kq = KetQua(tieu_de=f"Chiến trường — {bv.ten}", mau=config.MAU_HUYET, anh="dau_phap.png")
    kq.them(bv.mo_ta)
    con_lai = int(hien["huyet"]) / max(1, int(hien["huyet_max"]))
    kq.them(_muc_do(bv, con_lai))
    kq.them(
        f"*Nó nán lại thêm {khac_gio(max(0, int(hien['bat_dau']) + thoi_han_giay(bv) - int(time.time())))} "
        "rồi rút. Đánh hay không thì quyết nhanh.*"
    )

    dong = await kho.boss_ds(guild_id)
    if dong:
        kq.them("**Ai đã ra tay:**\n" + "\n".join(
            _bang_cong(d, int(hien["huyet_max"]), i + 1) for i, d in enumerate(dong[:8])))
    else:
        kq.them("Chưa ai động thủ. Con mồi còn nguyên, mà kẻ dám ăn thì chưa thấy ai.")
    kq.du_lieu.update({"boss_ma": bv.ma, "con_lai": con_lai, "co_boss": True})
    return kq


def _muc_do(bv: dl_boss.BossVuong, ti_le: float) -> str:
    if ti_le > 0.92:
        return "Nó vẫn còn nguyên như lúc chui lên. Máu chưa chảy, mà cái ngạo thì đã đủ đầy."
    if ti_le > 0.66:
        return f"Trên da {bv.ten} đã loang lổ mấy vệt sâu — đủ để nó ngừng nhìn khinh thiên hạ."
    if ti_le > 0.4:
        return f"{bv.ten} thở gấp hơn hẳn ban nãy. Mỗi bước nó đi, máu nhỏ lại thành hàng trên đá."
    if ti_le > 0.18:
        return "Nó không còn gầm nữa. Yêu vương sắp chết thì im lặng — cái im lặng ấy cả chiến trường nghe thấy."
    if ti_le > 0.0:
        return "Chỉ còn một hơi tàn chống đỡ. Ai chém nhát cuối, nhát ấy sẽ được kể lại cả trăm năm."
    return "Xương nó đã gãy, khí nó đã tán. Nó chưa khuỵu vì chưa tìm được kẻ đáng để khuỵu trước mặt."


def _bang_cong(d: dict, huyet_max: int, hang: int) -> str:
    ti = max(1, round(100 * int(d["sat_thuong"]) / max(1, huyet_max)))
    return f"**{hang}. {d['ten']}** — {d['so_lan']} lần ra tay, để lại chừng {ti}% thương tích"


# ───────────────────────── ra đòn ─────────────────────────

async def danh_thuong(kho, ts, guild_id: int, rng: random.Random | None = None,
                      hs: dict | None = None) -> KetQua:
    """Một lần lao vào chiến trường.

    kq.du_lieu["thong_bao"]: các dòng nên loan đi khắp thiên hạ.
    kq.du_lieu["boss_chet"]: True nếu chính nhát này kết liễu nó.
    """
    rng = rng or random.Random()
    hs = hs or {}

    if ts.da_chet:
        return KetQua(tieu_de="Người chết không đánh được ai",
                      van=["Kẻ đã khuất thì chỉ còn cách xem trận bằng mắt người khác."],
                      thanh_cong=False)
    hien = await kho.boss_lay(guild_id)
    if not hien:
        return KetQua(tieu_de="Không có gì để đánh",
                      van=["Chiến trường trống trơn. Yêu vương nào đó chưa thức, hoặc đã rút về rồi."],
                      thanh_cong=False)
    bv = dl_boss.lay(hien["ma"])
    if bv is None or _con_het_han(hien, bv):
        if bv:
            await _bo_chay(kho, guild_id, bv, rng)
        return KetQua(tieu_de="Nó về rồi",
                      van=["Ngươi chạy tới nơi thì chỉ thấy dấu chân kéo dài về phía chân trời. "
                           "Chậm một canh giờ, mất cả danh lẫn công."],
                      thanh_cong=False)

    con = await kho.con_cho(ts.user_id, "daboss")
    if con > 0:
        return KetQua(tieu_de="Chưa lại sức",
                      van=["Mỗi nhát với yêu vương là dồn cả sở học vào một cánh tay. "
                           f"Đừng cố thêm nữa — nghỉ {khac_gio(con)} đã."],
                      thanh_cong=False)
    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Thương nặng",
                      van=["Với cái thân này mà lao vào chiến trường thì không gọi là đánh boss, "
                          f"mà gọi là nộp mình. Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa mới nên động võ."],
                      thanh_cong=False)
    if bv.canh_gioi - ts.canh_gioi >= 2:
        return KetQua(tieu_de="Không tới được gần",
                      van=["Ngươi mới đi tới rìa chiến trường thì khí tức của nó đè xuống, và hai đầu gối "
                          "ngươi tự khuỵu. Đây không phải hèn — đây là đạo lý của bậc. "
                          "Cách nhau hai cảnh giới thì đòn của ngươi chưa chạm đã tan."])

    a = ben_tu_nguoi_choi(ts)
    b = ben_boss(bv)
    kq_mo = KetQua()
    kq_mo.them(f"{bv.ten} thấy ngươi. {bv.loi_de}" if bv.loi_de else f"{bv.ten} thấy ngươi.")

    td = chiendau.giao_dau(a, b, rng, so_hiep=rng.randint(3, 4))

    kq = KetQua(tieu_de=f"{ts.ten} đánh {bv.ten}", mau=config.MAU_HUYET)
    for c in kq_mo.van:
        kq.them(c)
    for c in td.van:
        kq.them(c)

    thang = td.thang is a
    sa, sb = a.suc_chien(), b.suc_chien()
    vk = van_khi(rng, ts.dao_tam, ts.danh_vong)
    goc = (sa ** 0.60) * (sb ** 0.40)
    sat_thuong = int(goc * (0.9 + 1.4 * max(0.0, td.ap_dao - 0.5)) * vk)
    if not thang:
        sat_thuong = max(1, int(sat_thuong * 0.16))
    sat_thuong = max(1, sat_thuong)
    # kể cả kẻ không đủ sức, mỗi lần lao vào cũng phải lại được một vệt rõ —
    # không ai đánh bò cạp tới ngày thứ bốn mươi mà nó vẫn như mới.
    san = max(2, int(int(hien["huyet_max"]) / 70))
    sat_thuong = max(sat_thuong, san)

    thu_nho = int(tu_vi_can_thiet(bv.canh_gioi, bv.tang) * 0.012 * (0.5 + td.ap_dao) * vk)
    ts.tu_vi += max(1, thu_nho)

    if thang:
        ts.so_tran_thang += 1
        ts.danh_vong += 2 + bv.canh_gioi
        ton = int(td.ton_thuong_ke_thua * rng.uniform(0.25, 0.45))
        ts.than_the = max(8, ts.than_the - max(1, ton))
        kq.them(f"Đòn của ngươi ngập vào tới cán. {bv.ten} gầm lên — lần đầu tiên trong trận này, "
                "tiếng gầm ấy mang theo chút gì gần giống ngạc nhiên.")
    else:
        ts.so_tran_thua += 1
        ton = int(td.ton_thuong_ke_thua * rng.uniform(0.8, 1.15))
        ts.than_the = max(1, ts.than_the - ton)
        # đánh boss mà thua thì phần lớn là bị hất văng — đau, gãy, nhưng còn đường bò về.
        ts.thuong_toi = int(time.time()) + int(
            config.DUONG_THUONG_TOI_DA * (0.18 + 0.3 * td.ap_dao))
        kq.them(f"Ngươi bị hất văng khỏi rìa chiến trường, cày một vệt dài tới tận bìa rừng. "
                "Vẫn kịp để lại một đường lên mình nó, nhưng cái giá thì nằm cả trong ngực.")
        chet = td.chi_mang and rng.random() < 0.16
        if chet:
            ts.da_chet = 1
            kq.them(
                f"**{bv.ten} đuổi theo.**\n\nMột cái bóng chụp xuống, và ngươi hiểu ra rằng trên chiến trường "
                "này, kẻ bị thương xong còn phải học cách bò đi. Ngươi không kịp. "
                "Người ta tìm thấy ngươi ba hôm sau, và chôn ở triền núi, hướng nhìn về phía đầm."
            )

    con_lai = await kho.boss_giam_huyet(guild_id, ts.user_id, ts.ten, sat_thuong)
    await kho.dat_cho(ts.user_id, "daboss", config.NGUOI_LANH["daboss"])
    await kho.luu(ts)

    bao: list[str] = []
    if con_lai <= 0:
        ket = await _ket_thuc(kho, ts, guild_id, bv, rng)
        for c in ket.van:
            kq.them(c)
        kq.mau = config.MAU_KIM
        kq.chu_thich = ket.chu_thich
        bao.append(f"⚔ **{bv.ten}** đã bị hạ. Nhát cuối thuộc về **{ts.ten}**.")
        kq.du_lieu["boss_chet"] = True
        kq.du_lieu["an_huong"] = True
    else:
        huyet_max = int(hien["huyet_max"])
        ti = max(1, round(100 * con_lai / max(1, huyet_max)))
        bao.append(f"⚔ **{bv.ten}** còn chừng {ti}% nguyên khí. **{ts.ten}** vừa để lại một vết thương "
                   f"(-{sat_thuong}). Chiến trường còn {khac_gio(thoi_han_giay(bv) - (int(time.time()) - int(hien['bat_dau'])))}.")
        kq.them(
            f"*Nguyên khí của nó đã hao chừng {max(1, round(100 * (huyet_max - con_lai) / huyet_max))}%.*"
        )
    kq.du_lieu["thong_bao"] = bao
    return kq


# ───────────────────────── kết thúc: hạ được hoặc nó tự về ─────────────────────────

async def _ket_thuc(kho, ts_ke_chot, guild_id: int, bv: dl_boss.BossVuong,
                    rng: random.Random) -> KetQua:
    """Boss vừa gục. Chia công theo vết thương; kẻ chém nhát cuối ăn thêm."""
    hien = await kho.boss_lay(guild_id) or {}
    huyet_max = int(hien.get("huyet_max", 1) or 1)
    dong = await kho.boss_ds(guild_id)
    base_tv = int(tu_vi_can_thiet(bv.canh_gioi, bv.tang) * 0.35)
    base_lt = int(40 * (2.35 ** bv.canh_gioi))
    base_dv = int(60 * (1 + bv.canh_gioi) ** 2)

    kq = KetQua(tieu_de=f"{bv.ten} đã gục")
    kq.them(
        f"**{bv.ten}** khuỵu xuống trước, rồi đổ nghiêng xuống sau — chậm chạp, gần như ung dung, "
        "kiểu của kẻ biết mình chết vì bao nhiêu nhát và của tay nào. Máu nó ngấm vào đất, "
        "và chỗ đất ấy ba năm sau vẫn không cỏ mọc."
    )
    kq.them(
        f"{ts_ke_chot.ten} là kẻ chém nhát cuối. Trong giang hồ, nhát cuối đáng giá hơn mười nhát dẫn đường — "
        "không phải vì sát thương, mà vì cái tên ấy sẽ được nhắc mỗi lần người ta kể chuyện đêm nay."
    )

    so_nguoi = 0
    ten_rot_ke_chot: list[str] = []
    for d in dong:
        c = await kho.lay_tu_si(d["user_id"])
        if c is None:
            continue
        share = min(1.0, int(d["sat_thuong"]) / max(1, huyet_max))
        c.tu_vi += max(3, int(base_tv * share))
        c.linh_thach += max(5, int(base_lt * share))
        c.danh_vong += max(3, int(base_dv * share))
        rot = roi_do(rng, bv.chien_loi, 0.5 + 1.3 * share)
        ten_rot = []
        for ma in rot:
            if ma == "linh_thach_ha":
                c.linh_thach += rng.randint(30, 90) * (1 + bv.canh_gioi)
                continue
            await kho.them_vat(c.user_id, ma, 1)
            ten_rot.append(vatpham.ten(ma))
        if c.user_id == ts_ke_chot.user_id:
            c.danh_vong += int(base_dv * 0.5)
            for ma in roi_do(rng, bv.chien_loi, 1.5):
                if ma == "linh_thach_ha":
                    c.linh_thach += rng.randint(60, 150) * (1 + bv.canh_gioi)
                    continue
                await kho.them_vat(c.user_id, ma, 1)
                ten_rot.append(vatpham.ten(ma))
            g = c.ghi()
            g["boss_ha"] = int(g.get("boss_ha", 0)) + 1
            c.dat_ghi(g)
            ten_rot_ke_chot = list(dict.fromkeys(ten_rot))
        await kho.luu(c)
        so_nguoi += 1
        await kho.chep(c.user_id, "boss",
                       f"Hạ {bv.ten}: {d['so_lan']} lần ra tay, chiến lợi phẩm đã chia.")

    if ten_rot_ke_chot:
        kq.them("Ngươi lục xác nó trước, theo đúng luật kẻ ra tay cuối. Thu được: **"
                + ", ".join(ten_rot_ke_chot) + "**.")
    kq.them(f"Chiến trường giải toả trong lặng lẽ. {so_nguoi} kẻ dám đứng hôm nay — "
            "thiên hạ sẽ kiểm lại sau, khi máu trên tay ai cũng đã rửa sạch.")
    await kho.boss_xoa(guild_id)
    kq.chu_thich = f"⚔ {ts_ke_chot.ten} hạ {bv.ten} — {so_nguoi} tu sĩ được chia công."
    return kq


async def _bo_chay(kho, guild_id: int, bv: dl_boss.BossVuong, rng: random.Random) -> None:
    """Hết hạn mà chưa giết nổi: an ủi bằng danh vọng, rồi dọn trận địa."""
    dong = await kho.boss_ds(guild_id)
    for d in dong:
        c = await kho.lay_tu_si(d["user_id"])
        if c is None:
            continue
        c.danh_vong += min(12, 2 * max(1, int(d["so_lan"])))
        await kho.luu(c)
        await kho.chep(c.user_id, "boss",
                       f"{bv.ten} rút về, mang theo {d['so_lan']} vết thương của ngươi.")
    await kho.boss_xoa(guild_id)


async def don_dep(kho, guild_id: int, rng: random.Random | None = None) -> list[str]:
    """Vòng tuần tra: dọn chiến trường hết hạn, có thể triệu boss mới. Trả về dòng để loan báo."""
    rng = rng or random.Random()
    bao: list[str] = []
    hien = await kho.boss_lay(guild_id)
    if hien:
        bv = dl_boss.lay(hien["ma"])
        if bv and _con_het_han(hien, bv):
            await _bo_chay(kho, guild_id, bv, rng)
            bao.append(f"🌫 **{bv.ten}** đã mang mình rời chiến trường. "
                       "Vết thương còn đó — lần sau gặp lại, nó sẽ nhớ.")
        return bao

    now = int(time.time())
    lan_goi = await kho.thoi_muc_xem("boss_lan_goi") or 0
    _, so_nguoi = await kho.dinh_the_gioi(guild_id)
    if so_nguoi > 0 and now - int(lan_goi) >= config.BOSS_TRONG_THOI and rng.random() < config.BOSS_XAC_SUAT:
        await kho.thoi_muc_dat("boss_lan_goi", now)
        bac, _ = await kho.dinh_the_gioi(guild_id)
        bv = dl_boss.chon_ngau_nhien(bac, rng)
        await kho.boss_dat(guild_id, bv.ma, huyet_toi_da(bv), 0)
        bao.append(f"⛰ **{bv.ten}** — *{bv.hieu}* — vừa hiện thế. {bv.xuat_the} "
                   "Ai muốn nổi danh thì hôm nay đấy.")
    return bao
