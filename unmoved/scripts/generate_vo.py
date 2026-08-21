#!/usr/bin/env python3
"""Generate a full eleven_v3 VO from a spoken script + the Daniel voice."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib import (
    NOTES_DIR,
    OUT_DIR,
    die,
    load_voices,
    load_wound,
    require_api_key,
    require_daniel_voice_id,
    validate_script,
    write_json,
)


def synthesize(text: str, voice_id: str, model_id: str, out_path: Path) -> int:
    key = require_api_key()
    body = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.62,
            "similarity_boost": 0.78,
            "style": 0.15,
            "use_speaker_boost": True,
        },
    }
    request = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(),
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            audio = response.read()
    except urllib.error.HTTPError as error:
        die(f"ElevenLabs HTTP {error.code}: {error.read()[:400]!r}")
    if len(audio) < 10_000:
        die(f"suspiciously small audio response ({len(audio)} bytes)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(audio)
    return len(audio)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wound", default="waiting-on-read")
    parser.add_argument("--script", help="Override spoken-script path")
    parser.add_argument("--out", help="Output mp3 path")
    args = parser.parse_args()

    voices = load_voices()
    wound = load_wound(args.wound)
    script = Path(args.script).read_text() if args.script else wound["script"]
    spoken = validate_script(script, wound["hook"])
    voice_id = require_daniel_voice_id()
    model_id = str(voices.get("model_id") or "eleven_v3")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = Path(args.out) if args.out else OUT_DIR / f"{args.wound}-daniel-{stamp}.mp3"

    nbytes = synthesize(spoken, voice_id, model_id, out_path)
    note = {
        "wound": args.wound,
        "hook": wound["hook"],
        "voice_id": voice_id,
        "model_id": model_id,
        "script_chars": len(spoken),
        "audio_path": str(out_path),
        "audio_bytes": nbytes,
        "box_sample_file_id": "2418917961003",
        "published_to_youtube": False,
    }
    note_path = NOTES_DIR / f"{args.wound}-vo.json"
    write_json(note_path, note)
    print(f"audio: {out_path} ({nbytes} bytes)")
    print(f"voice_id: {voice_id}")
    print(f"model_id: {model_id}")
    print(f"note: {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
