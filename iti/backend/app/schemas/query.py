from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user query or question to be answered by the RAG assistant.")
    top_k: Optional[int] = Field(default=None, ge=1, le=10, description="Optional override for number of retrieved chunks.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What is the difference between HNSW and IVF vector indexes?",
                    "top_k": 3
                }
            ]
        }
    }

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What is the difference between HNSW and IVF vector indexes?",
                    "answer": "HNSW constructs a multi-layer graph with bi-directional links for fast ANN search, whereas IVF partitions space into Voronoi cells using k-means clustering.",
                    "sources": ["vector_db_manual.md (Section 3)"],
                    "retrieved_chunks": []
                }
            ]
        }
    }

class HealthResponse(BaseModel):
    status: str
    version: str
    vector_store_loaded: bool
    ollama_connected: bool
