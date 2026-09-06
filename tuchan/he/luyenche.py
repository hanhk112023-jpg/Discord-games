"""Luyện đan và luyện khí — hai nghề mà ai cũng muốn học, và chín phần mười học dở dang."""

from __future__ import annotations

import random

from .. import config
from ..data import congthuc as dl_congthuc
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..vanphong import khac_gio
from .ketqua import KetQua
from .thienco import thanh_bai, van_khi

MO_LO = (
    "Ngươi rửa đan lô ba lượt bằng nước suối, lau khô, rồi mới dám nhóm lửa.",
    "Lửa nhóm lên từ một mồi than cũ. Ngươi ngồi xổm bên lò, quạt từng nhịp, không nhanh không chậm.",
    "Đan lô đặt trên ba viên đá kê. Đáy lò còn vết cháy của những mẻ hỏng lần trước — ngươi không lau chúng đi.",
)

MO_LO_REN = (
    "Ngươi thổi bễ cho tới khi than trong lò chuyển từ đỏ sang trắng.",
    "Búa, đe, một chậu nước, và một đêm dài. Luyện khí không có đường tắt nào cả.",
    "Ngươi vạch phù văn lên nền đất trước, tập tay cho quen, rồi mới dám khắc lên phôi thật.",
)

THAT_BAI_DAN = (
    "Tới lúc thu hoả, trong lò vang một tiếng 'bụp' đục. Ngươi mở nắp: một cục than đen bốc khói khét lẹt. "
    "Bao nhiêu dược liệu, đổi lấy chừng đó khói.",
    "Dược tính cắn nhau. Ngươi thấy khói đổi màu và biết là hỏng, nhưng vẫn cố cứu — "
    "và cố cứu thì hỏng hẳn.",
    "Lửa già nửa phân. Chỉ nửa phân thôi. Khi mở lò, thứ nằm dưới đáy đã dính chặt vào thành, cạy không ra.",
)

THAT_BAI_KHI = (
    "Phôi nứt ngay lúc tôi nước. Tiếng nứt nghe rất nhỏ, nhưng trong lòng ngươi thì nó vang như sấm.",
    "Phù văn khắc lệch một nét ở đường cuối. Cả bộ phù đổ sập, kim loại chảy nhão ra thành một vũng vô dụng.",
    "Vật liệu không chịu được nhiệt. Nó cong lên, xoắn lại, rồi gãy làm đôi trong tay ngươi.",
)


async def luyen_dan(kho, ts, ma_cong_thuc: str, rng: random.Random | None = None,
                    hs: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    ct = dl_congthuc.DAN_PHUONG.get(ma_cong_thuc)
    if ct is None:
        return KetQua(tieu_de="Không có đan phương này",
                      van=["Ngươi lục trong trí nhớ mà không tìm ra thứ gì như vậy."], thanh_cong=False)
    if ma_cong_thuc not in await kho.so_tay(ts.user_id):
        return KetQua(tieu_de="Chưa học",
                      van=[f"**{ct.ten}** — ngươi có nghe tên, nhưng chưa từng đọc một chữ nào của nó. "
                           "Đan phương không phải thứ đoán mò mà ra."], thanh_cong=False)
    con = await kho.con_cho(ts.user_id, "luyendan")
    if con > 0:
        return KetQua(tieu_de="Lò còn nóng",
                      van=[f"Đan lô chưa nguội, thần thức còn mệt. Đợi {khac_gio(con)}."], thanh_cong=False)
    if ts.canh_gioi < ct.canh_gioi_toi_thieu:
        return KetQua(tieu_de="Chưa đủ hoả hầu",
                      van=[f"Muốn khống chế được hoả hầu của **{ct.ten}**, thần thức phải mạnh hơn ngươi bây giờ nhiều. "
                           "Cố thì lò nổ, mà lò nổ thì mặt ngươi lãnh trọn."], thanh_cong=False)
    if not await kho.du_nguyen_lieu(ts.user_id, ct.nguyen_lieu):
        thieu = []
        tui = await kho.tui(ts.user_id)
        for ma, sl in ct.nguyen_lieu.items():
            co = tui.get(ma, 0)
            if co < sl:
                thieu.append(f"{vatpham.ten(ma)} (thiếu {sl - co})")
        return KetQua(tieu_de="Thiếu dược liệu",
                      van=["Ngươi bày hết ra chiếu rồi đếm lại: vẫn thiếu **" + ", ".join(thieu) + "**."],
                      thanh_cong=False)

    await kho.tieu_nguyen_lieu(ts.user_id, ct.nguyen_lieu)
    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    vk = van_khi(rng, ts.dao_tam)
    ti_le = (1.0 - ct.do_kho) * 0.9 + 0.10 * (ts.canh_gioi + 1) * 0.25
    ti_le *= vk * hs.get("dan_thanh", 1.0)
    if mp and mp.ma == "van_duoc":
        ti_le *= 1.35

    kq = KetQua(tieu_de=f"Luyện {vatpham.ten(ct.thanh_pham)}", anh="dan_phong.png", mau=config.MAU_KIM)
    kq.them(rng.choice(MO_LO))
    kq.them(ct.mo_ta)
    kq.them(
        "Dược liệu vào lò theo thứ tự. Khói bốc lên, ban đầu trắng đục, rồi ngả xanh. "
        "Ngươi không dám chớp mắt: hoả hầu sai một nhịp là cả mẻ thành than."
    )

    if thanh_bai(rng, ti_le):
        so = rng.randint(*ct.so_luong)
        await kho.them_vat(ts.user_id, ct.thanh_pham, so)
        vp = vatpham.lay(ct.thanh_pham)
        kq.them(
            f"Ngươi thu hoả. Nắp lò mở ra, một luồng hương xộc lên mũi — thơm, nhưng là cái thơm khiến người ta tỉnh táo. "
            f"Dưới đáy lò: **{vp.ten}**{f' ×{so}' if so > 1 else ''}."
        )
        kq.them(vp.mo_ta)
        if rng.random() < 0.12:
            ts.tu_vi += int(80 * (1 + ts.canh_gioi))
            kq.them(
                "Có một khoảnh khắc trong lúc khống hoả, ngươi hiểu ra một điều về 'độ' — "
                "về chỗ dừng lại. Cái hiểu ấy không chỉ dùng cho luyện đan."
            )
        ts.danh_vong += 2
    else:
        kq.mau = config.MAU_HUYET
        kq.them(rng.choice(THAT_BAI_DAN))
        kq.them(
            "Ngươi ngồi nhìn cái lò một lúc lâu. Rồi ngươi lau nó, cất nó đi, và không nói gì cả. "
            "Đan sư nào cũng có một chồng tro trong quá khứ; khác nhau ở chỗ ai chịu ngồi xuống làm lại."
        )
        if rng.random() < 0.15:
            ts.than_the = max(5, ts.than_the - rng.randint(4, 12))
            kq.them("Lò phụt một luồng lửa tạt qua mặt. Lông mày ngươi cháy sém, da má bỏng rát.")

    await kho.dat_cho(ts.user_id, "luyendan", config.NGUOI_LANH["luyendan"])
    await kho.luu(ts)
    return kq


async def luyen_khi(kho, ts, ma_cong_thuc: str, rng: random.Random | None = None,
                    hs: dict | None = None) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    ct = dl_congthuc.KHI_PHUONG.get(ma_cong_thuc)
    if ct is None:
        return KetQua(tieu_de="Không có đồ hình này",
                      van=["Trong đầu ngươi không có bản vẽ nào như vậy."], thanh_cong=False)
    if ma_cong_thuc not in await kho.so_tay(ts.user_id):
        return KetQua(tieu_de="Chưa học",
                      van=[f"**{ct.ten}** ngươi chưa từng được xem qua. Luyện khí mà không có đồ hình "
                           "thì chỉ là đập sắt cho vui."], thanh_cong=False)
    con = await kho.con_cho(ts.user_id, "luyenkhi")
    if con > 0:
        return KetQua(tieu_de="Tay còn run",
                      van=[f"Cả đêm quai búa, cổ tay ngươi còn run. Đợi {khac_gio(con)}."], thanh_cong=False)
    if ts.canh_gioi < ct.canh_gioi_toi_thieu:
        return KetQua(tieu_de="Chưa đủ sức",
                      van=["Thần thức ngươi chưa đủ để giữ phù văn ổn định trong lửa. Chưa tới lúc."],
                      thanh_cong=False)
    if not await kho.du_nguyen_lieu(ts.user_id, ct.nguyen_lieu):
        tui = await kho.tui(ts.user_id)
        thieu = [f"{vatpham.ten(ma)} (thiếu {sl - tui.get(ma, 0)})"
                 for ma, sl in ct.nguyen_lieu.items() if tui.get(ma, 0) < sl]
        return KetQua(tieu_de="Thiếu vật liệu",
                      van=["Trên đe còn trống một chỗ: **" + ", ".join(thieu) + "**."], thanh_cong=False)

    await kho.tieu_nguyen_lieu(ts.user_id, ct.nguyen_lieu)
    mp = dl_monphai.lay(ts.mon_phai) if ts.mon_phai else None
    vk = van_khi(rng, ts.dao_tam)
    ti_le = (1.0 - ct.do_kho) * 0.92 + 0.08 * (ts.canh_gioi + 1) * 0.3
    ti_le *= vk * hs.get("khi_thanh", 1.0)
    if mp and mp.ma == "huyen_vu":
        ti_le *= 1.2

    kq = KetQua(tieu_de=f"Luyện chế {vatpham.ten(ct.thanh_pham)}", mau=config.MAU_KIM)
    kq.them(rng.choice(MO_LO_REN))
    kq.them(ct.mo_ta)
    kq.them(
        "Tiếng búa vang đều trong đêm. Mỗi nhát là một hơi thở, mỗi hơi thở là một phần chân khí "
        "ngươi rót vào thứ kim loại vô tri kia, mong nó chịu nhận."
    )

    if thanh_bai(rng, ti_le):
        await kho.them_vat(ts.user_id, ct.thanh_pham, 1)
        vp = vatpham.lay(ct.thanh_pham)
        kq.them(
            f"Nhát cuối cùng hạ xuống. Phù văn trên thân vật sáng lên một lượt rồi lặn vào trong. "
            f"**{vp.ten}** đã thành."
        )
        kq.them(vp.mo_ta)
        kq.them(
            "Ngươi cầm nó lên, thử một đường. Nó theo tay ngươi — không hoàn toàn ngoan ngoãn, "
            "nhưng nó đã bắt đầu nhận chủ. *(Muốn mang theo người thì phải đeo nó vào.)*"
        )
        ts.danh_vong += 3
    else:
        kq.mau = config.MAU_HUYET
        kq.them(rng.choice(THAT_BAI_KHI))
        kq.them(
            "Ngươi nhặt mảnh vỡ lên, xem xét chỗ gãy rất lâu, rồi ném vào góc. "
            "Trong góc ấy đã có mấy mảnh như thế rồi."
        )
        if rng.random() < 0.2:
            ts.than_the = max(5, ts.than_the - rng.randint(3, 10))
            kq.them("Một mảnh kim loại nóng bắn ra găm vào cánh tay ngươi. Ngươi rút nó ra, không kêu.")

    await kho.dat_cho(ts.user_id, "luyenkhi", config.NGUOI_LANH["luyenkhi"])
    await kho.luu(ts)
    return kq


async def deo_phap_bao(kho, ts, ma: str) -> KetQua:
    vp = vatpham.lay(ma)
    if vp is None or vp.loai != "phap_bao":
        return KetQua(tieu_de="Không phải pháp bảo",
                      van=["Thứ đó không phải là vật để mang ra trận."], thanh_cong=False)
    if await kho.dem_vat(ts.user_id, ma) <= 0:
        return KetQua(tieu_de="Không có trong tay",
                      van=[f"Ngươi không có **{vp.ten}**."], thanh_cong=False)
    if ts.canh_gioi < vp.canh_gioi_toi_thieu:
        return KetQua(
            tieu_de="Không kham nổi",
            van=[f"**{vp.ten}** nặng hơn thứ ngươi gánh được. Vừa dẫn chân khí vào, "
                 "nó đã hút ngược lại làm ngươi tối sầm mặt mũi. Vật này chê chủ."],
            thanh_cong=False)
    cu = ts.phap_bao
    ts.phap_bao = ma
    await kho.luu(ts)
    kq = KetQua(tieu_de="Nhận chủ")
    if cu and cu != ma:
        kq.them(f"Ngươi thu **{vatpham.ten(cu)}** vào túi càn khôn, không phải vì nó dở, mà vì hôm nay ngươi cần thứ khác.")
    kq.them(
        f"Ngươi cắn đầu ngón tay, nhỏ một giọt tinh huyết lên **{vp.ten}**. "
        "Giọt máu không chảy xuống — nó thấm vào, mất hút. Vật ấy rung lên một cái rất khẽ, như đáp lời."
    )
    kq.them(vp.mo_ta)
    return kq


async def uong_dan(kho, ts, ma: str, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    vp = vatpham.lay(ma)
    if vp is None or vp.loai != "dan_duoc":
        return KetQua(tieu_de="Không phải đan dược",
                      van=["Thứ đó mà nuốt vào thì đúng là ngươi đã chán sống."], thanh_cong=False)
    if not await kho.bot_vat(ts.user_id, ma, 1):
        return KetQua(tieu_de="Không có", van=[f"Trong túi không có **{vp.ten}**."], thanh_cong=False)

    kq = KetQua(tieu_de=f"Dùng {vp.ten}")
    kq.them(f"Ngươi đặt **{vp.ten}** lên lưỡi. {vp.mo_ta}")
    hq = vp.hieu_qua
    if "tri_thuong" in hq:
        ts.than_the = min(100, ts.than_the + int(hq["tri_thuong"]))
        ts.thuong_toi = 0
        kq.them(
            "Một luồng ấm chạy dọc kinh mạch, tìm tới từng chỗ rách mà vá lại. "
            "Ngươi ngồi im, mồ hôi túa ra như tắm, và khi mở mắt thì cơn đau đã lùi xuống thành một tiếng thì thầm."
        )
    if "tu_vi" in hq:
        ts.tu_vi += int(hq["tu_vi"])
        kq.them(
            "Dược lực tan trong đan điền như tuyết gặp lửa. Chân khí dày lên thấy rõ — "
            "nhưng đan dược cho ngươi lượng, không cho ngươi hiểu. Phần hiểu, vẫn phải tự ngồi mà lấy."
        )
    if "dao_tam" in hq:
        ts.dao_tam = min(100, ts.dao_tam + int(hq["dao_tam"]))
        kq.them("Tạp niệm lắng xuống. Trong đầu chỉ còn một khoảng trống rất sạch, và ngươi thở ra rất chậm.")
    if "sat_nghiep" in hq:
        ts.sat_nghiep += int(hq["sat_nghiep"])
        kq.them("Có thứ gì đó trong đó không thuộc về ngươi, và nó vừa đi vào máu ngươi.")
    if "can_cot" in hq:
        ts.can_cot += 0.05
        kq.them("Xương cốt kêu răng rắc suốt một canh giờ. Khi ngừng, ngươi thấy mình... chắc hơn.")
    if "dot_pha" in hq:
        kq.them(
            "*Loại đan này chỉ phát huy tác dụng khi dùng ngay trong lúc xung quan. "
            "Nuốt suông thế này thì dược lực tản đi quá nửa — lần sau, hãy dùng nó đúng lúc.*"
        )
    await kho.luu(ts)
    return kq
