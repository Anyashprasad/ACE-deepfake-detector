"use client";

import { Activity, ArrowUpRight, CheckCircle2, AlertTriangle } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { PredictionResult } from "@/lib/api";

interface EnhancedResultCardProps extends PredictionResult {
    filename: string;
    index: number;
}

export function EnhancedResultCard({
    prediction,
    confidence,
    inference_time,
    filename,
    index
}: EnhancedResultCardProps) {
    const [isHovering, setIsHovering] = useState(false);
    const isFake = prediction.toLowerCase().includes("fake");

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}
            className={cn(
                "relative h-full rounded-3xl p-6",
                "glass-card",
                "hover:border-neon-green/50",
                "transition-all duration-300"
            )}
        >
            {/* Header with Icon */}
            <div className="flex items-center gap-3 mb-6">
                <div className={cn(
                    "p-2 rounded-full transition-colors",
                    isFake ? "bg-red-500/10" : "bg-neon-green/10"
                )}>
                    {isFake ? (
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                    ) : (
                        <CheckCircle2 className="w-5 h-5 text-neon-green" />
                    )}
                </div>
                <div>
                    <h3 className={cn(
                        "text-lg font-semibold font-mono",
                        isFake ? "text-red-500" : "text-neon-green"
                    )}>
                        {prediction.toUpperCase()}
                    </h3>
                    <p className="text-sm text-text-muted truncate max-w-[200px]">
                        {filename}
                    </p>
                </div>
            </div>

            {/* Confidence Ring */}
            <div className="relative flex flex-col items-center mb-6">
                <div
                    className="relative w-32 h-32"
                    onMouseEnter={() => setIsHovering(true)}
                >
                    {/* Background ring */}
                    <div className="absolute inset-0 rounded-full border-4 border-glass-border" />

                    {/* Animated progress ring */}
                    <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
                        <motion.circle
                            cx="50"
                            cy="50"
                            r="45"
                            fill="none"
                            stroke={isFake ? "#ef4444" : "#39FF8A"}
                            strokeWidth="4"
                            strokeDasharray={`${2 * Math.PI * 45}`}
                            initial={{ strokeDashoffset: 2 * Math.PI * 45 }}
                            animate={{
                                strokeDashoffset: 2 * Math.PI * 45 * (1 - confidence),
                                scale: isHovering ? 1.05 : 1
                            }}
                            transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                            className="transition-all duration-500"
                        />
                    </svg>

                    {/* Center value */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold font-mono text-foreground">
                            {(confidence * 100).toFixed(1)}
                        </span>
                        <span className="text-xs text-text-muted">% model score</span>
                    </div>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="space-y-3">
                <div className="p-3 rounded-xl bg-background/50">
                    <div className="flex items-center gap-2 mb-1">
                        <Activity className="w-4 h-4 text-neon-teal" />
                        <span className="text-xs text-text-muted uppercase">Inference Time</span>
                    </div>
                    <p className="text-xl font-bold font-mono text-neon-teal">
                        {inference_time.toFixed(3)}s
                    </p>
                </div>
            </div>

            <p className="mt-4 text-xs leading-relaxed text-text-muted">
                Experimental signal only. This is not proof that the media is authentic or manipulated.
            </p>

            {/* Hover arrow */}
            <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: isHovering ? 1 : 0, x: isHovering ? 0 : -10 }}
                className="absolute bottom-6 right-6"
            >
                <ArrowUpRight className="w-5 h-5 text-neon-green" />
            </motion.div>
        </motion.div>
    );
}
