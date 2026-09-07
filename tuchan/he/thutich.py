"""Thư tịch — mấy quyển sách trong Tàng Kinh Các mà ai cũng được mở.

Bia mười bậc, sổ chín cửa ải, Binh Khí Phổ, Đan Phổ, và một tờ giấy chép về
chín phẩm kim đan. Cùng một bộ chữ này được dùng cho cả bot Discord lẫn diễn rạp web.
"""

from __future__ import annotations

from .. import config
from ..canhgioi import (BANG_CANH_GIOI, KHAO_NGHIEM, MO_TA_DAN_PHAM,
                        TONG_SO_BAC, ten_dan_pham)
from ..data import vatpham as dl_vatpham
from .ketqua import KetQua

LOI_VU_KHI = {
    "kiem": "kiếm", "dao": "đao", "thuong": "thương", "phi_kiem": "phi kiếm",
    "cung": "cung", "ti": "ti tuyến", "chuy": "chuỳ", "phu": "phù lục",
    "giap": "hộ giáp", "chuong": "pháp chung", "an": "ấn", "phuong": "phướn",
    "but": "bút", "quat": "quạt", "dinh": "đan đỉnh", "kinh": "bảo kính",
    "dai": "trảm đài",
}


def bia_muoi_bac() -> KetQua:
    kq = KetQua(tieu_de="Bia đá mười bậc", anh="bia_tien_do.png")
    kq.them(
        "Trong Tàng Kinh Các có một tấm bia đá, khắc mười cái tên. "
        "Chữ ở trên cùng đã mòn gần hết — không phải vì thời gian, mà vì quá nhiều bàn tay từng sờ lên đó."
    )
    for i, cg in enumerate(BANG_CANH_GIOI):
        dong = (f"**{i + 1}. {cg.ten}** — chia làm {cg.so_tang} bậc nhỏ, "
                f"từ *{cg.ten_tang[0]}* tới *{cg.ten_tang[-1]}*.\n"
                f"{cg.than_the.capitalize()}. {cg.the_gioi.capitalize()}.")
        kn = KHAO_NGHIEM.get(i)
        if kn:
            dong += f"\n*Cửa vào bậc này là **{kn.ten}**.*"
        kq.them(dong)
    kq.them(
        f"Cộng lại, từ lúc dẫn khí nhập thể tới lúc tên ngươi thành một thời đại, tất cả có "
        f"**{TONG_SO_BAC} bậc**. Người ta hay quên điều đó, vì phần lớn dừng lại trong mười bậc đầu."
    )
    kq.them(
        "Dưới cùng tấm bia, có kẻ nào đó khắc thêm một dòng bằng dao găm, chữ nguệch ngoạc: "
        "*“Ta đã đi tới bậc thứ tư. Không đáng.”*"
    )
    return kq


def chin_cua_ai() -> KetQua:
    kq = KetQua(tieu_de="Chín cửa ải", mau=config.MAU_HUYET, anh="do_kiep.png")
    kq.them(
        "Có một quyển sách mỏng trong Tàng Kinh Các mà đám đệ tử mới không được phép mượn. "
        "Nó không dạy công pháp. Nó chỉ chép lại chín cửa ải, và chép rất lạnh lùng, "
        "như người ta chép sổ tang."
    )
    for chi_so in sorted(KHAO_NGHIEM):
        kn = KHAO_NGHIEM[chi_so]
        cg = BANG_CANH_GIOI[chi_so]
        kq.them(f"**{kn.ten}** — trước cửa {cg.ten}.\n{kn.mo_ta}"
                + (f"\n*{kn.can_dan}*" if kn.can_dan else ""))
    kq.them(
        "Trang cuối chỉ có một câu, viết bằng thứ mực đã ngả nâu: "
        "*“Kiếp nạn không phải hình phạt. Nó là câu hỏi. Trời hỏi ngươi có thật lòng muốn đi tiếp không — "
        "và trời không nhận câu trả lời bằng lời.”*"
    )
    return kq


def binh_khi_pho(nguong_pham: int = 1) -> KetQua:
    nguong = max(1, min(9, nguong_pham))
    kq = KetQua(tieu_de="Binh Khí Phổ", mau=config.MAU_KIM, anh="binh_khi_pho.png")
    kq.them(
        "Ở Lạc Hà Thành có một lão thợ rèn cụt tay trái, cả đời chỉ làm một việc: "
        "chép lại tên những món khí giới mà lão từng nghe nói tới. "
        "Lão bảo: *“Ta không rèn được chúng. Nhưng ta muốn có người nhớ.”*"
    )
    bo = [v for v in dl_vatpham.theo_loai("phap_bao") if v.pham >= nguong]
    bo.sort(key=lambda v: (v.pham, v.ten))
    for v in bo:
        loai = LOI_VU_KHI.get(v.loai_vu_khi, "khí giới")
        dong = f"**{v.ten}** · {loai} · phẩm thứ {v.pham}\n{v.mo_ta}"
        if v.ghi_chu:
            dong += f"\n*{v.ghi_chu}*"
        if v.tranh:
            dong += "\n*(Trong phổ có kèm một bức vẽ món này — xem bằng lệnh vật phẩm.)*"
        kq.them(dong)
    kq.them(
        "*“Phẩm càng cao thì càng khó thuần,”* lão nói, gõ búa xuống đe một cái. "
        "*“Cầm món không hợp tay thì nó không giết địch — nó giết ngươi, chậm thôi, nhưng chắc.”*"
    )
    return kq


def _cong_dung(vp) -> list[str]:
    hq, cong = vp.hieu_qua, []
    if "dot_pha" in hq:
        cong.append("phá quan")
    if "dot_pha_tang" in hq:
        cong.append("phá chướng")
    if "ho_kiep" in hq:
        cong.append("hộ thể độ kiếp")
    if "tri_thuong" in hq:
        cong.append("chữa thương")
    if "tu_vi" in hq:
        cong.append("tăng đạo hạnh")
    if hq.get("dao_tam", 0) > 0:
        cong.append("tĩnh tâm")
    if "tho_nguyen" in hq:
        cong.append("kéo thọ")
    if "an_tuc" in hq:
        cong.append("giấu khí tức")
    if "can_cot" in hq:
        cong.append("luyện thể")
    if hq.get("sat_nghiep", 0) > 0:
        cong.append("**tổn đức**")
    return cong


def dan_pho() -> KetQua:
    kq = KetQua(tieu_de="Đan Phổ", mau=config.MAU_LINH, anh="dan_pho.png")
    kq.them(
        "Đan Phổ không phải sách quý. Nó là một xấp giấy dày, mép đã quăn, treo bằng dây gai "
        "trong mọi hiệu thuốc từ Lạc Hà tới Vọng Hải. Ai cũng đọc được. "
        "Chỉ có điều đọc xong rồi mới biết: biết tên đan là chuyện dễ nhất trong toàn bộ câu chuyện."
    )
    for v in sorted(dl_vatpham.theo_loai("dan_duoc"), key=lambda v: (v.pham, v.ten)):
        cong = _cong_dung(v)
        kq.them(f"**{v.ten}** · phẩm thứ {v.pham}" + (f" · {', '.join(cong)}" if cong else "")
                + f"\n{v.mo_ta}")
    kq.them(
        "Ở góc dưới cùng tờ giấy, có người viết thêm bằng bút chì: "
        "*“Đan chỉ mở cửa. Bước qua cửa vẫn là chuyện của chính ngươi.”*"
    )
    return kq


def kim_dan_pho() -> KetQua:
    kq = KetQua(tieu_de="Chín phẩm kim đan", mau=config.MAU_KIM, anh="kim_dan.png")
    kq.them(
        "Kết đan chỉ có một lần trong đời. Viên đan ngưng ra hôm ấy tròn hay méo, trong hay đục, "
        "sẽ theo ngươi tới tận lúc nhắm mắt — và không có đan dược, cơ duyên hay sư phụ nào sửa lại được."
    )
    for pham in range(1, 10):
        kq.them(f"**Phẩm thứ {pham} — {ten_dan_pham(pham)}.** {MO_TA_DAN_PHAM[pham]}")
    kq.them(
        "Vì thế mới có câu: *“Trúc cơ xem tư chất, kết đan xem tâm tính, sau kết đan thì xem số.”* "
        "Kẻ ôm một viên đan hạ phẩm mà vẫn lên tới Nguyên Anh — kẻ ấy đáng sợ hơn nhiều "
        "so với kẻ sinh ra đã có thượng phẩm."
    )
    return kq
