"""Exercise the workflow itself, with no installer or external project mutation."""

import importlib.util, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workflow/scripts/lib"))
sys.path.insert(0, str(ROOT / "workflow/scripts/wiki"))
spec = importlib.util.spec_from_file_location(
    "wiki_format", ROOT / "workflow/scripts/wiki/lint-wiki-format.py"
)
fmt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fmt)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["wiki", "workflow", ".cursor/rules"]:
            shutil.copytree(
                ROOT / name,
                self.root / name,
                ignore=shutil.ignore_patterns("__pycache__"),
            )
        for name in ["AGENTS.md", "README.md", ".gitignore"]:
            shutil.copy2(ROOT / name, self.root / name)

    def run_(self, *args):
        return subprocess.run(args, cwd=self.root, text=True, capture_output=True)

    def git(self, *args):
        p = self.run_("git", *args)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def init(self):
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")

    def errors(self):
        return fmt.validate(self.root, self.root / "wiki")

    def test_unrecognized_paths_still_require_semantic_review(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "测试基线")
        (self.root / "pom.xml").write_text("<project/>")
        for name in ("src/main/java/domain/RecordDO.java",
                     "src/main/java/task/xxljob/RunTask.java",
                     "src/main/resources/mybatis/user_account.xml"):
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("<mapper/>" if name.endswith(".xml") else "class Example {}")
        out = self.run_("bash", "workflow/scripts/audit/audit-change-scope.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("SEMANTIC_REVIEW=pending", out.stdout)
        self.assertNotIn("TRIGGER_SECURITY=", out.stdout)
        self.assertNotIn("TRIGGER_BUGBOT=", out.stdout)
        self.assertNotIn("SKIP_SUBAGENT=", out.stdout)
        self.assertIn("COMPILE_MODULES=.", out.stdout)

    def test_semantic_review_status_does_not_fake_completion(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "测试基线")
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("SEMANTIC_REVIEW=no_changes", out.stdout)
        p = self.root / "wiki/system/README.md"
        p.write_text(p.read_text() + "\n补充范围说明。\n")
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("SEMANTIC_REVIEW=pending", out.stdout)
        self.assertIn("COMPILE=skip", out.stdout)

    def test_wiki_complies(self):
        self.assertEqual(self.errors(), [])

    def test_wrong_heading_is_rejected(self):
        p = self.root / "wiki/system/README.md"
        p.write_text(p.read_text().replace("## 核心规则", "## 概述"))
        self.assertTrue(any("二级章节" in e for e in self.errors()))

    def test_missing_source_is_rejected(self):
        p = self.root / "wiki/system/README.md"
        p.write_text(p.read_text().replace("wiki/templates/schema.json", "missing.mdc"))
        p.write_text(fmt.rendered_document(p.read_text(), p, self.root))
        self.assertTrue(any("来源文件不存在" in e for e in self.errors()))

    def test_unknown_exception_is_rejected(self):
        p = self.root / "wiki/system/README.md"
        p.write_text(p.read_text().replace("type: concept", "type: special"))
        p.write_text(fmt.rendered_document(p.read_text(), p, self.root))
        self.assertTrue(any("未知专题类型" in e for e in self.errors()))

    def test_format_failure_reaches_finish(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        p = self.root / "wiki/system/README.md"
        p.write_text(p.read_text().replace("## 核心规则", "## 概述"))
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertNotEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("LINT_WIKI_FORMAT=fail", out.stdout)

    def test_maven_compile_after_path_move(self):
        self.init()
        (self.root / "pom.xml").write_text(
            "<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>core-check</artifactId><version>1</version><properties><maven.compiler.source>8</maven.compiler.source><maven.compiler.target>8</maven.compiler.target></properties></project>"
        )
        p = self.root / "src/main/java/example/Example.java"
        p.parent.mkdir(parents=True)
        p.write_text(
            "package example; public class Example { public int value() { return 1; } }"
        )
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertTrue((self.root / "target/classes/example/Example.class").is_file())

    def test_html_sources_and_gate_order(self):
        script = self.root / "workflow/dashboard/build-workflow-page.py"
        out = self.run_("python3", str(script))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        import re

        page = (self.root / "workflow/dashboard/index.html").read_text()
        data = json.loads(
            re.search(
                r'<script type="application/json" id="workflow-data">(.*?)</script>',
                page,
                re.S,
            )[1]
        )
        self.assertIn("lint-wiki-format.sh", data["chains"]["local"])
        self.assertIn("workflow/task-start.md", data["sources"])
        for path in re.findall(r'data-source="([^"]+)"', page):
            if "${" not in path:
                self.assertIn(path, data["sources"])
        self.assertIn('data-source="${esc(path)}"', page)

    def test_preview_metadata_is_visible_and_consistent(self):
        p = self.root / "wiki/README.md"
        text = p.read_text()
        self.assertIn("# 项目知识库", text)
        self.assertIn("| module | system |", text)
        self.assertIn("| sources |", text)
        p.write_text(text.replace("title: 项目知识库", "title: 新知识库", 1))
        self.assertTrue(any("预览信息区未同步" in e for e in self.errors()))
        out = self.run_("python3", "workflow/scripts/wiki/wiki_metadata.py", "--write")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("# 新知识库", p.read_text())
        self.assertEqual(self.errors(), [])

    def test_project_preferences_do_not_become_gates(self):
        self.init()
        p = self.root / "Choice.java"
        p.write_text(
            "class Choice {\n/** @param value existing */\nvoid set(int value) {}\n}"
        )
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        text = (
            p.read_text()
            + "\nclass QueryWrapper {}\nclass ItemEntity {}\nclass ItemDTO extends ItemEntity { QueryWrapper query = new QueryWrapper(); }\n"
        )
        p.write_text(text)
        out = self.run_("bash", "workflow/scripts/java/lint-agent-diff.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        p.write_text(text.replace("/** @param value existing */", ""))
        out = self.run_("bash", "workflow/scripts/java/lint-agent-diff.sh")
        self.assertNotEqual(out.returncode, 0)

    def test_optional_review_failure_does_not_block_finish(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        p = self.root / "workflow/scripts/wiki/lint-wiki-stale.sh"
        p.write_text("#!/usr/bin/env bash\nexit 2\n")
        p = self.root / "wiki/system/README.md"
        p.write_text(
            fmt.rendered_document(p.read_text() + "\n复核测试说明。\n", p, self.root)
        )
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("LINT_WIKI_STALE=warn", out.stdout)

    def test_old_wiki_is_optional_and_never_blocks(self):
        p = self.root / "wiki/system/README.md"
        p.write_text(
            p.read_text().replace("updated: 2026-09-19", "updated: 2000-01-01")
        )
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-stale.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("SKIP", out.stdout)
        cfg = self.root / "workflow/config.json"
        data = json.loads(cfg.read_text())
        data["wiki_review_days"] = 90
        cfg.write_text(json.dumps(data))
        before = p.read_bytes()
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-stale.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("不是错误，不阻断", out.stdout)
        self.assertNotIn("P2", out.stdout)
        self.assertEqual(p.read_bytes(), before)

    def test_http_hint_outside_controller_and_conditional_scope(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        cfg = self.root / "workflow/config.json"
        data = json.loads(cfg.read_text())
        data["build_command"] = [sys.executable, "-c", "pass"]
        cfg.write_text(json.dumps(data))
        (self.root / "Endpoint.java").write_text(
            'class Endpoint { @GetMapping("/example") void call() {} }'
        )
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("HTTP_PATH_CHANGED:", out.stdout)
        self.assertIn("LINT_HTTP=ok", out.stdout)
        self.assertIn("鉴权或数据范围变化时才", out.stdout)

    def test_schema_gate_is_opt_in(self):
        out = self.run_("bash", "workflow/scripts/sql/lint-schema-wiki.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("SKIP", out.stdout)

    def test_sql_example_is_opt_in(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        p = self.root / "workflow/changes/arbitrary/change.sql"
        p.parent.mkdir(parents=True)
        p.write_text("SELECT 1;")
        out = self.run_("bash", "workflow/scripts/sql/lint-version-sql.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("SKIP", out.stdout)
        cfg = self.root / "workflow/config.json"
        data = json.loads(cfg.read_text())
        data["packs"].append("version-sql")
        cfg.write_text(json.dumps(data))
        out = self.run_("bash", "workflow/scripts/sql/lint-version-sql.sh")
        self.assertNotEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_mixed_guide_and_script_change_checks_format(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        p = self.root / "workflow/guides/wiki-doc-template.md"
        p.write_text(p.read_text().replace("## 适用场景", "## 错误章节"))
        p = self.root / "workflow/scripts/java/java_checks.py"
        p.write_text(p.read_text() + "\n# changed\n")
        out = self.run_("bash", "workflow/scripts/finish-audit.sh")
        self.assertNotEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("LINT_WIKI_FORMAT=fail", out.stdout)

    def test_wiki_index_accepts_unicode_alias_and_anchor(self):
        p = self.root / "wiki/订单/说明.md"
        p.parent.mkdir()
        p.write_text("test")
        index = self.root / "wiki/index.md"
        index.write_text(index.read_text() + "\n[[订单/说明#范围|订单说明]]\n")
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-index.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        index.write_text(index.read_text() + "\n[[订单/不存在|失效链接]]\n")
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-index.sh")
        self.assertNotEqual(out.returncode, 0)

    def test_all_bugfix_symptoms_must_be_registered(self):
        p = self.root / "wiki/common/example.md"
        p.write_text(
            '---\ntitle: 测试\ntype: bugfix\nsymptoms:\n  - "超时"\n  - "重复请求"\n---\n'
        )
        index = self.root / "wiki/index.md"
        index.write_text(index.read_text() + "\n超时 [[common/example|说明]]\n")
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-symptoms.sh")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("重复请求", out.stdout)
        index.write_text(
            index.read_text() + "\n重复请求 [[common/example#回归|回归]]\n"
        )
        out = self.run_("bash", "workflow/scripts/wiki/lint-wiki-symptoms.sh")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_frontmatter_accepts_inline_separator(self):
        p = self.root / "wiki/README.md"
        p.write_text(p.read_text().replace("title: 项目知识库", "title: 项目---知识库"))
        out = self.run_("python3", "workflow/scripts/wiki/wiki_metadata.py", "--write")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("# 项目---知识库", p.read_text())
        self.assertEqual(self.errors(), [])

    def test_branch_audit_rejects_implicit_head_baseline(self):
        self.init()
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        out = self.run_(
            "bash", "workflow/scripts/audit/audit-change-scope.sh", "--scope=branch"
        )
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("--base", out.stderr)
        base = self.git("rev-parse", "HEAD").strip()
        out = self.run_(
            "bash", "workflow/scripts/audit/audit-change-scope.sh", "--base=" + base
        )
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_http_multiline_argument_change_is_reported(self):
        self.init()
        p = self.root / "Endpoint.java"
        p.write_text(
            'class Endpoint { @GetMapping(\n value="/old)",\n produces="application/json"\n) void get() {} }'
        )
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        p.write_text(p.read_text().replace("/old)", "/new)"))
        out = self.run_("bash", "workflow/scripts/java/lint-http-paths.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("HTTP_PATH_CHANGED:", out.stdout)
        self.assertIn("/new)", out.stdout)


if __name__ == "__main__":
    unittest.main()
