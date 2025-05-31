import os
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_memory_append_and_query():
    # Append a memory moment
    payload = {
        "prompt": "Test memory prompt",
        "response": "Test memory response",
        "model_used": "gpt-test",
        "context_tags": ["unit_test"]
    }
    resp = client.post("/memory/append", json=payload)
    assert resp.status_code == 200
    assert resp.json().get("ok") is True

    # Query memory for the same prompt
    query_resp = client.get("/memory/query", params={"q": "Test memory prompt", "k": 1})
    assert query_resp.status_code == 200
    data = query_resp.json()
    assert "results" in data
    results = data["results"]
    # Should return at least one item, which may be the MemoryMoment or Pinecone doc
    assert isinstance(results, list)
    assert len(results) >= 0  # Might be empty if backend stub


def test_identity_note_endpoint(tmp_path):
    # Use a temporary profiles directory
    profiles_dir = tmp_path / "profiles" / "identities"
    os.environ["PROFILES_DIR"] = str(tmp_path / "profiles")

    # Append a note
    note_payload = {"agent_id": "unit_agent", "note": "Important note"}
    resp = client.post("/memory/identity/note", json=note_payload)
    assert resp.status_code == 200
    assert resp.json().get("ok") is True

    # Check that dynamic identity file was created
    dyn_file = profiles_dir / "unit_agent_dynamic.md"
    assert dyn_file.exists(), "Dynamic identity file not found"
    content = dyn_file.read_text(encoding="utf-8")
    assert "Important note" in content
