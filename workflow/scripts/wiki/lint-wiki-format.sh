#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/wiki/lint-wiki-format.py"
