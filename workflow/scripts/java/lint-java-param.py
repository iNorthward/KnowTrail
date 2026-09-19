#!/usr/bin/env python3
"""Protect retained Java method parameter docs using whole-file snapshots.

A small declaration scanner, not a Java compiler. Unmapped removed tags require
review instead of granting a hunk-wide exemption for an unrelated deletion.
"""
import re
import subprocess
from pathlib import Path
import sys

LEX = re.compile(
    r'/\*.*?\*/|//[^\n]*|""".*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][\w$]*|[^\s]',
    re.S,
)
IDENT = re.compile(r"[A-Za-z_$][\w$]*\Z")
TAG = re.compile(r"@param\s+(<[^>]+>|[\w$]+)")


def without_annotations(tokens):
    clean = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "@":
            i += 2
            while i + 1 < len(tokens) and tokens[i] == ".":
                i += 2
            if i < len(tokens) and tokens[i] == "(":
                level = 1
                i += 1
                while i < len(tokens) and level:
                    level += (tokens[i] == "(") - (tokens[i] == ")")
                    i += 1
        else:
            clean.append(tokens[i])
            i += 1
    return clean


def parameters(tokens):
    groups = []
    group = []
    depth = 0
    for t in tokens + [","]:
        if t in ("<", "(", "["):
            depth += 1
        elif t in (">", ")", "]"):
            depth -= 1
        if t == "," and depth == 0:
            if group:
                groups.append(group)
            group = []
        else:
            group.append(t)
    names = []
    types = []
    for group in groups:
        # Annotations and final do not identify overloads.
        clean = []
        i = 0
        while i < len(group):
            if group[i] == "@":
                i += 2
                while i + 1 < len(group) and group[i] == ".":
                    i += 2
                if i < len(group) and group[i] == "(":
                    level = 1
                    i += 1
                    while i < len(group) and level:
                        level += (group[i] == "(") - (group[i] == ")")
                        i += 1
            elif group[i] == "final":
                i += 1
            else:
                clean.append(group[i])
                i += 1
        ids = [i for i, t in enumerate(clean) if IDENT.fullmatch(t)]
        if not ids:
            raise ValueError("无法识别 Java 参数")
        pos = ids[-1]
        names.append(clean[pos])
        types.append("".join(clean[:pos] + clean[pos + 1 :]))
    return names, tuple(types)


def methods(text):
    docs = []
    tokens = []
    for m in LEX.finditer(text):
        value = m.group()
        if value.startswith("/**"):
            docs.append((m.start(), m.end(), set(TAG.findall(value))))
        if value.startswith(("/*", "//", '"', "'")):
            continue
        tokens.append((value, m.start()))
    values = [t[0] for t in tokens]
    stack = []
    boundary = 0
    found = {}
    mapped = 0
    i = 0
    while i < len(tokens):
        t = values[i]
        if t == "@" and i + 1 < len(values) and values[i + 1] != "interface":
            j = i + 2
            while j + 1 < len(values) and values[j] == ".":
                j += 2
            if j < len(values) and values[j] == "(":
                level = 1
                j += 1
                while j < len(values) and level:
                    level += (values[j] == "(") - (values[j] == ")")
                    j += 1
            i = j
            continue
        if t == "{":
            header = values[boundary:i]
            name = None
            for j, v in enumerate(header[:-1]):
                if v in ("class", "interface", "enum", "record") and IDENT.fullmatch(
                    header[j + 1]
                ):
                    name = header[j + 1]
            stack.append(("class", name) if name else ("body", None))
            boundary = i + 1
        elif t == "}":
            if stack:
                stack.pop()
            boundary = i + 1
        elif t == ";":
            boundary = i + 1
        elif t == "(" and stack and stack[-1][0] == "class" and i > boundary:
            name = values[i - 1]
            header = without_annotations(values[boundary : i - 1])
            if (
                not IDENT.fullmatch(name)
                or "=" in header
                or (i > 1 and values[i - 2] == "@")
            ):
                i += 1
                continue
            level = 1
            j = i + 1
            while j < len(values) and level:
                level += (values[j] == "(") - (values[j] == ")")
                j += 1
            k = j
            if k < len(values) and values[k] == "throws":
                while k < len(values) and values[k] not in ("{", ";"):
                    k += 1
            if level or k >= len(values) or values[k] not in ("{", ";"):
                i += 1
                continue
            names, types = parameters(values[i + 1 : j - 1])
            key = (tuple(v for kind, v in stack if kind == "class"), name, types)
            start = tokens[boundary - 1][1] + 1 if boundary else 0
            attached = [d for d in docs if start <= d[0] and d[1] <= tokens[i - 1][1]]
            tags = attached[-1][2] if attached else set()
            if key in found:
                raise ValueError("无法唯一对应重载方法 " + name)
            found[key] = (names, tags)
            mapped += len(tags)
            i = j - 1
        i += 1
    return found, mapped


def violations(old, new):
    if old == new or "@param" not in old:
        return []
    before, mapped = methods(old)
    after, _ = methods(new)
    errors = []
    if len(TAG.findall(old)) > mapped and set(TAG.findall(old)) != set(
        TAG.findall(new)
    ):
        errors.append("需复核：移除的 @param 未能对应到方法声明")
    for key, (names, tags) in before.items():
        match = key if key in after else None
        if match is None:
            # A signature edit is not deletion if there is one new declaration
            # with the same owner/name; existing overloads do not count as new.
            changed = [k for k in after if k[:2] == key[:2] and k not in before]
            if len(changed) > 1:
                errors.append("需复核：无法唯一对应签名变化 " + key[1])
                continue
            if not changed:
                continue
            match = changed[0]
        new_names, new_tags = after[match]
        for tag in tags:
            if tag in names and len(names) != len(new_names):
                if tag not in new_names:
                    continue  # This parameter was removed.
                expected = tag
            else:
                expected = new_names[names.index(tag)] if tag in names else tag
            if expected not in new_tags:
                errors.append(
                    "%s.%s 缺少 @param %s" % (".".join(key[0]), key[1], expected)
                )
    return errors


def at(ref, path):
    result = subprocess.run(
        ["git", "show", ref + ":" + path], text=True, capture_output=True
    )
    if result.returncode:
        exists = subprocess.run(
            ["git", "cat-file", "-e", ref + ":" + path], capture_output=True
        )
        if exists.returncode:
            return ""  # Added/deleted file.
        raise ValueError("无法读取 " + ref + ":" + path)
    return result.stdout


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else ""
    paths = sorted(set(p for p in sys.stdin.read().splitlines() if p.endswith(".java")))
    failures = []
    if base:
        result = subprocess.run(
            ["git", "merge-base", base, "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        )
        base = result.stdout.strip()
    for p in paths:
        pairs = (
            [(at(base, p), at("HEAD", p))]
            if base
            else [
                (at("HEAD", p), at("", p)),
                (at("", p), Path(p).read_text() if Path(p).exists() else ""),
            ]
        )
        for old, new in pairs:
            for error in violations(old, new):
                failures.append(p + ": " + error)
    for error in sorted(set(failures)):
        print(error)
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("需复核：Java 注释检查无法完成：" + str(error))
        sys.exit(2)
