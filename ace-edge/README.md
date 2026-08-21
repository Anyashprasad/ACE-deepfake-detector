# ACE Edge — compact deepfake detection

ACE Edge is a research-only, compact deepfake-detection pipeline engineered for reproducible dual-T4 Kaggle training. The release focus is face manipulation detection; it is not presented as a universal AI-image detector or as evidence that media is authentic.

## Validated result

On the held-out face-manipulation validation partition (4,864 samples; 720 face-manipulated), the final dual-T4 run achieved **0.9347 precision**, **0.8750 recall**, **0.9039 F1**, **0.99394 AUROC**, and **0.95671 PR-AUC** for the `face_manipulated` class. The distributed smoke benchmark passed with a median 1-vs-2 GPU speedup of **1.8437x** (95% CI: 1.8396–1.8458; 10 fresh counterbalanced repetitions).

The `ai_generated` class remains exploratory: it was intentionally evaluated on unseen generators and showed uneven generalisation, especially to VQDM. It is retained for research analysis, not the headline performance claim.

Canonical learned classes are `likely_real`, `ai_generated`, and `face_manipulated`. `inconclusive` is reserved for a future calibrated abstention policy and is not a fourth class. The baseline currently hard-disables the reliability loss and reports `abstention_release_ready=false`.

1. Inventory mounts: `python -m ace_edge.discover --root /kaggle/input --output /kaggle/working/input_inventory.json`
2. Supply normalized, frozen CSV manifests (schema in `ace_edge/data.py`).
3. Train: `python -m ace_edge.train --config configs/kaggle_dual_t4.json`

Install dependencies with `pip install -r requirements-kaggle.txt`. Raw media, manifests, pretrained weights, checkpoints, and predictions are intentionally excluded from Git; see `DATASET_NOTICES.md` before recreating a run.

The production entrypoint refuses anything except exactly two NVIDIA T4 GPUs.
It trains directly from `/kaggle/input`; no expensive run is started by this change. Run the fixed-work one-versus-two-GPU smoke benchmark first. Full training is allowed only when the runtime confirms exactly two T4s, at least 1.35x speedup, zero manifest-content mismatches, complete prediction coverage, healthy telemetry, and output below 2 GiB.

The independent executable review contract is in `review/`. Research-v1 gates are frozen before external evaluation; failing a gate permits a negative research report, not deployment.
