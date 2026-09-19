#!/usr/bin/env bash
# 一键收尾：按 change-audit-checklist 顺序执行脚本链并输出 Agent 摘要
# 用法：
#   workflow/scripts/finish-audit.sh
#   workflow/scripts/finish-audit.sh --scope=branch
#   需要编译时禁止用 SKIP_COMPILE=yes 将完整收尾标为通过。
#
# 说明：不因单步失败而中断，跑完全链后输出 AGENT_SUMMARY 供填审计模板。
set -uo pipefail

# shellcheck source=_common.sh
source "$(dirname "$0")/lib/_common.sh"
cd "$ROOT"

SCOPE="uncommitted"
SCOPE_ARG=""
for arg in "${@:-}"; do
  case "$arg" in
    --scope=branch)
      SCOPE="branch"
      SCOPE_ARG="--scope=branch"
      ;;
    --base=*) SCOPE=base; SCOPE_ARG="$arg" ;;
    '') ;;
    *) echo "ERROR: 不支持的参数 $arg" >&2; exit 2 ;;
  esac
done

step_ok() { echo "  → OK"; }
step_fail() { echo "  → FAIL (exit $1)"; }

CHECK_BRANCH=skip
LINT_AGENT_DOCS=skip
LINT_WIKI_SYMPTOMS=skip
LINT_WIKI_FORMAT=skip
LINT_DIFF=skip
COMPILE=skip
LINT_HTTP=skip
LINT_INDEX=skip
LINT_VERSION=skip
LINT_WIKI_INDEX=skip
LINT_WIKI_STALE=skip
PRECIPITATE_WARN=skip

echo "== finish-audit ($SCOPE) =="
echo "branch: $(git branch --show-current 2>/dev/null || echo unknown)"
echo "date:   $(date '+%Y-%m-%d %H:%M:%S %z')"
echo ""

echo "--- 1/10 audit-change-scope ---"
if AUDIT_OUT="$("$AGENT_DIR/audit/audit-change-scope.sh" ${SCOPE_ARG:+$SCOPE_ARG} 2>&1)"; then
  echo "$AUDIT_OUT"
else
  rc=$?
  echo "$AUDIT_OUT"
  echo "  → FAIL（audit-change-scope exit $rc）"
  exit "$rc"
fi

TAGS="$(echo "$AUDIT_OUT" | awk -F= '/^TAGS=/{print $2; exit}')"
SEMANTIC_REVIEW="$(echo "$AUDIT_OUT" | awk -F= '/^SEMANTIC_REVIEW=/{print $2; exit}')"
FILES_CHANGED="$(echo "$AUDIT_OUT" | awk -F= '/^FILES_CHANGED=/{print $2; exit}')"
COMPILE_MODULES="$(echo "$AUDIT_OUT" | awk -F= '/^COMPILE_MODULES=/{print $2; exit}')"
SKIP_COMPILE_FLAG="$(echo "$AUDIT_OUT" | awk -F= '/^SKIP_COMPILE=/{print $2; exit}')"

has_version_sql=no
if [ "${FILES_CHANGED:-0}" != "0" ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$line" in
      "$WORKFLOW_VERSION_DIR"/*) has_version_sql=yes ;;
    esac
  done < <(echo "$AUDIT_OUT" | sed -n '/^changed files:/,$p' | tail -n +2 | sed 's/^  //')
fi

echo ""
echo "--- 2/10 check-branch ---"
if [ "$has_version_sql" = yes ]; then
  if "$AGENT_DIR/sql/check-branch.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    CHECK_BRANCH=ok
    step_ok
  else
    rc=$?
    CHECK_BRANCH=fail
    step_fail "$rc"
  fi
else
  echo "  → SKIP（无版本 SQL / entity 变更）"
fi

echo ""
echo "--- 3/10 lint-agent-docs ---"
if echo "${TAGS:-}" | rg -q '(^|,)(wiki|docs-only)(,|$)' || [ "${FILES_CHANGED:-0}" != "0" ]; then
  if "$AGENT_DIR/audit/lint-agent-docs.sh"; then
    LINT_AGENT_DOCS=ok
    step_ok
  else
    rc=$?
    LINT_AGENT_DOCS=fail
    step_fail "$rc"
  fi
else
  echo "  → SKIP"
fi

echo ""
echo "--- Wiki format ---"
if echo "${TAGS:-}" | rg -q '(^|,)(wiki|docs-only)(,|$)'; then
  if "$AGENT_DIR/wiki/lint-wiki-format.sh"; then LINT_WIKI_FORMAT=ok; else LINT_WIKI_FORMAT=fail; fi
fi

echo "--- 4/10 lint-wiki-symptoms ---"
if echo "${TAGS:-}" | rg -q '(^|,)(wiki|docs-only)(,|$)'; then
  if "$AGENT_DIR/wiki/lint-wiki-symptoms.sh"; then
    LINT_WIKI_SYMPTOMS=ok
    step_ok
  else
    rc=$?
    LINT_WIKI_SYMPTOMS=fail
    step_fail "$rc"
  fi
else
  echo "  → SKIP（无 wiki 变更）"
fi

echo ""
echo "--- 5/10 lint-agent-diff ---"
if [ "${FILES_CHANGED:-0}" = "0" ]; then
  echo "  → SKIP（无改动）"
else
  if "$AGENT_DIR/java/lint-agent-diff.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    LINT_DIFF=ok
    step_ok
  else
    rc=$?
    LINT_DIFF=fail
    step_fail "$rc"
  fi
fi

echo ""
echo "--- 6/10 compile-audit ---"
if [ "${SKIP_COMPILE_FLAG:-}" = "yes" ]; then
  echo "  → SKIP（改动范围无需编译）"
elif [ "${SKIP_COMPILE:-}" = "yes" ]; then
  COMPILE=fail
  echo "  → FAIL（本次需要编译，SKIP_COMPILE=yes 不能作为完整收尾通过）"
elif [ "${FILES_CHANGED:-0}" = "0" ]; then
  echo "  → SKIP（无改动）"
else
  if "$AGENT_DIR/build/compile-audit.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    COMPILE=ok
    step_ok
  else
    rc=$?
    COMPILE=fail
    step_fail "$rc"
  fi
fi

echo ""
echo "--- 7/10 lint-http-paths ---"
if echo "${TAGS:-}" | rg -q '(^|,)(http)(,|$)'; then
  if "$AGENT_DIR/java/lint-http-paths.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    LINT_HTTP=ok
    step_ok
  else
    LINT_HTTP=fail
    echo "  → FAIL（HTTP 提示脚本执行异常）"
  fi
else
  echo "  → SKIP（无 HTTP 接口变更）"
fi

echo ""
echo "--- 8/10 lint-index-ddl ---"
if [ "$has_version_sql" = yes ] || echo "${TAGS:-}" | rg -q '(^|,)(sql)(,|$)'; then
  if "$AGENT_DIR/sql/lint-index-ddl.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    LINT_INDEX=ok
    step_ok
  else
    LINT_INDEX=fail
    echo "  → FAIL（索引提示脚本执行异常）"
  fi
else
  echo "  → SKIP（无版本 SQL）"
fi

echo ""
echo "--- 9/10 lint-version-sql ---"
if [ "$has_version_sql" = yes ] || echo "${TAGS:-}" | rg -q '(^|,)(sql)(,|$)'; then
  if "$AGENT_DIR/sql/lint-version-sql.sh" ${SCOPE_ARG:+$SCOPE_ARG}; then
    LINT_VERSION=ok
    step_ok
  else
    rc=$?
    LINT_VERSION=fail
    step_fail "$rc"
  fi
else
  echo "  → SKIP（无版本 SQL）"
fi

echo ""
echo "--- 10/10 lint-wiki ---"
if echo "${TAGS:-}" | rg -q '(^|,)(wiki|docs-only)(,|$)'; then
  if "$AGENT_DIR/wiki/lint-wiki-index.sh"; then
    LINT_WIKI_INDEX=ok
    step_ok
  else
    rc=$?
    LINT_WIKI_INDEX=fail
    step_fail "$rc"
  fi
  if "$AGENT_DIR/wiki/lint-wiki-stale.sh"; then
    LINT_WIKI_STALE=ok
    step_ok
  else
    LINT_WIKI_STALE=warn
    echo "  → WARN（可选复核提醒未完成，不阻断交付）"
  fi
else
  echo "  → SKIP（无 wiki 变更）"
fi

echo ""
echo "--- precipitate ---"
PRECIPITATE_WARN=no
PRECIPITATE_STATUS=fail
if PRECIP_OUT="$("$AGENT_DIR/wiki/check-precipitate.sh")"; then
  PRECIPITATE_STATUS=ok
  echo "$PRECIP_OUT"
  PRECIPITATE_WARN="$(echo "$PRECIP_OUT" | awk -F= '/^PRECIPITATE_WARN=/{print $2; exit}')"
fi

echo ""
EXTRA_STATUS=ok
if ! python3 "$AGENT_DIR/lib/workflow_support.py" checks; then EXTRA_STATUS=fail; fi

echo "== AGENT_SUMMARY（填入 change-audit-checklist 模板）=="
echo "AUDIT_SCOPE=$SCOPE"
echo "EXTRA_CHECKS=$EXTRA_STATUS"
echo "FILES_CHANGED=${FILES_CHANGED:-0}"
echo "TAGS=${TAGS:-none}"
echo "COMPILE_MODULES=${COMPILE_MODULES:-none}"
echo "CHECK_BRANCH=$CHECK_BRANCH"
echo "LINT_AGENT_DOCS=$LINT_AGENT_DOCS"
echo "LINT_WIKI_SYMPTOMS=$LINT_WIKI_SYMPTOMS"
echo "LINT_WIKI_FORMAT=$LINT_WIKI_FORMAT"
echo "LINT_AGENT_DIFF=$LINT_DIFF"
echo "COMPILE=$COMPILE"
echo "LINT_HTTP=$LINT_HTTP"
echo "LINT_INDEX=$LINT_INDEX"
echo "LINT_WORKFLOW_VERSION=$LINT_VERSION"
echo "LINT_WIKI_INDEX=$LINT_WIKI_INDEX"
echo "LINT_WIKI_STALE=$LINT_WIKI_STALE"
echo "PRECIPITATE_WARN=${PRECIPITATE_WARN:-no}"
echo ""
echo "SEMANTIC_REVIEW=${SEMANTIC_REVIEW:-pending}"
echo "TAGS 仅列出脚本识别到的线索；none 或缺少某项不表示没有相关风险。"
echo "SEMANTIC_REVIEW=pending 表示需由 Agent 按实际 diff 核对行为与适用规则，并在变更审计记录依据。"
echo "脚本通过只代表已执行的自动检查通过，不代表语义审阅完成；不据此决定是否启用其他 Agent 或审查工具。"
echo "未执行或不可用的检查必须如实说明，不能标记为通过。"
echo "下一步：输出《变更审计》模板；P0/P1 全清后输出《最终交付清单》"

FINISH_FAIL=0
for s in "$LINT_HTTP" "$LINT_INDEX" "$LINT_WIKI_FORMAT" "$CHECK_BRANCH" "$LINT_AGENT_DOCS" "$LINT_WIKI_SYMPTOMS" "$LINT_DIFF" "$COMPILE" "$LINT_VERSION" "$LINT_WIKI_INDEX" "$PRECIPITATE_STATUS" "$EXTRA_STATUS"; do
  [ "$s" = fail ] && FINISH_FAIL=1
done
exit "$FINISH_FAIL"
