"use client";

import { motion } from "framer-motion";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { Activity, Zap, Target, TrendingUp } from "lucide-react";

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    description: string;
    index: number;
}

function MetricCard({ icon, label, value, description, index }: MetricCardProps) {
    const { ref, isInView } = useScrollReveal();

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 40 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="p-6 rounded-2xl glass-card hover:border-neon-green/30 transition-all group"
        >
            <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-neon-green/10 text-neon-green group-hover:bg-neon-green/20 transition-colors">
                    {icon}
                </div>
                <div className="flex-1">
                    <p className="text-sm text-text-muted uppercase tracking-wider mb-1">{label}</p>
                    <h3 className="text-3xl font-bold font-mono text-neon-green mb-2">{value}</h3>
                    <p className="text-sm text-text-muted">{description}</p>
                </div>
            </div>
        </motion.div>
    );
}

export function MetricsGrid() {
    const metrics = [
        {
            icon: <Activity className="w-6 h-6" />,
            label: "Accuracy",
            value: "98.7%",
            description: "Detection accuracy on test dataset",
        },
        {
            icon: <Zap className="w-6 h-6" />,
            label: "Speed",
            value: "<1s",
            description: "Average inference time per image",
        },
        {
            icon: <Target className="w-6 h-6" />,
            label: "Precision",
            value: "97.2%",
            description: "False positive rate minimized",
        },
        {
            icon: <TrendingUp className="w-6 h-6" />,
            label: "Recall",
            value: "99.1%",
            description: "True deepfake detection rate",
        },
    ];

    return (
        <section className="py-20 px-6">
            <div className="max-w-7xl mx-auto">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-4xl md:text-5xl font-bold text-center mb-4"
                >
                    Model <span className="text-neon-green">Performance</span>
                </motion.h2>
                <motion.p
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-center text-text-muted mb-12 max-w-2xl mx-auto"
                >
                    Powered by state-of-the-art deep learning architecture, trained on millions of images
                </motion.p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {metrics.map((metric, index) => (
                        <MetricCard key={metric.label} {...metric} index={index} />
                    ))}
                </div>
            </div>
        </section>
    );
}
