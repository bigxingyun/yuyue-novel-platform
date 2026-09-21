#!/usr/bin/env bash
# 欲阅 · Ubuntu 一键环境安装
#
# 用法:
#   chmod +x scripts/install.sh
#   sudo bash scripts/install.sh [--with-seed] [--port 9080]
#
# 开放端口:
#   9080/tcp（默认，可通过 --port 修改）— 公网 IP:端口 直接访问前端 + API
#
# 安装路径:
#   项目根目录         — 当前仓库 clone 位置
#   /var/lib/yuyue     — SQLite 数据库与上传文件
#   /var/log/yuyue     — 运行日志
#   /etc/systemd/system/yuyue.service — systemd 服务

set -euo pipefail

# WinSCP / Windows 上传可能带 CRLF，Ubuntu 下 bash 会报错
_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if grep -q $'\r' "${_script_dir}/lib/common.sh" 2>/dev/null; then
  find "${_script_dir}" -name '*.sh' -exec sed -i 's/\r$//' {} +
fi

# shellcheck source=lib/common.sh
source "${_script_dir}/lib/common.sh"

WITH_SEED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-seed)
      WITH_SEED=1
      shift
      ;;
    --port)
      YUYUE_PORT="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '1,18p' "$0"
      exit 0
      ;;
    *)
      die "未知参数: $1（可用 --with-seed --port）"
      ;;
  esac
done

require_ubuntu

if [[ "${EUID}" -ne 0 ]]; then
  die "请使用 root 执行: sudo bash scripts/install.sh"
fi

log "项目根目录: ${YUYUE_ROOT}"
log "部署用户: ${YUYUE_DEPLOY_USER}"
log "服务端口: ${YUYUE_PORT}"

log "更新 apt 并安装系统依赖…"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
  python3 python3-venv python3-pip \
  curl openssl ca-certificates \
  ufw lsb-release

if ! command -v node >/dev/null 2>&1 || [[ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]]; then
  log "安装 Node.js 20 LTS…"
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi

log "Node $(node -v) · npm $(npm -v) · Python $(python3 --version)"

ensure_dirs

log "创建 Python 虚拟环境…"
if [[ ! -d "${YUYUE_VENV}" ]]; then
  sudo -u "${YUYUE_DEPLOY_USER}" python3 -m venv "${YUYUE_VENV}"
fi
sudo -u "${YUYUE_DEPLOY_USER}" "${YUYUE_VENV}/bin/pip" install -q --upgrade pip
sudo -u "${YUYUE_DEPLOY_USER}" "${YUYUE_VENV}/bin/pip" install -q -r "${YUYUE_BACKEND}/requirements.txt"

SERVER_IP="$(detect_primary_ip)"
PUBLIC_URL="http://${SERVER_IP}:${YUYUE_PORT}"

if [[ ! -f "${YUYUE_BACKEND}/.env" ]]; then
  log "生成 backend/.env …"
  SECRET_KEY="$(openssl rand -hex 32)"
  cat > "${YUYUE_BACKEND}/.env" <<EOF
ENVIRONMENT=production
SEED_ON_STARTUP=false
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:////var/lib/yuyue/yuyue.db
UPLOAD_DIR=/var/lib/yuyue/uploads
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_UPLOAD_MB=2
HOST=0.0.0.0
PORT=${YUYUE_PORT}
FRONTEND_DIST=${YUYUE_FRONTEND}/dist
CORS_ORIGINS=["${PUBLIC_URL}","http://127.0.0.1:${YUYUE_PORT}","http://localhost:${YUYUE_PORT}"]
EOF
  chown "${YUYUE_DEPLOY_USER}:${YUYUE_DEPLOY_USER}" "${YUYUE_BACKEND}/.env"
  chmod 600 "${YUYUE_BACKEND}/.env"
else
  warn "已存在 backend/.env，跳过生成（如需改端口请编辑 PORT= 与 FRONTEND_DIST=）"
fi

log "构建前端…"
sudo -u "${YUYUE_DEPLOY_USER}" bash -lc "cd '${YUYUE_FRONTEND}' && npm ci && npm run build"

log "初始化数据库表结构…"
sudo -u "${YUYUE_DEPLOY_USER}" bash -lc "cd '${YUYUE_BACKEND}' && source .venv/bin/activate && python -c 'from app.seed import init_db; init_db(); print(\"schema ok\")'"

if [[ "${WITH_SEED}" -eq 1 ]]; then
  warn "写入演示测试数据（seed_test，仅首次部署建议使用）…"
  sudo -u "${YUYUE_DEPLOY_USER}" bash -lc "cd '${YUYUE_BACKEND}' && source .venv/bin/activate && ENVIRONMENT=development python -m app.seed_test"
fi

log "配置 systemd 服务…"
render_template "${YUYUE_ROOT}/deploy/systemd/yuyue-backend.service.template" "/etc/systemd/system/${YUYUE_SERVICE}.service"
systemctl daemon-reload
systemctl enable "${YUYUE_SERVICE}"

log "配置防火墙 ufw…"
if ufw status | grep -q inactive; then
  ufw --force enable
fi
ufw allow OpenSSH >/dev/null 2>&1 || ufw allow 22/tcp
ufw allow "${YUYUE_PORT}/tcp" comment 'yuyue app' >/dev/null 2>&1 || true

log "启动服务…"
systemctl restart "${YUYUE_SERVICE}"

cat <<EOF

============================================================
  欲阅 · 安装完成（单端口模式）
============================================================
  访问地址:     ${PUBLIC_URL}
  健康检查:     ${PUBLIC_URL}/health
  API 文档:     ${PUBLIC_URL}/docs
  数据目录:     ${YUYUE_DATA_DIR}
  日志目录:     ${YUYUE_LOG_DIR}
  服务管理:     systemctl status ${YUYUE_SERVICE}

  开放端口:     ${YUYUE_PORT}/tcp（公网 IP:端口 直连，无 Nginx）

  常用命令:
    bash scripts/start.sh
    bash scripts/stop.sh
    bash scripts/status.sh

  修改端口后请同步:
    1. backend/.env 中 PORT=
    2. sudo bash scripts/install.sh --port <新端口>  或手动改 systemd 单元

EOF

if [[ "${WITH_SEED}" -eq 1 ]]; then
  cat <<'EOF'
  测试账号（seed）:
    admin / admin123
    reader / test123
  注册码: YUYUE-DEMO-2026
EOF
fi

echo "============================================================"
