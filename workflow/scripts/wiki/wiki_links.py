"""Validate Wiki navigation using the same metadata parser as format checks."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from workflow_support import ROOT, config, safe
from wiki_metadata import metadata


def links(text):
    text = re.sub(r"<!--.*?-->|```.*?```", "", text, flags=re.S)
    return [
        match.split("|", 1)[0].split("#", 1)[0]
        for match in re.findall(r"\[\[([^\]]+)\]\]", text)
    ]


def validate(wiki, kind):
    index = wiki / "index.md"
    if not index.is_file():
        return ["找不到知识索引: " + str(index)]
    body = index.read_text()
    pages = [
        p
        for p in wiki.rglob("*.md")
        if not any(
            part in {".agent", "templates"} for part in p.relative_to(wiki).parts
        )
    ]
    errors = []
    if kind == "index":
        registered = set(links(body))
        for page in pages:
            if page in (index, wiki / "README.md"):
                continue
            relative = page.relative_to(wiki).with_suffix("").as_posix()
            if relative not in registered:
                errors.append("专题页未登记: " + relative)
        for name in sorted(registered):
            try:
                target = safe(wiki, name + ".md")
                if not target.is_file():
                    errors.append("索引引用不存在: " + name)
            except ValueError:
                errors.append("索引引用越界: " + name)
    else:
        section = re.search(r"^## 症状 → 模块\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        rows = section[1].splitlines() if section else []
        for page in pages:
            data, _ = metadata(page.read_text())
            if data.get("type") != "bugfix":
                continue
            name = page.relative_to(wiki).with_suffix("").as_posix()
            symptoms = data.get("symptoms")
            if not isinstance(symptoms, list) or not symptoms:
                errors.append("bugfix 缺少 symptoms: " + name)
                continue
            matching = [row for row in rows if name in links(row)]
            for symptom in symptoms:
                if not any(symptom in row for row in matching):
                    errors.append("症状未与文档同一行登记: " + name + " / " + symptom)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["index", "symptoms"])
    args = parser.parse_args()
    settings = config()
    if "wiki" not in settings["packs"]:
        print("SKIP: wiki pack 未启用")
        return 0
    errors = validate(ROOT / settings["wiki_root"], args.kind)
    for message in errors:
        print("FAIL:", message)
    if not errors:
        print("OK: Wiki " + args.kind + " 一致")
    return int(bool(errors))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
