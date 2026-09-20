import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from app.core.config import settings
from app.utils.logging_config import logger

class RetrievalService:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedder = None
        self.is_loaded = False

    def initialize(self):
        """Loads vector store and embedding model on startup (FastAPI Lifespan)."""
        try:
            logger.info(f"Initializing embedding model '{settings.EMBEDDING_MODEL_NAME}' on CPU...")
            self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device='cpu')
            
            logger.info(f"Connecting to ChromaDB at '{settings.PERSIST_DIRECTORY}'...")
            os.makedirs(settings.PERSIST_DIRECTORY, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.PERSIST_DIRECTORY)
            
            # Load or create collection
            self.collection = self.client.get_or_create_collection(name=settings.COLLECTION_NAME)
            self.is_loaded = True
            logger.info(f"ChromaDB collection '{settings.COLLECTION_NAME}' loaded. Total items: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Failed to initialize RetrievalService: {e}")
            self.is_loaded = False

    def retrieve(self, query_text: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant context chunks for the input query."""
        if not self.is_loaded or self.collection is None:
            logger.warning("RetrievalService requested before initialization or empty database.")
            return []

        k = top_k or settings.DEFAULT_TOP_K
        total_count = self.collection.count()
        if total_count == 0:
            logger.warning("Vector store is empty. Returning 0 retrieved chunks.")
            return []

        actual_k = min(k, total_count)
        
        # Generate query vector
        query_vector = self.embedder.encode(query_text).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, dists):
                chunks.append({
                    "content": doc,
                    "metadata": meta,
                    "source": meta.get("source", "Unknown Document"),
                    "score": round(1.0 - float(dist), 4) if dist is not None else 1.0
                })
                
        return chunks

retrieval_service = RetrievalService()
