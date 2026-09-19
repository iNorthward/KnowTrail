"""Verify configurable builds without depending on installed JDK versions."""

import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/lib"))
from java_environment import build_environment
from workflow_support import compile_module, audit


class BuildEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def jdk(self, major):
        root = self.root / ("jdk " + str(major))
        (root / "bin").mkdir(parents=True)
        for tool in ["java", "javac"]:
            p = root / "bin" / tool
            version = "1.8.0" if major == 8 else str(major) + ".0.1"
            line = (
                ('openjdk version "' + version + '"')
                if tool == "java"
                else "javac " + version
            )
            p.write_text("#!/bin/sh\nprintf '%s\\n' '" + line + "'\n")
            p.chmod(0o755)
        return str(root)

    def config(self, **values):
        (self.root / "workflow").mkdir(exist_ok=True)
        (self.root / "workflow/config.json").write_text(json.dumps(values))

    def test_current_jdk_8_11_17_21_and_exact_version(self):
        for major in [8, 11, 17, 21]:
            with (
                self.subTest(major=major),
                patch.dict(
                    os.environ, {"JAVA_HOME": self.jdk(major), "WORKFLOW_JAVA_HOME": ""}
                ),
            ):
                env = build_environment(major)
                self.assertEqual(env["JAVA_HOME"], os.environ["JAVA_HOME"])
                with self.assertRaises(ValueError):
                    build_environment(major + 1)

    def test_explicit_invalid_jdk_does_not_fallback(self):
        with patch.dict(
            os.environ,
            {
                "JAVA_HOME": self.jdk(17),
                "WORKFLOW_JAVA_HOME": str(self.root / "missing"),
            },
        ):
            with self.assertRaises(ValueError):
                build_environment()

    def test_custom_build_no_maven_flags_and_failure_propagates(self):
        self.config(build_command=[sys.executable, "-c", "import sys;sys.exit(7)"])
        with patch.dict(
            os.environ, {"JAVA_HOME": "/missing", "WORKFLOW_JAVA_HOME": ""}
        ):
            self.assertEqual(compile_module(self.root, "."), 7)

    def test_wrapper_wins_and_receives_selected_environment(self):
        self.config(java_version=11)
        (self.root / "pom.xml").write_text("<project/>")
        wrapper = self.root / "mvnw"
        wrapper.write_text(
            '#!/bin/sh\nprintf \'%s\\n\' "$JAVA_HOME" "$@" > wrapper-result\n'
        )
        wrapper.chmod(0o755)
        selected = self.jdk(11)
        with patch.dict(os.environ, {"JAVA_HOME": selected, "WORKFLOW_JAVA_HOME": ""}):
            self.assertEqual(compile_module(self.root, "."), 0)
        self.assertEqual(
            (self.root / "wrapper-result").read_text().splitlines(),
            [selected, "compile"],
        )

    def test_gradle_changes_use_custom_command_without_pom(self):
        self.config(build_command=[sys.executable, "-c", "pass"])
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "build.gradle.kts").write_text("// project build")
        self.assertEqual(audit(self.root)["COMPILE_MODULES"], ".")

    def test_unsupported_build_is_not_silently_skipped(self):
        self.config()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "build.gradle").write_text("// build")
        with self.assertRaises(ValueError):
            audit(self.root)


if __name__ == "__main__":
    unittest.main()
