#!/usr/bin/env python3
"""
Text-to-Speech Service (ElevenLabs v2 API)
"""

import structlog
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice
from pathlib import Path
import tempfile

logger = structlog.get_logger()


class TTSService:
    """Text-to-Speech using ElevenLabs v2 API"""

    def __init__(self, api_key: str, voice_id: str, language: str = "he"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.language = language
        self.client = ElevenLabs(api_key=api_key)
        logger.info("TTS service initialized",
                   voice_id=voice_id,
                   language=language)

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Generate audio using v2 API
            response = self.client.generate(
                text=text,
                voice=Voice(voice_id=self.voice_id),
                model="eleven_multilingual_v2"
            )

            # Extract audio bytes
            audio = b"".join(chunk for chunk in response)

            logger.info("TTS synthesis complete",
                       text_length=len(text),
                       audio_size=len(audio))

            return audio

        except Exception as e:
            logger.error("TTS synthesis failed", error=str(e))
            raise

    async def synthesize_to_file(self, text: str, output_path: str) -> None:
        """
        Synthesize speech and save to file

        Args:
            text: Text to synthesize
            output_path: Output file path
        """
        try:
            audio = await self.synthesize(text)

            # Save to file
            with open(output_path, "wb") as f:
                f.write(audio)

            logger.info("TTS saved to file",
                       text_length=len(text),
                       output_path=output_path)

        except Exception as e:
            logger.error("TTS file save failed", error=str(e))
            raise
