"""Builds structured prompts for the LLM from retrieved context."""
from __future__ import annotations
from app.rag.retriever import RetrievedChunk

KNOWLEDGE_GAP_INSTRUCTION = (
    "NOTE: Insufficient documentation found. "
    "Tell the user you cannot find this in current approved documentation "
    "and that the query has been flagged for the Knowledge Base Manager."
)


class PromptBuilder:
    """Assembles system prompt + retrieved context + user query into LLM messages."""

    def build(
        self,
        system_prompt: str,
        query: str,
        chunks: list[RetrievedChunk],
        is_knowledge_gap: bool = False,
    ) -> list[dict]:
        """Return messages list ready for the OpenAI chat completions API."""
        context = self._format_context(chunks) if chunks else "No relevant documents found."
        system = system_prompt
        if is_knowledge_gap:
            system += f"\n\n{KNOWLEDGE_GAP_INSTRUCTION}"

        return [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"RETRIEVED DOCUMENT CONTEXT:\n"
                    f"{'='*60}\n"
                    f"{context}\n"
                    f"{'='*60}\n\n"
                    f"USER QUESTION: {query}"
                ),
            },
        ]

    def _format_context(self, chunks: list[RetrievedChunk]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            m = chunk.metadata
            header_parts = [f"[{i}]"]
            if m.get("name"):      header_parts.append(f"Document: {m['name']}")
            if m.get("section"):   header_parts.append(f"Section: {m['section']}")
            if m.get("version"):   header_parts.append(f"Version: {m['version']}")
            if m.get("approved_date"): header_parts.append(f"Approved: {m['approved_date']}")
            header = " | ".join(header_parts)
            parts.append(f"{header}\n{chunk.text}")
        return "\n\n---\n\n".join(parts)
