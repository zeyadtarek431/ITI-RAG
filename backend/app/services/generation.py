import httpx
import ollama
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.utils.logging_config import logger

class GenerationService:
    def __init__(self):
        self.ollama_host = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    def check_ollama_status(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            response = httpx.get(f"{self.ollama_host}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def build_prompt(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Constructs a grounded RAG prompt template."""
        if not retrieved_chunks:
            context_str = "No relevant document context found in the vector database."
        else:
            context_blocks = []
            for i, chunk in enumerate(retrieved_chunks, 1):
                source = chunk.get("source", "Unknown")
                content = chunk.get("content", "").strip()
                context_blocks.append(f"[Source {i}: {source}]\n{content}")
            context_str = "\n\n".join(context_blocks)

        prompt = f"""You are an expert AI documentation assistant. Answer the user's question accurately based ONLY on the provided context below. 

Instructions:
1. Every fact in your answer must be directly supported by the context.
2. Explicitly cite the sources used in your answer (e.g., [rag_architecture_guide.md]).
3. If the provided context does not contain enough information to answer the question, state: "Based on the provided documents, I do not have enough information to answer this question."

Context Information:
---------------------
{context_str}
---------------------

User Question: {question}

Grounded Answer:"""
        return prompt

    def generate_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """Synthesizes answer using Ollama LLM with fallback heuristic when Ollama is offline."""
        sources = list(set([c.get("source", "Unknown Document") for c in retrieved_chunks if c.get("source")]))
        prompt = self.build_prompt(question, retrieved_chunks)

        if self.check_ollama_status():
            try:
                logger.info(f"Calling Ollama model '{self.model}' at {self.ollama_host}...")
                client = ollama.Client(host=self.ollama_host)
                response = client.generate(model=self.model, prompt=prompt)
                answer = response.get("response", "").strip()
                if answer:
                    return answer, sources
            except Exception as e:
                logger.warning(f"Ollama call failed: {e}. Falling back to internal grounded synthesizer.")

        # Fallback Grounded Synthesizer (when Ollama service is not running locally)
        logger.info("Using internal RAG synthesis engine.")
        if not retrieved_chunks:
            return "Based on the provided documents, I do not have enough information to answer this question.", []

        # Construct synthesised response from top chunk context
        top_chunk = retrieved_chunks[0]["content"]
        answer_text = (
            f"Based on the index documentation ({', '.join(sources)}):\n\n"
            f"{top_chunk[:400]}...\n\n"
            f"*(Generated from retrieved context chunks)*"
        )
        return answer_text, sources

generation_service = GenerationService()
