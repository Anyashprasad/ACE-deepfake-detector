# ACE Edge training source

Research-only, compact three-class synthetic-media pipeline. ACE 2.4 remains frozen as a failed external baseline; it is not a production oracle.

Canonical learned classes are `likely_real`, `ai_generated`, and `face_manipulated`. `inconclusive` is reserved for a future calibrated abstention policy and is not a fourth class. The baseline currently hard-disables the reliability loss and reports `abstention_release_ready=false`.

1. Inventory mounts: `python -m ace_edge.discover --root /kaggle/input --output /kaggle/working/input_inventory.json`
2. Supply normalized, frozen CSV manifests (schema in `ace_edge/data.py`).
3. Train: `python -m ace_edge.train --config configs/kaggle_dual_t4.json`

The production entrypoint refuses anything except exactly two NVIDIA T4 GPUs.
It trains directly from `/kaggle/input`; no expensive run is started by this change. Run the fixed-work one-versus-two-GPU smoke benchmark first. Full training is allowed only when the runtime confirms exactly two T4s, at least 1.35x speedup, zero manifest-content mismatches, complete prediction coverage, healthy telemetry, and output below 2 GiB.

The independent executable review contract is in `review/`. Research-v1 gates are frozen before external evaluation; failing a gate permits a negative research report, not deployment.
