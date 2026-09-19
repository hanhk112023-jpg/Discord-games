#!/usr/bin/env python3
"""Máy chủ Telegram Mini App: HTML, trạng thái game, lệnh và xác thực initData.

Cookie HttpOnly ký HMAC; khách dùng uid âm ngẫu nhiên, tài khoản Telegram dùng
uid thật đã xác thực. Bot và Mini App dùng cùng Long/Kho, không nhân đôi luật chơi.
Chạy bằng `python run.py` hoặc `python run_tele.py --mini`.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import random
import secrets
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from aiohttp import web

from .. import config
from ..db import Kho
from .hien_thi import Trang
from .long import Lo, Long, TinDen

log = logging.getLogger("tien.mini")

DUONG_WEB = Path(__file__).parent / "web"
TEN_COOK = "tien-qua-nguong"
TUOI_PHIEN = 30 * 86400
KHOA_PHIEN = os.getenv("MINI_SESSION_SECRET") or config.TELEGRAM_TOKEN or secrets.token_hex(32)
CHO_KHACH = not config.TELEGRAM_TOKEN or os.getenv("TELE_ALLOW_GUEST") == "1"

# ───────────────────────── ký & kiểm: initData, quá nguỡng, cookie ─────────────────────────


def _ch(bao: str) -> bytes:
    return hashlib.sha256(f"mini|{bao}|{KHOA_PHIEN}".encode()).digest()


def kiem_dau_init(init: str) -> dict | None:
    """initData của Telegram WebApp — kiểm chữ ký theo đúng quy cách chính thức."""
    if not init or not config.TELEGRAM_TOKEN:
        return None
    try:
        parts = dict(parse_qsl(init, keep_blank_values=True))
        chu_ky = parts.pop("hash", "")
        # auth_date ở lại trong chuỗi kiểm — chuẩn Telegram: mọi tham số trừ hash
        luc = int(parts.get("auth_date", "0"))
        if not 0 <= time.time() - luc <= 24 * 3600:
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

    MA_NGUON = "mini"

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
        del self.chat[chat][:-200]

    async def gui(self, chat_id: int, trang: Trang) -> int:
        self.dem += 1
        tin = {"id": self.dem, "c": self.dem, "me": False, "html": trang.html,
               "anh": trang.anh or "", "phim": trang.phim or "",
               "nut": [[{"l": a, "u": b} for a, b in hang] for hang in (trang.hang or [])]}
        self._dong(chat_id, tin)
        return tin["id"]

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
        chat = self.cua.get(uid, uid)
        self.cua[uid] = chat
        return chat


# ───────────────────────── lõi app ─────────────────────────


class Dong:
    kho: Kho
    lo: LoMini
    core: Long | None = None

    def uid_cua(self, request: web.Request) -> tuple[int, int]:
        """Trả (uid, chat) của phiên đã ký; không suy đoán danh tính từ IP."""
        phien = doc_pien(request.cookies.get(TEN_COOK))
        if phien is not None:
            return phien, self.lo.cho_cua(phien)
        raise web.HTTPUnauthorized(text="Hãy mở lại Mini App để đăng nhập.")

    @staticmethod
    async def _json(request: web.Request) -> dict:
        try:
            body = await request.json()
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text="JSON không hợp lệ.")
        if not isinstance(body, dict):
            raise web.HTTPBadRequest(text="Cần một JSON object.")
        return body

    async def vao(self, request: web.Request) -> web.Response:
        """Cửa ngõ. Trong Telegram: initData → nhập danh chính chủ. Ngoài Telegram:
        khách lang thang, vẫn chơi được (uid âm), vẫn lưu sổ — đó là cách diễn tập."""
        body = await self._json(request)
        init = body.get("initData") or request.headers.get("X-Telegram-Init-Data") or ""
        if not isinstance(init, str) or len(init) > 16384:
            raise web.HTTPBadRequest(text="initData không hợp lệ.")
        dau = kiem_dau_init(init)
        if init and not dau:
            return web.json_response({"ok": False, "loi": "Phiên Telegram không hợp lệ hoặc đã hết hạn. Hãy mở lại từ bot."}, status=401)
        if dau:
            uid, chat = dau["u"], self.lo.cho_cua(dau["u"])
            self.lo.cua[uid] = chat
            await self.kho.danh_thiep_luu(uid, chat, dau["ten"])
            r = web.json_response({"ok": True, "chu": dau["ten"], "chinh_chu": True})
            r.set_cookie(TEN_COOK, lam_pien(uid), max_age=TUOI_PHIEN, httponly=True,
                         samesite="None", secure=True)
            return r
        if not CHO_KHACH:
            return web.json_response({"ok": False, "loi": "Hãy mở Mini App từ bot Telegram."}, status=401)
        cu = doc_pien(request.cookies.get(TEN_COOK))
        uid = cu if cu is not None and cu < 0 else -secrets.randbelow(2**52 - 1) - 1
        self.lo.cho_cua(uid)
        r = web.json_response({"ok": True, "chu": "khách qua ngưỡng", "chinh_chu": False})
        r.set_cookie(TEN_COOK, lam_pien(uid), max_age=TUOI_PHIEN, httponly=True,
                     samesite="None" if request.secure or request.headers.get("X-Forwarded-Proto") == "https" else "Lax",
                     secure=request.secure or request.headers.get("X-Forwarded-Proto") == "https")
        return r

    async def gui_lenh(self, request: web.Request) -> web.Response:
        if self.core is None:
            return web.json_response({"ok": False, "loi": "động đang nhóm lửa, giây nữa thôi"}, status=503)
        body = await self._json(request)
        uid, chat = self.uid_cua(request)
        text = body.get("text", "")
        if not isinstance(text, str) or len(text) > 500:
            raise web.HTTPBadRequest(text="Lệnh phải là chuỗi, tối đa 500 ký tự.")
        text = text.strip()
        await self.core.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="",
                                     loai="lenh" if text.startswith(("/", "!")) else "text",
                                     data=text, msg_id=None, nguon="mini"))
        return web.json_response({"ok": True})

    async def bam_nut(self, request: web.Request) -> web.Response:
        if self.core is None:
            return web.json_response({"ok": False}, status=503)
        body = await self._json(request)
        uid, chat = self.uid_cua(request)
        nut, msg = body.get("nut"), body.get("msg")
        if not isinstance(nut, str) or len(nut) > 120 or (msg is not None and type(msg) is not int):
            raise web.HTTPBadRequest(text="Nút bấm không hợp lệ.")
        await self.core.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="", loai="cb",
                                     data=nut, msg_id=msg, nguon="mini"))
        return web.json_response({"ok": True})

    async def keo_tin(self, request: web.Request) -> web.Response:
        uid, chat = self.uid_cua(request)
        try:
            moc = max(0, int(request.query.get("since", "0")))
        except ValueError:
            raise web.HTTPBadRequest(text="Mốc tin không hợp lệ.")
        tin = [t for t in self.lo._noi(chat) if t["c"] > moc]
        dem = max([t["c"] for t in self.lo._noi(chat)] or [0])
        ts = await self.kho.lay_tu_si(uid)
        bao = self.lo.toast.pop(chat, None)
        return web.json_response({"tin": tin[-60:], "moc": dem,
                                  "la": ts.ten if ts else None, "bao": bao})


    async def trang_thai(self, request: web.Request) -> web.Response:
        from .trang_thai import lay
        uid, _ = self.uid_cua(request)
        if self.core is None:
            raise web.HTTPServiceUnavailable(text="Đang mở cửa động.")
        async with self.core.khoa_lenh:
            return web.json_response(await lay(self.kho, uid), headers={"Cache-Control": "no-store"})


@web.middleware
async def bao_ve(request, handler):
    if request.method == "POST":
        # Cookie SameSite=None dùng trong Telegram: chặn form/text/plain CSRF.
        if request.content_type != "application/json":
            raise web.HTTPUnsupportedMediaType(text="Chỉ nhận application/json.")
        origin = request.headers.get("Origin")
        if origin and urlsplit(origin).netloc != request.host:
            raise web.HTTPForbidden(text="Nguồn yêu cầu không hợp lệ.")
    response = await handler(request)
    if request.path in {"/vao", "/gui", "/nut", "/keo", "/api/state"}:
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def tao_app(dong: Dong) -> web.Application:
    app = web.Application(middlewares=[bao_ve], client_max_size=65536)
    async def static_file(request):
        filename = "index.html" if request.path == "/" else request.path.lstrip("/")
        return web.FileResponse(DUONG_WEB / filename)
    for route in ("/", "/favicon.svg", "/mong.css", "/dong.js"):
        app.router.add_get(route, static_file)
    app.router.add_static("/fonts/", str(DUONG_WEB / "fonts"))
    app.router.add_get("/api/state", dong.trang_thai)
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
    from .vong import vong_tron_doi
    app = tao_app(dong)
    async def cycle(app):
        task = asyncio.create_task(vong_tron_doi(dong.core))
        yield
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await kho.dong()
    app.cleanup_ctx.append(cycle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", cong or config.WEB_PORT).start()
    return runner, None, dong


async def mo_site(dong: Dong, cong: int | None = None):
    """Mở cổng cho một bộ máy đã có lõi. Trả runner."""
    app = tao_app(dong)
    runner = web.AppRunner(app)
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
