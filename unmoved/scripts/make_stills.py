#!/usr/bin/env python3
"""Build the four 1080x1920 stills used by Ken Burns remux."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib import SERIF_FONT, STILLS_DIR, die, load_wound, run, which


def ensure_still(path: Path, tone: str, whisper: str) -> None:
    if not which("ffmpeg"):
        die("ffmpeg not found")
    path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"color=c={tone}:s=1080x1920:d=1",
            "-vf",
            (
                f"drawtext=fontfile={SERIF_FONT}:text='{whisper}':"
                "fontcolor=white@0.12:fontsize=86:x=(w-text_w)/2:y=(h-text_h)/2"
            ),
            "-frames:v",
            "1",
            str(path),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wound", default="waiting-on-read")
    args = parser.parse_args()
    wound = load_wound(args.wound)
    written = []
    for still in wound["stills"]:
        path = STILLS_DIR / f"{still['id']}.png"
        ensure_still(path, still["tone"], still["whisper"])
        written.append(str(path))
    for path in written:
        print(f"still: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
