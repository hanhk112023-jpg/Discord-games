"""Chỉ dẫn — viết như một lão tiền bối nói chuyện, không phải như bảng hướng dẫn."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot
from ..he import thutich
from ..he.ketqua import KetQua

LOI_MO = (
    "Lão nhân bán trà bên quan đạo rót cho ngươi một chén, không lấy tiền. "
    "Lão nói: *“Ta nhìn ngươi là biết ngươi mới nhập đạo. Ngồi xuống, ta nói cho mấy câu, "
    "nghe hay không thì tuỳ.”*"
)


class CogChiDan(commands.Cog, name="Chỉ dẫn"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="chidan", aliases=["huongdan", "giupdo"],
                             description="Nghe một lão nhân nói về con đường phía trước.")
    async def chidan(self, ctx: commands.Context):
        p = config.TIEN_TO
        kq = KetQua(tieu_de="Lời của lão bán trà", anh="bia_tien_do.png")
        kq.thanh_anh = "giang_ho.mp4"
        kq.them(LOI_MO)
        kq.them(
            "*“Trước hết, phải có tên đã.”*\n"
            f"`{p}dangky` — bước vào cửa đạo, chọn lấy một lai lịch.\n"
            f"`{p}nhanvat` — nhìn lại chính mình. `{p}tuido` — dốc túi ra xem có gì. "
            f"`{p}nhatky` — đọc lại mấy dòng mình từng chép."
        )
        kq.them(
            "*“Tu là ngồi. Ngồi lâu tới mức quên mất mình đang ngồi.”*\n"
            f"`{p}luyentap` — toạ quan, mỗi lần cách nhau một canh giờ.\n"
            f"`{p}thiennhien` — hút linh khí thiên địa: nhanh, và dễ chết.\n"
            f"`{p}dotpha` — xung quan. Khi đan điền đã chật thì hãy nghĩ tới nó, đừng nghĩ sớm hơn.\n"
            f"`{p}duongthuong` — nằm im mà chờ xương liền lại."
        )
        kq.them(
            "*“Trong núi có thứ nuôi ngươi, và có thứ ăn ngươi.”*\n"
            f"`{p}khampha` — đi vào chốn người ta khuyên đừng đi. `{p}diadanh` — xem bản đồ.\n"
            f"`{p}timduoc` — hái thuốc. `{p}duykysi` — tìm kẻ qua đường mà đo sức."
        )
        kq.them(
            "*“Lửa và búa. Hai thứ đó chôn nhiều người hơn đao kiếm.”*\n"
            f"`{p}sotay` — những đan phương ngươi thuộc. `{p}luyendan` — mở lò. `{p}luyenkhi` — rèn pháp bảo.\n"
            f"`{p}deo` — nhỏ tinh huyết nhận chủ một món pháp bảo. `{p}uongdan` — nuốt một viên đan."
        )
        kq.them(
            "*“Một mình thì tự do. Tự do thì đói.”*\n"
            f"`{p}monphai` — nghe kể về các tông môn. `{p}gianhap` — xin vào. `{p}roimon` — xin ra.\n"
            f"`{p}nhiemvu nhan` / `{p}nhiemvu di` / `{p}nhiemvu nop` — việc chấp sự đường giao."
        )
        kq.them(
            "*“Còn chuyện đánh nhau… ai rồi cũng phải đánh.”*\n"
            f"`{p}thidau @người` — thách một người. Thêm `sinhtu:true` nếu ngươi đã chán sống.\n"
            f"`{p}banghieu` — những cái tên đang được nhắc tới."
        )
        kq.them(
            "*“Chợ họp ba phiên một tháng, ai cũng phải xuống chợ.”*\n"
            f"`{p}cuahang` `{p}mua` `{p}ban` `{p}tang @người [vật]` `{p}taolinhthach @người [số]`"
        )
        kq.them(
            "*“Và cuối cùng — nhìn trời.”*\n"
            f"`{p}thientuong` — xem thiên tượng. `{p}canhgioi` — nghe về mười bậc trên con đường này.\n"
            f"`{p}kiepnan` — chín cửa ải chờ sẵn. `{p}kimdan` — vì sao người ta sợ kim đan hạ phẩm.\n"
            f"`{p}binhkhi` — Binh Khí Phổ. `{p}linhdan` — Đan Phổ.\n\n"
            "Mọi lệnh đều dùng được cả hai kiểu: gõ `/` cho gọn, hoặc gõ "
            f"`{p}` cho giống người xưa."
        )
        kq.them(
            "*“Còn một điều nữa.”* Lão rót thêm chén trà, không nhìn ngươi. "
            "*“Đừng vội. Kẻ vội thì chết sớm, mà chết sớm thì không ai nhớ tên.”*"
        )
        await giaodien.gui(ctx, kq)

    @commands.hybrid_command(name="canhgioi", aliases=["bacthang"],
                             description="Mười bậc lớn, sáu mươi mốt bậc nhỏ trên con đường tu hành.")
    async def canhgioi(self, ctx: commands.Context):
        await giaodien.gui(ctx, thutich.bia_muoi_bac())

    @commands.hybrid_command(name="kiepnan", aliases=["cuaai", "khaonghiem"],
                             description="Chín cửa ải trời đặt sẵn trước mỗi bậc lớn.")
    async def kiepnan(self, ctx: commands.Context):
        await giaodien.gui(ctx, thutich.chin_cua_ai())

    @commands.hybrid_command(name="binhkhi", aliases=["phapbao", "khipho"],
                             description="Binh Khí Phổ — những món khí giới còn được nhắc tên.")
    @app_commands.describe(pham="Chỉ xem khí giới từ phẩm này trở lên (1–9)")
    async def binhkhi(self, ctx: commands.Context, pham: int | None = None):
        await giaodien.gui(ctx, thutich.binh_khi_pho(pham or 1))

    @commands.hybrid_command(name="linhdan", aliases=["danpho", "dancac"],
                             description="Đan Phổ — những viên đan mà đan sư trong thiên hạ còn luyện.")
    async def linhdan(self, ctx: commands.Context):
        await giaodien.gui(ctx, thutich.dan_pho())

    @commands.hybrid_command(name="kimdan", aliases=["danpham"],
                             description="Chín phẩm kim đan, và vì sao người ta sợ phẩm thấp.")
    async def kimdan(self, ctx: commands.Context):
        await giaodien.gui(ctx, thutich.kim_dan_pho())

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                description="Ngươi nói chưa hết câu. Người nghe nhíu mày, chờ.",
                colour=config.MAU_MUC))
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                description="Ngươi không có tư cách ra lệnh cho trời.", colour=config.MAU_HUYET))
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(
                description="Chậm lại. Vội trên đường tu là cách chết chậm mà chắc.",
                colour=config.MAU_MUC))
            return
        import logging
        logging.getLogger("tuchan").exception("Lỗi lệnh: %s", error)
        await ctx.send(embed=discord.Embed(
            description=("Thiên cơ hỗn loạn, có thứ gì đó trong thế giới này vừa trục trặc. "
                         "Hãy thử lại sau một lát."),
            colour=config.MAU_HUYET))


async def setup(bot: TuChanBot):
    await bot.add_cog(CogChiDan(bot))
