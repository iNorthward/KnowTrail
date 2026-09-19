#!/usr/bin/env bash
# 项目构建入口：遵循当前 JDK/Wrapper，或运行配置中的完整命令。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/lib/workflow_support.py" compile "${1:-.}"
