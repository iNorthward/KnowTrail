#!/usr/bin/env python3
"""Build the offline workflow reference. Standard library only; never runs gates.

Descriptions are curated; source text, glob declarations and invocation order are
read from the repository. --check detects stale generated output without writing.
"""
import argparse
import base64
import html
import hashlib
import json
import os
import tempfile
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "workflow/dashboard/index.html"
TEMPLATE = ROOT / "workflow/dashboard/page.template.html"

# name, source, trigger, purpose; the authoritative glob list is extracted below.
PACKS = [
    (
        "java",
        "java-coding-standards",
        "Java 源码路径",
        "使用者填写的规范入口，按既有约定验证。",
    ),
    (
        "wiki",
        "java-wiki",
        "结构关联变化、完整档或 Wiki 路径",
        "维护专题、数据库字典、索引与症状。",
    ),
    (
        "index",
        "java-index",
        "Mapper、原生 SQL、建表与批量 Job",
        "核对索引覆盖和批量处理上界。",
    ),
    (
        "version-sql",
        "java-version-delivery",
        "版本 SQL 与 Entity",
        "正向、回滚、版本归属与冻结。",
    ),
]
GATES = [
    (
        "lint-wiki-format.sh",
        "Wiki 文档规范",
        "检查头部、五类章节、专用结构及来源链接。",
        "Wiki/文档变化",
        "同本地条件",
        "block",
    ),
    (
        "workflow_support.py",
        "项目附加门禁",
        "运行配置 checks 中的 argv 检查；失败或超时阻断。",
        "完整收尾末尾",
        "同本地条件",
        "block",
    ),
    (
        "audit-change-scope.sh",
        "识别改动范围",
        "从 Git 推断改动与 Maven 模块。",
        "总是执行",
        "总是执行",
        "block",
    ),
    (
        "check-branch.sh",
        "版本归属与冻结",
        "检查可选版本 SQL 归属。",
        "启用 version-sql 且版本目录变化",
        "启用 version-sql 且版本目录变化",
        "block",
    ),
    (
        "lint-agent-docs.sh",
        "Agent 指引",
        "检查错误的手动操作要求。",
        "文档或代码变化",
        "同本地条件",
        "block",
    ),
    (
        "lint-wiki-symptoms.sh",
        "症状索引",
        "缺陷页症状必须在索引注册。",
        "Wiki 变化",
        "同本地条件",
        "block",
    ),
    (
        "lint-agent-diff.sh",
        "Java 与结构门禁",
        "既有参数文档保护；可选结构文档与版本冻结。",
        "有改动",
        "有改动",
        "block",
    ),
    (
        "compile-audit.sh",
        "编译受影响模块",
        "遵循当前或显式指定的 JDK；执行 Maven 或项目自定义构建。",
        "Java/构建变化",
        "同本地条件",
        "block",
    ),
    (
        "lint-http-paths.sh",
        "HTTP 路径提示",
        "标出 Mapping 差异，按变化核对调用兼容性；不强制鉴权或文档平台。",
        "含 Mapping 的 Java 文件变化",
        "同本地条件",
        "warn",
    ),
    (
        "lint-index-ddl.sh",
        "索引 DDL 提示",
        "列出索引变更；不证明查询覆盖，脚本异常会阻断。",
        "SQL 变化",
        "同本地条件",
        "warn",
    ),
    (
        "lint-version-sql.sh",
        "版本 SQL",
        "正向、回滚和动态语句检查。",
        "启用 version-sql 且版本 SQL 变化",
        "同本地条件",
        "block",
    ),
    (
        "lint-wiki-index.sh",
        "Wiki 索引",
        "全库检查专题注册与索引链接。",
        "Wiki/文档变化",
        "同本地条件",
        "block",
    ),
    (
        "lint-wiki-stale.sh",
        "可选复核提醒",
        "默认关闭；长期未更新不代表失效，提醒与工具异常均不阻断。",
        "显式配置 wiki_review_days 后",
        "同本地条件",
        "warn",
    ),
    (
        "check-precipitate.sh",
        "待沉淀提示",
        "重复同类项提醒人工沉淀。",
        "完整收尾",
        "同本地条件",
        "warn",
    ),
]
CHILDREN = [
    (
        "java_checks.py",
        "通用检查编排",
        "保护仍保留的参数说明；按选择调用结构与冻结检查。",
    ),
    (
        "lint-java-param.py",
        "参数文档保护",
        "保护仍存在的方法参数文档；删除整个方法不误报。",
    ),
    ("lint-version-freeze.py", "版本冻结", "核对目标版本、旧目录冻结与原样继承。"),
    ("lint-schema-wiki.py", "结构与字典同步", "核对变更表对应数据库文档段落同步更新。"),
]

SCRIPT_PATHS = {
    "audit-change-scope.sh": "audit/audit-change-scope.sh",
    "lint-agent-docs.sh": "audit/lint-agent-docs.sh",
    "compile.sh": "build/compile.sh",
    "compile-audit.sh": "build/compile-audit.sh",
    "compile.cmd": "build/compile.cmd",
    "compile.ps1": "build/compile.ps1",
    "lint-agent-diff.sh": "java/lint-agent-diff.sh",
    "lint-java-param.py": "java/lint-java-param.py",
    "lint-http-paths.sh": "java/lint-http-paths.sh",
    "java_checks.py": "java/java_checks.py",
    "check-branch.sh": "sql/check-branch.sh",
    "lint-index-ddl.sh": "sql/lint-index-ddl.sh",
    "lint-schema-wiki.sh": "sql/lint-schema-wiki.sh",
    "lint-schema-wiki.py": "sql/lint-schema-wiki.py",
    "lint-version-freeze.py": "sql/lint-version-freeze.py",
    "lint-version-sql.sh": "sql/lint-version-sql.sh",
    "check-precipitate.sh": "wiki/check-precipitate.sh",
    "lint-wiki-format.sh": "wiki/lint-wiki-format.sh",
    "lint-wiki-format.py": "wiki/lint-wiki-format.py",
    "lint-wiki-index.sh": "wiki/lint-wiki-index.sh",
    "lint-wiki-stale.sh": "wiki/lint-wiki-stale.sh",
    "lint-wiki-symptoms.sh": "wiki/lint-wiki-symptoms.sh",
    "wiki_metadata.py": "wiki/wiki_metadata.py",
    "_common.sh": "lib/_common.sh",
    "workflow_support.py": "lib/workflow_support.py",
}


def calls(source):
    """Ordered, deduplicated literal AGENT_DIR calls (not console step labels)."""
    return list(
        dict.fromkeys(
            Path(p).name
            for p in re.findall(r"\$AGENT_DIR/([a-z][a-z0-9_/-]*\.(?:sh|py))", source)
        )
    )


def build_data(root=ROOT):
    paths = {
        "workflow/config.json",
        "workflow/task-start.md",
        ".cursor/rules/agent-workflow.mdc",
    }
    cfg = json.loads((root / "workflow/config.json").read_text())
    wiki = cfg["wiki_root"]
    paths.update(
        "workflow/guides/" + name + ".md"
        for name in [
            "agent-essentials",
            "task-routing",
            "change-audit-checklist",
            "wiki-doc-template",
        ]
    )
    paths.update(
        ".cursor/rules/" + rule + ".mdc"
        for _, rule, _, _ in PACKS
        if (root / (".cursor/rules/" + rule + ".mdc")).exists()
    )
    paths.update(
        "workflow/scripts/" + SCRIPT_PATHS.get(name, name)
        for name in {g[0] for g in GATES}
        | {c[0] for c in CHILDREN}
        | {
            "finish-audit.sh",
            "ci-lint.sh",
            "compile.sh",
            "_common.sh",
            "workflow_support.py",
            "lint-schema-wiki.sh",
            "lint-wiki-format.py",
            "wiki_metadata.py",
        }
    )
    paths.add("workflow/scripts/lib/java_environment.py")
    paths.add("workflow/scripts/wiki/review-reminder.py")
    paths.add("workflow/scripts/wiki/wiki_links.py")
    paths.add("workflow/templates/version-sql.md")
    sources = {
        path: (root / path).read_text()
        for path in sorted(paths)
        if (root / path).is_file()
    }
    sources["AGENTS.md"] = (root / "AGENTS.md").read_text()
    packs = []
    for name, rule, trigger, purpose in PACKS:
        path = ".cursor/rules/" + rule + ".mdc"
        if name not in cfg["packs"] or path not in sources:
            continue
        fm = sources[path].split("---", 2)[1]
        packs.append(
            dict(
                name=name,
                source=path,
                trigger=trigger,
                purpose=purpose,
                globs=re.findall(r"^  - (.+)$", fm, re.M),
                baseline=False,
            )
        )
    gates = {
        g[0]: dict(zip(["name", "title", "purpose", "local", "ci", "kind"], g))
        for g in GATES
    }
    order = calls(sources["workflow/scripts/finish-audit.sh"])
    unknown = set(order) - set(gates)
    if unknown:
        raise ValueError("未说明的新门禁: " + str(unknown))
    payload = dict(
        scriptPaths=SCRIPT_PATHS,
        packs=packs,
        gates=gates,
        chains=dict(local=order, ci=order),
        children=[dict(name=n, title=t, purpose=p) for n, t, p in CHILDREN],
        sources=sources,
    )
    payload["fingerprint"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()[:12]
    return payload


def render(root=ROOT):
    data = json.dumps(
        build_data(root), ensure_ascii=False, separators=(",", ":")
    ).replace("<", "\\u003c")
    template = (root / "workflow/dashboard/page.template.html").read_text(
        encoding="utf-8"
    )
    if template.count("__WORKFLOW_DATA__") != 1:
        raise ValueError("Expected exactly one data placeholder")
    icon = (root / "workflow/dashboard/assets/workflow-mark.svg").read_bytes()
    icon_url = "data:image/svg+xml;base64," + base64.b64encode(icon).decode("ascii")
    header_icon = icon.replace(b"#343631", b"#faf9f5")
    header_url = "data:image/svg+xml;base64," + base64.b64encode(header_icon).decode(
        "ascii"
    )
    for path in re.findall(r'data-source="([^"]+)"', template):
        if "${" not in path and path not in build_data(root)["sources"]:
            template = re.sub(
                r'<button class="source" data-source="'
                + re.escape(path)
                + r'">.*?</button>',
                '<span class="pill">该资料未启用</span>',
                template,
            )
    return (
        template.replace("__BRAND_HEADER_ICON__", header_url)
        .replace("__BRAND_ICON__", icon_url)
        .replace("__WORKFLOW_DATA__", data)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != result:
            parser.exit(
                1,
                "FAIL: workflow HTML differs from current sources/template; regenerate it.\n",
            )
        print("OK: workflow HTML matches its sources and template")
    else:
        # Replace only after rendering succeeds; readers never see a partial page.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=OUTPUT.parent, delete=False
            ) as stream:
                temporary = Path(stream.name)
                stream.write(result)
            temporary.chmod(0o644)
            os.replace(temporary, OUTPUT)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        print("Generated workflow/dashboard/index.html")


if __name__ == "__main__":
    main()
