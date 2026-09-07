"""Diễn Rạp — xem thử thế giới tu chân ngay trong trình duyệt, không cần bot Discord.

    python tools/web_dienrap.py            # mở ở cổng 8080
    PORT=3000 python tools/web_dienrap.py

Dùng đúng bộ máy mà bot Discord dùng, chỉ khác cái miệng kể chuyện.
"""

from __future__ import annotations

import asyncio
import os
import random
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("CAP_TOC", "1")  # diễn tập thì không bắt ai chờ một canh giờ
os.environ.setdefault("HE_SO_THOI_GIAN", "0.0015")  # một canh giờ rút còn mấy nhịp thở

from aiohttp import web  # noqa: E402

from tuchan import config  # noqa: E402
from tuchan.canhgioi import ten_canh_gioi  # noqa: E402
from tuchan.data import diadanh as dl_diadanh  # noqa: E402
from tuchan.data import monphai as dl_monphai  # noqa: E402
from tuchan.data import xuatthan as dl_xuatthan  # noqa: E402
from tuchan.db import Kho  # noqa: E402
from tuchan.he import (giaothuong, luyenche, nhanvat, phieuluu, thienbien,  # noqa: E402
                       tongmon, tuluyen)
from tuchan.he.ketqua import KetQua  # noqa: E402
from tuchan.he.thienco import he_so_the_gioi  # noqa: E402

GOC = Path(__file__).resolve().parent.parent
KHO = Kho(str(GOC / "data" / "dienrap.sqlite3"))
RNG = random.Random()
PHIEN: dict[str, int] = {}
_dem = [900000]

TRANG = """<!doctype html>
<html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tiên Đồ Vô Tận — Diễn Rạp</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{--muc:#0d0c0b;--giay:#cfc6b4;--mo:#8b8375;--kim:#b08d3f;--huyet:#7a2222;--linh:#4e7f74}
*{box-sizing:border-box}
body{margin:0;background:var(--muc);color:var(--giay);font-family:'Noto Serif',Georgia,serif;line-height:1.85}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.5;
 background:radial-gradient(ellipse at 50% 0%,rgba(176,141,63,.09),transparent 60%),
            radial-gradient(ellipse at 50% 100%,rgba(0,0,0,.9),transparent 60%)}
.khung{max-width:920px;margin:0 auto;padding:28px 20px 90px;position:relative}
header{text-align:center;padding:26px 0 14px;border-bottom:1px solid #2a2622}
h1{font-size:30px;letter-spacing:.34em;margin:0 0 6px;font-weight:600;color:#e6dcc6}
header p{margin:0;color:var(--mo);font-style:italic;font-size:14px}
.thanh{position:sticky;top:0;z-index:9;background:rgba(13,12,11,.94);backdrop-filter:blur(6px);
 border-bottom:1px solid #2a2622;padding:10px 0;margin-bottom:18px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
button{background:transparent;border:1px solid #3a352e;color:var(--giay);font-family:inherit;font-size:13.5px;
 padding:6px 13px;border-radius:2px;cursor:pointer;transition:.18s}
button:hover{border-color:var(--kim);color:#f0e6cf;background:rgba(176,141,63,.08)}
button.nguy{border-color:#4a2020;color:#c99}
button.nguy:hover{border-color:var(--huyet);background:rgba(122,34,34,.12)}
select,input{background:#15130f;border:1px solid #3a352e;color:var(--giay);font-family:inherit;
 padding:6px 9px;border-radius:2px;font-size:13.5px}
.canh{border:1px solid #2a2622;border-left:2px solid var(--kim);background:linear-gradient(180deg,#131211,#0f0e0d);
 padding:20px 24px;margin:20px 0;animation:hien .5s ease}
@keyframes hien{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.canh h2{margin:0 0 14px;font-size:17px;letter-spacing:.2em;color:var(--kim);font-weight:600;text-transform:uppercase}
.canh p{margin:0 0 13px;white-space:pre-wrap}
.canh video{width:100%;border-radius:2px;margin:4px 0 16px;border:1px solid #241f1a;background:#000}
.canh img{width:100%;border-radius:2px;margin:4px 0 16px;filter:saturate(.8) contrast(1.05);border:1px solid #241f1a}
.canh.huyet{border-left-color:var(--huyet)} .canh.linh{border-left-color:var(--linh)}
strong{color:#e8dcbe;font-weight:600} em{color:#a89c86}
.ghi{color:var(--mo);font-style:italic;font-size:13px;border-top:1px dashed #2a2622;padding-top:10px;margin-top:6px}
footer{text-align:center;color:#5f5950;font-size:12px;padding:30px 0 0;font-style:italic}
.hang{display:flex;gap:8px;flex-wrap:wrap;align-items:center;justify-content:center;margin-top:8px}
#dang{color:var(--mo);text-align:center;font-style:italic;padding:12px;display:none}
</style></head><body><div class="khung">
<header>
  <h1>仙 途 無 盡</h1>
  <p>Tiên Đồ Vô Tận — diễn rạp thử, thời gian chờ đã được rút ngắn</p>
</header>
<div class="thanh" id="thanh"></div>
<div id="dang">…thiên cơ đang chuyển…</div>
<div id="canh"></div>
<footer>Mọi thứ ngươi đọc ở đây đều do cùng một bộ máy sinh ra với bot Discord.</footer>
</div>
<script>
const NUT = [
 ["nhanvat","Nhìn lại mình"],["luyentap","Toạ quan"],["thiennhien","Dẫn thiên địa"],["dotpha","Xung quan",1],
 ["khampha","Khám phá"],["timduoc","Hái thuốc"],["duykysi","Tỉ thí",1],["monphai","Tông môn"],
 ["nhiemvu","Chấp sự đường"],["viecdi","Lên đường"],["sotay","Sổ tay"],["luyendan","Mở lò"],
 ["cuahang","Xuống chợ"],["tuido","Túi càn khôn"],["thientuong","Xem trời"],["nhatky","Thủ ký"],
 ["uongdan","Uống đan"],["deo","Đeo pháp bảo"],["mua","Mua hàng"],
 ["vatpham","Ngắm vật phẩm"],["canhgioi","Bia mười bậc"],["kiepnan","Chín cửa ải"],["binhkhi","Binh Khí Phổ"],
 ["linhdan","Đan Phổ"],["kimdan","Chín phẩm kim đan"],
 ["sukien","Gọi thiên biến"],["lam_lai","Làm lại từ đầu",1]
];
const thanh=document.getElementById('thanh'), canh=document.getElementById('canh'), dang=document.getElementById('dang');
NUT.forEach(([ma,ten,nguy])=>{const b=document.createElement('button');b.textContent=ten;
 if(nguy)b.className='nguy';b.onclick=()=>goi(ma);thanh.appendChild(b)});
async function goi(lenh,tham){
 dang.style.display='block';
 const r=await fetch('/lenh',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({lenh,tham:tham||''})});
 const d=await r.json(); dang.style.display='none'; ve(d);
}
function ve(d){
 const el=document.createElement('div'); el.className='canh '+(d.lop||'');
 let h='<h2>'+d.tieu_de+'</h2>';
 if(d.phim) h+='<video src="/thanh_anh/'+d.phim+'" controls playsinline preload="metadata" poster="/tranh/'+(d.anh||'bia_tien_do.png')+'"></video>';
 else if(d.anh) h+='<img src="/tranh/'+d.anh+'" alt="">';
 h+=d.van.map(p=>'<p>'+p+'</p>').join('');
 if(d.chon) h+=d.chon;
 el.innerHTML=h; canh.prepend(el); window.scrollTo({top:0,behavior:'smooth'});
}
window.chon=function(lenh,id){goi(lenh,document.getElementById(id).value)};
goi('vao');
</script></body></html>"""


def dinh_dang(van: str) -> str:
    import re
    van = (van.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    van = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", van)
    van = re.sub(r"\*(.+?)\*", r"<em>\1</em>", van, flags=re.S)
    return van


def goi_ra(kq: KetQua, chon: str = "") -> web.Response:
    lop = "huyet" if kq.mau == config.MAU_HUYET else ("linh" if kq.mau == config.MAU_LINH else "")
    return web.json_response({
        "tieu_de": kq.tieu_de or "…",
        "van": [dinh_dang(v) for v in kq.van],
        "anh": kq.anh or "",
        "phim": kq.thanh_anh or "",
        "lop": lop,
        "chon": chon,
    })


async def lay_ts(request):
    sid = request.cookies.get("sid")
    if sid and sid in PHIEN:
        return await KHO.lay_tu_si(PHIEN[sid]), sid
    return None, sid


async def xu_ly(request: web.Request) -> web.Response:
    d = await request.json()
    lenh = d.get("lenh", "")
    tham = (d.get("tham") or "").strip()
    sid = request.cookies.get("sid")
    moi = False
    if not sid:
        sid = secrets.token_hex(8)
        moi = True
    uid = PHIEN.get(sid)
    ts = await KHO.lay_tu_si(uid) if uid else None
    hs = await he_so_the_gioi(KHO, 1)

    if lenh == "lam_lai" and uid:
        await KHO.xoa_tu_si(uid)
        PHIEN.pop(sid, None)
        ts = None
        uid = None

    if ts is None or ts.da_chet:
        if lenh == "nhap_dao" and tham:
            _dem[0] += 1
            uid = _dem[0]
            PHIEN[sid] = uid
            kq = await nhanvat.tao_nhan_vat(KHO, uid, 1, tham.split("|")[0][:24] or "Vô Danh",
                                            "nam", tham.split("|")[1] if "|" in tham else "pham_nhan", RNG)
            kq.thanh_anh = "nhap_dao.mp4"
            r = goi_ra(kq)
        else:
            opts = "".join(f'<option value="{x.ma}">{x.ten}</option>' for x in dl_xuatthan.DANH_SACH.values())
            chon = (
                '<div class="ghi">Ngươi từ đâu tới?</div><div class="hang">'
                '<input id="ten" placeholder="Đạo hiệu" value="Hàn Lập">'
                f'<select id="xt">{opts}</select>'
                '<button onclick="goi(\'nhap_dao\', document.getElementById(\'ten\').value + \'|\' '
                '+ document.getElementById(\'xt\').value)">Bước qua cổng</button></div>'
            )
            kq = KetQua(
                tieu_de="Trước cửa đạo", anh="bia_tien_do.png",
                van=["Ngươi đứng dưới chân núi, ngửa mặt nhìn con đường đá dẫn lên chỗ mây phủ. "
                     "Gió trên cao mang xuống mùi tuyết và một thứ mùi lạ mà về sau ngươi sẽ biết tên: linh khí.",
                     "Trước khi bước, có một câu phải trả lời — câu mà cả đời tu hành ngươi sẽ bị hỏi lại nhiều lần: "
                     "**ngươi từ đâu tới?**"],
                mau=config.MAU_LINH)
            r = goi_ra(kq, chon)
        if moi:
            r.set_cookie("sid", sid, max_age=86400 * 7, samesite="Lax")
        return r

    # ── các lệnh khi đã có nhân vật ──
    if lenh in ("vao", "nhanvat"):
        kq = await nhanvat.xem_nhan_vat(KHO, ts, hs)
    elif lenh == "luyentap":
        kq = await tuluyen.luyen_tap(KHO, ts, RNG, hs)
    elif lenh == "thiennhien":
        kq = await tuluyen.hap_thu_thien_dia(KHO, ts, RNG, hs)
    elif lenh == "dotpha":
        from tuchan.canhgioi import la_dinh_canh
        len_bac = la_dinh_canh(ts.canh_gioi, ts.tang)
        kq = await tuluyen.dot_pha(KHO, ts, RNG, hs)
        if kq.du_lieu.get("thanh_cong") and len_bac:
            kq.thanh_anh = "dot_pha.mp4"
    elif lenh == "khampha":
        kq = await phieuluu.kham_pha(KHO, ts, RNG, hs, tham or None)
    elif lenh == "timduoc":
        kq = await phieuluu.tim_duoc(KHO, ts, RNG, hs)
    elif lenh == "duykysi":
        kq = await phieuluu.duy_ky_si(KHO, ts, RNG, hs)
    elif lenh == "monphai":
        if tham:
            kq = await tongmon.gia_nhap(KHO, ts, tham, RNG)
        else:
            kq = KetQua(tieu_de="Các tông môn", anh="thanh_van_mon.png")
            for mp in dl_monphai.DANH_SACH.values():
                kq.them(f"**{mp.ten}** *({mp.tinh_chat})* — {mp.dia_the}. {mp.mo_ta.split('.')[0]}. "
                        f"Nhận đệ tử từ {ten_canh_gioi(mp.yeu_cau_canh_gioi, mp.yeu_cau_tang)}.")
            opts = "".join(f'<option value="{m.ma}">{m.ten}</option>' for m in dl_monphai.DANH_SACH.values())
            chon = ('<div class="hang">'
                    f'<select id="mp">{opts}</select>'
                    '<button onclick="chon(\'monphai\',\'mp\')">Xin nhập môn</button></div>')
            return goi_ra(kq, chon)
    elif lenh == "nhiemvu":
        kq = await tongmon.nhan_viec(KHO, ts, RNG)
    elif lenh == "viecdi":
        dangviec = await KHO.viec_hien_tai(ts.user_id)
        if dangviec:
            v = await tongmon.di_viec(KHO, ts, RNG, hs)
            kq = v if v.thanh_cong else await tongmon.nop_viec(KHO, ts)
            if not kq.thanh_cong:
                kq = v
        else:
            kq = KetQua(tieu_de="Chưa nhận việc", van=["Chấp sự đường vẫn mở. Tới đó trước đã."])
    elif lenh == "sotay":
        from tuchan.data import congthuc as dl_ct
        biet = await KHO.so_tay(ts.user_id)
        kq = KetQua(tieu_de="Sổ tay trong đầu ngươi")
        if not biet:
            kq.them("Trống trơn. Chưa ai truyền cho ngươi thứ gì.")
        else:
            for m in biet:
                c = dl_ct.lay(m)
                if c:
                    kq.them(f"**{c.ten}** — {c.mo_ta}")
            opts = "".join(f'<option value="{m}">{dl_ct.lay(m).ten}</option>'
                           for m in biet if dl_ct.lay(m))
            chon = ('<div class="hang">'
                    f'<select id="ct">{opts}</select>'
                    '<button onclick="chon(\'luyen\',\'ct\')">Mở lò / quai búa</button></div>')
            return goi_ra(kq, chon)
    elif lenh in ("luyendan", "luyen"):
        from tuchan.data import congthuc as dl_ct
        ma = tham or next(iter(await KHO.so_tay(ts.user_id)), "")
        if ma in dl_ct.KHI_PHUONG:
            kq = await luyenche.luyen_khi(KHO, ts, ma, RNG, hs)
        elif ma in dl_ct.DAN_PHUONG:
            kq = await luyenche.luyen_dan(KHO, ts, ma, RNG, hs)
        else:
            kq = KetQua(tieu_de="Không có gì để luyện",
                        van=["Ngươi chưa thuộc đan phương nào. Đi tìm ngọc giản, hoặc xin vào một tông môn."])
    elif lenh == "cuahang":
        kq = await giaothuong.xem_hang(KHO, ts, hs, RNG)
    elif lenh == "tuido":
        from tuchan.vanphong import liet_ke_tui, mo_ta_linh_thach, mo_ta_phap_bao
        tui = await KHO.tui(ts.user_id)
        kq = KetQua(tieu_de="Túi càn khôn")
        if not tui:
            kq.them("Ngươi lộn ngược cái túi. Rơi ra một hạt bụi, và không có gì khác.")
        for loai, nhan in (("duoc_lieu", "Dược liệu"), ("vat_lieu", "Vật liệu"), ("dan_duoc", "Đan dược"),
                           ("phap_bao", "Pháp bảo"), ("ky_vat", "Vật khác")):
            s = liet_ke_tui(tui, loai, 40)
            if s:
                kq.them(f"**{nhan}:** {s}")
        kq.them(mo_ta_phap_bao(ts.phap_bao))
        kq.them(mo_ta_linh_thach(ts.linh_thach))
    elif lenh == "vatpham":
        from tuchan.data import vatpham as dl_vp
        if not tham:
            uu_tien = [m for m, v in dl_vp.DANH_MUC.items() if v.tranh]
            con_lai = [m for m in dl_vp.DANH_MUC if m not in uu_tien]
            opts = "".join(f'<option value="{m}">{dl_vp.ten(m)}</option>' for m in uu_tien + sorted(con_lai))
            chon = ('<div class="ghi">Hỏi kỹ về món nào?</div><div class="hang">'
                    f'<select id="vp_xem">{opts}</select>'
                    '<button onclick="chon(\'vatpham\',\'vp_xem\')">Cầm lên xem</button></div>')
            return goi_ra(KetQua(tieu_de="Giá hàng", van=[""]), chon)
        vp = dl_vp.lay(tham)
        if vp is None:
            kq = KetQua(tieu_de="Không có món ấy", van=["Chưa ai nghe nói tới thứ đó."])
        else:
            kq = KetQua(tieu_de=vp.ten, anh=dl_vp.tranh_cua(vp))
            kq.them(vp.mo_ta)
            kq.them(f"Người trong nghề xếp nó vào hàng **{vp.pham} phẩm**.")
            if vp.loai_vu_khi:
                from tuchan.he.thutich import LOI_VU_KHI
                kq.them(f"Lối dùng: **{LOI_VU_KHI.get(vp.loai_vu_khi, 'khí giới')}**.")
            if vp.ghi_chu:
                kq.them(f"*{vp.ghi_chu}*")
    elif lenh in ("canhgioi", "kiepnan", "binhkhi", "linhdan", "kimdan"):
        from tuchan.he import thutich
        kq = {"canhgioi": thutich.bia_muoi_bac, "kiepnan": thutich.chin_cua_ai,
              "binhkhi": thutich.binh_khi_pho, "linhdan": thutich.dan_pho,
              "kimdan": thutich.kim_dan_pho}[lenh]()
    elif lenh in ("uongdan", "deo", "mua"):
        from tuchan.data import vatpham as dl_vp
        tui = await KHO.tui(ts.user_id)
        if lenh == "mua":
            nguon = list(giaothuong.hang_ban_cho(ts))
            nhan, viec = "Mua thứ gì?", "Trả linh thạch"
        else:
            loai = "dan_duoc" if lenh == "uongdan" else "phap_bao"
            nguon = [m for m in tui if (dl_vp.lay(m) and dl_vp.lay(m).loai == loai)]
            nhan = "Nuốt viên nào?" if lenh == "uongdan" else "Cầm món nào?"
            viec = "Uống" if lenh == "uongdan" else "Đeo lên người"
        if not tham:
            if not nguon:
                kq = KetQua(tieu_de="Không có gì",
                            van=["Ngươi lục túi một lượt, rồi thôi. Trong đó không có thứ ngươi cần."])
            else:
                opts = "".join(f'<option value="{m}">{dl_vp.ten(m)}</option>' for m in sorted(nguon))
                chon = (f'<div class="ghi">{nhan}</div><div class="hang">'
                        f'<select id="vp_{lenh}">{opts}</select>'
                        f'<button onclick="chon(\'{lenh}\',\'vp_{lenh}\')">{viec}</button></div>')
                return goi_ra(KetQua(tieu_de=nhan, van=[""]), chon)
        elif lenh == "uongdan":
            kq = await luyenche.uong_dan(KHO, ts, tham, RNG)
        elif lenh == "deo":
            kq = await luyenche.deo_phap_bao(KHO, ts, tham)
        else:
            kq = await giaothuong.mua(KHO, ts, dl_vp.ten(tham), 1, hs)
    elif lenh == "thientuong":
        kq = await thienbien.xem_thien_bien(KHO, 1)
    elif lenh == "sukien":
        kq = await thienbien.khoi_su_kien(KHO, 1, None, RNG)
    elif lenh == "nhatky":
        dong = await KHO.doc_nhat_ky(ts.user_id, 10)
        kq = KetQua(tieu_de=f"Thủ ký của {ts.ten}")
        kq.them("\n".join(f"— *{x['noi_dung']}*" for x in dong) or "Trang giấy còn trắng.")
    else:
        kq = KetQua(tieu_de="Không hiểu", van=["Ngươi lẩm bẩm một câu mà chính mình cũng không hiểu."])
    return goi_ra(kq)


async def trang_chu(request):
    return web.Response(text=TRANG, content_type="text/html")


async def khoi_tao(app):
    await KHO.mo()


def tao_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(khoi_tao)
    app.router.add_get("/", trang_chu)
    app.router.add_post("/lenh", xu_ly)
    app.router.add_static("/tranh/", str(config.DUONG_DAN_TRANH))
    config.DUONG_DAN_THANH_ANH.mkdir(parents=True, exist_ok=True)
    app.router.add_static("/thanh_anh/", str(config.DUONG_DAN_THANH_ANH))
    return app


if __name__ == "__main__":
    cong = int(os.getenv("PORT", "8080"))
    web.run_app(tao_app(), host="0.0.0.0", port=cong)
