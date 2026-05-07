#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
NOTEBOOK="${SCRIPT_DIR}/ibeatles_config_file_editor.py"

if ! command -v firefox >/dev/null 2>&1; then
    echo "firefox not found in PATH" >&2
    exit 1
fi

if ! command -v pixi >/dev/null 2>&1; then
    echo "pixi not found in PATH" >&2
    exit 1
fi

cd "${REPO_DIR}"

LOG="$(mktemp -t marimo-XXXXXX.log)"
trap 'rm -f "${LOG}"' EXIT

pixi run marimo run --headless "${NOTEBOOK}" >"${LOG}" 2>&1 &
MARIMO_PID=$!
trap 'rm -f "${LOG}"; kill "${MARIMO_PID}" 2>/dev/null || true' EXIT

URL=""
for _ in $(seq 1 60); do
    URL="$(grep -Eo 'http://[^[:space:]]+' "${LOG}" | head -n1 || true)"
    [[ -n "${URL}" ]] && break
    if ! kill -0 "${MARIMO_PID}" 2>/dev/null; then
        echo "marimo exited before printing a URL:" >&2
        cat "${LOG}" >&2
        exit 1
    fi
    sleep 0.5
done

if [[ -z "${URL}" ]]; then
    echo "timed out waiting for marimo URL" >&2
    cat "${LOG}" >&2
    exit 1
fi

echo "Opening ${URL} in Firefox"
firefox --new-window "${URL}" >/dev/null 2>&1 &

wait "${MARIMO_PID}"
