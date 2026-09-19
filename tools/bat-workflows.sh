#!/usr/bin/env bash
# Gài bản trực 24/7 lên GitHub: chép workflow vào đúng chỗ rồi commit.
# (Token của một số công cụ bị chặn ghi vào .github/workflows — chạy tay một lần là xong.)
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .github/workflows
cp tools/workflows/live-mini.yml .github/workflows/live-mini.yml
git add .github/workflows/live-mini.yml
git -c user.name="${GIT_AUTHOR_NAME:-arena}" -c user.email="${GIT_AUTHOR_EMAIL:-arena@local}" \
    commit -m "Sống 24/7: nạp workflow trực cửa động Mini App" || true
echo "Đã nạp — giờ lên Actions → 'Sống · cửa động 24/7' → Run workflow (chế độ 'thu' để thử máy)."
