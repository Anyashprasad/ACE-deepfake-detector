"use client";

import { motion } from "framer-motion";
import { useScrollReveal } from "@/hooks/useScrollReveal";

export function DetailedMetricsSection() {
    const { ref: ref1, isInView: isInView1 } = useScrollReveal();
    const { ref: ref2, isInView: isInView2 } = useScrollReveal();

    return (
        <section className="py-20 px-6">
            <div className="max-w-7xl mx-auto">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-4xl md:text-5xl font-bold text-center mb-16"
                >
                    Training <span className="text-neon-green">Metrics</span>
                </motion.h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Configuration Parameters */}
                    <motion.div
                        ref={ref1}
                        initial={{ opacity: 0, y: 40 }}
                        animate={isInView1 ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6 }}
                        className="glass-card p-6 rounded-2xl overflow-hidden"
                    >
                        <h3 className="text-2xl font-bold mb-6 text-neon-teal">Configuration</h3>
                        <div className="space-y-3">
                            {[
                                ["Model Name", "ACE 2.4 (Adaptive Counter-Deepfake Engine)"],
                                ["Base Model", "ACE 2.3 Balanced — Xception architecture"],
                                ["Image Input Size", "299 × 299 pixels"],
                                ["Datasets Used", "140K Real-vs-Fake Faces + FaceForensics++"],
                                ["Optimizer", "AdamW (lr=3×10⁻⁵, wd=1×10⁻⁴)"],
                                ["Loss Function", "Binary Cross-Entropy"],
                                ["Training Epochs", "12 (Early Stopping patience = 5)"],
                                ["Batch Size", "32"],
                            ].map(([key, value], index) => (
                                <motion.div
                                    key={key}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={isInView1 ? { opacity: 1, x: 0 } : {}}
                                    transition={{ duration: 0.4, delay: index * 0.05 }}
                                    className="flex justify-between items-start p-3 rounded-lg bg-background/30 hover:bg-neon-green/5 transition-colors"
                                >
                                    <span className="text-text-muted font-mono text-sm">{key}</span>
                                    <span className="text-foreground font-medium text-sm text-right ml-4">{value}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Performance Metrics */}
                    <motion.div
                        ref={ref2}
                        initial={{ opacity: 0, y: 40 }}
                        animate={isInView2 ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="glass-card p-6 rounded-2xl overflow-hidden"
                    >
                        <h3 className="text-2xl font-bold mb-6 text-neon-green">🧠 Performance Metrics</h3>
                        <div className="space-y-4">
                            {[
                                { label: "Train Accuracy", value: 0.978, color: "#39FF8A" },
                                { label: "Validation Accuracy", value: 0.961, color: "#00F0FF" },
                                { label: "Test Accuracy", value: 0.957, color: "#39FF8A" },
                                { label: "AUC (ROC)", value: 0.981, color: "#00F0FF" },
                                { label: "Precision", value: 0.945, color: "#39FF8A" },
                                { label: "Recall", value: 0.952, color: "#00F0FF" },
                                { label: "F1 Score", value: 0.948, color: "#39FF8A" },
                            ].map((metric, index) => (
                                <motion.div
                                    key={metric.label}
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={isInView2 ? { opacity: 1, x: 0 } : {}}
                                    transition={{ duration: 0.4, delay: index * 0.05 }}
                                    className="space-y-2"
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="text-text-muted font-medium">{metric.label}</span>
                                        <span className="text-2xl font-bold font-mono" style={{ color: metric.color }}>
                                            {metric.value.toFixed(3)}
                                        </span>
                                    </div>

                                    <div className="h-2 bg-background/50 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={isInView2 ? { width: `${metric.value * 100}%` } : {}}
                                            transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                                            className="h-full rounded-full"
                                            style={{ backgroundColor: metric.color }}
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
