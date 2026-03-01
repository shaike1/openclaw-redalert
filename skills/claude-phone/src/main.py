#!/usr/bin/env python3
"""
Voice Processor - Main Entry Point
STT → LLM → TTS Pipeline
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, make_asgi_app, REGISTRY, CollectorRegistry
import uvicorn

from src.config import settings
from src.api.routes import router
from src.services.stt import STTService
from src.services.llm import LLMService
from src.services.tts import TTSService
from src.services.redis_client import RedisService

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Custom Prometheus registry to avoid duplicates
metrics_registry = CollectorRegistry()

# Prometheus metrics using custom registry
request_counter = Counter(
    'voice_processor_requests_total',
    'Total requests',
    ['endpoint', 'status'],
    registry=metrics_registry
)
request_duration = Histogram(
    'voice_processor_request_duration_seconds',
    'Request duration',
    ['endpoint'],
    registry=metrics_registry
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Voice Processor v2.0")

    # Initialize services
    try:
        redis = RedisService(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        await redis.connect()
        app.state.redis = redis
        logger.info("Redis connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        stt = STTService(
            api_key=settings.OPENAI_API_KEY,
            model=settings.STT_MODEL
        )
        app.state.stt = stt
        logger.info("STT service initialized", model=settings.STT_MODEL)

        llm = LLMService(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.LLM_MODEL
        )
        app.state.llm = llm
        logger.info("LLM service initialized", model=settings.LLM_MODEL)

        tts = TTSService(
            api_key=settings.ELEVENLABS_API_KEY,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            language=settings.LANGUAGE
        )
        app.state.tts = tts
        logger.info("TTS service initialized", voice=settings.ELEVENLABS_VOICE_ID)

        logger.info("All services initialized successfully")
        yield

    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    finally:
        # Cleanup
        logger.info("Shutting down Voice Processor")
        if hasattr(app.state, 'redis'):
            await app.state.redis.disconnect()


# Create FastAPI app
app = FastAPI(
    title="Voice Processor v2",
    description="OpenClaw Voice AI Pipeline: STT → LLM → TTS",
    version="2.0.0",
    lifespan=lifespan
)

# Mount Prometheus metrics
metrics_app = make_asgi_app(metrics_registry)
app.mount("/metrics", metrics_app)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "redis": "connected" if hasattr(app.state, 'redis') else "disconnected",
            "stt": "ready",
            "llm": "ready",
            "tts": "ready"
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Voice Processor v2",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process": "/api/v1/process",
            "metrics": "/metrics"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


def main():
    """Main entry point"""
    # Create log directory
    Path("/var/log/voice").mkdir(parents=True, exist_ok=True)

    # Configure uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_config=None,  # Use structlog
        access_log=True
    )


if __name__ == "__main__":
    main()
