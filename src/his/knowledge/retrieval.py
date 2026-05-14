from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from his.config import settings
from his.knowledge.ingestion import iter_manual_texts


@dataclass(frozen=True)
class ManualChunk:
    source: str
    text: str
    score: int


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_%-]+", text.lower()) if len(token) > 2}


def _chunk_text(source: str, text: str, chunk_size: int = 900) -> list[ManualChunk]:
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    chunks: list[ManualChunk] = []
    buffer = ""
    for paragraph in paragraphs:
        if len(buffer) + len(paragraph) > chunk_size and buffer:
            chunks.append(ManualChunk(source=source, text=buffer.strip(), score=0))
            buffer = ""
        buffer += paragraph + "\n\n"
    if buffer.strip():
        chunks.append(ManualChunk(source=source, text=buffer.strip(), score=0))
    return chunks


def load_chunks(manuals_dir: Path | None = None) -> list[ManualChunk]:
    directory = manuals_dir or settings.manuals_dir
    chunks: list[ManualChunk] = []
    for source, text in iter_manual_texts(directory):
        chunks.extend(_chunk_text(source, text))
    return chunks


def query_manual(question: str, top_k: int = 3, manuals_dir: Path | None = None) -> list[dict[str, str | int]]:
    query_tokens = _tokenize(question)
    scored: list[ManualChunk] = []
    for chunk in load_chunks(manuals_dir):
        chunk_tokens = _tokenize(chunk.text)
        overlap = len(query_tokens & chunk_tokens)
        phrase_bonus = sum(1 for token in query_tokens if token in chunk.text.lower())
        score = overlap * 3 + phrase_bonus
        if score > 0:
            scored.append(ManualChunk(source=chunk.source, text=chunk.text, score=score))

    scored.sort(key=lambda item: item.score, reverse=True)
    return [
        {
            "source": item.source,
            "score": item.score,
            "excerpt": item.text[:900],
        }
        for item in scored[:top_k]
    ]
