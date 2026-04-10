from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        matches = self.store.search(question, top_k=top_k)

        if matches:
            context_blocks = []
            for index, match in enumerate(matches, start=1):
                metadata = match.get("metadata", {})
                context_blocks.append(
                    f"[{index}] score={match.get('score', 0.0):.4f} | metadata={metadata}\n{match.get('content', '')}"
                )
            context = "\n\n".join(context_blocks)
        else:
            context = "(No relevant context retrieved.)"

        prompt = (
            "You are a helpful assistant answering from a knowledge base.\n"
            "Use only the provided context when possible, and state uncertainty when context is insufficient.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}\n\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
