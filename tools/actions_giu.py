#!/usr/bin/env python3
"""Trạng thái của cửa động giữa những lần máy chủ GitHub Actions thức giấc.

Runner của Actions là nhà trọ: ra khỏi cổng là mất hết đồ. Cái sổ sinh tử thì
không được phép ở nhờ đó — `luu` chép nó lên nhánh `du-tru` (an toàn, dùng API
online-backup của sqlite nên chẳng ever sợ ghi dở), `lay` kéo nó về trước khi mở cửa.

Chạy trong workflow, cần `gh` đã đăng ký GITHUB_TOKEN:

    python tools/actions_giu.py lay
    python tools/actions_giu.py luu
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
NHANH = "du-tru"
DUONG_DB = os.getenv("DB_PATH", str(GOC / "data" / "tienlo.sqlite3"))
FILE_TRONG_NHANH = "tienlo.sqlite3"


def _repo() -> str:
    o, r = os.environ["GITHUB_REPOSITORY"].split("/")
    return f"{o}/{r}"


def _sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=GOC, capture_output=True,
                          text=True, check=True).stdout.strip()


def _api(*ls: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", "api", *ls], capture_output=True, text=True)


def luu() -> int:
    Path(DUONG_DB).parent.mkdir(parents=True, exist_ok=True)
    if not Path(DUONG_DB).exists():
        print("· chưa có sổ gì mà chốt — bỏ qua")
        return 0
    tam = Path(tempfile.mkstemp(suffix=".sqlite3")[1])
    nguon = sqlite3.connect(DUONG_DB)
    dich = sqlite3.connect(tam)
    with nguon, dich:
        nguon.backup(dich)
    nguon.close(); dich.close()
    du_lieu = base64.b64encode(tam.read_bytes()).decode()
    tam.unlink(missing_ok=True)
    repo = _repo()

    def ghi(co_sha: bool) -> subprocess.CompletedProcess:
        than = {"message": "chốt sổ giữa canh", "branch": NHANH, "content": du_lieu}
        if co_sha:
            than["sha"] = _sha()
        return subprocess.run(["gh", "api", "-X", "PUT",
                               f"repos/{repo}/contents/{FILE_TRONG_NHANH}", "--input", "-"],
                              input=json.dumps(than), capture_output=True, text=True)

    r = ghi(True)
    if r.returncode != 0:
        r = ghi(False)  # nhánh hoặc tệp chưa tồn tại — tạo mới
    if r.returncode != 0:
        print("⚠ không chốt được sổ:", r.stderr[:300], file=sys.stderr)
        return 1
    print(f"✔ đã chốt sổ lên `{NHANH}` ({len(du_lieu) * 3 // 4 // 1024} KB)")
    return 0


def lay() -> int:
    repo = _repo()
    r = _api(f"repos/{repo}/contents/{FILE_TRONG_NHANH}?ref={NHANH}")
    if r.returncode != 0:
        print("· sổ mới tinh — chưa có gì để kéo về")
        return 0
    try:
        noi_dung = base64.b64decode(json.loads(r.stdout)["content"])
    except Exception as e:
        print("⚠ sổ trên nhánh đọc không nổi:", e, file=sys.stderr)
        return 1
    # kiểm là sqlite thật rồi mới đè
    Path(DUONG_DB).parent.mkdir(parents=True, exist_ok=True)
    tam = Path(tempfile.mkstemp(suffix=".sqlite3")[1])
    tam.write_bytes(noi_dung)
    try:
        c = sqlite3.connect(tam)
        c.execute("SELECT count(*) FROM tu_si").fetchone()
        c.close()
    except Exception as e:
        print("⚠ sổ kéo về hỏng, bỏ: ", e, file=sys.stderr)
        tam.unlink(missing_ok=True)
        return 1
    shutil.move(str(tam), DUONG_DB)
    for duoi in ("-wal", "-shm"):
        p = Path(DUONG_DB + duoi)
        if p.exists():
            p.unlink()
    print(f"✔ đã kéo sổ về từ `{NHANH}`")
    return 0


if __name__ == "__main__":
    lenh = sys.argv[1] if len(sys.argv) > 1 else "lay"
    raise SystemExit(luu() if lenh == "luu" else lay())
