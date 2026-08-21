#!/usr/bin/env bash
# Daily Unmoved Short path for Grok Bot.
# Generates an eleven_v3 Daniel VO (unless --audio is passed), remuxes
# 1080x1920 30fps H.264 + AAC mono, optional Box upload. Never publishes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
WOUND="waiting-on-read"
AUDIO=""
OUT=""
UPLOAD_BOX=0

usage() {
  cat <<'EOF'
Usage: render_short.sh [--wound SLUG] [--audio FILE] [--out FILE] [--upload-box]

Requires ELEVENLABS_API_KEY or a with-elevenlabs-key wrapper unless --audio is set.
Daniel voice_id must be in unmoved/voices.json, UNMOVED_VOICE_ID, or resolved first.

Does not publish to YouTube.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wound) WOUND="${2:?}"; shift 2 ;;
    --audio) AUDIO="${2:?}"; shift 2 ;;
    --out) OUT="${2:?}"; shift 2 ;;
    --upload-box) UPLOAD_BOX=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

python3 "$SCRIPTS/make_stills.py" --wound "$WOUND"

if [[ -z "$AUDIO" ]]; then
  if [[ -z "${ELEVENLABS_API_KEY:-}" && -x "$(command -v with-elevenlabs-key || true)" ]]; then
    echo "ERROR: ELEVENLABS_API_KEY is unset. Run: with-elevenlabs-key $0 $*" >&2
    exit 1
  fi
  AUDIO="$(python3 "$SCRIPTS/generate_vo.py" --wound "$WOUND" | awk '/^audio:/{print $2}')"
  [[ -n "$AUDIO" && -s "$AUDIO" ]] || { echo "ERROR: VO generation did not write audio" >&2; exit 1; }
fi

OUT_ARGS=()
if [[ -n "$OUT" ]]; then
  OUT_ARGS=(--out "$OUT")
fi
python3 "$SCRIPTS/remux_short.py" --wound "$WOUND" --audio "$AUDIO" "${OUT_ARGS[@]}"

if [[ "$UPLOAD_BOX" -eq 1 ]]; then
  command -v box >/dev/null 2>&1 || { echo "ERROR: Box CLI not found; skip --upload-box or install/auth box." >&2; exit 1; }
  PARENT="${BOX_PARENT_ID:-410644410730}"
  VIDEO="${OUT:-}"
  if [[ -z "$VIDEO" ]]; then
    VIDEO="$(ls -1t "$ROOT/out/${WOUND}"*.mp4 2>/dev/null | head -n 1 || true)"
  fi
  [[ -s "$VIDEO" ]] || { echo "ERROR: no remuxed mp4 to upload" >&2; exit 1; }
  FILE_ID="$(box files:upload "$VIDEO" --parent-id "$PARENT" --json \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")"
  [[ -n "$FILE_ID" ]] || { echo "ERROR: Box upload failed" >&2; exit 1; }
  echo "box_file_id: $FILE_ID"
  echo "box_parent_id: $PARENT"
  echo "box_shared_link: (not created; keep Unmoved private)"
fi
