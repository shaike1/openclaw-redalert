#!/usr/bin/env python3
"""
Configuration Settings for Voice Processor
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    ELEVENLABS_API_KEY: str

    # Service Configuration
    STT_MODEL: str = "whisper-1"
    LLM_MODEL: str = "claude-3-7-sonnet-20250219"
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    LANGUAGE: str = "he"

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Call Configuration
    MAX_CALL_DURATION: int = 300  # seconds
    RESPONSE_TIMEOUT: int = 30  # seconds
    SILENCE_TIMEOUT: int = 5  # seconds

    # Audio Configuration
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"

    # Logging
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
