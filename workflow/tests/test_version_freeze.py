"""Run the release guard against real, disposable Git histories."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sql/lint-version-freeze.py"


class VersionFreezeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q", "-b", "1.0.3")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.path = "workflow/changes/1.0.2/changes.sql"
        f = self.root / self.path
        f.parent.mkdir(parents=True)
        f.write_text("-- original\n")
        self.commit()
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args):
        p = subprocess.run(
            ["git", *args], cwd=self.root, text=True, capture_output=True, check=True
        )
        return p.stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")

    def check(self, base="", **env):
        environ = {
            k: v
            for k, v in os.environ.items()
            if k not in ["WORKFLOW_TARGET_VERSION", "WORKFLOW_MERGE_SOURCE"]
        }
        environ.update(env)
        return subprocess.run(
            ["python3", str(SCRIPT), base],
            input=self.path + "\n",
            cwd=self.root,
            env=environ,
            text=True,
            capture_output=True,
        )

    def merge_source(self):
        self.git("checkout", "-qb", "1.0.2")
        (self.root / self.path).write_text("-- source\n")
        self.commit()
        self.git("checkout", "-q", "1.0.3")
        self.git("merge", "--no-ff", "-qm", "merge", "1.0.2")

    def test_old_version_change_is_rejected(self):
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("1.0.3", r.stdout)
        self.assertNotIn("unbound", r.stderr)

    def test_target_version_allowed(self):
        self.path = "workflow/changes/1.0.3/new.sql"
        self.assertEqual(self.check().returncode, 0)

    def test_detached_requires_version(self):
        self.git("checkout", "--detach", "-q")
        self.assertEqual(self.check().returncode, 1)
        self.assertEqual(self.check(WORKFLOW_TARGET_VERSION="1.0.3").returncode, 1)
        self.path = "workflow/changes/1.0.3/new.sql"
        self.assertEqual(self.check(WORKFLOW_TARGET_VERSION="1.0.3").returncode, 0)

    def test_cannot_override_release_branch(self):
        self.assertEqual(self.check(WORKFLOW_TARGET_VERSION="1.0.2").returncode, 1)

    def test_merge_inheritance_and_extra_edit(self):
        self.merge_source()
        self.git("checkout", "--detach", "-q")
        env = {"WORKFLOW_TARGET_VERSION": "1.0.3", "WORKFLOW_MERGE_SOURCE": "1.0.2"}
        self.assertEqual(self.check(self.base, **env).returncode, 0)
        (self.root / self.path).write_text("-- added after merge\n")
        self.commit()
        self.assertEqual(self.check(self.base, **env).returncode, 1)

    def test_staged_bad_worktree_good_cannot_hide(self):
        self.merge_source()
        env = {"WORKFLOW_MERGE_SOURCE": "1.0.2"}
        self.assertEqual(self.check(**env).returncode, 0)
        (self.root / self.path).write_text("-- changed\n")
        self.git("add", self.path)
        (self.root / self.path).write_text("-- source\n")
        self.assertEqual(self.check(**env).returncode, 1)

    def test_unmerged_source_rejected(self):
        self.git("checkout", "-qb", "1.0.2")
        (self.root / self.path).write_text("-- source\n")
        self.commit()
        self.git("checkout", "-q", "1.0.3")
        self.assertEqual(self.check(WORKFLOW_MERGE_SOURCE="1.0.2").returncode, 1)

    def test_deleted_frozen_file_rejected(self):
        self.merge_source()
        self.git("rm", self.path)
        self.commit()
        self.assertEqual(
            self.check(self.base, WORKFLOW_MERGE_SOURCE="1.0.2").returncode, 1
        )


if __name__ == "__main__":
    unittest.main()
