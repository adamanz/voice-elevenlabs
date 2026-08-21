#!/usr/bin/env python3
"""Remux a vertical Unmoved Short: 4 Ken Burns stills + hook on frame 0."""

from __future__ import annotations

import argparse
import os
import sys
import zlib
from pathlib import Path
from struct import pack

sys.path.insert(0, os.path.dirname(__file__))
from lib import (
    ASSETS_DIR,
    OUT_DIR,
    SERIF_FONT,
    STILLS_DIR,
    audio_duration_s,
    die,
    load_wound,
    probe_media,
    run,
    which,
    write_json,
)

WIDTH = 1080
HEIGHT = 1920
FPS = 30


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return pack(">I", len(data)) + tag + data + pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, rgba: bytes) -> None:
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(rgba[y * stride : (y + 1) * stride])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + png_chunk(b"IEND", b"")
    )


def inside_rounded(x: int, y: int, left: int, top: int, right: int, bottom: int, radius: int) -> bool:
    if x < left or x >= right or y < top or y >= bottom:
        return False
    if x < left + radius and y < top + radius:
        return (x - (left + radius)) ** 2 + (y - (top + radius)) ** 2 <= radius ** 2
    if x >= right - radius and y < top + radius:
        return (x - (right - radius - 1)) ** 2 + (y - (top + radius)) ** 2 <= radius ** 2
    if x < left + radius and y >= bottom - radius:
        return (x - (left + radius)) ** 2 + (y - (bottom - radius - 1)) ** 2 <= radius ** 2
    if x >= right - radius and y >= bottom - radius:
        return (x - (right - radius - 1)) ** 2 + (y - (bottom - radius - 1)) ** 2 <= radius ** 2
    return True


def write_lower_third(path: Path) -> None:
    pixels = bytearray(WIDTH * HEIGHT * 4)
    left, right = 48, WIDTH - 48
    top, bottom = 1548, 1848
    radius = 36
    for y in range(top - 1, bottom + 1):
        for x in range(left - 1, right + 1):
            if inside_rounded(x, y, left, top, right, bottom, radius):
                i = (y * WIDTH + x) * 4
                pixels[i : i + 4] = b"\x10\x0e\x0c\xb8"
    write_png(path, WIDTH, HEIGHT, bytes(pixels))


def still_paths(wound: dict) -> list[Path]:
    paths = []
    for still in wound["stills"]:
        path = STILLS_DIR / f"{still['id']}.png"
        if not path.is_file():
            die(f"missing still {path}; run unmoved/scripts/make_stills.py")
        paths.append(path)
    if len(paths) != 4:
        die(f"need exactly 4 stills, found {len(paths)}")
    return paths


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")


def hook_drawtext(hook: str) -> str:
    words = hook.split()
    mid = max(3, len(words) // 2)
    line1 = escape_drawtext(" ".join(words[:mid]))
    line2 = escape_drawtext(" ".join(words[mid:]))
    return (
        f"drawtext=fontfile={SERIF_FONT}:text='{line1}':"
        "fontcolor=white:fontsize=42:"
        "x=(w-text_w)/2:y=1618,"
        f"drawtext=fontfile={SERIF_FONT}:text='{line2}':"
        "fontcolor=white:fontsize=42:"
        "x=(w-text_w)/2:y=1680"
    )


def remux(audio: Path, wound: dict, out_path: Path, min_audio_s: float = 8.0) -> dict:
    if not which("ffmpeg"):
        die("ffmpeg not found")
    duration = audio_duration_s(audio)
    if duration < min_audio_s:
        die(f"audio is {duration:.2f}s; expected a full VO, not the 4s sample")
    stills = still_paths(wound)
    overlay = ASSETS_DIR / "lower-third.png"
    if not overlay.is_file():
        write_lower_third(overlay)

    total_frames = max(int(round(duration * FPS)), FPS)
    base = total_frames // 4
    remainder = total_frames - base * 4
    frames = [base + (1 if i < remainder else 0) for i in range(4)]

    inputs: list[str] = []
    filters: list[str] = []
    for index, (still, count) in enumerate(zip(stills, frames)):
        inputs.extend(["-loop", "1", "-t", f"{count / FPS:.4f}", "-i", str(still)])
        step = 0.00055 if index % 2 == 0 else 0.0004
        filters.append(
            f"[{index}:v]scale=1296:2304,zoompan=z='min(zoom+{step:.5f},1.12)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={count}:"
            f"s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p[v{index}]"
        )
    filters.append("[v0][v1][v2][v3]concat=n=4:v=1:a=0[vcat]")
    overlay_index = 4
    audio_index = 5
    inputs.extend(["-i", str(overlay), "-i", str(audio)])
    filters.append(f"[vcat][{overlay_index}:v]overlay=0:0:format=auto[vbar]")
    filters.append(f"[vbar]{hook_drawtext(wound['hook'])}[vout]")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            *inputs,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            f"{audio_index}:a",
            "-r",
            str(FPS),
            "-t",
            f"{duration:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-profile:v",
            "high",
            "-level",
            "4.0",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ac",
            "1",
            "-b:a",
            "128k",
            "-ar",
            "44100",
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )

    info = probe_media(out_path)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio_s = next(s for s in info["streams"] if s["codec_type"] == "audio")
    summary = {
        "output": str(out_path),
        "hook": wound["hook"],
        "hook_on_first_frame": True,
        "width": int(video.get("width") or 0),
        "height": int(video.get("height") or 0),
        "fps": FPS,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio_s.get("codec_name"),
        "audio_channels": int(audio_s.get("channels") or 0),
        "duration_s": float((info.get("format") or {}).get("duration") or 0),
        "published_to_youtube": False,
    }
    if summary["width"] != WIDTH or summary["height"] != HEIGHT:
        die(f"bad frame size {summary['width']}x{summary['height']}")
    if summary["video_codec"] != "h264":
        die(f"expected h264, got {summary['video_codec']}")
    if summary["audio_codec"] != "aac" or summary["audio_channels"] != 1:
        die(f"expected aac mono, got {summary['audio_codec']} ch={summary['audio_channels']}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--wound", default="waiting-on-read")
    parser.add_argument("--out")
    parser.add_argument(
        "--min-audio-s",
        type=float,
        default=8.0,
        help="Reject shorter audio so the 4s Box sample cannot be remuxed as a Short",
    )
    args = parser.parse_args()

    audio = Path(args.audio)
    if not audio.is_file():
        die(f"missing audio: {audio}")
    wound = load_wound(args.wound)
    out_path = Path(args.out) if args.out else OUT_DIR / f"{args.wound}.mp4"
    summary = remux(audio, wound, out_path, min_audio_s=args.min_audio_s)
    write_json(out_path.with_suffix(".json"), summary)
    for key in (
        "output",
        "width",
        "height",
        "fps",
        "video_codec",
        "audio_codec",
        "audio_channels",
        "duration_s",
        "hook",
    ):
        print(f"{key}: {summary[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
