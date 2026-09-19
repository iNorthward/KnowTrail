#!/usr/bin/env python3
"""Check version ownership, including detached merge snapshots; never infer a release."""
import os
from pathlib import Path
import re
import subprocess
import sys

VERSION = re.compile(r"\d+\.\d+\.\d+(?:[-.][A-Za-z0-9]+)*\Z")
PREFIX = os.environ.get("WORKFLOW_VERSION_DIR", "workflow/changes").rstrip("/") + "/"


def git(*args, allow_missing=False):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode and not allow_missing:
        raise ValueError("Git 无法核验版本上下文: " + " ".join(args))
    return result.stdout.strip() if result.returncode == 0 else None


def check(paths, base=""):
    versioned = [
        (p, p[len(PREFIX) :].split("/")[0])
        for p in paths
        if p.startswith(PREFIX) and "/" in p[len(PREFIX) :]
    ]
    if not versioned:
        return []
    branch = git("branch", "--show-current")
    explicit = os.environ.get("WORKFLOW_TARGET_VERSION", "")
    target = explicit or (branch if VERSION.fullmatch(branch) else "")
    if not VERSION.fullmatch(target):
        return [
            "版本目录变更缺少目标版本；detached/功能分支须设置 WORKFLOW_TARGET_VERSION"
        ]
    if VERSION.fullmatch(branch) and explicit and explicit != branch:
        return ["WORKFLOW_TARGET_VERSION 与当前版本分支不一致"]
    source_ref = os.environ.get("WORKFLOW_MERGE_SOURCE", "")
    source_version = source_sha = None
    if source_ref:
        # Require a named release ref, not a guessed version paired with an arbitrary SHA.
        source_version = source_ref.rsplit("/", 1)[-1]
        if not VERSION.fullmatch(source_version) or source_version == target:
            return ["WORKFLOW_MERGE_SOURCE 须为另一个版本的分支/ref"]
        source_sha = git("rev-parse", "--verify", source_ref + "^{commit}")
        merged = (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", source_sha, "HEAD"]
            ).returncode
            == 0
        )
        merging = (
            git("rev-parse", "--verify", "MERGE_HEAD", allow_missing=True) == source_sha
        )
        if not merged and not merging:
            return ["合并来源不是 HEAD 的祖先，也不是当前 MERGE_HEAD"]
    problems = []
    for path, version in versioned:
        if version == target:
            continue
        inherited = False
        if source_sha and version == source_version:
            source_entry = git("ls-tree", source_sha, "--", path)
            if source_entry:  # Do not exempt deletions of frozen files.
                if base:
                    inherited = source_entry == git("ls-tree", "HEAD", "--", path)
                else:
                    # Compare index and working tree separately; one cannot hide the other.
                    staged = subprocess.run(
                        ["git", "diff", "--quiet", source_sha, "--cached", "--", path]
                    ).returncode
                    work = subprocess.run(
                        ["git", "diff", "--quiet", source_sha, "--", path]
                    ).returncode
                    inherited = staged == work == 0
        if not inherited:
            problems.append(
                "改了非目标版本目录 %s（目标 %s）；仅允许可核验的合并来源原样继承"
                % (path, target)
            )
    return problems


if __name__ == "__main__":
    try:
        failures = check(
            [p for p in sys.stdin.read().splitlines() if p],
            sys.argv[1] if len(sys.argv) > 1 else "",
        )
    except (ValueError, OSError) as error:
        print("ERROR: " + str(error))
        sys.exit(2)
    for failure in failures:
        print("P0: " + failure)
    sys.exit(1 if failures else 0)
