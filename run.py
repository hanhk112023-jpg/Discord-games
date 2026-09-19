"""Điểm khởi mặc định: Telegram Mini App (và bot nếu có token)."""
import asyncio
from run_tele import main

if __name__ == "__main__":
    try:
        asyncio.run(main(mini=True))
    except KeyboardInterrupt:
        print("\nThu công. Sổ sinh tử đã cất vào ngăn kéo.")
