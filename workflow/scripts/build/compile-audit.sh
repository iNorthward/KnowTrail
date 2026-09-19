#!/usr/bin/env bash
# 按 audit-change-scope.sh 推断的 COMPILE_MODULES 依次编译
# 用法：
#   workflow/scripts/build/compile-audit.sh
#   workflow/scripts/build/compile-audit.sh --scope=branch
#   workflow/scripts/build/compile-audit.sh --base=<sha>
set -euo pipefail

# shellcheck source=_common.sh
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"

SCOPE_ARGS=()
for arg in "${@:-}"; do
  case "$arg" in
    --scope=branch|--base=*) SCOPE_ARGS+=("$arg") ;;
    '') ;;
    *) echo "ERROR: 不支持的参数 $arg" >&2; exit 2 ;;
  esac
done

# bash 3.2 + set -u：空数组 "${arr[@]}" 报 unbound variable
if [ "${#SCOPE_ARGS[@]}" -eq 0 ]; then
  AUDIT_OUT="$("$AGENT_DIR/audit/audit-change-scope.sh")"
else
  AUDIT_OUT="$("$AGENT_DIR/audit/audit-change-scope.sh" "${SCOPE_ARGS[@]}")"
fi

SKIP_COMPILE="$(echo "$AUDIT_OUT" | awk -F= '/^SKIP_COMPILE=/{print $2; exit}')"
COMPILE_MODULES="$(echo "$AUDIT_OUT" | awk -F= '/^COMPILE_MODULES=/{print $2; exit}')"

if [ "$SKIP_COMPILE" = "yes" ]; then
  echo "SKIP: 当前范围没有构建影响"
  exit 0
fi

if [ -z "$COMPILE_MODULES" ] || [ "$COMPILE_MODULES" = "none" ]; then
  echo "ERROR: 需要编译但未确定 COMPILE_MODULES，不能作为编译通过" >&2
  exit 2
fi

IFS=',' read -ra MODULES <<< "$COMPILE_MODULES"
for mod in "${MODULES[@]}"; do
  echo "== compile: $mod =="
  "$AGENT_DIR/build/compile.sh" "$mod"
done

echo "OK: compile-audit 全部构建命令执行成功"
