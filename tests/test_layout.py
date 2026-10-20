from __future__ import annotations

import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from markdown_mermaid_tool import app_server  # noqa: E402


class SourceLayoutTests(unittest.TestCase):
    def test_source_resources_and_http(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(app_server, "runtime_base_dir", return_value=Path(temporary)):
                context = app_server.AppContext()
            self.assertTrue((context.static_dir / "index.html").is_file())
            server = app_server._bind_server(
                "127.0.0.1", 0, app_server._make_handler(context)
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}"
                for route in ("/", "/static/app.js", "/static/styles.css", "/api/state"):
                    with self.subTest(route=route), urlopen(url + route, timeout=5) as response:
                        self.assertEqual(response.status, 200)
                        self.assertTrue(response.read())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    @unittest.skipUnless(os.environ.get("PC_TOOL_TEST_EXE") == "1", "EXE smoke is opt-in")
    def test_packaged_resources_and_http(self) -> None:
        executable = ROOT / "build" / "MarkdownMermaidTool.exe"
        self.assertTrue(executable.is_file())
        with tempfile.TemporaryDirectory() as temporary:
            isolated_exe = Path(temporary) / executable.name
            shutil.copy2(executable, isolated_exe)
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            process = subprocess.Popen(
                [str(isolated_exe), "--no-open", "--port", str(port)],
                cwd=temporary,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                deadline = time.monotonic() + 20
                while True:
                    self.assertIsNone(process.poll(), "Packaged executable exited early")
                    try:
                        with urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
                            self.assertEqual(response.status, 200)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            self.fail("Packaged executable did not serve its embedded UI")
                        time.sleep(0.1)
                with urlopen(f"http://127.0.0.1:{port}/static/app.js", timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(response.read())
            finally:
                # Only terminate the isolated child owned by this test; never
                # close an existing user instance or write its configuration.
                if os.name == "nt" and process.poll() is None:
                    # A PyInstaller one-file bootloader owns a second process.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                elif process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
