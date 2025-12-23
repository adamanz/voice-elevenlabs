# Voice ElevenLabs - Claude Code Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://claude.ai/code)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-FF6B35)](https://elevenlabs.io)

> Add natural voice capabilities to Claude Code using ElevenLabs AI voices.

## Install

**One command in Claude Code:**

```
/plugin install adamanz/voice-elevenlabs
```

Or manually:
```bash
cd ~/.claude/plugins
git clone https://github.com/adamanz/voice-elevenlabs.git
```

## Setup

1. Get a free API key from [ElevenLabs](https://elevenlabs.io/app/settings/api-keys)

2. Add to your shell config:
```bash
echo 'export ELEVENLABS_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

3. Install the voice notification CLI:
```bash
npm install -g claude-voice-notifications
```

4. Restart Claude Code

## Commands

| Command | Description |
|---------|-------------|
| `/speak [text]` | Speak text aloud (or summarize last response) |
| `/voices` | List available ElevenLabs voices |
| `/voice-config` | View and modify voice settings |

## Features

- **Voice Notifications** - Hear when Claude finishes tasks or needs input
- **ElevenLabs TTS** - Natural AI voices via MCP integration
- **Voice Agent** - Conversational assistant that speaks responses
- **Customizable** - Choose from multiple voices

## Voices

| Voice | ID | Style |
|-------|-----|-------|
| George | `JBFqnCBsd6RMkjVDRZzb` | Natural male (default) |
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep male |
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Natural female |
| Domi | `AZnzlk1XvdvUeBnXmlld` | Young female |

Change voice: Set `ELEVENLABS_VOICE_ID` environment variable.

## Hooks

Auto-triggers on these events:
- **Stop** - "Claude has finished responding"
- **SubagentStop** - "Subagent finished: [task]"
- **Notification** - "Claude needs your permission"

## Requirements

- [Claude Code](https://claude.ai/code)
- [ElevenLabs API key](https://elevenlabs.io) (free tier works)
- [claude-voice-notifications](https://github.com/ZeldOcarina/claude-code-voice-notifications) (`npm i -g claude-voice-notifications`)

## License

MIT

## Author

Adam Anzuoni - [@adamanz](https://github.com/adamanz)

---

**Keywords:** claude-code, plugin, voice, tts, text-to-speech, elevenlabs, notifications, accessibility
