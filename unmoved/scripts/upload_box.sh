#!/usr/bin/env bash
# Upload a finished Unmoved Short to Box. No shared link. No YouTube.
set -euo pipefail
FILE="${1:?usage: upload_box.sh <file> [parent-id]}"
PARENT="${2:-${BOX_PARENT_ID:-410644410730}}"
command -v box >/dev/null 2>&1 || { echo "ERROR: Box CLI not found." >&2; exit 1; }
[[ -s "$FILE" ]] || { echo "ERROR: missing file: $FILE" >&2; exit 1; }
FILE_ID="$(box files:upload "$FILE" --parent-id "$PARENT" --json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")"
[[ -n "$FILE_ID" ]] || { echo "ERROR: Box upload failed" >&2; exit 1; }
echo "box_file_id: $FILE_ID"
echo "box_parent_id: $PARENT"
echo "box_shared_link: (not created)"
