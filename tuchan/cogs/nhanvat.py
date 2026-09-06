"""Nhập đạo, soi lại chính mình, và chuyện sinh tử."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..canhgioi import ten_canh_gioi
from ..data import xuatthan as dl_xuatthan
from ..he import nhanvat as he_nhanvat
from ..he.ketqua import KetQua


class ChonXuatThan(discord.ui.Select):
    def __init__(self, cog: "CogNhanVat", user_id: int):
        self.cog = cog
        self.user_id = user_id
        opts = [
            discord.SelectOption(
                label=x.ten,
                value=x.ma,
                description=(x.linh_can[:95]),
            )
            for x in dl_xuatthan.DANH_SACH.values()
        ]
        super().__init__(placeholder="Ngươi từ đâu tới?", options=opts, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Đây không phải chuyện của ngươi.", ephemeral=True)
            return
        await interaction.response.send_modal(KhaiTen(self.cog, self.values[0]))


class KhaiTen(discord.ui.Modal, title="Khai tên trước cửa đạo"):
    ten = discord.ui.TextInput(
        label="Đạo hiệu", placeholder="Hàn Lập, Vương Lâm, Mạnh Hạo…",
        max_length=24, required=True,
    )
    gioi_tinh = discord.ui.TextInput(
        label="Nam hay nữ", placeholder="nam / nữ", max_length=6, required=True, default="nam",
    )

    def __init__(self, cog: "CogNhanVat", ma_xuat_than: str):
        super().__init__()
        self.cog = cog
        self.ma_xuat_than = ma_xuat_than

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        kq = await he_nhanvat.tao_nhan_vat(
            self.cog.bot.kho,
            interaction.user.id,
            interaction.guild_id or 0,
            str(self.ten),
            str(self.gioi_tinh),
            self.ma_xuat_than,
            self.cog.bot.rng,
        )
        kq.thanh_anh = "nhap_dao.mp4"
        await giaodien.gui(interaction, kq, tac_gia=interaction.user.display_name)


class BangNhapDao(discord.ui.View):
    def __init__(self, cog: "CogNhanVat", user_id: int):
        super().__init__(timeout=180)
        self.add_item(ChonXuatThan(cog, user_id))


class CogNhanVat(commands.Cog, name="Nhân vật"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    # ─────────────── nhập đạo ───────────────
    @commands.hybrid_command(
        name="dangky", aliases=["nhapdao"],
        description="Bước chân vào cửa đạo, khai tên vào sổ sinh tử.")
    async def dangky(self, ctx: commands.Context):
        cu = await self.bot.kho.lay_tu_si(ctx.author.id)
        if cu is not None and not cu.da_chet:
            await ctx.send(embed=discord.Embed(
                title="❖ Tên ngươi đã có trong sổ",
                description=(
                    f"**{cu.ten}** — {ten_canh_gioi(cu.canh_gioi, cu.tang)}.\n\n"
                    "Một người chỉ sống được một đời. Sống cho hết cái đã có đi đã."
                ),
                colour=config.MAU_MUC))
            return
        if cu is not None and cu.da_chet:
            await ctx.send(embed=discord.Embed(
                title="❖ Người đã khuất",
                description=("Kẻ mang tên ấy đã chết rồi. Muốn đi tiếp thì phải **chuyển thế**."),
                colour=config.MAU_HUYET))
            return

        e = discord.Embed(
            title="❖ Trước cửa đạo",
            description=(
                "Ngươi đứng dưới chân núi, ngửa mặt nhìn con đường đá dẫn lên chỗ mây phủ. "
                "Gió trên cao mang xuống mùi tuyết và mùi hương lạ.\n\n"
                "Trước khi bước, có một câu phải trả lời — câu mà cả đời tu hành ngươi sẽ bị hỏi lại nhiều lần:\n\n"
                "**Ngươi từ đâu tới?**"
            ),
            colour=config.MAU_LINH,
        )
        anh = giaodien.duong_dan_anh("bia_tien_do.png")
        files = []
        if anh:
            files.append(discord.File(str(anh), filename=anh.name))
            e.set_image(url=f"attachment://{anh.name}")
        await ctx.send(embed=e, files=files, view=BangNhapDao(self, ctx.author.id))

    # ─────────────── xem mình ───────────────
    @commands.hybrid_command(name="nhanvat", aliases=["ta", "banthan"],
                             description="Nhìn lại chính mình: tu vi, thân thể, đạo tâm, vật tuỳ thân.")
    async def nhanvat(self, ctx: commands.Context, nguoi: discord.Member | None = None):
        muc_tieu = nguoi or ctx.author
        ts = await self.bot.kho.lay_tu_si(muc_tieu.id)
        if ts is None:
            await ctx.send(embed=discord.Embed(
                title="❖ Không có người này trong sổ",
                description=("Kẻ ngươi hỏi tới chưa từng bước vào cửa đạo."
                             if nguoi else
                             "Ngươi còn chưa nhập đạo. Hãy dùng lệnh `dangky` trước."),
                colour=config.MAU_MUC))
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_nhanvat.xem_nhan_vat(self.bot.kho, ts, hs)
        if nguoi and nguoi.id != ctx.author.id:
            kq.van.insert(0, (
                f"Ngươi đứng từ xa quan sát **{ts.ten}**. Nhìn người khác thì dễ, "
                "nhìn mình mới khó."))
        await giaodien.gui(ctx, kq, tac_gia=muc_tieu.display_name)

    # ─────────────── nhật ký ───────────────
    @commands.hybrid_command(name="nhatky", description="Đọc lại mấy dòng ngươi từng chép trong đời tu.")
    async def nhatky(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot, cho_phep_chet=True)
        if ts is None:
            return
        dong = await self.bot.kho.doc_nhat_ky(ts.user_id, 10)
        kq = KetQua(tieu_de=f"Thủ ký của {ts.ten}")
        if not dong:
            kq.them("Trang giấy trắng. Ngươi chưa làm được việc gì đáng để chép lại.")
        else:
            kq.them("Mấy dòng chép vội bằng mực loãng, chữ sau đè lên chữ trước:")
            kq.them("\n".join(f"— *{d['noi_dung']}*" for d in dong))
            kq.them("Ngươi gấp sổ lại. Có những chuyện chép ra rồi mới thấy nó ngắn đến thế.")
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    # ─────────────── bảng danh ───────────────
    @commands.hybrid_command(name="banghieu", aliases=["bangdanh"],
                             description="Xem những cái tên hiện đang được nhắc tới nhiều nhất.")
    async def banghieu(self, ctx: commands.Context):
        ds = await self.bot.kho.bang_danh_vong(10)
        kq = KetQua(tieu_de="Bảng danh trong giang hồ")
        if not ds:
            kq.them("Giang hồ vắng lặng. Chưa có ai đáng để nhắc tới.")
        else:
            kq.them(
                "Ở tửu lâu bên quan đạo, người ta vẫn kể chuyện. Kể lâu ngày thì thành một cái bảng, "
                "tuy chẳng ai chép nó xuống:"
            )
            dong = []
            for i, t in enumerate(ds, 1):
                mo = "đã khuất" if t.da_chet else ten_canh_gioi(t.canh_gioi, t.tang)
                dong.append(f"**{i}. {t.ten}** — {mo}")
            kq.them("\n".join(dong))
            kq.them("Đứng đầu bảng không có nghĩa là sống lâu nhất. Thường thì ngược lại.")
        await giaodien.gui(ctx, kq)

    # ─────────────── chuyển thế ───────────────
    @commands.hybrid_command(name="chuyenthe", description="Kẻ đã chết xin một kiếp khác.")
    @app_commands.describe(ten="Đạo hiệu kiếp này", xuat_than="Lai lịch kiếp này")
    async def chuyenthe(self, ctx: commands.Context, ten: str, xuat_than: str = "pham_nhan"):
        ts = await self.bot.kho.lay_tu_si(ctx.author.id)
        if ts is None:
            await ctx.send("Ngươi còn chưa từng sống, lấy gì mà chuyển thế.")
            return
        kq = await he_nhanvat.chuyen_the(self.bot.kho, ts, ten, xuat_than, self.bot.rng)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @chuyenthe.autocomplete("xuat_than")
    async def _ac_xuat_than(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=x.ten, value=x.ma)
            for x in dl_xuatthan.DANH_SACH.values()
            if current.lower() in x.ten.lower() or current.lower() in x.ma
        ][:25]

    @commands.hybrid_command(name="xoaminh", description="Xoá sạch dấu vết của ngươi khỏi thế giới này.")
    async def xoaminh(self, ctx: commands.Context, xac_nhan: str = ""):
        if xac_nhan.strip().lower() not in ("dong y", "đồng ý", "xac nhan", "xác nhận"):
            await ctx.send(embed=discord.Embed(
                title="❖ Việc này không quay lại được",
                description=("Xoá đi thì mọi thứ ngươi từng nhặt, từng luyện, từng chịu đau để có — "
                             "đều tan hết.\n\nNếu đã quyết, hãy gõ lại lệnh kèm hai chữ **đồng ý**."),
                colour=config.MAU_HUYET))
            return
        await self.bot.kho.xoa_tu_si(ctx.author.id)
        await ctx.send(embed=discord.Embed(
            title="❖ Xoá tên",
            description=("Trang sổ bị xé ra, đốt đi. Tro bay lên rồi tản mất trong gió núi. "
                         "Thế gian này vốn không nhớ ai lâu."),
            colour=config.MAU_MUC))


async def setup(bot: TuChanBot):
    await bot.add_cog(CogNhanVat(bot))
