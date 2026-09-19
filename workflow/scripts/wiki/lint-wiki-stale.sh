#!/usr/bin/env bash
# 可选复核提醒，默认关闭；日期不代表知识失效。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/wiki/review-reminder.py"
