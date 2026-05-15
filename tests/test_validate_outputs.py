import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_outputs


class ValidateOutputsTests(unittest.TestCase):
    def test_validate_hashes_current_file_not_stale_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "config").mkdir()
            (base / "logs").mkdir()
            (base / "outputs").mkdir()

            output = base / "outputs" / "table.csv"
            original = b"stable output\n"
            output.write_bytes(original)
            expected_hash = hashlib.sha256(original).hexdigest()

            (base / "config" / "expected_outputs.json").write_text(
                json.dumps(
                    {
                        "files": [
                            {
                                "path": "outputs/table.csv",
                                "sha256": expected_hash,
                                "required": True,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (base / "logs" / "actual_manifest.json").write_text(
                json.dumps(
                    {
                        "files": [
                            {
                                "path": "outputs/table.csv",
                                "sha256": expected_hash,
                                "exists": True,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(validate_outputs.validate(base), [])

            output.write_bytes(b"corrupted output\n")
            failures = validate_outputs.validate(base)

            self.assertEqual(len(failures), 1)
            self.assertIn("Hash mismatch for outputs/table.csv", failures[0])

    def test_optional_missing_output_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "config").mkdir()
            (base / "config" / "expected_outputs.json").write_text(
                json.dumps(
                    {
                        "files": [
                            {
                                "path": "outputs/optional.json",
                                "sha256": "",
                                "required": False,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(validate_outputs.validate(base), [])


if __name__ == "__main__":
    unittest.main()
