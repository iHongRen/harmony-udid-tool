#!/usr/bin/env sh

set -eu

REPO_OWNER="${REPO_OWNER:-iHongRen}"
REPO_NAME="${REPO_NAME:-harmony-udid-tool}"
APP_NAME="${APP_NAME:-HarmonyOS-UDID-Tool}"
INSTALL_DIR="${INSTALL_DIR:-/Applications}"
RELEASE_API_URL="${RELEASE_API_URL:-https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest}"

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'error: required command not found: %s\n' "$1" >&2
    exit 1
  fi
}

need_command curl
need_command hdiutil
need_command open
need_command xattr

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/harmony-udid-tool-install.XXXXXX")"
MOUNT_DIR="${TMP_DIR}/mount"
MOUNTED=0

cleanup() {
  if [ "${MOUNTED}" -eq 1 ]; then
    hdiutil detach "${MOUNT_DIR}" -quiet >/dev/null 2>&1 || true
  fi
  rm -rf "${TMP_DIR}"
}

trap cleanup EXIT INT TERM

if [ -n "${DMG_URL:-}" ]; then
  DOWNLOAD_URL="${DMG_URL}"
else
  printf 'Finding the latest release...\n'
  DOWNLOAD_URL="$(curl -fsSL "${RELEASE_API_URL}" \
    | sed -nE 's/.*"browser_download_url": "([^" ]+\.dmg)".*/\1/p' \
    | head -n 1)"
  if [ -z "${DOWNLOAD_URL}" ]; then
    printf 'error: no DMG asset was found in the latest release\n' >&2
    exit 1
  fi
fi

DMG_NAME="${DOWNLOAD_URL##*/}"
DMG_PATH="${TMP_DIR}/${DMG_NAME}"
TARGET_APP="${INSTALL_DIR}/${APP_NAME}.app"

printf 'Downloading %s...\n' "${DOWNLOAD_URL}"
curl -fL --progress-bar "${DOWNLOAD_URL}" -o "${DMG_PATH}"

mkdir -p "${MOUNT_DIR}"
printf 'Mounting %s...\n' "${DMG_NAME}"
hdiutil attach "${DMG_PATH}" \
  -nobrowse \
  -readonly \
  -noverify \
  -mountpoint "${MOUNT_DIR}" \
  -quiet
MOUNTED=1

SOURCE_APP="${MOUNT_DIR}/${APP_NAME}.app"
if [ ! -d "${SOURCE_APP}" ]; then
  printf 'error: %s was not found in the DMG\n' "${APP_NAME}.app" >&2
  exit 1
fi

printf 'Installing to %s...\n' "${TARGET_APP}"
mkdir -p "${INSTALL_DIR}"
rm -rf "${TARGET_APP}"
cp -R "${SOURCE_APP}" "${TARGET_APP}"

printf 'Removing macOS quarantine attributes...\n'
xattr -dr com.apple.quarantine "${TARGET_APP}" >/dev/null 2>&1 || true

printf 'Installed %s successfully.\n' "${TARGET_APP}"
printf 'Opening %s...\n' "${APP_NAME}.app"
open "${TARGET_APP}"