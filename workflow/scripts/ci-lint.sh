#!/usr/bin/env bash
# CI 与完整收尾使用同一链；显式 --base=<sha>，不把干净工作树当分支无改动。
set -euo pipefail
source "$(dirname "$0")/lib/_common.sh"
if [ "$#" -eq 0 ]; then set -- --scope=branch; fi
export CI=true
exec "$AGENT_DIR/finish-audit.sh" "$@"
