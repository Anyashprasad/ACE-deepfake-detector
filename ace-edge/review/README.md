# ACE Edge independent pre-GPU review

This package implements fail-closed checks for the evidence that must exist before an
ACE Edge production training run or public release. It intentionally depends only on
the Python standard library so it can run locally, in CI, and in Kaggle.

## Commands

```powershell
python -m unittest discover -s tests -v
python ace_edge_review.py preflight --manifest manifest.csv --contract contract.json --run-config run.json
python ace_edge_review.py release --manifest manifest.csv --contract contract.json --run-config run.json --predictions validation_predictions.csv --artifacts artifacts.json --metrics metrics.json --gates gates.json
```

All checks fail closed. Missing provenance, an unknown label, a held-out generator in
fit/calibration, cross-split hashes/families, incomplete distributed validation, or an
unaccounted learned artifact is an error rather than a warning.

Required contracts and evidence are documented in `REVIEW_CHECKLIST.md`.
