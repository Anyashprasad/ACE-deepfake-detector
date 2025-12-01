# ACE 2.4 - AI-Powered Deepfake Detection System

Complete full-stack deepfake detection system with 99.97% validation AUC, featuring a modern glassmorphism UI and FastAPI backend.

![ACE 2.4 Engine](https://img.shields.io/badge/ACE-2.4-00ff88?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge)
![Next.js](https://img.shields.io/badge/next.js-16-black?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

## Overview

ACE 2.4 is a production-ready deepfake detection system that combines state-of-the-art machine learning with a stunning user interface. Upload images or videos to detect AI-generated content with industry-leading accuracy.

### Live Demo

- **Frontend**: [Coming Soon - Cloudflare Pages]
- **Backend API**: [Coming Soon - Heroku]

## Features

### Backend
- 🔍 **Image Analysis** - Single image deepfake detection
- 🎬 **Video Analysis** - Temporal fusion across 12 frames
- 🚀 **Fast Inference** - TensorFlow 2.20 optimization
- 📊 **99.97% AUC** - State-of-the-art accuracy
- 🐳 **Dockerized** - Easy deployment

### Frontend
- ✨ **Anime-Style Animations** - Fast, impactful reveals
- 🎨 **Glassmorphism Design** - Modern neon aesthetic
- 📱 **Fully Responsive** - Mobile-first approach
- 🔄 **Real-Time Results** - Inline analysis display
- 📤 **Drag & Drop Upload** - Intuitive file handling

## Tech Stack

### Backend
- FastAPI + Uvicorn
- TensorFlow 2.20
- Xception CNN (256MB model)
- OpenCV for preprocessing

### Frontend
- Next.js 16 (App Router)
- Tailwind CSS
- Framer Motion
- TypeScript

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### Backend Setup

```bash
cd ace-backend
pip install -r requirements.txt
python main.py
# Server: http://localhost:8000
```

### Frontend Setup

```bash
cd ace-frontend
npm install
npm run dev
# App: http://localhost:3000
```

### Docker Compose

```bash
docker-compose up
```

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │─────▶│  Next.js     │─────▶│  FastAPI    │
│             │      │  Frontend    │      │  Backend    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      ▼
                            │               ┌─────────────┐
                            │               │  Xception   │
                            │               │  Model      │
                            │               │  (256MB)    │
                            │               └─────────────┘
                            ▼
                     ┌──────────────┐
                     │  Cloudflare  │
                     │  Pages       │
                     └──────────────┘
```

## Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | 99.49% |
| AUC | 99.97% |
| Precision | 99.33% |
| Recall | 99.64% |
| F1 Score | 99.48% |

**Training**: 140K images (70K real + 70K fake)  
**Validation**: Early stopping at epoch 2  
**Architecture**: Xception with custom preprocessing

## Deployment

### Production Stack
- **Backend**: Heroku (Container)
- **Frontend**: Cloudflare Pages
- **Cost**: ~$5/month

### Deploy Backend (Heroku)
```bash
heroku container:push web -a ace24-backend
heroku container:release web -a ace24-backend
```

### Deploy Frontend (Cloudflare)
1. Push to GitHub
2. Connect Cloudflare Pages
3. Configure build settings
4. Deploy!

## Project Structure

```
PythonProject12/
├── ace-backend/
│   ├── main.py
│   ├── utils/
│   ├── model/
│   ├── Dockerfile
│   └── requirements.txt
│
├── ace-frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

## API Documentation

### Health Check
```bash
curl https://ace24-backend.herokuapp.com/health
```

### Analyze Image
```bash
curl -X POST https://ace24-backend.herokuapp.com/predict/image \
  -F "file=@image.jpg"
```

Response:
```json
{
  "label": "REAL",
  "confidence": 0.9876
}
```

## Screenshots

[Coming after logo integration]

## Contributing

Contributions welcome! Please open an issue or PR.

## Author

**Anyash Prasad**
- LinkedIn: [anyash-prasad-03699a284](https://www.linkedin.com/in/anyash-prasad-03699a284/)
- Email: anyashprasad.work@gmail.com
- Portfolio: [WikiScan](https://www.wikiscan.dev)

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Trained on 140K Real and Fake Faces dataset
- Built with FastAPI, Next.js, and TensorFlow
- Inspired by cutting-edge deepfake detection research

---

**⚡ ACE 2.4 - Detecting the Unreal**
