"""Toạ quan, dẫn khí, và xung quan."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..canhgioi import la_dinh_canh
from ..data import vatpham
from ..he import tuluyen as he_tuluyen
from ..he import luyenche as he_luyenche
from ..he import phieuluu as he_phieuluu
from ..data import dichthu as dl_dichthu


class CogTuLuyen(commands.Cog, name="Tu luyện"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="luyentap", aliases=["toaquan"],
                             description="Ngồi xuống, thở, và đổi thời gian lấy đạo hạnh.")
    async def luyentap(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_tuluyen.luyen_tap(self.bot.kho, ts, self.bot.rng, hs)
        if kq.du_lieu.get("san_sang_dot_pha"):
            kq.chu_thich = "Cửa ải đang mở — dùng lệnh đột phá khi ngươi thấy mình đã sẵn sàng."
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="thiennhien", aliases=["hapthu"],
                             description="Hấp thu linh khí thiên địa: nhanh gấp bội, và nguy gấp bội.")
    async def thiennhien(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_tuluyen.hap_thu_thien_dia(self.bot.kho, ts, self.bot.rng, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

        ma_dich = kq.du_lieu.get("gap_dich")
        if ma_dich:
            d = dl_dichthu.lay(ma_dich)
            ts2 = await self.bot.kho.lay_tu_si(ctx.author.id)
            if d and ts2 and not ts2.dang_bi_thuong:
                kq2 = await he_phieuluu.dau_voi_dich(
                    self.bot.kho, ts2, d, self.bot.rng, hs,
                    boi_canh="Hắn xuống ngựa. Không hỏi tên, không hỏi môn phái. Chỉ rút binh khí ra.")
                await giaodien.gui(ctx, kq2, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="dotpha", aliases=["xungquan"],
                             description="Đem cả mạng ra đánh cược lấy một bậc cảnh giới.")
    @app_commands.describe(dan="Tên đan dược hỗ trợ (nếu có)")
    async def dotpha(self, ctx: commands.Context, dan: str | None = None):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        ma_dan = None
        if dan:
            from ..he.giaothuong import tim_hang
            ma_dan = tim_hang(dan)
            if ma_dan is None:
                await ctx.send("Không có thứ đan dược nào tên như vậy.")
                return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        len_bac = la_dinh_canh(ts.canh_gioi, ts.tang)
        kq = await he_tuluyen.dot_pha(self.bot.kho, ts, self.bot.rng, hs, ma_dan)
        if kq.du_lieu.get("thanh_cong") and len_bac:
            kq.thanh_anh = "dot_pha.mp4"
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @dotpha.autocomplete("dan")
    async def _ac_dan(self, interaction: discord.Interaction, current: str):
        tui = await self.bot.kho.tui(interaction.user.id)
        ra = []
        for ma in tui:
            vp = vatpham.lay(ma)
            if vp and vp.loai == "dan_duoc" and "dot_pha" in vp.hieu_qua:
                if current.lower() in vp.ten.lower():
                    ra.append(app_commands.Choice(name=vp.ten, value=vp.ten))
        return ra[:25]

    @commands.hybrid_command(name="uongdan", aliases=["dungdan"],
                             description="Nuốt một viên đan dược.")
    async def uongdan(self, ctx: commands.Context, *, dan: str):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        from ..he.giaothuong import tim_hang
        ma = tim_hang(dan)
        if ma is None:
            await ctx.send("Ngươi mò trong túi mà không thấy thứ nào tên như thế.")
            return
        kq = await he_luyenche.uong_dan(self.bot.kho, ts, ma, self.bot.rng)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @uongdan.autocomplete("dan")
    async def _ac_uong(self, interaction: discord.Interaction, current: str):
        tui = await self.bot.kho.tui(interaction.user.id)
        ra = []
        for ma in tui:
            vp = vatpham.lay(ma)
            if vp and vp.loai == "dan_duoc" and current.lower() in vp.ten.lower():
                ra.append(app_commands.Choice(name=vp.ten, value=vp.ten))
        return ra[:25]

    @commands.hybrid_command(name="duongthuong", aliases=["nghi"],
                             description="Nằm im mà chờ thân thể tự vá lại.")
    async def duongthuong(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        from ..vanphong import khac_gio, mo_ta_than_the
        from ..he.ketqua import KetQua
        kq = KetQua(tieu_de="Dưỡng thương")
        if ts.dang_bi_thuong:
            kq.them(
                "Ngươi trải áo xuống nền hang, nằm nghiêng, tay đè lên chỗ xương sườn gãy. "
                "Trần hang có một vệt nước rỉ, nhỏ từng giọt xuống một vũng nhỏ. Ngươi đếm tới giọt thứ hai trăm thì thôi đếm."
            )
            kq.them(f"Còn {khac_gio(ts.con_bao_lau_duong_thuong)} nữa mới cử động mạnh được. "
                    "Nếu có Liễm Thương Đan thì nên dùng — nằm không cũng chẳng làm ngươi khá lên nhanh hơn.")
        else:
            ts.than_the = min(100, ts.than_the + 10)
            await self.bot.kho.luu(ts)
            kq.them(
                "Ngươi ngồi tựa vách, nhắm mắt, để chân khí tự đi một vòng chậm rãi khắp châu thân, "
                "vá lại những chỗ rách nhỏ mà mắt không nhìn thấy."
            )
            kq.them(mo_ta_than_the(ts.than_the, False))
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)


async def setup(bot: TuChanBot):
    await bot.add_cog(CogTuLuyen(bot))
