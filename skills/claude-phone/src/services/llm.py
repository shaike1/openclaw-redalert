#!/usr/bin/env python3
"""
LLM Service (Anthropic Claude AI)
"""

import structlog
from anthropic import Anthropic

logger = structlog.get_logger()


class LLMService:
    """LLM service using Anthropic Claude"""

    def __init__(self, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info("LLM service initialized", model=model)

    async def generate_response(
        self,
        user_input: str,
        conversation_history: list = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate response using Claude

        Args:
            user_input: User's text input
            conversation_history: Previous messages
            system_prompt: Custom system prompt

        Returns:
            Generated response text
        """
        try:
            # Default system prompt
            if system_prompt is None:
                system_prompt = (
                    "You are Luky Bot, a helpful AI assistant. "
                    "Respond in Hebrew if the user speaks Hebrew, "
                    "or in English if they speak English. "
                    "Be friendly, concise, and helpful."
                )

            # Build messages
            messages = []

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user input
            messages.append({
                "role": "user",
                "content": user_input
            })

            # Generate response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            # Extract response text
            response_text = response.content[0].text

            logger.info("LLM response generated",
                       input_length=len(user_input),
                       response_length=len(response_text))

            return response_text

        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            raise
