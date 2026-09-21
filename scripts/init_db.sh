#!/usr/bin/env bash
# 开发环境：初始化 SQLite 数据库（非生产部署请用 scripts/install.sh）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="${ROOT}/backend"

cd "${BACKEND}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "已创建 backend/.env"
fi

python -c "from app.seed import init_db; init_db(); print('Database initialized.')"

echo "开发环境可运行: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
