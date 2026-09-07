"""Diễn tập: chạy thử toàn bộ hệ thống mà không cần Discord.

    python tools/mophong.py            # chạy một vòng đời rút gọn
    CAP_TOC=1 python tools/mophong.py  # bỏ qua thời gian chờ
"""

from __future__ import annotations

import asyncio
import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("CAP_TOC", "1")

from tuchan.db import Kho  # noqa: E402
from tuchan.he import (giaothuong, luyenche, nhanvat, phieuluu, thidau,  # noqa: E402
                       thienbien, tongmon, tuluyen)
from tuchan.he.ketqua import KetQua  # noqa: E402
from tuchan.he.thienco import he_so_the_gioi  # noqa: E402
from tuchan.data import congthuc as dl_congthuc  # noqa: E402


def in_ra(kq: KetQua) -> None:
    print("\n" + "═" * 72)
    print(f"【 {kq.tieu_de} 】" + (f"   〔tranh: {kq.anh}〕" if kq.anh else ""))
    print("─" * 72)
    print(kq.toan_van)


async def main() -> None:
    rng = random.Random(20260906)
    duong = os.path.join(tempfile.mkdtemp(), "dienrap.sqlite3")
    kho = Kho(duong)
    await kho.mo()

    hs = await he_so_the_gioi(kho, 1)
    in_ra(await nhanvat.tao_nhan_vat(kho, 1, 1, "Hàn Lập", "nam", "pham_nhan", rng))
    in_ra(await nhanvat.tao_nhan_vat(kho, 2, 1, "Nam Cung Uyển", "nữ", "the_gia", rng))

    ts = await kho.lay_tu_si(1)
    for _ in range(6):
        kq = await tuluyen.luyen_tap(kho, ts, rng, hs)
    in_ra(kq)
    in_ra(await tuluyen.hap_thu_thien_dia(kho, ts, rng, hs))

    # ép đầy đạo hạnh để thử xung quan
    from tuchan.canhgioi import tu_vi_can_thiet
    ts = await kho.lay_tu_si(1)
    ts.tu_vi = tu_vi_can_thiet(ts.canh_gioi, ts.tang)
    ts.thuong_toi = 0
    await kho.luu(ts)
    in_ra(await tuluyen.dot_pha(kho, ts, rng, hs))

    ts = await kho.lay_tu_si(1)
    ts.thuong_toi = 0
    ts.tang = 6
    await kho.luu(ts)
    in_ra(await tongmon.gia_nhap(kho, ts, "thanh_van", rng))
    in_ra(await phieuluu.kham_pha(kho, ts, rng, hs))
    ts = await kho.lay_tu_si(1)
    ts.thuong_toi = 0
    await kho.luu(ts)
    in_ra(await phieuluu.tim_duoc(kho, ts, rng, hs))
    ts = await kho.lay_tu_si(1)
    ts.thuong_toi = 0
    await kho.luu(ts)
    in_ra(await phieuluu.duy_ky_si(kho, ts, rng, hs))

    # luyện đan: nạp nguyên liệu rồi luyện
    ts = await kho.lay_tu_si(1)
    ts.thuong_toi = 0
    await kho.luu(ts)
    await kho.hoc_cong_thuc(1, "ct_hoi_khi")
    ct = dl_congthuc.lay("ct_hoi_khi")
    for ma, sl in ct.nguyen_lieu.items():
        await kho.them_vat(1, ma, sl * 2)
    in_ra(await luyenche.luyen_dan(kho, ts, "ct_hoi_khi", rng, hs))

    await kho.hoc_cong_thuc(1, "kp_thanh_cuong")
    await kho.them_vat(1, "hac_thiet", 8)
    in_ra(await luyenche.luyen_khi(kho, ts, "kp_thanh_cuong", rng, hs))
    in_ra(await luyenche.deo_phap_bao(kho, ts, "thanh_cuong_kiem"))

    in_ra(await tongmon.nhan_viec(kho, ts, rng))
    in_ra(await tongmon.di_viec(kho, ts, rng, hs))

    in_ra(await giaothuong.xem_hang(kho, ts, hs, rng))
    ts = await kho.lay_tu_si(1)
    ts.linh_thach += 500
    await kho.luu(ts)
    in_ra(await giaothuong.mua(kho, ts, "Hồi Khí Đan", 2, hs))
    in_ra(await giaothuong.ban(kho, ts, "Hoàng Tinh Thảo", 1, hs))

    in_ra(await thienbien.khoi_su_kien(kho, 1, "linh_trieu", rng))
    in_ra(await thienbien.xem_thien_bien(kho, 1))

    a = await kho.lay_tu_si(1)
    b = await kho.lay_tu_si(2)
    a.thuong_toi = 0
    b.thuong_toi = 0
    in_ra(await thidau.thi_dau(kho, a, b, rng, hs))

    in_ra(await nhanvat.xem_nhan_vat(kho, await kho.lay_tu_si(1), hs))
    in_ra(await nhanvat.xem_nhan_vat(kho, await kho.lay_tu_si(2), hs))

    await kho.dong()
    print("\n\n✓ Diễn tập xong, không có lỗi.")


if __name__ == "__main__":
    asyncio.run(main())
