# ACE 2.4 Backend - Deepfake Detection API

FastAPI backend for ACE 2.4 deepfake detection system using Xception CNN trained on 140K images.

## Features

- 🔍 Image deepfake detection
- 🎬 Video deepfake detection (temporal fusion)
- 🚀 Fast inference with TensorFlow 2.20
- 📊 99.97% validation AUC
- 🐳 Docker ready

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **ML**: TensorFlow 2.20, OpenCV
- **Model**: Xception CNN (256MB)
- **Preprocessing**: Center crop + Xception normalization

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server runs on http://localhost:8000
```

### Docker

```bash
# Build image
docker build -t ace24-backend .

# Run container
docker run -p 8000:8000 ace24-backend
```

## API Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "ok", "model": "ACE 2.4"}
```

### Predict Image
```bash
POST /predict/image
Content-Type: multipart/form-data

# Response:
{
  "label": "REAL" | "FAKE",
  "confidence": 0.9876
}
```

### Predict Video
```bash
POST /predict/video
Content-Type: multipart/form-data

# Response:
{
  "label": "REAL" | "FAKE",
  "confidence": 0.9543,
  "frames_used": 12
}
```

## Model Details

**Architecture**: Xception CNN  
**Input**: 299x299 RGB images  
**Training**: 140K real + fake faces  
**Polarity**: Inverted (high score = REAL)

### Performance Metrics
- Accuracy: 99.49%
- AUC: 99.97%
- Precision: 99.33%
- Recall: 99.64%

### ⚠️ Important: Inverted Polarity

**The model has inverted output polarity:**
- High scores (~1.0) = **REAL** images
- Low scores (~0.0) = **FAKE** images

This is a common occurrence in binary classifiers depending on how labels were encoded during training.

**Example outputs:**
```python
# Real image
model.predict(real_img) → 0.998  # High score
label = "REAL" if score >= 0.5 else "FAKE"  # ✅ REAL

# Fake image  
model.predict(fake_img) → 0.013  # Low score
label = "REAL" if score >= 0.5 else "FAKE"  # ✅ FAKE
```

**Validation:**
- Avg REAL score: **0.998**
- Avg FAKE score: **0.013**
- Test accuracy: **100%** (30 real + 30 fake images)

The model is working perfectly - the polarity is just inverted from typical conventions. The backend correctly handles this with inverted threshold logic.

## Deployment

### Heroku

```bash
# Deploy with Docker
heroku container:push web -a your-app
heroku container:release web -a your-app
```

### Environment Variables

```bash
MODEL_PATH=/app/model/ACE_2.4_faces_best.keras
THRESHOLD=0.5
ALLOWED_ORIGINS=https://yourdomain.com
```

## Project Structure

```
ace-backend/
├── main.py              # FastAPI app
├── utils/
│   └── preprocess.py    # Image preprocessing
├── model/
│   └── ACE_2.4_faces_best.keras
├── requirements.txt
├── Dockerfile
└── README.md
```

## Contributing

Built with ❤️ by Anyash Prasad

## License

MIT
