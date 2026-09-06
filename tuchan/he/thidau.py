"""Thí đấu giữa hai người tu hành. Có loại điểm tới là dừng, có loại thì không."""

from __future__ import annotations

import random
import time

from .. import config
from ..canhgioi import ten_canh_gioi
from ..data import monphai as dl_monphai
from ..vanphong import khac_gio
from . import chiendau
from .ketqua import KetQua
from .phieuluu import ben_tu_nguoi_choi

BOI_CANH = (
    "Hai người chọn một khoảng đất trống sau núi, nơi cỏ đã bị dẫm nát bởi những kẻ tới trước.",
    "Trên đài đá xanh trước Diễn Võ Trường, mấy đệ tử ngoại môn đứng vòng ngoài, không ai dám bàn tán to.",
    "Bên bờ suối cạn, trời sắp mưa. Cả hai đều muốn xong trước khi hạt đầu tiên rơi xuống.",
    "Trong sân sau một tửu điếm, dưới ánh đèn lồng đỏ. Chủ quán đóng cửa, không phải vì sợ, mà vì quen.",
)

LOI_MO = (
    "{a} chắp tay: *“Xin chỉ giáo.”* {b} không đáp, chỉ nhấc cằm lên một chút.",
    "{b} nói, giọng bình thản: *“Ngươi chắc chứ?”* {a} không trả lời — câu trả lời nằm ở chỗ {a} vẫn đứng đó.",
    "Không ai chào ai. Trong giang hồ, lễ nghĩa nhiều khi chỉ là cách kéo dài thời gian.",
)


async def thi_dau(kho, a_ts, b_ts, rng: random.Random | None = None, hs: dict | None = None,
                  sinh_tu: bool = False) -> KetQua:
    rng = rng or random.Random()
    hs = hs or {}
    a = ben_tu_nguoi_choi(a_ts)
    b = ben_tu_nguoi_choi(b_ts)

    boi_canh = rng.choice(BOI_CANH)
    td = chiendau.giao_dau(a, b, rng)

    kq = KetQua(tieu_de=f"{a_ts.ten} đấu {b_ts.ten}", anh="dau_phap.png", mau=config.MAU_HUYET)
    kq.them(
        f"**{a_ts.ten}** — {ten_canh_gioi(a_ts.canh_gioi, a_ts.tang)}"
        + (f", đệ tử {dl_monphai.lay(a_ts.mon_phai).ten}" if dl_monphai.lay(a_ts.mon_phai or "") else ", tán tu")
        + f".\n**{b_ts.ten}** — {ten_canh_gioi(b_ts.canh_gioi, b_ts.tang)}"
        + (f", đệ tử {dl_monphai.lay(b_ts.mon_phai).ten}" if dl_monphai.lay(b_ts.mon_phai or "") else ", tán tu")
        + "."
    )
    kq.them(boi_canh)
    kq.them(rng.choice(LOI_MO).format(a=a_ts.ten, b=b_ts.ten))
    for c in td.van:
        kq.them(c)

    thang_ts = a_ts if td.thang is a else b_ts
    thua_ts = b_ts if td.thang is a else a_ts

    thang_ts.so_tran_thang += 1
    thua_ts.so_tran_thua += 1
    thuong = int(6 + 16 * (td.ap_dao - 0.5) * 2)
    cach_bac = thua_ts.canh_gioi - thang_ts.canh_gioi
    thang_ts.danh_vong += max(2, thuong * (1 + max(0, cach_bac) * 2))
    thua_ts.danh_vong = max(0, thua_ts.danh_vong - max(1, thuong // 2))

    ton = int(td.ton_thuong_ke_thua * (1.0 if sinh_tu else 0.55))
    thua_ts.than_the = max(1, thua_ts.than_the - ton)
    thua_ts.thuong_toi = int(time.time()) + int(
        config.DUONG_THUONG_TOI_DA * (0.5 if sinh_tu else 0.25) * (0.5 + td.ap_dao)
    )

    if sinh_tu:
        thang_ts.sat_nghiep += 3
        thang_ts.dao_tam = max(3, thang_ts.dao_tam - 2)
        if td.chi_mang and rng.random() < 0.5:
            thua_ts.da_chet = 1
            kq.them(
                f"**{thang_ts.ten} không thu tay.**\n\n"
                f"{thua_ts.ten} nằm đó, mắt còn mở, nhìn về một chỗ nào đó rất xa. "
                "Đây là sinh tử chiến — hai bên đã ký vào giấy, và giấy thì không biết thương ai. "
                "Người xem lặng lẽ tản đi. Sẽ có kẻ kể lại chuyện này, thêm thắt vài phần, "
                "và cái tên vừa tắt sẽ sống thêm được ít lâu trong miệng thiên hạ."
            )
        else:
            kq.them(
                f"{thang_ts.ten} dừng lại ở nhát cuối, đứng thở, rồi quay đi. "
                "Không phải nhân từ — chỉ là hôm nay {0} không muốn thêm một cái tên vào giấc ngủ của mình.".format(thang_ts.ten)
            )
    else:
        kq.them(
            f"**{thang_ts.ten}** thu thế, chắp tay. **{thua_ts.ten}** chống gối đứng dậy, "
            "gạt máu ở khoé miệng, cũng chắp tay đáp lễ. Tỉ thí điểm tới là dừng — "
            "nhưng vết thương thì không biết đó là quy củ."
        )

    kq.them(chiendau.loi_binh(td, a))
    kq.them(
        f"*{thua_ts.ten} sẽ cần {khac_gio(thua_ts.con_bao_lau_duong_thuong)} để dưỡng thương.*"
    )

    await kho.luu(a_ts)
    await kho.luu(b_ts)
    await kho.chep(a_ts.user_id, "thi_dau", f"{a_ts.ten} đấu {b_ts.ten}: {thang_ts.ten} thắng.")
    await kho.chep(b_ts.user_id, "thi_dau", f"{b_ts.ten} đấu {a_ts.ten}: {thang_ts.ten} thắng.")
    kq.du_lieu["thang"] = thang_ts.user_id
    return kq
