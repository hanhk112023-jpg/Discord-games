"""Đại chiến yêu vương (boss) — coi chiến trường, lao vào đánh, và chia công."""

from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands, tasks

from .. import config, giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..data import boss as dl_boss
from ..he import dauboss as he_boss


class CogBoss(commands.Cog, name="Yêu vương"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot
        self.vong_chien_truong.start()

    def cog_unload(self):
        self.vong_chien_truong.cancel()

    # ─────────────── xem chiến trường ───────────────
    @commands.hybrid_command(name="boss", aliases=["chientruong", "yêu vương"],
                             description="Xem yêu vương hiện thế và bảng ra tay.")
    async def boss(self, ctx: commands.Context):
        gid = ctx.guild.id if ctx.guild else 0
        kq = await he_boss.hien_trang(self.bot.kho, gid)
        await giaodien.gui(ctx, kq)

    # ─────────────── đánh ───────────────
    @commands.hybrid_command(name="daboss", aliases=["go", "danhboss"],
                             description="Lao vào chiến trường, để lại một vết thương.")
    async def daboss(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        gid = ctx.guild.id if ctx.guild else 0
        hs = await self.bot.he_so(gid)
        kq = await he_boss.danh_thuong(self.bot.kho, ts, gid, self.bot.rng, hs)
        await giaodien.gui(ctx, kq)
        await self._loan(ctx, kq)

    async def _loan(self, ctx, kq):
        """Tin chiến trường loan đi cả kênh."""
        bao = kq.du_lieu.get("thong_bao") or []
        if not bao or ctx.guild is None:
            return
        for dong in bao:
            try:
                await ctx.send(dong[:1900])
            except Exception:  # pragma: no cover
                pass

    # ─────────────── admin triệu boss ───────────────
    @commands.hybrid_command(name="trieuboss", description="[Quản trị] Ép một yêu vương hiện thế.")
    @app_commands.describe(ten="Tên boss (để trống thì tuỳ trời)")
    @commands.has_permissions(manage_guild=True)
    async def trieuboss(self, ctx: commands.Context, *, ten: str | None = None):
        gid = ctx.guild.id if ctx.guild else 0
        ma = None
        if ten:
            for b in dl_boss.DANH_SACH:
                if ten.lower() in b.ten.lower() or ten.lower() == b.ma:
                    ma = b.ma
                    break
        kq = await he_boss.chieu_muoi(self.bot.kho, gid, self.bot.rng, ma, ctx.author.id)
        await giaodien.gui(ctx, kq)
        if kq.thanh_cong:
            await giaodien.gui(ctx, kq, tac_gia="Tin đồn giang hồ")

    @trieuboss.autocomplete("ten")
    async def _ac(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=b.ten, value=b.ten)
            for b in dl_boss.DANH_SACH if current.lower() in b.ten.lower()
        ][:25]

    # ─────────────── vòng chiến trường ───────────────
    @tasks.loop(minutes=5)
    async def vong_chien_truong(self):
        try:
            for gid in await self.bot.kho.cac_guild_co_nguoi():
                bao = await he_boss.don_dep(self.bot.kho, gid, random.Random())
                if not bao:
                    continue
                guild = self.bot.get_guild(gid)
                if guild is None:
                    continue
                chan = self._kenh(guild)
                if chan is None:
                    continue
                for dong in bao:
                    await chan.send(dong[:1900])
        except Exception:  # pragma: no cover
            import logging
            logging.getLogger("tuchan").exception("Vòng chiến trường gặp trục trặc")

    @vong_chien_truong.before_loop
    async def _cho(self):
        await self.bot.wait_until_ready()

    def _kenh(self, guild: discord.Guild):
        uu = ("chien-truong", "chientruong", "boss", "tin-tuc", "thong-bao", "general", "chung")
        for ten in uu:
            for c in guild.text_channels:
                if ten in c.name.lower() and c.permissions_for(guild.me).send_messages:
                    return c
        return guild.system_channel

    # ─────────────── sổ boss ───────────────
    @commands.hybrid_command(name="bosssach", aliases=["danhboss"],
                             description="Điểm danh những yêu vương từng nghe tên.")
    async def bosssach(self, ctx: commands.Context):
        from ..he.ketqua import KetQua
        kq = KetQua(tieu_de="Yêu vương phổ")
        kq.them("Trong cổ tích kể lại có nhiều hơn, nhưng ở vùng đất này thì chỉ từng này kẻ "
                "đã thật sự đứng dậy mà đi:")
        for b in dl_boss.DANH_SACH:
            kq.them(f"**{b.ten}** — *{b.hieu}*. {b.mo_ta}")
        await giaodien.gui(ctx, kq)


async def setup(bot: TuChanBot):
    await bot.add_cog(CogBoss(bot))
