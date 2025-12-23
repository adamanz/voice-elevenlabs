---
name: voices
description: List available ElevenLabs voices
---

# List Available Voices

Use the ElevenLabs MCP to fetch and display all available voices.

## Instructions

1. Call the ElevenLabs `get_voices` tool to retrieve available voices
2. Display them in a formatted table with:
   - Voice name
   - Voice ID
   - Description/labels
   - Preview URL (if available)

## Output Format

Display voices in a clean table:

| Voice | ID | Description |
|-------|----|-----------|
| George | JBFqnCBsd6RMkjVDRZzb | Natural, warm male voice |
| Adam | pNInz6obpgDQGcFmaJgB | Deep, authoritative male |
| Rachel | 21m00Tcm4TlvDq8ikWAM | Natural female voice |

Include a note about how to change voices with `/voice-config set-voice <id>`
