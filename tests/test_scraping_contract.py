import json
from pathlib import Path

from chunking import TokenChunker


FIXTURE = Path(__file__).parent / "fixtures" / "acquired_resource.json"


def test_scraping_acquired_resource_contract_can_feed_chunking():
    resource = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert set(resource) == {
        "uri",
        "media_type",
        "content_hash",
        "raw_path",
        "size",
        "retrieved_at",
        "discovered_by",
    }

    content = "A paper document. A second paragraph."
    chunks = TokenChunker().chunk(
        content,
        document_id=resource["content_hash"],
        metadata={"uri": resource["uri"], "media_type": resource["media_type"]},
        provenance=resource,
    )

    assert chunks
    assert chunks[0].document_id == resource["content_hash"]
    assert chunks[0].provenance == resource
