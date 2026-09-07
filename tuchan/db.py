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

CREATE INDEX IF NOT EXISTS idx_nhat_ky_user ON nhat_ky(user_id, id DESC);
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

    async def xoa_tu_si(self, user_id: int) -> None:
        for bang in ("tu_si", "tui_do", "so_tay", "nguoi_lanh", "nhat_ky", "viec_mon"):
            await self.conn.execute(f"DELETE FROM {bang} WHERE user_id=?", (user_id,))
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
