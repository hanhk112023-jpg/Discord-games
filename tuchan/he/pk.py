"""PK — luật giang hồ có người làm chứng.

Thách đấu treo thành một lời hứa: bên được thách phải đích thân ứng chiến, quá hạn
thì coi như khước từ — và thiên hạ sẽ nhớ. Có thể đặt cược linh thạch; hai bên cùng
đặt, kẻ thắng ăn cả. Tội gì cũng có giá của nó: thắng một kẻ hơn mình hai bậc
đáng giá hơn mười trận bắt nạt hậu bối.
"""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import ten_canh_gioi
from ..vanphong import khac_gio
from .ketqua import KetQua
from .thidau import thi_dau


# ───────────────────────── gửi lời thách ─────────────────────────

async def thach_thuc(kho, ts_a, ts_b, cuoc: int = 0, sinh_tu: bool = False) -> tuple[int, KetQua]:
    """Tạo một lời thách treo. Trả về (mã thách, KetQua để đưa cho bên được thách)."""
    cuoc = max(0, int(cuoc or 0))
    if ts_b.da_chet:
        return 0, KetQua(tieu_de="Không thách được",
                         van=[f"**{ts_b.ten}** đã chết. Đấu với người chết thì chỉ có thầy đồng nhận lời."],
                         thanh_cong=False)
    if ts_a.da_chet:
        return 0, KetQua(tieu_de="Chính ngươi còn chưa xong",
                         van=["Kẻ còn nằm dưới ba thước đất thì cất giọng ở đâu ra."],
                         thanh_cong=False)
    if ts_a.dang_bi_thuong:
        return 0, KetQua(tieu_de="Thương chưa lành",
                         van=[f"Đã mang thương mà còn đi thách người — giang hồ gọi đó là tìm chỗ chết có nhân chứng. "
                              f"Đợi {khac_gio(ts_a.con_bao_lau_duong_thuong)} nữa đã."],
                         thanh_cong=False)
    if ts_b.dang_bi_thuong:
        return 0, KetQua(tieu_de="Đối phương đang dưỡng thương",
                         van=[f"Lúc này mà đánh **{ts_b.ten}** thì không gọi là tỉ thí, mà gọi là hành hình. "
                              "Danh vọng kiếm kiểu đó không dùng được."],
                         thanh_cong=False)
    if ts_a.linh_thach < cuoc:
        return 0, KetQua(tieu_de="Cược không nổi",
                         van=["Ngươi vừa đặt một số tiền lớn hơn cả túi. "
                             "Chủ quỹ của giang hồ không nhận séc."],
                         thanh_cong=False)
    if ts_b.linh_thach < cuoc:
        return 0, KetQua(tieu_de="Hắn cược không nổi",
                         van=[f"**{ts_b.ten}** dốc túi ra cũng không đủ số ấy. "
                              "Đặt cược là để hai bên cùng dứt khoát, không phải để ép nhau bán nhà."],
                         thanh_cong=False)

    ma = await kho.thach_tao(ts_a.guild_id, ts_a.user_id, ts_a.ten, ts_b.user_id, ts_b.ten,
                             cuoc, sinh_tu)
    cach = ts_b.canh_gioi - ts_a.canh_gioi
    loi = (f"*\"{ts_a.ten} muốn thỉnh giáo {ts_b.ten}. Điểm tới là dừng.\"*" if not sinh_tu else
           f"*\"{ts_a.ten} muốn lấy mạng {ts_b.ten}. Sinh tử chiến — hai bên đã nói ra lời, không ai được rút.\"*")
    kq = KetQua(tieu_de="Lời thách treo giữa sân", mau=config.MAU_HUYET if sinh_tu else config.MAU_MUC,
                anh="dau_phap.png")
    kq.them(
        f"**{ts_a.ten}** — {ten_canh_gioi(ts_a.canh_gioi, ts_a.tang)} — bước ra giữa sân, "
        f"chắp tay về phía **{ts_b.ten}** — {ten_canh_gioi(ts_b.canh_gioi, ts_b.tang)}."
        + (" *Hắn nhắm kẻ trên mình một bậc — kẻ đứng xem bắt đầu kiểm lại gia sản hộ hắn.*"
           if cach > 0 else "")
    )
    kq.them(loi)
    if cuoc:
        kq.them(f"Trên đài bày ra **{cuoc} linh thạch** phần của ngươi. Bên kia đặt lại đúng ngần ấy "
                "thì trận này mới đánh được — kẻ thắng ăn cả, đó là lệ chợ.")
    kq.them("*Lời thách có hiệu lực trong một thời gian ngắn. Không ứng chiến thì coi như khước từ — "
            "khước từ thì không mất gì, trừ một hai kẻ sẽ nhắc lại chuyện này lúc ngươi vắng mặt.*")
    kq.du_lieu["thach_ma"] = ma
    return ma, kq


# ───────────────────────── ứng chiến / khước từ / huỷ ─────────────────────────

async def ung_chien(kho, ma_thach: int, ts_b, rng: random.Random | None = None,
                    hs: dict | None = None) -> KetQua:
    """Bên được thách bấm nút. Đánh thật, thu xếp tiền cược luôn."""
    rng = rng or random.Random()
    hs = hs or {}
    thach = await kho.thach_lay(ma_thach)
    if not thach or thach["b_id"] != ts_b.user_id:
        return KetQua(tieu_de="Lời thách không còn",
                      van=["Sân đã vắng người. Chuyện cũ thì thôi bỏ qua."], thanh_cong=False)
    ts_a = await kho.lay_tu_si(thach["a_id"])
    if ts_a is None or ts_a.da_chet or ts_b.da_chet:
        await kho.thach_xoa(ma_thach)
        return KetQua(tieu_de="Một bên đã không còn ở đây",
                      van=["Có kẻ đổi lời hứa bằng một nấm mồ. Trận này treo tới bao giờ?"],
                      thanh_cong=False)
    for ben in (ts_a, ts_b):
        if await kho.con_cho(ben.user_id, "thidau") > 0:
            return KetQua(tieu_de="Chưa tới giờ",
                          van=[f"Vừa động võ xong, hơi còn chưa đều. "
                               f"*{ben.ten}* cần nghỉ thêm {khac_gio(await kho.con_cho(ben.user_id, 'thidau'))}."],
                          thanh_cong=False)
        if ben.dang_bi_thuong:
            return KetQua(tieu_de="Thương chưa lành",
                          van=[f"**{ben.ten}** đang dưỡng thương; hai bên đã hứa điểm tới là dừng, "
                               "đánh bây giờ thì thành ra tận diệt. Đợt khác."],
                          thanh_cong=False)

    await kho.thach_xoa(ma_thach)
    cuoc = int(thach["cuoc"] or 0)
    sinh_tu = bool(thach["sinh_tu"])

    if cuoc:
        ts_a.linh_thach -= cuoc
        ts_b.linh_thach -= cuoc
        await kho.luu(ts_a)
        await kho.luu(ts_b)

    kq = await thi_dau(kho, ts_a, ts_b, rng, hs, sinh_tu=sinh_tu)
    kq.tieu_de = ("Sinh tử đài — " if sinh_tu else "Đài tỉ thí — ") + kq.tieu_de

    if cuoc:
        thang_id = kq.du_lieu.get("thang")
        if thang_id == ts_a.user_id:
            ts_a.linh_thach += 2 * cuoc
            await kho.luu(ts_a)
            ket = ts_a
        else:
            ts_b.linh_thach += 2 * cuoc
            await kho.luu(ts_b)
            ket = ts_b
        kq.them(
            f"Chủ quỹ đẩy {2 * cuoc} linh thạch sang phía **{ket.ten}** không nói một lời. "
            "Tiền thắng bằng mạng hay bằng đòn thì tiêu cũng chẳng thấy nặng tay hơn."
        )

    cho = config.NGUOI_LANH["thidau"]
    await kho.dat_cho(ts_a.user_id, "thidau", cho)
    await kho.dat_cho(ts_b.user_id, "thidau", cho)
    return kq


async def tu_khuoc(kho, ma_thach: int, ts_b) -> KetQua:
    thach = await kho.thach_lay(ma_thach)
    if not thach or thach["b_id"] != ts_b.user_id:
        return KetQua(tieu_de="Lời thách không còn", van=["Chuyện cũ rồi."], thanh_cong=False)
    await kho.thach_xoa(ma_thach)
    ts_b.dao_tam = max(3, ts_b.dao_tam - 1)
    await kho.luu(ts_b)
    await kho.chep(ts_b.user_id, "thi_dau", f"Khước từ lời thách của {thach['a_ten']}.")
    return KetQua(
        tieu_de="Lời thách rơi xuống đất",
        van=[f"**{ts_b.ten}** chắp tay: *\"Hôm nay không tiện.\"*\n\n"
             "Từ chối một lời thách không phải là hèn. Trong giang hồ, kẻ biết lúc nào nên đánh "
             "thường sống lâu hơn kẻ lúc nào cũng dám đánh. Chỉ có điều cái câu 'không tiện' ấy "
             "sẽ đi theo ngươi vài ba năm, trong mấy cái nhìn quá lâu của người lạ."],
        mau=config.MAU_MUC)


async def huy_thach(kho, ma_thach: int, ts_a) -> KetQua:
    thach = await kho.thach_lay(ma_thach)
    if not thach or thach["a_id"] != ts_a.user_id:
        return KetQua(tieu_de="Không có gì để rút", van=["Lời ấy không còn treo ở đâu cả."],
                      thanh_cong=False)
    await kho.thach_xoa(ma_thach)
    ts_a.dao_tam = max(3, ts_a.dao_tam - 1)
    await kho.luu(ts_a)
    return KetQua(tieu_de="Rút lời",
                  van=[f"*{ts_a.ten}* cất lại lời đã buông. Ném lời xuống rồi nhặt lên — "
                       "động tác ấy thiên hạ thấy hết."])


async def ru_het_han(kho) -> list[dict]:
    """Những lời thách quá hạn — trả về để còn than phiền."""
    return await kho.thach_het_gio()


# ───────────────────────── bảng PK ─────────────────────────

_TU = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")
_HO = ("lẻ", "mười", "hai mươi", "ba mươi", "bốn mươi", "năm mươi",
       "sáu mươi", "bảy mươi", "tám mươi", "chín mươi")


def so_chu(n: int) -> str:
    """Số trận thì kể bằng miệng người xưa cho phải phép."""
    n = max(0, int(n))
    if n < 10:
        return _TU[n]
    if n < 20:
        return "mười" if n == 10 else "mười " + _TU[n - 10]
    chuc, le = divmod(n, 10)
    if chuc > 9:
        return str(n)
    if le == 0:
        return _HO[chuc]
    if le == 1:
        return _HO[chuc] + " mốt"
    if le == 5:
        return _HO[chuc] + " lăm"
    return _HO[chuc] + " " + _TU[le]


async def bang_pk(kho, ts=None) -> KetQua:
    ds = await kho.bang_danh_vong(12)
    kq = KetQua(tieu_de="Bảng tỉ thí giang hồ")
    if not ds:
        kq.them("Chưa có ai đáng nhắc tên. Đài đá dưới núi vẫn còn nguyên rêu.")
        return kq
    dong = []
    for i, t in enumerate(ds, 1):
        th, td_ = t.so_tran_thang, t.so_tran_thua
        if t.da_chet:
            ket = "đã khuất"
        elif td_ == 0 and th >= 3:
            ket = f"{so_chu(th)} trận, **bất bại**"
        elif th == 0 and td_ == 0:
            ket = "chưa từng lên đài"
        else:
            ket = f"{so_chu(th)} thắng, {so_chu(td_)} bại"
        boss = int(t.ghi().get("boss_ha", 0))
        them = f", hạ {so_chu(boss)} yêu vương" if boss > 0 else ""
        dong.append(f"**{i}. {t.ten}** — {ten_canh_gioi(t.canh_gioi, t.tang)} — {ket}{them}")
    kq.them("\n".join(dong))
    kq.them("Đứng đầu bảng không có nghĩa là sống lâu nhất. Thường thì ngược lại.")
    if ts is not None:
        hang = next((i for i, t in enumerate(ds, 1) if t.user_id == ts.user_id), None)
        if hang is None and ts.so_tran_thang + ts.so_tran_thua > 0:
            kq.them("*Tên ngươi chưa vào bảng. Vào bằng máu cũng được, vào bằng tiếng cũng xong — "
                    "chỉ có đứng ngoài bảng thì đừng.*")
        elif hang:
            kq.them(f"*Hiện ngươi đứng thứ {so_chu(hang)}. Kẻ đứng trên đang chờ ngươi, hoặc đã quên ngươi.*")
    return kq


async def danh_sach_thach(kho, ts) -> KetQua:
    cho, gui = await kho.thach_cua_toi(ts.user_id)
    kq = KetQua(tieu_de="Những lời thách còn treo")
    if not cho and not gui:
        kq.them("Không có gì treo trên đầu ngươi. Bình yên — tạm thời.")
        return kq
    if cho:
        now = int(time.time())
        dong = []
        for x in cho:
            con = max(1, config.THACH_THOI_HAN - (now - int(x["luc"])))
            dong.append(
                f"— **{x['a_ten']}** thách {x['b_ten']}"
                + (f", cược {x['cuoc']} linh thạch" if x["cuoc"] else "")
                + (" — *có đặt mạng*" if x["sinh_tu"] else "")
                + f" *(còn hạn {khac_gio(con)})*"
            )
        kq.them("**Người ta chờ ngươi trả lời:**\n" + "\n".join(dong))
    if gui:
        dong = [f"— ngươi thách **{x['b_ten']}**"
                + (f", cược {x['cuoc']} linh thạch" if x["cuoc"] else "")
                + (" — *sinh tử*" if x["sinh_tu"] else "")
                for x in gui]
        kq.them("**Ngươi đã buông lời, đang chờ:**\n" + "\n".join(dong))
    return kq
