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
    config_candidates = list(Path("/kaggle/input/ace-edge-training-source").glob("**/configs/kaggle_dual_t4.json"))
    if len(config_candidates) != 1:
        raise RuntimeError(f"Expected one mounted dual-T4 config, found {len(config_candidates)}")
    sys.argv = [sys.argv[0], "--config", str(config_candidates[0])]
    main()
