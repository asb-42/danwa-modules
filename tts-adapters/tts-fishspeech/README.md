# Fish Speech TTS Module for Danwa

## Overview

This module adds Fish Speech S2 Pro as a TTS engine option in Danwa. Fish Speech is a state-of-the-art open-source TTS system supporting 80+ languages with fine-grained emotion control.

## ⚠️ License Warning

**Fish Speech is NOT licensed under an open-source license.**

Fish Speech uses the **Fish Audio Research License** which restricts usage to **non-commercial purposes only**. Commercial use requires a separate written agreement from Fish Audio.

By installing this module, you confirm that:

1. You have read and understood the [Fish Audio Research License](https://github.com/fishaudio/fish-speech/blob/main/LICENSE)
2. You will only use Fish Speech for non-commercial purposes
3. You understand this license is separate from Danwa's AGPL-3.0 license

## Requirements

This module requires a **separately installed Fish Speech server**. The Danwa module only contains the adapter code (HTTP client) — no Fish Speech code, weights, or models are included.

### Installation Steps

1. **Install Fish Speech Server**
   
   Follow the official installation guide:
   https://speech.fish.audio/install/
   
   Or use Docker:
   ```bash
   docker pull fishaudio/fish-speech
   docker run -p 8080:8080 fishaudio/fish-speech
   ```

2. **Install this Danwa Module**
   
   Via Danwa UI: Build → Modules → GitHub → Search "tts-fishspeech"
   
   Or via API:
   ```bash
   POST /api/v1/modules/install-from-repo
   {
     "source": "github",
     "repo": "asb-42/danwa-modules",
     "module_id": "tts-fishspeech",
     "version": "1.0.0"
   }
   ```

3. **Configure Fish Speech Endpoint**
   
   The adapter defaults to `http://localhost:8080`. If your Fish Speech server runs elsewhere, update the adapter configuration in Danwa.

## Features

- **80+ languages** including German, English, Chinese, Japanese, Korean
- **Fine-grained emotion control** via `[tag]` syntax (e.g., `[whisper]`, `[excited]`, `[angry]`)
- **Multi-speaker** and **voice cloning** support
- **Self-hosted** — your data stays on your infrastructure
- **High quality** — SOTA benchmarks (lowest WER on Seed-TTS Eval)

## Attribution Requirement

The Fish Audio Research License requires you to display **"Built with Fish Audio"** on any UI, documentation, or product that uses Fish Speech. This attribution is automatically included in the adapter's `license_info()` method.

## Technical Details

- **Engine ID**: `fishspeech`
- **API**: OpenAI-compatible `/v1/audio/speech` endpoint
- **Default voice**: `default` (reference audio-based cloning)
- **Style hints**: Supported via `[tag]` syntax prepended to text

## License

This Danwa module (adapter code) is licensed under AGPL-3.0.

The Fish Speech TTS engine itself is licensed under the Fish Audio Research License (non-commercial).

See [LICENSE](LICENSE) for the full Fish Audio Research License text.
