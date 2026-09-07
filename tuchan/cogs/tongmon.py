"""Tông môn: cổng núi, chấp sự đường, và việc phải làm."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..canhgioi import ten_canh_gioi
from ..data import monphai as dl_monphai
from ..he import tongmon as he_tongmon
from ..he.ketqua import KetQua


class CogTongMon(commands.Cog, name="Tông môn"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="monphai", aliases=["tongmon"],
                             description="Nghe người ta kể về các tông môn trong thiên hạ.")
    async def monphai(self, ctx: commands.Context, *, ten: str | None = None):
        if ten:
            mp = dl_monphai.tim_theo_ten(ten)
            if mp is None:
                await ctx.send("Không có tông môn nào tên như thế — hoặc có, nhưng người biết đã chết cả rồi.")
                return
            kq = KetQua(tieu_de=mp.ten, anh=mp.tranh or None)
            kq.them(f"**{mp.ten}** — {mp.tinh_chat}. {mp.dia_the}.")
            kq.them(mp.mo_ta)
            kq.them(f"**Quy củ:** {mp.quy_cu}")
            kq.them(f"**Trấn phái công pháp:** {mp.cong_phap}. {mp.cong_phap_mo_ta}")
            kq.them(f"Cổng núi chỉ mở cho kẻ đã tới **{ten_canh_gioi(mp.yeu_cau_canh_gioi, mp.yeu_cau_tang)}** trở lên.")
            await giaodien.gui(ctx, kq)
            return

        kq = KetQua(tieu_de="Các tông môn trong vùng")
        kq.them(
            "Ở tửu lâu, một lão tán tu uống hết chén thứ ba thì bắt đầu kể. "
            "Lão kể như thể chính mình từng đứng trước từng cánh cổng ấy — có thể là thật."
        )
        for mp in dl_monphai.DANH_SACH.values():
            kq.them(
                f"**{mp.ten}** *({mp.tinh_chat})* — {mp.dia_the}.\n"
                f"{mp.mo_ta.split('.')[0]}. Nhận đệ tử từ {ten_canh_gioi(mp.yeu_cau_canh_gioi, mp.yeu_cau_tang)}."
            )
        kq.them("*Muốn biết kỹ thì hỏi thẳng tên một môn. Muốn vào thì phải tự leo lên tới cổng.*")
        await giaodien.gui(ctx, kq)

    @commands.hybrid_command(name="gianhap", description="Quỳ ba lạy trước tổ sư đường.")
    @app_commands.describe(mon="Tên tông môn muốn xin vào")
    async def gianhap(self, ctx: commands.Context, *, mon: str):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        kq = await he_tongmon.gia_nhap(self.bot.kho, ts, mon, self.bot.rng)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @gianhap.autocomplete("mon")
    async def _ac_mon(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=mp.ten, value=mp.ten)
            for mp in dl_monphai.DANH_SACH.values()
            if current.lower() in mp.ten.lower()
        ][:25]

    @commands.hybrid_command(name="roimon", description="Gạch tên mình khỏi sổ tông môn.")
    async def roimon(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        kq = await he_tongmon.roi_mon(self.bot.kho, ts)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="nhiemvu", aliases=["viecmon", "chapsu"],
                             description="Tới chấp sự đường xem có ai cần nhờ việc.")
    @app_commands.describe(viec="nhan | xem | di | nop")
    async def nhiemvu(self, ctx: commands.Context, viec: str = "xem"):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        v = viec.strip().lower()
        if v in ("nhan", "nhận", "moi", "mới"):
            kq = await he_tongmon.nhan_viec(self.bot.kho, ts, self.bot.rng)
        elif v in ("di", "đi", "lenduong", "lên đường"):
            kq = await he_tongmon.di_viec(self.bot.kho, ts, self.bot.rng, hs)
        elif v in ("nop", "nộp", "giao"):
            kq = await he_tongmon.nop_viec(self.bot.kho, ts)
        else:
            dang = await self.bot.kho.viec_hien_tai(ts.user_id)
            kq = await (he_tongmon.xem_viec(self.bot.kho, ts) if dang
                        else he_tongmon.nhan_viec(self.bot.kho, ts, self.bot.rng))
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @nhiemvu.autocomplete("viec")
    async def _ac_viec(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=n, value=v) for n, v in (
                ("Xem việc đang dở", "xem"), ("Nhận việc mới", "nhan"),
                ("Lên đường", "di"), ("Nộp đồ", "nop"))
            if current.lower() in n.lower()
        ]


async def setup(bot: TuChanBot):
    await bot.add_cog(CogTongMon(bot))
