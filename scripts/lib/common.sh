#!/usr/bin/env bash
# 欲阅部署脚本公共函数（Ubuntu）

set -euo pipefail

# 被 source 时 BASH_SOURCE[0] 指向本文件（scripts/lib/），需上溯到项目根
_yuyue_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "${_yuyue_lib_dir}")" == "lib" ]]; then
  YUYUE_SCRIPT_DIR="$(cd "${_yuyue_lib_dir}/.." && pwd)"
else
  YUYUE_SCRIPT_DIR="${_yuyue_lib_dir}"
fi
YUYUE_ROOT="$(cd "${YUYUE_SCRIPT_DIR}/.." && pwd)"
YUYUE_BACKEND="${YUYUE_ROOT}/backend"
YUYUE_FRONTEND="${YUYUE_ROOT}/frontend"
YUYUE_VENV="${YUYUE_BACKEND}/.venv"
YUYUE_DATA_DIR="/var/lib/yuyue"
YUYUE_LOG_DIR="/var/log/yuyue"
YUYUE_RUN_DIR="${YUYUE_ROOT}/run"
YUYUE_PORT="${YUYUE_PORT:-9080}"
YUYUE_SERVICE="yuyue"

if [[ "${EUID}" -eq 0 ]]; then
  YUYUE_SUDO=""
  YUYUE_DEPLOY_USER="${SUDO_USER:-root}"
  if [[ "${YUYUE_DEPLOY_USER}" == "root" ]]; then
    YUYUE_DEPLOY_USER="$(logname 2>/dev/null || echo root)"
  fi
else
  YUYUE_SUDO="sudo"
  YUYUE_DEPLOY_USER="$(id -un)"
fi

log() {
  printf '\033[1;34m[yuyue]\033[0m %s\n' "$*"
}

warn() {
  printf '\033[1;33m[yuyue]\033[0m %s\n' "$*" >&2
}

die() {
  printf '\033[1;31m[yuyue]\033[0m %s\n' "$*" >&2
  exit 1
}

require_ubuntu() {
  if [[ ! -f /etc/os-release ]]; then
    die "未检测到 /etc/os-release，本脚本仅支持 Ubuntu。"
  fi
  # shellcheck source=/dev/null
  source /etc/os-release
  if [[ "${ID:-}" != "ubuntu" ]]; then
    die "当前系统为 ${PRETTY_NAME:-unknown}，部署脚本仅支持 Ubuntu。"
  fi
  log "系统: ${PRETTY_NAME}"
}

detect_primary_ip() {
  hostname -I 2>/dev/null | awk '{print $1}'
}

read_deploy_port() {
  if [[ -f "${YUYUE_BACKEND}/.env" ]]; then
    local line
    line="$(grep -E '^PORT=' "${YUYUE_BACKEND}/.env" | tail -n1 || true)"
    if [[ -n "${line}" ]]; then
      echo "${line#PORT=}"
      return
    fi
  fi
  echo "${YUYUE_PORT}"
}

public_url() {
  local ip port
  ip="$(detect_primary_ip)"
  port="$(read_deploy_port)"
  echo "http://${ip}:${port}"
}

render_template() {
  local src="$1"
  local dest="$2"
  sed \
    -e "s|__YUYUE_ROOT__|${YUYUE_ROOT}|g" \
    -e "s|__YUYUE_USER__|${YUYUE_DEPLOY_USER}|g" \
    -e "s|__YUYUE_PORT__|${YUYUE_PORT}|g" \
    "${src}" > "${dest}"
}

ensure_dirs() {
  ${YUYUE_SUDO} mkdir -p "${YUYUE_DATA_DIR}/uploads" "${YUYUE_LOG_DIR}" "${YUYUE_RUN_DIR}"
  ${YUYUE_SUDO} chown -R "${YUYUE_DEPLOY_USER}:${YUYUE_DEPLOY_USER}" "${YUYUE_DATA_DIR}" "${YUYUE_LOG_DIR}"
  chmod 755 "${YUYUE_RUN_DIR}" 2>/dev/null || true
}

is_service_running() {
  ${YUYUE_SUDO} systemctl is-active --quiet "${YUYUE_SERVICE}" 2>/dev/null
}
