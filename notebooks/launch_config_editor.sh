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

export BROWSER=firefox

cd "${REPO_DIR}"
exec pixi run marimo run "${NOTEBOOK}"
