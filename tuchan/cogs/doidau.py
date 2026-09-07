"""Thí đấu giữa người với người."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..canhgioi import ten_canh_gioi
from ..he import thidau as he_thidau


class UngChien(discord.ui.View):
    def __init__(self, cog: "CogDoiDau", ctx: commands.Context, a_id: int, b_id: int, sinh_tu: bool):
        super().__init__(timeout=120)
        self.cog = cog
        self.ctx = ctx
        self.a_id = a_id
        self.b_id = b_id
        self.sinh_tu = sinh_tu
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
        a = await self.cog.bot.kho.lay_tu_si(self.a_id)
        b = await self.cog.bot.kho.lay_tu_si(self.b_id)
        if a is None or b is None:
            await interaction.followup.send("Một trong hai bên đã không còn ở đây.")
            return
        if a.dang_bi_thuong or b.dang_bi_thuong:
            await interaction.followup.send(
                "Một bên còn mang thương thế. Đánh nhau lúc này thì không phải tỉ thí, mà là hành hình.")
            return
        hs = await self.cog.bot.he_so(interaction.guild_id or 0)
        kq = await he_thidau.thi_dau(self.cog.bot.kho, a, b, self.cog.bot.rng, hs, self.sinh_tu)
        await giaodien.gui(interaction, kq)
        self.stop()

    @discord.ui.button(label="Khước từ", style=discord.ButtonStyle.secondary)
    async def tu_choi(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.xong = True
        for c in self.children:
            c.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=discord.Embed(
            description=(
                f"**{interaction.user.display_name}** chắp tay: *“Hôm nay không tiện.”*\n\n"
                "Từ chối một lời thách không phải là hèn. Trong giang hồ, kẻ biết lúc nào nên đánh "
                "thường sống lâu hơn kẻ lúc nào cũng dám đánh."),
            colour=config.MAU_MUC))
        self.stop()

    async def on_timeout(self):
        if self.xong:
            return
        try:
            await self.ctx.send(embed=discord.Embed(
                description=("Lời thách treo giữa không trung một hồi lâu rồi rơi xuống đất. "
                             "Không ai bước ra. Đám đông tản đi, hơi thất vọng."),
                colour=config.MAU_MUC))
        except Exception:
            pass


class CogDoiDau(commands.Cog, name="Đối đầu"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="thidau", aliases=["thachdau"],
                             description="Thách một người khác đo sức.")
    @app_commands.describe(nguoi="Kẻ ngươi muốn thách", sinhtu="Đặt cược cả tính mạng?")
    async def thidau(self, ctx: commands.Context, nguoi: discord.Member, sinhtu: bool = False):
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
        if doi.da_chet:
            await ctx.send("Kẻ ấy đã chết. Chuyện cũ thì thôi bỏ qua.")
            return
        if ts.dang_bi_thuong:
            await ctx.send("Với thương thế này mà đòi lên đài? Ngươi muốn chết cho nhanh à.")
            return

        e = discord.Embed(
            title="❖ Lời thách",
            description=(
                f"**{ts.ten}** — {ten_canh_gioi(ts.canh_gioi, ts.tang)} — bước ra giữa sân, "
                f"chắp tay về phía **{doi.ten}**.\n\n"
                + (f"*“Ta muốn thỉnh giáo. **Sinh tử chiến** — sống chết tự chịu, không oán không hối.”*"
                   if sinhtu else
                   f"*“Ta muốn thỉnh giáo vài chiêu. Điểm tới là dừng.”*")
                + "\n\nĐám đông giãn ra thành một vòng tròn. Bây giờ, chuyện tuỳ ở kẻ được thách."
            ),
            colour=config.MAU_HUYET if sinhtu else config.MAU_MUC,
        )
        anh = giaodien.duong_dan_anh("dau_phap.png")
        files = []
        if anh:
            files.append(discord.File(str(anh), filename=anh.name))
            e.set_image(url=f"attachment://{anh.name}")
        await ctx.send(
            content=nguoi.mention, embed=e, files=files,
            view=UngChien(self, ctx, ctx.author.id, nguoi.id, sinhtu))


async def setup(bot: TuChanBot):
    await bot.add_cog(CogDoiDau(bot))
