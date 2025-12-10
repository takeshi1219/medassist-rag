"""Embedding generation for vector search."""
from typing import List
from openai import AsyncOpenAI
from loguru import logger

from app.config import settings


# OpenAI client for embeddings
_client = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for a text string.
    
    Uses OpenAI's text-embedding-3-small model (1536 dimensions).
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        client = get_openai_client()
        
        # Clean and truncate text if needed
        text = text.replace("\n", " ").strip()
        if len(text) > 8000:
            text = text[:8000]
        
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        # Return zero vector as fallback (will have low similarity to everything)
        return [0.0] * 1536


async def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch.
    
    More efficient than calling get_embedding multiple times.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    try:
        client = get_openai_client()
        
        # Clean texts
        cleaned_texts = [
            t.replace("\n", " ").strip()[:8000]
            for t in texts
        ]
        
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=cleaned_texts
        )
        
        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [e.embedding for e in embeddings]
        
    except Exception as e:
        logger.error(f"Batch embedding error: {e}")
        return [[0.0] * 1536 for _ in texts]

