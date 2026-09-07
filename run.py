"""Điểm khởi: python run.py

Cần một biến môi trường DISCORD_TOKEN (đặt trong tệp .env cũng được).
"""

from __future__ import annotations

import asyncio
import logging
import sys

from tuchan import config
from tuchan.bot import TuChanBot

BANNER = r"""
        ╔══════════════════════════════════════════════╗
        ║        TIÊN  ĐỒ  VÔ  TẬN                     ║
        ║   một thế giới tu chân, kể bằng chữ          ║
        ╚══════════════════════════════════════════════╝
"""


def dat_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("discord").setLevel(logging.WARNING)


async def main() -> None:
    dat_log()
    print(BANNER)
    if not config.TOKEN:
        print(
            "Chưa có DISCORD_TOKEN.\n"
            "  1. Sao chép .env.example thành .env\n"
            "  2. Dán token của bot vào đó\n"
            "  3. Chạy lại: python run.py\n\n"
            "Muốn xem thử thế giới mà không cần token: python tools/mophong.py"
        )
        sys.exit(1)
    bot = TuChanBot()
    async with bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nThu công. Thế giới tạm ngừng xoay.")
