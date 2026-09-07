"""Thiên biến: trời tự đổi, hoặc có kẻ cầm quyền đổi hộ trời."""

from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands, tasks

from .. import config, giaodien
from ..bot import TuChanBot
from ..data import sukien as dl_sukien
from ..he import thienbien as he_thienbien
from ..he.ketqua import KetQua

# Xác suất mỗi vòng kiểm tra (30 phút) trời sẽ đổi sắc ở một guild
XAC_SUAT = 0.14


class CogThienBien(commands.Cog, name="Thiên biến"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot
        self.vong_troi.start()

    def cog_unload(self):
        self.vong_troi.cancel()

    # ─────────────── lệnh ───────────────
    @commands.hybrid_command(name="thientuong", aliases=["xemtroi", "sukien"],
                             description="Ngửa mặt xem trời có gì lạ.")
    async def thientuong(self, ctx: commands.Context):
        kq = await he_thienbien.xem_thien_bien(self.bot.kho, ctx.guild.id if ctx.guild else 0)
        await giaodien.gui(ctx, kq)

    @commands.hybrid_command(name="khoisukien", description="[Quản trị] Ép trời đổi sắc.")
    @app_commands.describe(ten="Tên thiên biến (để trống thì tuỳ trời)")
    @commands.has_permissions(manage_guild=True)
    async def khoisukien(self, ctx: commands.Context, *, ten: str | None = None):
        kq = await he_thienbien.khoi_su_kien(
            self.bot.kho, ctx.guild.id if ctx.guild else 0, ten, self.bot.rng)
        await giaodien.gui(ctx, kq)

    @khoisukien.autocomplete("ten")
    async def _ac_sk(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=s.ten, value=s.ten)
            for s in dl_sukien.DANH_SACH.values()
            if current.lower() in s.ten.lower()
        ][:25]

    # ─────────────── vòng trời ───────────────
    @tasks.loop(minutes=30)
    async def vong_troi(self):
        try:
            for guild in self.bot.guilds:
                ket = await he_thienbien.don_dep(self.bot.kho, guild.id)
                kenh = self._kenh(guild)
                if kenh is None:
                    continue
                for cau in ket:
                    await kenh.send(embed=discord.Embed(
                        description=cau, colour=config.MAU_MUC))
                if random.random() < XAC_SUAT:
                    kq = await he_thienbien.khoi_su_kien(self.bot.kho, guild.id, None, self.bot.rng)
                    if kq.thanh_cong:
                        await giaodien.gui(kenh, kq)
        except Exception:  # pragma: no cover
            import logging
            logging.getLogger("tuchan").exception("Vòng trời gặp trục trặc")

    @vong_troi.before_loop
    async def _cho(self):
        await self.bot.wait_until_ready()

    def _kenh(self, guild: discord.Guild):
        uu_tien = ("tu-chan", "tien-hiep", "tu-tien", "giang-ho", "general", "chung")
        for ten in uu_tien:
            for c in guild.text_channels:
                if ten in c.name.lower() and c.permissions_for(guild.me).send_messages:
                    return c
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            return guild.system_channel
        for c in guild.text_channels:
            if c.permissions_for(guild.me).send_messages:
                return c
        return None


async def setup(bot: TuChanBot):
    await bot.add_cog(CogThienBien(bot))
