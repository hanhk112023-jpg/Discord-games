"""Đan lô và lò rèn."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import giaodien
from ..bot import TuChanBot, lay_tu_si_hoac_bao
from ..data import congthuc as dl_congthuc
from ..data import vatpham
from ..he import luyenche as he_luyenche
from ..he.ketqua import KetQua


def _tim_cong_thuc(chuoi: str, loai: str) -> str | None:
    chuoi = (chuoi or "").strip().lower()
    kho = dl_congthuc.DAN_PHUONG if loai == "dan" else dl_congthuc.KHI_PHUONG
    for ma, ct in kho.items():
        if chuoi == ma or chuoi == ct.ten.lower():
            return ma
    for ma, ct in kho.items():
        if chuoi in ct.ten.lower() or chuoi in vatpham.ten(ct.thanh_pham).lower():
            return ma
    return None


class CogLuyenChe(commands.Cog, name="Luyện chế"):
    def __init__(self, bot: TuChanBot):
        self.bot = bot

    @commands.hybrid_command(name="sotay", aliases=["congthuc", "danphuong"],
                             description="Những đan phương và đồ hình ngươi thuộc nằm lòng.")
    async def sotay(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        biet = await self.bot.kho.so_tay(ts.user_id)
        kq = KetQua(tieu_de="Sổ tay trong đầu ngươi")
        if not biet:
            kq.them(
                "Ngươi nhắm mắt lục lại trí nhớ và chỉ thấy một khoảng trống. "
                "Chưa ai truyền cho ngươi thứ gì, và ngươi cũng chưa nhặt được thứ gì đáng nhớ."
            )
        else:
            dan = [dl_congthuc.lay(m) for m in biet if m in dl_congthuc.DAN_PHUONG]
            khi = [dl_congthuc.lay(m) for m in biet if m in dl_congthuc.KHI_PHUONG]
            if dan:
                kq.them("**Đan phương:**\n" + "\n".join(
                    f"• **{c.ten}** → {vatpham.ten(c.thanh_pham)} — cần: "
                    + ", ".join(f"{vatpham.ten(k)} ×{v}" for k, v in c.nguyen_lieu.items())
                    for c in dan))
            if khi:
                kq.them("**Đồ hình luyện khí:**\n" + "\n".join(
                    f"• **{c.ten}** → {vatpham.ten(c.thanh_pham)} — cần: "
                    + ", ".join(f"{vatpham.ten(k)} ×{v}" for k, v in c.nguyen_lieu.items())
                    for c in khi))
            kq.them(
                "Ngươi nhớ chúng không phải bằng chữ, mà bằng mùi khói, bằng tiếng lửa reo, "
                "bằng cả những lần hỏng."
            )
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="luyendan", description="Nhóm lửa, mở lò, và cầu trời cho mẻ này không thành than.")
    @app_commands.describe(danphuong="Tên đan phương muốn dùng")
    async def luyendan(self, ctx: commands.Context, *, danphuong: str):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        ma = _tim_cong_thuc(danphuong, "dan")
        if ma is None:
            await ctx.send("Không có đan phương nào tên như vậy trong thiên hạ mà ngươi biết tới.")
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_luyenche.luyen_dan(self.bot.kho, ts, ma, self.bot.rng, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @luyendan.autocomplete("danphuong")
    async def _ac_dan(self, interaction: discord.Interaction, current: str):
        biet = await self.bot.kho.so_tay(interaction.user.id)
        return [
            app_commands.Choice(name=dl_congthuc.lay(m).ten, value=dl_congthuc.lay(m).ten)
            for m in biet if m in dl_congthuc.DAN_PHUONG
            and current.lower() in dl_congthuc.lay(m).ten.lower()
        ][:25]

    @commands.hybrid_command(name="luyenkhi", aliases=["renkhi"],
                             description="Quai búa suốt đêm để mong một món pháp bảo chịu nhận chủ.")
    @app_commands.describe(dohinh="Tên đồ hình luyện khí")
    async def luyenkhi(self, ctx: commands.Context, *, dohinh: str):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        ma = _tim_cong_thuc(dohinh, "khi")
        if ma is None:
            await ctx.send("Bản vẽ ấy, ngươi chưa từng thấy qua.")
            return
        hs = await self.bot.he_so(ctx.guild.id if ctx.guild else 0)
        kq = await he_luyenche.luyen_khi(self.bot.kho, ts, ma, self.bot.rng, hs)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @luyenkhi.autocomplete("dohinh")
    async def _ac_khi(self, interaction: discord.Interaction, current: str):
        biet = await self.bot.kho.so_tay(interaction.user.id)
        return [
            app_commands.Choice(name=dl_congthuc.lay(m).ten, value=dl_congthuc.lay(m).ten)
            for m in biet if m in dl_congthuc.KHI_PHUONG
            and current.lower() in dl_congthuc.lay(m).ten.lower()
        ][:25]

    @commands.hybrid_command(name="deo", aliases=["trangbi", "nhanchu"],
                             description="Nhỏ một giọt tinh huyết, nhận một món pháp bảo làm của mình.")
    async def deo(self, ctx: commands.Context, *, phapbao: str):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        from ..he.giaothuong import tim_hang
        ma = tim_hang(phapbao)
        if ma is None:
            await ctx.send("Không có pháp bảo nào tên như thế.")
            return
        kq = await he_luyenche.deo_phap_bao(self.bot.kho, ts, ma)
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @deo.autocomplete("phapbao")
    async def _ac_bao(self, interaction: discord.Interaction, current: str):
        tui = await self.bot.kho.tui(interaction.user.id)
        ra = []
        for ma in tui:
            vp = vatpham.lay(ma)
            if vp and vp.loai == "phap_bao" and current.lower() in vp.ten.lower():
                ra.append(app_commands.Choice(name=vp.ten, value=vp.ten))
        return ra[:25]

    @commands.hybrid_command(name="tuido", aliases=["tui", "hanhtrang"],
                             description="Dốc túi càn khôn ra xem có gì.")
    async def tuido(self, ctx: commands.Context):
        ts = await lay_tu_si_hoac_bao(ctx, self.bot)
        if ts is None:
            return
        from ..vanphong import liet_ke_tui, mo_ta_linh_thach, mo_ta_phap_bao
        tui = await self.bot.kho.tui(ts.user_id)
        kq = KetQua(tieu_de="Túi càn khôn")
        if not tui:
            kq.them("Ngươi lộn ngược cái túi. Rơi ra một hạt bụi, và không có gì khác.")
        else:
            kq.them("Ngươi trải mọi thứ lên tấm vải thô, xếp theo thứ tự quen thuộc:")
            for loai, nhan in (("duoc_lieu", "Dược liệu"), ("vat_lieu", "Vật liệu"),
                               ("dan_duoc", "Đan dược"), ("phap_bao", "Pháp bảo"),
                               ("ky_vat", "Vật khác"), ("ngoc_gian", "Ngọc giản")):
                s = liet_ke_tui(tui, loai, toi_da=40)
                if s:
                    kq.them(f"**{nhan}:** {s}")
        kq.them(mo_ta_phap_bao(ts.phap_bao))
        kq.them(mo_ta_linh_thach(ts.linh_thach))
        await giaodien.gui(ctx, kq, tac_gia=ctx.author.display_name)

    @commands.hybrid_command(name="vatpham", description="Hỏi kỹ về một món đồ.")
    async def vatpham_(self, ctx: commands.Context, *, ten: str):
        from ..he.giaothuong import tim_hang
        ma = tim_hang(ten)
        if ma is None:
            await ctx.send("Chưa ai nghe nói tới món đó.")
            return
        vp = vatpham.lay(ma)
        kq = KetQua(tieu_de=vp.ten)
        kq.them(vp.mo_ta)
        loai = {"duoc_lieu": "một loại dược liệu", "vat_lieu": "vật liệu luyện khí",
                "dan_duoc": "một loại đan dược", "phap_bao": "pháp bảo",
                "ky_vat": "vật kỳ lạ", "ngoc_gian": "ngọc giản"}.get(vp.loai, "một món đồ")
        kq.them(f"Người trong nghề xếp nó vào hàng **{vp.pham} phẩm** — {loai}.")
        if vp.loai == "phap_bao" and vp.canh_gioi_toi_thieu:
            from ..canhgioi import canh_gioi
            kq.them(f"Kẻ dưới **{canh_gioi(vp.canh_gioi_toi_thieu).ten}** thì đừng mơ điều khiển nổi nó.")
        await giaodien.gui(ctx, kq)


async def setup(bot: TuChanBot):
    await bot.add_cog(CogLuyenChe(bot))
