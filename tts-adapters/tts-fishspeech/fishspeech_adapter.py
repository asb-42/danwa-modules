"""Fish Speech TTS adapter — external module for Danwa.

License: Fish Audio Research License (non-commercial)
Requires: Separately installed Fish Speech instance
Repository: https://github.com/fishaudio/fish-speech

By using this adapter, you confirm you have reviewed and accept the
Fish Audio license terms independently of Danwa's AGPL license.

This adapter calls a separately running Fish Speech server via HTTP.
It does NOT contain any Fish Speech code, weights, or models.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default Fish Speech API configuration
_DEFAULT_ENDPOINT = "http://localhost:8080"
_DEFAULT_MODEL = "s2-pro"


class FishSpeechAdapter:
    """Adapter for Fish Speech S2 Pro TTS.

    Requires a separately installed Fish Speech server running at the
    configured endpoint. The server must expose an OpenAI-compatible API.

    License: Fish Audio Research License (non-commercial)
    See: https://github.com/fishaudio/fish-speech/blob/main/LICENSE
    """

    # Adapter metadata (used by registry)
    ADAPTER_NAME = "fishspeech"
    ADAPTER_DISPLAY_NAME = "Fish Speech S2 Pro"
    ADAPTER_LICENSE = {
        "name": "Fish Audio Research License",
        "type": "non-commercial",
        "url": "https://github.com/fishaudio/fish-speech/blob/main/LICENSE",
        "attribution": "Built with Fish Audio",
    }

    def __init__(
        self,
        endpoint: str = _DEFAULT_ENDPOINT,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
    ) -> None:
        """Initialize Fish Speech adapter.

        Args:
            endpoint: Fish Speech server URL (e.g. "http://localhost:8080").
            api_key: Optional API key for authentication.
            model: Model ID to use (default: "s2-pro").
        """
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._model = model

    @staticmethod
    def name() -> str:
        return "fishspeech"

    @staticmethod
    def display_name() -> str:
        return "Fish Speech S2 Pro"

    def is_available(self) -> bool:
        """Check if Fish Speech server is reachable."""
        try:
            import httpx

            response = httpx.get(f"{self._endpoint}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def synthesize_segment(
        self,
        text: str,
        voice: str,
        output_path: Path,
        *,
        style_hint: str = "",
        **kwargs: Any,
    ) -> None:
        """Synthesize a single text segment to audio file.

        Calls the Fish Speech server's /v1/audio/speech endpoint.

        Args:
            text: The text to synthesize.
            voice: Voice ID or reference audio URL.
            output_path: Target audio file path.
            style_hint: Optional style hint (Fish Speech uses [tag] syntax).
        """
        import httpx

        url = f"{self._endpoint}/v1/audio/speech"

        payload: dict[str, Any] = {
            "model": self._model,
            "input": text,
            "voice": voice,
        }

        # Add style hint if provided (Fish Speech uses [tag] syntax in text)
        if style_hint:
            # Prepend style tag to text for Fish Speech
            payload["input"] = f"[{style_hint}] {text}"

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Fish Speech API returned {response.status_code}: {response.text[:500]}"
                )

            # Write audio data to file
            output_path.write_bytes(response.content)

        logger.debug("Fish Speech segment rendered: %s → %s", text[:50], output_path)

    def list_voices(
        self,
        language: str | None = None,
        gender: str | None = None,
    ) -> list[dict[str, Any]]:
        """List available Fish Speech voices.

        Returns a hardcoded list of known voices. For a dynamic list,
        the Fish Speech server would need to expose a /v1/voices endpoint.
        """
        # Fish Speech uses reference audio for voice cloning,
        # so voices are dynamic. Return common presets.
        voices = [
            {"voice_id": "default", "name": "Default", "language": "multi", "gender": "Unknown"},
        ]

        if language:
            voices = [v for v in voices if v["language"].startswith(language) or v["language"] == "multi"]
        if gender:
            voices = [v for v in voices if v["gender"] == gender or v["gender"] == "Unknown"]

        return voices

    @property
    def supports_style_hints(self) -> bool:
        """Fish Speech supports style control via [tag] syntax."""
        return True

    def license_info(self) -> dict[str, str]:
        """Return Fish Speech license information."""
        return self.ADAPTER_LICENSE.copy()


# ---------------------------------------------------------------------------
# Module registration hook
# ---------------------------------------------------------------------------


def register_module() -> None:
    """Register this adapter with the TTSAdapterRegistry.

    Called by Danwa when the module is installed and loaded.
    """
    try:
        from backend.services.output.plugins.tts_adapter import TTSAdapterRegistry

        # Create a wrapper class that matches the TTSAdapter ABC
        class FishSpeechTTSAdapter:
            """TTSAdapter-compatible wrapper for FishSpeechAdapter."""

            @staticmethod
            def name() -> str:
                return "fishspeech"

            @staticmethod
            def display_name() -> str:
                return "Fish Speech S2 Pro"

            def __init__(self) -> None:
                self._impl = FishSpeechAdapter()

            def is_available(self) -> bool:
                return self._impl.is_available()

            async def synthesize_segment(
                self,
                text: str,
                voice: str,
                output_path: Path,
                *,
                style_hint: str = "",
                **kwargs: Any,
            ) -> None:
                await self._impl.synthesize_segment(
                    text, voice, output_path, style_hint=style_hint, **kwargs
                )

            def list_voices(
                self,
                language: str | None = None,
                gender: str | None = None,
            ) -> list[dict[str, Any]]:
                return self._impl.list_voices(language=language, gender=gender)

            @property
            def supports_style_hints(self) -> bool:
                return True

            def license_info(self) -> dict[str, str]:
                return self._impl.license_info()

        TTSAdapterRegistry.register(FishSpeechTTSAdapter)
        logger.info("Fish Speech TTS adapter registered successfully")

    except ImportError:
        logger.warning(
            "Could not register Fish Speech adapter: "
            "backend.services.output.plugins.tts_adapter not found. "
            "Make sure Danwa core is installed."
        )


# Auto-register on import
register_module()
