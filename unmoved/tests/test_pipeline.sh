#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  [[ "$1" == *"$2"* ]] || fail "expected to contain: $2"
}

test_hook_is_first_and_last() {
  python3 - "$ROOT/wounds/waiting-on-read.txt" "$ROOT/wounds/waiting-on-read.json" <<'PY'
import json, pathlib, sys
script = pathlib.Path(sys.argv[1]).read_text().strip()
hook = json.loads(pathlib.Path(sys.argv[2]).read_text())["hook"]
spoken = " ".join(script.split())
assert spoken.startswith(hook), spoken[:80]
assert spoken.endswith(hook), spoken[-80:]
print("ok hook")
PY
}

test_voice_map_does_not_assume_premade_daniel() {
  python3 - "$ROOT/voices.json" <<'PY'
import json, pathlib, sys
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
daniel = data["voices"]["daniel"]
assert daniel["voice_id"] is None, daniel
assert daniel["status"] == "unresolved"
assert daniel["do_not_assume_voice_id"] == "onwK4e9ZLuTAKqWW03F9"
assert data["voices"]["brian"]["voice_id"] == "nPczCjzI2devNBz1zQrb"
print("ok voice map")
PY
}

test_missing_key_fails_cleanly() {
  local output status
  set +e
  output="$(env -u ELEVENLABS_API_KEY -u UNMOVED_VOICE_ID -u VOICE_ID \
    PATH="/usr/bin:/bin" python3 "$SCRIPTS/generate_vo.py" --wound waiting-on-read 2>&1)"
  status=$?
  set -e
  [[ $status -ne 0 ]] || fail "generate_vo succeeded without a key or voice id"
  assert_contains "$output" "ERROR:"
}

test_premade_daniel_override_is_blocked() {
  local output status
  set +e
  output="$(env -u UNMOVED_ALLOW_PREMADE_DANIEL UNMOVED_VOICE_ID=onwK4e9ZLuTAKqWW03F9 \
    ELEVENLABS_API_KEY=test-only python3 "$SCRIPTS/generate_vo.py" --wound waiting-on-read 2>&1)"
  status=$?
  set -e
  [[ $status -ne 0 ]] || fail "premade Daniel override was accepted"
  assert_contains "$output" "not verified"
}

test_script_rejects_wrong_hook() {
  local output status
  printf 'Wrong opener. Middle. Wrong closer.\n' > "$TMP/bad.txt"
  set +e
  output="$(UNMOVED_VOICE_ID=abcdefghijklmnopqrstuvwx ELEVENLABS_API_KEY=test-only \
    python3 "$SCRIPTS/generate_vo.py" --wound waiting-on-read --script "$TMP/bad.txt" 2>&1)"
  status=$?
  set -e
  [[ $status -ne 0 ]] || fail "bad hook was accepted"
  assert_contains "$output" "hook must be the first line"
}

test_missing_box_cli_fails_upload() {
  local output status
  printf 'x' > "$TMP/empty.mp4"
  set +e
  output="$(PATH="/usr/bin:/bin" "$SCRIPTS/upload_box.sh" "$TMP/empty.mp4" 2>&1)"
  status=$?
  set -e
  [[ $status -ne 0 ]] || fail "upload succeeded without Box CLI"
  assert_contains "$output" "Box CLI not found"
}

test_remux_style_lock() {
  python3 "$SCRIPTS/make_stills.py" --wound waiting-on-read
  ffmpeg -y -hide_banner -loglevel error \
    -f lavfi -i sine=frequency=220:sample_rate=44100:duration=12 \
    -ac 1 -c:a libmp3lame -q:a 6 "$TMP/fixture.mp3"
  python3 "$SCRIPTS/remux_short.py" \
    --wound waiting-on-read \
    --audio "$TMP/fixture.mp3" \
    --out "$TMP/short.mp4"
  python3 - "$TMP/short.mp4" "$TMP/short.json" <<'PY'
import json, pathlib, subprocess, sys
video = pathlib.Path(sys.argv[1])
meta = json.loads(pathlib.Path(sys.argv[2]).read_text())
assert meta["width"] == 1080
assert meta["height"] == 1920
assert meta["fps"] == 30
assert meta["video_codec"] == "h264"
assert meta["audio_codec"] == "aac"
assert meta["audio_channels"] == 1
assert 11.0 <= meta["duration_s"] <= 13.0
assert meta["hook"].startswith("You wait six hours")
assert meta["published_to_youtube"] is False
frame = video.with_suffix(".png")
subprocess.check_call([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(video), "-vframes", "1", str(frame),
])
assert frame.stat().st_size > 20_000
print("ok remux")
PY
}

test_hook_is_first_and_last
test_voice_map_does_not_assume_premade_daniel
test_missing_key_fails_cleanly
test_premade_daniel_override_is_blocked
test_script_rejects_wrong_hook
test_missing_box_cli_fails_upload
test_remux_style_lock
echo "PASS: 7 tests"
