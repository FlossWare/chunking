"""Contracts produced by the chunking capability."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Chunk:
    """A canonical piece of a source document.

    Offsets refer to the source document's character positions. Metadata and
    provenance are deliberately untyped dictionaries so callers can preserve
    source-specific information without coupling this capability to storage or
    retrieval implementations.
    """

    id: str
    document_id: str
    sequence: int
    content: str
    token_count: int
    start_offset: int
    end_offset: int
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
