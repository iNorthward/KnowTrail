#!/usr/bin/env bash
# 禁止在 Agent 入口文档中要求用户手动运行 额外命令或脚本
set -euo pipefail

# shellcheck source=_common.sh
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"

FAIL=0

check_file() {
  local f="$1"
  [ -f "$f" ] || return 0
  local hits
  hits="$(rg -n '请你运行|用户.*运行 workflow/scripts|手动 @ 引用' "$f" 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    echo "FAIL: $f 含面向用户的 Agent 操作指引："
    echo "$hits" | sed 's/^/  /'
    FAIL=1
  fi
}

echo "== lint-agent-docs（用户零操作）=="

for f in \
  AGENTS.md \
  "$WORKFLOW_WIKI_ROOT/README.md" \
  "$WORKFLOW_WIKI_ROOT/index.md" \
  "workflow/guides/agent-essentials.md" \
  "workflow/guides/task-routing.md"; do
  check_file "$f"
done

if [ "$FAIL" -eq 0 ]; then
  echo "OK: Agent 入口文档无用户手动操作指引"
fi

exit "$FAIL"
