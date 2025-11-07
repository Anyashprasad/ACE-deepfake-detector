ACE — Adaptive Confidence Engine for Deepfake Detection
Version: ACE v2.4 (2025 Release)

A high-accuracy deepfake detection system trained on 140K real & fake faces and FaceForensics++, featuring adaptive scoring, hybrid pooling, and robust face extraction.

✅ Features

✅ High-accuracy face-based deepfake detection

✅ Works on images and videos

✅ Hybrid pooling for video consistency

✅ Adaptive threshold shifting

✅ Robust face extraction with fallback

✅ Clean API for inference

✅ Dataset Citations

Please cite the datasets used to train ACE:

Comprehensive Deepfake Detection Dataset (2025)

Islam, Md Raisul; Rakib, Md. Aminul Islam; Sahin Afridi, Arafat;
Islam, Mohammad Monirul (2025),
“Comprehensive Deepfake Detection Dataset: Real and Synthetic Frames from Roop and Akool AI Technologies”,
Mendeley Data, V1, doi: 10.17632/pdcp9mjy3z.1

FaceForensics++ (2019)

Rössler, A., Cozzolino, D., Verdoliva, L., Riess, C., Thies, J., & Nießner, M.
FaceForensics++: Learning to Detect Manipulated Facial Images, ICCV 2019.

✅ Model Versions

See the full changelog here:
👉 /docs/ACE_ChangeLog.md

Major releases:

ACE v1.0 – Initial system

ACE v2.0 – Hybrid video pooling

ACE v2.3 – Balanced FF++ + 140K training

ACE v2.4 – Unified best-performing release

✅ Basic Usage
Image Inference
from ace import predict_image
label, score = predict_image("example.jpg")

Video Inference
from ace import predict_video
label, score = predict_video("video.mp4")

✅ Performance

✔ High generalization to unseen deepfake methods

✔ Strong robustness to compression & low-res inputs

✔ Excellent face-detection fallback logic

Full evaluation results available in /results/.
