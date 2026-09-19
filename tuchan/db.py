"""Sổ sinh tử: nơi chép lại mọi kẻ đang tu hành trong thế giới này.

Dùng SQLite (aiosqlite). Không có gì hoa mỹ ở đây — chỉ có chữ và số,
để tầng trên còn kể chuyện.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

import aiosqlite

from . import config

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS tu_si (
    user_id        INTEGER PRIMARY KEY,
    guild_id       INTEGER NOT NULL DEFAULT 0,
    ten            TEXT NOT NULL,
    gioi_tinh      TEXT NOT NULL DEFAULT 'nam',
    xuat_than      TEXT NOT NULL DEFAULT 'pham_nhan',
    canh_gioi      INTEGER NOT NULL DEFAULT 0,
    tang           INTEGER NOT NULL DEFAULT 1,
    tu_vi          INTEGER NOT NULL DEFAULT 0,
    tu_chat        REAL NOT NULL DEFAULT 1.0,
    can_cot        REAL NOT NULL DEFAULT 1.0,
    dao_tam        INTEGER NOT NULL DEFAULT 60,
    than_the       INTEGER NOT NULL DEFAULT 100,
    linh_thach     INTEGER NOT NULL DEFAULT 0,
    mon_phai       TEXT NOT NULL DEFAULT '',
    cong_hien      INTEGER NOT NULL DEFAULT 0,
    danh_vong      INTEGER NOT NULL DEFAULT 0,
    sat_nghiep     INTEGER NOT NULL DEFAULT 0,
    phap_bao       TEXT NOT NULL DEFAULT '',
    tho_nguyen     INTEGER NOT NULL DEFAULT 0,
    nhap_dao_luc   INTEGER NOT NULL DEFAULT 0,
    thuong_toi     INTEGER NOT NULL DEFAULT 0,
    that_bai_lien  INTEGER NOT NULL DEFAULT 0,
    so_lan_dot_pha INTEGER NOT NULL DEFAULT 0,
    so_tran_thang  INTEGER NOT NULL DEFAULT 0,
    so_tran_thua   INTEGER NOT NULL DEFAULT 0,
    da_chet        INTEGER NOT NULL DEFAULT 0,
    dan_pham       INTEGER NOT NULL DEFAULT 0,
    tho_nguyen_them INTEGER NOT NULL DEFAULT 0,
    buff_ho_kiep   REAL NOT NULL DEFAULT 0,
    buff_pha_chuong REAL NOT NULL DEFAULT 0,
    an_tuc_toi     INTEGER NOT NULL DEFAULT 0,
    so_kiep_da_qua INTEGER NOT NULL DEFAULT 0,
    ghi_chu        TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tui_do (
    user_id  INTEGER NOT NULL,
    ma       TEXT NOT NULL,
    so_luong INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, ma)
);

CREATE TABLE IF NOT EXISTS so_tay (          -- công thức đã học
    user_id INTEGER NOT NULL,
    ma      TEXT NOT NULL,
    hoc_luc INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, ma)
);

CREATE TABLE IF NOT EXISTS nguoi_lanh (      -- thời điểm được phép hành động tiếp
    user_id INTEGER NOT NULL,
    viec    TEXT NOT NULL,
    den_luc INTEGER NOT NULL,
    PRIMARY KEY (user_id, viec)
);

CREATE TABLE IF NOT EXISTS nhat_ky (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    luc      INTEGER NOT NULL,
    loai     TEXT NOT NULL,
    noi_dung TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS viec_mon (
    user_id   INTEGER PRIMARY KEY,
    ma        TEXT NOT NULL,
    chang     INTEGER NOT NULL DEFAULT 0,
    nhan_luc  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS thien_bien (
    guild_id  INTEGER NOT NULL,
    ma        TEXT NOT NULL,
    bat_dau   INTEGER NOT NULL,
    ket_thuc  INTEGER NOT NULL,
    PRIMARY KEY (guild_id, ma)
);

CREATE TABLE IF NOT EXISTS boss_hien (          -- yêu vương đang hiện thế (mỗi thế giới một con)
    guild_id   INTEGER PRIMARY KEY,
    ma         TEXT NOT NULL,
    huyet      INTEGER NOT NULL,                -- nguyên khí còn lại
    huyet_max  INTEGER NOT NULL,
    bat_dau    INTEGER NOT NULL,
    luot_cuoi  INTEGER NOT NULL DEFAULT 0,
    ke_chot    INTEGER NOT NULL DEFAULT 0,      -- ai chém nhát cuối
    ke_goi     INTEGER NOT NULL DEFAULT 0       -- ai triệu nó ra (0 = trời tự xếp)
);

CREATE TABLE IF NOT EXISTS boss_con (          -- vết thương do từng người để lại
    guild_id   INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    ten        TEXT NOT NULL DEFAULT '',
    sat_thuong INTEGER NOT NULL DEFAULT 0,
    so_lan     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS thach_dau (          -- lời thách PK đang treo
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    a_id     INTEGER NOT NULL,
    a_ten    TEXT NOT NULL,
    b_id     INTEGER NOT NULL,
    b_ten    TEXT NOT NULL,
    cuoc     INTEGER NOT NULL DEFAULT 0,
    sinh_tu  INTEGER NOT NULL DEFAULT 0,
    luc      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS danh_thiep (         -- Telegram: nơi gửi thư cho từng tu sĩ
    user_id  INTEGER PRIMARY KEY,
    chat_id  INTEGER NOT NULL,
    ten      TEXT NOT NULL DEFAULT '',
    luu_luc  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS thoi_muc (           -- mốc thời gian lặt vặt của thế giới
    khoa     TEXT PRIMARY KEY,
    gia_tri  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nhat_ky_user ON nhat_ky(user_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_thach_b ON thach_dau(b_id, luc);
"""


@dataclass
class TuSi:
    user_id: int
    guild_id: int = 0
    ten: str = ""
    gioi_tinh: str = "nam"
    xuat_than: str = "pham_nhan"
    canh_gioi: int = 0
    tang: int = 1
    tu_vi: int = 0
    tu_chat: float = 1.0
    can_cot: float = 1.0
    dao_tam: int = 60
    than_the: int = 100
    linh_thach: int = 0
    mon_phai: str = ""
    cong_hien: int = 0
    danh_vong: int = 0
    sat_nghiep: int = 0
    phap_bao: str = ""
    tho_nguyen: int = 0
    nhap_dao_luc: int = 0
    thuong_toi: int = 0
    that_bai_lien: int = 0
    so_lan_dot_pha: int = 0
    so_tran_thang: int = 0
    so_tran_thua: int = 0
    da_chet: int = 0
    dan_pham: int = 0            # phẩm chất kim đan (0 = chưa kết đan)
    tho_nguyen_them: int = 0     # số năm thọ mua thêm được bằng đan dược
    buff_ho_kiep: float = 0.0    # hộ thể còn hiệu lực cho lần độ kiếp tới
    buff_pha_chuong: float = 0.0 # cơ hội cộng thêm cho lần xung quan tới
    an_tuc_toi: int = 0          # khí tức bị che tới thời khắc này
    so_kiep_da_qua: int = 0      # đã đi qua bao nhiêu lần kiếp nạn lớn
    ghi_chu: str = "{}"

    # ── tiện ích ──
    @property
    def dang_bi_thuong(self) -> bool:
        return self.thuong_toi > int(time.time())

    @property
    def con_bao_lau_duong_thuong(self) -> int:
        return max(0, self.thuong_toi - int(time.time()))

    @property
    def dang_an_tuc(self) -> bool:
        return self.an_tuc_toi > int(time.time())

    def ghi(self) -> dict[str, Any]:
        try:
            return json.loads(self.ghi_chu or "{}")
        except Exception:
            return {}

    def dat_ghi(self, d: dict[str, Any]) -> None:
        self.ghi_chu = json.dumps(d, ensure_ascii=False)

    def lay_trang_bi(self) -> dict[str, str]:
        g = self.ghi()
        tb = dict(g.get("trang_bi", {}))
        if self.phap_bao and "phap_bao" not in tb and "vu_khi" not in tb:
            from .data import vatpham
            vp = vatpham.lay(self.phap_bao)
            if vp:
                slot = vp.slot_trang_bi or "phap_bao"
                tb[slot] = self.phap_bao
        return tb

    def dat_trang_bi(self, slot: str, ma_vat: str) -> None:
        g = self.ghi()
        tb = dict(g.get("trang_bi", {}))
        tb[slot] = ma_vat
        g["trang_bi"] = tb
        self.dat_ghi(g)
        if slot in ("vu_khi", "phap_bao"):
            self.phap_bao = ma_vat

    def thao_trang_bi(self, slot: str) -> str:
        g = self.ghi()
        tb = dict(g.get("trang_bi", {}))
        da_thao = tb.pop(slot, "")
        g["trang_bi"] = tb
        self.dat_ghi(g)
        if self.phap_bao == da_thao:
            self.phap_bao = tb.get("vu_khi") or tb.get("phap_bao") or ""
        return da_thao

    def lay_cuong_hoa(self) -> dict[str, int]:
        return dict(self.ghi().get("cuong_hoa", {}))

    def dat_cuong_hoa(self, ma_vat: str, cap: int) -> None:
        g = self.ghi()
        ch = dict(g.get("cuong_hoa", {}))
        ch[ma_vat] = cap
        g["cuong_hoa"] = ch
        self.dat_ghi(g)

    def thap_tang(self) -> int:
        return max(1, int(self.ghi().get("thap_tang", 1)))

    def dat_thap_tang(self, tang: int) -> None:
        g = self.ghi()
        g["thap_tang"] = tang
        self.dat_ghi(g)

    def tinh_chi_so(self) -> dict[str, Any]:
        from .canhgioi import tu_vi_can_thiet
        from .data import vatpham, monphai
        cg = self.canh_gioi
        tang = self.tang

        hp_max = int(250 + 120 * tang + 850 * (cg ** 1.8))
        mp_max = int(60 + 25 * tang + 150 * (cg ** 1.6))
        cong = int((35 + 16 * tang + 140 * (cg ** 1.8)) * self.tu_chat)
        thu = int((15 + 9 * tang + 70 * (cg ** 1.8)) * self.can_cot)
        bao_kich = round(5.0 + min(25.0, (self.dao_tam - 50) * 0.2 + self.can_cot * 3.0), 1)
        toc_do = int(50 + 10 * cg + tang * 3)

        mp = monphai.lay(self.mon_phai) if self.mon_phai else None
        if mp:
            cong = int(cong * mp.he_so_chien)

        tb = self.lay_trang_bi()
        ch = self.lay_cuong_hoa()
        for slot, ma in tb.items():
            vp = vatpham.lay(ma)
            if not vp:
                continue
            he_so_ch = 1.0 + 0.15 * ch.get(ma, 0)
            cong += int(vp.chi_so_cong * he_so_ch)
            thu += int(vp.chi_so_thu * he_so_ch)
            hp_max += int(vp.chi_so_hp * he_so_ch)
            bao_kich = round(bao_kich + vp.chi_so_bao_kich * (1.0 + 0.1 * ch.get(ma, 0)), 1)
            toc_do += int(vp.chi_so_toc_do * he_so_ch)

        hp_hien_tai = int(hp_max * (max(1, min(100, self.than_the)) / 100.0))
        luc_chien = int(cong * 3.5 + thu * 3.0 + hp_max * 0.4 + mp_max * 0.5 + bao_kich * 25 + toc_do * 2.0)
        tu_vi_can = tu_vi_can_thiet(cg, tang)
        tu_vi_sec = max(1, int(1.6 ** cg + tang * 0.6))
        if mp:
            tu_vi_sec = max(1, int(tu_vi_sec * mp.he_so_tu_luyen))

        return {
            "hp": hp_hien_tai,
            "hp_max": hp_max,
            "mp": mp_max,
            "mp_max": mp_max,
            "cong": cong,
            "thu": thu,
            "bao_kich": bao_kich,
            "toc_do": toc_do,
            "luc_chien": luc_chien,
            "tu_vi_can": tu_vi_can,
            "tu_vi_sec": tu_vi_sec,
        }

    def nhan_tu_vi_treo_may(self) -> tuple[int, int]:
        g = self.ghi()
        now = int(time.time())
        last = g.get("last_idle", now)
        delta = min(12 * 3600, max(0, now - last))
        cs = self.tinh_chi_so()
        cong = int(delta * cs["tu_vi_sec"])
        g["last_idle"] = now
        self.dat_ghi(g)
        if cong > 0:
            self.tu_vi += cong
        return cong, delta


CAC_COT = [f.name for f in TuSi.__dataclass_fields__.values()]  # type: ignore[attr-defined]


class Kho:
    """Lớp truy cập dữ liệu. Một thể hiện dùng chung cho cả bot."""

    def __init__(self, duong_dan: str | None = None):
        self.duong_dan = duong_dan or config.DB_PATH
        Path(self.duong_dan).parent.mkdir(parents=True, exist_ok=True)
        self._conn: aiosqlite.Connection | None = None

    async def mo(self) -> None:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.duong_dan)
            self._conn.row_factory = aiosqlite.Row
            await self._conn.executescript(SCHEMA)
            await self._di_tru()
            await self._conn.commit()

    async def _di_tru(self) -> None:
        """Thêm những cột sinh sau đẻ muộn vào sổ cũ, không làm mất dữ liệu."""
        assert self._conn is not None
        cur = await self._conn.execute("PRAGMA table_info(tu_si)")
        co = {r[1] for r in await cur.fetchall()}
        await cur.close()
        kieu = {
            "dan_pham": "INTEGER NOT NULL DEFAULT 0",
            "tho_nguyen_them": "INTEGER NOT NULL DEFAULT 0",
            "buff_ho_kiep": "REAL NOT NULL DEFAULT 0",
            "buff_pha_chuong": "REAL NOT NULL DEFAULT 0",
            "an_tuc_toi": "INTEGER NOT NULL DEFAULT 0",
            "so_kiep_da_qua": "INTEGER NOT NULL DEFAULT 0",
        }
        for cot, dinh_nghia in kieu.items():
            if cot not in co:
                await self._conn.execute(f"ALTER TABLE tu_si ADD COLUMN {cot} {dinh_nghia}")

    async def dong(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Kho chưa mở. Gọi await kho.mo() trước.")
        return self._conn

    # ─────────── tu sĩ ───────────
    async def lay_tu_si(self, user_id: int) -> TuSi | None:
        cur = await self.conn.execute("SELECT * FROM tu_si WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        if row is None:
            return None
        return TuSi(**{k: row[k] for k in row.keys()})

    async def tao_tu_si(self, ts: TuSi) -> None:
        cot = ", ".join(CAC_COT)
        hoi = ", ".join("?" for _ in CAC_COT)
        await self.conn.execute(
            f"INSERT INTO tu_si ({cot}) VALUES ({hoi})",
            tuple(getattr(ts, c) for c in CAC_COT),
        )
        await self.conn.commit()

    async def luu(self, ts: TuSi) -> None:
        gan = ", ".join(f"{c}=?" for c in CAC_COT if c != "user_id")
        await self.conn.execute(
            f"UPDATE tu_si SET {gan} WHERE user_id=?",
            tuple(getattr(ts, c) for c in CAC_COT if c != "user_id") + (ts.user_id,),
        )
        await self.conn.commit()

    async def luu_bi_canh(self, ts: TuSi, vat_thuong: str | None,
                         cho: int, nhat_ky: str) -> None:
        """Lưu tiến độ, thưởng và hồi chiêu cùng một transaction.

        Gọi trong khóa lõi Telegram: không có lần commit nhận thưởng trước khi
        ghi tiến độ, kể cả khi tiến trình bị dừng giữa chừng.
        """
        try:
            await self.conn.execute(
                "UPDATE tu_si SET ghi_chu=?, linh_thach=?, danh_vong=?, than_the=? WHERE user_id=?",
                (ts.ghi_chu, ts.linh_thach, ts.danh_vong, ts.than_the, ts.user_id),
            )
            if vat_thuong:
                await self.conn.execute(
                    "INSERT INTO tui_do (user_id, ma, so_luong) VALUES (?,?,1) "
                    "ON CONFLICT(user_id, ma) DO UPDATE SET so_luong=so_luong+1",
                    (ts.user_id, vat_thuong),
                )
            await self.conn.execute(
                "INSERT INTO nguoi_lanh (user_id, viec, den_luc) VALUES (?,?,?) "
                "ON CONFLICT(user_id, viec) DO UPDATE SET den_luc=excluded.den_luc",
                (ts.user_id, "bicanh", int(time.time()) + cho),
            )
            await self.conn.execute(
                "INSERT INTO nhat_ky (user_id, luc, loai, noi_dung) VALUES (?,?,?,?)",
                (ts.user_id, int(time.time()), "bicanh", nhat_ky),
            )
            await self.conn.commit()
        except BaseException:
            await self.conn.rollback()
            raise

    async def xoa_tu_si(self, user_id: int) -> None:
        for bang in ("tu_si", "tui_do", "so_tay", "nguoi_lanh", "nhat_ky", "viec_mon"):
            await self.conn.execute(f"DELETE FROM {bang} WHERE user_id=?", (user_id,))
        await self.conn.execute("DELETE FROM boss_con WHERE user_id=?", (user_id,))
        await self.conn.execute("DELETE FROM thach_dau WHERE a_id=? OR b_id=?", (user_id, user_id))
        await self.conn.commit()

    async def bang_danh_vong(self, gioi_han: int = 10) -> list[TuSi]:
        cur = await self.conn.execute(
            "SELECT * FROM tu_si ORDER BY canh_gioi DESC, tang DESC, tu_vi DESC, danh_vong DESC LIMIT ?",
            (gioi_han,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [TuSi(**{k: r[k] for k in r.keys()}) for r in rows]

    # ─────────── túi đồ ───────────
    async def them_vat(self, user_id: int, ma: str, so_luong: int = 1) -> None:
        if so_luong == 0:
            return
        await self.conn.execute(
            "INSERT INTO tui_do (user_id, ma, so_luong) VALUES (?,?,?) "
            "ON CONFLICT(user_id, ma) DO UPDATE SET so_luong = so_luong + excluded.so_luong",
            (user_id, ma, so_luong),
        )
        await self.conn.execute("DELETE FROM tui_do WHERE user_id=? AND so_luong<=0", (user_id,))
        await self.conn.commit()

    async def bot_vat(self, user_id: int, ma: str, so_luong: int = 1) -> bool:
        con = await self.dem_vat(user_id, ma)
        if con < so_luong:
            return False
        await self.them_vat(user_id, ma, -so_luong)
        return True

    async def dem_vat(self, user_id: int, ma: str) -> int:
        cur = await self.conn.execute(
            "SELECT so_luong FROM tui_do WHERE user_id=? AND ma=?", (user_id, ma)
        )
        row = await cur.fetchone()
        await cur.close()
        return int(row[0]) if row else 0

    async def tui(self, user_id: int) -> dict[str, int]:
        cur = await self.conn.execute(
            "SELECT ma, so_luong FROM tui_do WHERE user_id=? AND so_luong>0", (user_id,)
        )
        rows = await cur.fetchall()
        await cur.close()
        return {r["ma"]: r["so_luong"] for r in rows}

    async def du_nguyen_lieu(self, user_id: int, can: dict[str, int]) -> bool:
        tui = await self.tui(user_id)
        return all(tui.get(k, 0) >= v for k, v in can.items())

    async def tieu_nguyen_lieu(self, user_id: int, can: dict[str, int]) -> bool:
        if not await self.du_nguyen_lieu(user_id, can):
            return False
        for k, v in can.items():
            await self.them_vat(user_id, k, -v)
        return True

    # ─────────── sổ tay công thức ───────────
    async def hoc_cong_thuc(self, user_id: int, ma: str) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM so_tay WHERE user_id=? AND ma=?", (user_id, ma)
        )
        co = await cur.fetchone()
        await cur.close()
        if co:
            return False
        await self.conn.execute(
            "INSERT INTO so_tay (user_id, ma) VALUES (?,?)", (user_id, ma)
        )
        await self.conn.commit()
        return True

    async def so_tay(self, user_id: int) -> set[str]:
        cur = await self.conn.execute("SELECT ma FROM so_tay WHERE user_id=?", (user_id,))
        rows = await cur.fetchall()
        await cur.close()
        return {r["ma"] for r in rows}

    # ─────────── người lành / thời khắc ───────────
    async def con_cho(self, user_id: int, viec: str) -> int:
        cur = await self.conn.execute(
            "SELECT den_luc FROM nguoi_lanh WHERE user_id=? AND viec=?", (user_id, viec)
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return 0
        return max(0, int(row[0]) - int(time.time()))

    async def dat_cho(self, user_id: int, viec: str, giay: int) -> None:
        await self.conn.execute(
            "INSERT INTO nguoi_lanh (user_id, viec, den_luc) VALUES (?,?,?) "
            "ON CONFLICT(user_id, viec) DO UPDATE SET den_luc=excluded.den_luc",
            (user_id, viec, int(time.time()) + giay),
        )
        await self.conn.commit()

    # ─────────── nhật ký ───────────
    async def chep(self, user_id: int, loai: str, noi_dung: str) -> None:
        await self.conn.execute(
            "INSERT INTO nhat_ky (user_id, luc, loai, noi_dung) VALUES (?,?,?,?)",
            (user_id, int(time.time()), loai, noi_dung),
        )
        await self.conn.commit()

    async def doc_nhat_ky(self, user_id: int, gioi_han: int = 8) -> list[dict[str, Any]]:
        cur = await self.conn.execute(
            "SELECT luc, loai, noi_dung FROM nhat_ky WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, gioi_han),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    # ─────────── việc môn ───────────
    async def viec_hien_tai(self, user_id: int) -> dict[str, Any] | None:
        cur = await self.conn.execute("SELECT * FROM viec_mon WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def nhan_viec(self, user_id: int, ma: str) -> None:
        await self.conn.execute(
            "INSERT INTO viec_mon (user_id, ma, chang, nhan_luc) VALUES (?,?,0,?) "
            "ON CONFLICT(user_id) DO UPDATE SET ma=excluded.ma, chang=0, nhan_luc=excluded.nhan_luc",
            (user_id, ma, int(time.time())),
        )
        await self.conn.commit()

    async def tien_chang(self, user_id: int, chang: int) -> None:
        await self.conn.execute("UPDATE viec_mon SET chang=? WHERE user_id=?", (chang, user_id))
        await self.conn.commit()

    async def xong_viec(self, user_id: int) -> None:
        await self.conn.execute("DELETE FROM viec_mon WHERE user_id=?", (user_id,))
        await self.conn.commit()

    # ─────────── thiên biến ───────────
    async def khoi_thien_bien(self, guild_id: int, ma: str, gio: int) -> None:
        now = int(time.time())
        await self.conn.execute(
            "INSERT INTO thien_bien (guild_id, ma, bat_dau, ket_thuc) VALUES (?,?,?,?) "
            "ON CONFLICT(guild_id, ma) DO UPDATE SET bat_dau=excluded.bat_dau, ket_thuc=excluded.ket_thuc",
            (guild_id, ma, now, now + gio * 3600),
        )
        await self.conn.commit()

    async def thien_bien_dang_dien(self, guild_id: int) -> list[str]:
        now = int(time.time())
        cur = await self.conn.execute(
            "SELECT ma FROM thien_bien WHERE guild_id=? AND ket_thuc>?", (guild_id, now)
        )
        rows = await cur.fetchall()
        await cur.close()
        return [r["ma"] for r in rows]

    async def don_thien_bien(self, guild_id: int) -> list[str]:
        """Trả về mã các thiên biến vừa kết thúc rồi xoá chúng."""
        now = int(time.time())
        cur = await self.conn.execute(
            "SELECT ma FROM thien_bien WHERE guild_id=? AND ket_thuc<=?", (guild_id, now)
        )
        rows = await cur.fetchall()
        await cur.close()
        ma = [r["ma"] for r in rows]
        if ma:
            await self.conn.execute(
                "DELETE FROM thien_bien WHERE guild_id=? AND ket_thuc<=?", (guild_id, now)
            )
            await self.conn.commit()
        return ma

    async def cac_guild_co_nguoi(self) -> list[int]:
        cur = await self.conn.execute("SELECT DISTINCT guild_id FROM tu_si WHERE guild_id<>0")
        rows = await cur.fetchall()
        await cur.close()
        return [int(r[0]) for r in rows]

    async def dinh_the_gioi(self, guild_id: int = 0) -> tuple[int, int]:
        """(bậc cao nhất đang có người ngồi, số người) — dùng để chọn boss vừa sức."""
        sql = "SELECT MAX(canh_gioi), COUNT(*) FROM tu_si"
        args: tuple = ()
        if guild_id:
            sql += " WHERE guild_id=?"
            args = (guild_id,)
        cur = await self.conn.execute(sql, args)
        row = await cur.fetchone()
        await cur.close()
        return int(row[0] or 0), int(row[1] or 0)

    async def tim_theo_ten(self, ten: str, loai_tru: int | None = None) -> TuSi | None:
        """Tìm tu sĩ theo đạo hiệu: khớp trước, khớp một phần sau."""
        ten = (ten or "").strip()
        if not ten:
            return None
        where, args = "LOWER(ten)=?", (ten.lower(),)
        if loai_tru is not None:
            where += " AND user_id<>?"
            args += (loai_tru,)
        cur = await self.conn.execute(f"SELECT * FROM tu_si WHERE {where}", args)
        row = await cur.fetchone()
        await cur.close()
        if row is None:
            like, largs = "ten LIKE ?", (f"%{ten}%",)
            if loai_tru is not None:
                like += " AND user_id<>?"
                largs += (loai_tru,)
            cur = await self.conn.execute(f"SELECT * FROM tu_si WHERE {like} LIMIT 2", largs)
            rows = await cur.fetchall()
            await cur.close()
            if len(rows) == 1:
                row = rows[0]
        if row is None:
            return None
        return TuSi(**{k: row[k] for k in row.keys()})

    # ─────────── chiến trường yêu vương ───────────
    async def boss_lay(self, guild_id: int) -> dict[str, Any] | None:
        cur = await self.conn.execute("SELECT * FROM boss_hien WHERE guild_id=?", (guild_id,))
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def boss_dat(self, guild_id: int, ma: str, huyet: int, ke_goi: int = 0) -> None:
        now = int(time.time())
        await self.conn.execute(
            "INSERT INTO boss_hien (guild_id, ma, huyet, huyet_max, bat_dau, luot_cuoi, ke_chot, ke_goi) "
            "VALUES (?,?,?,?,?,?,0,?) ON CONFLICT(guild_id) DO UPDATE SET "
            "ma=excluded.ma, huyet=excluded.huyet, huyet_max=excluded.huyet_max, "
            "bat_dau=excluded.bat_dau, luot_cuoi=excluded.luot_cuoi, ke_chot=0, ke_goi=excluded.ke_goi",
            (guild_id, ma, huyet, huyet, now, now, ke_goi),
        )
        await self.conn.execute("DELETE FROM boss_con WHERE guild_id=?", (guild_id,))
        await self.conn.commit()

    async def boss_giam_huyet(self, guild_id: int, user_id: int, ten: str, sat_thuong: int) -> int:
        """Trừ nguyên khí của boss, ghi công kẻ ra đòn. Trả về nguyên khí còn lại."""
        cur = await self.conn.execute(
            "UPDATE boss_hien SET huyet = MAX(0, huyet - ?), luot_cuoi=?, ke_chot=? WHERE guild_id=?",
            (sat_thuong, int(time.time()), user_id, guild_id),
        )
        await cur.close()
        await self.conn.execute(
            "INSERT INTO boss_con (guild_id, user_id, ten, sat_thuong, so_lan) VALUES (?,?,?,?,1) "
            "ON CONFLICT(guild_id, user_id) DO UPDATE SET sat_thuong = sat_thuong + excluded.sat_thuong, "
            "so_lan = so_lan + 1, ten = excluded.ten",
            (guild_id, user_id, ten, sat_thuong),
        )
        cur = await self.conn.execute("SELECT huyet FROM boss_hien WHERE guild_id=?", (guild_id,))
        row = await cur.fetchone()
        await cur.close()
        await self.conn.commit()
        return int(row[0]) if row else 0

    async def boss_ds(self, guild_id: int) -> list[dict[str, Any]]:
        cur = await self.conn.execute(
            "SELECT * FROM boss_con WHERE guild_id=? ORDER BY sat_thuong DESC", (guild_id,)
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    async def boss_xoa(self, guild_id: int) -> None:
        await self.conn.execute("DELETE FROM boss_hien WHERE guild_id=?", (guild_id,))
        await self.conn.execute("DELETE FROM boss_con WHERE guild_id=?", (guild_id,))
        await self.conn.commit()

    # ─────────── lời thách PK ───────────
    async def thach_tao(self, guild_id: int, a_id: int, a_ten: str, b_id: int, b_ten: str,
                        cuoc: int = 0, sinh_tu: bool = False) -> int:
        cur = await self.conn.execute(
            "INSERT INTO thach_dau (guild_id, a_id, a_ten, b_id, b_ten, cuoc, sinh_tu, luc) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (guild_id, a_id, a_ten, b_id, b_ten, int(cuoc), 1 if sinh_tu else 0, int(time.time())),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def thach_lay(self, ma: int) -> dict[str, Any] | None:
        cur = await self.conn.execute("SELECT * FROM thach_dau WHERE id=?", (ma,))
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def thach_cua_toi(self, user_id: int) -> tuple[list[dict], list[dict]]:
        """(đang chờ ta ứng chiến, ta gửi đi chưa có hồi âm)."""
        cur = await self.conn.execute(
            "SELECT * FROM thach_dau WHERE b_id=? ORDER BY id DESC", (user_id,))
        cho = [dict(r) for r in await cur.fetchall()]
        await cur.close()
        cur = await self.conn.execute(
            "SELECT * FROM thach_dau WHERE a_id=? ORDER BY id DESC", (user_id,))
        gui = [dict(r) for r in await cur.fetchall()]
        await cur.close()
        return cho, gui

    async def thach_xoa(self, ma: int) -> None:
        await self.conn.execute("DELETE FROM thach_dau WHERE id=?", (ma,))
        await self.conn.commit()

    async def thach_het_gio(self) -> list[dict[str, Any]]:
        """Những lời thách quá hạn — xoá luôn, coi như chưa từng buông lời."""
        han = int(time.time()) - config.THACH_THOI_HAN
        cur = await self.conn.execute("SELECT * FROM thach_dau WHERE luc<?", (han,))
        rows = [dict(r) for r in await cur.fetchall()]
        await cur.close()
        if rows:
            await self.conn.execute("DELETE FROM thach_dau WHERE luc<?", (han,))
            await self.conn.commit()
        return rows

    # ─────────── danh thiếp Telegram ───────────
    async def danh_thiep_luu(self, user_id: int, chat_id: int, ten: str = "") -> None:
        await self.conn.execute(
            "INSERT INTO danh_thiep (user_id, chat_id, ten, luu_luc) VALUES (?,?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET chat_id=excluded.chat_id, "
            "ten=excluded.ten, luu_luc=excluded.luu_luc",
            (user_id, chat_id, ten, int(time.time())),
        )
        await self.conn.commit()

    async def danh_thiep_cua(self, user_id: int) -> int | None:
        cur = await self.conn.execute("SELECT chat_id FROM danh_thiep WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        return int(row[0]) if row else None

    async def danh_thiep_all(self) -> list[tuple[int, int]]:
        """(user_id, chat_id) không trùng — để gieo tin khắp nhân gian."""
        cur = await self.conn.execute(
            "SELECT user_id, MAX(chat_id) FROM danh_thiep GROUP BY user_id")
        rows = await cur.fetchall()
        await cur.close()
        return [(int(r[0]), int(r[1])) for r in rows]

    # ─────────── mốc thời gian ───────────
    async def thoi_muc_xem(self, khoa: str) -> int | None:
        cur = await self.conn.execute("SELECT gia_tri FROM thoi_muc WHERE khoa=?", (khoa,))
        row = await cur.fetchone()
        await cur.close()
        return int(row[0]) if row else None

    async def thoi_muc_dat(self, khoa: str, gia_tri: int) -> None:
        await self.conn.execute(
            "INSERT INTO thoi_muc (khoa, gia_tri) VALUES (?,?) "
            "ON CONFLICT(khoa) DO UPDATE SET gia_tri=excluded.gia_tri",
            (khoa, int(gia_tri)),
        )
        await self.conn.commit()
