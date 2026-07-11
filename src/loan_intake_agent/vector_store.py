"""A minimal in-memory vector store: cosine-similarity search over embedded chunks."""

import math

from pydantic import BaseModel

from .schema import Chunk


class ScoredChunk(BaseModel):
    chunk: Chunk
    score: float


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: list[list[float]] = []

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"Got {len(chunks)} chunks but {len(vectors)} vectors; counts must match.")
        self._chunks.extend(chunks)
        self._vectors.extend(vectors)

    def query(self, vector: list[float], top_k: int = 3) -> list[ScoredChunk]:
        scored = [
            ScoredChunk(chunk=chunk, score=_cosine_similarity(vector, stored))
            for chunk, stored in zip(self._chunks, self._vectors)
        ]
        scored.sort(key=lambda sc: sc.score, reverse=True)
        return scored[:top_k]
