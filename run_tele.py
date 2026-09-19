"""Điểm khởi cho Telegram: python run_tele.py

Cần TELEGRAM_TOKEN trong biến môi trường (hoặc tệp .env).
"""

from __future__ import annotations

import asyncio
import logging
import sys

from tuchan import config

BANNER = r"""
        ╔══════════════════════════════════════════════╗
        ║        TIÊN  ĐỒ  VÔ  TẬN  ·  Telegram        ║
        ║   một thế giới tu chân, kể bằng chữ — có     ║
        ║   chiến trường yêu vương (boss) và PK có cược║
        ╚══════════════════════════════════════════════╝
"""


def dat_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("aiogram", "aiogram.client", "aiohttp.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


async def main() -> None:
    dat_log()
    print(BANNER)
    if not config.TELEGRAM_TOKEN:
        print(
            "Chưa có TELEGRAM_TOKEN.\n"
            "  1. Xin token từ @BotFather (mệnh lệnh /newbot)\n"
            "  2. Dán vào .env: TELEGRAM_TOKEN=123456:ABC...\n"
            "  3. Bật inline feedback không cần thiết — bot dùng lệnh và nút thường.\n"
            "  4. Chạy lại: python run_tele.py\n\n"
            "Chưa có token vẫn muốn thử? Diễn tập trong trình duyệt:\n"
            "  python tools/tele_dienrap.py    → mở cổng 8080, cùng một bộ máy."
        )
        sys.exit(1)
    from tuchan.tele.bot import chay
    await chay()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nThu công. Sổ sinh tử đã cất vào ngăn kéo.")
