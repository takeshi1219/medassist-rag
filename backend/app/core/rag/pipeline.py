"""Medical RAG Pipeline - Orchestrates retrieval and generation."""
import time
import uuid
from typing import List, Dict, Any, AsyncGenerator, Optional
from loguru import logger

from app.config import settings
from app.core.rag.retriever import MedicalRetriever
from app.core.rag.reranker import Reranker
from app.core.rag.generator import MedicalGenerator
from app.models.schemas import Citation, ChatResponse, Source


MEDICAL_SYSTEM_PROMPT = """You are MedAssist, a clinical decision support AI assistant.
You help healthcare professionals by providing accurate, evidence-based medical information.

## Guidelines:
1. Always cite sources for medical claims using [1], [2], etc. format
2. Clearly distinguish between established facts and emerging research
3. Include relevant warnings, contraindications, and precautions
4. If information is uncertain or conflicting, acknowledge this explicitly
5. Never provide definitive diagnoses - support clinical decision-making only
6. For drug-related queries, always mention checking for interactions
7. Respond in the same language as the query (Japanese or English)
8. Use clinical terminology but explain complex concepts when helpful
9. Prioritize patient safety in all recommendations
10. When in doubt, recommend consulting with specialists

## Important Disclaimers:
- This is a clinical decision support tool only
- Final medical decisions should always be made by qualified healthcare professionals
- Always verify critical information through authoritative sources
- Consider individual patient factors not captured in general guidelines

## Context from Medical Literature:
{context}

Based on the above context, provide a comprehensive and accurate response to the healthcare professional's query."""


class MedicalRAGPipeline:
    """
    RAG Pipeline for medical queries.
    
    Combines retrieval, reranking, and generation for accurate
    medical information with proper citations.
    """
    
    def __init__(self):
        """Initialize the RAG pipeline components."""
        self.retriever = MedicalRetriever()
        self.reranker = Reranker()
        self.generator = MedicalGenerator()
        
    async def query(
        self,
        question: str,
        language: str = "en",
        conversation_id: Optional[str] = None,
        include_sources: bool = True
    ) -> ChatResponse:
        """
        Process a medical query through the RAG pipeline.
        
        Args:
            question: The user's medical question
            language: Response language ('en' or 'ja')
            conversation_id: Optional conversation ID for context
            include_sources: Whether to include source citations
            
        Returns:
            ChatResponse with answer and citations
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        conv_id = conversation_id or str(uuid.uuid4())
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving documents for query: {question[:100]}...")
            docs = await self.retriever.retrieve(question, k=10)
            
            if not docs:
                logger.warning("No documents retrieved, using fallback response")
                return self._create_fallback_response(
                    question, query_id, conv_id, start_time
                )
            
            # Step 2: Rerank documents for relevance
            logger.info(f"Reranking {len(docs)} documents...")
            reranked_docs = await self.reranker.rerank(docs, question, top_k=5)
            
            # Step 3: Format context with citations
            context, citations = self._format_context(reranked_docs)
            
            # Step 4: Generate response
            logger.info("Generating response...")
            answer = await self.generator.generate(
                question=question,
                context=context,
                system_prompt=MEDICAL_SYSTEM_PROMPT,
                language=language
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                answer=answer,
                sources=citations if include_sources else [],
                conversation_id=conv_id,
                query_id=query_id,
                processing_time_ms=processing_time,
                model_used=settings.openai_model
            )
            
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")
            raise
    
    async def query_stream(
        self,
        question: str,
        language: str = "en",
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response for real-time output.
        
        Yields SSE-formatted chunks for streaming responses.
        """
        query_id = str(uuid.uuid4())
        conv_id = conversation_id or str(uuid.uuid4())
        
        try:
            # Retrieve and rerank
            docs = await self.retriever.retrieve(question, k=10)
            
            if not docs:
                yield f'data: {{"type": "content", "content": "I couldn\'t find relevant medical information for your query. Please try rephrasing or consult authoritative medical sources directly."}}\n\n'
                yield f'data: {{"type": "done", "query_id": "{query_id}", "conversation_id": "{conv_id}"}}\n\n'
                return
            
            reranked_docs = await self.reranker.rerank(docs, question, top_k=5)
            context, citations = self._format_context(reranked_docs)
            
            # Stream the response
            async for chunk in self.generator.generate_stream(
                question=question,
                context=context,
                system_prompt=MEDICAL_SYSTEM_PROMPT,
                language=language
            ):
                yield f'data: {{"type": "content", "content": {repr(chunk)}}}\n\n'
            
            # Send sources
            for citation in citations:
                yield f'data: {{"type": "source", "source": {citation.model_dump_json()}}}\n\n'
            
            # Done signal
            yield f'data: {{"type": "done", "query_id": "{query_id}", "conversation_id": "{conv_id}"}}\n\n'
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f'data: {{"type": "error", "error": "An error occurred while processing your query"}}\n\n'
    
    def _format_context(
        self,
        docs: List[Source]
    ) -> tuple[str, List[Citation]]:
        """
        Format retrieved documents into context string with citations.
        
        Returns:
            Tuple of (context_string, citations_list)
        """
        context_parts = []
        citations = []
        
        for i, doc in enumerate(docs, 1):
            # Extract metadata
            metadata = doc.metadata
            title = metadata.get("title", "Untitled Source")
            authors = metadata.get("authors", [])
            journal = metadata.get("journal")
            year = metadata.get("year")
            doi = metadata.get("doi")
            pmid = metadata.get("pmid")
            url = metadata.get("url")
            
            # Format context entry
            context_parts.append(f"[{i}] {title}\n{doc.content}\n")
            
            # Create citation
            citation = Citation(
                id=i,
                title=title,
                authors=authors if isinstance(authors, list) else [authors] if authors else None,
                journal=journal,
                year=int(year) if year else None,
                doi=doi,
                pmid=pmid,
                url=url,
                snippet=doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                relevance_score=doc.score
            )
            citations.append(citation)
        
        context = "\n".join(context_parts)
        return context, citations
    
    def _create_fallback_response(
        self,
        question: str,
        query_id: str,
        conversation_id: str,
        start_time: float
    ) -> ChatResponse:
        """Create a fallback response when no documents are found."""
        processing_time = int((time.time() - start_time) * 1000)
        
        return ChatResponse(
            answer=(
                "I couldn't find specific medical literature matching your query. "
                "This could be because:\n\n"
                "1. The query is too specific or uses terminology not in the database\n"
                "2. The topic may require more specialized sources\n\n"
                "**Recommendations:**\n"
                "- Try rephrasing your question with different medical terms\n"
                "- Consult authoritative sources like PubMed, UpToDate, or clinical guidelines directly\n"
                "- For drug-related queries, check official prescribing information\n\n"
                "*This response is generated without source documents. "
                "Please verify all medical information through authoritative sources.*"
            ),
            sources=[],
            conversation_id=conversation_id,
            query_id=query_id,
            processing_time_ms=processing_time,
            model_used=settings.openai_model
        )


# Singleton instance
_pipeline: Optional[MedicalRAGPipeline] = None


def get_rag_pipeline() -> MedicalRAGPipeline:
    """Get or create the RAG pipeline singleton."""
    global _pipeline
    if _pipeline is None:
        _pipeline = MedicalRAGPipeline()
    return _pipeline

