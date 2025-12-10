"""Reranker - Improve relevance of retrieved documents."""
from typing import List
from loguru import logger

from app.models.schemas import Source


class Reranker:
    """
    Reranker for improving document relevance.
    
    Uses a combination of semantic similarity and keyword matching
    to reorder retrieved documents by relevance to the query.
    """
    
    def __init__(self):
        """Initialize the reranker."""
        pass
    
    async def rerank(
        self,
        documents: List[Source],
        query: str,
        top_k: int = 5
    ) -> List[Source]:
        """
        Rerank documents by relevance to the query.
        
        Uses a hybrid scoring approach:
        1. Original vector similarity score
        2. Keyword overlap bonus
        3. Medical term matching bonus
        
        Args:
            documents: List of retrieved documents
            query: The original query
            top_k: Number of documents to return
            
        Returns:
            Reranked list of documents
        """
        if not documents:
            return []
        
        # Tokenize query
        query_terms = self._tokenize(query.lower())
        medical_terms = self._extract_medical_terms(query)
        
        scored_docs = []
        for doc in documents:
            score = self._calculate_relevance_score(
                doc, query_terms, medical_terms
            )
            scored_docs.append((doc, score))
        
        # Sort by combined score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k with updated scores
        reranked = []
        for doc, score in scored_docs[:top_k]:
            reranked.append(Source(
                content=doc.content,
                metadata=doc.metadata,
                score=score
            ))
        
        logger.debug(f"Reranked {len(documents)} -> {len(reranked)} documents")
        return reranked
    
    def _calculate_relevance_score(
        self,
        doc: Source,
        query_terms: set,
        medical_terms: set
    ) -> float:
        """
        Calculate combined relevance score for a document.
        
        Combines:
        - Original vector similarity (60% weight)
        - Keyword overlap (25% weight)
        - Medical term presence (15% weight)
        """
        # Base score from vector similarity
        base_score = doc.score * 0.6
        
        # Tokenize document
        doc_terms = self._tokenize(doc.content.lower())
        
        # Keyword overlap score
        if query_terms:
            overlap = len(query_terms & doc_terms) / len(query_terms)
            keyword_score = overlap * 0.25
        else:
            keyword_score = 0
        
        # Medical term presence score
        if medical_terms:
            med_overlap = len(medical_terms & doc_terms) / len(medical_terms)
            medical_score = med_overlap * 0.15
        else:
            medical_score = 0
        
        # Boost for title match
        title = doc.metadata.get("title", "").lower()
        title_terms = self._tokenize(title)
        title_overlap = len(query_terms & title_terms)
        title_boost = min(title_overlap * 0.05, 0.1)
        
        total_score = base_score + keyword_score + medical_score + title_boost
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _tokenize(self, text: str) -> set:
        """Simple tokenization - split on whitespace and punctuation."""
        import re
        tokens = re.findall(r'\b\w+\b', text)
        # Filter out very short tokens
        return {t for t in tokens if len(t) > 2}
    
    def _extract_medical_terms(self, text: str) -> set:
        """Extract medical terms from text."""
        # Common medical terms for boosting
        medical_keywords = {
            # Conditions
            'hypertension', 'diabetes', 'pneumonia', 'infection', 'cancer',
            'stroke', 'infarction', 'failure', 'disease', 'syndrome',
            'disorder', 'deficiency', 'inflammation', 'neoplasm',
            # Treatments
            'therapy', 'treatment', 'medication', 'drug', 'antibiotic',
            'antihypertensive', 'insulin', 'chemotherapy', 'surgery',
            # Body systems
            'cardiac', 'pulmonary', 'renal', 'hepatic', 'neurological',
            'gastrointestinal', 'cardiovascular', 'respiratory',
            # Clinical terms
            'diagnosis', 'prognosis', 'symptom', 'indication', 'contraindication',
            'dosage', 'adverse', 'interaction', 'efficacy', 'safety',
            # Japanese medical terms (romanized)
            'ketsuen', 'tounyou', 'haien', 'kansen', 'gan',
        }
        
        text_lower = text.lower()
        found_terms = set()
        
        for term in medical_keywords:
            if term in text_lower:
                found_terms.add(term)
        
        return found_terms

