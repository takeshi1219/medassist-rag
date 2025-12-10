"""Medical Response Generator - LLM-based answer generation."""
from typing import AsyncGenerator
from loguru import logger
from openai import AsyncOpenAI

from app.config import settings


class MedicalGenerator:
    """
    Generator for medical responses using OpenAI's GPT models.
    
    Handles both standard and streaming response generation.
    """
    
    def __init__(self):
        """Initialize the generator with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
    async def generate(
        self,
        question: str,
        context: str,
        system_prompt: str,
        language: str = "en"
    ) -> str:
        """
        Generate a response to a medical question.
        
        Args:
            question: The user's question
            context: Formatted context from retrieved documents
            system_prompt: System prompt with guidelines
            language: Response language
            
        Returns:
            Generated response text
        """
        try:
            # Add language instruction
            lang_instruction = ""
            if language == "ja":
                lang_instruction = "\n\nPlease respond in Japanese (日本語で回答してください)."
            
            messages = [
                {
                    "role": "system",
                    "content": system_prompt.format(context=context) + lang_instruction
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=2000,
                top_p=0.95,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._get_error_response(language)
    
    async def generate_stream(
        self,
        question: str,
        context: str,
        system_prompt: str,
        language: str = "en"
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response to a medical question.
        
        Yields chunks of the response as they are generated.
        """
        try:
            # Add language instruction
            lang_instruction = ""
            if language == "ja":
                lang_instruction = "\n\nPlease respond in Japanese (日本語で回答してください)."
            
            messages = [
                {
                    "role": "system",
                    "content": system_prompt.format(context=context) + lang_instruction
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                top_p=0.95,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield self._get_error_response(language)
    
    def _get_error_response(self, language: str) -> str:
        """Get an error response in the appropriate language."""
        if language == "ja":
            return (
                "申し訳ございません。回答の生成中にエラーが発生しました。"
                "しばらくしてから再度お試しください。"
                "緊急の場合は、医療専門家に直接ご相談ください。"
            )
        return (
            "I apologize, but an error occurred while generating the response. "
            "Please try again in a moment. "
            "For urgent matters, please consult a healthcare professional directly."
        )

