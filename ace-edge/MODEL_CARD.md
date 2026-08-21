# ACE Edge model card

ACE Edge is an experimental compact synthetic-media classifier. This repository contains training and evaluation code, not released model weights.

## Release evidence

The final gated Kaggle run completed on exactly two NVIDIA T4 GPUs. On its held-out validation partition (4,864 samples, including 720 face-manipulated samples), `face_manipulated` achieved precision 0.9347, recall 0.8750, F1 0.9039, AUROC 0.99394, and PR-AUC 0.95671. These are validation results for the stated partition, not a claim of forensic certainty or universal real-world performance.

The fixed-work benchmark used 10 fresh counterbalanced one-versus-two-GPU repetitions and measured 1.8437x median speedup (95% CI 1.8396–1.8458), exceeding the 1.35x gate.

The fixed learned class order is `likely_real`, `ai_generated`, `face_manipulated`. `inconclusive` is not a fourth class. The baseline disables reliability training and cannot support an abstention claim.

Intended use is research and educational analysis. It is not intended for identity verification, enforcement, criminal attribution, or proof that media is authentic.

Known limitation: performance on unseen AI-image generators was heterogeneous (particularly weak for VQDM). Therefore the public project is scoped as a deepfake / face-manipulation detector; `ai_generated` is exploratory and must not be used as a broad claim about all synthetic images.

The shared MobileNetV3-Large-class stack must remain at most 50 MiB FP32; INT8 target is 15 MiB. Every learned inference artifact counts. Final exports must record paths, roles, hashes, and byte sizes.

FF++ is grouped by reciprocal source family before extraction. SD 1.5, Midjourney, and VQDM are held out from fitting/calibration. SDFVD remains external-test only. Mounted bytes are rehashed and cross-split exact/near-duplicate content fails closed.

Frozen research-v1 thresholds live in `review/gates.research-v1.json`. Deployment is blocked unless every gate passes. ACE 2.4's clean SDFVD baseline—50% balanced accuracy and 0% fake recall—is retained only as historical motivation.
