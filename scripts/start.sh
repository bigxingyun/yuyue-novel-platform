#!/usr/bin/env bash
# 欲阅 · 一键启动
#
# 用法: bash scripts/start.sh

set -euo pipefail

# shellcheck source=lib/common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

require_ubuntu

if [[ ! -f "${YUYUE_VENV}/bin/uvicorn" ]]; then
  die "未找到虚拟环境，请先运行: sudo bash scripts/install.sh"
fi

if [[ "${EUID}" -ne 0 ]]; then
  YUYUE_SUDO="sudo"
fi

log "启动 ${YUYUE_SERVICE} …"
${YUYUE_SUDO} systemctl start "${YUYUE_SERVICE}"

log "已启动 → $(public_url)"
log "状态检查: bash scripts/status.sh"
