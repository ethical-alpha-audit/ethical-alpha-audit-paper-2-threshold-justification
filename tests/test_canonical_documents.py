"""Checks for canonical document metadata that can be validated from git."""
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _canonical_notebook_entries():
    current = None
    text = (ROOT / "canonical_documents.yaml").read_text(encoding="utf-8")
    for line in text.splitlines():
        filename_match = re.match(r"\s*- filename: (notebooks/.+\.ipynb)", line)
        if filename_match:
            current = {"filename": filename_match.group(1)}
            continue

        if current is None:
            continue

        hash_match = re.match(r"\s*canonical_sha256: ([0-9a-f]{64})", line)
        if hash_match:
            current["canonical_sha256"] = hash_match.group(1)
            continue

        size_match = re.match(r"\s*size_bytes: ([0-9]+)", line)
        if size_match:
            current["size_bytes"] = int(size_match.group(1))
            yield current
            current = None


def test_canonical_notebook_hashes_match_tracked_files():
    entries = list(_canonical_notebook_entries())

    assert entries, "No canonical notebook entries found"
    for entry in entries:
        path = ROOT / entry["filename"]
        data = path.read_bytes()

        assert hashlib.sha256(data).hexdigest() == entry["canonical_sha256"]
        assert len(data) == entry["size_bytes"]
