"""Dữ liệu trình bày của Mini App — đầy đủ chỉ số RPG, trang bị, khu vực săn quái và trấn yêu tháp."""

from ..canhgioi import ten_canh_gioi, tu_vi_can_thiet
from ..data import congthuc, kynang, monphai, vatpham, xuatthan
from ..he import bicanh, sanquai


def vat(vp, sl=0, cap_cuong_hoa=0):
    he_so_ch = 1.0 + 0.15 * cap_cuong_hoa
    return dict(
        ma=vp.ma,
        ten=vp.ten,
        loai=vp.loai,
        pham=vp.pham,
        mo_ta=vp.mo_ta,
        gia=vp.gia,
        so_luong=sl,
        slot=vp.slot_trang_bi,
        cap=cap_cuong_hoa,
        cong=int(vp.chi_so_cong * he_so_ch),
        thu=int(vp.chi_so_thu * he_so_ch),
        hp=int(vp.chi_so_hp * he_so_ch),
        bao_kich=round(vp.chi_so_bao_kich * (1.0 + 0.1 * cap_cuong_hoa), 1),
        toc_do=int(vp.chi_so_toc_do * he_so_ch),
        hieu_qua=vp.hieu_qua,
        anh=f"/tranh/{vp.tranh}" if vp.tranh else f"/tranh/vatpham/{vp.loai}.svg",
    )


async def lay(kho, uid):
    ts = await kho.lay_tu_si(uid)
    tui = await kho.tui(uid) if ts else {}
    qua = bicanh.tien_do(ts)
    ais = []
    for i, b in enumerate(bicanh.AI):
        ais.append(dict(
            ma=b.ma, ten=b.ten, hieu=b.hieu, mo_ta=b.mo_ta, so=i+1,
            canh_gioi=ten_canh_gioi(b.canh_gioi, b.tang),
            anh="/tranh/" + bicanh.ANH[i],
            trang_thai="da_qua" if i < qua else "mo" if i == qua and (ts is None or ts.canh_gioi >= b.canh_gioi) else "khoa",
            linh_thach=50 * (i + 1),
            thuong=vat(vatpham.lay(bicanh.THUONG[i]), 1)
        ))

    nv = None
    tb_map = {}
    ch_map = {}

    if ts:
        # Nhận tu vi treo máy tự động
        cong_tv, _ = ts.nhan_tu_vi_treo_may()
        if cong_tv > 0:
            await kho.luu(ts)

        mp = monphai.lay(ts.mon_phai)
        cs = ts.tinh_chi_so()
        tb_map = ts.lay_trang_bi()
        ch_map = ts.lay_cuong_hoa()

        # Dựng thông tin trang bị đang mặc
        trang_bi_info = {}
        for slot in ("vu_khi", "giap", "phap_bao", "ngoc_boi"):
            ma_item = tb_map.get(slot)
            if ma_item and vatpham.lay(ma_item):
                trang_bi_info[slot] = vat(vatpham.lay(ma_item), 1, ch_map.get(ma_item, 0))
            else:
                trang_bi_info[slot] = None

        nv = dict(
            ten=ts.ten,
            canh_gioi=ten_canh_gioi(ts.canh_gioi, ts.tang),
            canh_gioi_so=ts.canh_gioi,
            tang=ts.tang,
            tu_vi=ts.tu_vi,
            tu_vi_can=cs["tu_vi_can"],
            tu_vi_sec=cs["tu_vi_sec"],
            luc_chien=cs["luc_chien"],
            hp=cs["hp"],
            hp_max=cs["hp_max"],
            mp=cs["mp"],
            mp_max=cs["mp_max"],
            cong=cs["cong"],
            thu=cs["thu"],
            bao_kich=cs["bao_kich"],
            toc_do=cs["toc_do"],
            can_cot=ts.can_cot,
            tu_chat=ts.tu_chat,
            dao_tam=ts.dao_tam,
            than_the=ts.than_the,
            linh_thach=ts.linh_thach,
            mon_phai=mp.ten if mp else "Tán tu",
            phap_bao=ts.phap_bao,
            trang_bi=trang_bi_info,
            thap_tang=ts.thap_tang(),
            so_tran_thang=ts.so_tran_thang,
            so_tran_thua=ts.so_tran_thua,
            dang_bi_thuong=ts.dang_bi_thuong,
            con_duong_thuong=ts.con_bao_lau_duong_thuong,
            da_chet=bool(ts.da_chet),
            da_qua=qua,
            ky_nang_da_hoc=ts.lay_ky_nang(),
            ky_nang_trang_bi=ts.lay_ky_nang_trang_bi(),
        )

    # Hệ thống Kỹ Năng & Công Pháp
    ky_nang_da_hoc = ts.lay_ky_nang() if ts else {}
    ky_nang_trang_bi = ts.lay_ky_nang_trang_bi() if ts else []

    ky_nang_list = []
    for kn in kynang.DANH_SACH_KY_NANG.values():
        da_hoc = kn.ma in ky_nang_da_hoc
        cap = ky_nang_da_hoc.get(kn.ma, 0)
        da_trang_bi = kn.ma in ky_nang_trang_bi
        slot_idx = ky_nang_trang_bi.index(kn.ma) if da_trang_bi else -1
        mult = round(kn.he_so_sat_thuong * (1.0 + 0.15 * max(0, cap - 1)), 2)
        st_cd = int(kn.sat_thuong_co_dinh * (1.0 + 0.2 * max(0, cap - 1)))
        gia_up_tv = int(kn.gia_tu_vi * (1.5 ** max(0, cap)))
        gia_up_lt = int(kn.gia_linh_thach * (1.5 ** max(0, cap)))
        ky_nang_list.append(dict(
            ma=kn.ma,
            ten=kn.ten,
            he=kn.he,
            icon=kn.icon,
            loai=kn.loai,
            canh_gioi=kn.canh_gioi,
            canh_gioi_ten=kn.canh_gioi_ten,
            mp=kn.mp,
            he_so_sat_thuong=mult,
            sat_thuong_co_dinh=st_cd,
            he_so_hoi_phuc=kn.he_so_hoi_phuc,
            he_so_la_chan=kn.he_so_la_chan,
            tang_bao_kich=kn.tang_bao_kich,
            hoi_chieu=kn.hoi_chieu,
            mo_ta=kn.mo_ta,
            da_hoc=da_hoc,
            cap=cap,
            da_trang_bi=da_trang_bi,
            slot=slot_idx,
            gia_hoc_tv=kn.gia_tu_vi,
            gia_hoc_lt=kn.gia_linh_thach,
            gia_up_tv=gia_up_tv,
            gia_up_lt=gia_up_lt,
            co_the_hoc=(ts is not None and ts.canh_gioi >= kn.canh_gioi and not da_hoc and ts.tu_vi >= kn.gia_tu_vi and ts.linh_thach >= kn.gia_linh_thach),
            co_the_up=(ts is not None and da_hoc and ts.tu_vi >= gia_up_tv and ts.linh_thach >= gia_up_lt),
        ))

    # Hệ thống Công thức Đan Phòng & Luyện Khí
    cong_thuc_list = []
    for ct in congthuc.DAN_PHUONG.values():
        nl_info = []
        du_nguyen_lieu = True
        for m_nl, sl_can in ct.nguyen_lieu.items():
            vp_nl = vatpham.lay(m_nl)
            co = tui.get(m_nl, 0)
            if co < sl_can:
                du_nguyen_lieu = False
            nl_info.append(dict(
                ma=m_nl,
                ten=vp_nl.ten if vp_nl else m_nl,
                can=sl_can,
                co=co,
                du=co >= sl_can,
            ))
        vp_tp = vatpham.lay(ct.thanh_pham)
        cong_thuc_list.append(dict(
            ma=ct.ma,
            ten=ct.ten,
            loai="dan",
            nguyen_lieu=nl_info,
            thanh_pham=dict(
                ma=ct.thanh_pham,
                ten=vp_tp.ten if vp_tp else ct.thanh_pham,
                pham=vp_tp.pham if vp_tp else 1,
                loai=vp_tp.loai if vp_tp else "dan_duoc",
                anh=f"/tranh/{vp_tp.tranh}" if vp_tp and vp_tp.tranh else "/tranh/vatpham/dan_duoc.svg",
            ),
            canh_gioi_toi_thieu=ct.canh_gioi_toi_thieu,
            mo_ta=ct.mo_ta,
            du_nguyen_lieu=du_nguyen_lieu,
            co_the_luyen=(ts is not None and ts.canh_gioi >= ct.canh_gioi_toi_thieu and du_nguyen_lieu),
        ))

    for ct in congthuc.KHI_PHUONG.values():
        nl_info = []
        du_nguyen_lieu = True
        for m_nl, sl_can in ct.nguyen_lieu.items():
            vp_nl = vatpham.lay(m_nl)
            co = tui.get(m_nl, 0)
            if co < sl_can:
                du_nguyen_lieu = False
            nl_info.append(dict(
                ma=m_nl,
                ten=vp_nl.ten if vp_nl else m_nl,
                can=sl_can,
                co=co,
                du=co >= sl_can,
            ))
        vp_tp = vatpham.lay(ct.thanh_pham)
        cong_thuc_list.append(dict(
            ma=ct.ma,
            ten=ct.ten,
            loai="khi",
            nguyen_lieu=nl_info,
            thanh_pham=dict(
                ma=ct.thanh_pham,
                ten=vp_tp.ten if vp_tp else ct.thanh_pham,
                pham=vp_tp.pham if vp_tp else 1,
                loai=vp_tp.loai if vp_tp else "phap_bao",
                anh=f"/tranh/{vp_tp.tranh}" if vp_tp and vp_tp.tranh else "/tranh/vatpham/phap_bao.svg",
            ),
            canh_gioi_toi_thieu=ct.canh_gioi_toi_thieu,
            mo_ta=ct.mo_ta,
            du_nguyen_lieu=du_nguyen_lieu,
            co_the_luyen=(ts is not None and ts.canh_gioi >= ct.canh_gioi_toi_thieu and du_nguyen_lieu),
        ))

    # Khu vực săn quái
    khu_vuc_san = []
    for ma_kv, info in sanquai.KHU_VUC.items():
        quai_list = []
        for mq in info["quai"]:
            q = sanquai.DANH_SACH_QUAI.get(mq)
            if q:
                quai_list.append(dict(
                    ma=q.ma, ten=q.ten, hp=q.hp, cong=q.cong, thu=q.thu,
                    bao_kich=q.bao_kich, toc_do=q.toc_do, exp=q.exp,
                    linh_thach=q.linh_thach, mo_ta=q.mo_ta,
                    canh_gioi=ten_canh_gioi(q.canh_gioi, q.tang),
                    roi_do=[vatpham.ten(m) for m, _ in q.roi_do if vatpham.lay(m)]
                ))
        khu_vuc_san.append(dict(
            ma=ma_kv,
            ten=info["ten"],
            canh_gioi_yeu_cau=info["canh_gioi_yeu_cau"],
            canh_gioi_ten=info["canh_gioi_ten"],
            mo_ta=info["mo_ta"],
            mo=(ts is None or ts.canh_gioi >= info["canh_gioi_yeu_cau"]),
            quai=quai_list,
        ))

    # Trấn Yêu Tháp
    thap_hien_tai = ts.thap_tang() if ts else 1
    q_thap = sanquai.quai_thap(thap_hien_tai)
    tran_thap_info = dict(
        tang=thap_hien_tai,
        ten=q_thap.ten,
        hp=q_thap.hp,
        cong=q_thap.cong,
        thu=q_thap.thu,
        exp=q_thap.exp * 2,
        linh_thach=q_thap.linh_thach * 2,
        mo_ta=q_thap.mo_ta,
        roi_do=[vatpham.ten(m) for m, _ in q_thap.roi_do if vatpham.lay(m)],
    )

    tui_list = [
        vat(vatpham.lay(m), n, ch_map.get(m, 0))
        for m, n in tui.items() if vatpham.lay(m)
    ]

    return dict(
        nhan_vat=nv,
        tui=tui_list,
        vat_pham=[vat(v) for v in vatpham.DANH_MUC.values()],
        ai=ais,
        khu_vuc_san=khu_vuc_san,
        tran_thap=tran_thap_info,
        ky_nang=ky_nang_list,
        cong_thuc=cong_thuc_list,
        xuat_than=[dict(ma=x.ma, ten=x.ten, mo_ta=x.mo_ta, linh_can=x.linh_can)
                   for x in xuatthan.DANH_SACH.values()],
        cho={k: await kho.con_cho(uid, k) if ts else 0
             for k in ("luyentap", "khampha", "bicanh")},
    )
