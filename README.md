# ace-1-20m-deepfake-detector
Xception‑based deepfake image detector using transfer learning and mixed precision; best model by validation AUC; test results verified.

ACE_1_20M: Xception-based Deepfake Detector
ACE_1_20M is a binary image classifier that predicts whether a face image is real or fake using an Xception CNN backbone fine‑tuned via transfer learning. It was trained and selected by validation AUC, then verified on a held‑out test split with perfect scores.

What this is
Model file: Ace_1_20m.keras (single‑file Keras format).

Task: Binary classification — real (0) vs fake (1).

Backbone: Xception CNN with depthwise‑separable convolutions for efficient, high‑accuracy vision features.

Training approach: Transfer learning from an ImageNet‑pretrained backbone, mixed‑precision training on GPU, early stopping, and best‑checkpoint selection by validation AUC.

Dataset
Source: FaceForensics++ (FF++) derived image dataset prepared into train/val/test with class subfolders.

Test split used for final reporting: 1,010 images total (616 fake, 394 real).

Note: Images are face‑centric frames extracted and organized into “real/” and “fake/” subfolders per split.

Results
Test accuracy: 100% (all 1,010 images correctly classified at threshold 0.5).

Test ROC AUC: 1.00 (perfect ranking of fakes above reals across thresholds).

Confusion matrix (test):

Fake: 616 correct, 0 incorrect.

Real: 394 correct, 0 incorrect.

Intended use
Educational and research use for deepfake detection on image frames.

Not a drop‑in production forensic tool; performance on other datasets or distribution shifts may differ.

How to load and use
Requirements: Python 3, TensorFlow/Keras compatible with the .keras format.

Load the model in Keras and pass preprocessed 299×299 RGB images.

Preprocessing: Use the official Xception preprocessing and the 299×299 input size to match training.

Example (Python):

python
import tensorflow as tf
from tensorflow.keras.applications.xception import preprocess_input
import numpy as np, cv2

model = tf.keras.models.load_model("Ace_1_20m.keras")

img = cv2.imread("path/to/image.jpg")[:, :, ::-1]          # BGR->RGB
img = cv2.resize(img, (299, 299)).astype("float32")
x = preprocess_input(img[None, ...])                        # shape (1,299,299,3)
p_fake = float(model.predict(x, verbose=0)[0][0])           # probability of fake (1)
label = "fake" if p_fake >= 0.5 else "real"
print({"prob_fake": p_fake, "label": label})
File info
Filename: Ace_1_20m.keras

Format: Keras single‑file model (architecture, weights, and config bundled).
