"use client";

import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, Clock, Activity } from "lucide-react";
import { PredictionResult } from "@/lib/api";

interface ResultProps extends PredictionResult {
    filename: string;
    index: number;
}

export function ResultsCard({ prediction, confidence, inference_time, filename, index }: ResultProps) {
    const isFake = prediction.toLowerCase().includes("fake");

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-6 rounded-2xl glass-card border-2 hover:border-neon-green/30 transition-all"
        >
            {/* Result Badge */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    {isFake ? (
                        <AlertTriangle className="w-6 h-6 text-red-500" />
                    ) : (
                        <CheckCircle2 className="w-6 h-6 text-neon-green" />
                    )}
                    <div>
                        <h3 className="font-mono text-2xl font-bold">
                            <span className={isFake ? "text-red-500" : "text-neon-green"}>
                                {prediction.toUpperCase()}
                            </span>
                        </h3>
                        <p className="text-sm text-text-muted truncate max-w-[200px]">{filename}</p>
                    </div>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-background/50">
                    <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-4 h-4 text-neon-teal" />
                        <span className="text-xs text-text-muted uppercase tracking-wider">Confidence</span>
                    </div>
                    <p className="text-2xl font-bold font-mono">{(confidence * 100).toFixed(2)}%</p>
                    <div className="mt-2 h-2 bg-background rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${confidence * 100}%` }}
                            transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                            className={`h-full ${isFake ? "bg-red-500" : "bg-neon-green"}`}
                        />
                    </div>
                </div>

                <div className="p-4 rounded-xl bg-background/50">
                    <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-neon-teal" />
                        <span className="text-xs text-text-muted uppercase tracking-wider">Inference Time</span>
                    </div>
                    <p className="text-2xl font-bold font-mono">{inference_time.toFixed(3)}s</p>
                </div>
            </div>
        </motion.div>
    );
}

interface ResultsGridProps {
    results: ({ prediction: string; confidence: number; inference_time: number; filename: string })[];
}

export default function ResultsGrid({ results }: ResultsGridProps) {
    if (results.length === 0) return null;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-12 w-full max-w-4xl mx-auto"
        >
            <h2 className="text-3xl font-bold mb-6 text-center">
                Analysis Results <span className="text-neon-green">({results.length})</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {results.map((result, index) => (
                    <ResultsCard key={index} {...result} index={index} />
                ))}
            </div>
        </motion.div>
    );
}
