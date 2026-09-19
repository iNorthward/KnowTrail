#!/usr/bin/env bash
# 仅对本次版本目录变更检查版本归属；普通 Java 功能分支不被强制命名 x.y.z。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
workflow_has_pack version-sql || { echo "SKIP: version-sql pack 未启用"; exit 0; }
audit="$(python3 "$AGENT_DIR/lib/workflow_support.py" audit "$@")"
base="$(printf '%s\n' "$audit" | sed -n 's/^BASE=//p')"
printf '%s\n' "$audit" | sed -n '/^changed files:/,$p' | tail -n +2 | sed 's/^  //' | python3 "$AGENT_DIR/sql/lint-version-freeze.py" "$base"
