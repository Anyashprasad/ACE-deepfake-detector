import unittest
import numpy as np
import pandas as pd
from ace_edge.contracts import CLASS_TO_ID
from ace_edge.data import (assert_independent, assert_all_splits_independent,
                           canonical_generator, file_sha256, manifest_digest, perceptual_hash,
                           phash_distance, raw_manifest_digest, verify_manifest_content, PHASH_VERSION)
from ace_edge.metrics import dangerous_false_real_rate, multiclass_brier, unseen_generator_metrics
from ace_edge.train import decode_sample_ids

class TestContracts(unittest.TestCase):
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
                        "phash":["0000000000000000"],"local_phash":["ffffffffffffffff"]})
        b=pd.DataFrame({"sample_id":["b"],"family_id":["fb"],"sha256":["x"],"local_sha256":["xl"],
                        "phash":["0000000000000001"],"local_phash":["aaaaaaaaaaaaaaaa"]})
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
