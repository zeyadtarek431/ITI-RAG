from fastapi import APIRouter, HTTPException, status
from app.schemas.query import QueryRequest, QueryResponse, HealthResponse
from app.services.retrieval import retrieval_service
from app.services.generation import generation_service
from app.core.config import settings
from app.utils.logging_config import logger

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """GET /health - Verifies backend health, vector store status, and Ollama connectivity."""
    ollama_ok = generation_service.check_ollama_status()
    vector_ok = retrieval_service.is_loaded
    return HealthResponse(
        status="healthy" if vector_ok else "degraded",
        version=settings.VERSION,
        vector_store_loaded=vector_ok,
        ollama_connected=ollama_ok
    )

@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_rag(request: QueryRequest):
    """POST /query - Accepts a question, retrieves context chunks, and generates a grounded response with source citations."""
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question string cannot be empty."
        )

    logger.info(f"Received query request: '{request.question}'")

    # Step 1: Retrieve context chunks
    chunks = retrieval_service.retrieve(query_text=request.question, top_k=request.top_k)

    # Step 2: Synthesize grounded response
    answer, sources = generation_service.generate_answer(question=request.question, retrieved_chunks=chunks)

    return QueryResponse(
        question=request.question,
        answer=answer,
        sources=sources,
        retrieved_chunks=chunks
    )
