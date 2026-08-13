"""Kaggle script entrypoint; upload this directory with `kaggle kernels push`."""
import sys
from pathlib import Path

# Kaggle script kernels upload only this entry file. The reviewed package is
# mounted as a private source dataset so imports remain versioned and auditable.
source_roots = list(Path("/kaggle/input/ace-edge-training-source").glob("**/ace_edge"))
if not source_roots:
    raise RuntimeError("Missing private ace-edge-training-source input")
sys.path.insert(0, str(source_roots[0].parent))

from ace_edge.train import main

if __name__ == "__main__":
    config_name = "kaggle_smoke_dual_t4.json"
    config_candidates = list(Path("/kaggle/input/ace-edge-training-source").glob(f"**/configs/{config_name}"))
    if len(config_candidates) != 1:
        raise RuntimeError(f"Expected one mounted {config_name}, found {len(config_candidates)}")
    config = __import__("json").loads(config_candidates[0].read_text())
    manifest_roots = [p for p in Path("/kaggle/input").rglob("ace-edge-manifests") if p.is_dir()]
    roots = [p for p in manifest_roots if (p / "train.csv").is_file()]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one mounted manifest root, found {[str(p) for p in roots]}")
    root = roots[0]
    config["train_manifest"] = str(root / "train.csv")
    config["validation_manifest"] = str(root / "validation.csv")
    config["unseen_generator_manifest"] = str(root / "unseen_generator_test.csv")
    runtime_config = Path("/kaggle/working/ace-edge-smoke-runtime.json")
    runtime_config.write_text(__import__("json").dumps(config, indent=2))
    sys.argv = [sys.argv[0], "--config", str(runtime_config)]
    main()
