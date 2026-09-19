#!/usr/bin/env python3
"""Render visible Markdown metadata from YAML without requiring a custom previewer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import argparse, os, re, sys
from pathlib import Path
from workflow_support import ROOT, config

START = "<!-- wiki:metadata:start -->"
END = "<!-- wiki:metadata:end -->"


def metadata(text):
    if not text.startswith("---\n"):
        raise ValueError("缺少 YAML 头部")
    match = re.match(r"\A---\n(.*?)^---[ \t]*(?:\n|$)(.*)\Z", text, re.M | re.S)
    if not match:
        raise ValueError("YAML 头部缺少独立的结束分隔行")
    header, body = match.groups()
    result = {}
    key = None
    for line in header.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^  - (.+)$", line)
        if item:
            if key is None or not isinstance(result[key], list):
                raise ValueError("列表必须属于头部字段")
            result[key].append(item[1].strip().strip("\"'"))
            continue
        field = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not field:
            raise ValueError("头部使用 key: value 与两空格缩进的列表")
        key, value = field.groups()
        if key in result:
            raise ValueError("重复字段 " + key)
        result[key] = value.strip().strip("\"'") if value else []
    return result, body


def escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("|", r"\|")
        .replace("\n", " ")
    )


def rendered_document(text, path, root):
    data, body = metadata(text)
    if START in body or END in body:
        if body.count(START) != 1 or body.count(END) != 1:
            raise ValueError("预览信息区标记损坏")
        body = re.sub(re.escape(START) + r".*?" + re.escape(END), "", body, flags=re.S)
    title = escape(data.get("title", ""))
    rows = []
    for key, value in data.items():
        if key == "title":
            continue
        if isinstance(value, list):
            value = " · ".join(str(x) for x in value)
        rows.append("| " + key + " | " + escape(value) + " |")
    block = (
        START
        + "\n# "
        + title
        + "\n\n| 字段 | 内容 |\n|---|---|\n"
        + "\n".join(rows)
        + "\n"
        + END
    )
    header = re.match(r"\A---\n(.*?)^---[ \t]*(?:\n|$)", text, re.M | re.S)[1]
    return "---\n" + header + "---\n\n" + block + "\n\n" + body.strip() + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", action="store_true")
    a = p.parse_args()
    c = config()
    files = list((ROOT / c["wiki_root"]).rglob("*.md")) + list(
        (ROOT / "workflow/guides").glob("*.md")
    )
    changed = []
    for path in files:
        if ".agent" in path.parts:
            continue
        text = path.read_text()
        result = rendered_document(text, path, ROOT)
        if result != text:
            changed.append(path.relative_to(ROOT).as_posix())
            if a.write:
                path.write_text(result)
    if changed and not a.write:
        print("FAIL: 预览信息区未同步：" + "、".join(changed))
        return 1
    print(
        "OK: YAML 与可见标题、信息区一致"
        + ("；更新 " + str(len(changed)) + " 页" if a.write else "")
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
