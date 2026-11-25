from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def usage_entry(model, input, cache_write, cache_read, output, message_id=None, request_id=None):
    entry = {
        "type": "assistant",
        "message": {
            "model": model,
            "usage": {
                "input_tokens": input,
                "cache_creation_input_tokens": cache_write,
                "cache_read_input_tokens": cache_read,
                "output_tokens": output,
            },
        },
    }
    if message_id is not None:
        entry["message"]["id"] = message_id
    if request_id is not None:
        entry["requestId"] = request_id
    return entry


def write_transcript(tmp_path, entries):
    path = tmp_path / "transcript.jsonl"
    lines = [e if isinstance(e, str) else json.dumps(e) for e in entries]
    path.write_text("\n".join(lines))
    return path


@pytest.fixture
def transcript(tmp_path):
    return lambda entries: write_transcript(tmp_path, entries)
