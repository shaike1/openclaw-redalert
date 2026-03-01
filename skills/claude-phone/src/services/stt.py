#!/usr/bin/env python3
"""
Speech-to-Text Service (OpenAI Whisper)
"""

import structlog
from openai import OpenAI
from pathlib import Path
import tempfile

logger = structlog.get_logger()


class STTService:
    """Speech-to-Text using OpenAI Whisper"""

    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info("STT service initialized", model=model)

    async def transcribe(self, audio_data: bytes, language: str = "he") -> str:
        """
        Transcribe audio to text

        Args:
            audio_data: Raw audio bytes
            language: Language code (default: he for Hebrew)

        Returns:
            Transcribed text
        """
        try:
            # Write audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            # Transcribe using Whisper
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language
                )

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            logger.info("Transcription complete",
                       text_length=len(transcript.text),
                       language=language)

            return transcript.text

        except Exception as e:
            logger.error("Transcription failed", error=str(e))
            raise
