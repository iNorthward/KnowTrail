"""Optional age reminder; never classify knowledge as wrong based on age."""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workflow_support import ROOT, config
from wiki_metadata import metadata


def main():
    settings = config()
    days = settings["wiki_review_days"]
    if "wiki" not in settings["packs"] or days is None:
        print("SKIP: Wiki 定期复核提醒未启用；长期未更新不代表内容失效")
        return 0
    today = datetime.date.today()
    count = 0
    for path in sorted((ROOT / settings["wiki_root"]).rglob("*.md")):
        relative = path.relative_to(ROOT / settings["wiki_root"])
        if any(part in {".agent", "templates"} for part in relative.parts):
            continue
        data, _ = metadata(path.read_text())
        value = data.get("verified") or data.get("updated")
        if not value:
            continue
        age = (today - datetime.date.fromisoformat(str(value))).days
        if age > days:
            count += 1
            print(f"INFO: {relative} 距上次记录 {age} 天，可按需复核；不是错误，不阻断")
    print(f"INFO: {count} 页可按需复核；未修改文档、未定级，不要求为刷新日期而改文档")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError) as exc:
        print("WARN: Wiki 复核提醒未完成：" + str(exc), file=sys.stderr)
        sys.exit(2)
