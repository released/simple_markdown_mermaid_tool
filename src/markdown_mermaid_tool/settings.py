from __future__ import annotations

import configparser
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


INVALID_FILE_CHARS = r'<>:"/\|?*'


def runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def default_ini_path(base_dir: Path | None = None) -> Path:
    root = base_dir or runtime_base_dir()
    return root / "markdown_mermaid_tool.ini"


def default_output_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or runtime_base_dir()
    return root / "output"


def derive_output_name(md_path: str, fallback: str = "document") -> str:
    if not md_path:
        return fallback
    name = Path(md_path).stem.strip()
    return name or fallback


def sanitize_output_name(name: str, fallback: str = "document") -> str:
    clean = "".join("_" if ch in INVALID_FILE_CHARS else ch for ch in name.strip())
    clean = re.sub(r"\s+", "_", clean)
    clean = clean.strip(" ._")
    return clean or fallback


def _bool_from_any(value: Any, fallback: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return fallback
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "y"}:
        return True
    if text in {"0", "false", "no", "off", "n"}:
        return False
    return fallback


@dataclass
class FormatState:
    html: bool = True
    pdf: bool = False
    png: bool = False
    jpg: bool = False

    def any_selected(self) -> bool:
        return self.html or self.pdf or self.png or self.jpg

    def to_json(self) -> dict[str, bool]:
        return {
            "html": self.html,
            "pdf": self.pdf,
            "png": self.png,
            "jpg": self.jpg,
        }

    @classmethod
    def from_json(cls, payload: Any) -> "FormatState":
        payload = payload or {}
        return cls(
            html=_bool_from_any(payload.get("html"), True),
            pdf=_bool_from_any(payload.get("pdf"), False),
            png=_bool_from_any(payload.get("png"), False),
            jpg=_bool_from_any(payload.get("jpg"), False),
        )


@dataclass
class AppState:
    md_path: str = ""
    ini_path: str = ""
    output_dir: str = ""
    output_name: str = "document"
    formats: FormatState = field(default_factory=FormatState)

    @classmethod
    def default(cls, base_dir: Path | None = None) -> "AppState":
        root = base_dir or runtime_base_dir()
        return cls(
            ini_path=str(default_ini_path(root)),
            output_dir=str(default_output_dir(root)),
            output_name="document",
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "mdPath": self.md_path,
            "iniPath": self.ini_path,
            "outputDir": self.output_dir,
            "outputName": self.output_name,
            "formats": self.formats.to_json(),
        }

    @classmethod
    def from_json(cls, payload: Any, base_dir: Path | None = None) -> "AppState":
        payload = payload or {}
        root = base_dir or runtime_base_dir()
        state = cls.default(root)
        state.md_path = str(payload.get("mdPath") or "").strip()
        state.ini_path = str(payload.get("iniPath") or state.ini_path).strip()
        state.output_dir = str(payload.get("outputDir") or state.output_dir).strip()
        state.output_name = str(payload.get("outputName") or "").strip()
        if not state.output_name:
            state.output_name = derive_output_name(state.md_path)
        state.formats = FormatState.from_json(payload.get("formats"))
        if not state.formats.any_selected():
            state.formats.html = True
        return state


def load_state_from_ini(path: Path, base_dir: Path | None = None) -> AppState:
    root = base_dir or runtime_base_dir()
    parser = configparser.ConfigParser()
    with path.open("r", encoding="utf-8-sig") as fp:
        parser.read_file(fp)

    state = AppState.default(root)
    state.ini_path = str(path)
    state.md_path = parser.get("PATHS", "md_path", fallback=state.md_path).strip()
    state.output_dir = parser.get("PATHS", "output_dir", fallback=state.output_dir).strip()
    state.output_name = parser.get("OUTPUT", "name", fallback=state.output_name).strip()
    if not state.output_name:
        state.output_name = derive_output_name(state.md_path)

    state.formats = FormatState(
        html=parser.getboolean("OUTPUT", "html", fallback=True),
        pdf=parser.getboolean("OUTPUT", "pdf", fallback=False),
        png=parser.getboolean("OUTPUT", "png", fallback=False),
        jpg=parser.getboolean("OUTPUT", "jpg", fallback=False),
    )
    if not state.formats.any_selected():
        state.formats.html = True
    return state


def save_state_to_ini(path: Path, state: AppState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["APP"] = {
        "tool": "simple_markdown_mermaid_tool",
    }
    parser["PATHS"] = {
        "md_path": state.md_path,
        "ini_path": str(path),
        "output_dir": state.output_dir,
    }
    parser["OUTPUT"] = {
        "name": state.output_name,
        "html": "1" if state.formats.html else "0",
        "pdf": "1" if state.formats.pdf else "0",
        "png": "1" if state.formats.png else "0",
        "jpg": "1" if state.formats.jpg else "0",
    }
    with path.open("w", encoding="utf-8", newline="\n") as fp:
        parser.write(fp)
