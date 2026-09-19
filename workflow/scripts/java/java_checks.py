"""Java diff checks and optional schema checks."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import argparse
import difflib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from workflow_support import ROOT, config, baseline, paths, pairs, git, safe


def module(name):
    spec = importlib.util.spec_from_file_location(
        name,
        Path(__file__).resolve().parents[1]
        / ("java" if name == "lint-java-param" else "sql")
        / (name + ".py"),
    )
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def added(old, new):
    return "\n".join(
        line[1:]
        for line in difflib.unified_diff(old.splitlines(), new.splitlines())
        if line.startswith("+") and not line.startswith("+++")
    )


def http_annotations(source):
    """Collect common Mapping annotations including multiline arguments."""
    annotations = []
    for match in re.finditer(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\b", source):
        end = match.end()
        while end < len(source) and source[end].isspace():
            end += 1
        if end < len(source) and source[end] == "(":
            depth, quote, escaped = 0, None, False
            for index in range(end, len(source)):
                char = source[index]
                if quote:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == quote:
                        quote = None
                elif char in ("'", '"'):
                    quote = char
                elif char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        end = index + 1
                        break
        else:
            end = match.end()
        annotations.append(source[match.start() : end])
    return annotations


def run(kind, base="", scope="uncommitted"):
    c = config()
    base = baseline(ROOT, base, scope)
    files = paths(ROOT, base)
    errors = []
    if kind == "diff":
        param = module("lint-java-param")
        for path in files:
            if not path.endswith(".java") or "java" not in c["packs"]:
                continue
            for old, new in pairs(ROOT, path, base):
                for message in param.violations(old, new):
                    errors.append(path + ": " + message)
        if "version-sql" in c["packs"]:
            freeze = module("lint-version-freeze")
            errors += freeze.check(files, base)
            relevant = [
                f
                for f in files
                if f.startswith(c["version_dir"] + "/") and f.endswith(".sql")
            ]
            if relevant:
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(
                            Path(__file__).resolve().parents[1]
                            / "sql/lint-schema-wiki.py"
                        ),
                    ]
                    + (["--base=" + base] if base else []),
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode:
                    errors.append(proc.stdout + proc.stderr)
    elif kind == "version":
        if "version-sql" not in c["packs"]:
            print("SKIP: version-sql pack 未启用")
            return 0
        schema = module("lint-schema-wiki")
        for path in files:
            if not path.startswith(c["version_dir"] + "/") or not path.endswith(".sql"):
                continue
            for _, new in pairs(ROOT, path, base):
                if not new:
                    continue
                if "【正向变更】" not in new or "【回滚脚本】" not in new:
                    errors.append(path + ": 必须有正向变更与回滚脚本两段")
                tokens = [
                    m[0]
                    for m in schema.TOKEN.finditer(new)
                    if not m[0].startswith(("--", "#", "/*", "'", '"'))
                ]
                text = " ".join(tokens)
                if re.search(
                    r"\b(?:PREPARE|EXECUTE|information_schema)\b|\bSET\s+@", text, re.I
                ):
                    errors.append(path + ": 不允许动态 SQL/元数据守卫")
    elif kind == "http":
        for path in files:
            if not path.endswith(".java"):
                continue
            for old, new in pairs(ROOT, path, base):
                for line in difflib.unified_diff(
                    http_annotations(old), http_annotations(new)
                ):
                    if line[:1] in ("+", "-") and not line.startswith(("+++", "---")):
                        print("HTTP_PATH_CHANGED:", path, line.replace("\n", " "))

        print(
            "INFO: 以上仅为 Spring Mapping 注解差异线索；按实际变更核对调用兼容性和已有接口说明。鉴权或数据范围变化时才按项目规则另行核查；不要求文档平台或上传。"
        )
    elif kind == "index":
        if "index" not in c["packs"]:
            print("SKIP: index pack 未启用")
            return 0
        for path in files:
            if not path.endswith(".sql"):
                continue
            for old, new in pairs(ROOT, path, base):
                table = "?"
                for line in difflib.unified_diff(
                    old.splitlines(), new.splitlines(), n=100000
                ):
                    match = re.search(
                        r"(?:CREATE|ALTER)\s+TABLE\s+(?:IF NOT EXISTS\s+)?`?([\w]+)",
                        line,
                        re.I,
                    )
                    if match:
                        table = match[1]
                    if (
                        line[:1] in ("+", "-")
                        and not line.startswith(("+++", "---"))
                        and re.search(r"\b(?:KEY|INDEX)\b", line, re.I)
                        and not re.search(r"\b(?:PRIMARY|FOREIGN)\s+KEY\b", line, re.I)
                    ):
                        print("INDEX_DDL_CHANGED:", path, "table=" + table, line)
        print("INFO: 命中索引须列入交付；本检查不证明查询索引覆盖")
    for error in sorted(set(errors)):
        print("P1:", error)
    if not errors:
        print("OK:", kind)
    return int(bool(errors))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["diff", "version", "http", "index"])
    p.add_argument("--base", default="")
    p.add_argument("--scope", default="uncommitted", choices=["branch", "uncommitted"])
    a = p.parse_args()
    try:
        raise SystemExit(run(a.kind, a.base, a.scope))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print("FAIL:", exc)
        raise SystemExit(2)
