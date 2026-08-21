import ast
import hashlib
import json
import unittest
from pathlib import Path
from pathlib import PurePosixPath


def resolve(recorded, roots):
    normalized = str(recorded).replace("\\", "/")
    for slug, mounted_root in roots.items():
        marker = f"/{slug}/"
        if marker in normalized:
            return str(PurePosixPath(mounted_root) / normalized.split(marker, 1)[1])
    raise RuntimeError(recorded)


class KagglePathResolutionTests(unittest.TestCase):
    def test_bundled_imagenet_weights_match_frozen_digest(self):
        root = Path(__file__).parents[1]
        weights = root / "weights" / "weights_mobilenet_v3_large_224_1.0_float_no_top_v2.h5"
        self.assertTrue(weights.is_file())
        self.assertEqual(
            hashlib.sha256(weights.read_bytes()).hexdigest(),
            "88252c55061fd4434ccc4c37fd7bb71c8832e9453190e4d8326a7adf58577411",
        )

    def test_offline_weights_are_resolved_before_benchmark(self):
        source = Path(__file__).parents[1].joinpath("kaggle_entry.py").read_text()
        self.assertLess(
            source.index('config["backbone_weights"] = resolve_backbone_weights'),
            source.index('"ace_edge.benchmark_orchestrator"'),
        )

    def test_new_builder_path_maps_to_flat_kernel_mount(self):
        path = "/kaggle/input/datasets/anyashprasad/ace-edge-ffpp-compact/crops/train/x.jpg"
        roots = {"ace-edge-ffpp-compact": "/kaggle/input/ace-edge-ffpp-compact"}
        self.assertEqual(resolve(path, roots), "/kaggle/input/ace-edge-ffpp-compact/crops/train/x.jpg")

    def test_unknown_dataset_fails_closed(self):
        with self.assertRaises(RuntimeError):
            resolve("/kaggle/input/unknown/x.jpg", {"tiny-genimage": "/kaggle/input/tiny-genimage"})

    def test_entry_exports_package_root_to_child_pythonpath(self):
        source = Path(__file__).parents[1].joinpath("kaggle_entry.py").read_text()
        assignments = [node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assign)]
        self.assertTrue(any("PYTHONPATH" in ast.unparse(node.targets[0]) for node in assignments))

    def test_full_config_matches_production_benchmark_contract(self):
        config = json.loads(Path(__file__).parents[1].joinpath("configs", "kaggle_dual_t4.json").read_text())
        self.assertGreaterEqual(config["benchmark_warmup_steps"], 15)
        self.assertGreaterEqual(config["benchmark_steps"], 100)
        self.assertGreaterEqual(config["benchmark_repetitions"], 10)
        self.assertEqual(config["benchmark_repetition_scope"], "fresh_process")
        self.assertGreaterEqual(config["benchmark_bootstrap_draws"], 10000)


if __name__ == "__main__":
    unittest.main()
