"""Điểm khởi của Telegram:

    python run_tele.py           # chỉ bot (cần TELEGRAM_TOKEN)
    python run_tele.py --mini    # bot + cửa động Mini App (cổng WEB_PORT, mặc định 8080)
    python run_tele.py --mini    # không có token → cửa động diễn tập cho khách, bot nằm chờ
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from tuchan import config

BANNER = r"""
        ╔══════════════════════════════════════════════╗
        ║        TIÊN  ĐỒ  VÔ  TẬN  ·  Telegram        ║
        ║   Mini App tu tiên · động phủ · pháp bảo     ║
        ║   bảy ải yêu vương · kỳ duyên · tông môn     ║
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


async def main(mini: bool) -> None:
    dat_log()
    print(BANNER)

    runner = None
    if mini:
        from tuchan.db import Kho
        from tuchan.tele import mini as cua_dong
        if not config.TELEGRAM_TOKEN:
            runner, _site, dong = await cua_dong.mo()
        else:
            # một lõi lệnh, hai cái miệng: Telegram bot và cửa động cùng nuốt chung sổ sách
            kho = Kho(); await kho.mo()
            dong = cua_dong.nhan(kho)
            runner = await cua_dong.mo_site(dong)
        print(f"⛩  Cửa động: http://localhost:{config.WEB_PORT}  ·  sổ: {config.DB_PATH}")
        print("   (đưa URL https công khai vào TELE_MINIAPP_URL để Telegram mở nút Vào động)\n")

    if not config.TELEGRAM_TOKEN:
        if mini:
            print("Chưa có TELEGRAM_TOKEN — cửa động vẫn mở cho khách lang thang; "
                  "muốn bot thật thì dán token vào .env rồi chạy lại.\n")
            try:
                while True:
                    await asyncio.sleep(3600)
            except KeyboardInterrupt:
                pass
            finally:
                await runner.cleanup()
            return
        print(
            "Chưa có TELEGRAM_TOKEN.\n"
            "  1. Xin token từ @BotFather (mệnh lệnh /newbot)\n"
            "  2. Dán vào .env: TELEGRAM_TOKEN=123456:ABC...\n"
            "  3. Chạy lại: python run_tele.py\n\n"
            "Chưa có token vẫn muốn thử? Mở cả cửa động diễn tập:\n"
            "  python run_tele.py --mini        → cổng 8080, cùng một bộ máy.\n"
            "  hoặc giao diện tập lệnh thuần:   → python tools/tele_dienrap.py"
        )
        sys.exit(1)

    from tuchan.tele.bot import chay
    try:
        if runner is not None:
            await chay(kho=kho, lo_them=dong.lo, gan_core=lambda core: setattr(dong, "core", core))
        else:
            await chay()
    finally:
        if runner is not None:
            await runner.cleanup()
            await kho.dong()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--mini", action="store_true", help="kèm cửa động Mini App (aiohttp)")
    args = ap.parse_args()
    try:
        asyncio.run(main(args.mini))
    except KeyboardInterrupt:
        print("\nThu công. Sổ sinh tử đã cất vào ngăn kéo.")
