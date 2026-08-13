"use client";

import * as React from "react";
import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface PerformanceGraphProps {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
}

function PerformanceGraph({ accuracy, precision, recall, f1Score }: PerformanceGraphProps) {
    const metrics = [
        { label: "Accuracy", value: accuracy, color: "#39FF8A" },
        { label: "Precision", value: precision, color: "#00F0FF" },
        { label: "Recall", value: recall, color: "#39FF8A" },
        { label: "F1", value: f1Score, color: "#00F0FF" },
    ];

    return (
        <div className="space-y-4">
            {metrics.map((metric, idx) => (
                <div key={metric.label}>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-text-muted">{metric.label}</span>
                        <span className="font-mono font-bold" style={{ color: metric.color }}>
                            {(metric.value * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="h-2 bg-background/50 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${metric.value * 100}%` }}
                            transition={{ duration: 1, delay: idx * 0.1 }}
                            className="h-full rounded-full"
                            style={{ backgroundColor: metric.color }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
}

interface ModelPerformanceCardProps extends HTMLMotionProps<"div"> {
    imageUrl: string;
    title: string;
    subtitle: string;
    description: string;
    highlights?: string[];
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1Score?: number;
}

export const ModelPerformanceCard = React.forwardRef<
    HTMLDivElement,
    ModelPerformanceCardProps
>(
    (
        {
            className,
            imageUrl,
            title,
            subtitle,
            description,
            highlights = [],
            accuracy = 0.957,
            precision = 0.945,
            recall = 0.952,
            f1Score = 0.948,
            ...props
        },
        ref
    ) => {
        return (
            <motion.div
                ref={ref}
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 250, damping: 20 }}
                className={cn(
                    "relative w-full max-w-2xl overflow-hidden rounded-3xl hover:shadow-xl glass-card",
                    className
                )}
                {...props}
            >
                {/* Top image with parallax */}
                <motion.div
                    className="relative h-64 w-full overflow-hidden"
                    whileHover={{ scale: 1.1 }}
                    transition={{ duration: 0.45 }}
                >
                    <img
                        src={imageUrl}
                        alt={title}
                        className="h-full w-full object-cover"
                    />
                    {/* Fade connection */}
                    <div className="absolute bottom-0 h-32 w-full bg-gradient-to-t from-background via-background/80 to-transparent" />
                </motion.div>

                {/* Bottom content with graph */}
                <div className="relative z-10 p-6 bg-background/50 backdrop-blur">
                    <p className="text-sm uppercase tracking-wider text-neon-teal">
                        {subtitle}
                    </p>
                    <h3 className="mt-1 text-2xl font-bold text-foreground">{title}</h3>
                    <p className="mt-3 text-sm leading-relaxed text-text-muted">
                        {description}
                    </p>

                    {/* Performance Graph */}
                    <div className="mt-6">
                        <h4 className="text-sm font-semibold text-foreground mb-4">Model Performance</h4>
                        <PerformanceGraph
                            accuracy={accuracy}
                            precision={precision}
                            recall={recall}
                            f1Score={f1Score}
                        />
                    </div>

                    {/* Highlights */}
                    {highlights.length > 0 && (
                        <ul className="mt-4 grid grid-cols-2 gap-2 text-xs text-text-muted">
                            {highlights.map((item, idx) => (
                                <li
                                    key={idx}
                                    className="flex items-center gap-2 rounded-md bg-glass-bg px-2 py-1"
                                >
                                    <span className="h-1.5 w-1.5 rounded-full bg-neon-green" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </motion.div>
        );
    }
);

ModelPerformanceCard.displayName = "ModelPerformanceCard";
