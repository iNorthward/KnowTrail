#!/usr/bin/env bash
# 结构 DDL 变更须同时更新对应 Markdown 段落；不连数据库。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
workflow_has_pack version-sql || { echo "SKIP: version-sql 示例未启用"; exit 0; }
exec python3 "$AGENT_DIR/sql/lint-schema-wiki.py" "$@"
