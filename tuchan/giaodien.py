"""Giao diện: đổi một KetQua thành thứ Discord hiển thị được.

Cố ý giữ cho mọi thứ giống một trang sách hơn là một bảng điều khiển:
không thanh máu, không con số, không nút bấm loè loẹt.
"""

from __future__ import annotations

from pathlib import Path

import discord

from . import config
from .he.ketqua import KetQua

GIOI_HAN = 3900


def tach_van(van: str, gioi_han: int = GIOI_HAN) -> list[str]:
    """Cắt một đoạn văn dài thành nhiều trang, cắt ở chỗ xuống dòng cho đẹp."""
    if len(van) <= gioi_han:
        return [van]
    trang: list[str] = []
    con = van
    while len(con) > gioi_han:
        cat = con.rfind("\n\n", 0, gioi_han)
        if cat < gioi_han // 2:
            cat = con.rfind("\n", 0, gioi_han)
        if cat < gioi_han // 2:
            cat = con.rfind(" ", 0, gioi_han)
        if cat <= 0:
            cat = gioi_han
        trang.append(con[:cat].strip())
        con = con[cat:].strip()
    if con:
        trang.append(con)
    return trang


def duong_dan_anh(ten: str | None) -> Path | None:
    if not ten:
        return None
    p = config.DUONG_DAN_TRANH / ten
    return p if p.exists() else None


def duong_dan_thanh_anh(ten: str | None) -> Path | None:
    if not ten:
        return None
    p = config.DUONG_DAN_THANH_ANH / ten
    return p if p.exists() else None


def dung_embed(kq: KetQua, tac_gia: str | None = None) -> tuple[list[discord.Embed], list[discord.File]]:
    trang = tach_van(kq.toan_van)
    embeds: list[discord.Embed] = []
    files: list[discord.File] = []

    for i, t in enumerate(trang):
        e = discord.Embed(
            title=(f"❖ {kq.tieu_de}" if i == 0 and kq.tieu_de else None),
            description=t,
            colour=kq.mau,
        )
        if i == len(trang) - 1 and kq.chu_thich:
            e.set_footer(text=kq.chu_thich)
        embeds.append(e)

    anh = duong_dan_anh(kq.anh)
    if anh is not None:
        f = discord.File(str(anh), filename=anh.name)
        files.append(f)
        embeds[0].set_image(url=f"attachment://{anh.name}")

    if tac_gia:
        embeds[0].set_author(name=tac_gia)

    clip = duong_dan_thanh_anh(kq.thanh_anh)
    if clip is not None:
        files.append(discord.File(str(clip), filename=clip.name))

    return embeds, files


async def gui(dich, kq: KetQua, tac_gia: str | None = None, ephemeral: bool = False):
    """Gửi kết quả tới một Context / Interaction response."""
    embeds, files = dung_embed(kq, tac_gia)
    dau = embeds[0]
    con_lai = embeds[1:]

    if isinstance(dich, discord.Interaction):
        if dich.response.is_done():
            msg = await dich.followup.send(embed=dau, files=files, ephemeral=ephemeral)
        else:
            await dich.response.send_message(embed=dau, files=files, ephemeral=ephemeral)
            msg = await dich.original_response()
        for e in con_lai:
            await dich.followup.send(embed=e, ephemeral=ephemeral)
        return msg

    msg = await dich.send(embed=dau, files=files)
    for e in con_lai:
        await dich.send(embed=e)
    return msg
