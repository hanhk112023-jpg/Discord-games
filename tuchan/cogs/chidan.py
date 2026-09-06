"""Chỉ dẫn — viết như một lão tiền bối nói chuyện, không phải như bảng hướng dẫn."""

from __future__ import annotations

import discord
from discord.ext import commands

from .. import config, giaodien
from ..bot import TuChanBot
from ..canhgioi import BANG_CANH_GIOI
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
            f"`{p}thientuong` — xem thiên tượng. `{p}canhgioi` — nghe về mười bậc trên con đường này.\n\n"
            "Mọi lệnh đều dùng được cả hai kiểu: gõ `/` cho gọn, hoặc gõ "
            f"`{p}` cho giống người xưa."
        )
        kq.them(
            "*“Còn một điều nữa.”* Lão rót thêm chén trà, không nhìn ngươi. "
            "*“Đừng vội. Kẻ vội thì chết sớm, mà chết sớm thì không ai nhớ tên.”*"
        )
        await giaodien.gui(ctx, kq)

    @commands.hybrid_command(name="canhgioi", aliases=["bacthang"],
                             description="Mười bậc trên con đường tu hành.")
    async def canhgioi(self, ctx: commands.Context):
        kq = KetQua(tieu_de="Mười bậc")
        kq.them(
            "Trong Tàng Kinh Các có một tấm bia đá, khắc mười cái tên. "
            "Chữ ở trên cùng đã mòn gần hết — không phải vì thời gian, mà vì quá nhiều bàn tay từng sờ lên đó."
        )
        for i, cg in enumerate(BANG_CANH_GIOI):
            kq.them(f"**{i + 1}. {cg.ten}** — {cg.than_the.capitalize()}. {cg.the_gioi.capitalize()}.")
        kq.them(
            "Dưới cùng tấm bia, có kẻ nào đó khắc thêm một dòng bằng dao găm, chữ nguệch ngoạc: "
            "*“Ta đã đi tới bậc thứ tư. Không đáng.”*"
        )
        await giaodien.gui(ctx, kq)

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
