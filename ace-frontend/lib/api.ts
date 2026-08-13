// API client for FastAPI backend
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

export interface PredictionResult {
    prediction: string;
    confidence: number;
    inference_time: number;
    model_version?: string;
}

async function requestPrediction(path: string, file: File): Promise<PredictionResult> {
    const formData = new FormData();
    formData.append('file', file);
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 120_000);
    const startTime = performance.now();

    try {
        const response = await fetch(`${API_BASE}${path}`, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(payload.detail || `Analysis failed (${response.status})`);
        }
        return {
            prediction: payload.label,
            confidence: payload.confidence,
            inference_time: (performance.now() - startTime) / 1000,
            model_version: payload.model_version ?? 'ACE 2.4',
        };
    } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
            throw new Error('The model took too long to respond. Please try a smaller file.');
        }
        throw error;
    } finally {
        window.clearTimeout(timeout);
    }
}

export async function predictImage(file: File): Promise<PredictionResult> {
    return requestPrediction('/predict/image', file);
}

export async function predictVideo(file: File): Promise<PredictionResult> {
    return requestPrediction('/predict/video', file);
}
