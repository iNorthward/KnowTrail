#!/usr/bin/env bash
# 输出改动范围与检查提示；向上查找最近 pom.xml 确定模块。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/lib/workflow_support.py" audit "$@"
