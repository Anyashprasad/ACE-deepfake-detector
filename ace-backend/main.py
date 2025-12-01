from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import tensorflow as tf
import uvicorn
import tempfile
import os
from utils.preprocess import prepare_image

# ============================================
# CONFIG
# ============================================
MODEL_PATH = "model/ACE_2.4_faces_best.keras"
THRESHOLD = 0.5

# ============================================
# APP INIT
# ============================================
app = FastAPI(
    title="ACE 2.4 Deepfake Detection API",
    description="Backend API for detecting deepfakes using ACE 2.4 model.",
    version="2.4"
)

# Allow your Lovable frontend or local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# LOAD MODEL
# ============================================
print("🔄 Loading ACE 2.4 model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

# Warm up model
_dummy = np.zeros((1, 299, 299, 3), dtype=np.float32)
_ = model.predict(_dummy, verbose=0)
print("🔥 Model ready for inference.")

# ============================================
# ROUTES
# ============================================

@app.get("/")
def home():
    """Base endpoint to verify API is running."""
    return {"message": "ACE 2.4 Deepfake Detection API is running ✅"}

@app.get("/health")
def health():
    return {"status": "ok", "model": "ACE 2.4"}

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    """Detect deepfake probability in an image."""
    try:
        data = await file.read()
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        inp = prepare_image(img)
        pred = float(model.predict(inp, verbose=0)[0][0])
        
        # MODEL HAS INVERTED POLARITY:
        # High scores (~1.0) = REAL images
        # Low scores (~0.0) = FAKE images
        label = "REAL" if pred >= THRESHOLD else "FAKE"
        
        # Return confidence as distance from threshold for consistency
        # For REAL: confidence = pred
        # For FAKE: confidence = 1 - pred
        confidence = pred if label == "REAL" else (1 - pred)

        return {"label": label, "confidence": round(confidence, 5)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/video")
async def predict_video(file: UploadFile = File(...)):
    """Detect deepfake probability in a video (temporal fusion)."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            video_path = tmp.name

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Unable to read video")

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        idxs = np.linspace(0, max(1, total-1), 12, dtype=int)
        scores = []

        for i in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, frame = cap.read()
            if not ok:
                continue
            inp = prepare_image(frame)
            score = float(model.predict(inp, verbose=0)[0][0])
            scores.append(score)

        cap.release()
        os.remove(video_path)

        if not scores:
            raise HTTPException(status_code=400, detail="No frames could be processed")

        # temporal fusion: mean + max + 75th percentile
        final_score = 0.3*np.max(scores) + 0.5*np.mean(scores) + 0.2*np.percentile(scores, 75)
        
        # MODEL HAS INVERTED POLARITY (same as images)
        label = "REAL" if final_score >= THRESHOLD else "FAKE"
        confidence = final_score if label == "REAL" else (1 - final_score)

        return {
            "label": label,
            "confidence": round(confidence, 5),
            "frames_used": len(scores)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
