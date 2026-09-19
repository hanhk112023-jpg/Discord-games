"""Lõi lệnh Telegram — mọi lệnh của bot Tiên Đồ đều đi qua đây.

Triết lý: phần chữ (handler) không được biết ai đang vận nó. `Lo` là cái miệng:
bot thật nói bằng aiogram, diễn tập nói bằng terminal/trình duyệt. Nhờ vậy toàn bộ
kịch bản (nhập đạo, tu luyện, đánh boss, PK có cược) chạy được trong
tools/tele_thutap.py mà không cần mạng.
"""

from __future__ import annotations

import asyncio
import random
from contextvars import ContextVar
from dataclasses import dataclass, field

from .. import config
from ..canhgioi import la_dinh_canh, ten_canh_gioi
from ..data import boss as dl_boss
from ..data import congthuc as dl_congthuc
from ..data import diadanh as dl_diadanh
from ..data import monphai as dl_monphai
from ..data import vatpham
from ..data import xuatthan as dl_xuatthan
from ..he import dauboss as he_boss
from ..he import giaothuong as he_giao
from ..he import luyenche as he_luyen
from ..he import nhanvat as he_nhan
from ..he import phieuluu as he_phieu
from ..he import pk as he_pk
from ..he import thienbien as he_troi
from ..he import thutich as he_tich
from ..he import tongmon as he_tong
from ..he import tuluyen as he_tu
from ..he.ketqua import KetQua
from ..he.thienco import he_so_the_gioi
from .hien_thi import Trang, dinh_dang, xuat


NGUON_TIN = ContextVar("nguon_tin", default="")


def _dong(nut: list, moi_hang: int) -> list[list]:
    """Xếp danh sách nút [(label, cb), ...] thành các hàng."""
    return [nut[i:i + moi_hang] for i in range(0, len(nut), moi_hang)] or []


@dataclass
class TinDen:
    """Một thứ tới từ người dùng: lệnh, nút bấm, hoặc chữ thường."""
    user_id: int
    chat_id: int
    ten: str
    loai: str                       # "lenh" | "cb" | "text"
    data: str = ""
    msg_id: int | None = None       # tin chứa nút — để sửa thay vì gửi mới
    nguon: str = ""                # mini | telegram; rỗng cho diễn tập/thông báo


@dataclass
class TraLoi:
    pages: list[Trang] = field(default_factory=list)
    sua_tin: bool = False
    toast: str | None = None

    @staticmethod
    def cua(kq=None, hang=None, sua_tin=False, toast=None, pages=None):
        if pages is None:
            pages = xuat(kq, hang) if kq is not None else []
        return TraLoi(pages=pages, sua_tin=sua_tin, toast=toast)


class Lo:
    """Cái miệng. Lớp vận hành (aiogram / terminal / web) hiện thực hiện ba việc."""

    async def gui(self, chat_id: int, trang: Trang):
        raise NotImplementedError

    async def sua(self, chat_id: int, msg_id, trang: Trang) -> None:
        raise NotImplementedError

    async def bao(self, user_id: int, text: str) -> None:  # toast trên nút bấm
        pass


class LoNhip(Lo):
    """Một lõi, hai giao diện. Trả lời/sửa tin chỉ về đúng nơi phát sinh lệnh.

    Mã tin Telegram và web độc lập, không được dùng lẫn. Thông báo cho người
    khác và vòng tuần tra vẫn phát qua cả hai giao diện.
    """

    def __init__(self, *los: Lo):
        self.cac = [l for l in los if l is not None]

    @property
    def MA_URL_NUT(self) -> bool:  # ai trong tốp biết render nút url: là được
        return any(getattr(l, "MA_URL_NUT", False) for l in self.cac)

    def _noi_nhan(self):
        nguon = NGUON_TIN.get()
        return [lo for lo in self.cac if not nguon or getattr(lo, "MA_NGUON", "") == nguon]

    async def gui_tat_ca(self, chat_id: int, trang):
        token = NGUON_TIN.set("")
        try:
            return await self.gui(chat_id, trang)
        finally:
            NGUON_TIN.reset(token)

    async def gui(self, chat_id: int, trang) -> int | None:
        thu = None
        for l in self._noi_nhan():
            try:
                ma = await l.gui(chat_id, trang)
                thu = thu if thu is not None else ma
            except Exception:  # một cái miệng lạc (mạng Telegram chập) không được bịt các miệng khác
                continue
        return thu

    async def sua(self, chat_id: int, msg_id, trang) -> None:
        for l in self._noi_nhan():
            try:
                await l.sua(chat_id, msg_id, trang)
            except Exception:
                continue

    async def bao(self, user_id: int, text: str) -> None:
        for l in self._noi_nhan():
            try:
                await l.bao(user_id, text)
            except Exception:
                continue

    async def doi_uid(self, chat_id: int, uid: int) -> None:
        for l in self.cac:
            hook = getattr(l, "doi_uid", None)
            if hook is not None:
                try:
                    await hook(chat_id, uid)
                except Exception:
                    continue


class Long:
    """Bộ não của bot: một thế giới, một giao ước lệnh."""

    def __init__(self, kho, guild_id: int, lo: Lo, rng=None,
                 thu_duyen: bool = False, admin_ids=()):
        self.kho = kho
        self.guild = guild_id
        self.lo = lo
        self.rng = rng or random.Random()
        self.thu_duyen = thu_duyen
        self.admin_ids = set(admin_ids or ())
        self.khoa_lenh = asyncio.Lock()
        self.pending: dict[int, dict] = {}
        self.Lenh: dict[str, tuple] = {}
        self._dang_ky_lenh()

    # ─────────── cổng vào duy nhất ───────────

    async def xu_ly(self, tin: TinDen) -> None:
        # Bot và Mini App cùng một khóa: bấm đúp không nhận thưởng hai lần.
        async with self.khoa_lenh:
            token = NGUON_TIN.set(tin.nguon)
            try:
                await self._xu_ly(tin)
            finally:
                NGUON_TIN.reset(token)

    async def _xu_ly(self, tin: TinDen) -> None:
        await self.kho.danh_thiep_luu(tin.user_id, tin.chat_id, tin.ten or "")
        if tin.loai == "cb":
            await self._xu_ly_nut(tin)
            return
        text = (tin.data or "").strip()
        if self.pending.get(tin.user_id):
            await self._xu_ly_pending(tin, text)
            return
        if not text:
            await self._tra(tin, await self._menu(tin))
            return
        if text[0] in "/!":
            parts = text.lstrip("/!").split(" ", 1)
            ma = parts[0].split("@")[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""
            await self._goi(tin, ma, arg)
            return
        await self._tra(tin, await self._khong_hieu(tin, text))

    async def _goi(self, tin: TinDen, ma: str, arg: str) -> None:
        entry = self.Lenh.get(ma)
        if entry is None:
            await self._tra(tin, await self._khong_hieu(tin, ma))
            return
        ham, can_ts, _mo = entry
        ts = await self.kho.lay_tu_si(tin.user_id)
        if can_ts and ts is None:
            await self._tra(tin, await self._chua_nhap_dao(tin))
            return
        if can_ts and ts.da_chet:
            await self._tra(tin, await self._da_chet(tin))
            return
        try:
            tra = await ham(self, tin, ts, (arg or "").strip())
        except Exception as exc:  # đừng để một lệnh chết làm chết cả bot
            kq = KetQua(tieu_de="Trời nghiêng một tảng",
                        van=[f"Giữa chừng thì có thứ gì đó gãy. Ghi lại đây cho người coi sổ: `{exc}`"],
                        thanh_cong=False)
            tra = TraLoi.cua(kq)
        if tra is not None:
            await self._tra(tin, tra)

    async def _tra(self, tin: TinDen, tra) -> None:
        if tra is None:
            return
        if isinstance(tra, list):
            tra = TraLoi(pages=tra)
        if tra.toast:
            await self.lo.bao(tin.user_id, tra.toast)
        if not tra.pages:
            return
        if tra.sua_tin and tin.msg_id is not None:
            await self.lo.sua(tin.chat_id, tin.msg_id, tra.pages[0])
            for trang in tra.pages[1:]:
                await self.lo.gui(tin.chat_id, trang)
        else:
            for trang in tra.pages:
                await self.lo.gui(tin.chat_id, trang)

    def _dang(self, ma, ham, mo, can_ts=True, bia=()):
        for k in tuple(bia) + (ma,):
            self.Lenh[k] = (ham, can_ts, mo)

    # ─────────── đăng ký lệnh ───────────

    def _dang_ky_lenh(self):
        D = self._dang
        D("start", _lenh_menu, "mở menu", False)
        D("menu", _lenh_menu, "mở menu", False)
        D("mini", _lenh_mini, "mở lối web — động tu luyện trong Telegram", False)
        D("dangky", _lenh_dangky, "nhập đạo", False, ("nhapdao", "battau"))
        D("chuyenthe", _lenh_chuyenthe, "xin kiếp khác cho kẻ đã khuất", False)
        D("nhanvat", _lenh_nhanvat, "nhìn lại chính mình", True, ("nv",))
        D("luyentap", _lenh_luyentap, "toạ quan một canh giờ", True, ("lt",))
        D("thiennhien", _lenh_thiennhien, "dẫn thiên địa nhập thể — nhanh và dữ", True, ("td",))
        D("dotpha", _lenh_dotpha, "xung quan; /dotpha <tên đan> nếu có đan hộ trợ", True, ("dp",))
        D("duongthuong", _lenh_duongthuong, "nằm chờ xương liền lại", True, ("nghi",))
        D("uongdan", _lenh_uongdan, "nuốt một viên đan", True, ("dungdan",))
        D("khampha", _lenh_khampha, "đi vào chốn người ta khuyên đừng đi", True, ("kp",))
        D("diadanh", _lenh_diadanh, "bản đồ giang hồ", True)
        D("timduoc", _lenh_timduoc, "hái thuốc", True)
        D("duykysi", _lenh_duykysi, "đo sức kẻ qua đường", True)
        D("sotay", _lenh_sotay, "sổ tay công thức", True)
        D("sanquai", _lenh_sanquai, "săn yêu thú cày cuốc tu vi & trang bị", True, ("san", "danhquai"))
        D("tranthap", _lenh_tranthap, "khiêu chiến Trấn Yêu Tháp", True, ("thap", "leothap"))
        D("trangbi", _lenh_trangbi, "trang bị pháp bảo vào người: /trangbi <tên>", True, ("mac",))
        D("thaodo", _lenh_thaodo, "tháo trang bị: /thaodo <vị trí>", True, ("thao",))
        D("cuonghoa", _lenh_cuonghoa, "cường hóa trang bị bằng linh thạch: /cuonghoa <tên>", True, ("ch",))
        D("luyendan", _lenh_luyendan, "mở lò luyện đan", True, ("ld",))
        D("luyenkhi", _lenh_luyenkhi, "quai búa rèn khí", True, ("lk",))
        D("deo", _lenh_deo, "nhỏ tinh huyết nhận chủ pháp bảo", True)
        D("tuido", _lenh_tuido, "dốc túi càn khôn", True, ("tui", "bag"))
        D("vatpham", _lenh_vatpham, "hỏi kỹ một món đồ", True, ("vp",))
        D("cuahang", _lenh_cuahang, "xuống chợ", True, ("shop",))
        D("mua", _lenh_mua, "mua hàng", True)
        D("ban", _lenh_ban, "bán hàng", True)
        D("tang", _lenh_tang, "đưa vật cho ai đó", True)
        D("tl", _lenh_tl, "đưa linh thạch", True, ("taolinhthach",))
        D("monphai", _lenh_monphai, "nghe kể về các tông môn", True, ("phai",))
        D("gianhap", _lenh_gianhap, "xin nhập môn", True, ("gia",))
        D("roimon", _lenh_roimon, "xin ra đi", True, ("roi",))
        D("nhiemvu", _lenh_nhiemvu, "chấp sự đường", True, ("vm",))
        D("boss", _lenh_boss, "xem chiến trường yêu vương", True, ("chientruong", "ct"))
        D("bicanh", _lenh_bicanh, "vượt ải huyễn cảnh cá nhân", True)
        D("daboss", _lenh_daboss, "lao vào đánh boss", True, ("danhboss",))
        D("bosssach", _lenh_bosssach, "điểm danh yêu vương", True)
        D("trieuboss", _lenh_trieuboss, "triệu hồi yêu vương (đại năng)", True, ("goiboss",))
        D("pk", _lenh_pk, "thách đấu: /pk <tên> [cược] [sinhtu]", True, ("thidau", "thachdau"))
        D("thach", _lenh_thach, "lời thách đang treo trên đầu", True, ("loithach",))
        D("bangpk", _lenh_bangpk, "bảng tỉ thí", True, ("bangtythi",))
        D("troi", _lenh_troi, "ngửa mặt xem thiên biến", True, ("thientuong",))
        D("sukien", _lenh_sukien, "gọi trời đổi sắc (đại năng)", False)
        D("canhgioi", _lenh_canhgioi, "bia mười bậc", False, ("cg",))
        D("kiepnan", _lenh_kiepnan, "chín cửa ải", False, ("kn",))
        D("binhkhi", _lenh_binhkhi, "Binh Khí Phổ", False)
        D("linhdan", _lenh_linhdan, "Đan Phổ", False)
        D("kimdan", _lenh_kimdan, "chín phẩm kim đan", False)
        D("chidan", _lenh_chidan, "nghe lão bán trà chỉ đường", False, ("huongdan", "help", "giup"))
        D("nhatky", _lenh_nhatky, "đọc lại thủ ký", True)
        D("xoa", _lenh_xoa, "xoá nhân vật, làm lại từ đầu", True)
        D("doi", _lenh_doi, "diễn tập: nhập vào một kẻ khác", False)
        D("tao", _lenh_tao, "diễn tập: gọi ra một kẻ mới", False)

    # ─────────── phương tiện ───────────

    async def hs(self) -> dict:
        return await he_so_the_gioi(self.kho, self.guild)

    def co_quyen(self, tin: TinDen) -> bool:
        return self.thu_duyen or tin.user_id in self.admin_ids

    async def lien_ket(self, uid: int):
        return await self.kho.danh_thiep_cua(uid)

    async def gui_toi(self, uid: int, kq: KetQua, hang=None) -> None:
        chat = await self.lien_ket(uid)
        if not chat:
            return
        for trang in xuat(kq, hang):
            try:
                await getattr(self.lo, "gui_tat_ca", self.lo.gui)(chat, trang)
            except Exception:
                pass

    async def loan(self, dong: str, ngoai_tru=None) -> None:
        """Một câu tin đồn — gửi đi mọi chat bot biết đường tới."""
        html = dinh_dang(dong)
        da_gui: set = set()
        for _uid, chat in await self.kho.danh_thiep_all():
            if chat in da_gui or (ngoai_tru is not None and chat == ngoai_tru):
                continue
            da_gui.add(chat)
            try:
                await getattr(self.lo, "gui_tat_ca", self.lo.gui)(chat, Trang(html=html))
            except Exception:
                pass

    # ─────────── khung cửa chung ───────────

    async def _menu(self, tin: TinDen) -> TraLoi:
        ts = await self.kho.lay_tu_si(tin.user_id)
        kq = KetQua(tieu_de="Tiên Đồ Vô Tận", anh="bia_tien_do.png")
        if ts is None:
            kq.them("Ngươi đứng dưới chân núi. Trong túi không có gì ngoài một cái tên, "
                    "trên đầu không có gì ngoài một bầu trời quá rộng.\n\n"
                    "Bấm **Nhập đạo** để bắt đầu.")
            hang = [[("🧘 Nhập đạo", "l:dangky"), ("📜 Nghe chỉ dẫn", "l:chidan")]]
            if config.TELE_MINIAPP_URL and getattr(self.lo, "MA_URL_NUT", False):
                hang.insert(0, [("⛩ Chơi Tiên Đồ · Mini App", "url:" + config.TELE_MINIAPP_URL)])
            return TraLoi.cua(kq, hang)
        ghi = ""
        if ts.dang_bi_thuong:
            ghi = "\n*Thương thế còn chưa lành — nhớ dưỡng thương.*"
        if ts.da_chet:
            ghi = "\n**Ngươi đã khuất.** Bấm Chuyển thế để xin kiếp khác."
        ph = f"\nĐệ tử {dl_monphai.lay(ts.mon_phai).ten}." if ts.mon_phai and dl_monphai.lay(ts.mon_phai) else "\nTán tu, không môn phái."
        kq.them(f"**{ts.ten}** — {ten_canh_gioi(ts.canh_gioi, ts.tang)}.{ph}{ghi}")
        hang = [
            [("🧘 Toạ quan", "l:luyentap"), ("🌩 Thiên địa", "l:thiennhien"), ("⚡ Xung quan", "l:dotpha")],
            [("🐲 Chiến trường", "l:boss"), ("⚔ PK", "l:pk"), ("🏆 Bảng PK", "l:bangpk")],
            [("🎒 Túi đồ", "l:tuido"), ("🏪 Chợ", "l:cuahang"), ("🔥 Lò", "l:sotay")],
            [("⛰ Khám phá", "l:khampha"), ("🌿 Hái thuốc", "l:timduoc"), ("🗡 Tỉ thí dạo", "l:duykysi")],
            [("🏯 Tông môn", "l:monphai"), ("📋 Việc môn", "l:nhiemvu"), ("🌌 Trời", "l:troi")],
            [("🕯 Chuyển thế", "l:chuyenthe"), ("🪧 Bia cảnh giới", "l:canhgioi"), ("📜 Chỉ dẫn", "l:chidan")],
        ]
        if config.TELE_MINIAPP_URL and getattr(self.lo, "MA_URL_NUT", False):
            hang.insert(0, [("⛩ Chơi Tiên Đồ · Mini App", "url:" + config.TELE_MINIAPP_URL)])
        return TraLoi.cua(kq, hang)

    async def _chua_nhap_dao(self, tin: TinDen) -> TraLoi:
        kq = KetQua(tieu_de="Chưa nhập đạo", anh="bia_tien_do.png",
                    van=["Ngươi còn chưa bước chân vào cửa đạo. Tên ngươi không có trong sổ, "
                         "khí tức ngươi không khác gì kẻ gánh nước ngoài chợ."],
                    thanh_cong=False)
        return TraLoi.cua(kq, [[("🧘 Nhập đạo", "l:dangky")]])

    async def _da_chet(self, tin: TinDen) -> TraLoi:
        kq = KetQua(tieu_de="Người đã khuất", mau=config.MAU_HUYET,
                    van=["Xác đã lạnh, đạo hạnh đã tan theo gió.\n\n"
                         "*Nếu còn muốn đi tiếp, hãy chuyển thế — nhưng đừng mong mang được gì sang "
                         "kiếp sau, ngoài cảm giác mơ hồ rằng mình đã từng ngã ở đâu đó.*"],
                    thanh_cong=False)
        return TraLoi.cua(kq, [[("🕯 Chuyển thế", "l:chuyenthe"), ("🏮 Menu", "menu")]])

    async def _khong_hieu(self, tin: TinDen, chuoi: str) -> TraLoi:
        kq = KetQua(van=[f"Ngươi lẩm bẩm *“{chuoi[:160]}”* — không ai đáp, chưa có luật nào chép thế. "
                         "Gõ /chidan để nghe lão bán trà chỉ đường."],
                    thanh_cong=False)
        return TraLoi.cua(kq, [[("🏮 Menu", "menu"), ("📜 Chỉ dẫn", "l:chidan")]])

    # ─────────── nhập đạo / chuyển thế ───────────

    async def _chon_xuat_than(self, tin: TinDen, ts, ma: str) -> None:
        p = self.pending.setdefault(tin.user_id, {})
        p["mode"] = p.get("mode", "dangky")
        p["xt"] = self.rng.choice(list(dl_xuatthan.DANH_SACH.keys())) if ma == "ngau" else ma
        xt = dl_xuatthan.lay(p["xt"])
        if xt is None:
            xt = dl_xuatthan.lay("pham_nhan")
            p["xt"] = "pham_nhan"
        if p["mode"] == "chuyenthe" and p.get("ten"):
            await self._hoan_thanh_dang_ky(tin, p)
            return
        if p.get("ten") and p.get("gt"):
            await self._hoan_thanh_dang_ky(tin, p)
            return
        if p.get("ten"):
            # tên đã khai, thiếu mỗi giới tính — hỏi nốt rồi mới đóng sổ
            await self._tra(tin, TraLoi(
                pages=[Trang(html=f"<b>{dinh_dang(xt.ten)}</b> — cái tên <i>{dinh_dang(p['ten'])}</i> "
                                  "đã ghi. Còn một câu cuối: ngươi là nam hay nữ?")],
                sua_tin=True))
            await self.lo.gui(tin.chat_id, Trang(html="Chọn ở hàng nút.", hang=[
                [("🧑 Nam", "gt:nam"), ("👩 Nữ", "gt:nu")]]))
            return
        if p.get("gt"):
            await self._tra(tin, TraLoi(
                pages=[Trang(html=f"<b>{dinh_dang(xt.ten)}</b> — đã chép vào sổ tạm. "
                                  "Khai đạo hiệu kiếp này đi (gõ một cái tên).")],
                sua_tin=True))
            return
        await self._tra(tin, TraLoi(
            pages=[Trang(html=(f"<b>Kiếp này: {dinh_dang(xt.ten)}</b>\n\n"
                               f"{dinh_dang(xt.mo_ta)}\n\n"
                               f"<i>Linh căn: {dinh_dang(xt.linh_can)}.</i>"))],
            sua_tin=True))
        hang = [[("🧑 Nam", "gt:nam"), ("👩 Nữ", "gt:nu"), ("🪶 Mặc định nam", "gt:tu")]]
        await self.lo.gui(tin.chat_id, Trang(
            html="Ngươi là nam hay nữ? (Thế giới này không phân biệt lắm — nhưng sổ thì phải chép đủ.)",
            hang=hang))

    async def _hoan_thanh_dang_ky(self, tin: TinDen, p: dict) -> None:
        mode = p.get("mode", "dangky")
        ten = (p.get("ten") or "Vô Danh").strip()
        gt = p.get("gt", "nam")
        xt = p.get("xt", "pham_nhan")
        self.pending.pop(tin.user_id, None)
        if mode == "chuyenthe":
            ts_cu = await self.kho.lay_tu_si(tin.user_id)
            if ts_cu is None or not ts_cu.da_chet:
                await self._tra(tin, TraLoi.cua(KetQua(
                    tieu_de="Chuyển thế muộn",
                    van=["Bên kia cửa vẫn chưa có chỗ cho ngươi. Hãy sống đã."],
                    thanh_cong=False)))
                return
            kq = await he_nhan.chuyen_the(self.kho, ts_cu, ten, xt, self.rng)
        else:
            kq = await he_nhan.tao_nhan_vat(self.kho, tin.user_id, self.guild, ten, gt, xt, self.rng)
            if kq.thanh_cong:
                kq.thanh_anh = "nhap_dao.mp4"
        await self._tra(tin, TraLoi.cua(kq, [[("🏮 Menu", "menu")]]))

    async def _xu_ly_pending(self, tin: TinDen, text: str) -> None:
        p = self.pending[tin.user_id]
        if text.lower().lstrip("/!").split(" ")[0] in ("huy", "cancel"):
            self.pending.pop(tin.user_id, None)
            await self._tra(tin, TraLoi(pages=[Trang(html="Ngươi xoá luôn cái tên định khai. Cửa đạo vẫn mở.")]))
            return
        p["ten"] = (text[:24] or "Vô Danh").strip()
        await self._hoan_thanh_dang_ky(tin, p)

    # ─────────── nút bấm ───────────

    async def _xu_ly_nut(self, tin: TinDen) -> None:
        loai, _, tham = (tin.data or "").partition(":")
        ts = await self.kho.lay_tu_si(tin.user_id)
        if loai == "l":
            ma, _, arg = tham.partition(" ")
            await self._goi(tin, ma, arg)
            return
        if loai == "menu":
            await self._tra(tin, await self._menu(tin))
            return
        if loai == "xt":
            await self._chon_xuat_than(tin, ts, tham)
            return
        if loai == "gt":
            p = self.pending.setdefault(tin.user_id, {"mode": "dangky"})
            p["gt"] = {"nu": "nữ", "nam": "nam"}.get(tham, "nam")
            if p.get("xt") and p.get("ten"):
                await self._hoan_thanh_dang_ky(tin, p)
                return
            await self._tra(tin, TraLoi(
                pages=[Trang(html="<b>Khai đạo hiệu.</b>\n\nGõ một cái tên — nó sẽ nằm trong sổ sinh tử "
                                  "cho tới khi trời xoá. (Gõ /huy để nghĩ lại.)")],
                sua_tin=True))
            return
        if loai == "sp":
            await self._mua_nut(tin, ts, tham)
            return
        if loai == "bd":
            await self._bag_nut(tin, ts, tham)
            return
        if loai == "mp":
            if ts is None:
                return
            await self._tra(tin, TraLoi.cua(await he_tong.gia_nhap(self.kho, ts, tham, self.rng)))
            return
        if loai == "ct":
            await self._luyen_nut(tin, ts, tham)
            return
        if loai == "bs":
            await self._boss_nut(tin, ts, tham)
            return
        if loai == "pk":
            await self._pk_nut(tin, ts, tham)
            return
        if loai == "sk":
            if not self.co_quyen(tin):
                await self._tra(tin, TraLoi(pages=[Trang(html="Ngươi không giữ chìa của trời.")]))
                return
            kq = await he_troi.khoi_su_kien(self.kho, self.guild, (tham or None) if tham != "_" else None,
                                            self.rng)
            await self._tra(tin, TraLoi.cua(kq))
            return
        if loai == "nv":
            if ts is None:
                return
            await self._nhiem_viec(tin, ts, tham or "xem")
            return
        await self._tra(tin, TraLoi(pages=[Trang(html="Cái nút này chưa ai dạy cách bấm.")]))

    # ─────────── trang túi & chợ & lò (dùng chung cho lệnh và nút) ───────────

    async def _trang_tui(self, tin: TinDen, ts) -> TraLoi:
        from ..vanphong import mo_ta_linh_thach, mo_ta_phap_bao
        tui = await self.kho.tui(ts.user_id)
        kq = KetQua(tieu_de=f"Túi càn khôn của {ts.ten}")
        nut = []
        if not tui:
            kq.them("Ngươi lộn ngược cái túi. Rơi ra một hạt bụi, và không có gì khác.")
        else:
            nhom = []
            for ma, sl in sorted(tui.items()):
                vp = vatpham.lay(ma)
                if not vp:
                    continue
                nhom.append(f"• {vp.ten}×{sl} · {vp.pham} phẩm")
                if len(nhom) >= 24:
                    break
            kq.them("\n".join(nhom))
            if len(tui) > 24:
                kq.chu_thich = f"…còn {len(tui) - 24} món nữa. /vatpham <tên> để hỏi kỹ."
            dem = 0
            for ma, sl in tui.items():
                vp = vatpham.lay(ma)
                if not vp or dem >= 8:
                    continue
                if vp.loai == "dan_duoc":
                    nut.append((f"Uống {vp.ten}", f"bd:uong:{ma}"))
                    dem += 1
                elif vp.loai == "phap_bao":
                    nut.append((f"Đeo {vp.ten}", f"bd:deo:{ma}"))
                    dem += 1
                elif vp.gia > 1 and sl > 1:
                    nut.append((f"Bán {vp.ten}×1", f"bd:ban:{ma}"))
                    dem += 1
        kq.them(mo_ta_phap_bao(ts.phap_bao))
        kq.them(mo_ta_linh_thach(ts.linh_thach))
        return TraLoi.cua(kq, _dong(nut, 2) or None)

    async def _trang_chợ(self, tin: TinDen, ts) -> TraLoi:
        hs = await self.hs()
        kq = await he_giao.xem_hang(self.kho, ts, hs, self.rng)
        hang = _dong([(vatpham.ten(m), f"sp:{m}") for m in he_giao.hang_ban_cho(ts)[:18]], 3)
        return TraLoi.cua(kq, hang or None)

    async def _xem_vatpham(self, ma: str) -> KetQua:
        vp = vatpham.lay(ma)
        if vp is None:
            return KetQua(tieu_de="Không có món ấy",
                          van=["Chưa ai nghe nói tới thứ đó."], thanh_cong=False)
        kq = KetQua(tieu_de=vp.ten, anh=vatpham.tranh_cua(vp) or None)
        kq.them(vp.mo_ta)
        kq.them(f"Người trong nghề xếp nó vào hàng **{vp.pham} phẩm**.")
        if vp.loai_vu_khi:
            kq.them(f"Lối dùng: **{he_tich.LOI_VU_KHI.get(vp.loai_vu_khi, 'khí giới')}**.")
        if vp.ghi_chu:
            kq.them(f"*{vp.ghi_chu}*")
        return kq

    async def _mua_nut(self, tin: TinDen, ts, ma: str) -> None:
        if ts is None:
            await self._tra(tin, await self._chua_nhap_dao(tin))
            return
        vp = vatpham.lay(ma)
        if vp is None:
            await self._tra(tin, TraLoi(pages=[Trang(html="Món này chợ không bày nữa.")]))
            return
        hs = await self.hs()
        kq = await he_giao.mua(self.kho, ts, vp.ten, 1, hs)
        await self._tra(tin, TraLoi.cua(kq, toast="Xong rồi." if kq.thanh_cong else "Không mua được."))

    async def _bag_nut(self, tin: TinDen, ts, tham: str) -> None:
        if ts is None:
            return
        viec, _, ma = (tham or "").partition(":")
        if viec == "uong":
            kq = await he_luyen.uong_dan(self.kho, ts, ma, self.rng)
        elif viec == "deo":
            kq = await he_luyen.deo_phap_bao(self.kho, ts, ma)
        elif viec == "ban":
            kq = await he_giao.ban(self.kho, ts, vatpham.ten(ma), 1, await self.hs())
        elif viec == "xem":
            kq = await self._xem_vatpham(ma)
        else:
            kq = KetQua(van=["Nút này chưa có luật."], thanh_cong=False)
        await self._tra(tin, TraLoi.cua(kq))

    async def _luyen_nut(self, tin: TinDen, ts, tham: str) -> None:
        if ts is None:
            return
        viec, _, ma = (tham or "").partition(":")
        hs = await self.hs()
        if viec == "dan":
            kq = await he_luyen.luyen_dan(self.kho, ts, ma, self.rng, hs)
        elif viec == "khi":
            kq = await he_luyen.luyen_khi(self.kho, ts, ma, self.rng, hs)
        else:
            kq = KetQua(tieu_de="Không hiểu lò này",
                        van=["Công thức đã đổi tên từ lâu."], thanh_cong=False)
        await self._tra(tin, TraLoi.cua(kq))

    async def _nhiem_viec(self, tin: TinDen, ts, viec: str) -> None:
        if viec == "nhan":
            kq = await he_tong.nhan_viec(self.kho, ts, self.rng)
        elif viec == "di":
            kq = await he_tong.di_viec(self.kho, ts, self.rng, await self.hs())
        elif viec == "nop":
            kq = await he_tong.nop_viec(self.kho, ts)
        else:
            kq = await he_tong.xem_viec(self.kho, ts)
            hang = [[("Nhận việc", "nv:nhan"), ("Lên đường", "nv:di"), ("Nộp việc", "nv:nop")]]
            await self._tra(tin, TraLoi.cua(kq, hang))
            return
        await self._tra(tin, TraLoi.cua(kq))

    # ─────────── boss ───────────

    async def _boss_nut(self, tin: TinDen, ts, tham: str) -> None:
        viec, _, ma = (tham or "").partition(":")
        if viec == "view":
            kq = await he_boss.hien_trang(self.kho, self.guild)
            if kq.du_lieu.get("co_boss"):
                hang = [[("⚔ Lao vào đánh", "bs:go"), ("👀 Xem lại", "bs:view")]]
            else:
                hang = [[("🐲 Triệu yêu vương", "bs:trieu:_"), ("📜 Điểm danh", "bs:sach")]]
            await self._tra(tin, TraLoi.cua(kq, hang, sua_tin=True))
            return
        if ts is None:
            await self._tra(tin, await self._chua_nhap_dao(tin))
            return
        if viec == "go":
            kq = await he_boss.danh_thuong(self.kho, ts, self.guild, self.rng, await self.hs())
            await self._tra(tin, TraLoi.cua(kq, [[("⚔ Đánh tiếp khi đã lại sức", "bs:go")],
                                                 [("👀 Chiến trường", "bs:view")]]))
            for dong in (kq.du_lieu.get("thong_bao") or []):
                await self.loan(dong, ngoai_tru=tin.chat_id)
            if kq.du_lieu.get("boss_chet"):
                await self.loan(kq.chu_thich or f"{ts.ten} đã hạ boss.", ngoai_tru=tin.chat_id)
            return
        if viec == "trieu":
            if not self.co_quyen(tin):
                await self._tra(tin, TraLoi.cua(KetQua(
                    tieu_de="Ngươi chưa đủ tư cách gọi chúng dậy",
                    van=["Triệu yêu vương là đem cả một vùng ra đặt cược. "
                         "Trời chỉ cho kẻ giữ sổ làm chuyện đó — cứ chờ, chúng tự dậy."],
                    thanh_cong=False)))
                return
            kq = await he_boss.chieu_muoi(self.kho, self.guild, self.rng,
                                          (ma if ma and ma != "_" else None), tin.user_id)
            await self._tra(tin, TraLoi.cua(kq))
            for dong in (kq.du_lieu.get("thong_bao") or []):
                await self.loan(dong, ngoai_tru=tin.chat_id)
            return
        if viec == "sach":
            await self._tra(tin, await _lenh_bosssach(self, tin, ts, ""))
            return
        await self._tra(tin, TraLoi(pages=[Trang(html="Nút boss này chưa có luật.")]))

    # ─────────── PK ───────────

    async def _pk_nut(self, tin: TinDen, ts, tham: str) -> None:
        viec, _, so = (tham or "").partition(":")
        so = so.lstrip("-")
        if viec == "c":
            if ts is None:
                return
            b = await self.kho.lay_tu_si(int(so)) if so.isdigit() else None
            if b is None:
                await self._tra(tin, TraLoi(pages=[Trang(html="Kẻ đó không còn trong sổ.")]))
                return
            ma, kq = await he_pk.thach_thuc(self.kho, ts, b, 0, False)
            if not kq.thanh_cong:
                await self._tra(tin, TraLoi.cua(kq))
                return
            hang = [[("⚔ Ứng chiến", f"pk:y:{ma}"), ("✋ Khước từ", f"pk:n:{ma}")]]
            chat_b = await self.lien_ket(b.user_id)
            if chat_b and chat_b != tin.chat_id:
                await self.gui_toi(b.user_id, kq, hang)
            await self._tra(tin, TraLoi.cua(kq, hang))
            return
        if not so.isdigit():
            await self._tra(tin, TraLoi(pages=[Trang(html="Lời thách ấy đã tan.")]))
            return
        ma = int(so)
        thach = await self.kho.thach_lay(ma)
        if thach is None:
            await self._tra(tin, TraLoi(pages=[Trang(html="Sân đã vắng người. Lời thách này hết hạn rồi — "
                                                        "muốn đánh nữa thì thách lại từ đầu.")]))
            return
        if viec == "y":
            if ts is None or (ts.user_id != thach["b_id"] and not self.thu_duyen):
                await self._tra(tin, TraLoi(pages=[Trang(html="Lời thách này không gửi cho ngươi. Đứng xem thôi.")]))
                return
            nguoi = ts if ts.user_id == thach["b_id"] else await self.kho.lay_tu_si(thach["b_id"])
            if nguoi is None:
                return
            kq = await he_pk.ung_chien(self.kho, ma, nguoi, self.rng, await self.hs())
            await self._tra(tin, TraLoi.cua(kq))
            chat_a = await self.lien_ket(thach["a_id"])
            if chat_a and chat_a != tin.chat_id:
                await self.loan(f"⚔ Trận **{thach['a_ten']} — {nguoi.ten}** đã ngã ngũ. "
                                "Kết quả nằm trong chat của người trong cuộc.", ngoai_tru=tin.chat_id)
            return
        if viec == "n":
            if ts is None or (ts.user_id != thach["b_id"] and not self.thu_duyen):
                await self._tra(tin, TraLoi(pages=[Trang(html="Ngươi không phải kẻ được thách.")]))
                return
            nguoi = ts if ts.user_id == thach["b_id"] else await self.kho.lay_tu_si(thach["b_id"])
            if nguoi is None:
                return
            kq = await he_pk.tu_khuoc(self.kho, ma, nguoi)
            await self._tra(tin, TraLoi.cua(kq))
            await self.loan(f"**{nguoi.ten}** khước từ lời thách của **{thach['a_ten']}**. "
                            "Đám đông tản đi, hơi thất vọng.", ngoai_tru=tin.chat_id)
            return
        if viec == "x":
            if ts is None or ts.user_id != thach["a_id"]:
                return
            await self._tra(tin, TraLoi.cua(await he_pk.huy_thach(self.kho, ma, ts)))
            return


# ═══════════════════════ các hàm lệnh (chữ ký chung: core, tin, ts, arg) ═══════════════════════

def _tach_so(arg: str) -> tuple[str, int]:
    """'Hồi Khí Đan 3' -> ('Hồi Khí Đan', 3). Không có số thì coi là 1."""
    words = (arg or "").split()
    n = 1
    if words and words[-1].isdigit():
        n = max(1, min(99, int(words.pop())))
    return " ".join(words), n


def _vat_cua_tu(arg: str) -> tuple[str, str | None, int]:
    """/tang <người> <vật> [số] — cắt từ phải sang vì cả hai tên đều có dấu cách."""
    words = (arg or "").split()
    n = 1
    if words and words[-1].isdigit():
        n = max(1, min(99, int(words.pop())))
    for i in range(len(words) - 1, 0, -1):
        ma = he_giao.tim_hang(" ".join(words[i:]))
        if ma:
            return " ".join(words[:i]), ma, n
    return " ".join(words), None, n


async def _lenh_menu(core, tin, ts, arg):
    return await core._menu(tin)


async def _lenh_mini(core, tin, ts, arg):
    if not config.TELE_MINIAPP_URL:
        return TraLoi.cua(KetQua(
            tieu_de="Chưa có cửa động",
            van=["Trời đất bên này chỉ có chữ và nút bấm. Cái động khô dành cho lối web "
                 "chưa được khoét — người giữ vườn chưa mở cổng. Cứ chơi ở đây, sổ sách "
                 "một đường như nhau."],
            thanh_cong=False))
    kq = KetQua(tieu_de="Cửa động", anh="bia_tien_do.png",
                van=["Sau lưng núi có một cái động khô, bàn đá đã lau, đèn dầu đã thắp. "
                     "Vào đó ngồi — cùng một thế giới, cùng một cuốn sổ, chỉ khác là "
                     "ngươi bấm tay thay vì gõ chữ."])
    return TraLoi.cua(kq, [[("🏮 Vào động", "url:" + config.TELE_MINIAPP_URL)]])


# ── tu luyện ──

async def _lenh_nhanvat(core, tin, ts, arg):
    return TraLoi.cua(await he_nhan.xem_nhan_vat(core.kho, ts, await core.hs()))


async def _lenh_luyentap(core, tin, ts, arg):
    return TraLoi.cua(await he_tu.luyen_tap(core.kho, ts, core.rng, await core.hs()))


async def _lenh_thiennhien(core, tin, ts, arg):
    return TraLoi.cua(await he_tu.hap_thu_thien_dia(core.kho, ts, core.rng, await core.hs()))


async def _lenh_dotpha(core, tin, ts, arg):
    dung_dan = he_giao.tim_hang(arg) if arg else None
    if arg and dung_dan is None:
        return TraLoi.cua(KetQua(tieu_de="Không có đan ấy",
                                 van=[f"Túi ngươi không có thứ nào gần giống *“{arg[:60]}”*. "
                                      "Nếu định xung quan tay không thì gõ lại: `/dotpha`."],
                                 thanh_cong=False))
    len_bac = la_dinh_canh(ts.canh_gioi, ts.tang)
    kq = await he_tu.dot_pha(core.kho, ts, core.rng, await core.hs(), dung_dan)
    if kq.du_lieu.get("thanh_cong") and len_bac:
        kq.thanh_anh = "dot_pha.mp4"
    return TraLoi.cua(kq)


async def _lenh_duongthuong(core, tin, ts, arg):
    ts.thuong_toi = 0
    ts.than_the = 100
    await core.kho.luu(ts)
    cs = ts.tinh_chi_so()
    kq = KetQua(tieu_de="Vận khí điều tức — Hồi phục toàn diện")
    kq.them(
        f"💖 **Vận chuyển chu thiên trị thương thành công!**\n"
        f"• ❤️ Khí Huyết (HP): `{cs['hp_max']:,} / {cs['hp_max']:,}` (100%)\n"
        f"• 🔷 Chân Khí (MP): `{cs['mp_max']:,} / {cs['mp_max']:,}`\n"
        f"Thân thể sung mãn, kinh mạch thông suốt. Đạo hữu đã sẵn sàng tiếp tục chiến đấu và tu luyện!"
    )
    return TraLoi.cua(kq)


async def _lenh_uongdan(core, tin, ts, arg):
    if arg:
        ma = he_giao.tim_hang(arg)
        if ma is None:
            return TraLoi.cua(KetQua(van=["Ngươi mò trong túi mà không thấy thứ nào tên như thế."],
                                     thanh_cong=False))
        return TraLoi.cua(await he_luyen.uong_dan(core.kho, ts, ma, core.rng))
    tui = await core.kho.tui(ts.user_id)
    ho = [(vatpham.ten(m), f"bd:uong:{m}") for m in tui
          if vatpham.lay(m) and vatpham.lay(m).loai == "dan_duoc"]
    if not ho:
        return TraLoi.cua(KetQua(tieu_de="Trong túi không có đan",
                                 van=["Chỉ toàn cỏ với đá. Đan thì phải luyện, hoặc phải mua."],
                                 thanh_cong=False))
    kq = KetQua(tieu_de="Nuốt viên nào?")
    kq.them("Ngươi dốc túi ra giữa chiếu. Đan ở đó — mỗi viên là một lần đánh cược với chính mình.")
    return TraLoi.cua(kq, _dong(ho, 2))


# ── phiêu lưu ──

async def _lenh_khampha(core, tin, ts, arg):
    dd = None
    if arg:
        for d in dl_diadanh.DANH_SACH.values():
            if arg.lower() in d.ten.lower() or arg == d.ma:
                dd = d.ma
                break
    return TraLoi.cua(await he_phieu.kham_pha(core.kho, ts, core.rng, await core.hs(), dd))


async def _lenh_diadanh(core, tin, ts, arg):
    kq = KetQua(tieu_de="Bản đồ giang hồ")
    hang = []
    for d in dl_diadanh.DANH_SACH.values():
        phep = d.canh_gioi_toi_thieu <= ts.canh_gioi
        kq.them(f"**{d.ten}** · {'vào được' if phep else 'chưa đủ bậc'} · nguy hiểm {int(d.nguy_hiem * 100)}%\n{d.mo_ta}")
        if phep:
            hang.append((f"Đi {d.ten}", f"l:khampha {d.ma}"))
    return TraLoi.cua(kq, _dong(hang, 2) or None)


async def _lenh_timduoc(core, tin, ts, arg):
    return TraLoi.cua(await he_phieu.tim_duoc(core.kho, ts, core.rng, await core.hs()))


async def _lenh_duykysi(core, tin, ts, arg):
    return TraLoi.cua(await he_phieu.duy_ky_si(core.kho, ts, core.rng, await core.hs()))


# ── săn quái & trấn yêu tháp ──

async def _lenh_sanquai(core, tin, ts, arg):
    from ..he import sanquai
    if not arg:
        kq = KetQua(tieu_de="Sơn Dã Trảm Yêu — Chọn mục tiêu săn quái")
        kq.them("🌲 **DANH SÁCH BÃI SĂN THEO CẢNH GIỚI:**\n")
        hang = []
        for kv_k, kv_v in sanquai.KHU_VUC.items():
            if ts.canh_gioi >= kv_v["canh_gioi_yeu_cau"]:
                kq.them(f"📍 **{kv_v['ten']}** ({kv_v['canh_gioi_ten']}):")
                for mq in kv_v["quai"]:
                    q = sanquai.DANH_SACH_QUAI.get(mq)
                    if q:
                        kq.them(f"• `/sanquai {q.ma}` — **{q.ten}** (HP: {q.hp:,} | Công: {q.cong} | +{q.exp:,} Tu vi)")
                        hang.append((f"⚔️ {q.ten}", f"l:sanquai {q.ma}"))
        kq.them("\nGõ `/sanquai <mã quái>` để khiêu chiến ngay!")
        return TraLoi.cua(kq, _dong(hang, 2) or None)

    ma_quai = arg.strip().lower()
    kq = await sanquai.san_quai(core.kho, ts, ma_quai, core.rng)
    return TraLoi.cua(kq)


async def _lenh_tranthap(core, tin, ts, arg):
    from ..he import sanquai
    kq = await sanquai.vuot_thap(core.kho, ts, core.rng)
    return TraLoi.cua(kq)


async def _lenh_trangbi(core, tin, ts, arg):
    from ..data import vatpham
    if not arg:
        tb = ts.lay_trang_bi()
        ch = ts.lay_cuong_hoa()
        kq = KetQua(tieu_de="Trang bị hiện tại")
        slot_names = {"vu_khi": "Vũ Khí", "giap": "Chiến Giáp", "phap_bao": "Pháp Bảo", "ngoc_boi": "Ngọc Bội"}
        lines = []
        for s_k, s_v in slot_names.items():
            ma = tb.get(s_k)
            cap = ch.get(ma, 0)
            cap_str = f" (+{cap})" if cap > 0 else ""
            ten = f"{vatpham.ten(ma)}{cap_str}" if ma else "*(Trống)*"
            lines.append(f"• **{s_v}:** {ten}")
        kq.them("\n".join(lines))
        kq.them("\nDùng lệnh `/trangbi <tên vật phẩm>` để trang bị món đồ từ túi càn khôn.")
        return TraLoi.cua(kq)

    ma = he_giao.tim_hang(arg)
    if not ma:
        return TraLoi.cua(KetQua(van=[f"Không tìm thấy vật phẩm nào tên gần giống *“{arg}”*."], thanh_cong=False))
    vp = vatpham.lay(ma)
    slot = vp.slot_trang_bi if vp else ""
    if not slot:
        return TraLoi.cua(KetQua(van=[f"**{vp.ten}** không phải là trang bị có thể mang lên người."], thanh_cong=False))
    so = await core.kho.dem_vat(ts.user_id, ma)
    if so <= 0:
        return TraLoi.cua(KetQua(van=[f"Ngươi không có **{vp.ten}** trong túi càn khôn."], thanh_cong=False))

    ts.dat_trang_bi(slot, ma)
    await core.kho.luu(ts)
    cs = ts.tinh_chi_so()
    kq = KetQua(tieu_de="Trang bị thành công")
    kq.them(f"⚔️ Đã trang bị **{vp.ten}** vào vị trí **{slot}**!")
    kq.them(f"📊 Lực chiến mới: **{cs['luc_chien']:,}** (Công: {cs['cong']} | Thủ: {cs['thu']} | Máu: {cs['hp_max']})")
    return TraLoi.cua(kq)


async def _lenh_thaodo(core, tin, ts, arg):
    slot = arg.strip().lower()
    if slot not in ("vu_khi", "giap", "phap_bao", "ngoc_boi"):
        return TraLoi.cua(KetQua(van=["Vị trí không hợp lệ. Chọn: `vu_khi`, `giap`, `phap_bao`, hoặc `ngoc_boi`."], thanh_cong=False))
    da_thao = ts.thao_trang_bi(slot)
    await core.kho.luu(ts)
    if not da_thao:
        return TraLoi.cua(KetQua(van=["Vị trí này đang để trống."], thanh_cong=False))
    vp = vatpham.lay(da_thao)
    ten = vp.ten if vp else da_thao
    return TraLoi.cua(KetQua(van=[f"Đã tháo **{ten}** khỏi vị trí **{slot}**."]))


async def _lenh_cuonghoa(core, tin, ts, arg):
    from ..data import vatpham
    if not arg:
        return TraLoi.cua(KetQua(van=["Gõ `/cuonghoa <tên trang bị>` để nâng cấp trang bị lên +1, +2..."]))
    ma = he_giao.tim_hang(arg)
    if not ma:
        return TraLoi.cua(KetQua(van=[f"Không tìm thấy trang bị *“{arg}”*."], thanh_cong=False))
    vp = vatpham.lay(ma)
    if not vp or not vp.slot_trang_bi:
        return TraLoi.cua(KetQua(van=[f"**{vp.ten if vp else arg}** không phải trang bị để cường hóa."], thanh_cong=False))
    ch = ts.lay_cuong_hoa()
    cap = ch.get(ma, 0)
    if cap >= 10:
        return TraLoi.cua(KetQua(van=[f"**{vp.ten}** đã đạt cấp cường hóa tối đa (+10)!"], thanh_cong=False))
    chi_phi = int(60 * (vp.pham ** 1.4) * (cap + 1))
    if ts.linh_thach < chi_phi:
        return TraLoi.cua(KetQua(van=[f"Không đủ linh thạch! Cần **{chi_phi:,} Linh Thạch** để cường hóa lên +{cap + 1}."], thanh_cong=False))

    ts.linh_thach -= chi_phi
    ts.dat_cuong_hoa(ma, cap + 1)
    await core.kho.luu(ts)
    cs = ts.tinh_chi_so()
    kq = KetQua(tieu_de=f"Cường Hóa Thành Công — {vp.ten} (+{cap + 1})")
    kq.them(f"✨ Chúc mừng! **{vp.ten}** đã được cường hóa lên cấp **+{cap + 1}**!")
    kq.them(f"📊 Thuộc tính trang bị tăng 15%! Lực chiến mới: **{cs['luc_chien']:,}**")
    return TraLoi.cua(kq)


# ── luyện chế ──

async def _lenh_sotay(core, tin, ts, arg):
    biet = await core.kho.so_tay(ts.user_id)
    kq = KetQua(tieu_de="Sổ tay trong đầu ngươi")
    if not biet:
        kq.them("Trống trơn. Chưa ai truyền cho ngươi thứ gì. Ngọc giản nhặt ngoài đường, việc tông môn "
                "ban thưởng, hoặc một vị sư phụ nào đó — ba con đường ấy, không có đường thứ tư.")
        return TraLoi.cua(kq)
    cho = []
    for ma in sorted(biet):
        c = dl_congthuc.lay(ma)
        if not c:
            continue
        kq.them(f"**{c.ten}** — {c.mo_ta}\n*Nguyên liệu: "
                + ", ".join(f"{vatpham.ten(m)}×{n}" for m, n in c.nguyen_lieu.items()) + "*")
        cho.append((("Luyện " if c.loai == "dan" else "Rèn ") + c.ten, f"ct:{c.loai}:{c.ma}"))
    return TraLoi.cua(kq, _dong(cho, 2) or None)


async def _lenh_luyendan(core, tin, ts, arg):
    if arg:
        if arg in dl_congthuc.DAN_PHUONG:
            return TraLoi.cua(await he_luyen.luyen_dan(core.kho, ts, arg, core.rng, await core.hs()))
        ma_sp = he_giao.tim_hang(arg)
        ct = next((c for c in dl_congthuc.DAN_PHUONG.values() if ma_sp and c.thanh_pham == ma_sp), None)
        if ct:
            return TraLoi.cua(await he_luyen.luyen_dan(core.kho, ts, ct.ma, core.rng, await core.hs()))
    return await _lenh_sotay(core, tin, ts, "")


async def _lenh_luyenkhi(core, tin, ts, arg):
    if arg and arg in dl_congthuc.KHI_PHUONG:
        return TraLoi.cua(await he_luyen.luyen_khi(core.kho, ts, arg, core.rng, await core.hs()))
    return await _lenh_sotay(core, tin, ts, "")


async def _lenh_deo(core, tin, ts, arg):
    if arg:
        ma = he_giao.tim_hang(arg)
        if ma:
            return TraLoi.cua(await he_luyen.deo_phap_bao(core.kho, ts, ma))
    tui = await core.kho.tui(ts.user_id)
    ho = [(vatpham.ten(m), f"bd:deo:{m}") for m in tui
          if vatpham.lay(m) and vatpham.lay(m).loai == "phap_bao"]
    if not ho:
        return TraLoi.cua(KetQua(van=["Trong túi không có pháp bảo để nhận chủ. "
                                      "Kiếm cùn trong chợ cũng là kiếm — xuống chợ đi."],
                                 thanh_cong=False))
    return TraLoi.cua(KetQua(tieu_de="Nhận chủ món nào?"), _dong(ho, 2))


async def _lenh_tuido(core, tin, ts, arg):
    return await core._trang_tui(tin, ts)


async def _lenh_vatpham(core, tin, ts, arg):
    ma = he_giao.tim_hang(arg) if arg else None
    if ma is None:
        return TraLoi.cua(KetQua(tieu_de="Hỏi món nào?",
                                 van=["Gõ `/vatpham <tên>` — ví dụ `/vatpham Huyết Hà Ma Đao`."],
                                 thanh_cong=False))
    return TraLoi.cua(await core._xem_vatpham(ma))


# ── giao thương ──

async def _lenh_cuahang(core, tin, ts, arg):
    return await core._trang_chợ(tin, ts)


async def _lenh_mua(core, tin, ts, arg):
    ten, n = _tach_so(arg)
    return TraLoi.cua(await he_giao.mua(core.kho, ts, ten, n, await core.hs()))


async def _lenh_ban(core, tin, ts, arg):
    ten, n = _tach_so(arg)
    return TraLoi.cua(await he_giao.ban(core.kho, ts, ten, n, await core.hs()))


async def _lenh_tang(core, tin, ts, arg):
    ten_nguoi, ma_vat, n = _vat_cua_tu(arg)
    if ma_vat is None:
        return TraLoi.cua(KetQua(van=["Phải nói đủ: `/tang <tên người> <tên vật> [số]`."],
                                 thanh_cong=False))
    doi = await core.kho.tim_theo_ten(ten_nguoi, loai_tru=ts.user_id)
    if doi is None:
        return TraLoi.cua(KetQua(tieu_de="Không tìm thấy người đó",
                                 van=["Sổ sinh tử không có cái tên ấy. Kiểm tra lại coi."],
                                 thanh_cong=False))
    kq = await he_giao.trao_tay(core.kho, ts, doi, ma_vat, n)
    await core.gui_toi(doi.user_id, kq)
    return TraLoi.cua(kq)


async def _lenh_tl(core, tin, ts, arg):
    ten, so = _tach_so(arg)
    doi = await core.kho.tim_theo_ten(ten, loai_tru=ts.user_id)
    if doi is None:
        return TraLoi.cua(KetQua(van=["Không tìm thấy người đó trong sổ."], thanh_cong=False))
    kq = await he_giao.tang_linh_thach(core.kho, ts, doi, so)
    await core.gui_toi(doi.user_id, kq)
    return TraLoi.cua(kq)


# ── tông môn ──

async def _lenh_monphai(core, tin, ts, arg):
    kq = KetQua(tieu_de="Các tông môn", anh="thanh_van_mon.png")
    hang = []
    for mp in dl_monphai.DANH_SACH.values():
        thuoc = ts.mon_phai == mp.ma
        kq.them(f"**{mp.ten}** *({mp.tinh_chat})* — {mp.dia_the}.\n{mp.mo_ta}\n"
                f"Công pháp: *{mp.cong_phap}* · nhận đệ tử từ {ten_canh_gioi(mp.yeu_cau_canh_gioi, mp.yeu_cau_tang)}"
                + (" · **ngươi đang ở đây.**" if thuoc else ""))
        if ts and not thuoc:
            hang.append((f"Nhập {mp.ten}", f"mp:{mp.ma}"))
    return TraLoi.cua(kq, _dong(hang, 2) or None)


async def _lenh_gianhap(core, tin, ts, arg):
    if not arg:
        return await _lenh_monphai(core, tin, ts, "")
    return TraLoi.cua(await he_tong.gia_nhap(core.kho, ts, arg, core.rng))


async def _lenh_roimon(core, tin, ts, arg):
    return TraLoi.cua(await he_tong.roi_mon(core.kho, ts))


async def _lenh_nhiemvu(core, tin, ts, arg):
    viec = (arg or "xem").split(" ")[0]
    await core._nhiem_viec(tin, ts, viec)
    return None


# ── boss ──

async def _lenh_boss(core, tin, ts, arg):
    kq = await he_boss.hien_trang(core.kho, core.guild)
    if kq.du_lieu.get("co_boss"):
        hang = [[("⚔ Lao vào đánh", "bs:go"), ("👀 Xem lại", "bs:view")]]
    else:
        hang = [[("🐲 Triệu yêu vương", "bs:trieu:_"), ("📜 Điểm danh boss", "bs:sach")]]
    return TraLoi.cua(kq, hang)


async def _lenh_daboss(core, tin, ts, arg):
    kq = await he_boss.danh_thuong(core.kho, ts, core.guild, core.rng, await core.hs())
    for dong in (kq.du_lieu.get("thong_bao") or []):
        await core.loan(dong, ngoai_tru=tin.chat_id)
    return TraLoi.cua(kq, [[("⚔ Đánh tiếp khi đã lại sức", "bs:go"), ("👀 Chiến trường", "bs:view")]])


async def _lenh_bosssach(core, tin, ts, arg):
    kq = KetQua(tieu_de="Yêu vương phổ",
                van=["Trong cổ tích kể lại còn nhiều hơn. Ở vùng đất này, từng này kẻ đã thật sự "
                     "đứng dậy mà đi:"])
    hang = []
    for b in dl_boss.DANH_SACH:
        kq.them(f"**{b.ten}** — *{b.hieu}*\n{b.mo_ta}")
        if core.co_quyen(tin):
            hang.append((f"Triệu {b.ten}", f"bs:trieu:{b.ma}"))
    return TraLoi.cua(kq, _dong(hang, 2) or None)


async def _lenh_trieuboss(core, tin, ts, arg):
    if not core.co_quyen(tin):
        return TraLoi.cua(KetQua(tieu_de="Không phải ngươi gọi được",
                                 van=["Chỉ kẻ giữ sổ mới triệu yêu vương. Muốn đánh thì cứ chờ — "
                                      "chúng tự dậy, và thiên hạ sẽ dậy theo."],
                                 thanh_cong=False))
    ma = None
    for b in dl_boss.DANH_SACH:
        if arg and (arg.lower() in b.ten.lower() or arg == b.ma):
            ma = b.ma
            break
    kq = await he_boss.chieu_muoi(core.kho, core.guild, core.rng, ma, tin.user_id)
    for dong in (kq.du_lieu.get("thong_bao") or []):
        await core.loan(dong, ngoai_tru=tin.chat_id)
    return TraLoi.cua(kq)


# ── PK ──

async def _lenh_pk(core, tin, ts, arg):
    if not arg:
        ds = await core.kho.bang_danh_vong(9)
        doi = [t for t in ds if t.user_id != ts.user_id and not t.da_chet]
        if not doi:
            return TraLoi.cua(KetQua(tieu_de="Giang hồ vắng người",
                                     van=["Chưa có ai đáng để thách. Chờ thêm kẻ nhập đạo, "
                                          "hoặc xuống chiến trường mà đánh boss."]))
        hang = [[(f"⚔ {t.ten} · {ten_canh_gioi(t.canh_gioi, t.tang)}", f"pk:c:{t.user_id}")]
                for t in doi[:6]]
        kq = KetQua(tieu_de="Đài tỉ thí", anh="dau_phap.png", mau=config.MAU_HUYET,
                    van=["Bấm để thách — hoặc tự viết lời: `/pk <tên> [số linh thạch cược] [sinhtu]`. "
                         "Cược thì hai bên cùng đặt, thắng ăn cả; sinh tử thì hai bên cùng đặt mạng."])
        return TraLoi.cua(kq, hang)
    words = arg.split()
    cuoc, sinh_tu = 0, False
    if words and words[-1].isdigit():
        cuoc = int(words.pop())
    if words and words[-1].lower() in ("sinhtu", "st", "sinh", "tử", "tuchien"):
        sinh_tu = True
        words.pop()
    ten = " ".join(words)
    doi = await core.kho.tim_theo_ten(ten, loai_tru=ts.user_id)
    if doi is None:
        return TraLoi.cua(KetQua(tieu_de="Không tìm thấy người đó",
                                 van=[f"Trong sổ không có kẻ nào tên gần giống *“{ten[:60]}”*. "
                                      "Khai sai tên thì lời thách chỉ treo vào khoảng không."],
                                 thanh_cong=False))
    ma, kq = await he_pk.thach_thuc(core.kho, ts, doi, cuoc, sinh_tu)
    if not kq.thanh_cong:
        return TraLoi.cua(kq)
    hang = [[("⚔ Ứng chiến" + (f" — cược {cuoc}" if cuoc else ""), f"pk:y:{ma}"),
             ("✋ Khước từ", f"pk:n:{ma}")]]
    await core.gui_toi(doi.user_id, kq, hang)   # gửi tận nơi, phòng khi hai người ở hai chat
    return TraLoi.cua(kq, hang)


async def _lenh_thach(core, tin, ts, arg):
    kq = await he_pk.danh_sach_thach(core.kho, ts)
    cho, gui = await core.kho.thach_cua_toi(ts.user_id)
    nut = []
    for x in cho[:4]:
        nut.append((f"⚔ Ứng chiến {x['a_ten']}", f"pk:y:{x['id']}"))
        nut.append((f"✋ Khước từ {x['a_ten']}", f"pk:n:{x['id']}"))
    for x in gui[:3]:
        nut.append((f"Rút lời tới {x['b_ten']}", f"pk:x:{x['id']}"))
    return TraLoi.cua(kq, _dong(nut, 2) or None)


async def _lenh_bangpk(core, tin, ts, arg):
    return TraLoi.cua(await he_pk.bang_pk(core.kho, ts))


# ── trời đất & thư tịch & lặt vặt ──

async def _lenh_troi(core, tin, ts, arg):
    kq = await he_troi.xem_thien_bien(core.kho, core.guild)
    nut = []
    if core.co_quyen(tin):
        nut.append(("🌩 Ép trời đổi sắc", "sk:_"))
    nut.append(("🐲 Chiến trường", "bs:view"))
    return TraLoi.cua(kq, [nut])


async def _lenh_sukien(core, tin, ts, arg):
    if not core.co_quyen(tin):
        return TraLoi.cua(KetQua(van=["Ngươi không giữ chìa của trời."], thanh_cong=False))
    kq = await he_troi.khoi_su_kien(core.kho, core.guild, (arg or None), core.rng)
    return TraLoi.cua(kq)


async def _lenh_canhgioi(core, tin, ts, arg):
    return TraLoi.cua(he_tich.bia_muoi_bac())


async def _lenh_kiepnan(core, tin, ts, arg):
    return TraLoi.cua(he_tich.chin_cua_ai())


async def _lenh_binhkhi(core, tin, ts, arg):
    nguong = int(arg) if arg.isdigit() and 1 <= int(arg) <= 9 else 1
    return TraLoi.cua(he_tich.binh_khi_pho(nguong))


async def _lenh_linhdan(core, tin, ts, arg):
    return TraLoi.cua(he_tich.dan_pho())


async def _lenh_kimdan(core, tin, ts, arg):
    return TraLoi.cua(he_tich.kim_dan_pho())


async def _lenh_chidan(core, tin, ts, arg):
    kq = KetQua(tieu_de="Lời của lão bán trà", anh="bia_tien_do.png", thanh_anh="giang_ho.mp4")
    kq.them("Lão nhân bán trà bên quan đạo rót cho ngươi một chén, không lấy tiền. Lão nói: "
            "*“Ta nhìn ngươi là biết ngươi mới nhập đạo. Ngồi xuống, ta nói cho mấy câu, "
            "nghe hay không thì tuỳ.”*")
    kq.them("**Tu:** `/luyentap` toạ quan · `/thiennhien` dẫn thiên địa (nhanh, dễ chết) · "
            "`/dotpha` xung quan · `/duongthuong` nằm chờ xương liền.")
    kq.them("**Đi:** `/khampha` vào núi · `/diadanh` xem bản đồ · `/timduoc` hái thuốc · "
            "`/duykysi` đo sức kẻ qua đường.")
    kq.them("**Lửa và búa:** `/sotay` sổ công thức · `/luyendan` · `/luyenkhi` · `/deo` nhận chủ "
            "pháp bảo · `/uongdan` nuốt đan · `/tuido` dốc túi.")
    kq.them("**Người:** `/pk <tên> [cược]` thách đấu — có nút *Ứng chiến*; `/thach` xem lời thách treo; "
            "`/boss` xem chiến trường yêu vương, `/daboss` lao vào đánh; `/bangpk` xem ai đang bất bại.")
    kq.them("**Sinh nhai:** `/cuahang` xuống chợ, `/mua` `/ban` `/tang` `/tl` · "
            "`/monphai` tông môn, `/nhiemvu` việc môn.")
    kq.them("**Chữ nghĩa:** `/canhgioi` bia mười bậc · `/kiepnan` chín cửa ải · `/binhkhi` · `/linhdan` · "
            "`/kimdan` · `/vatpham <tên>` · `/nhatky` thủ ký.")
    kq.them("*“Đừng vội. Kẻ vội thì chết sớm, mà chết sớm thì không ai nhớ tên.”*")
    return TraLoi.cua(kq, [[("🏮 Về menu", "menu")]])


async def _lenh_nhatky(core, tin, ts, arg):
    dong = await core.kho.doc_nhat_ky(ts.user_id, 10)
    kq = KetQua(tieu_de=f"Thủ ký của {ts.ten}")
    kq.them("\n".join(f"— *{x['noi_dung']}*" for x in dong) or "Trang giấy còn trắng.")
    return TraLoi.cua(kq)


async def _lenh_xoa(core, tin, ts, arg):
    if (arg or "").strip() != ts.ten:
        return TraLoi.cua(KetQua(tieu_de="Không xoá đâu cả",
                                 van=["Gõ `/xoa <đạo hiệu của ngươi>` — phải tự tay đọc lại cái tên mình "
                                      "mới được phép bỏ nó đi. Cái chết trong sổ sinh tử là chuyện lớn, "
                                      "dù là chết trên giấy."],
                                 thanh_cong=False))
    await core.kho.xoa_tu_si(ts.user_id)
    core.pending.pop(tin.user_id, None)
    kq = KetQua(tieu_de="Sạch", van=["Một cái tên bị gạch khỏi sổ. Không ai khóc — "
                                     "thế giới này đủ rộng để quên, và đủ hẹp để nhớ lại."])
    return TraLoi.cua(kq, [[("🧘 Nhập đạo lại", "l:dangky")]])


async def _lenh_doi(core, tin, ts, arg):
    """Diễn tập: đổi con mắt đang nhìn thế giới."""
    if not core.thu_duyen:
        return TraLoi.cua(KetQua(van=["Lệnh này chỉ có ở chiếu diễn tập."], thanh_cong=False))
    doi = await core.kho.tim_theo_ten(arg or "")
    if doi is None:
        return TraLoi.cua(KetQua(van=[f"Không có ai tên gần giống *“{arg[:40]}”* trong sổ."],
                                 thanh_cong=False))
    kq = KetQua(van=[f"Ngươi nhắm mắt. Khi mở ra, đang nhìn bằng mắt của **{doi.ten}**."])
    kq.du_lieu["doi_uid"] = doi.user_id
    hook = getattr(core.lo, "doi_uid", None)
    if hook:
        await hook(tin.chat_id, doi.user_id)
    return TraLoi.cua(kq)


async def _lenh_tao(core, tin, ts, arg):
    """Diễn tập: dựng thêm một kẻ chờ sẵn ngoài cửa đạo — để thử PK hai người."""
    if not core.thu_duyen:
        return TraLoi.cua(KetQua(van=["Lệnh này chỉ có ở chiếu diễn tập."], thanh_cong=False))
    ten = (arg or "").strip()
    if not ten:
        return TraLoi.cua(KetQua(van=["Dùng: `/tao <tên nhân vật mới>`."], thanh_cong=False))
    uid = -(abs(hash(ten.lower())) % 4_000_000_000 + 1)
    if await core.kho.lay_tu_si(uid):
        kq = KetQua(van=[f"Kẻ tên **{ten}** đã có trong sổ — bấm /menu mà sống tiếp."])
        kq.du_lieu["doi_uid"] = uid
        return TraLoi.cua(kq)
    kq = await he_nhan.tao_nhan_vat(core.kho, uid, core.guild, ten, "nam",
                                    core.rng.choice(list(dl_xuatthan.DANH_SACH.keys())), core.rng)
    kq.du_lieu["doi_uid"] = uid
    hook = getattr(core.lo, "doi_uid", None)
    if hook:
        await hook(tin.chat_id, uid)
    return TraLoi.cua(kq, [[("🏮 Menu", "menu")]])


async def _lenh_dangky(core, tin, ts, arg):
    if ts is not None:
        return TraLoi.cua(KetQua(tieu_de="Ngươi đã có một đời để sống",
                                 van=["Danh tính của ngươi đã nằm trong sổ. "
                                      "Sống cho hết cái đã có, rồi hẵng nghĩ tới chuyện làm người khác."],
                                 thanh_cong=False))
    core.pending.pop(tin.user_id, None)
    if arg:
        core.pending.setdefault(tin.user_id, {})["ten"] = arg[:24]
    hang = _dong([(x.ten, f"xt:{x.ma}") for x in dl_xuatthan.DANH_SACH.values()], 2)
    hang.append([("🎲 Để trời chọn cho", "xt:ngau")])
    kq = KetQua(tieu_de="Trước cửa đạo", anh="bia_tien_do.png", mau=config.MAU_LINH,
                van=["Mỗi kẻ bước qua cửa này đều phải trả lời một câu: **ngươi từ đâu tới?** "
                     "Lai lịch kiếp này quyết định tư chất, căn cốt, hành trang — và một lời thề. "
                     "Chọn một cái bên dưới."])
    return TraLoi.cua(kq, hang)

async def _lenh_chuyenthe(core, tin, ts, arg):
    p = {"mode": "chuyenthe"}
    if ts is not None and not ts.da_chet:
        return TraLoi.cua(KetQua(tieu_de="Ngươi vẫn còn sống",
                                 van=["Kẻ còn thở thì chưa được phép đi đường vòng."],
                                 thanh_cong=False))
    if ts is None:
        return await _lenh_dangky(core, tin, None, arg)
    if arg:
        p["ten"] = arg[:24]
    core.pending[tin.user_id] = p
    hang = _dong([(x.ten, f"xt:{x.ma}") for x in dl_xuatthan.DANH_SACH.values()], 2)
    hang.append([("🎲 Kiếp sau trời định", "xt:ngau")])
    kq = KetQua(tieu_de="Chuyển thế",
                van=["Trong chỗ tối, một cái tên cũ vừa mờ đi. Trời cho ngươi một tờ giấy trắng "
                     "và đúng một câu hỏi: **kiếp này ngươi từ đâu tới?**"])
    return TraLoi.cua(kq, hang)


async def _lenh_bicanh(core, tin, ts, arg):
    from ..he import bicanh
    kq = await bicanh.vuot_ai(core.kho, ts, arg, core.rng)
    return TraLoi.cua(kq)
