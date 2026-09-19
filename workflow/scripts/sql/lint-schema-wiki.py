#!/usr/bin/env python3
"""Check that changed forward DDL has matching Markdown edits. Never connects to a DB."""
import argparse
import os
from collections import Counter
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
DOCS = os.environ.get("WORKFLOW_WIKI_ROOT", "wiki").rstrip("/") + "/database/"
# Literals precede comments so a semicolon/comment marker in a string stays literal.
TOKEN = re.compile(
    r"'(?:\\.|''|[^'\\])*'|\"(?:\\.|\"\"|[^\"\\])*\"|`(?:``|[^`])*`|/\*.*?\*/|--(?=\s|$)[^\n]*|\#[^\n]*|[A-Za-z0-9_$]+|[^\s]",
    re.S,
)
HEADING = re.compile(r"^#{2,3} `([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)`\s*$", re.M)


def forward_ddl(text):
    statements, current = [], []
    for match in TOKEN.finditer(text):
        t = match[0]
        if t.startswith(("--", "#")):
            if re.search(r"【回滚(?:脚本)?】", t):
                break
            continue
        if t.startswith("/*"):
            if t.startswith("/*!"):
                raise ValueError("版本 DDL 中的条件执行注释需人工展开核对，不能跳过")
            continue
        if t == ";":
            statements.append(tuple(current))
            current = []
        else:
            current.append(t)
    if current:
        statements.append(tuple(current))
    return Counter(
        s
        for s in statements
        if s
        and s[0].upper() in ("CREATE", "ALTER", "DROP", "RENAME")
        and any(t.upper() in ("TABLE", "VIEW", "INDEX") for t in s[:9])
    )


def targets(ts, default_db):
    u = [t.upper() for t in ts]
    if "INDEX" in u[:3] and "ON" in u:
        positions = [u.index("ON") + 1]
    elif "TABLE" in u[:4] or "VIEW" in u[:9]:
        at = u.index("TABLE") if "TABLE" in u[:4] else u.index("VIEW")
        pos = at + 1
        if u[pos : pos + 3] == ["IF", "NOT", "EXISTS"]:
            pos += 3
        elif u[pos : pos + 2] == ["IF", "EXISTS"]:
            pos += 2
        positions = [pos]
        if u[0] in ("DROP", "RENAME"):
            positions += [i + 1 for i in range(pos, len(ts)) if u[i] in (",", "TO")]
        elif u[:2] == ["ALTER", "TABLE"] and "RENAME" in u:
            # RENAME COLUMN/INDEX is not a table rename.
            i = u.index("RENAME")
            if u[i + 1] not in ("COLUMN", "INDEX", "KEY"):
                positions.append(i + 2 if u[i + 1] in ("TO", "AS") else i + 1)
    else:
        raise ValueError("无法识别结构变更对象: " + " ".join(ts[:12]))
    result = set()
    for pos in positions:
        name = ts[pos].strip("`")
        db = default_db
        if ts[pos + 1 : pos + 2] == (".",):
            db, name = name, ts[pos + 2].strip("`")
        if not re.fullmatch(r"[A-Za-z0-9_]+", db) or not re.fullmatch(
            r"[A-Za-z0-9_]+", name
        ):
            raise ValueError("未登记的逻辑库/表: " + db + "." + name)
        result.add((db, name))
    return result


def sections(text):
    matches = list(HEADING.finditer(text))
    result = {}
    for i, m in enumerate(matches):
        key = m.groups()
        if key in result:
            raise ValueError("重复结构段落: " + ".".join(key))
        rest = text[m.end() :]
        boundary = re.search(r"^#{1,3} ", rest, re.M)
        result[key] = rest[: boundary.start() if boundary else len(rest)].strip()
    return result


def structure_content(section):
    """Ignore prose and formatting around full SQL definitions; templates use text."""
    if section is None:
        return None
    blocks = re.findall(r"^```sql\s*\n(.*?)^```\s*$", section, re.M | re.S)
    if not blocks:
        return section
    return tuple(
        t[0]
        for t in TOKEN.finditer("\n".join(blocks))
        if not t[0].startswith(("--", "#", "/*"))
    )


def check_pairs(sql_pairs, doc_pairs):
    old_docs, new_docs = {}, {}
    for old, new in doc_pairs:
        for result, text in [(old_docs, old), (new_docs, new)]:
            for key, value in sections(text).items():
                if key in result:
                    raise ValueError("重复结构段落: " + ".".join(key))
                result[key] = value
    for path, old, new in sql_pairs:
        before, after = forward_ddl(old), forward_ddl(new)
        changed = (after - before) + (before - after)
        for statement in changed:
            stem = Path(path).stem
            db = (
                stem
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", stem)
                else os.environ.get("WORKFLOW_DATABASE", "app")
            )
            upper = [t.upper() for t in statement]
            renamed_from = set()
            if upper[:2] == ["ALTER", "TABLE"] and "RENAME" in upper:
                i = upper.index("RENAME")
                if upper[i + 1] not in ("COLUMN", "INDEX", "KEY"):
                    renamed_from = targets(statement[:i], db)
            for database, table in targets(statement, db):
                key = (database, table)
                if key not in new_docs and key not in old_docs:
                    raise ValueError(f"{path}: 缺少 {database}.{table} 的结构段落")
                if structure_content(new_docs.get(key)) == structure_content(
                    old_docs.get(key)
                ):
                    raise ValueError(
                        f"{path}: {database}.{table} 的 DDL 已变更，对应 MD 段落未更新"
                    )
                must_exist = (
                    upper[0] in ("CREATE", "ALTER", "RENAME")
                    and key not in renamed_from
                )
                if upper[0] == "RENAME":
                    # Each TO is followed by a destination; sources may disappear.
                    must_exist = any(
                        key
                        in targets(("ALTER", "TABLE", *statement[i + 1 : i + 4]), db)
                        for i, t in enumerate(upper)
                        if t == "TO"
                    )
                if must_exist and statement in after and key not in new_docs:
                    raise ValueError(
                        f"{path}: {database}.{table} 仍存在，不能仅删除结构段落"
                    )


def git(*args):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        text=True,
        encoding="utf-8",
        stderr=subprocess.PIPE,
    )


def git_path(path):
    return str(path).replace("\\", "/")


def read_at(path, ref):
    path = git_path(path)
    if ref == "EMPTY":
        return ""
    if ref == "work":
        p = ROOT / path
        return p.read_text(encoding="utf-8") if p.is_file() else ""
    exists = (
        git("ls-files", "--", path)
        if ref == ":"
        else git("ls-tree", "--name-only", ref, "--", path)
    )
    if not exists.strip():
        return ""
    return git("show", (":" if ref == ":" else ref + ":") + path)


def check_snapshot(base, target, paths):
    sql_pairs = [
        (p, read_at(p, base), read_at(p, target))
        for p in paths
        if p.endswith(".sql")
        and p.startswith(
            os.environ.get("WORKFLOW_VERSION_DIR", "workflow/changes").rstrip("/") + "/"
        )
    ]
    old_paths = (
        []
        if base == "EMPTY"
        else git("ls-tree", "-r", "--name-only", base, "--", DOCS).splitlines()
    )
    if target == "work":
        new_paths = [p.relative_to(ROOT).as_posix() for p in (ROOT / DOCS).glob("*.md")]
    elif target == ":":
        new_paths = git("ls-files", "--", DOCS).splitlines()
    else:
        new_paths = git("ls-tree", "-r", "--name-only", target, "--", DOCS).splitlines()
    docs = set(p for p in old_paths + new_paths if p.endswith(".md"))
    pairs = [(read_at(p, base), read_at(p, target)) for p in sorted(docs)]
    check_pairs(sql_pairs, pairs)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base")
    p.add_argument("--scope", choices=["branch", "uncommitted"], default="uncommitted")
    args = p.parse_args()
    if args.base or args.scope == "branch":
        ref = args.base
        if not ref:
            for candidate in ["origin/HEAD", "main", "origin/main"]:
                try:
                    ref = git("merge-base", "HEAD", candidate).strip()
                    break
                except subprocess.CalledProcessError:
                    pass
            if not ref:
                raise ValueError("无法确定分支基准，请指定 --base")
        base = git("merge-base", "HEAD", ref).strip()
        paths = git("diff", "--name-only", base, "HEAD").splitlines()
        check_snapshot(base, "HEAD", paths)
    else:
        head = (
            subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "--verify", "HEAD"],
                capture_output=True,
            ).returncode
            == 0
        )
        base = "HEAD" if head else "EMPTY"
        paths = set(
            (
                git("diff", "--name-only", "HEAD").splitlines()
                if head
                else git("ls-files").splitlines()
            )
            + git("ls-files", "--others", "--exclude-standard").splitlines()
        )
        check_snapshot(base, "work", paths)
        staged = git("diff", "--cached", "--name-only").splitlines()
        if staged:
            check_snapshot(base, ":", staged)
    print("OK: 结构 DDL 与对应 MD 段落已同步检查（字段/索引内容仍须审阅）")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, IndexError, subprocess.CalledProcessError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
