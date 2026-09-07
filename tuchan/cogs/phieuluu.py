"""Ra khỏi cửa động: khám phá, hái thuốc, tỉ thí với kẻ qua đường."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..data import diadanh as dl_diadanh
from ..he import phieuluu as he_phieuluu
from ..he.ketqua import KetQua


class CogPhieuLuu(commands.Cog, name="Phiêu lưu"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="khampha", aliases=["dilai"],
                             description="Đi vào chỗ người ta khuyên đừng đi.")
    @app_commands.describe(noi="Tên địa danh muốn tới (để trống thì đi đâu tuỳ chân)")
    async def khampha(self, ctx: commands.Context, *, noi: str | None = None):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        ma = None
        if noi:
            dd = dl_diadanh.tim_theo_ten(noi)
            if dd is None:
                await ctx.send("Không ai nghe nói tới một nơi như thế bao giờ.")
                return
            ma = dd.ma
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_phieuluu.kham_pha(self.bot.kho, ts, self.bot.rng, hs, ma)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @khampha.autocomplete("noi")
    async def _ac_noi(self, interaction: discord.Interaction, current: str):
        ts = await self.bot.kho.lay_tu_si(interaction.user.id)
        cg = ts.canh_gioi if ts else 0
        return [
            app_commands.Choice(name=d.ten, value=d.ten)
            for d in dl_diadanh.cho_phep(cg)
            if current.lower() in d.ten.lower()
        ][:25]

    @commands.hybrid_command(name="diadanh", aliases=["bando"],
                             description="Những nơi ngươi biết đường tới.")
    async def diadanh(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        kq = KetQua(tieu_de="Những chốn ngươi biết đường tới")
        kq.them(
            "Ngươi trải tấm bản đồ da dê đã sờn lên bàn đá. Mực vẽ nhoè ở mấy chỗ, "
            "và có mấy vòng tròn đỏ mà chính ngươi cũng không nhớ vì sao mình khoanh."
        )
        cho_phep = dl_diadanh.cho_phep(ts.canh_gioi)
        for d in dl_diadanh.DANH_SACH.values():
            if d in cho_phep:
                kq.them(f"**{d.ten}** — {d.mo_ta}")
            else:
                kq.them(
                    f"**{d.ten}** — nơi này nằm ngoài rìa bản đồ của ngươi. "
                    "Người ta nhắc tới nó bằng giọng hạ thấp, và ngươi chưa đủ tư cách để hỏi thêm."
                )
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="timduoc", aliases=["haithuoc"],
                             description="Cúi lưng cả buổi để đổi lấy vài nhánh cỏ.")
    async def timduoc(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_phieuluu.tim_duoc(self.bot.kho, ts, self.bot.rng, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="duykysi", aliases=["tithi"],
                             description="Tìm một kẻ qua đường mà đo sức.")
    async def duykysi(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_phieuluu.duy_ky_si(self.bot.kho, ts, self.bot.rng, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)


async def setup(bot: TuChanBot):
    await bot.add_cog(CogPhieuLuu(bot))
