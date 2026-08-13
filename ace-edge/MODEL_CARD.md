# ACE Edge model card (pre-training)

ACE Edge is an experimental compact synthetic-media classifier. No ACE Edge weights have passed the release gate yet.

The fixed learned class order is `likely_real`, `ai_generated`, `face_manipulated`. `inconclusive` is not a fourth class. The baseline disables reliability training and cannot support an abstention claim.

Intended use is research and educational analysis. It is not intended for identity verification, enforcement, criminal attribution, or proof that media is authentic.

The shared MobileNetV3-Large-class stack must remain at most 50 MiB FP32; INT8 target is 15 MiB. Every learned inference artifact counts. Final exports must record paths, roles, hashes, and byte sizes.

FF++ is grouped by reciprocal source family before extraction. SD 1.5, Midjourney, and VQDM are held out from fitting/calibration. SDFVD remains external-test only. Mounted bytes are rehashed and cross-split exact/near-duplicate content fails closed.

Frozen research-v1 thresholds live in `review/gates.research-v1.json`. Deployment is blocked unless every gate passes. ACE 2.4's clean SDFVD baseline—50% balanced accuracy and 0% fake recall—is retained only as historical motivation.
