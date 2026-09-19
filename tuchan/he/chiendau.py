"""Giao đấu — hệ thống chiến đấu chỉ số trực quan, hành động từng hiệp, sát thương & bạo kích."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..canhgioi import (canh_gioi, he_so_dan_pham, suc_manh_nen,
                        ten_canh_gioi)
from ..data import vatpham


@dataclass
class BenThamChien:
    ten: str
    canh_gioi: int
    tang: int
    xung: str = "hắn"
    phap_bao: str = ""
    he_so_chien: float = 1.0
    can_cot: float = 1.0
    dao_tam: int = 60
    than_the: int = 100
    thu_doan: tuple[str, ...] = ()
    la_nguoi_choi: bool = False
    hung_hang: float = 1.0
    cong_phap: str = ""
    dan_pham: int = 0
    hp: int = 0
    hp_max: int = 0
    mp: int = 0
    mp_max: int = 0
    cong: int = 0
    thu: int = 0
    bao_kich: float = 5.0
    toc_do: int = 50
    ky_nang: list[str] = field(default_factory=list)

    def __post_init__(self):
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        cong_vp = vp.chi_so_cong if vp else 0
        thu_vp = vp.chi_so_thu if vp else 0
        hp_vp = vp.chi_so_hp if vp else 0
        bk_vp = vp.chi_so_bao_kich if vp else 0.0

        if self.hp_max <= 0:
            self.hp_max = int((250 + 120 * self.tang + 850 * (self.canh_gioi ** 1.8) + hp_vp) * self.he_so_chien)
        if self.hp <= 0:
            self.hp = int(self.hp_max * (max(1, min(100, self.than_the)) / 100.0))
        if self.mp_max <= 0:
            self.mp_max = int(60 + 25 * self.tang + 150 * (self.canh_gioi ** 1.6))
            self.mp = self.mp_max
        if self.cong <= 0:
            self.cong = int(((35 + 16 * self.tang + 140 * (self.canh_gioi ** 1.8)) * self.he_so_chien + cong_vp) * self.hung_hang)
        if self.thu <= 0:
            self.thu = int(((15 + 9 * self.tang + 70 * (self.canh_gioi ** 1.8)) * self.can_cot + thu_vp))
        if self.bao_kich <= 5.0:
            self.bao_kich = round(5.0 + min(25.0, (self.dao_tam - 50) * 0.2 + self.can_cot * 2.0) + bk_vp, 1)
        if self.toc_do <= 50:
            self.toc_do = int(50 + 10 * self.canh_gioi + self.tang * 3)

        if not self.ky_nang:
            if self.la_nguoi_choi:
                self.ky_nang = ["Phổ Thông Tấn Công", "Kiếm Khí Trảm", "Liệt Diễm Chưởng", "Kim Cương Hộ Thể"]
            else:
                self.ky_nang = list(self.thu_doan) if self.thu_doan else ["Phổ Thông Tấn Công", "Móng Vuốt Xé Rách"]

    @property
    def ten_phap_bao(self) -> str:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.ten if vp else ""

    @property
    def loai_vu_khi(self) -> str:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.loai_vu_khi if vp else ""

    @property
    def uy_luc_phap_bao(self) -> float:
        vp = vatpham.lay(self.phap_bao) if self.phap_bao else None
        return vp.uy_luc if vp else 0.0

    def suc_chien(self) -> float:
        s = suc_manh_nen(self.canh_gioi, self.tang)
        s *= 1.0 + self.uy_luc_phap_bao
        s *= self.he_so_chien
        s *= 0.75 + 0.25 * self.can_cot
        s *= 0.55 + 0.45 * max(0, min(100, self.than_the)) / 100.0
        s *= 0.88 + 0.24 * max(0, min(100, self.dao_tam)) / 100.0
        if self.canh_gioi >= 2 and self.dan_pham:
            s *= he_so_dan_pham(self.dan_pham)
        return max(0.01, s)


@dataclass
class TranDau:
    thang: BenThamChien
    thua: BenThamChien
    van: list[str] = field(default_factory=list)
    ap_dao: float = 0.5
    chi_mang: bool = False
    ton_thuong_ke_thua: int = 30
    so_hiep: int = 0
    hiep_dau: list[dict] = field(default_factory=list)
    exp_nhan: int = 0
    lt_nhan: int = 0
    vat_pham_roi: list[str] = field(default_factory=list)


KY_NANG_INFO: dict[str, dict] = {
    "Phổ Thông Tấn Công": {"mult": 1.0, "mp": 0, "mo_ta": "tung đòn tấn công cơ bản"},
    "Kiếm Khí Trảm": {"mult": 1.75, "mp": 20, "mo_ta": "chém ra kiếm khí xé gió"},
    "Liệt Diễm Chưởng": {"mult": 2.15, "mp": 35, "mo_ta": "vận chân hoả giáng chưởng thiêu đốt"},
    "Vạn Kiếm Quy Tông": {"mult": 2.6, "mp": 50, "mo_ta": "ngưng kiếm quang rền vang giáng xuống"},
    "Kim Cương Hộ Thể": {"mult": 0.85, "mp": 25, "mo_ta": "kích hoạt hộ thể kim quang"},
    "Móng Vuốt Xé Rách": {"mult": 1.35, "mp": 0, "mo_ta": "vung vuốt sắc xé rách"},
}


def _chon_chieu(b: BenThamChien, rng: random.Random) -> tuple[str, float]:
    kn = b.ky_nang or ["Phổ Thông Tấn Công"]
    if b.mp >= 50 and "Vạn Kiếm Quy Tông" in kn and rng.random() < 0.45:
        b.mp -= 50
        return "Vạn Kiếm Quy Tông", 2.6
    if b.mp >= 35 and "Liệt Diễm Chưởng" in kn and rng.random() < 0.55:
        b.mp -= 35
        return "Liệt Diễm Chưởng", 2.15
    if b.mp >= 20 and "Kiếm Khí Trảm" in kn and rng.random() < 0.65:
        b.mp -= 20
        return "Kiếm Khí Trảm", 1.75
    # Nếu có chiêu thủ đoạn của quái
    ds = [k for k in kn if k not in ("Vạn Kiếm Quy Tông", "Liệt Diễm Chưởng", "Kiếm Khí Trảm")]
    chieu = rng.choice(ds) if ds else "Phổ Thông Tấn Công"
    mult = KY_NANG_INFO.get(chieu, {}).get("mult", 1.25)
    return chieu, mult


def giao_dau(
    a: BenThamChien,
    b: BenThamChien,
    rng: random.Random | None = None,
    boi_canh: str = "",
    so_hiep: int | None = None,
) -> TranDau:
    rng = rng or random.Random()
    van: list[str] = []
    if boi_canh:
        van.append(boi_canh)

    van.append(f"⚔️ **Trận giao chiến bắt đầu: {a.ten} VS {b.ten}**")
    van.append(f"📊 {a.ten}: HP {a.hp}/{a.hp_max} | Công {a.cong} | Thủ {a.thu} ⚡ VS ⚡ {b.ten}: HP {b.hp}/{b.hp_max} | Công {b.cong} | Thủ {b.thu}")

    max_hiep = so_hiep or 12
    hiep_dau: list[dict] = []
    hiep = 0

    while hiep < max_hiep and a.hp > 0 and b.hp > 0:
        hiep += 1
        # Quyết định thứ tự xuất chiêu dựa trên tốc độ
        tien, hau = (a, b) if (a.toc_do + rng.randint(-5, 5)) >= (b.toc_do + rng.randint(-5, 5)) else (b, a)

        # Đòn đánh của người đi trước
        chieu_1, mult_1 = _chon_chieu(tien, rng)
        raw_1 = tien.cong * mult_1
        dmg_1 = max(12, int((raw_1 - hau.thu * 0.52) * rng.uniform(0.9, 1.15)))
        crit_1 = rng.random() < (tien.bao_kich / 100.0)
        if crit_1:
            dmg_1 = int(dmg_1 * 1.75)
        hau.hp = max(0, hau.hp - dmg_1)

        crit_str_1 = " 💥 (BẠO KÍCH!)" if crit_1 else ""
        van.append(f"⚡ [Hiệp {hiep}] **{tien.ten}** xuất chiêu 【{chieu_1}】{crit_str_1} gây **{dmg_1}** sát thương! ({hau.ten} HP: {hau.hp}/{hau.hp_max})")
        hiep_dau.append({
            "hiep": hiep, "nguoi_danh": tien.ten, "chieu": chieu_1,
            "sat_thuong": dmg_1, "bao_kich": crit_1, "hp_a": a.hp, "hp_b": b.hp
        })

        if hau.hp <= 0:
            break

        # Đòn phản công của người đi sau
        chieu_2, mult_2 = _chon_chieu(hau, rng)
        raw_2 = hau.cong * mult_2
        dmg_2 = max(12, int((raw_2 - tien.thu * 0.52) * rng.uniform(0.9, 1.15)))
        crit_2 = rng.random() < (hau.bao_kich / 100.0)
        if crit_2:
            dmg_2 = int(dmg_2 * 1.75)
        tien.hp = max(0, tien.hp - dmg_2)

        crit_str_2 = " 💥 (BẠO KÍCH!)" if crit_2 else ""
        van.append(f"🗡️ [Hiệp {hiep}] **{hau.ten}** phản kích 【{chieu_2}】{crit_str_2} gây **{dmg_2}** sát thương! ({tien.ten} HP: {tien.hp}/{tien.hp_max})")
        hiep_dau.append({
            "hiep": hiep, "nguoi_danh": hau.ten, "chieu": chieu_2,
            "sat_thuong": dmg_2, "bao_kich": crit_2, "hp_a": a.hp, "hp_b": b.hp
        })

    # Xác định người thắng
    if a.hp > 0 and b.hp <= 0:
        thang, thua = a, b
    elif b.hp > 0 and a.hp <= 0:
        thang, thua = b, a
    else:
        # Nếu hết hiệp, so sánh tỷ lệ máu còn lại
        ti_a = a.hp / max(1, a.hp_max)
        ti_b = b.hp / max(1, b.hp_max)
        thang, thua = (a, b) if ti_a >= ti_b else (b, a)

    ap_dao = min(1.0, max(0.5, 1.0 - (thua.hp / max(1, thua.hp_max)) * 0.5))

    if thang is a:
        van.append(f"🏆 **CHIẾN THẮNG!** {a.ten} đã xuất sắc đánh bại {b.ten} sau {hiep} hiệp quyết đấu!")
    else:
        van.append(f"💀 **THẤT BẠI!** {a.ten} đã kiệt sức trước đòn đánh dồn dập của {b.ten}!")

    ton_thuong = int(max(5, min(95, (1.0 - (a.hp / max(1, a.hp_max))) * 100)))

    return TranDau(
        thang=thang,
        thua=thua,
        van=van,
        ap_dao=ap_dao,
        chi_mang=thua.hp <= 0 and ap_dao > 0.85,
        ton_thuong_ke_thua=ton_thuong,
        so_hiep=hiep,
        hiep_dau=hiep_dau,
    )


def loi_binh(td: TranDau, nguoi_choi: BenThamChien) -> str:
    thang = td.thang is nguoi_choi
    if thang and td.ap_dao > 0.8:
        return f"🏆 Áp đảo toàn diện! Lực chiến của ngươi hoàn toàn đè bẹp đối thủ sau {td.so_hiep} hiệp."
    if thang:
        return f"⚔️ Thắng lợi vẻ vang! Trận đấu giằng co quyết liệt trong {td.so_hiep} hiệp."
    return f"🩸 Bại trận! Đối thủ có sức chiến đấu vượt trội, hãy tăng cường tu luyện và nâng cấp trang bị."
