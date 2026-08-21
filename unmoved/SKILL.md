---
name: unmoved-shorts
description: Generate an Unmoved stoic YouTube Short with the Daniel ElevenLabs voice and remux it to 1080x1920. Use when asked for Unmoved, stoic Shorts, Daniel VO, or the daily Unmoved render. Do not publish to YouTube.
---

# Unmoved Shorts

1. Read `unmoved/DANIEL.md` and `unmoved/voices.json`. Do not invent a Daniel `voice_id`.
2. If `voices.daniel.voice_id` is null, run `python3 unmoved/scripts/resolve_voice.py` with `ELEVENLABS_API_KEY`. Do not auto-pick premade `onwK4e9ZLuTAKqWW03F9`.
3. Use the spoken script exactly as given. Hook first and last line.
4. Render with `unmoved/scripts/render_short.sh --wound waiting-on-read`.
5. Optional: upload to Box folder `410644410730` with `upload_box.sh`. Do not create a shared link.
6. Do not publish to YouTube. Do not invent analytics.

Runtime: `ELEVENLABS_API_KEY` or `with-elevenlabs-key`. `UNMOVED_VOICE_ID` only after the Box sample is confirmed.
