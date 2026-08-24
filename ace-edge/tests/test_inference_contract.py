import tempfile
import unittest
from pathlib import Path

from ace_edge.inference import RELEASE_WEIGHTS_SHA256, sha256_file


class ReleaseInferenceContractTests(unittest.TestCase):
    def test_release_digest_is_frozen(self):
        self.assertEqual(
            RELEASE_WEIGHTS_SHA256,
            "cc88d6e5a5a744a7e51645787a34f5c3c077c1d7e7ea6f53a532bdf2f02052fa",
        )

    def test_streaming_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "artifact.bin"
            artifact.write_bytes(b"ace-edge")
            self.assertEqual(
                sha256_file(artifact),
                "6fc40efea4119ca4da5ebfb74a27c9c253c10ca13b48c1e48a97ef2bae31d89b",
            )


if __name__ == "__main__":
    unittest.main()
