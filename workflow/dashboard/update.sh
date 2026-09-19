#!/bin/sh
set -eu
DASHBOARD_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$DASHBOARD_DIR/build-workflow-page.py"
python3 "$DASHBOARD_DIR/build-workflow-page.py" --check
printf '\n%s\n' '看板已更新。可把以下提示词发给 Agent 核对流程说明：'
cat "$DASHBOARD_DIR/update-prompt.txt"
