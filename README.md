# ACE Edge — Adaptive Compact Evidence Engine

ACE Edge is a research reboot of the original ACE deepfake-detector prototype. It is designed to distinguish **likely real**, **AI-generated**, and **face-manipulated** media with a compact shared model. `inconclusive` is a selective decision, not a fourth learned class.

## Why the reboot exists

ACE 2.4 is preserved as a historical baseline, not a production authenticity oracle. A clean external evaluation on SDFVD exposed a serious generalization failure: 50% balanced accuracy and 0% fake recall (all 53 manipulated videos were classified as real). The earlier near-99% results were not reliable evidence of external generalization because the development pipeline used frame-level splitting, inconsistent label polarity, and post-hoc test adaptation.

ACE Edge starts again with grouped source-family splits, held-out generator families, content-hash leakage checks, fixed pre-registered release gates, and per-sample evaluation evidence.

## Current status

- Dual-T4 baseline training code is statically approved after independent review.
- Production execution must begin with a short one-versus-two-T4 smoke/throughput gate.
- The complete learned inference stack is capped at 50 MiB FP32; INT8 target is 15 MiB.
- Reliability/abstention training is currently disabled. No public deployment or `inconclusive` safety claim is approved yet.
- No new ACE Edge performance claim will be published until held-out and SDFVD gates pass.

See [`ace-edge/README.md`](ace-edge/README.md) for the training entrypoint and [`ace-edge/review/REVIEW_CHECKLIST.md`](ace-edge/review/REVIEW_CHECKLIST.md) for the frozen evaluation contract.

## Historical artifacts

The ACE 2.4 weights remain in the repository solely for reproducibility and comparison. They must not be described as generally robust or used as proof that media is authentic.

## Data and licensing

ACE Edge training uses research datasets under their respective terms, including FaceForensics++, Tiny GenImage/GenImage derivatives, Unbiased Tiny GenImage, and 140K Real and Fake Faces. SDFVD is reserved for final external evaluation. Raw datasets and private FF++ derivatives are not redistributed in this repository.

This project is research-only. A detector score is evidence for analysis, not proof of authenticity.
