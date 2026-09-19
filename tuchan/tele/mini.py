#!/usr/bin/env python3
"""Động khô — backend của Telegram Mini App.

Một tệp aiohttp nằm cạnh lõi `long.py`: khung chat trong Telegram mở ra bằng nút
*Vào động*, và mọi thứ ngươi bấm ở đó đi thẳng vào cùng bộ máy, cùng cuốn sổ sinh tử
mà bot dùng. Không có tầng trung gian, không có bản sao luật chơi.

Ba điều lớp này chịu trách nhiệm, không cái nào thuộc về luật chơi:

* **verify initData** — Telegram ký gói người dùng bằng HMAC của token bot
  (chuẩn chính thức của Mini App); ký đúng mới được nhập danh.
* **phiên âm không trạng thái** — cookie là bản HMAC tự ký, không có session table.
  Máy chủ trên GitHub Actions sống thọ bằng một cái ổ đĩa tạm; mất hết bộ nhớ
  là chuyện thường tình — người thật thì vẫn còn nguyên trong CSDL.
* **vận chuyển Trang** — cùng giao ước `Lo` như bot Telegram: gui/sua, nút bấm, ảnh, video.

    python -m tuchan.tele.web          # chạy một mình: khách lang thang, chưa cần token
    python run_tele.py --mini          # bot + cửa động trong một tiến trình
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import random
import time
from pathlib import Path
from urllib.parse import parse_qsl

from aiohttp import web

from .. import config
from ..db import Kho
from .hien_thi import Trang
from .long import Lo, Long, TinDen

log = logging.getLogger("tien.mini")

DUONG_WEB = Path(__file__).parent / "web"
TEN_COOK = "tien-qua-nguong"
TUOI_PHIEN = 30 * 86400

# ───────────────────────── ký & kiểm: initData, quá nguỡng, cookie ─────────────────────────


def _ch(bao: str) -> bytes:
    return hashlib.sha256(f"mini|{bao}|{config.TELEGRAM_TOKEN}".encode()).digest()


def kiem_dau_init(init: str) -> dict | None:
    """initData của Telegram WebApp — kiểm chữ ký theo đúng quy cách chính thức."""
    if not init or not config.TELEGRAM_TOKEN:
        return None
    try:
        parts = dict(parse_qsl(init, keep_blank_values=True))
        chu_ky = parts.pop("hash", "")
        # auth_date ở lại trong chuỗi kiểm — chuẩn Telegram: mọi tham số trừ hash
        luc = int(parts.get("auth_date", "0"))
        if time.time() - luc > 24 * 3600:
            return None
        chuoi = "\n".join(f"{k}={v}" for k, v in sorted(parts.items()))
        khoa = hmac.new(b"WebAppData", config.TELEGRAM_TOKEN.encode(), hashlib.sha256).digest()
        if hmac.compare_digest(hmac.new(khoa, chuoi.encode(), hashlib.sha256).hexdigest(), chu_ky):
            nguoi = json.loads(parts.get("user", "{}"))
            return dict(u=int(nguoi["id"]), ten=nguoi.get("first_name") or nguoi.get("username")
                        or "bạn đồng đạo")
    except Exception as e:  # một initData méo cũng không được làm sập cả cổng
        log.debug("initData fail: %s", e)
    return None


def lam_pien(uid: int) -> str:
    luc = int(time.time()) + TUOI_PHIEN
    chu = f"{uid}.{luc}"
    return f"{chu}.{hmac.new(_ch('phien'), chu.encode(), hashlib.sha256).hexdigest()[:32]}"


def doc_pien(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        s, luc, chu = raw.split(".")
        if int(luc) < time.time():
            return None
        if hmac.compare_digest(hmac.new(_ch("phien"), f"{s}.{luc}".encode(), hashlib.sha256).hexdigest()[:32], chu):
            return int(s)
    except Exception:
        pass
    return None


# ───────────────────────── vận chuyển: một chat web là một cái hang ─────────────────────────


class LoMini(Lo):
    """Khung chat của một cửa sổ trình duyệt. Tin mới và tin sửa đều tính lượt
    (bộ đếm vọt) để bên web chỉ việc kéo tiếp, không cần biết tin nào bị sửa."""

    def __init__(self):
        self.chat = {}      # chat -> [tin]
        self.cua = {}       # uid -> chat đang ngồi
        self.toast = {}     # chat -> mẩu tin báo ngắn
        self.dem = 0

    def _noi(self, chat: int) -> list:
        return self.chat.setdefault(chat, [])

    def _dong(self, chat: int, tin: dict) -> None:
        self.dem += 1
        tin["c"] = self.dem
        self._noi(chat).append(tin)

    async def gui(self, chat_id: int, trang: Trang) -> int:
        self.dem += 1
        tin = {"id": self.dem, "c": self.dem, "me": False, "html": trang.html,
               "anh": trang.anh or "", "phim": trang.phim or "",
               "nut": [[{"l": a, "u": b} for a, b in hang] for hang in (trang.hang or [])]}
        self._dong(chat_id, tin)
        return self.dem

    async def sua(self, chat_id: int, msg_id, trang: Trang) -> None:
        if msg_id is None:
            return
        for tin in self._noi(chat_id):
            if tin["id"] == int(msg_id):
                self.dem += 1
                tin.update(html=trang.html, c=self.dem, anh=trang.anh or tin["anh"],
                           nut=[[{"l": a, "u": b} for a, b in hang] for hang in (trang.hang or [])])
                break

    async def bao(self, user_id: int, text: str) -> None:
        chat = self.cua.get(user_id)
        if chat is not None:
            self.toast[chat] = text[:120]

    async def doi_uid(self, chat_id: int, uid: int) -> None:
        self.cua[uid] = chat_id

    # --- dùng nội bộ -------------------------------------------------------

    def cho_cua(self, uid: int) -> int:
        """Mỗi tu sĩ một hang riêng theo uid — mở lại cửa sổ vẫn đúng chỗ cũ."""
        chat = self.cua.get(uid) or (uid if uid > 0 else -(abs(uid) * 7919 + 1) % (2 ** 31))
        self.cua[uid] = chat
        return chat


# ───────────────────────── lõi app ─────────────────────────


class Dong:
    kho: Kho
    lo: LoMini
    core: Long

    def uid_cua(self, request: web.Request) -> tuple[int, int]:
        """Trả (uid, chat). Khách chưa đăng ký thì mượn một uid âm — deterministic
        theo địa chỉ IP+trình duyệt để lần sau quay lại vẫn đúng hang đã ngồi."""
        phien = doc_pien(request.cookies.get(TEN_COOK))
        if phien is not None:
            return phien, self.lo.cho_cua(phien)
        chat = self.lo.cho_cua(self.khach_uid(request))
        uid = -chat
        self.lo.cua.setdefault(uid, chat)
        return uid, chat

    @staticmethod
    def khach_uid(request: web.Request) -> int:
        ip = (request.headers.get("X-Forwarded-For", "") or request.remote or "?").split(",")[0].strip()
        return abs(hash(ip + str(request.headers.get("User-Agent", "")))) % (2 ** 30) + 1

    @staticmethod
    async def _json(request: web.Request) -> dict:
        """Khách gửi gì méo mó thì nhận lại con rỗng — cửa động không cãi nhau với người say."""
        try:
            return await request.json() or {}
        except Exception:
            return {}

    async def vao(self, request: web.Request) -> web.Response:
        """Cửa ngõ. Trong Telegram: initData → nhập danh chính chủ. Ngoài Telegram:
        khách lang thang, vẫn chơi được (uid âm), vẫn lưu sổ — đó là cách diễn tập."""
        body = await self._json(request)
        dau = kiem_dau_init(body.get("initData") or request.headers.get("X-Telegram-Init-Data") or "")
        if dau:
            uid, chat = dau["u"], self.lo.cho_cua(dau["u"])
            self.lo.cua[uid] = chat
            await self.kho.danh_thiep_luu(uid, chat, dau["ten"])
            r = web.json_response({"ok": True, "chu": dau["ten"], "chinh_chu": True})
            r.set_cookie(TEN_COOK, lam_pien(uid), max_age=TUOI_PHIEN, httponly=True,
                         samesite="None", secure=True)
            return r
        gk = self.khach_uid(request)
        chat = self.lo.cho_cua(gk)
        uid = -chat
        self.lo.cua.setdefault(uid, chat)
        r = web.json_response({"ok": True, "chu": "khách qua ngưỡng", "chinh_chu": False})
        r.set_cookie(TEN_COOK, lam_pien(uid), max_age=TUOI_PHIEN, httponly=True, samesite="Lax")
        return r

    async def gui_lenh(self, request: web.Request) -> web.Response:
        if self.core is None:
            return web.json_response({"ok": False, "loi": "động đang nhóm lửa, giây nữa thôi"}, status=503)
        body = await self._json(request)
        uid, chat = self.uid_cua(request)
        text = (body.get("text") or "").strip()
        await self.core.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="",
                                     loai="lenh" if text.startswith(("/", "!")) else "text",
                                     data=text, msg_id=None))
        return web.json_response({"ok": True})

    async def bam_nut(self, request: web.Request) -> web.Response:
        if self.core is None:
            return web.json_response({"ok": False}, status=503)
        body = await self._json(request)
        uid, chat = self.uid_cua(request)
        await self.core.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="", loai="cb",
                                     data=str(body.get("nut") or ""), msg_id=body.get("msg")))
        return web.json_response({"ok": True})

    async def keo_tin(self, request: web.Request) -> web.Response:
        uid, chat = self.uid_cua(request)
        moc = int(request.query.get("since", "0"))
        tin = [t for t in self.lo._noi(chat) if t["c"] > moc]
        dem = max([t["c"] for t in self.lo._noi(chat)] or [0])
        ts = await self.kho.lay_tu_si(uid)
        bao = self.lo.toast.pop(chat, None)
        return web.json_response({"tin": tin[-60:], "moc": dem,
                                  "la": ts.ten if ts else None, "bao": bao})


def tao_app(dong: Dong) -> web.Application:
    app = web.Application()
    app.router.add_get("/", lambda r: web.FileResponse(DUONG_WEB / "index.html"))
    app.router.add_get("/favicon.svg", lambda r: web.FileResponse(DUONG_WEB / "favicon.svg"))
    if (DUONG_WEB / "mong.css").exists():
        app.router.add_get("/mong.css", lambda r: web.FileResponse(DUONG_WEB / "mong.css"))
    if (DUONG_WEB / "dong.js").exists():
        app.router.add_get("/dong.js", lambda r: web.FileResponse(DUONG_WEB / "dong.js"))
    app.router.add_post("/vao", dong.vao)
    app.router.add_post("/gui", dong.gui_lenh)
    app.router.add_post("/nut", dong.bam_nut)
    app.router.add_get("/keo", dong.keo_tin)
    config.DUONG_DAN_TRANH.mkdir(parents=True, exist_ok=True)
    config.DUONG_DAN_THANH_ANH.mkdir(parents=True, exist_ok=True)
    app.router.add_static("/tranh/", str(config.DUONG_DAN_TRANH))
    app.router.add_static("/thanh/", str(config.DUONG_DAN_THANH_ANH))
    return app


def nhan(kho: Kho) -> Dong:
    """Dựng bộ máy cửa động chưa có lõi lệnh — bot Telegram gọi `gan_core` sau."""
    dong = Dong()
    dong.kho = kho
    dong.lo = LoMini()
    return dong


async def mo(core: Long | None = None, kho: Kho | None = None,
             cong: int | None = None, rng: random.Random | None = None):
    """Khởi động cửa động độc lập (không bot — diễn tập). Trả (runner, site, dong)."""
    kho = kho or Kho()
    await kho.mo()
    dong = nhan(kho)
    dong.core = core or Long(kho, config.TELE_GUILD, dong.lo, rng=rng or random.Random(),
                             thu_duyen=not config.TELEGRAM_TOKEN)
    return await mo_site(dong, cong), None, dong


async def mo_site(dong: Dong, cong: int | None = None):
    """Mở cổng cho một bộ máy đã có lõi. Trả runner."""
    runner = web.AppRunner(tao_app(dong))
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", cong or config.WEB_PORT)
    await site.start()
    log.info("Cửa động mở ở cổng %s", cong or config.WEB_PORT)
    return runner


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s")
    os.environ.setdefault("CAP_TOC", "1")

    async def _chay() -> None:
        runner, site, dong = await mo()
        print(f"\n⛩  Động đã mở: http://localhost:{config.WEB_PORT}  "
              f"(khách lang thang; {config.DB_PATH})\n")
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, asyncio.CancelledError):
            await runner.cleanup()

    asyncio.run(_chay())
