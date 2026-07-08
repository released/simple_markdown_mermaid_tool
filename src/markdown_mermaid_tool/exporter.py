from __future__ import annotations

import base64
import html
import json
import os
import secrets
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .settings import AppState, sanitize_output_name


MARKED_CDN = "https://cdn.jsdelivr.net/npm/marked/marked.min.js"
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"
DEFAULT_VIEWPORT_WIDTH = 1440
DEFAULT_VIEWPORT_HEIGHT = 1200
MAX_PDF_PAGE_INCHES = 200.0


@dataclass
class GeneratedFile:
    format: str
    path: str


@dataclass
class GenerateResult:
    outputs: list[GeneratedFile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, object]:
        return {
            "outputs": [{"format": item.format, "path": item.path} for item in self.outputs],
            "warnings": self.warnings,
        }


class BrowserRenderError(RuntimeError):
    pass


def find_browser_executable() -> str | None:
    env_path = os.environ.get("MARKDOWN_MERMAID_BROWSER", "").strip()
    if env_path and Path(env_path).is_file():
        return env_path

    for name in ("msedge.exe", "chrome.exe", "chromium.exe"):
        found = shutil.which(name)
        if found:
            return found

    candidates = [
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def generate_outputs(state: AppState, markdown_text: str, static_dir: Path, base_dir: Path) -> GenerateResult:
    result = GenerateResult()
    output_dir = _resolve_output_dir(state, base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = sanitize_output_name(state.output_name)
    formats = state.formats
    if not formats.any_selected():
        formats.html = True
        result.warnings.append("No output format was selected; HTML was enabled.")

    html_text = build_export_html(markdown_text, output_name, static_dir)
    html_path = output_dir / f"{output_name}.html"

    with tempfile.TemporaryDirectory(prefix="markdown_mermaid_") as temp_root:
        temp_dir = Path(temp_root)
        render_html_path = html_path if formats.html else temp_dir / f"{output_name}.html"
        _write_text(render_html_path, html_text)

        if formats.html:
            result.outputs.append(GeneratedFile("html", str(html_path)))

        browser_needed = formats.pdf or formats.png or formats.jpg
        browser = find_browser_executable() if browser_needed else None
        if browser_needed and not browser:
            if not formats.html:
                _write_text(html_path, html_text)
                result.outputs.append(GeneratedFile("html", str(html_path)))
            result.warnings.append("PDF/PNG/JPG output needs Microsoft Edge or Google Chrome.")
            return result

        if browser_needed and browser:
            try:
                _render_browser_outputs(browser, render_html_path, output_dir, output_name, formats, result)
            except BrowserRenderError as exc:
                result.warnings.append(str(exc))

    return result


def build_export_html(markdown_text: str, title: str, static_dir: Path) -> str:
    export_css = _read_optional(static_dir / "export.css")
    renderer_js = _read_optional(static_dir / "renderer.js")
    marked_tag = _script_tag(static_dir / "vendor" / "marked.min.js", MARKED_CDN)
    mermaid_tag = _script_tag(static_dir / "vendor" / "mermaid.min.js", MERMAID_CDN)
    title_text = title or "markdown_export"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title_text)}</title>
  <style>{export_css}</style>
  {marked_tag}
  {mermaid_tag}
</head>
<body>
  <main id="preview" class="markdown-body"></main>
  <script>{renderer_js}</script>
  <script>
    window.__MARKDOWN_SOURCE__ = {json.dumps(markdown_text)};
    window.addEventListener("DOMContentLoaded", async function () {{
      const target = document.getElementById("preview");
      if (window.MarkdownMermaidRenderer) {{
        await window.MarkdownMermaidRenderer.render(window.__MARKDOWN_SOURCE__, target);
      }}
      document.body.setAttribute("data-render-ready", "1");
    }});
  </script>
</body>
</html>
"""


def _render_browser_outputs(browser: str, html_path: Path, output_dir: Path, output_name: str, formats: object, result: GenerateResult) -> None:
    with BrowserPage(browser, html_path) as page:
        metrics = page.measure_content()
        if getattr(formats, "pdf", False):
            pdf_path = output_dir / f"{output_name}.pdf"
            warnings = page.save_pdf(pdf_path, metrics)
            result.outputs.append(GeneratedFile("pdf", str(pdf_path)))
            result.warnings.extend(warnings)
        if getattr(formats, "png", False):
            png_path = output_dir / f"{output_name}.png"
            page.save_screenshot(png_path, "png", metrics)
            result.outputs.append(GeneratedFile("png", str(png_path)))
        if getattr(formats, "jpg", False):
            jpg_path = output_dir / f"{output_name}.jpg"
            page.save_screenshot(jpg_path, "jpeg", metrics, quality=92)
            result.outputs.append(GeneratedFile("jpg", str(jpg_path)))


class BrowserPage:
    def __init__(self, browser: str, html_path: Path) -> None:
        self.browser = browser
        self.html_path = html_path
        self.process: subprocess.Popen[str] | None = None
        self.profile_dir: tempfile.TemporaryDirectory[str] | None = None
        self.ws: WebSocketClient | None = None
        self.cdp: CdpClient | None = None
        self.port = 0

    def __enter__(self) -> "BrowserPage":
        self.profile_dir = tempfile.TemporaryDirectory(prefix="markdown_mermaid_browser_")
        self.port = _free_local_port()
        uri = self.html_path.resolve().as_uri()
        cmd = [
            self.browser,
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--allow-file-access-from-files",
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile_dir.name}",
            "about:blank",
        ]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        ws_url = _wait_for_page_websocket_url(self.port)
        self.ws = WebSocketClient(ws_url)
        self.cdp = CdpClient(self.ws)
        self.cdp.call("Page.enable", timeout_s=10)
        self.cdp.call("Runtime.enable", timeout_s=10)
        self.cdp.call("Page.navigate", {"url": uri}, timeout_s=10)
        self._wait_render_ready()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.ws is not None:
            self.ws.close()
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.profile_dir is not None:
            self.profile_dir.cleanup()

    def measure_content(self) -> dict[str, int]:
        cdp = self._cdp()
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": DEFAULT_VIEWPORT_WIDTH,
                "height": DEFAULT_VIEWPORT_HEIGHT,
                "deviceScaleFactor": 1,
                "mobile": False,
            },
            timeout_s=10,
        )
        self._wait_render_ready()
        initial = self._measure_once()
        width = max(DEFAULT_VIEWPORT_WIDTH, int(initial["width"]))
        height = max(DEFAULT_VIEWPORT_HEIGHT, int(initial["height"]))
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": min(height, 8192),
                "deviceScaleFactor": 1,
                "mobile": False,
            },
            timeout_s=10,
        )
        time.sleep(0.2)
        measured = self._measure_once()
        return {
            "width": max(DEFAULT_VIEWPORT_WIDTH, int(measured["width"])),
            "height": max(DEFAULT_VIEWPORT_HEIGHT, int(measured["height"])),
        }

    def save_screenshot(self, path: Path, image_format: str, metrics: dict[str, int], quality: int | None = None) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        params: dict[str, object] = {
            "format": image_format,
            "fromSurface": True,
            "captureBeyondViewport": True,
            "clip": {
                "x": 0,
                "y": 0,
                "width": metrics["width"],
                "height": metrics["height"],
                "scale": 1,
            },
        }
        if quality is not None:
            params["quality"] = quality
        result = self._cdp().call("Page.captureScreenshot", params, timeout_s=120)
        data = result.get("data")
        if not isinstance(data, str) or not data:
            raise BrowserRenderError(f"{image_format.upper()} screenshot generation failed.")
        path.write_bytes(base64.b64decode(data))

    def save_pdf(self, path: Path, metrics: dict[str, int]) -> list[str]:
        path.parent.mkdir(parents=True, exist_ok=True)
        warnings: list[str] = []
        paper_width = max(1.0, metrics["width"] / 96.0)
        paper_height = max(1.0, metrics["height"] / 96.0)
        if paper_width > MAX_PDF_PAGE_INCHES:
            paper_width = MAX_PDF_PAGE_INCHES
            warnings.append("PDF content width exceeds Chromium single-page limit; PDF may scale or paginate.")
        if paper_height > MAX_PDF_PAGE_INCHES:
            paper_height = MAX_PDF_PAGE_INCHES
            warnings.append("PDF content height exceeds Chromium single-page limit; PDF may paginate.")
        result = self._cdp().call(
            "Page.printToPDF",
            {
                "printBackground": True,
                "paperWidth": paper_width,
                "paperHeight": paper_height,
                "marginTop": 0,
                "marginBottom": 0,
                "marginLeft": 0,
                "marginRight": 0,
                "scale": 1,
                "preferCSSPageSize": False,
            },
            timeout_s=120,
        )
        data = result.get("data")
        if not isinstance(data, str) or not data:
            raise BrowserRenderError("PDF generation failed.")
        path.write_bytes(base64.b64decode(data))
        return warnings

    def _wait_render_ready(self) -> None:
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            try:
                result = self._cdp().call(
                    "Runtime.evaluate",
                    {
                        "expression": "document.body && document.body.getAttribute('data-render-ready') === '1'",
                        "returnByValue": True,
                    },
                    timeout_s=5,
                )
                if result.get("result", {}).get("value") is True:
                    time.sleep(0.3)
                    return
            except BrowserRenderError:
                pass
            time.sleep(0.2)
        raise BrowserRenderError("Timed out while waiting for Markdown/Mermaid rendering.")

    def _measure_once(self) -> dict[str, object]:
        return self._evaluate_json(
            r"""
(() => {
  const doc = document.documentElement;
  const body = document.body;
  const preview = document.getElementById("preview");
  let right = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0, window.innerWidth);
  let bottom = Math.max(doc.scrollHeight, body ? body.scrollHeight : 0, window.innerHeight);
  const scan = (node) => {
    if (!node) return;
    const rect = node.getBoundingClientRect();
    const x = Math.ceil(rect.left + window.scrollX);
    const y = Math.ceil(rect.top + window.scrollY);
    right = Math.max(right, Math.ceil(rect.right + window.scrollX), x + node.scrollWidth);
    bottom = Math.max(bottom, Math.ceil(rect.bottom + window.scrollY), y + node.scrollHeight);
  };
  scan(preview);
  document.querySelectorAll("svg, .mermaid").forEach(scan);
  return {
    width: Math.max(320, Math.ceil(right + 8)),
    height: Math.max(320, Math.ceil(bottom + 8))
  };
})()
""",
            timeout_s=10,
        )

    def _evaluate_json(self, expression: str, timeout_s: int) -> dict[str, object]:
        result = self._cdp().call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
            timeout_s=timeout_s,
        )
        value = result.get("result", {}).get("value")
        if not isinstance(value, dict):
            raise BrowserRenderError("Browser measurement failed.")
        return value

    def _cdp(self) -> "CdpClient":
        if self.cdp is None:
            raise BrowserRenderError("Browser is not connected.")
        return self.cdp


class CdpClient:
    def __init__(self, ws: "WebSocketClient") -> None:
        self.ws = ws
        self.next_id = 1

    def call(self, method: str, params: dict[str, object] | None = None, timeout_s: int = 30) -> dict[str, object]:
        message_id = self.next_id
        self.next_id += 1
        payload: dict[str, object] = {"id": message_id, "method": method}
        if params is not None:
            payload["params"] = params
        self.ws.send_text(json.dumps(payload, separators=(",", ":")))
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            text = self.ws.receive_text(max(0.1, deadline - time.monotonic()))
            try:
                message = json.loads(text)
            except json.JSONDecodeError:
                continue
            if message.get("id") != message_id:
                continue
            if "error" in message:
                raise BrowserRenderError(f"{method} failed: {message['error']}")
            result = message.get("result", {})
            if isinstance(result, dict):
                return result
            return {}
        raise BrowserRenderError(f"{method} timed out.")


class WebSocketClient:
    def __init__(self, ws_url: str) -> None:
        parsed = urlparse(ws_url)
        if parsed.scheme != "ws" or not parsed.hostname or not parsed.port:
            raise BrowserRenderError(f"Unsupported DevTools WebSocket URL: {ws_url}")
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
        self.path = parsed.path
        if parsed.query:
            self.path += "?" + parsed.query
        self.host = f"{parsed.hostname}:{parsed.port}"
        self._handshake()

    def close(self) -> None:
        try:
            self._send_frame(b"", opcode=0x8)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass

    def send_text(self, text: str) -> None:
        self._send_frame(text.encode("utf-8"), opcode=0x1)

    def receive_text(self, timeout_s: float) -> str:
        self.sock.settimeout(timeout_s)
        fragments: list[bytes] = []
        while True:
            opcode, payload, fin = self._read_frame()
            if opcode == 0x8:
                raise BrowserRenderError("DevTools WebSocket closed.")
            if opcode == 0x9:
                self._send_frame(payload, opcode=0xA)
                continue
            if opcode in (0x1, 0x0):
                fragments.append(payload)
                if fin:
                    return b"".join(fragments).decode("utf-8")

    def _handshake(self) -> None:
        key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        self.sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk
        status_line = response.split(b"\r\n", 1)[0]
        if b" 101 " not in status_line:
            raise BrowserRenderError("DevTools WebSocket handshake failed.")

    def _send_frame(self, payload: bytes, opcode: int) -> None:
        first = 0x80 | opcode
        length = len(payload)
        mask = secrets.token_bytes(4)
        if length < 126:
            header = struct.pack("!BB", first, 0x80 | length)
        elif length < 65536:
            header = struct.pack("!BBH", first, 0x80 | 126, length)
        else:
            header = struct.pack("!BBQ", first, 0x80 | 127, length)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def _read_frame(self) -> tuple[int, bytes, bool]:
        header = self._read_exact(2)
        first, second = header
        fin = (first & 0x80) != 0
        opcode = first & 0x0F
        masked = (second & 0x80) != 0
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
        mask = self._read_exact(4) if masked else b""
        payload = self._read_exact(length) if length else b""
        if masked:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        return opcode, payload, fin

    def _read_exact(self, size: int) -> bytes:
        data = b""
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise BrowserRenderError("DevTools WebSocket connection ended.")
            data += chunk
        return data


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_page_websocket_url(port: int) -> str:
    deadline = time.monotonic() + 15.0
    url = f"http://127.0.0.1:{port}/json/list"
    last_error = ""
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                targets = json.loads(response.read().decode("utf-8"))
            for target in targets:
                if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
                    return str(target["webSocketDebuggerUrl"])
        except Exception as exc:
            last_error = str(exc)
        time.sleep(0.2)
    raise BrowserRenderError(f"Cannot connect to browser DevTools endpoint: {last_error}")


def _resolve_output_dir(state: AppState, base_dir: Path) -> Path:
    if state.output_dir:
        output_dir = Path(state.output_dir).expanduser()
        if output_dir.is_absolute():
            return output_dir
        return base_dir / output_dir
    if state.md_path:
        md_parent = Path(state.md_path).expanduser().parent
        if str(md_parent):
            return md_parent
    return base_dir / "output"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _read_optional(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _script_tag(path: Path, fallback_url: str) -> str:
    script = _read_optional(path)
    if script:
        script = script.replace("</script>", "<\\/script>")
        return f"<script>{script}</script>"
    return f'<script src="{html.escape(fallback_url)}"></script>'
