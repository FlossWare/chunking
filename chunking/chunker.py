"""Sentence-aware token-bounded chunking."""

from __future__ import annotations

import re
import uuid
from typing import Any

from .types import Chunk

_CHARS_PER_TOKEN = 4
_BOUNDARY_RE = re.compile(r".*?(?:\. |\n|$)", re.DOTALL)


class TokenChunker:
    """Split text into overlapping, approximately token-bounded chunks."""

    def chunk(
        self,
        content: str,
        *,
        document_id: str | None = None,
        max_tokens: int = 512,
        overlap: int = 50,
        metadata: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> list[Chunk]:
        if not content:
            return []
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= max_tokens:
            raise ValueError("overlap must be smaller than max_tokens")

        document_id = document_id or str(uuid.uuid4())
        max_chars = max_tokens * _CHARS_PER_TOKEN
        overlap_chars = overlap * _CHARS_PER_TOKEN
        segments = self._split_sentences(content)

        ranges: list[tuple[int, int]] = []
        current_start: int | None = None
        current_end = 0
        current_segments: list[tuple[int, int]] = []

        def flush() -> None:
            nonlocal current_start, current_end, current_segments
            if current_start is not None:
                ranges.append((current_start, current_end))
            current_start = None
            current_end = 0
            current_segments = []

        for start, end in segments:
            length = end - start
            if length > max_chars:
                flush()
                for pos in range(start, end, max_chars):
                    ranges.append((pos, min(pos + max_chars, end)))
                continue

            if current_start is not None and current_end - current_start + length > max_chars:
                old_segments = current_segments
                flush()
                if overlap_chars:
                    tail: list[tuple[int, int]] = []
                    total = 0
                    for seg_start, seg_end in reversed(old_segments):
                        seg_len = seg_end - seg_start
                        if total + seg_len > overlap_chars:
                            break
                        tail.append((seg_start, seg_end))
                        total += seg_len
                    tail.reverse()
                    if tail:
                        current_start = tail[0][0]
                        current_end = tail[-1][1]
                        current_segments = tail

            if current_start is None:
                current_start = start
            current_end = end
            current_segments.append((start, end))

        flush()

        chunks: list[Chunk] = []
        for sequence, (start, end) in enumerate(ranges):
            text = content[start:end]
            chunks.append(
                Chunk(
                    id=f"{document_id}:{sequence}",
                    document_id=document_id,
                    sequence=sequence,
                    content=text,
                    token_count=max(1, (len(text) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN),
                    start_offset=start,
                    end_offset=end,
                    metadata=dict(metadata or {}),
                    provenance=dict(provenance or {}),
                )
            )
        return chunks

    def chunk_text(self, content: str, *, max_tokens: int = 512, overlap: int = 50) -> list[str]:
        """Compatibility convenience returning only chunk text."""
        return [c.content for c in self.chunk(content, max_tokens=max_tokens, overlap=overlap)]

    @staticmethod
    def _split_sentences(text: str) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        offset = 0
        for match in _BOUNDARY_RE.finditer(text):
            if match.start() != offset:
                continue
            end = match.end()
            if end > offset:
                ranges.append((offset, end))
            offset = end
            if offset >= len(text):
                break
        if offset < len(text):
            ranges.append((offset, len(text)))
        return ranges
