import unittest
import numpy as np
import pandas as pd
from ace_edge.contracts import CLASS_TO_ID, ensure_under_directory
from ace_edge.data import (assert_independent, assert_all_splits_independent,
                           canonical_generator, file_sha256, manifest_digest, perceptual_hash,
                           phash_distance, raw_manifest_digest, verify_manifest_content, PHASH_VERSION)
from ace_edge.metrics import dangerous_false_real_rate, multiclass_brier, unseen_generator_metrics
from ace_edge.train import decode_sample_ids, validation_ai_threshold
from ace_edge.train import bootstrap_speedup_interval

class TestContracts(unittest.TestCase):
    def test_validation_threshold_rejects_non_finite_probabilities(self):
        truth = np.array([0, 0, 1])
        probabilities = np.array([
            [.9, .1, 0.],
            [np.nan, np.nan, np.nan],
            [.1, .9, 0.],
        ])
        with self.assertRaisesRegex(RuntimeError, "non-finite"):
            validation_ai_threshold(truth, probabilities, .95)

    def test_validation_threshold_preserves_target_recall_with_ties(self):
        truth = np.array([0, 0, 0, 0, 1])
        probabilities = np.array([
            [.8, .2, 0.],
            [.8, .2, 0.],
            [.8, .2, 0.],
            [.4, .6, 0.],
            [.1, .9, 0.],
        ])
        threshold = validation_ai_threshold(truth, probabilities, .75)
        real_recall = np.mean(probabilities[truth == 0, 1] < threshold)
        self.assertGreaterEqual(real_recall, .75)

    def test_unseen_metrics_report_precision_and_f1(self):
        truth = np.array([0, 0, 1, 1])
        probabilities = np.array([
            [.9, .1, 0.],
            [.3, .7, 0.],
            [.2, .8, 0.],
            [.6, .4, 0.],
        ])
        metrics = unseen_generator_metrics(
            truth, probabilities, np.array(["real", "real", "sd_1_5", "midjourney"]), .5
        )
        self.assertAlmostEqual(metrics["precision"], .5)
        self.assertAlmostEqual(metrics["f1"], .5)

    def test_bootstrap_speedup_interval_is_deterministic(self):
        one = [100.0, 101.0, 99.0, 100.5] * 30
        dual = [150.0, 151.0, 149.0, 150.5] * 30
        first = bootstrap_speedup_interval(one, dual, seed=2401, draws=500)
        second = bootstrap_speedup_interval(one, dual, seed=2401, draws=500)
        self.assertEqual(first, second)
        self.assertGreater(first["ci95_low"], 1.35)
        self.assertLessEqual(first["ci95_low"], first["median"])
        self.assertLessEqual(first["median"], first["ci95_high"])

    def test_only_approved_kaggle_manifest_roots(self):
        ensure_under_directory("/kaggle/input/ace-edge-manifests/train.csv")
        ensure_under_directory("/kaggle/working/ace-edge-runtime-manifests/train.csv")
        with self.assertRaises(ValueError):
            ensure_under_directory("/kaggle/working/untrusted/train.csv")

    def test_bk_tree_finds_only_radius_matches(self):
        from ace_edge.data import _HammingRadiusFourIndex
        tree = _HammingRadiusFourIndex(["0000000000000000", "ffffffffffffffff"])
        self.assertTrue(tree.has_within("000000000000000f", 4))
        self.assertFalse(tree.has_within("000000000000001f", 4))

    def test_ahash_cannot_satisfy_production_leakage_gate(self):
        left = pd.DataFrame({"sample_id":["a"],"family_id":["fam-a"],"sha256":["a"],"local_sha256":["la"],
                             "phash":["0"*16],"local_phash":["0"*16],"phash_version":["ahash64-v1"]})
        right = pd.DataFrame({"sample_id":["b"],"family_id":["fam-b"],"sha256":["b"],"local_sha256":["lb"],
                              "phash":["f"*16],"local_phash":["f"*16],"phash_version":["ahash64-v1"]})
        with self.assertRaisesRegex(ValueError, "diagnostic-only"):
            assert_independent(left, right)

    def test_canonical_class_order(self):
        self.assertEqual(CLASS_TO_ID, {"likely_real":0,"ai_generated":1,"face_manipulated":2})
    def test_heldout_aliases(self):
        for alias in ("SD1.5", "SD 1.5", "stable_diffusion_1_5"):
            self.assertEqual(canonical_generator(alias), "sd_1_5")
    def test_phash_hamming(self):
        self.assertEqual(phash_distance("00", "0f"), 4)
    def test_tensorflow_byte_ids_decode(self):
        self.assertEqual(decode_sample_ids(np.array([b"sample-a"]))[0], "sample-a")
    def test_family_leak_fails(self):
        with self.assertRaises(ValueError):
            assert_independent(pd.DataFrame({"sample_id":["a"],"family_id":["f"]}),
                               pd.DataFrame({"sample_id":["b"],"family_id":["f"]}))
    def test_digest_stable_column_order(self):
        x=pd.DataFrame({"b":[2],"a":[1]}); self.assertEqual(manifest_digest(x),manifest_digest(x[["a","b"]]))
    def test_all_split_leakage(self):
        a=pd.DataFrame({"sample_id":["a"],"family_id":["fa"],"sha256":["h"],"local_sha256":["hl"],
                        "phash":["0000000000000000"],"local_phash":["ffffffffffffffff"],"phash_version":["phash64-v1"]})
        b=pd.DataFrame({"sample_id":["b"],"family_id":["fb"],"sha256":["x"],"local_sha256":["xl"],
                        "phash":["0000000000000001"],"local_phash":["aaaaaaaaaaaaaaaa"],"phash_version":["phash64-v1"]})
        with self.assertRaisesRegex(ValueError,"Perceptual"):
            assert_all_splits_independent({"train":a,"external":b})
    def test_raw_manifest_hash_binds_bytes(self):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as stream:
            stream.write(b"manifest-bytes"); name=stream.name
        try:
            self.assertEqual(raw_manifest_digest(name), "7abe730d8933f3f50dfd2b5e4d8be28fb52cad62481446b6f59860f6be7bed09")
        finally:
            import os; os.unlink(name)
    def test_recomputed_content_integrity(self):
        import tempfile, os
        from PIL import Image
        handle=tempfile.NamedTemporaryFile(suffix=".png",delete=False); handle.close()
        try:
            Image.new("RGB",(8,8),(10,20,30)).save(handle.name)
            frame=pd.DataFrame({"sample_id":["s"],"path":[handle.name],"sha256":[file_sha256(handle.name)],
                                "phash":[perceptual_hash(handle.name)],"phash_version":[PHASH_VERSION],
                                "local_path":[handle.name],"local_valid":[0],
                                "local_sha256":[file_sha256(handle.name)],"local_phash":[perceptual_hash(handle.name)],
                                "local_phash_version":[PHASH_VERSION]})
            self.assertEqual(verify_manifest_content(frame,"raw")["verified"],1)
            frame.loc[0,"sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"integrity"):
                verify_manifest_content(frame,"raw")
        finally: os.unlink(handle.name)
    def test_unseen_metric_suite(self):
        y=np.array([0,0,1,1]); p=np.array([[.9,.1,0],[.8,.2,0],[.1,.9,0],[.4,.6,0]])
        result=unseen_generator_metrics(y,p,np.array(["real","real","sd_1_5","midjourney"]))
        self.assertEqual(result["balanced_accuracy"],1.0)
        self.assertEqual(set(result["per_generator_recall"]),{"sd_1_5","midjourney"})
    def test_cross_role_local_exact_leakage(self):
        a=pd.DataFrame({"sample_id":["a"],"family_id":["fa"],"sha256":["global-a"],"local_sha256":["shared"],
                        "phash":["0000000000000000"],"local_phash":["ffffffffffffffff"]})
        b=pd.DataFrame({"sample_id":["b"],"family_id":["fb"],"sha256":["shared"],"local_sha256":["local-b"],
                        "phash":["aaaaaaaaaaaaaaaa"],"local_phash":["5555555555555555"]})
        with self.assertRaisesRegex(ValueError,"Exact"):
            assert_independent(a,b)
    def test_metrics(self):
        y=np.array([0,1,2]); p=np.array([[.9,.05,.05],[.6,.3,.1],[.1,.1,.8]])
        self.assertEqual(dangerous_false_real_rate(y,p),.5); self.assertGreater(multiclass_brier(y,p),0)

if __name__ == "__main__": unittest.main()
