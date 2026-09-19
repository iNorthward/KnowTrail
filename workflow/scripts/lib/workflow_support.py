"""Shared mechanical helpers for the Java shell workflow, not a product runtime."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from java_environment import build_environment

ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = dict(
    version=1,
    project_name="Java 工作流",
    wiki_root="wiki",
    version_dir="workflow/changes",
    database="app",
    java_version=None,
    wiki_review_days=None,
    packs=["java", "wiki", "index"],
    build_command=[],
    build_args=[],
    offline=False,
    hot_tables=[],
    checks=[],
)


def safe(root, name):
    root = Path(root).resolve()
    if (
        not isinstance(name, str)
        or Path(name).is_absolute()
        or ".." in Path(name).parts
        or "\\" in name
    ):
        raise ValueError("非法相对路径: " + str(name))
    p = root / name
    if p.resolve() != root and root not in p.resolve().parents:
        raise ValueError("路径越界: " + name)
    return p


def config(root=ROOT):
    path = Path(root) / "workflow/config.json"
    value = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(value, dict) or set(value) - set(DEFAULTS):
        raise ValueError("工作流配置存在未知字段")
    c = {**DEFAULTS, **value}
    if c["wiki_review_days"] is not None and (
        type(c["wiki_review_days"]) is not int or c["wiki_review_days"] <= 0
    ):
        raise ValueError("wiki_review_days 应为正整数或 null")
    if type(c["offline"]) is not bool:
        raise ValueError("offline 应为布尔值")
    if type(c["version"]) is not int or c["version"] != 1:
        raise ValueError("配置版本不支持")
    for name in ["wiki_root", "version_dir"]:
        safe(root, c[name])
    if any(
        not Path(c[k]).parts or Path(c[k]).parts[0] in (".git", ".cursor")
        for k in ["wiki_root", "version_dir"]
    ):
        raise ValueError("Wiki/SQL 根不能是仓库或工作流保留目录")
    if c["java_version"] is not None and (
        type(c["java_version"]) is not int or not 8 <= c["java_version"] <= 99
    ):
        raise ValueError("java_version 应为 JDK 主版本整数或 null")
    if not isinstance(c["database"], str) or not re.fullmatch(
        r"[A-Za-z0-9_]+", c["database"]
    ):
        raise ValueError("逻辑库名非法")
    for key in ["packs", "build_command", "build_args", "hot_tables"]:
        if not isinstance(c[key], list) or not all(
            isinstance(x, str) and x for x in c[key]
        ):
            raise ValueError("配置应为字符串数组: " + key)
    if set(c["packs"]) - {"java", "wiki", "index", "version-sql"}:
        raise ValueError("未知内置 pack；扩展使用 custom MDC 与 checks")
    if "version-sql" in c["packs"] and "wiki" not in c["packs"]:
        raise ValueError("version-sql 依赖 wiki 结构文档")
    if not isinstance(c["checks"], list):
        raise ValueError("checks 应为数组")
    names = set()
    for check in c["checks"]:
        if not isinstance(check, dict) or set(check) - {
            "id",
            "description",
            "command",
            "timeout",
        }:
            raise ValueError("额外门禁字段非法")
        if (
            not re.fullmatch(r"[a-z][a-z0-9-]*", check.get("id", ""))
            or check["id"] in names
        ):
            raise ValueError("门禁 id 非法或重复")
        names.add(check["id"])
        if (
            not isinstance(check.get("command"), list)
            or not check["command"]
            or not all(isinstance(v, str) for v in check["command"])
        ):
            raise ValueError("门禁必须为 argv 数组")
        if (
            not isinstance(check.get("timeout", 300), (float, int))
            or not 0 < check.get("timeout", 300) <= 3600
        ):
            raise ValueError("门禁超时无效")
    return c


def git(root, *args, missing=False):
    p = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if p.returncode and not missing:
        raise ValueError(p.stderr.strip() or "Git 执行失败")
    return p.stdout if p.returncode == 0 else ""


def baseline(root, base="", scope="uncommitted"):
    if base:
        if base.startswith("-"):
            raise ValueError("base 不得为选项")
        return git(root, "merge-base", "HEAD", base).strip()
    if scope == "branch":
        head = git(root, "rev-parse", "HEAD").strip()
        for ref in ["origin/HEAD", "origin/main", "main", "origin/master", "master"]:
            value = git(root, "merge-base", "HEAD", ref, missing=True).strip()
            if value and value != head:
                return value
        raise ValueError("无法确定分支基线；指定 --base=<sha>")
    return ""


def paths(root, base=""):
    if base:
        return sorted(
            set(git(root, "diff", "--name-only", "-z", base, "HEAD", "--").split("\0"))
            - {""}
        )
    result = set()
    for args in [
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ]:
        result.update(git(root, *args).split("\0"))
    return sorted(result - {""})


def snapshot(root, path, ref):
    if ref == "work":
        p = safe(root, path)
        return p.read_text() if p.is_file() else ""
    return git(
        root, "show", (":" + path) if ref == ":" else ref + ":" + path, missing=True
    )


def pairs(root, path, base=""):
    if base:
        return [(snapshot(root, path, base), snapshot(root, path, "HEAD"))]
    return [
        (snapshot(root, path, "HEAD"), snapshot(root, path, ":")),
        (snapshot(root, path, ":"), snapshot(root, path, "work")),
    ]


def audit(root, base="", scope="uncommitted"):
    c = config(root)
    base = baseline(root, base, scope)
    files = paths(root, base)
    tags = set()
    modules = set()
    for f in files:
        if any(ch in f for ch in ("\n", "\r", ",")):
            raise ValueError("审计暂不支持路径中的换行或逗号: " + f)
        build_file = Path(f).name in {
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "settings.gradle",
            "settings.gradle.kts",
            "gradle.properties",
            "gradlew",
            "mvnw",
        } or f.startswith((".mvn/", "gradle/"))
        build_changed = (
            f.endswith(".java")
            or build_file
            or (
                "/src/" in "/" + f
                and f.endswith((".xml", ".properties", ".yml", ".yaml"))
            )
        )
        if build_changed:
            if c["build_command"]:
                modules.add(
                    "."
                )  # A custom command owns its workspace and module selection.
            else:
                d = Path(f).parent
                while not (Path(root) / d / "pom.xml").is_file():
                    if d == Path("."):
                        raise ValueError(
                            "构建改动无法匹配 Maven；请在 build_command 配置项目构建命令: "
                            + f
                        )
                    d = d.parent
                modules.add(d.as_posix())
        if f.endswith(".java"):
            tags.add("java")
        if f.endswith(".java"):
            if any(
                re.search(
                    r"@(Get|Post|Put|Patch|Delete|Request)Mapping\b", old + "\n" + new
                )
                for old, new in pairs(root, f, base)
            ):
                tags.add("http")
        if f.endswith("Mapper.xml") or f.endswith("Mapper.java"):
            tags.add("mapper")
        if "/job/" in f or f.endswith("JobHandler.java"):
            tags.add("job")
        if "/feign/" in f:
            tags.add("feign")
        if "/mq/" in f or f.endswith("Listener.java"):
            tags.add("mq")
        if "/entity/" in f or f.endswith("Entity.java"):
            tags.add("entity")
        if f.endswith(".sql"):
            tags.add("sql")
        if (
            f.startswith(c["wiki_root"] + "/")
            or f.startswith(".cursor/")
            or f == "AGENTS.md"
            or f.startswith("workflow/guides/")
            or f == "workflow/config.json"
        ):
            tags.add("wiki")
    if files and all(
        f.endswith((".md", ".mdc", ".txt", ".html", ".svg")) or "/.agent/" in f
        for f in files
    ):
        tags.add("docs-only")
    return dict(
        AUDIT_SCOPE="base" if base else scope,
        BASE=base,
        FILES_CHANGED=len(files),
        TAGS=",".join(sorted(tags)) or "none",
        COMPILE_MODULES=",".join(sorted(modules)) or "none",
        SKIP_COMPILE="no" if modules else "yes",
        # Tags are recognition hints, never a decision to waive semantic review.
        SEMANTIC_REVIEW="pending" if files else "no_changes",
        files=files,
    )


def compile_module(root, module):
    c = config(root)
    path = safe(root, module)
    root = Path(root)
    custom = bool(c["build_command"])
    if custom:
        command = c["build_command"] + c["build_args"]
        cwd = root
        if c["offline"]:
            raise ValueError("自定义构建的离线参数应显式写入 build_command/build_args")
    else:
        if not (path / "pom.xml").is_file():
            raise ValueError(
                "模块缺少 pom.xml；其他构建工具请配置 build_command: " + module
            )
        cwd = root if (root / "pom.xml").is_file() else path
        wrapper = cwd / "mvnw"
        command = ([str(wrapper)] if wrapper.is_file() else ["mvn"]) + (
            c["build_args"] or ["compile"]
        )
        if c["offline"]:
            command += ["-o"]
        if cwd == root and module != ".":
            command += ["-pl", module, "-am"]
    env = build_environment(c["java_version"], require_java=not custom)
    print("build command:", shlex.join(command), "cwd=" + str(cwd), flush=True)
    return subprocess.run(command, cwd=cwd, env=env).returncode


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["shell", "audit", "compile", "checks", "doctor"])
    p.add_argument("module", nargs="?", default=".")
    p.add_argument("--base", default="")
    p.add_argument("--scope", default="uncommitted", choices=["branch", "uncommitted"])
    a = p.parse_args()
    c = config()
    if a.command == "shell":
        for key, value in {
            "WORKFLOW_WIKI_ROOT": c["wiki_root"],
            "WORKFLOW_VERSION_DIR": c["version_dir"],
            "WORKFLOW_DATABASE": c["database"],
            "WORKFLOW_PACKS": ",".join(c["packs"]),
        }.items():
            print("export " + key + "=" + shlex.quote(str(value)))
    elif a.command == "audit":
        out = audit(ROOT, a.base, a.scope)
        for key, value in out.items():
            if key != "files":
                print(str(key) + "=" + str(value))
        print("---\nchanged files:")
        for path in out["files"]:
            print("  " + path)
    elif a.command == "compile":
        return compile_module(ROOT, a.module)
    elif a.command == "checks":
        failed = False
        for check in c["checks"]:
            print("== custom check: " + check["id"] + " ==", flush=True)
            try:
                failed = (
                    subprocess.run(
                        check["command"], cwd=ROOT, timeout=check.get("timeout", 300)
                    ).returncode
                    != 0
                    or failed
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                print("FAIL:", exc)
                failed = True
        if not c["checks"]:
            print("SKIP: 无自定义门禁")
        return int(failed)
    else:
        if not c["build_command"] and not (ROOT / "pom.xml").is_file():
            raise ValueError("没有根 POM；请配置项目 build_command")
        print(json.dumps(c, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        raise SystemExit(2)
