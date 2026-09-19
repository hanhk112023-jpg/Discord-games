#!/usr/bin/env python3
"""Diễn tập bot Telegram ngay trong terminal — không cần token, không cần mạng.

    python tools/tele_thutap.py            # chơi bằng bàn phím
    python tools/tele_thutap.py --tu-dong  # tự chạy một kịch bản trình diễn

Lệnh gõ vào dùng hệt như trong Telegram: /menu, /dangky, /pk Hàn Lập 500, /boss…
Nút bấm của tin nhắn cuối liệt kê ở dạng [1] [2]… — g `~3` để bấm nút thứ 3.
"""

from __future__ import annotations

import asyncio
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "thutap.sqlite3"))
if "--tu-dong" in sys.argv:
    os.environ.setdefault("HE_SO_THOI_GIAN", "0.0008")   # một canh giờ còn ~7 giây

from tuchan.db import Kho                          # noqa: E402
from tuchan.tele.hien_thi import Trang             # noqa: E402
from tuchan.tele.long import Lo, Long, TinDen       # noqa: E402

TEN_MAU = "Hàn Lập"
CHAT = 1


def bo_tag(html: str) -> str:
    s = re.sub(r"<b>(.*?)</b>", r"\1", html, flags=re.S)
    s = re.sub(r"<i>(.*?)</i>", lambda m: f"*{m.group(1)}*", s, flags=re.S)
    s = re.sub(r"<code>(.*?)</code>", r"`\1`", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return s


class LoTerminal(Lo):
    def __init__(self):
        self.nut_cuoi: list[tuple[str, str]] = []

    async def gui(self, chat_id: int, trang: Trang):
        if trang.anh:
            print(f"      🖼  [assets/tranh/{trang.anh}]")
        if trang.phim:
            print(f"      🎬  [assets/thanh_anh/{trang.phim}]")
        print(bo_tag(trang.html))
        self.nut_cuoi = []
        if trang.hang:
            for row in trang.hang:
                for label, cb in row:
                    self.nut_cuoi.append((label, cb))
            if self.nut_cuoi:
                print("  " + "   ".join(f"[{i+1}] {l}" for i, (l, _c) in enumerate(self.nut_cuoi)))
        print("─" * 72)

    async def sua(self, chat_id, msg_id, trang: Trang):
        print("(sửa tin nhắn:) " + bo_tag(trang.html))
        self.nut_cuoi = [n for r in (trang.hang or []) for n in r]

    async def doi_uid(self, chat_id: int, uid: int):
        global UID
        UID = uid
        print(f"  (đang nhìn bằng mắt uid={uid})")


async def nhap_lenh(core: Long, lo: LoTerminal, text: str, uid: int):
    tin = TinDen(user_id=uid, chat_id=CHAT, ten="kẻ thử võ",
                 loai="lenh" if text.startswith("/") else "text", data=text, msg_id=None)
    await core.xu_ly(tin)


async def tu_dong() -> int:
    """Kịch bản trình diễn: hai tu sĩ, một con boss, một canh bạc PK."""
    ok = True
    loi = []

    def kiem_tra(ten_kiem, dieu_kien):
        nonlocal ok
        if not dieu_kien:
            ok = False
            loi.append(ten_kiem)
        print(f"  {'✔' if dieu_kien else '✘'} {ten_kiem}")

    kho = Kho()
    await kho.mo()
    # dọn chiếu
    for uid in (111, 222):
        await kho.xoa_tu_si(uid)
    await kho.boss_xoa(1)

    lo = LoTerminal()
    rng = random.Random(777)
    core = Long(kho, 1, lo, rng=rng, thu_duyen=True)

    print("\n════ NHẬP ĐẠO ════")
    await nhap_lenh(core, lo, "/dangky Hàn Lập", 111)
    await core._xu_ly_nut(TinDen(111, CHAT, "Hàn Lập", "cb", "xt:pham_nhan"))
    await core._xu_ly_nut(TinDen(111, CHAT, "Hàn Lập", "cb", "gt:nam"))
    await nhap_lenh(core, lo, "Hàn Lập", 111)
    ts1 = await kho.lay_tu_si(111)
    kiem_tra("Hàn Lập có tên trong sổ", ts1 is not None and ts1.ten == "Hàn Lập")

    await nhap_lenh(core, lo, "/dangky Thạch Tiểu Tiên", 222)
    await core._xu_ly_nut(TinDen(222, CHAT, "Tiểu Tiên", "cb", "xt:tan_tu"))
    await core._xu_ly_nut(TinDen(222, CHAT, "Tiểu Tiên", "cb", "gt:nu"))
    await nhap_lenh(core, lo, "Thạch Tiểu Tiên", 222)
    ts2 = await kho.lay_tu_si(222)
    kiem_tra("Thạch Tiểu Tiên có tên trong sổ", ts2 is not None and ts2.gioi_tinh == "nữ")

    print("\n════ TU LUYỆN ════")
    for _ in range(3):
        await nhap_lenh(core, lo, "/luyentap", 111)
        ts1 = await kho.lay_tu_si(111)
        if ts1.tu_vi < 300:
            await asyncio.sleep(1.2)
    ts1 = await kho.lay_tu_si(111)
    kiem_tra("đạo hạnh đã tích được (tu_vi>0)", ts1.tu_vi > 0)
    await nhap_lenh(core, lo, "/nhanvat", 111)
    await nhap_lenh(core, lo, "/kp", 111)

    print("\n════ BOSS ════")
    await nhap_lenh(core, lo, "/trieuboss Thiết Nha", 111)
    hien = await kho.boss_lay(1)
    kiem_tra("boss đã hiện thế", hien is not None)
    if hien:
        tv_truoc = (await kho.lay_tu_si(111)).tu_vi
        vong = 0
        ha_xong = False
        while vong < 90 and not ha_xong:
            vong += 1
            for uid in (111, 222):
                ts_i = await kho.lay_tu_si(uid)
                if ts_i is None or ts_i.dang_bi_thuong or ts_i.than_the < 45:
                    await nhap_lenh(core, lo, "/duongthuong", uid)   # nằm chờ cho liền xương
                    continue
                await core._xu_ly_nut(TinDen(uid, CHAT, "x", "cb", "bs:go"))
            if await kho.boss_lay(1) is None:
                ha_xong = True
            else:
                await asyncio.sleep(0.7)
        kiem_tra(f"boss đã bị hạ sau {vong} vòng chia công", ha_xong)
        ts1 = await kho.lay_tu_si(111)
        kiem_tra("kẻ tham chiến nhận đạo hạnh", ts1.tu_vi > tv_truoc)
        nk = await kho.doc_nhat_ky(111, 30)
        kiem_tra("có dòng 'Hạ' trong thủ ký", any("Hạ" in x["noi_dung"] for x in nk))

    print("\n════ PK CÓ CƯỢC ════")
    cho_den_luc = 0
    while cho_den_luc < 20:
        t1, t2 = await kho.lay_tu_si(111), await kho.lay_tu_si(222)
        if not t1.dang_bi_thuong and not t2.dang_bi_thuong:
            break
        await asyncio.sleep(1.0)
        cho_den_luc += 1
    ts2 = await kho.lay_tu_si(222)
    cuoc = 5
    gia_vao = max(ts2.linh_thach, cuoc)
    ts2.linh_thach = gia_vao
    await kho.luu(ts2)
    ts1 = await kho.lay_tu_si(111)
    ts1.linh_thach = max(ts1.linh_thach, cuoc + 10)
    await kho.luu(ts1)
    lt1, lt2 = ts1.linh_thach, ts2.linh_thach
    await nhap_lenh(core, lo, f"/pk Thạch 5", 111)
    cho = (await kho.thach_cua_toi(222))[0]
    kiem_tra("lời thách đã treo", len(cho) == 1)
    if cho:
        ma = cho[0]["id"]
        await core._xu_ly_nut(TinDen(222, CHAT, "Tiểu Tiên", "cb", f"pk:y:{ma}"))
        ts1 = await kho.lay_tu_si(111)
        ts2 = await kho.lay_tu_si(222)
        tong_truoc = lt1 + lt2
        tong_sau = ts1.linh_thach + ts2.linh_thach
        kiem_tra("tiền cược không bay hơi (thắng ăn cả)", abs(tong_sau - (tong_truoc - 10)) <= 10)
        kiem_tra("có người thắng trận", ts1.so_tran_thang + ts2.so_tran_thang >= 1)
    await nhap_lenh(core, lo, "/bangpk", 111)
    await nhap_lenh(core, lo, "/nhatky", 222)

    print("\n════ KHƯỚC TỪ ════")
    await nhap_lenh(core, lo, "/pk Hàn Lập", 222)
    cho = (await kho.thach_cua_toi(111))[0]
    if cho:
        await core._xu_ly_nut(TinDen(111, CHAT, "Hàn Lập", "cb", f"pk:n:{cho[0]['id']}"))
    kiem_tra("lời thách bị khước đã xoá sạch", (await kho.thach_cua_toi(111))[0] == [])

    print("\n════ TRẠI ĐIỀU KHIỂN ════")
    await nhap_lenh(core, lo, "/troi", 111)
    await nhap_lenh(core, lo, "/sukien", 111)
    await nhap_lenh(core, lo, "/canhgioi", 111)
    await nhap_lenh(core, lo, "/binhkhi 4", 111)

    await kho.dong()
    print("\n" + ("KỊCH BẢN XONG — KHÔNG SÓT CHỖ NÀO." if ok else f"CÒN LỖI: {loi}"))
    return 0 if ok else 1


async def replay() -> None:
    kho = Kho()
    await kho.mo()
    lo = LoTerminal()
    core = Long(kho, 1, lo, rng=random.Random(), thu_duyen=True)
    global UID
    UID = 111
    print("TIÊN ĐỒ VÔ TẬN — chiếu diễn tập Telegram.")
    print("Gõ /menu để xem mọi cửa. Gõ `~số` để bấm nút của tin cuối. /quit để thu công.\n")
    await nhap_lenh(core, lo, "/menu", UID)
    while True:
        try:
            text = input("🕯 ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text in ("/quit", "/thuc", "exit"):
            break
        if text.startswith("~"):
            so = text[1:].strip()
            if so.isdigit() and lo.nut_cuoi and int(so) <= len(lo.nut_cuoi):
                _lbl, cb = lo.nut_cuoi[int(so) - 1]
                await core._xu_ly_nut(TinDen(UID, CHAT, "kẻ thử võ", "cb", cb))
            else:
                print("không có nút ấy.")
            continue
        await nhap_lenh(core, lo, text if text.startswith("/") else "/" + text, UID)
    await kho.dong()
    print("\nThu công.")


if __name__ == "__main__":
    UID = 111
    raise SystemExit(asyncio.run(tu_dong() if "--tu-dong" in sys.argv else replay()))
