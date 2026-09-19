#!/usr/bin/env python3
"""Local workflow dashboard; serves only the page and its explicit update endpoint."""
import argparse, importlib.util, json, os, secrets, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

DIRECTORY = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "dashboard_builder", DIRECTORY / "build-workflow-page.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def refresh():
    page = builder.render()
    target = DIRECTORY / "index.html"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=DIRECTORY, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(page)
        temporary.chmod(0o644)
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return page


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind="application/json"):
        if not isinstance(body, bytes):
            body = (
                json.dumps(body, ensure_ascii=False)
                if kind == "application/json"
                else body
            ).encode()
        self.send_response(status)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def local_host(self):
        return self.headers.get("Host") in {
            "127.0.0.1:" + str(self.server.server_port),
            "localhost:" + str(self.server.server_port),
        }

    def do_GET(self):
        if not self.local_host():
            self.reply(403, {"error": "仅允许本机地址"})
            return
        if urlsplit(self.path).path not in ("/", "/index.html"):
            self.reply(404, {"error": "不存在的入口"})
            return
        try:
            page = (DIRECTORY / "index.html").read_text()
            page = page.replace(
                "</head>",
                '<meta name="dashboard-token" content="'
                + self.server.token
                + '"></head>',
            )
            self.reply(200, page, "text/html")
        except OSError as exc:
            self.reply(500, {"error": str(exc)})

    def do_POST(self):
        if not self.local_host():
            self.reply(403, {"error": "仅允许本机地址"})
            return
        expected = "http://" + self.headers.get("Host", "")
        if self.headers.get("Origin") != expected or not secrets.compare_digest(
            self.headers.get("X-Dashboard-Token", ""), self.server.token
        ):
            self.reply(403, {"error": "更新请求必须来自本机看板"})
            return
        if urlsplit(self.path).path != "/api/update":
            self.reply(404, {"error": "不存在的操作"})
            return
        if self.headers.get("Content-Length", "0") != "0" or self.headers.get(
            "Transfer-Encoding"
        ):
            self.reply(400, {"error": "更新不接收文件路径或命令参数"})
            return
        try:
            refresh()
            self.reply(
                200,
                {
                    "data": builder.build_data(),
                    "prompt": (DIRECTORY / "update-prompt.txt").read_text(),
                },
            )
        except Exception as exc:
            self.reply(500, {"error": "未能生成看板：" + str(exc)})

    def log_message(self, fmt, *args):
        pass


def make_server(port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.token = secrets.token_urlsafe(32)
    return server


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--port", type=int, default=0, help="监听端口；默认由系统分配空闲端口"
    )
    a = p.parse_args()
    refresh()
    server = make_server(a.port)
    print("工作流看板：http://127.0.0.1:" + str(server.server_port) + "/", flush=True)
    print("Ctrl+C 关闭；仅更新看板文件，不执行门禁、Git 操作或任意命令。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
