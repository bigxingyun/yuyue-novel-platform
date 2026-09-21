#!/usr/bin/env bash
# 欲阅 · 一键停止
#
# 用法: bash scripts/stop.sh

set -euo pipefail

# shellcheck source=lib/common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

require_ubuntu

if [[ "${EUID}" -ne 0 ]]; then
  YUYUE_SUDO="sudo"
fi

log "停止 ${YUYUE_SERVICE} …"
${YUYUE_SUDO} systemctl stop "${YUYUE_SERVICE}" || true

log "已停止"
