from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .exporter import find_browser_executable, generate_outputs
from .settings import (
    AppState,
    default_ini_path,
    default_output_dir,
    derive_output_name,
    load_state_from_ini,
    runtime_base_dir,
    save_state_to_ini,
)


class AppContext:
    def __init__(self) -> None:
        self.base_dir = runtime_base_dir()
        self.static_dir = _static_dir()
        self.state = AppState.default(self.base_dir)
        self.lock = threading.Lock()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simple Markdown Mermaid Tool")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args(argv)

    context = AppContext()
    handler = _make_handler(context)
    httpd = _bind_server(args.host, args.port, handler)
    host, port = httpd.server_address[:2]
    url = f"http://{host}:{port}/"

    print(f"Simple Markdown Mermaid Tool: {url}")
    print(f"Base directory: {context.base_dir}")
    if find_browser_executable():
        print("Headless export: available")
    else:
        print("Headless export: Edge/Chrome not found")

    if not args.no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        httpd.server_close()
    return 0


def _bind_server(host: str, port: int, handler: type[BaseHTTPRequestHandler]) -> ThreadingHTTPServer:
    try:
        return ThreadingHTTPServer((host, port), handler)
    except OSError:
        if port == 0:
            raise
        return ThreadingHTTPServer((host, 0), handler)


def _static_dir() -> Path:
    import sys

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "markdown_mermaid_tool" / "static"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent / "static"


def _make_handler(context: AppContext) -> type[BaseHTTPRequestHandler]:
    class ToolRequestHandler(BaseHTTPRequestHandler):
        server_version = "MarkdownMermaidTool/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:
            print("[%s] %s" % (self.log_date_time_string(), fmt % args))

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            if path == "/api/state":
                self._send_json(
                    {
                        "state": context.state.to_json(),
                        "browserAvailable": find_browser_executable() is not None,
                    }
                )
                return
            if path in {"", "/"}:
                self._serve_file(context.static_dir / "index.html")
                return
            if path.startswith("/static/"):
                rel = path[len("/static/") :]
                self._serve_file(context.static_dir / rel)
                return
            self._send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:
            try:
                payload = self._read_json()
                if self.path == "/api/load-md":
                    self._handle_load_md(payload)
                elif self.path == "/api/load-ini":
                    self._handle_load_ini(payload)
                elif self.path == "/api/save-ini":
                    self._handle_save_ini(payload)
                elif self.path == "/api/generate":
                    self._handle_generate(payload)
                elif self.path == "/api/pick-md":
                    self._send_json({"path": _pick_markdown_file()})
                elif self.path == "/api/pick-ini-open":
                    self._send_json({"path": _pick_ini_file(open_existing=True)})
                elif self.path == "/api/pick-ini-save":
                    self._send_json({"path": _pick_ini_file(open_existing=False)})
                elif self.path == "/api/pick-output-dir":
                    self._send_json({"path": _pick_output_dir()})
                else:
                    self._send_error(HTTPStatus.NOT_FOUND, "Not found")
            except ValueError as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
            except Exception as exc:  # pragma: no cover - keeps UI errors readable.
                self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

        def _handle_load_md(self, payload: dict[str, Any]) -> None:
            raw_path = str(payload.get("path") or "").strip()
            if not raw_path:
                raise ValueError("MD path is empty.")
            md_path = _resolve_user_path(raw_path, context.base_dir)
            if not md_path.is_file():
                raise ValueError(f"MD file does not exist: {md_path}")
            content = _read_text_file(md_path)
            preserve_output_dir = bool(payload.get("preserveOutputDir"))
            with context.lock:
                context.state.md_path = str(md_path)
                if not preserve_output_dir:
                    context.state.output_dir = str(md_path.parent)
                context.state.output_name = derive_output_name(str(md_path))
                state_json = context.state.to_json()
            self._send_json({"content": content, "state": state_json})

        def _handle_load_ini(self, payload: dict[str, Any]) -> None:
            raw_path = str(payload.get("path") or "").strip()
            if not raw_path:
                ini_path = default_ini_path(context.base_dir)
            else:
                ini_path = _resolve_user_path(raw_path, context.base_dir)
            if not ini_path.is_file():
                raise ValueError(f"INI file does not exist: {ini_path}")
            state = load_state_from_ini(ini_path, context.base_dir)
            content = ""
            warning = ""
            if state.md_path and _resolve_user_path(state.md_path, context.base_dir).is_file():
                content = _read_text_file(_resolve_user_path(state.md_path, context.base_dir))
            elif state.md_path:
                warning = f"MD file from INI does not exist: {state.md_path}"
            with context.lock:
                context.state = state
            self._send_json({"state": state.to_json(), "content": content, "warning": warning})

        def _handle_save_ini(self, payload: dict[str, Any]) -> None:
            state = AppState.from_json(payload.get("state"), context.base_dir)
            raw_path = str(payload.get("path") or state.ini_path or "").strip()
            if not raw_path:
                ini_path = default_ini_path(context.base_dir)
            else:
                ini_path = _resolve_user_path(raw_path, context.base_dir)
            state.ini_path = str(ini_path)
            save_state_to_ini(ini_path, state)
            with context.lock:
                context.state = state
            self._send_json({"state": state.to_json(), "path": str(ini_path)})

        def _handle_generate(self, payload: dict[str, Any]) -> None:
            state = AppState.from_json(payload.get("state"), context.base_dir)
            markdown_text = str(payload.get("markdown") or "")
            if not state.output_dir:
                state.output_dir = str(default_output_dir(context.base_dir))
            if not state.output_name:
                state.output_name = derive_output_name(state.md_path)
            result = generate_outputs(state, markdown_text, context.static_dir, context.base_dir)
            if state.ini_path:
                save_state_to_ini(Path(state.ini_path), state)
            with context.lock:
                context.state = state
            response = result.to_json()
            response["state"] = state.to_json()
            self._send_json(response)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))

        def _serve_file(self, path: Path) -> None:
            try:
                safe_path = path.resolve()
                static_root = context.static_dir.resolve()
                if static_root not in safe_path.parents and safe_path != static_root:
                    self._send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                    return
                data = safe_path.read_bytes()
            except OSError:
                self._send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            mime_type = mimetypes.guess_type(str(safe_path))[0] or "application/octet-stream"
            self._send_bytes(data, HTTPStatus.OK, mime_type)

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send_bytes(data, status, "application/json; charset=utf-8")

        def _send_error(self, status: HTTPStatus, message: str) -> None:
            self._send_json({"error": message}, status)

        def _send_bytes(self, data: bytes, status: HTTPStatus, content_type: str) -> None:
            self.send_response(status.value)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

    return ToolRequestHandler


def _read_text_file(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _resolve_user_path(path_text: str, base_dir: Path) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return base_dir / path


def _pick_markdown_file() -> str:
    return _run_dialog(
        lambda filedialog: filedialog.askopenfilename(
            title="Load Markdown",
            filetypes=[
                ("Markdown Files", "*.md *.markdown *.mdown"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*"),
            ],
        )
    )


def _pick_ini_file(open_existing: bool) -> str:
    if open_existing:
        return _run_dialog(
            lambda filedialog: filedialog.askopenfilename(
                title="Load INI",
                defaultextension=".ini",
                filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            )
        )
    return _run_dialog(
        lambda filedialog: filedialog.asksaveasfilename(
            title="Save INI",
            defaultextension=".ini",
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
        )
    )


def _pick_output_dir() -> str:
    return _run_dialog(lambda filedialog: filedialog.askdirectory(title="Select Output Directory"))


def _run_dialog(callback: Any) -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return ""

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    try:
        value = callback(filedialog)
    finally:
        root.destroy()
    return str(value or "")
