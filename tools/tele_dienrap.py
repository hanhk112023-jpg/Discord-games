#!/usr/bin/env python3
"""Diện mạo Telegram trong trình duyệt — chơi thử bot trước khi dựng bot thật.

    python tools/tele_dienrap.py           # http://localhost:8080
    PORT=3000 python tools/tele_dienrap.py

Giao diện mô phỏng khung chat Telegram: bong bóng tin nhắn, ảnh thuỷ mặc, video,
và hàng nút bấm inline. Lõi lệnh chạy y hệt `tuchan/tele/long.py` — thứ mà bot
aiogram thật dùng — chỉ khác cái miệng. Muốn thử PK hai người: `/tao <tên>` để gọi
thêm kẻ, `/doi <tên>` để nhập vào mắt nó mà bấm nút hộ.
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("CAP_TOC", "1")
os.environ.setdefault("HE_SO_THOI_GIAN", "0.004")

from aiohttp import web  # noqa: E402

from tuchan import config  # noqa: E402
from tuchan.db import Kho  # noqa: E402
from tuchan.tele.hien_thi import Trang  # noqa: E402
from tuchan.tele.long import Lo, Long, TinDen  # noqa: E402

GOC = Path(__file__).resolve().parent.parent
KHO = Kho(str(GOC / "data" / "tele_dienrap.sqlite3"))
RNG = random.Random()

LOCHAT: dict[int, list[dict]] = {}      # chat -> các tin đã gửi (kể cả tin loan)
UID: dict[int, int] = {}                # chat -> uid con mắt đang nhìn
DEM = [0]                               # bộ đếm mọi sự kiện (tin mới + tin sửa)
CORE: Long | None = None


def uid_moi(chat: int) -> int:
    """Chưa đăng ký thì tạm mượn một uid âm deterministic — mỗi trình duyệt một kẻ lạ."""
    return -(chat * 7919 + 1)


class LoWeb(Lo):
    def _dong(self, chat: int, tin: dict) -> None:
        DEM[0] += 1
        tin["c"] = DEM[0]
        LOCHAT.setdefault(chat, []).append(tin)

    async def gui(self, chat_id: int, trang: Trang) -> int:
        DEM[0] += 1
        mid = DEM[0]
        tin = {"id": mid, "c": DEM[0], "me": False, "html": trang.html,
               "anh": trang.anh or "", "phim": trang.phim or "",
               "nut": [[{"l": a, "cb": b} for a, b in hang] for hang in (trang.hang or [])]}
        LOCHAT.setdefault(chat_id, []).append(tin)
        return mid

    async def sua(self, chat_id: int, msg_id, trang: Trang) -> None:
        if msg_id is None:
            return
        for tin in LOCHAT.get(chat_id, []):
            if tin["id"] == int(msg_id):
                DEM[0] += 1
                tin.update(html=trang.html, c=DEM[0], anh=trang.anh or tin["anh"],
                           nut=[[{"l": a, "cb": b} for a, b in hang] for hang in (trang.hang or [])])
                break

    async def doi_uid(self, chat_id: int, uid: int) -> None:
        UID[chat_id] = uid


async def xu_ly(request: web.Request) -> web.Response:
    chat = lay_chat(request)
    body = await request.json()
    text = (body.get("text") or "").strip()
    uid = UID.setdefault(chat, uid_moi(chat))
    await CORE.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="", loai="lenh" if text.startswith("/") else "text",
                            data=text, msg_id=None))
    return web.json_response({"ok": True})


async def gui_nut(request: web.Request) -> web.Response:
    chat = lay_chat(request)
    body = await request.json()
    uid = UID.setdefault(chat, uid_moi(chat))
    await CORE.xu_ly(TinDen(user_id=uid, chat_id=chat, ten="", loai="cb",
                            data=body.get("cb", ""), msg_id=body.get("msg")))
    return web.json_response({"ok": True})


async def pull(request: web.Request) -> web.Response:
    chat = lay_chat(request)
    since = int(request.query.get("since", "0"))
    dem = 0
    for t in LOCHAT.get(chat, []):
        dem = max(dem, int(t["c"]))
    tin = [t for t in LOCHAT.get(chat, []) if t["c"] > since]
    uid = UID.get(chat)
    ts = await KHO.lay_tu_si(uid if uid is not None else uid_moi(chat))
    return web.json_response({"tin": tin[-40:], "next": dem,
                              "dang_la": ts.ten if ts else "(chưa nhập đạo)"})


async def trang_chu(request):
    if "chat" not in request.cookies:
        chat = random.randrange(1_000_000, 9_999_999)
        LOCHAT.setdefault(chat, [])
    else:
        chat = int(request.cookies["chat"])
        LOCHAT.setdefault(chat, [])
    r = web.Response(text=TRANG_HTML, content_type="text/html")
    r.set_cookie("chat", str(chat), max_age=86400 * 30, samesite="Lax")
    return r


def lay_chat(request) -> int:
    c = request.cookies.get("chat")
    if not c:
        raise web.HTTPBadRequest(text="thiếu vé vào chiếu")
    return int(c)


TRANG_HTML = """<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tiên Đồ Vô Tận — chiếu diễn tập Telegram</title>
<style>
:root{--nen:#0e1621;--truot:#17212b;--bot:#182533;--toi:#0d1721;--chu:#e9eef4;--mo:#7f95ad;--kim:#e3b562;--xanh:#2b527e;--nut:#243a54}
*{box-sizing:border-box}body{margin:0;background:var(--nen);color:var(--chu);
font-family:"Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif}
.khung{max-width:690px;margin:0 auto;min-height:100vh;display:flex;flex-direction:column}
header{background:var(--truot);padding:10px 14px;display:flex;align-items:center;gap:10px;
position:sticky;top:0;z-index:5;border-bottom:1px solid #0a121c}
header .av{width:38px;height:38px;border-radius:50%;background:radial-gradient(circle at 35% 30%,var(--kim),#7c5a1e);
display:flex;align-items:center;justify-content:center;font-size:19px;flex:0 0 auto}
header b{font-size:15px}header small{color:var(--mo);display:block;font-size:12px}
main{flex:1;overflow-y:auto;padding:16px 12px 8px;display:flex;flex-direction:column;gap:8px;
background:radial-gradient(1200px 500px at 50% -10%,#1a2938,transparent),var(--nen)}
.bong{max-width:88%;padding:8px 12px;border-radius:14px 14px 14px 5px;background:var(--bot);
line-height:1.55;font-size:14.5px;white-space:pre-wrap;overflow-wrap:anywhere;box-shadow:0 1px 2px #0006}
.bong.me{align-self:flex-end;border-radius:14px 14px 5px 14px;background:var(--xanh)}
.bong b{color:#ffe6b0}.bong i{color:#b6c7da}
.bong code{background:#0a121c;padding:1px 5px;border-radius:4px;color:#ffd479;font-size:13px}
.bong img,.bong video{max-width:100%;border-radius:8px;margin:6px 0;display:block;background:#000}
.hangnut{align-self:flex-start;display:flex;flex-wrap:wrap;gap:6px;margin:-3px 0 4px}
.hangnut button{background:var(--nut);color:#dbe9f7;border:0;border-radius:9px;padding:8px 13px;
font-size:13.5px;cursor:pointer;box-shadow:0 1px 2px #0008;max-width:330px}
.hangnut button:hover{background:#2f4d6d}
footer{position:sticky;bottom:0;background:var(--truot);padding:9px 12px;display:flex;gap:8px;border-top:1px solid #0a121c}
footer input{flex:1;background:var(--toi);border:1px solid #232f3d;color:var(--chu);
border-radius:18px;padding:11px 15px;font-size:14.5px;outline:none}
footer button{background:var(--xanh);border:0;color:#fff;border-radius:50%;width:42px;height:42px;
font-size:17px;cursor:pointer;flex:0 0 auto}
.ghi{color:var(--mo);font-size:11.5px;padding:0 16px 8px;background:var(--truot)}
</style></head><body><div class="khung">
<header><div class="av">仙</div><div><b>Tiên Đồ Vô Tận</b><small id="tt">đang nối…</small></div></header>
<main id="chat"></main>
<div class="ghi">Chiếu diễn tập — mọi thời gian chờ đã rút ngắn. /tao &lt;tên&gt; gọi thêm kẻ · /doi &lt;tên&gt; đổi con mắt · /menu mở bảng điều lệnh.</div>
<footer><input id="inp" placeholder="/menu" autocomplete="off"><button id="btn">➤</button></footer>
</div><script>
let since=0;
const chat=document.getElementById('chat');
function tao(t){const b=document.createElement('div');b.className='bong'+(t.me?' me':'');b.dataset.id=t.id;
 let h='';if(t.anh)h+=`<img src="/tranh/${t.anh}" alt="">`;if(t.phim)h+=`<video src="/thanh_anh/${t.phim}" controls preload="metadata"></video>`;
 b.innerHTML=h+(t.html||'');return b}
function nut_khung(t){const r=document.createElement('div');r.className='hangnut';r.dataset.nutof=t.id;
 (t.nut||[]).forEach(hang=>hang.forEach(n=>{const btn=document.createElement('button');btn.textContent=n.l;
  btn.onclick=()=>gui_nut(t.id,n.cb);r.appendChild(btn)}));return r}
function render(t){
 let el=chat.querySelector(`.bong[data-id="${t.id}"]`);
 if(el){el.innerHTML=media(t)+ (t.html||'');
  const old=chat.querySelector(`.hangnut[data-nutof="${t.id}"]`);if(old)old.remove();
  if((t.nut||[]).length)el.after(nut_khung(t));return}
 const b=tao(t);chat.appendChild(b);
 if((t.nut||[]).length)chat.appendChild(nut_khung(t));
 chat.scrollTop=chat.scrollHeight;
}
function media(t){let h='';if(t.anh)h+=`<img src="/tranh/${t.anh}" alt="">`;if(t.phim)h+=`<video src="/thanh_anh/${t.phim}" controls preload="metadata"></video>`;return h}
async function gui_nut(id,cb){await fetch('/nut',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({msg:id,cb:cb})});}
async function gui(){const inp=document.getElementById('inp');const v=inp.value.trim();if(!v)return;inp.value='';
 render({id:-(++since)-100000000,me:true,html:v.replace(/</g,'&lt;'),nut:[]});
 await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:v})});}
document.getElementById('btn').onclick=gui;
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')gui()});
async function vong(){try{
 const r=await fetch('/pull?since='+since);const d=await r.json();
 d.tin.forEach(render);if(d.next)since=d.next;
 document.getElementById('tt').textContent=d.dang_la==='(chưa nhập đạo)'?'một kẻ lạ trước cửa đạo':'đang sống kiếp '+d.dang_la;
}catch(e){}
 setTimeout(vong,1200);}
vong();
</script></body></html>"""


async def khoi_tao(app):
    global CORE
    await KHO.mo()
    CORE = Long(KHO, config.TELE_GUILD, LoWeb(), rng=RNG, thu_duyen=True)
    # chiến trường diễn tập: dọn mình cho khách — nếu chưa có boss thì gọi một con
    from tuchan.he import dauboss as he_boss
    await he_boss.don_dep(KHO, config.TELE_GUILD, RNG)


def tao_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(khoi_tao)
    app.router.add_get("/", trang_chu)
    app.router.add_post("/send", xu_ly)
    app.router.add_post("/nut", gui_nut)
    app.router.add_get("/pull", pull)
    app.router.add_static("/tranh/", str(config.DUONG_DAN_TRANH))
    config.DUONG_DAN_THANH_ANH.mkdir(parents=True, exist_ok=True)
    app.router.add_static("/thanh_anh/", str(config.DUONG_DAN_THANH_ANH))
    return app


if __name__ == "__main__":
    cong = int(os.getenv("PORT", "8080"))
    web.run_app(tao_app(), host="0.0.0.0", port=cong)
