"""Dựng thanh ảnh (đoạn phim ngắn) cho những khoảnh khắc lớn trong game.

Ghép tranh thuỷ mặc (chuyển động Ken Burns) + lời kể + gió + tiếng ngân trầm,
xuất ra mp4 để bot đính kèm vào lúc nhập đạo / đột phá.

    python tools/lam_thanh_anh.py            # dựng tất cả
    python tools/lam_thanh_anh.py nhap_dao   # dựng riêng một cảnh
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

GOC = Path(__file__).resolve().parent.parent
TRANH = GOC / "assets" / "tranh"
AM = GOC / "assets" / "am"
RA = GOC / "assets" / "thanh_anh"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H, FPS = 960, 540, 24
CRF = "30"   # giữ tệp dưới 10 MB để Discord chịu nhận
CHUYEN = 1.1  # thời lượng hoà hình giữa hai cảnh (giây)

# Mỗi tác phẩm: tên tệp ra, danh sách tranh, tệp lời kể
TAC_PHAM = {
    "nhap_dao": {
        "tranh": ["bia_tien_do.png", "thanh_van_mon.png", "luyen_khi.png", "hac_phong_lam.png"],
        "am": "nhap_dao.mp3",
        "duoi": 2.4,
    },
    "dot_pha": {
        "tranh": ["ket_dan.png", "do_kiep.png"],
        "am": "dot_pha.mp3",
        "duoi": 2.2,
    },
    "giang_ho": {
        "tranh": ["dau_phap.png", "dan_phong.png", "bia_tien_do.png"],
        "am": "loi_lao_ban_tra.mp3",
        "duoi": 2.0,
    },
}


def do_dai_am(tep: Path) -> float:
    ra = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(tep), "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    tong = 0.0
    for dong in ra.splitlines():
        if "time=" in dong:
            phan = dong.split("time=")[-1].split(" ")[0]
            try:
                h, m, s = phan.split(":")
                tong = max(tong, int(h) * 3600 + int(m) * 60 + float(s))
            except ValueError:
                pass
    return tong or 20.0


def dung(ten: str, cau_hinh: dict) -> Path:
    anh = [TRANH / t for t in cau_hinh["tranh"]]
    for a in anh:
        if not a.exists():
            raise SystemExit(f"Thiếu tranh: {a}")
    tep_am = AM / cau_hinh["am"]
    co_am = tep_am.exists()
    dai_am = do_dai_am(tep_am) if co_am else 24.0
    tong = dai_am + cau_hinh.get("duoi", 2.0)

    n = len(anh)
    # tổng = sum(d_i) - (n-1)*CHUYEN  →  d_i bằng nhau
    d = (tong + (n - 1) * CHUYEN) / n
    d = max(d, CHUYEN + 1.5)

    khung = int(d * FPS)
    dau_vao: list[str] = []
    for a in anh:
        dau_vao += ["-loop", "1", "-t", f"{d:.3f}", "-i", str(a)]
    if co_am:
        dau_vao += ["-i", str(tep_am)]

    loc: list[str] = []
    for i in range(n):
        # xen kẽ: cảnh chẵn phóng vào, cảnh lẻ lùi ra + trôi ngang
        if i % 2 == 0:
            z = f"min(zoom+0.00035,1.18)"
            x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        else:
            z = f"if(lte(zoom,1.0),1.18,max(1.001,zoom-0.00035))"
            x, y = "iw/2-(iw/zoom/2)+(on/{0})*90-45".format(khung), "ih/2-(ih/zoom/2)"
        loc.append(
            f"[{i}:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
            f"crop={W*2}:{H*2},setsar=1,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={khung}:s={W}x{H}:fps={FPS},"
            f"format=yuv420p[v{i}]"
        )

    truoc = "[v0]"
    moc = 0.0
    for i in range(1, n):
        moc += d - CHUYEN
        nhan = f"[x{i}]"
        loc.append(f"{truoc}[v{i}]xfade=transition=fade:duration={CHUYEN}:offset={moc:.3f}{nhan}")
        truoc = nhan

    loc.append(
        f"{truoc}eq=saturation=0.82:contrast=1.07:brightness=-0.02,"
        f"vignette=PI/4.2,noise=alls=4:allf=t,"
        f"fade=t=in:st=0:d=1.2,fade=t=out:st={max(0.1, tong-1.6):.2f}:d=1.6[vout]"
    )

    if co_am:
        # lời kể + gió (nhiễu lọc trầm) + một tiếng ngân rất thấp
        loc.append(
            f"[{n}:a]volume=1.0,afade=t=in:st=0:d=0.6,"
            f"afade=t=out:st={max(0.1, dai_am-0.8):.2f}:d=1.0[loi]"
        )
        loc.append(
            f"anoisesrc=color=brown:amplitude=0.35:duration={tong:.2f}:sample_rate=44100,"
            f"lowpass=f=320,volume=0.10,afade=t=in:st=0:d=2.5,"
            f"afade=t=out:st={max(0.1, tong-2.0):.2f}:d=2.0[gio]"
        )
        loc.append(
            f"sine=frequency=58:duration={tong:.2f}:sample_rate=44100,volume=0.05,"
            f"tremolo=f=0.4:d=0.6,afade=t=in:st=0:d=3,"
            f"afade=t=out:st={max(0.1, tong-2.5):.2f}:d=2.5[ngan]"
        )
        loc.append("[loi][gio][ngan]amix=inputs=3:duration=first:dropout_transition=3,"
                   "alimiter=limit=0.95[aout]")

    lenh = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *dau_vao,
            "-filter_complex", ";".join(loc),
            "-map", "[vout]"]
    if co_am:
        lenh += ["-map", "[aout]", "-c:a", "aac", "-b:a", "112k"]
    RA.mkdir(parents=True, exist_ok=True)
    ra = RA / f"{ten}.mp4"
    lenh += ["-c:v", "libx264", "-preset", "slow", "-crf", CRF,
             "-pix_fmt", "yuv420p", "-movflags", "+faststart",
             "-t", f"{tong:.2f}", str(ra)]

    print(f"→ dựng {ten}: {n} cảnh, {tong:.1f} giây")
    kq = subprocess.run(lenh, capture_output=True, text=True)
    if kq.returncode != 0:
        print(kq.stderr[-3000:])
        raise SystemExit(f"ffmpeg hỏng khi dựng {ten}")
    print(f"  ✓ {ra.relative_to(GOC)}  ({ra.stat().st_size/1_048_576:.1f} MB)")
    return ra


def main() -> None:
    ten_can = sys.argv[1:] or list(TAC_PHAM)
    for ten in ten_can:
        if ten not in TAC_PHAM:
            print(f"Không có tác phẩm tên {ten}")
            continue
        dung(ten, TAC_PHAM[ten])


if __name__ == "__main__":
    main()
