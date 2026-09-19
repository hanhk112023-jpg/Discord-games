"""Thí đấu giữa hai người tu hành — lời thách treo, ứng chiến bằng nút, có thể cá cược."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..he import pk as he_pk
from ..he.ketqua import KetQua


class UngChien(discord.ui.View):
    def __init__(self, cog: "CogDoiDau", a_id: int, b_id: int, ma_thach: int):
        super().__init__(timeout=600)
        self.cog = cog
        self.a_id = a_id
        self.b_id = b_id
        self.ma_thach = ma_thach
        self.xong = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.b_id:
            await interaction.response.send_message(
                "Lời thách này không gửi cho ngươi. Đứng xem thôi.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Ứng chiến", style=discord.ButtonStyle.danger)
    async def ung(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.xong = True
        for c in self.children:
            c.disabled = True
        await interaction.response.edit_message(view=self)
        b = await self.cog.bot.kho.lay_tu_si(self.b_id)
        if b is None:
            await interaction.followup.send("Một trong hai bên đã không còn ở đây.")
            return
        hs = await self.cog.bot.he_so(interaction.guild_id or 0)
        kq = await he_pk.ung_chien(self.cog.bot.kho, self.ma_thach, b, self.cog.bot.rng, hs)
        await giaodien.gui(interaction, kq)
        self.stop()

    @discord.ui.button(label="Khước từ", style=discord.ButtonStyle.secondary)
    async def tu_choi(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.xong = True
        for c in self.children:
            c.disabled = True
        await interaction.response.edit_message(view=self)
        b = await self.cog.bot.kho.lay_tu_si(self.b_id)
        if b is not None:
            kq = await he_pk.tu_khuoc(self.cog.bot.kho, self.ma_thach, b)
        else:
            kq = KetQua(tieu_de="Lời thách không còn", van=["Chuyện cũ rồi."])
        await giaodien.gui(interaction, kq)
        self.stop()

    async def on_timeout(self):
        if self.xong:
            return
        try:
            await self.cog.bot.kho.thach_xoa(self.ma_thach)
            ch = self.cog.bot.get_channel(self.cog.channel_id)
            if ch is not None:
                await ch.send(embed=discord.Embed(
                    description=("Lời thách treo giữa không trung một hồi lâu rồi rơi xuống đất. "
                                 "Không ai bước ra. Đám đông tản đi, hơi thất vọng."),
                    colour=config.MAU_MUC))
        except Exception:
            pass


class CogDoiDau(commands.Cog, name="Đối đầu"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot
        self.channel_id = 0

    @commands.hybrid_command(name="thidau", aliases=["thachdau", "pk"],
                             description="Thách một người khác đo sức — có thể cá cược linh thạch.")
    @app_commands.describe(nguoi="Kẻ ngươi muốn thách",
                           sinhtu="Đặt cược cả tính mạng?",
                           cuoc="Số linh thạch hai bên cùng đặt (tuỳ chọn)")
    async def thidau(self, ctx: commands.Context, nguoi: discord.Member,
                     sinhtu: bool = False, cuoc: int | None = None):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        if nguoi.id == ctx.author.id:
            await ctx.send("Đánh với chính mình thì khỏi cần đài — ngươi làm việc đó mỗi đêm rồi.")
            return
        if nguoi.bot:
            await ctx.send("Thứ đó không có xương để mà gãy.")
            return
        doi = await self.bot.kho.lay_tu_si(nguoi.id)
        if doi is None:
            await ctx.send(f"**{nguoi.display_name}** chưa từng bước vào cửa đạo. Đánh hắn thì mang tiếng.")
            return
        ma, kq = await he_pk.thach_thuc(self.bot.kho, ts, doi, int(cuoc or 0), sinhtu)
        self.channel_id = ctx.channel.id
        if not kq.thanh_cong:
            await giaodien.gui(ctx, kq)
            return
        embeds, files = giaodien.dung_embed(kq)
        await ctx.send(content=nguoi.mention, embed=embeds[0], files=files,
                       view=UngChien(self, ts.user_id, doi.user_id, ma))

    @commands.hybrid_command(name="thach", aliases=["loithach"],
                             description="Xem những lời thách còn treo trên đầu mình.")
    async def thach(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        await giaodien.gui(ctx, await he_pk.danh_sach_thach(self.bot.kho, ts))

    @commands.hybrid_command(name="bangpk", aliases=["bangtythi"],
                             description="Bảng tỉ thí: ai thắng ai, ai bất bại.")
    async def bangpk(self, ctx: commands.Context):
        ts = await self.bot.kho.lay_tu_si(ctx.author.id)
        await giaodien.gui(ctx, await he_pk.bang_pk(self.bot.kho, ts))


async def setup(bot: TuChanBot):
    await bot.add_cog(CogDoiDau(bot))
