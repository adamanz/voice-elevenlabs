#!/usr/bin/env python3
"""Find the ElevenLabs voice_id that produced daniel-deep-stoic-baritone.mp3.

Does not auto-select premade Daniel (onwK4e9ZLuTAKqWW03F9).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

sys.path.insert(0, os.path.dirname(__file__))
from lib import (
    NOTES_DIR,
    PREMADE_DANIEL,
    VOICES_PATH,
    die,
    load_voices,
    require_api_key,
    write_json,
)

SAMPLE_HINTS = (
    "daniel-deep-stoic-baritone",
    "deep stoic baritone",
    "stoic baritone",
    "daniel",
)


def api_get(path: str, key: str, params: dict[str, str] | None = None) -> Any:
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    request = urllib.request.Request(
        f"https://api.elevenlabs.io{path}{query}",
        headers={"xi-api-key": key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        body = error.read()[:400]
        die(f"ElevenLabs HTTP {error.code} on {path}: {body!r}")


def score_voice(item: dict[str, Any]) -> int:
    blob = " ".join(
        str(item.get(field) or "")
        for field in ("name", "description", "voice_id", "category", "label")
    ).lower()
    score = 0
    if "daniel" in blob:
        score += 10
    if "stoic" in blob:
        score += 6
    if "baritone" in blob:
        score += 6
    if "deep" in blob:
        score += 3
    if item.get("voice_id") == PREMADE_DANIEL:
        score -= 8
    return score


def flatten_voices(payload: Any, source: str) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        items = payload.get("voices") or payload.get("shared_voices") or []
    elif isinstance(payload, list):
        items = payload
    else:
        items = []
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "source": source,
                "voice_id": item.get("voice_id") or item.get("id"),
                "name": item.get("name"),
                "category": item.get("category"),
                "description": (item.get("description") or "")[:240],
                "score": score_voice(item),
            }
        )
    return [row for row in out if row.get("voice_id")]


def search_history(key: str) -> list[dict[str, Any]]:
    payload = api_get("/v1/history", key, {"page_size": "100"})
    rows = []
    for item in payload.get("history") or []:
        text = str(item.get("text") or "")
        voice_name = str(item.get("voice_name") or "")
        blob = f"{text} {voice_name} {item.get('voice_id') or ''}".lower()
        if not any(hint in blob for hint in SAMPLE_HINTS) and "daniel" not in voice_name.lower():
            continue
        rows.append(
            {
                "source": "history",
                "voice_id": item.get("voice_id"),
                "name": voice_name,
                "text": text[:160],
                "date_unix": item.get("date_unix"),
                "character_count_change_from": item.get("character_count_change_from"),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-map",
        action="store_true",
        help="Write a unique non-premade match into voices.json",
    )
    args = parser.parse_args()

    key = require_api_key()
    saved = flatten_voices(api_get("/v1/voices", key), "saved")
    shared_queries = [
        "daniel deep stoic baritone",
        "daniel stoic",
        "stoic baritone",
        "Daniel",
    ]
    shared: list[dict[str, Any]] = []
    seen: set[str] = set()
    for query in shared_queries:
        batch = flatten_voices(
            api_get("/v1/shared-voices", key, {"search": query, "page_size": "20"}),
            f"shared:{query}",
        )
        for row in batch:
            voice_id = str(row["voice_id"])
            if voice_id in seen:
                continue
            seen.add(voice_id)
            shared.append(row)

    history = search_history(key)
    ranked = sorted(saved + shared, key=lambda row: row["score"], reverse=True)
    unique_non_premade = [
        row
        for row in ranked
        if row["score"] >= 16 and row["voice_id"] != PREMADE_DANIEL
    ]

    note = {
        "sample": {
            "name": "daniel-deep-stoic-baritone.mp3",
            "box_file_id": "2418917961003",
            "duration_s": 4.0,
        },
        "premade_daniel_not_assumed": PREMADE_DANIEL,
        "saved_matches": [row for row in saved if row["score"] > 0][:12],
        "shared_matches": [row for row in ranked if row["source"].startswith("shared") and row["score"] > 0][:12],
        "history_matches": history[:12],
        "resolved_voice_id": None,
        "resolved_how": None,
    }

    if len(unique_non_premade) == 1:
        winner = unique_non_premade[0]
        note["resolved_voice_id"] = winner["voice_id"]
        note["resolved_how"] = (
            f"single high-score non-premade match: {winner['name']} "
            f"({winner['source']}, score {winner['score']})"
        )
        if args.write_map:
            voices = load_voices()
            voices["voices"]["daniel"]["voice_id"] = winner["voice_id"]
            voices["voices"]["daniel"]["status"] = "verified"
            voices["voices"]["daniel"]["kind"] = "library_or_saved"
            voices["voices"]["daniel"]["resolved_from"] = winner
            write_json(VOICES_PATH, voices)
    elif any(row.get("voice_id") == PREMADE_DANIEL for row in saved) and not unique_non_premade:
        note["resolved_how"] = (
            "Account has premade Daniel only. Not written to the map. "
            "Confirm against Box sample 2418917961003 before setting "
            f"UNMOVED_VOICE_ID={PREMADE_DANIEL} and UNMOVED_ALLOW_PREMADE_DANIEL=1."
        )

    out_path = NOTES_DIR / "daniel-voice.json"
    write_json(out_path, note)
    print(f"note: {out_path}")
    if note["resolved_voice_id"]:
        print(f"resolved_voice_id: {note['resolved_voice_id']}")
        print(f"resolved_how: {note['resolved_how']}")
    else:
        print("resolved_voice_id: (none)")
        print(note["resolved_how"] or "No unique match. Read the note and set UNMOVED_VOICE_ID.")
        if not args.write_map:
            print("Re-run with --write-map after a unique library match if you want voices.json updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
