#!/usr/bin/env python3
"""
Voice Gateway - Simplified Version
Receives webhooks and forwards to voice processor
"""

import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os

logger = structlog.get_logger()

# Configuration
PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://voice-processor:8080")
SIP_SERVER = os.getenv("SIP_SERVER", "pbx.right-api.com")
SIP_USERNAME = os.getenv("SIP_USERNAME", "voice-bot-v2")

# Create FastAPI app
app = FastAPI(title="Voice Gateway v2", version="2.0.0")


class IncomingCall(BaseModel):
    """Incoming call notification"""
    call_id: str
    caller_number: str
    timestamp: str


class AudioData(BaseModel):
    """Audio data from call"""
    call_id: str
    audio_data: str  # Base64 encoded
    sequence: int


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "sip_server": SIP_SERVER,
        "sip_username": SIP_USERNAME
    }


@app.post("/incoming")
async def incoming_call(call: IncomingCall):
    """
    Handle incoming call notification

    For POC: Just log and acknowledge
    In production: Would register with SIP server
    """
    logger.info("Incoming call",
               call_id=call.call_id,
               caller=call.caller_number)

    # TODO: Register with 3CX SIP server
    # For now, just return success
    return {
        "status": "accepted",
        "call_id": call.call_id,
        "message": "Call registered"
    }


@app.post("/audio")
async def receive_audio(audio: AudioData):
    """
    Receive audio data from active call

    For POC: Just forward to processor
    In production: Would receive RTP stream
    """
    logger.info("Audio received",
               call_id=audio.call_id,
               sequence=audio.sequence,
               data_size=len(audio.audio_data))

    # TODO: Forward to voice processor
    # For now, just return success
    return {
        "status": "received",
        "call_id": audio.call_id
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Voice Gateway v2",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "incoming": "/incoming",
            "audio": "/audio"
        }
    }


def main():
    """Main entry point"""
    # Create log directory
    os.makedirs("/var/log/voice", exist_ok=True)

    # Configure uvicorn
    uvicorn.run(
        "gateway:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )


if __name__ == "__main__":
    main()
