import hashlib
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def validate():
    expected = load_json(BASE_DIR / "config" / "expected_outputs.json")
    failures = []
    for item in expected["files"]:
        path = item["path"]
        required = item.get("required", True)
        expected_hash = item.get("sha256", "")
        output_path = BASE_DIR / path
        if not output_path.exists():
            if required:
                failures.append(f"Missing required output: {path}")
            continue
        actual_hash = sha256_file(output_path)
        if expected_hash and actual_hash != expected_hash:
            failures.append(f"Hash mismatch for {path}: expected {expected_hash}, got {actual_hash}")
    return failures

if __name__ == "__main__":
    failures = validate()
    if failures:
        print("VALIDATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)
    print("VALIDATION PASSED")
