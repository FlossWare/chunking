from chunking import TokenChunker


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


def test_invalid_configuration_is_rejected():
    chunker = TokenChunker()
    for kwargs in ({"max_tokens": 0}, {"max_tokens": 10, "overlap": -1}, {"max_tokens": 10, "overlap": 10}):
        try:
            chunker.chunk("text", **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
