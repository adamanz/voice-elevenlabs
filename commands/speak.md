---
name: speak
description: Speak text aloud using ElevenLabs v3 TTS with optional emotion tags
arguments:
  - name: text
    description: Text to speak (supports audio tags like [excited], [whispers], [laughs])
    required: false
  - name: emotion
    description: Emotion preset (excited, whispers, angry, sad, laughs, sighs)
    required: false
---

# Speak Command (ElevenLabs v3)

Use ElevenLabs v3 to convert text to expressive speech with emotion control.

## Audio Tags (v3 Feature)

You can add emotion and style with inline tags:
- `[excited]` - Enthusiastic delivery
- `[whispers]` - Quiet, intimate
- `[laughs]` or `[laughing]` - Natural laughter
- `[sighs]` - Thoughtful pause
- `[angry]` - Intense, frustrated
- `[sad]` or `[sorrowful]` - Melancholic
- `[nervous]` - Hesitant, anxious
- `[shouting]` - Loud, emphatic
- `[sarcastically]` - Dry humor

## Examples

Simple: `/speak Hello, I finished your task!`

With emotion: `/speak [excited] Great news! The build passed!`

Combined: `/speak [whispers] Don't tell anyone, but... [laughs] I love coding!`

## Behavior

1. If text provided, speak that text with any embedded audio tags
2. If emotion argument provided, wrap text in that emotion tag
3. If no text, summarize last response and speak it
4. Use ElevenLabs v3 model (`eleven_v3_alpha`) for best expressiveness

## Instructions

Use the ElevenLabs MCP with these settings:
- Model: `eleven_v3_alpha` (most expressive)
- Voice: Use configured ELEVENLABS_VOICE_ID
- Parse and preserve any [audio tags] in the text

Text to speak: $ARGUMENTS.text
Emotion preset: $ARGUMENTS.emotion
