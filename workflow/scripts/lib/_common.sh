# 公共路径与配置；不选择或修改 JDK。
AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$AGENT_DIR/../.." && pwd)"
_config_exports="$(python3 "$AGENT_DIR/lib/workflow_support.py" shell)" || { return 2 2>/dev/null || exit 2; }
eval "$_config_exports"
workflow_has_pack() { case ",${WORKFLOW_PACKS}," in *",$1,"*) return 0;; *) return 1;; esac; }
