// API client for FastAPI backend
const API_BASE = 'http://localhost:8000';

export interface PredictionResult {
    prediction: string;
    confidence: number;
    inference_time: number;
    model_version?: string;
}

export async function predictImage(file: File): Promise<PredictionResult> {
    const formData = new FormData();
    formData.append('file', file);

    const startTime = Date.now();
    const response = await fetch(`${API_BASE}/predict/image`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Prediction failed: ${response.statusText}`);
    }

    const data = await response.json();
    const inference_time = (Date.now() - startTime) / 1000;

    return {
        prediction: data.label,
        confidence: data.confidence,
        inference_time,
        model_version: 'ACE 2.4'
    };
}

export async function predictVideo(file: File): Promise<PredictionResult> {
    const formData = new FormData();
    formData.append('file', file);

    const startTime = Date.now();
    const response = await fetch(`${API_BASE}/predict/video`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Prediction failed: ${response.statusText}`);
    }

    const data = await response.json();
    const inference_time = (Date.now() - startTime) / 1000;

    return {
        prediction: data.label,
        confidence: data.confidence,
        inference_time,
        model_version: 'ACE 2.4'
    };
}
