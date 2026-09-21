#!/usr/bin/env bash
# 欲阅 · 服务状态与健康检查
#
# 用法: bash scripts/status.sh

set -euo pipefail

# shellcheck source=lib/common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

require_ubuntu

if [[ "${EUID}" -ne 0 ]]; then
  YUYUE_SUDO="sudo"
fi

PORT="$(read_deploy_port)"
URL="http://127.0.0.1:${PORT}"

echo "=== systemd ==="
${YUYUE_SUDO} systemctl status "${YUYUE_SERVICE}" --no-pager -l 2>/dev/null | head -n 14 || warn "服务未安装或未运行"
echo

echo "=== 端口监听 ==="
ss -tlnp 2>/dev/null | grep ":${PORT} " || warn "未监听 ${PORT}/tcp"
echo

echo "=== 健康检查 ==="
if curl -fsS "${URL}/health" >/dev/null 2>&1; then
  log "GET ${URL}/health → OK"
  curl -s "${URL}/health"
  echo
else
  warn "GET ${URL}/health → 失败"
fi

if curl -fsS "${URL}/" >/dev/null 2>&1; then
  log "GET ${URL}/ → 前端可达"
else
  warn "GET ${URL}/ → 前端不可达（检查 FRONTEND_DIST 与 dist 构建）"
fi

echo
log "公网访问: $(public_url)"
