# Unmoved Shorts pipeline

Faceless stoic YouTube Shorts. Source of truth is Box folder `410644410730` (Unmoved — Stoic Daily). This repo now holds the generate + remux path so Grok Bot can run it daily.

Does **not** publish to YouTube.

## Daily path

```bash
# 1. Lock Daniel if voices.json still has voice_id: null
with-elevenlabs-key python3 unmoved/scripts/resolve_voice.py --write-map

# 2. Spoken script + remux (1080x1920 30fps H.264 + AAC mono)
with-elevenlabs-key unmoved/scripts/render_short.sh --wound waiting-on-read

# 3. Optional private Box upload (no shared link)
unmoved/scripts/render_short.sh --wound waiting-on-read --audio unmoved/out/....mp3 --upload-box
```

If the voice is already resolved, skip step 1. You can also set `UNMOVED_VOICE_ID` after confirming it against Box file `2418917961003`.

## Style lock

- 1080×1920, 30fps, H.264 + AAC mono
- 4 stills, Ken Burns
- White serif lower-third on a dark rounded bar
- Hook is the first and last spoken line, and it is on screen at 0:00
- About 40s, driven by VO length
- Loop the hook

## Next wound

Spoken script is exact in `unmoved/wounds/waiting-on-read.txt`.

Hook: `You wait six hours for a two-word reply.`

## Voice

See `unmoved/DANIEL.md` and `unmoved/voices.json`. Brian (`nPczCjzI2devNBz1zQrb`) is the live first Short. Daniel is the picked sample and is **unresolved** until `resolve_voice.py` or `UNMOVED_VOICE_ID` fills it in.

## Keys and Box

- Inject `ELEVENLABS_API_KEY` at runtime, or wrap with `with-elevenlabs-key`. Never commit the key.
- Box upload needs the authenticated Box CLI and `BOX_PARENT_ID` (defaults to `410644410730`).
- No open shared links.

## Tests

```bash
unmoved/tests/test_pipeline.sh
```
