#!/usr/bin/env bash
# 分类检查入口；实现见 java/java_checks.py。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/java/java_checks.py" diff "$@"
