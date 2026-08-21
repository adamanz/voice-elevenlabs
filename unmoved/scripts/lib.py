#!/usr/bin/env python3
"""Shared helpers for the Unmoved Shorts pipeline."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
VOICES_PATH = ROOT / "voices.json"
WOUNDS_DIR = ROOT / "wounds"
ASSETS_DIR = ROOT / "assets"
STILLS_DIR = ASSETS_DIR / "stills"
NOTES_DIR = ROOT / "notes"
OUT_DIR = ROOT / "out"
PREMADE_DANIEL = "onwK4e9ZLuTAKqWW03F9"
BRIAN_ID = "nPczCjzI2devNBz1zQrb"
SERIF_FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_voices() -> dict[str, Any]:
    if not VOICES_PATH.is_file():
        die(f"missing voice map: {VOICES_PATH}")
    return json.loads(VOICES_PATH.read_text())


def load_wound(slug: str) -> dict[str, Any]:
    meta_path = WOUNDS_DIR / f"{slug}.json"
    if not meta_path.is_file():
        die(f"unknown wound: {slug} ({meta_path})")
    meta = json.loads(meta_path.read_text())
    script_name = meta.get("script_file") or f"{slug}.txt"
    script_path = WOUNDS_DIR / script_name
    if not script_path.is_file():
        die(f"missing spoken script: {script_path}")
    meta["script_path"] = str(script_path)
    meta["script"] = script_path.read_text().strip()
    return meta


def normalize_spoken(text: str) -> str:
    return " ".join(text.split()).strip()


def validate_script(script: str, hook: str) -> str:
    spoken = normalize_spoken(script)
    hook_n = normalize_spoken(hook)
    if not spoken:
        die("spoken script is empty")
    if not spoken.startswith(hook_n):
        die(f"hook must be the first line. expected start: {hook_n}")
    if not spoken.endswith(hook_n):
        die(f"hook must be the last line. expected end: {hook_n}")
    if len(spoken) > 5000:
        die(f"script is {len(spoken)} chars; keep under 5000 for one eleven_v3 request")
    return spoken


def elevenlabs_api_key() -> str | None:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    return None


def require_api_key() -> str:
    key = elevenlabs_api_key()
    if key:
        return key
    if which("with-elevenlabs-key"):
        die(
            "ELEVENLABS_API_KEY is unset. Re-run through with-elevenlabs-key "
            "or export the key at runtime. Do not paste the key into chat."
        )
    die(
        "ELEVENLABS_API_KEY is unset. Inject it at runtime or install a "
        "with-elevenlabs-key wrapper. Do not write the key into the repo."
    )


def which(name: str) -> str | None:
    from shutil import which as _which

    return _which(name)


def daniel_voice_id(voices: dict[str, Any] | None = None) -> str | None:
    override = os.environ.get("UNMOVED_VOICE_ID") or os.environ.get("VOICE_ID")
    if override:
        if override == PREMADE_DANIEL and os.environ.get("UNMOVED_ALLOW_PREMADE_DANIEL") != "1":
            die(
                "UNMOVED_VOICE_ID is premade Daniel "
                f"{PREMADE_DANIEL}. That id is not verified against "
                "daniel-deep-stoic-baritone.mp3. Set UNMOVED_ALLOW_PREMADE_DANIEL=1 "
                "only after you confirm the Box sample used it."
            )
        return override
    data = voices or load_voices()
    daniel = data.get("voices", {}).get("daniel") or {}
    voice_id = daniel.get("voice_id")
    if isinstance(voice_id, str) and voice_id.strip():
        return voice_id.strip()
    return None


def require_daniel_voice_id() -> str:
    voice_id = daniel_voice_id()
    if voice_id:
        return voice_id
    die(
        "Daniel voice_id is unresolved. Run unmoved/scripts/resolve_voice.py "
        "with ELEVENLABS_API_KEY, or set UNMOVED_VOICE_ID after confirming "
        "Box file 2418917961003. Do not silently use premade "
        f"{PREMADE_DANIEL}."
    )


def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def probe_media(path: Path) -> dict[str, Any]:
    if not which("ffprobe"):
        die("ffprobe not found")
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def audio_duration_s(path: Path) -> float:
    info = probe_media(path)
    fmt = info.get("format") or {}
    if fmt.get("duration"):
        return float(fmt["duration"])
    for stream in info.get("streams") or []:
        if stream.get("codec_type") == "audio" and stream.get("duration"):
            return float(stream["duration"])
    die(f"could not read duration: {path}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
