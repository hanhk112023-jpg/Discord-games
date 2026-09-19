"""Dữ liệu trình bày của Mini App. Không nhận chỉ số hay phần thưởng từ client."""
from ..canhgioi import ten_canh_gioi, tu_vi_can_thiet
from ..data import vatpham, xuatthan, monphai
from ..he import bicanh


def vat(vp, sl=0):
    return dict(ma=vp.ma, ten=vp.ten, loai=vp.loai, pham=vp.pham, mo_ta=vp.mo_ta,
                gia=vp.gia, so_luong=sl,
                anh=f"/tranh/{vp.tranh}" if vp.tranh else f"/tranh/vatpham/{vp.loai}.svg")


async def lay(kho, uid):
    ts = await kho.lay_tu_si(uid)
    tui = await kho.tui(uid) if ts else {}
    qua = bicanh.tien_do(ts)
    ais = []
    for i, b in enumerate(bicanh.AI):
        ais.append(dict(ma=b.ma, ten=b.ten, hieu=b.hieu, mo_ta=b.mo_ta, so=i+1,
                        canh_gioi=ten_canh_gioi(b.canh_gioi, b.tang),
                        anh="/tranh/" + bicanh.ANH[i],
                        trang_thai="da_qua" if i < qua else "mo" if i == qua and (ts is None or ts.canh_gioi >= b.canh_gioi) else "khoa",
                        linh_thach=50*(i+1), thuong=vat(vatpham.lay(bicanh.THUONG[i]), 1)))
    nv = None
    if ts:
        mp = monphai.lay(ts.mon_phai)
        nv = dict(ten=ts.ten, canh_gioi=ten_canh_gioi(ts.canh_gioi, ts.tang),
                  tu_vi=ts.tu_vi, tu_vi_can=tu_vi_can_thiet(ts.canh_gioi, ts.tang),
                  than_the=ts.than_the, dao_tam=ts.dao_tam, linh_thach=ts.linh_thach,
                  mon_phai=mp.ten if mp else "Tán tu", phap_bao=ts.phap_bao,
                  da_chet=bool(ts.da_chet), da_qua=qua)
    return dict(nhan_vat=nv, tui=[vat(vatpham.lay(m), n) for m, n in tui.items() if vatpham.lay(m)],
                vat_pham=[vat(v) for v in vatpham.DANH_MUC.values()], ai=ais,
                xuat_than=[dict(ma=x.ma, ten=x.ten, mo_ta=x.mo_ta, linh_can=x.linh_can)
                           for x in xuatthan.DANH_SACH.values()],
                cho={k: await kho.con_cho(uid, k) if ts else 0
                     for k in ("luyentap", "khampha", "bicanh")})
