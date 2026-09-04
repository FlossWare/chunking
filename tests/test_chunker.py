from chunking import TokenChunker


def assert_chunk_invariants(text, chunks, max_tokens):
    assert chunks
    for sequence, chunk in enumerate(chunks):
        assert chunk.sequence == sequence
        assert chunk.start_offset < chunk.end_offset
        assert text[chunk.start_offset : chunk.end_offset] == chunk.content
        assert chunk.token_count <= max_tokens


def test_empty_content_returns_no_chunks():
    assert TokenChunker().chunk("") == []


def test_chunk_has_contract_and_offsets():
    text = "First sentence. Second sentence."
    chunks = TokenChunker().chunk(text, document_id="doc-1", max_tokens=10, overlap=1)
    assert chunks
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].content == text
    assert chunks[0].start_offset == 0
    assert chunks[0].end_offset == len(text)
    assert chunks[0].id == "doc-1:0"
    assert_chunk_invariants(text, chunks, 10)


def test_automatic_document_id_is_deterministic():
    text = "Deterministic Unicode: café 東京."
    first = TokenChunker().chunk(text, max_tokens=4, overlap=1)
    second = TokenChunker().chunk(text, max_tokens=4, overlap=1)
    assert first == second
    assert first[0].document_id
    assert_chunk_invariants(text, first, 4)


def test_long_segment_uses_requested_overlap():
    text = "x" * 100
    chunks = TokenChunker().chunk(text, document_id="long", max_tokens=10, overlap=2)
    assert len(chunks) > 1
    for previous, current in zip(chunks, chunks[1:]):
        assert previous.end_offset - current.start_offset == 8
        assert current.start_offset < current.end_offset
    assert_chunk_invariants(text, chunks, 10)


def test_sentence_boundaries_include_question_and_exclamation():
    text = "First? Second! Third."
    ranges = TokenChunker._split_sentences(text)
    assert [text[start:end] for start, end in ranges] == ["First?", " Second!", " Third."]


def test_sentence_packing_never_exceeds_max_tokens_or_emits_redundant_tail():
    text = "A" * 15 + "." + " B" * 8 + "." + " C" * 14 + "."
    chunks = TokenChunker().chunk(text, document_id="bounded", max_tokens=10, overlap=5)
    assert len(chunks) >= 2
    assert_chunk_invariants(text, chunks, 10)
    for previous, current in zip(chunks, chunks[1:]):
        assert current.content not in previous.content
        assert previous.content not in current.content


def test_unicode_offsets_and_metadata_are_preserved():
    text = "Unicode café 東京. Next line."
    metadata = {"uri": "file://exports/papers/example.pdf", "media_type": "application/pdf"}
    provenance = {"source": "scraping", "content_hash": "abc123"}
    chunks = TokenChunker().chunk(
        text, document_id="doc", max_tokens=20, overlap=1, metadata=metadata, provenance=provenance
    )
    assert chunks[0].content == text
    assert chunks[0].start_offset == 0
    assert chunks[0].end_offset == len(text)
    assert chunks[0].metadata == metadata
    assert chunks[0].provenance == provenance
    assert_chunk_invariants(text, chunks, 20)


def test_invalid_configuration_is_rejected():
    chunker = TokenChunker()
    for kwargs in ({"max_tokens": 0}, {"max_tokens": 10, "overlap": -1}, {"max_tokens": 10, "overlap": 10}):
        try:
            chunker.chunk("text", **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
