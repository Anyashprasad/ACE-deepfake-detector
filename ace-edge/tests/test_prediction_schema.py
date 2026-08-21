import unittest

import numpy as np

from ace_edge.train import prediction_rows
from review.ace_edge_review import validate_predictions


class PredictionSchemaTests(unittest.TestCase):
    def test_rows_satisfy_release_reviewer_schema(self):
        rows = prediction_rows(
            np.array(["sample-1"]),
            np.array([1]),
            np.array([[0.1, 0.8, 0.1]], dtype=np.float32),
        )
        manifest = [{"sample_id": "sample-1", "split": "validation"}]
        validate_predictions(manifest, rows)
        self.assertEqual(rows[0]["predicted_class"], "ai_generated")
        self.assertEqual(rows[0]["class_id"], 1)


if __name__ == "__main__":
    unittest.main()
