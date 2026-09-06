"""Chợ búa và chuyện trao tay."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..data import vatpham
from ..he import giaothuong as he_giaothuong


class CogGiaoThuong(commands.Cog, name="Giao thương"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="cuahang", aliases=["cho", "phienchoe"],
                             description="Xuống chợ tu chân dưới núi.")
    async def cuahang(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_giaothuong.xem_hang(self.bot.kho, ts, hs, self.bot.rng)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="mua", description="Đặt linh thạch lên chiếu.")
    @app_commands.describe(hang="Tên món hàng", so_luong="Mua mấy phần")
    async def mua(self, ctx: commands.Context, hang: str, so_luong: int = 1):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_giaothuong.mua(self.bot.kho, ts, hang, so_luong, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @mua.autocomplete("hang")
    async def _ac_mua(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=vatpham.ten(m), value=vatpham.ten(m))
            for m in he_giaothuong.HANG_CO_BAN
            if current.lower() in vatpham.ten(m).lower()
        ][:25]

    @commands.hybrid_command(name="ban", description="Bán bớt thứ trong túi, giá rẻ nhưng trả ngay.")
    async def ban(self, ctx: commands.Context, hang: str, so_luong: int = 1):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_giaothuong.ban(self.bot.kho, ts, hang, so_luong, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @ban.autocomplete("hang")
    async def _ac_ban(self, interaction: discord.Interaction, current: str):
        tui = await self.bot.kho.tui(interaction.user.id)
        return [
            app_commands.Choice(name=vatpham.ten(m), value=vatpham.ten(m))
            for m in tui if current.lower() in vatpham.ten(m).lower()
        ][:25]

    @commands.hybrid_command(name="tang", aliases=["trao", "chovat"],
                             description="Đưa một món đồ cho người khác.")
    @app_commands.describe(nguoi="Người nhận", vat="Tên vật phẩm", so_luong="Bao nhiêu")
    async def tang(self, ctx: commands.Context, nguoi: discord.Member, vat: str, so_luong: int = 1):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        nhan = await self.bot.kho.lay_tu_si(nguoi.id)
        if nhan is None:
            await ctx.send("Kẻ đó chưa nhập đạo, đưa vật cho hắn cũng bằng thừa.")
            return
        kq = await he_giaothuong.trao_tay(self.bot.kho, ts, nhan, vat, so_luong)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @tang.autocomplete("vat")
    async def _ac_tang(self, interaction: discord.Interaction, current: str):
        tui = await self.bot.kho.tui(interaction.user.id)
        return [
            app_commands.Choice(name=vatpham.ten(m), value=vatpham.ten(m))
            for m in tui if current.lower() in vatpham.ten(m).lower()
        ][:25]

    @commands.hybrid_command(name="taolinhthach", aliases=["taotien", "chotien"],
                             description="Đẩy một khoản linh thạch qua bàn.")
    async def taolinhthach(self, ctx: commands.Context, nguoi: discord.Member, so: int):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        nhan = await self.bot.kho.lay_tu_si(nguoi.id)
        if nhan is None:
            await ctx.send("Kẻ đó chưa nhập đạo.")
            return
        kq = await he_giaothuong.tang_linh_thach(self.bot.kho, ts, nhan, so)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)


async def setup(bot: TuChanBot):
    await bot.add_cog(CogGiaoThuong(bot))
