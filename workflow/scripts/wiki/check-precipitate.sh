#!/usr/bin/env bash
# 待沉淀收件箱：同类 slug ≥2 则 WARN（不阻断、不定级）。
# 用法：workflow/scripts/wiki/check-precipitate.sh
set -euo pipefail

# shellcheck source=_common.sh
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
workflow_has_pack wiki || { echo "SKIP: wiki pack 未启用"; exit 0; }

INBOX="$WORKFLOW_WIKI_ROOT/common/weekly-summary.md"

echo "== check-precipitate =="
echo "HINT: 本轮若有用户纠正或规则/脚本拦不住的差点写错，须追加 §待沉淀（同类：slug，不定级）"

if [ ! -f "$INBOX" ]; then
  echo "PRECIPITATE_WARN=no"
  exit 0
fi

slugs="$(awk '
  /^## 待沉淀/ { p=1; next }
  /^## / { p=0 }
  p && $0 !~ /<!--/ { print }
' "$INBOX" | sed -n 's/.*同类：\([A-Za-z0-9_-][A-Za-z0-9_-]*\).*/\1/p')"

WARN=no
if [ -n "$slugs" ]; then
  while IFS= read -r slug; do
    [ -z "$slug" ] && continue
    n="$(printf '%s\n' "$slugs" | grep -cx "$slug" || true)"
    if [ "${n:-0}" -ge 2 ]; then
      echo "WARN: 同类「${slug}」已 ${n} 条未评估，会话结束须警示用户处理（仍不定级）"
      WARN=yes
    fi
  done < <(printf '%s\n' "$slugs" | sort -u)
fi

echo "PRECIPITATE_WARN=$WARN"
exit 0
