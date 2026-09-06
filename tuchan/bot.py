"""Thân bot: nối thế giới tu chân với Discord."""

from __future__ import annotations

import logging
import random

import discord
from discord.ext import commands

from . import config
from .db import Kho
from .he.thienco import he_so_the_gioi

log = logging.getLogger("tuchan")

CAC_COG = (
    "tuchan.cogs.nhanvat",
    "tuchan.cogs.tuluyen",
    "tuchan.cogs.phieuluu",
    "tuchan.cogs.luyenche",
    "tuchan.cogs.tongmon",
    "tuchan.cogs.doidau",
    "tuchan.cogs.giaothuong",
    "tuchan.cogs.thienbien",
    "tuchan.cogs.chidan",
)


class TuChanBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.TIEN_TO),
            intents=intents,
            help_command=None,
            description="Tiên Đồ Vô Tận — một thế giới tu chân bằng chữ.",
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
        )
        self.kho = Kho()
        self.rng = random.Random()

    async def setup_hook(self) -> None:
        await self.kho.mo()
        for c in CAC_COG:
            await self.load_extension(c)
            log.info("Đã nạp %s", c)
        if config.GUILD_THU_NGHIEM:
            guild = discord.Object(id=int(config.GUILD_THU_NGHIEM))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Đồng bộ slash trong guild thử nghiệm %s", config.GUILD_THU_NGHIEM)
        else:
            await self.tree.sync()
            log.info("Đồng bộ slash toàn cục (có thể mất tới một giờ để hiện)")

    async def close(self) -> None:
        await self.kho.dong()
        await super().close()

    async def on_ready(self) -> None:
        log.info("Đã nhập thế: %s (%s)", self.user, self.user.id if self.user else "?")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="thiên địa vận chuyển | !chidan",
            )
        )

    # ── tiện ích dùng chung cho các cog ──
    async def he_so(self, guild_id: int | None) -> dict:
        return await he_so_the_gioi(self.kho, int(guild_id or 0))

    async def tu_si_cua(self, user_id: int):
        return await self.kho.lay_tu_si(user_id)


CHUA_NHAP_DAO = (
    "Ngươi còn chưa bước chân vào cửa đạo. Tên ngươi không có trong sổ, "
    "khí tức ngươi không khác gì kẻ gánh nước ngoài chợ.\n\n"
    "*Hãy dùng lệnh nhập đạo trước đã.*"
)

DA_CHET = (
    "Kẻ mang tên này đã chết. Xác đã lạnh, đạo hạnh đã tan theo gió.\n\n"
    "*Nếu còn muốn đi tiếp con đường ấy, hãy chuyển thế — nhưng đừng mong mang được gì sang kiếp sau, "
    "ngoài một cảm giác mơ hồ rằng mình đã từng ngã ở đâu đó.*"
)


async def lay_tu_si_hoac_bao(ctx, bot: TuChanBot, cho_phep_chet: bool = False):
    """Trả về tu sĩ, hoặc None sau khi đã trả lời người dùng."""
    ts = await bot.kho.lay_tu_si(ctx.author.id)
    if ts is None:
        await ctx.send(embed=discord.Embed(
            title="❖ Chưa nhập đạo", description=CHUA_NHAP_DAO, colour=config.MAU_MUC))
        return None
    if ts.da_chet and not cho_phep_chet:
        await ctx.send(embed=discord.Embed(
            title="❖ Người đã khuất", description=DA_CHET, colour=config.MAU_HUYET))
        return None
    return ts
