#!/usr/bin/env bash
# 检查每条 bugfix 症状与文档的索引登记。
set -euo pipefail
source "$(dirname "$0")/../lib/_common.sh"
cd "$ROOT"
exec python3 "$AGENT_DIR/wiki/wiki_links.py" symptoms
