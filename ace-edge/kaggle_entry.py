"""Kaggle script entrypoint; upload this directory with `kaggle kernels push`."""
import os
import sys
import subprocess
import hashlib
from pathlib import Path
import pandas as pd


IMAGENET_WEIGHTS_NAME = "weights_mobilenet_v3_large_224_1.0_float_no_top_v2.h5"
IMAGENET_WEIGHTS_SHA256 = "88252c55061fd4434ccc4c37fd7bb71c8832e9453190e4d8326a7adf58577411"


def resolve_backbone_weights(config, mounted_package_root):
    """Bind ImageNet initialization to the audited offline artifact before any GPU work."""
    requested = config.get("backbone_weights")
    if requested is None:
        return None
    if requested != "imagenet":
        raise ValueError(f"Unsupported Kaggle backbone_weights value: {requested!r}")
    weights = Path(mounted_package_root) / "weights" / IMAGENET_WEIGHTS_NAME
    if not weights.is_file():
        raise FileNotFoundError(f"Missing bundled ImageNet weights: {weights}")
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    if digest != IMAGENET_WEIGHTS_SHA256:
        raise RuntimeError(f"ImageNet weights SHA-256 mismatch: {digest}")
    return str(weights)

# Kaggle script kernels upload only this entry file. The reviewed package is
# mounted as a private source dataset so imports remain versioned and auditable.
source_roots = list(Path("/kaggle/input/ace-edge-training-source").glob("**/ace_edge"))
if not source_roots:
    raise RuntimeError("Missing private ace-edge-training-source input")
package_root = str(source_roots[0].parent)
sys.path.insert(0, package_root)
existing_pythonpath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = (
    f"{package_root}{os.pathsep}{existing_pythonpath}"
    if existing_pythonpath else package_root
)

if __name__ == "__main__":
    config_name = "kaggle_dual_t4.json"
    config_candidates = list(Path("/kaggle/input/ace-edge-training-source").glob(f"**/configs/{config_name}"))
    if len(config_candidates) != 1:
        raise RuntimeError(f"Expected one mounted {config_name}, found {len(config_candidates)}")
    config = __import__("json").loads(config_candidates[0].read_text())
    config["backbone_weights"] = resolve_backbone_weights(config, package_root)
    manifest_roots = [p for p in Path("/kaggle/input").rglob("ace-edge-manifests") if p.is_dir()]
    roots = [p for p in manifest_roots if (p / "train.csv").is_file()]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one mounted manifest root, found {[str(p) for p in roots]}")
    root = roots[0]
    dataset_slugs = {
        "ace-edge-ffpp-compact": "ace-edge-ffpp-compact",
        "tiny-genimage": "tiny-genimage",
        "140k-real-and-fake-faces": "140k-real-and-fake-faces",
    }
    mounted_roots = {}
    for slug in dataset_slugs:
        candidates = [path for path in Path("/kaggle/input").rglob(slug) if path.is_dir()]
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one mounted root for {slug}, found {[str(p) for p in candidates]}")
        mounted_roots[slug] = candidates[0]

    runtime_manifest_root = Path("/kaggle/working/ace-edge-runtime-manifests")
    runtime_manifest_root.mkdir(parents=True, exist_ok=True)
    manifest_names = ("train", "validation", "internal_test", "unseen_generator_test")
    for manifest_name in manifest_names:
        frame = pd.read_csv(root / f"{manifest_name}.csv", keep_default_na=False, low_memory=False)
        for column in ("path", "local_path"):
            def resolve(recorded):
                normalized = str(recorded).replace("\\", "/")
                for slug, mounted_root in mounted_roots.items():
                    marker = f"/{slug}/"
                    if marker in normalized:
                        relative = normalized.split(marker, 1)[1]
                        return str(mounted_root / Path(relative))
                raise RuntimeError(f"No declared dataset slug in recorded path: {recorded}")
            frame[column] = frame[column].map(resolve)
        missing = [path for column in ("path", "local_path") for path in frame[column] if not Path(path).is_file()]
        if missing:
            raise FileNotFoundError(f"Runtime path resolution left {len(missing)} missing files; first={missing[0]}")
        frame.to_csv(runtime_manifest_root / f"{manifest_name}.csv", index=False)

    config["train_manifest"] = str(runtime_manifest_root / "train.csv")
    config["validation_manifest"] = str(runtime_manifest_root / "validation.csv")
    config["unseen_generator_manifest"] = str(runtime_manifest_root / "unseen_generator_test.csv")
    runtime_config = Path("/kaggle/working/ace-edge-smoke-runtime.json")
    benchmark_dir = Path("/kaggle/working/ace-edge-benchmark")
    config["benchmark_report"] = str(benchmark_dir / "benchmark.json")
    runtime_config.write_text(__import__("json").dumps(config, indent=2))
    subprocess.run([sys.executable, "-m", "ace_edge.benchmark_orchestrator",
                    "--config", str(runtime_config), "--output", str(benchmark_dir)], check=True)
    # Training starts in a new process after every benchmark CUDA context exits.
    subprocess.run([sys.executable, "-m", "ace_edge.train", "--config", str(runtime_config)], check=True)
