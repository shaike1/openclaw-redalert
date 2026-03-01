#!/usr/bin/env python3
"""
Redis Client for Call State Management
"""

import structlog
import json
from typing import Optional, Any
from datetime import datetime
import redis.asyncio as redis

logger = structlog.get_logger()


class RedisService:
    """Redis client for session and state management"""

    def __init__(self, host: str, port: int, password: str = None, db: int = 0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client: Optional[redis.Redis] = None
        logger.info("Redis service configured",
                   host=host,
                   port=port,
                   db=db)

    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis")

        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")

    async def set_session(
        self,
        call_id: str,
        data: dict,
        ttl: int = 3600
    ) -> None:
        """
        Store call session data

        Args:
            call_id: Call identifier
            data: Session data
            ttl: Time to live in seconds (default: 1 hour)
        """
        try:
            key = f"session:{call_id}"
            value = json.dumps(data)
            await self.client.setex(key, ttl, value)
            logger.info("Session stored", call_id=call_id, ttl=ttl)

        except Exception as e:
            logger.error("Failed to store session", error=str(e))
            raise

    async def get_session(self, call_id: str) -> Optional[dict]:
        """
        Retrieve call session data

        Args:
            call_id: Call identifier

        Returns:
            Session data or None
        """
        try:
            key = f"session:{call_id}"
            value = await self.client.get(key)

            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error("Failed to get session", error=str(e))
            return None

    async def update_conversation(
        self,
        call_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add message to conversation history

        Args:
            call_id: Call identifier
            role: Message role (user/assistant)
            content: Message content
        """
        try:
            key = f"conversation:{call_id}"
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Append to list
            await self.client.lpush(key, json.dumps(message))
            # Keep last 20 messages
            await self.client.ltrim(key, 0, 19)
            # Set TTL
            await self.client.expire(key, 3600)

            logger.info("Conversation updated", call_id=call_id, role=role)

        except Exception as e:
            logger.error("Failed to update conversation", error=str(e))
            raise

    async def get_conversation(self, call_id: str) -> list:
        """
        Retrieve conversation history

        Args:
            call_id: Call identifier

        Returns:
            List of messages
        """
        try:
            key = f"conversation:{call_id}"
            messages = await self.client.lrange(key, 0, -1)

            return [
                json.loads(msg)
                for msg in reversed(messages)
            ]

        except Exception as e:
            logger.error("Failed to get conversation", error=str(e))
            return []
