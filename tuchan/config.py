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

# ── Telegram ──
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
# Một thế giới, một sổ sinh tử. Bot Telegram ghi mọi tu sĩ vào "guild" này
# để dùng chung CSDL với bot Discord nếu muốn.
TELE_GUILD = int(os.getenv("TELE_GUILD", "1") or 1)
# User id được phép triệu boss / gọi thiên biến bên Telegram (phân cách bằng dấu phẩy)
TELE_ADMIN_IDS = {int(x) for x in os.getenv("TELE_ADMIN_IDS", "").replace(" ", "").split(",") if x.strip()}
# Lối vào Mini App (https://… — BotFather muốn vậy). Để trống thì không có nút "Vào động".
TELE_MINIAPP_URL = os.getenv("TELE_MINIAPP_URL", "").strip()
# Cổng mà máy chủ Mini App nghe (tuchan/tele/mini.py)
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

# Chế độ "thu ngắn thời gian" dùng khi thử nghiệm / diễn tập.
CAP_TOC = os.getenv("CAP_TOC", "0").strip().lower() in {"1", "true", "yes", "on"}
# Hệ số co giãn thời gian: 1.0 là thời gian thật của người tu hành.
try:
    _HE_SO = float(os.getenv("HE_SO_THOI_GIAN", "") or (0.01 if CAP_TOC else 1.0))
except ValueError:
    _HE_SO = 0.01 if CAP_TOC else 1.0


def _giay(x: float) -> int:
    return max(1, int(x * _HE_SO))


HE_SO_GIAY = _HE_SO  # cho các modul khác tự quy đổi thời gian thô sang "giờ diễn tập"


# Khoảng cách giữa các lần hành công (giây thực)
NGUOI_LANH = {
    "luyentap": _giay(60 * 60),
    "thiennhien": _giay(3 * 60 * 60),
    "khampha": _giay(30 * 60),
    "timduoc": _giay(20 * 60),
    "duykysi": _giay(15 * 60),
    "nhiemvu": _giay(2 * 60 * 60),
    "thidau": _giay(10 * 60),
    "daboss": _giay(12 * 60),   # một lần lao vào chiến trường cách nhau chừng này
    "luyendan": _giay(5 * 60),
    "luyenkhi": _giay(30 * 60),
}

# Thời gian dưỡng thương khi trọng thương (giây)
DUONG_THUONG_TOI_DA = _giay(6 * 60 * 60)

# ── đại chiến yêu vương (boss) ──
BOSS_THOI_HAN = _giay(50 * 60)     # yêu vương hiện thế tối đa bấy lâu, quá thì rút về
BOSS_TRONG_THOI = _giay(40 * 60)   # không có boss thì từng này lại gieo quẻ xem có kẻ thức tỉnh
BOSS_XAC_SUAT = float(os.getenv("BOSS_XAC_SUAT", "0.5"))  # mỗi vòng kiểm tra
# ── PK ──
THACH_THOI_HAN = 600  # giây: lời thách treo quá 10 khắc thì coi như khước từ

MAU_MUC = 0x2B2622  # màu nền thư tịch cũ
MAU_HUYET = 0x6E1B1B
MAU_LINH = 0x3F6C63
MAU_KIM = 0xB08D3F
