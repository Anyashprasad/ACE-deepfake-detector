import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ace_edge_review import (  # noqa: E402
    ReviewError,
    validate_artifacts,
    validate_contract,
    validate_manifest,
    validate_predictions,
    validate_release,
    validate_run_config,
)


def row(sample_id, split, label, digest, phash, **extra):
    return {"sample_id": sample_id, "split": split, "class_name": label, "sha256": digest, "phash": phash, "dataset": "tiny_genimage", **extra}


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            row("a", "train", "likely_real", "a" * 64, "0000000000000000", generator="adm"),
            row("b", "validation", "ai_generated", "b" * 64, "ffffffffffffffff", generator="biggan"),
        ]

    def test_contract_rejects_fourth_class(self):
        with self.assertRaises(ReviewError):
            validate_contract({"class_order": ["likely_real", "ai_generated", "face_manipulated", "inconclusive"], "inconclusive_semantics": "class", "probability_semantics": "softmax_p_class"})

    def test_heldout_generator_rejected_from_fit(self):
        rows = self.rows + [row("c", "train", "ai_generated", "c" * 64, "aaaaaaaaaaaaaaaa", generator="SD-1.5")]
        with self.assertRaisesRegex(ReviewError, "held-out generator"):
            validate_manifest(rows)

    def test_family_cross_split_rejected(self):
        rows = [dict(self.rows[0], family_id="001_002"), dict(self.rows[1], family_id="001_002")]
        with self.assertRaisesRegex(ReviewError, "family"):
            validate_manifest(rows)

    def test_exact_and_perceptual_leakage_rejected(self):
        exact = [self.rows[0], dict(self.rows[1], sha256="a" * 64)]
        with self.assertRaisesRegex(ReviewError, "exact duplicate"):
            validate_manifest(exact)
        near = [self.rows[0], dict(self.rows[1], phash="0000000000000001")]
        with self.assertRaisesRegex(ReviewError, "perceptual duplicate"):
            validate_manifest(near)

    def test_sdfvd_rejected_outside_external_test(self):
        rows = [dict(self.rows[0], dataset="SDFVD")]
        with self.assertRaisesRegex(ReviewError, "external_test"):
            validate_manifest(rows)

    def test_validation_requires_complete_global_gather(self):
        predictions = [{"sample_id": "b", "p_likely_real": "0.1", "p_ai_generated": "0.8", "p_face_manipulated": "0.1", "predicted_class": "ai_generated"}]
        validate_predictions(self.rows, predictions)
        with self.assertRaisesRegex(ReviewError, "missing"):
            validate_predictions(self.rows + [row("c", "validation", "face_manipulated", "c" * 64, "aaaaaaaaaaaaaaaa")], predictions)

    def test_dual_t4_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.csv"
            manifest.write_text("sample_id\n", encoding="utf-8")
            digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            config = {
                "manifest_sha256": digest, "devices": ["NVIDIA T4", "NVIDIA T4"], "replicas": 2,
                "global_batch_size": 64, "per_replica_batch_size": 32, "mixed_precision": "fp16",
                "output_dtype": "fp32", "loss_dtype": "fp32",
                "sampler_audit": {"replicas": 2, "steps_checked": 5, "cross_replica_collisions": 0},
                "learning_rate": {"scaled_from_global_batch": 64, "effective": .001},
                "throughput_benchmark": {"one_gpu_examples_s": 100, "two_gpu_examples_s": 170, "minimum_speedup": 1.5},
                "gpu_utilization": [90, 91], "examples_per_second": 170, "peak_memory_bytes": [1, 1], "epoch_duration_seconds": 10,
            }
            validate_run_config(config, manifest)
            config["devices"] = ["NVIDIA T4"]
            with self.assertRaisesRegex(ReviewError, "exactly two"):
                validate_run_config(config, manifest)

    def test_complete_stack_size_accounting(self):
        validate_artifacts({"learned_stack_complete": True, "learned_artifacts": [
            {"name": "classifier", "format": "fp32", "role": "classifier", "bytes": 40 * 1024 * 1024, "sha256": "x"},
            {"name": "detector", "format": "fp32", "role": "detector", "bytes": 9 * 1024 * 1024, "sha256": "y"},
        ]})
        with self.assertRaisesRegex(ReviewError, "limit"):
            validate_artifacts({"learned_stack_complete": True, "learned_artifacts": [
                {"name": "classifier", "format": "fp32", "role": "classifier", "bytes": 51 * 1024 * 1024, "sha256": "x"},
            ]})

    def test_release_gate_is_numeric_and_fail_closed(self):
        gates = {
            "frozen_before_external_evaluation": True,
            "heldout_ai_auc_min": .65, "heldout_face_auc_min": .65, "ai_recall_min": .25,
            "face_recall_min": .25, "dangerous_false_real_max": .2,
            "selective_coverage_min": .7,
            "abstention_false_real_reduction_min": .05, "int8_balanced_accuracy_drop_max": .03,
            "sdfvd_balanced_accuracy_gain_min": .1, "sdfvd_fake_recall_gain_min": .2,
        }
        metrics = {
            "heldout_ai_auc": .8, "heldout_face_auc": .8, "ai_recall": .7, "face_recall": .7,
            "dangerous_false_real": .1, "abstention_false_real_reduction": .1,
            "selective_coverage": .8,
            "int8_balanced_accuracy_drop": .01, "sdfvd_balanced_accuracy_gain_vs_ace24": .2,
            "sdfvd_fake_recall_gain_vs_ace24": .5,
        }
        validate_release(metrics, gates)
        metrics["face_recall"] = 0
        with self.assertRaisesRegex(ReviewError, "release blocked"):
            validate_release(metrics, gates)


if __name__ == "__main__":
    unittest.main()
