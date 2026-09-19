"""Local update endpoint contracts, exercised against an isolated repository copy."""

import importlib.util, json, shutil, socket, tempfile, threading, unittest
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["workflow", "wiki", ".cursor"]:
            shutil.copytree(
                ROOT / name,
                self.root / name,
                ignore=shutil.ignore_patterns("__pycache__", "local"),
            )
        shutil.copy2(ROOT / "AGENTS.md", self.root / "AGENTS.md")
        spec = importlib.util.spec_from_file_location(
            "dashboard_test_server", self.root / "workflow/dashboard/serve.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.refresh()
        self.server = self.module.make_server(0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        self.url = "http://127.0.0.1:" + str(self.server.server_port)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path="/", method="GET", headers=None):
        try:
            with build_opener(ProxyHandler({})).open(
                Request(self.url + path, method=method, headers=headers or {})
            ) as response:
                return response.status, response.read().decode()
        except HTTPError as exc:
            return exc.code, exc.read().decode()

    def headers(self):
        return {"Origin": self.url, "X-Dashboard-Token": self.server.token}

    def test_idle_browser_connection_does_not_block_requests(self):
        idle = socket.create_connection(self.server.server_address, timeout=2)
        try:
            # A browser may connect before sending an HTTP request.
            with build_opener(ProxyHandler({})).open(self.url, timeout=2) as response:
                self.assertEqual(response.status, 200)
                response.read()
        finally:
            idle.close()

    def test_root_without_suffix_and_no_template_portal(self):
        status, page = self.request()
        self.assertEqual(status, 200)
        self.assertIn('name="dashboard-token"', page)
        self.assertNotIn('id="templates"', page)
        self.assertNotIn('href="#templates"', page)
        self.assertNotIn(
            "wiki/templates/concept.md", self.module.builder.build_data()["sources"]
        )
        self.assertEqual(self.request("/workflow/config.json")[0], 404)

    def test_update_requires_same_origin_and_session_token(self):
        self.assertEqual(self.request("/api/update", "POST")[0], 403)
        headers = self.headers()
        headers["Origin"] = "https://example.invalid"
        self.assertEqual(self.request("/api/update", "POST", headers)[0], 403)

    def test_update_returns_fresh_sources_and_prompt(self):
        p = self.root / "workflow/task-start.md"
        p.write_text(p.read_text() + "\n测试快照更新\n")
        status, body = self.request("/api/update", "POST", self.headers())
        self.assertEqual(status, 200, body)
        result = json.loads(body)
        self.assertIn(
            "测试快照更新", str(result["data"]["sources"]["workflow/task-start.md"])
        )
        self.assertEqual(
            result["prompt"],
            (self.root / "workflow/dashboard/update-prompt.txt").read_text(),
        )
        self.assertIn(
            "测试快照更新", (self.root / "workflow/dashboard/index.html").read_text()
        )

    def test_generation_failure_preserves_last_page(self):
        page = self.root / "workflow/dashboard/index.html"
        before = page.read_bytes()
        (self.root / "workflow/dashboard/page.template.html").unlink()
        status, body = self.request("/api/update", "POST", self.headers())
        self.assertEqual(status, 500, body)
        self.assertNotIn('"prompt"', body)
        self.assertEqual(page.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
