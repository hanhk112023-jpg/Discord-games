"""Tông môn: xin vào thì khó, ra thì càng khó."""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import ten_canh_gioi
from ..data import congthuc as dl_congthuc
from ..data import dichthu as dl_dichthu
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..data import viecmon as dl_viecmon
from ..vanphong import khac_gio
from . import phieuluu
from .ketqua import KetQua


async def gia_nhap(kho, ts, ma_mon: str, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    mp = dl_monphai.lay(ma_mon) or dl_monphai.tim_theo_ten(ma_mon)
    if mp is None:
        return KetQua(tieu_de="Không có môn phái ấy",
                      van=["Ngươi hỏi khắp chợ, không ai nghe nói tới cái tên đó bao giờ."], thanh_cong=False)
    if ts.mon_phai:
        cu = dl_monphai.lay(ts.mon_phai)
        return KetQua(
            tieu_de="Đã có nơi để về",
            van=[f"Ngươi đã mang danh đệ tử **{cu.ten if cu else ts.mon_phai}**. "
                 "Trong giang hồ, kẻ đổi cửa hai lần thì cửa thứ ba sẽ không mở cho hắn nữa. "
                 "Muốn đi thì phải rời môn trước — và cái giá của việc ấy không rẻ."],
            thanh_cong=False)
    if (ts.canh_gioi, ts.tang) < (mp.yeu_cau_canh_gioi, mp.yeu_cau_tang):
        return KetQua(
            tieu_de="Bị từ chối",
            van=[f"Chấp sự nhìn khí tức của ngươi một lượt, rồi khép sổ lại. "
                 f"*“{mp.ten} năm nay chỉ nhận từ {ten_canh_gioi(mp.yeu_cau_canh_gioi, mp.yeu_cau_tang)} trở lên. "
                 f"Ngươi về luyện thêm đi. Nếu còn sống thì sang năm lại tới.”*\n\n"
                 "Cánh cổng đóng lại trước mặt ngươi, không dữ dằn, không thương hại. Chỉ là đóng lại."],
            thanh_cong=False)

    ts.mon_phai = mp.ma
    ts.cong_hien = 0
    kq = KetQua(tieu_de=f"Nhập môn — {mp.ten}", anh=mp.tranh or None, mau=config.MAU_LINH)
    kq.them(f"**{mp.ten}.** {mp.dia_the}.")
    kq.them(mp.mo_ta)
    kq.them(
        "Lễ nhập môn không có gì long trọng: ngươi quỳ ba lạy trước tổ sư đường, uống một chén nước lã, "
        "và ký tên mình vào một cuốn sổ dày đã ố vàng. Trên trang ấy, phía trên tên ngươi, "
        "có mấy cái tên đã bị gạch chéo bằng mực đỏ."
    )
    kq.them(f"**Quy củ:** {mp.quy_cu}")
    kq.them(
        f"Ngươi được truyền **{mp.cong_phap}**. {mp.cong_phap_mo_ta}\n\n"
        "Vị trưởng lão truyền công không dặn dò gì thêm, chỉ nói một câu trước khi quay đi: "
        "*“Công pháp này đã chôn nhiều người hơn là nâng người. Ngươi liệu mà đi cho chậm.”*"
    )

    cho = []
    for ma in mp.ban_cong_thuc:
        if await kho.hoc_cong_thuc(ts.user_id, ma):
            ct = dl_congthuc.lay(ma)
            cho.append(ct.ten if ct else ma)
    for ma in mp.ban_vat_pham:
        await kho.them_vat(ts.user_id, ma, 1)
        cho.append(vatpham.ten(ma))
    if cho:
        kq.them("Chấp sự phát cho ngươi: **" + ", ".join(cho) + "**. Ký nhận, lăn tay, xong.")
    kq.them(
        f"Từ hôm nay ngươi là **{dl_monphai.chuc_vi_theo_cong_hien(0)}** của {mp.ten}. "
        "Chức ấy nghe cho oai, thực ra chỉ có nghĩa là ngươi được phép quét sân trong khuôn viên tông môn."
    )
    await kho.luu(ts)
    await kho.chep(ts.user_id, "mon_phai", f"Nhập môn {mp.ten}.")
    return kq


async def roi_mon(kho, ts) -> KetQua:
    if not ts.mon_phai:
        return KetQua(tieu_de="Ngươi vốn đã tự do", van=["Chẳng có cửa nào để ngươi bước ra cả."], thanh_cong=False)
    mp = dl_monphai.lay(ts.mon_phai)
    ten = mp.ten if mp else ts.mon_phai
    ts.mon_phai = ""
    ts.cong_hien = 0
    ts.danh_vong = max(0, ts.danh_vong - 30)
    ts.dao_tam = max(5, ts.dao_tam - 5)
    await kho.luu(ts)
    return KetQua(
        tieu_de="Rời môn",
        mau=config.MAU_HUYET,
        van=[
            f"Ngươi tự tay gạch tên mình khỏi sổ **{ten}**, đặt áo môn phái lên bàn, "
            "và bước xuống nghìn bậc đá. Không ai tiễn.",
            "Từ hôm nay ngươi lại là một kẻ không có sau lưng. Điều đó có cái tự do của nó, "
            "và cũng có cái lạnh của nó — thứ lạnh mà ngươi sẽ hiểu vào đêm đầu tiên ngủ ngoài trời.",
        ],
    )


# ───────────────────────── việc tông môn ─────────────────────────

async def nhan_viec(kho, ts, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    if not ts.mon_phai:
        return KetQua(
            tieu_de="Không ai giao việc cho kẻ vô môn",
            van=["Ngươi không thuộc về đâu cả, nên cũng chẳng ai buồn nhờ vả ngươi. "
                 "Tán tu tự do, và tự do thì đói."],
            thanh_cong=False)
    dang = await kho.viec_hien_tai(ts.user_id)
    if dang:
        v = dl_viecmon.lay(dang["ma"])
        return await xem_viec(kho, ts)
    con = await kho.con_cho(ts.user_id, "nhiemvu")
    if con > 0:
        return KetQua(tieu_de="Chấp sự đường đóng cửa",
                      van=[f"Hôm nay không còn việc nào để giao. Quay lại sau {khac_gio(con)}."], thanh_cong=False)

    ung = dl_viecmon.cho_phep(ts.canh_gioi)
    v = rng.choice(ung)
    await kho.nhan_viec(ts.user_id, v.ma)
    kq = KetQua(tieu_de="Chấp sự đường", mau=config.MAU_LINH)
    mp = dl_monphai.lay(ts.mon_phai)
    kq.them(
        f"Ngươi tới chấp sự đường của {mp.ten if mp else 'tông môn'} lúc sáng sớm. "
        "Trong sân đã có mấy đệ tử ngoại môn ngồi chờ, không ai nói chuyện với ai."
    )
    kq.them(f"**{v.nguoi_giao}** gọi tên ngươi.")
    kq.them(v.loi_dan)
    if v.loai == "thu_thap":
        can = ", ".join(f"{vatpham.ten(m)} ×{n}" for m, n in v.vat_can.items())
        kq.them(f"Thứ phải mang về: **{can}**. Mang đủ thì tới nộp; thiếu một cọng cũng đừng vác mặt tới.")
    elif v.loai == "tru_diet":
        d = dl_dichthu.lay(v.dich)
        kq.them(f"Thứ phải giết: **{d.ten if d else v.dich}**. {d.mo_ta if d else ''}")
        kq.them("*Khi nào sẵn sàng thì lên đường.*")
    else:
        kq.them(f"Việc này chia làm {v.so_chang} chặng. *Cứ đi từng chặng một.*")
    await kho.luu(ts)
    return kq


async def xem_viec(kho, ts) -> KetQua:
    dang = await kho.viec_hien_tai(ts.user_id)
    if not dang:
        return KetQua(tieu_de="Không có việc",
                      van=["Ngươi chưa nhận việc nào. Chấp sự đường vẫn mở."], thanh_cong=False)
    v = dl_viecmon.lay(dang["ma"])
    if v is None:
        await kho.xong_viec(ts.user_id)
        return KetQua(tieu_de="Việc đã bị huỷ", van=["Không ai còn nhớ ai giao việc gì cho ngươi."], thanh_cong=False)
    kq = KetQua(tieu_de=f"Việc đang dở: {v.ten}")
    kq.them(f"**{v.nguoi_giao}** đã giao việc cho ngươi, và người ta vẫn đang chờ.")
    if v.loai == "thu_thap":
        tui = await kho.tui(ts.user_id)
        dong = []
        for ma, sl in v.vat_can.items():
            co = tui.get(ma, 0)
            dong.append(f"{vatpham.ten(ma)}: {'đủ' if co >= sl else f'còn thiếu {sl - co}'}")
        kq.them("Kiểm lại túi: " + "; ".join(dong) + ".")
        kq.them("*Đủ rồi thì đi nộp.*")
    elif v.loai == "tru_diet":
        d = dl_dichthu.lay(v.dich)
        kq.them(f"Thứ phải giết vẫn còn sống: **{d.ten if d else v.dich}**.")
        kq.them("*Lên đường khi ngươi thấy mình đủ sức — hoặc đủ liều.*")
    else:
        kq.them(f"Đã đi được {dang['chang']}/{v.so_chang} chặng.")
        kq.them("*Đi tiếp chặng sau.*")
    return kq


async def _thuong_viec(kho, ts, v) -> list[str]:
    dong = []
    ts.cong_hien += v.cong_hien
    ts.linh_thach += v.linh_thach
    ts.danh_vong += max(1, v.cong_hien // 8)
    dong.append(
        f"Ngươi nhận về một túi linh thạch và một nét mực ghi công trong sổ tông môn. "
        f"Chức vị hiện tại: **{dl_monphai.chuc_vi_theo_cong_hien(ts.cong_hien)}**."
    )
    for ma in v.thuong_them:
        if ma in dl_congthuc.TAT_CA:
            if await kho.hoc_cong_thuc(ts.user_id, ma):
                ct = dl_congthuc.lay(ma)
                dong.append(f"Kèm theo, người ta đưa ngươi một ngọc giản: **{ct.ten}**. "
                            "Đó là thứ đáng giá hơn cả số linh thạch kia cộng lại.")
        else:
            await kho.them_vat(ts.user_id, ma, 1)
            dong.append(f"Kèm theo: **{vatpham.ten(ma)}**.")
    await kho.xong_viec(ts.user_id)
    await kho.dat_cho(ts.user_id, "nhiemvu", config.NGUOI_LANH["nhiemvu"])
    await kho.luu(ts)
    return dong


async def nop_viec(kho, ts) -> KetQua:
    dang = await kho.viec_hien_tai(ts.user_id)
    if not dang:
        return KetQua(tieu_de="Không có việc gì để nộp", van=["Ngươi chưa nhận việc nào cả."], thanh_cong=False)
    v = dl_viecmon.lay(dang["ma"])
    if v is None or v.loai != "thu_thap":
        return KetQua(tieu_de="Không phải việc nộp đồ",
                      van=["Việc của ngươi không giải quyết được bằng cách đặt đồ lên bàn."], thanh_cong=False)
    if not await kho.du_nguyen_lieu(ts.user_id, v.vat_can):
        return KetQua(tieu_de="Chưa đủ",
                      van=[f"{v.nguoi_giao} liếc vào giỏ của ngươi, rồi đẩy nó trở lại. Không nói một lời."],
                      thanh_cong=False)
    await kho.tieu_nguyen_lieu(ts.user_id, v.vat_can)
    kq = KetQua(tieu_de="Nộp việc", mau=config.MAU_LINH)
    kq.them(
        f"Ngươi đặt mọi thứ lên bàn. **{v.nguoi_giao}** kiểm từng món, chậm rãi, "
        "như thể đang tìm một lý do để chê. Cuối cùng lão gật đầu — chỉ một cái."
    )
    for d in await _thuong_viec(kho, ts, v):
        kq.them(d)
    return kq


async def di_viec(kho, ts, rng: random.Random | None = None, hs: dict | None = None) -> KetQua:
    """Lên đường làm việc: trừ diệt hoặc tuần hành."""
    rng = rng or random.Random()
    hs = hs or {}
    dang = await kho.viec_hien_tai(ts.user_id)
    if not dang:
        return KetQua(tieu_de="Không có việc", van=["Ngươi chưa nhận việc nào."], thanh_cong=False)
    v = dl_viecmon.lay(dang["ma"])
    if v is None:
        await kho.xong_viec(ts.user_id)
        return KetQua(tieu_de="Việc đã tan", van=["Không còn ai nhớ tới việc ấy nữa."], thanh_cong=False)
    if ts.dang_bi_thuong:
        return KetQua(tieu_de="Thân này chưa đi được",
                      van=[f"Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa mới bò dậy nổi."], thanh_cong=False)

    if v.loai == "thu_thap":
        return await xem_viec(kho, ts)

    if v.loai == "tru_diet":
        d = dl_dichthu.lay(v.dich)
        kq = await phieuluu.dau_voi_dich(
            kho, ts, d, rng, hs,
            boi_canh="Ngươi tìm tới tận nơi. Không có lời qua tiếng lại nào — hai bên đều biết vì sao mình ở đây.",
        )
        kq.tieu_de = f"Việc tông môn: {v.ten}"
        if kq.du_lieu.get("thang"):
            kq.them("Ngươi mang chứng vật về tông môn.")
            for line in await _thuong_viec(kho, ts, v):
                kq.them(line)
        else:
            kq.them(
                "Việc chưa xong. Ngươi bò về, và không ai hỏi han gì — trong tông môn, "
                "kẻ thất bại tự biết đường im lặng. *Dưỡng thương rồi đi lại.*"
            )
        return kq

    # tuần hành
    chang = int(dang["chang"])
    kq = KetQua(tieu_de=f"{v.ten} — chặng {chang + 1}/{v.so_chang}")
    if chang < len(v.canh_chang):
        kq.them(v.canh_chang[chang])
    else:
        kq.them("Các ngươi đi thêm một quãng nữa. Không có gì xảy ra, và điều đó tự nó là một tin tốt.")

    if rng.random() < 0.30 * hs.get("nguy_hiem", 1.0):
        d = dl_dichthu.ngau_nhien_theo_muc(ts.canh_gioi, rng)
        kq.them("Rồi thứ mà các ngươi vẫn sợ, xuất hiện.")
        kq2 = await phieuluu.dau_voi_dich(kho, ts, d, rng, hs)
        for c in kq2.van:
            kq.them(c)

    chang += 1
    if chang >= v.so_chang:
        kq.them(v.ket or "Việc xong. Ngươi về.")
        for line in await _thuong_viec(kho, ts, v):
            kq.them(line)
    else:
        await kho.tien_chang(ts.user_id, chang)
    await kho.luu(ts)
    return kq
