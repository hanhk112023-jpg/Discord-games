"""Vỏ aiogram: nối cái lõi lệnh (long.py) với máy chủ Telegram.

Quy ước ảnh/video: đường dẫn tệp nằm trong assets/, gửi kèm Inline/FS; nếu Telegram
chối (mạng chập chờn), tin vẫn đi dưới dạng chữ — câu chuyện không chết vì một bức tranh.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (BotCommand, CallbackQuery, FSInputFile,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           MenuButtonWebApp, Message, WebAppInfo)

from .. import config
from ..db import Kho
from .hien_thi import GIOI_CAPTION, duong_dan_anh, duong_dan_phim
from .long import Lo, Long, TinDen
from . import vong

log = logging.getLogger("tien.tele")
router = Router()

CAC_LENH_MENU = [
    ("start", "mở menu, xem mình tới đâu"),
    ("dangky", "nhập đạo"),
    ("menu", "bảng điều lệnh"),
    ("nhanvat", "nhìn lại chính mình"),
    ("luyentap", "toạ quan một canh giờ"),
    ("thiennhien", "dẫn thiên địa nhập thể"),
    ("dotpha", "xung quan"),
    ("boss", "chiến trường yêu vương"),
    ("daboss", "lao vào đánh boss"),
    ("pk", "thách đấu: /pk <tên> [cược] [sinhtu]"),
    ("thach", "lời thách đang treo"),
    ("bangpk", "bảng tỉ thí"),
    ("khampha", "khám phá"),
    ("tuido", "túi càn khôn"),
    ("cuahang", "chợ tu chân"),
    ("monphai", "các tông môn"),
    ("troi", "thiên biến"),
    ("chidan", "lời lão bán trà"),
    ("mini", "mở lối web — động tu luyện trong Telegram"),
]


class LoTelegram(Lo):
    """Gửi Trang xuống Telegram: chữ thường → sendMessage; ảnh → sendPhoto;
    video → sendVideo (kèm chữ). Nút → InlineKeyboard."""

    MA_URL_NUT = True  # lớp này biết render nút "url:" thành lối vào Mini App

    def __init__(self, bot: Bot):
        self.bot = bot

    def _kb(self, hang) -> InlineKeyboardMarkup | None:
        if not hang:
            return None
        rows = []
        for row in hang:
            btns = []
            for label, cb in row:
                if str(cb).startswith("url:"):
                    btns.append(InlineKeyboardButton(text=label[:64],
                                                     web_app=WebAppInfo(url=str(cb)[4:])))
                    continue
                cb = str(cb).encode("utf-8")[:60].decode("utf-8", "ignore")
                btns.append(InlineKeyboardButton(text=label[:64], callback_data=cb))
            if btns:
                rows.append(btns)
        return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

    async def gui(self, chat_id: int, trang) -> int | None:
        kb = self._kb(trang.hang)
        if trang.phim:
            p = duong_dan_phim(trang.phim)
            if p is not None:
                try:
                    m = await self.bot.send_video(
                        chat_id, video=FSInputFile(str(p)),
                        caption=trang.html[:GIOI_CAPTION] or None,
                        reply_markup=kb, supports_streaming=True)
                    return m.message_id
                except TelegramBadRequest as e:
                    log.warning("send_video fail %s", e)
        if trang.anh:
            p = duong_dan_anh(trang.anh)
            if p is not None:
                try:
                    m = await self.bot.send_photo(
                        chat_id, photo=FSInputFile(str(p)),
                        caption=trang.html[:GIOI_CAPTION] or None, reply_markup=kb)
                    return m.message_id
                except TelegramBadRequest as e:
                    log.warning("send_photo fail %s", e)
        try:
            m = await self.bot.send_message(chat_id, trang.html or "\u2026",
                                            reply_markup=kb, parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            # nếu HTML có chỗ lệch, gửi trần — mất chữ in đậm còn hơn mất cả câu chuyện
            m = await self.bot.send_message(chat_id, trang.html or "\u2026", reply_markup=kb,
                                            parse_mode=None)
        return m.message_id

    async def sua(self, chat_id: int, msg_id, trang) -> None:
        if msg_id is None:
            return
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id, message_id=int(msg_id), text=trang.html or "\u2026",
                reply_markup=self._kb(trang.hang), parse_mode=ParseMode.HTML)
        except TelegramBadRequest as e:
            if "not modified" not in str(e).lower():
                log.debug("edit fail: %s", e)

    async def bao(self, user_id: int, text: str) -> None:
        pass


async def mo_dong(bot: Bot, kho: Kho, url: str) -> None:
    """Dựng cửa động: nút Menu toàn cục + một lời mời gửi tới những kẻ đã có tên trong sổ.

    Đường dẫn tunnel đổi theo mỗi lần máy chủ thức dậy — ai đã được gửi lời mời thì
    còn bấm tiếp, ai chưa kịp thấy thì `/mini` là chìa khóa dự phòng."""
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
            text="Vào động", web_app=WebAppInfo(url=url)))
    except Exception as e:  # pragma: no cover
        log.warning("Không dựng được nút menu: %s", e)
    from .hien_thi import Trang
    trang = Trang(html=(
        "<b>⛩ Cửa động vừa mở.</b>\n\n"
        "Sau lưng núi có một cái động khô, đặt sẵn bàn đá và đèn dầu. Ai lười gõ lệnh "
        "thì vào đó ngồi — cũng chính thế giới này, cũng chính sổ sách này, chỉ khác "
        "ngươi bấm tay thay vì gõ. Cửa sẽ khép khi trời sáng; hẹn qua <code>/menu</code>."
    ), anh="bia_tien_do.png",
        hang=[[("🏮 Vào động", "url:" + url)]])
    bia = duong_dan_anh("bia_tien_do.png")
    for uid, chat in await kho.danh_thiep_all():
        try:
            if bia is not None:
                await bot.send_photo(chat, photo=FSInputFile(str(bia)),
                                     caption=trang.html, parse_mode="HTML")
            else:
                await bot.send_message(chat, trang.html, parse_mode="HTML")
        except Exception as e:  # pragma: no cover
            log.debug("lời mời tới %s fail: %s", uid, e)


def tao_long(kho: Kho, lo: Lo) -> Long:
    return Long(kho, config.TELE_GUILD, lo,
                thu_duyen=False, admin_ids=config.TELE_ADMIN_IDS)


# ───────────────────────── hai cửa vào: chữ và nút ─────────────────────────

@router.message(F.text)
async def xu_ly_text(message: Message, core: Long) -> None:
    text = message.text or ""
    user = message.from_user
    tin = TinDen(user_id=user.id, chat_id=message.chat.id,
                 ten=user.full_name or user.username or "ai đó",
                 loai="lenh" if text.startswith(("/", "!")) else "text",
                 data=text, msg_id=message.message_id)
    await core.xu_ly(tin)


@router.callback_query()
async def xu_ly_nut(cb: CallbackQuery, core: Long) -> None:
    tin = TinDen(user_id=cb.from_user.id, chat_id=cb.message.chat.id,
                 ten=cb.from_user.full_name or "ai đó",
                 loai="cb", data=cb.data or "", msg_id=cb.message.message_id)
    await core.xu_ly(tin)
    try:
        await cb.answer()
    except TelegramBadRequest:
        pass


# ───────────────────────── khởi động ─────────────────────────

async def chay(kho: Kho | None = None, lo_them=None, gan_core=None) -> None:
    """Nâng bot Telegram. `lo_them`: miệng thứ hai (cửa động) nếu muốn một lõi hai miệng;
    `gan_core`: hàm nhận lõi về tay — Mini App cần nó để lệnh web đi đúng luồng."""
    if not config.TELEGRAM_TOKEN:
        raise SystemExit(
            "Chưa có TELEGRAM_TOKEN.\n"
            "  1. Xin token của bot từ @BotFather\n"
            "  2. Dán vào tệp .env (TELEGRAM_TOKEN=...)\n"
            "  3. Chạy lại: python run_tele.py\n\n"
            "Chưa muốn dựng bot? Diễn tập ngay trong trình duyệt: python tools/tele_dienrap.py")

    bot = Bot(config.TELEGRAM_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    tu_kho = kho is None
    if tu_kho:
        kho = Kho()
        await kho.mo()
    from .long import LoNhip
    lo = LoNhip(LoTelegram(bot), lo_them) if lo_them is not None else LoTelegram(bot)
    core = tao_long(kho, lo)
    if gan_core is not None:
        gan_core(core)
    dp = Dispatcher(core=core, kho=kho)
    dp.include_router(router)
    try:
        await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in CAC_LENH_MENU])
    except Exception as e:  # pragma: no cover
        log.warning("Không đăng ký được menu lệnh: %s", e)
    try:
        await bot.set_my_description("Tiên Đồ Vô Tận — tu chân bằng chữ, có đánh boss và PK.")
    except Exception:
        pass
    if config.TELE_MINIAPP_URL:
        await mo_dong(bot, kho, config.TELE_MINIAPP_URL)

    vong_tai = asyncio.create_task(vong.vong_tron_doi(core, bot))
    log.info("Đã nhập thế qua Telegram — guild diễn tập số %s", config.TELE_GUILD)
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        vong_tai.cancel()
        if tu_kho:
            await kho.dong()
        await bot.session.close()
