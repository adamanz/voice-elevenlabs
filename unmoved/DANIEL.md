# Daniel voice_id — investigation

Status: **unresolved**. The next Unmoved Short should use the voice that produced Box sample `daniel-deep-stoic-baritone.mp3` (file `2418917961003`, 4.0s only). That id is not stored in this repo, in `adamanz/elevenlabs-box-imessage-skill`, or in any Adam voice map I could read.

Do not treat premade Daniel `onwK4e9ZLuTAKqWW03F9` as the answer unless a resolver run proves it.

## What I checked

| Source | Result |
| --- | --- |
| This repo (`voice-elevenlabs`) | No Unmoved pipeline. Default speak voice is George `JBFqnCBsd6RMkjVDRZzb`. No Daniel. |
| `adamanz/elevenlabs-box-imessage-skill` | TTS + Box upload only. Default `VOICE_ID=nPczCjzI2devNBz1zQrb` (Brian). Model `eleven_v3`. No remux, no voice map, no Daniel. |
| `adamanz/podcast-generator-mcp` `VOICE_ID_MAP` | `"Daniel": "onwK4e9ZLuTAKqWW03F9"` — premade Steady Broadcaster. Not tied to the Box sample. |
| Linear / Slack / Notion / Gmail | No Unmoved voice notes. |
| Box folder `410846433426` / file `2418917961003` | Private. Box MCP is not in this environment. Box CLI is not installed. No key, no listing, no description read. |
| ElevenLabs shared-voice search | `GET /v1/shared-voices` returns 401 without `ELEVENLABS_API_KEY`. |

## Why the premade id is not assumed

Adam rejected several unique library options, then asked to try Daniel. The file he picked is named `daniel-deep-stoic-baritone.mp3`, not `Daniel - Steady Broadcaster`. That kebab label is how a library PVC sample usually gets saved. It might still be premade Daniel with extra adjectives. I cannot tell without account history or the Box file metadata.

## How to lock the id

1. Inject `ELEVENLABS_API_KEY` (never commit it).
2. Run `python3 unmoved/scripts/resolve_voice.py`.
3. The script searches saved voices, the shared library, and recent history. It writes `unmoved/notes/daniel-voice.json` and will not auto-pick `onwK4e9ZLuTAKqWW03F9`.
4. Or set `UNMOVED_VOICE_ID` yourself after you confirm the match.

Box IDs for the Unmoved agent:

- Stoic Daily folder: `410644410730`
- 11L Voice Clips folder: `410846433426`
- Daniel sample file: `2418917961003`
