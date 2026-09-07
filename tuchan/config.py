"""Cấu hình chung. Mọi con số ở đây là chuyện của người viết luật,
người chơi trong thế giới sẽ không bao giờ nhìn thấy chúng."""

from __future__ import annotations

import os
from pathlib import Path

try:  # dotenv là tuỳ chọn
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

GOC = Path(__file__).resolve().parent.parent
DUONG_DAN_ASSETS = GOC / "assets"
DUONG_DAN_TRANH = DUONG_DAN_ASSETS / "tranh"
DUONG_DAN_THANH_ANH = DUONG_DAN_ASSETS / "thanh_anh"
DUONG_DAN_AM = DUONG_DAN_ASSETS / "am"

TOKEN = os.getenv("DISCORD_TOKEN", "")
TIEN_TO = os.getenv("BOT_PREFIX", "!")
DB_PATH = os.getenv("DB_PATH", str(GOC / "data" / "tienlo.sqlite3"))
GUILD_THU_NGHIEM = os.getenv("GUILD_ID", "")  # đồng bộ slash nhanh khi thử nghiệm

# Chế độ "thu ngắn thời gian" dùng khi thử nghiệm / diễn tập.
CAP_TOC = os.getenv("CAP_TOC", "0").strip().lower() in {"1", "true", "yes", "on"}
# Hệ số co giãn thời gian: 1.0 là thời gian thật của người tu hành.
try:
    _HE_SO = float(os.getenv("HE_SO_THOI_GIAN", "") or (0.01 if CAP_TOC else 1.0))
except ValueError:
    _HE_SO = 0.01 if CAP_TOC else 1.0


def _giay(x: float) -> int:
    return max(1, int(x * _HE_SO))


# Khoảng cách giữa các lần hành công (giây thực)
NGUOI_LANH = {
    "luyentap": _giay(60 * 60),
    "thiennhien": _giay(3 * 60 * 60),
    "khampha": _giay(30 * 60),
    "timduoc": _giay(20 * 60),
    "duykysi": _giay(15 * 60),
    "nhiemvu": _giay(2 * 60 * 60),
    "thidau": _giay(10 * 60),
    "luyendan": _giay(5 * 60),
    "luyenkhi": _giay(30 * 60),
}

# Thời gian dưỡng thương khi trọng thương (giây)
DUONG_THUONG_TOI_DA = _giay(6 * 60 * 60)

MAU_MUC = 0x2B2622  # màu nền thư tịch cũ
MAU_HUYET = 0x6E1B1B
MAU_LINH = 0x3F6C63
MAU_KIM = 0xB08D3F
