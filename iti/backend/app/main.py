from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.query import router as query_router
from app.services.retrieval import retrieval_service
from app.utils.logging_config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize vector store & model state on application startup."""
    logger.info("Starting up FastAPI backend server...")
    logger.info("Loading vector store and embedding model into memory...")
    retrieval_service.initialize()
    logger.info("Startup complete. API is ready to process queries.")
    yield
    logger.info("Shutting down FastAPI backend server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade RAG Document Assistant FastAPI service.",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(query_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
