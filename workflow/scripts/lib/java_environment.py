"""Respect explicit Java selection. Never discover or switch installed JDKs."""

import os, re, shutil, subprocess
from pathlib import Path


def build_environment(version=None, require_java=True):
    env = os.environ.copy()
    selected = env.get("WORKFLOW_JAVA_HOME") or env.get("JAVA_HOME")
    if selected:
        directory = Path(selected) / "bin"
        env["JAVA_HOME"] = selected
        env["PATH"] = str(directory) + os.pathsep + env.get("PATH", "")
    if not require_java and version is None and not env.get("WORKFLOW_JAVA_HOME"):
        return env  # Custom command may use a container or its own toolchain.
    versions = []
    for tool in ("java", "javac"):
        if selected:
            binary = Path(selected) / "bin" / tool
            if not binary.is_file():
                binary = binary.with_suffix(".exe")
            if not binary.is_file():
                raise ValueError("指定 JDK 缺少 " + tool + ": " + selected)
            binary = str(binary)
        else:
            binary = shutil.which(tool, path=env.get("PATH"))
            if not binary:
                raise ValueError(
                    "当前环境找不到 "
                    + tool
                    + "；请配置 JAVA_HOME 或 WORKFLOW_JAVA_HOME"
                )
        result = subprocess.run(
            [binary, "-version"], env=env, text=True, capture_output=True
        )
        output = result.stdout + "\n" + result.stderr
        match = re.search(r'(?:version\s+"?|javac\s+)(\d+)(?:\.(\d+))?', output)
        if result.returncode or not match:
            raise ValueError("无法确认 " + tool + " 版本: " + output.strip())
        major = int(match[2]) if match[1] == "1" and match[2] else int(match[1])
        versions.append(major)
    if versions[0] != versions[1]:
        raise ValueError("java 与 javac 主版本不同；请明确指定同一 JDK")
    if version is not None and versions[0] != version:
        raise ValueError(
            "当前 JDK "
            + str(versions[0])
            + " 与 java_version="
            + str(version)
            + " 不符；不会自动切换 JDK"
        )
    print("build JDK:", versions[0], selected or "PATH", flush=True)
    return env
