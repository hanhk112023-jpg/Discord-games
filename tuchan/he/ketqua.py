"""Kết quả của một hành động: một đoạn chuyện, đôi khi kèm một bức tranh."""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import config


@dataclass
class KetQua:
    tieu_de: str = ""
    van: list[str] = field(default_factory=list)
    anh: str | None = None  # tên tệp trong assets/tranh
    thanh_anh: str | None = None  # tên tệp trong assets/thanh_anh
    mau: int = config.MAU_MUC
    chu_thich: str | None = None
    thanh_cong: bool = True
    du_lieu: dict = field(default_factory=dict)

    def them(self, *doan: str) -> "KetQua":
        for d in doan:
            if d and d.strip():
                self.van.append(d.strip())
        return self

    @property
    def toan_van(self) -> str:
        return "\n\n".join(self.van)
