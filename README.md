# chunking

Canonical document-to-chunk capability for FlossWare.

This repository owns deterministic, reusable chunking behavior. It intentionally has no embedding, storage, retrieval, or model-provider concerns.

## Scope

- Sentence-aware chunking
- Approximate token-bounded chunk sizes
- Configurable overlap
- Long-segment splitting
- Stable chunk contract with offsets and metadata

The reference implementation uses only the Python standard library.
