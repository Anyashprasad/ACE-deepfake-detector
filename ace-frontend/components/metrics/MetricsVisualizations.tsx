"use client";

import { motion } from "framer-motion";
import { useScrollReveal } from "@/hooks/useScrollReveal";

interface Metric {
    label: string;
    value: number;
    color: string;
}

export function MetricsVisualizations() {
    const { ref, isInView } = useScrollReveal();

    const metrics: Metric[] = [
        { label: "Accuracy", value: 0.957, color: "#39FF8A" },
        { label: "Precision", value: 0.945, color: "#00F0FF" },
        { label: "Recall", value: 0.952, color: "#39FF8A" },
        { label: "F1", value: 0.948, color: "#00F0FF" },
    ];

    // Radial chart configuration
    const centerX = 120;
    const centerY = 120;
    const radius = 80;
    const maxRadius = 90;

    // Calculate points for radial chart
    const calculatePoint = (index: number, value: number) => {
        const angle = (index * Math.PI * 2) / metrics.length - Math.PI / 2;
        const r = (value * maxRadius);
        return {
            x: centerX + r * Math.cos(angle),
            y: centerY + r * Math.sin(angle),
        };
    };

    // Create polygon path for filled area
    const polygonPath = metrics
        .map((metric, i) => {
            const point = calculatePoint(i, metric.value);
            return `${point.x},${point.y}`;
        })
        .join(" ");

    // Create guide circles
    const guideCircles = [0.25, 0.5, 0.75, 1.0];

    return (
        <div ref={ref} className="h-full flex items-center">
            {/* Radial Performance Chart */}
            <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6 }}
                className="glass-card p-6 rounded-2xl flex flex-col w-full"
            >
                <h3 className="text-xl font-bold mb-6 text-neon-green">
                    📊 Performance Overview
                </h3>

                <div className="flex flex-col items-center justify-center">
                    <svg
                        width="320"
                        height="320"
                        viewBox="0 0 240 240"
                        className="mb-6"
                    >
                        {/* Guide circles */}
                        {guideCircles.map((scale, idx) => (
                            <circle
                                key={idx}
                                cx={centerX}
                                cy={centerY}
                                r={scale * maxRadius}
                                fill="none"
                                stroke="rgba(255, 255, 255, 0.1)"
                                strokeWidth="1"
                                strokeDasharray="4 4"
                            />
                        ))}

                        {/* Axis lines */}
                        {metrics.map((_, index) => {
                            const point = calculatePoint(index, 1.0);
                            return (
                                <motion.line
                                    key={index}
                                    x1={centerX}
                                    y1={centerY}
                                    x2={point.x}
                                    y2={point.y}
                                    stroke="rgba(255, 255, 255, 0.15)"
                                    strokeWidth="1"
                                    initial={{ pathLength: 0 }}
                                    animate={isInView ? { pathLength: 1 } : {}}
                                    transition={{ duration: 0.8, delay: index * 0.1 }}
                                />
                            );
                        })}

                        {/* Animated filled polygon */}
                        <motion.polygon
                            points={polygonPath}
                            fill="url(#radialGradient)"
                            stroke="#39FF8A"
                            strokeWidth="2"
                            initial={{ opacity: 0, scale: 0 }}
                            animate={isInView ? { opacity: 0.6, scale: 1 } : {}}
                            transition={{ duration: 1, delay: 0.5 }}
                            style={{ transformOrigin: `${centerX}px ${centerY}px` }}
                        />

                        {/* Metric points */}
                        {metrics.map((metric, index) => {
                            const point = calculatePoint(index, metric.value);
                            return (
                                <motion.g key={index}>
                                    <motion.circle
                                        cx={point.x}
                                        cy={point.y}
                                        r="5"
                                        fill={metric.color}
                                        initial={{ scale: 0 }}
                                        animate={isInView ? { scale: 1 } : {}}
                                        transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                                    />
                                    <motion.circle
                                        cx={point.x}
                                        cy={point.y}
                                        r="8"
                                        fill="none"
                                        stroke={metric.color}
                                        strokeWidth="2"
                                        initial={{ scale: 0, opacity: 0 }}
                                        animate={isInView ? { scale: 1, opacity: 0.5 } : {}}
                                        transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                                    />
                                </motion.g>
                            );
                        })}

                        {/* Gradient definition */}
                        <defs>
                            <radialGradient id="radialGradient" cx="50%" cy="50%">
                                <stop offset="0%" stopColor="#39FF8A" stopOpacity="0.4" />
                                <stop offset="100%" stopColor="#00F0FF" stopOpacity="0.2" />
                            </radialGradient>
                        </defs>
                    </svg>

                    {/* Labels */}
                    <div className="grid grid-cols-2 gap-4 w-full">
                        {metrics.map((metric, index) => (
                            <motion.div
                                key={metric.label}
                                initial={{ opacity: 0, x: -10 }}
                                animate={isInView ? { opacity: 1, x: 0 } : {}}
                                transition={{ duration: 0.4, delay: 1.0 + index * 0.1 }}
                                className="flex items-center gap-2"
                            >
                                <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: metric.color }}
                                />
                                <span className="text-xs text-text-muted font-mono">
                                    {metric.label}
                                </span>
                                <span
                                    className="text-sm font-bold ml-auto"
                                    style={{ color: metric.color }}
                                >
                                    {(metric.value * 100).toFixed(1)}%
                                </span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
