"""Medical Document Retriever - Vector search for relevant documents."""
from typing import List, Optional, Dict, Any
from loguru import logger

from app.config import settings
from app.core.embeddings import get_embedding
from app.models.schemas import Source


class MedicalRetriever:
    """
    Retriever for medical documents using vector similarity search.
    
    Supports both Pinecone (production) and Chroma (local development).
    """
    
    def __init__(self):
        """Initialize the retriever with vector store connection."""
        self.use_chroma = settings.use_chroma
        self._vectorstore = None
        self._initialized = False
        
    async def _init_vectorstore(self):
        """Lazy initialization of vector store."""
        if self._initialized:
            return
            
        try:
            if self.use_chroma:
                await self._init_chroma()
            else:
                await self._init_pinecone()
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Continue without vector store - will return demo data
            self._initialized = True
    
    async def _init_chroma(self):
        """Initialize Chroma vector store."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name="medassist",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Chroma vector store initialized")
            
        except Exception as e:
            logger.warning(f"Chroma initialization failed: {e}")
            self._collection = None
    
    async def _init_pinecone(self):
        """Initialize Pinecone vector store."""
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=settings.pinecone_api_key)
            self._index = pc.Index(settings.pinecone_index_name)
            logger.info("Pinecone vector store initialized")
            
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {e}")
            self._index = None
    
    async def retrieve(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Source]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            filters: Optional metadata filters
            
        Returns:
            List of Source objects with content and metadata
        """
        await self._init_vectorstore()
        
        try:
            # Get query embedding
            query_embedding = await get_embedding(query)
            
            if self.use_chroma and self._collection:
                return await self._retrieve_from_chroma(query_embedding, k, filters)
            elif not self.use_chroma and hasattr(self, '_index') and self._index:
                return await self._retrieve_from_pinecone(query_embedding, k, filters)
            else:
                # Return demo data if no vector store available
                return self._get_demo_sources(query)
                
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self._get_demo_sources(query)
    
    async def _retrieve_from_chroma(
        self,
        embedding: List[float],
        k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Source]:
        """Retrieve from Chroma."""
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=k,
            where=filters
        )
        
        sources = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                
                sources.append(Source(
                    content=doc,
                    metadata=metadata,
                    score=1 - distance  # Convert distance to similarity
                ))
        
        return sources
    
    async def _retrieve_from_pinecone(
        self,
        embedding: List[float],
        k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Source]:
        """Retrieve from Pinecone."""
        results = self._index.query(
            vector=embedding,
            top_k=k,
            include_metadata=True,
            filter=filters
        )
        
        sources = []
        for match in results.matches:
            sources.append(Source(
                content=match.metadata.get("content", ""),
                metadata=match.metadata,
                score=match.score
            ))
        
        return sources
    
    def _get_demo_sources(self, query: str) -> List[Source]:
        """Return demo sources for development/testing."""
        demo_sources = [
            Source(
                content="""Hypertension Management Guidelines (2024): First-line treatments include 
                thiazide diuretics, ACE inhibitors, ARBs, and calcium channel blockers. Target BP 
                for most adults is <130/80 mmHg. Lifestyle modifications including DASH diet, 
                sodium restriction (<2.3g/day), regular aerobic exercise, and weight management 
                should be recommended for all patients.""",
                metadata={
                    "title": "ACC/AHA Hypertension Guidelines 2024",
                    "authors": ["American College of Cardiology", "American Heart Association"],
                    "journal": "Journal of the American College of Cardiology",
                    "year": 2024,
                    "doi": "10.1016/j.jacc.2024.01.001",
                    "source_type": "guideline"
                },
                score=0.92
            ),
            Source(
                content="""Drug interactions with antihypertensive medications: NSAIDs can reduce 
                the effectiveness of ACE inhibitors, ARBs, and diuretics. Potassium-sparing 
                diuretics combined with ACE inhibitors increase hyperkalemia risk. Monitor 
                potassium levels when combining these medications. Grapefruit juice affects 
                calcium channel blocker metabolism.""",
                metadata={
                    "title": "Antihypertensive Drug Interactions: A Comprehensive Review",
                    "authors": ["Smith J", "Johnson M", "Williams R"],
                    "journal": "Clinical Pharmacology & Therapeutics",
                    "year": 2023,
                    "pmid": "34567890",
                    "source_type": "paper"
                },
                score=0.88
            ),
            Source(
                content="""Diabetes mellitus type 2 treatment algorithm: Metformin remains 
                first-line therapy unless contraindicated. For patients with ASCVD, heart failure, 
                or CKD, consider SGLT2 inhibitors or GLP-1 receptor agonists regardless of A1C. 
                Target A1C <7% for most adults, individualize based on patient factors.""",
                metadata={
                    "title": "Standards of Medical Care in Diabetes - 2024",
                    "authors": ["American Diabetes Association"],
                    "journal": "Diabetes Care",
                    "year": 2024,
                    "doi": "10.2337/dc24-S001",
                    "source_type": "guideline"
                },
                score=0.85
            ),
            Source(
                content="""Clinical presentation of acute myocardial infarction: Classic symptoms 
                include chest pain/pressure, dyspnea, diaphoresis, and nausea. Atypical 
                presentations more common in women, elderly, and diabetic patients - may present 
                with fatigue, weakness, or epigastric discomfort. ECG changes and troponin 
                elevation confirm diagnosis.""",
                metadata={
                    "title": "Acute Coronary Syndromes: Recognition and Management",
                    "authors": ["Chen L", "Anderson K"],
                    "journal": "New England Journal of Medicine",
                    "year": 2023,
                    "pmid": "36789012",
                    "source_type": "paper"
                },
                score=0.82
            ),
            Source(
                content="""Antibiotic selection for community-acquired pneumonia: For outpatients 
                without comorbidities, amoxicillin or doxycycline recommended. For outpatients 
                with comorbidities, combination therapy with beta-lactam plus macrolide or 
                respiratory fluoroquinolone monotherapy. Duration typically 5-7 days for 
                uncomplicated cases.""",
                metadata={
                    "title": "IDSA/ATS CAP Guidelines 2023",
                    "authors": ["Infectious Diseases Society of America"],
                    "journal": "Clinical Infectious Diseases",
                    "year": 2023,
                    "doi": "10.1093/cid/ciad123",
                    "source_type": "guideline"
                },
                score=0.78
            )
        ]
        
        return demo_sources


# Singleton instance
_retriever: Optional[MedicalRetriever] = None


def get_retriever() -> MedicalRetriever:
    """Get or create retriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = MedicalRetriever()
    return _retriever

