#!/usr/bin/env python3
"""Validate the Wiki's documented YAML subset, headings and local evidence links."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import datetime, json, re, sys
from pathlib import Path
from workflow_support import ROOT, config

from wiki_metadata import metadata, rendered_document


def visible(text):
    return re.sub(r"<!--.*?-->|```.*?```|`[^`\n]*`", "", text, flags=re.S)


def validate(root, wiki):
    schema = json.loads((wiki / "templates/schema.json").read_text())
    errors = []
    files = list(wiki.rglob("*.md")) + list((root / "workflow/guides").glob("*.md"))
    for path in sorted(files):
        in_wiki = wiki in path.parents
        rel = path.relative_to(wiki if in_wiki else root).as_posix()
        if in_wiki and ".agent" in path.relative_to(wiki).parts:
            continue
        template = in_wiki and rel.startswith("templates/")
        try:
            original = path.read_text()
            data, body = metadata(original)
            if original != rendered_document(original, path, root):
                raise ValueError("预览信息区未同步；运行 wiki_metadata.py --write")
            for key in schema["required"]:
                if not data.get(key):
                    raise ValueError("缺少非空字段 " + key)
            if not isinstance(data["sources"], list):
                raise ValueError("sources 必须是列表")
            if not template:
                datetime.date.fromisoformat(data["updated"])
                if data.get("verified"):
                    datetime.date.fromisoformat(data["verified"])
                for source in data["sources"]:
                    if re.match(r"^https?://", source):
                        continue
                    dest = (root / source).resolve()
                    if root.resolve() not in dest.parents or not dest.is_file():
                        raise ValueError("来源文件不存在或越界 " + source)
            kind = data["type"]
            special = schema["special_documents"].get(rel) if in_wiki else None
            if special:
                if kind != special["type"]:
                    raise ValueError("专用文档 type 应为 " + special["type"])
                expected = special["headings"]
            else:
                if kind not in schema["types"]:
                    raise ValueError("未知专题类型 " + str(kind))
                expected = schema["types"][kind]
            if kind == "bugfix" and (
                not isinstance(data.get("symptoms"), list) or not data["symptoms"]
            ):
                raise ValueError("bugfix 缺少 symptoms 列表")
            if (
                kind == "decision"
                and data.get("status")
                and data["status"]
                not in ["proposed", "adopted", "implemented", "superseded"]
            ):
                raise ValueError("无效决策状态")
            clean = re.sub(r"```.*?```", "", body, flags=re.S)
            matches = list(re.finditer(r"^## (.+)$", clean, re.M))
            actual = [m[1] for m in matches]
            if special and special["type"] == "database":
                actual = [
                    x
                    for x in actual
                    if not re.fullmatch(r"`[A-Za-z0-9_]+\.[A-Za-z0-9_]+`", x)
                ]
            if actual != expected:
                raise ValueError(
                    "二级章节应为 "
                    + " → ".join(expected)
                    + "；实际 "
                    + " → ".join(actual)
                )
            if not template:
                for i, m in enumerate(matches):
                    end = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
                    if not re.sub(
                        r"<!--.*?-->", "", clean[m.end() : end], flags=re.S
                    ).strip():
                        raise ValueError("章节为空 " + m[1])
                for target in re.findall(r"\[\[([^\]]+)\]\]", visible(body)):
                    name = target.split("|")[0].split("#")[0]
                    dest = (wiki / (name + ".md")).resolve()
                    if wiki.resolve() not in dest.parents or not dest.is_file():
                        raise ValueError("Wiki 链接不存在 " + name)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(rel + ": " + str(exc))
    return errors


def main():
    c = config()
    if "wiki" not in c["packs"]:
        print("SKIP: wiki 规则未启用")
        return 0
    errors = validate(ROOT, ROOT / c["wiki_root"])
    if errors:
        print("\n".join("FAIL: " + e for e in errors))
        return 1
    print("OK: Wiki 头部、模板章节、专用结构与来源链接一致")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
