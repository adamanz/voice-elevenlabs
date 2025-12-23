---
name: speak
description: Speak text aloud using ElevenLabs TTS
arguments:
  - name: text
    description: The text to speak aloud
    required: false
---

# Speak Command

Use ElevenLabs to convert text to speech and play it aloud.

## Behavior

1. If text is provided as an argument, speak that text
2. If no text provided, summarize your last response in 1-2 sentences and speak that

## Instructions

Use the ElevenLabs MCP server to generate speech:
- Call the `text_to_speech` tool with the text
- Use the configured voice ID (default: George - JBFqnCBsd6RMkjVDRZzb)
- Play the audio immediately

## Text to speak

$ARGUMENTS.text

If the above is empty, generate a brief spoken summary of your previous response.
