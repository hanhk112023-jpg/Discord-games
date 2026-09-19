"""Bảy ải huyễn cảnh cá nhân, dùng chung bộ máy giao đấu và sổ nhân vật.

Đây là bóng chiếu của yêu vương, không phải boss thế giới. Thưởng mỗi ải một lần
mỗi kiếp; không thể bỏ qua ải hoặc tự khai chiến lợi phẩm từ trình duyệt.
"""
from __future__ import annotations

import json
import random
from dataclasses import replace

from .. import config
from ..canhgioi import ten_canh_gioi
from ..data.boss import DANH_SACH
from .chiendau import giao_dau
from .dauboss import ben_boss
from .phieuluu import ben_tu_nguoi_choi
from .ketqua import KetQua

# Ải nhập môn là bóng chiếu yếu hơn yêu vương thật, vừa sức người mới nhập đạo.
AI = [replace(b, canh_gioi=i, tang=1, tho=0.65 if i == 0 else 1.0)
      for i, b in enumerate(DANH_SACH)]
ANH = ["tru_vuong.jpg", "xa_vuong.jpg", "bach_cot.jpg", "giao_long.jpg",
       "huyet_ma.jpg", "loi_thu.jpg", "cuu_u_vuong.jpg"]
THUONG = ["hoi_khi_dan", "thanh_cuong_kiem", "yeu_dan", "u_dam_lien",
          "long_van_ngoc", "lac_lo_tinh_kim", "do_ach_dan"]


def tien_do(ts) -> int:
    if ts is None:
        return 0
    return max(0, min(len(AI), int(json.loads(ts.ghi_chu).get("bi_canh", 0))))


async def vuot_ai(kho, ts, ma: str, rng: random.Random | None = None) -> KetQua:
    rng = rng or random.Random()
    index = next((i for i, b in enumerate(AI) if b.ma == ma), -1)
    da_qua = tien_do(ts)
    if index < 0 or index != da_qua:
        return KetQua(tieu_de="Cửa ải chưa mở", van=["Đi lần lượt từng ải. Chiến lợi phẩm của ải đã qua chỉ nhận một lần."], thanh_cong=False)
    boss = AI[index]
    if ts.da_chet or ts.dang_bi_thuong or ts.than_the < 20:
        return KetQua(tieu_de="Cần dưỡng thương", van=["Trở về động phủ dưỡng thương trước khi bước vào huyễn cảnh."], thanh_cong=False)
    if ts.canh_gioi < boss.canh_gioi:
        return KetQua(tieu_de="Chưa đủ cảnh giới", van=[f"Ải này cần {ten_canh_gioi(boss.canh_gioi, 1)}."], thanh_cong=False)
    con = await kho.con_cho(ts.user_id, "bicanh")
    if con:
        return KetQua(tieu_de="Kiếm khí chưa hồi", van=[f"Hãy nghỉ thêm {con} giây rồi thử lại."], thanh_cong=False)
    a, b = ben_tu_nguoi_choi(ts), ben_boss(boss)
    tran = giao_dau(a, b, rng, so_hiep=4)
    thang = tran.thang is a
    kq = KetQua(tieu_de="Phá ải thành công" if thang else "Huyễn cảnh chưa phục",
                van=tran.van, thanh_cong=thang,
                anh=ANH[index])
    if thang:
        ghi = json.loads(ts.ghi_chu)
        ghi["bi_canh"] = index + 1
        ts.ghi_chu = json.dumps(ghi, ensure_ascii=False)
        ts.linh_thach += 50 * (index + 1)
        ts.danh_vong += 5 * (index + 1)
        kq.them("Bóng yêu vương tan thành ánh sáng. Chiến lợi phẩm đã vào túi càn khôn. "
                + ("Thất ải viên mãn — ngươi đã vượt hết bảy bóng yêu vương." if index == len(AI) - 1
                   else "Cửa ải tiếp theo hé mở, chờ ngươi đạt đủ cảnh giới."))
    else:
        ts.than_the = max(1, ts.than_the - min(20, tran.ton_thuong_ke_thua))
        kq.them("Pháp trận đưa ngươi ra ngoài. Dưỡng thương, tu luyện rồi hãy quay lại; thất bại không làm mất tiến độ.")
    await kho.luu_bi_canh(ts, THUONG[index] if thang else None, config._giay(60),
                          f"{boss.ten}: {'vượt ải' if thang else 'thất bại'}")
    return kq
