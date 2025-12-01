"use client";

import { motion } from "framer-motion";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { Layers, Image as ImageIcon, Eye, Database, Film, Zap } from "lucide-react";

interface SpecCardProps {
    icon: React.ReactNode;
    title: string;
    description: string;
    index: number;
}

function SpecCard({ icon, title, description, index }: SpecCardProps) {
    const { ref, isInView } = useScrollReveal();

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 50 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            whileHover={{ y: -10, scale: 1.02 }}
            className="p-6 rounded-2xl glass-card hover:border-neon-green/50 transition-all relative group"
        >
            <div className="absolute inset-0 bg-neon-green/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-neon-green/10 flex items-center justify-center mb-4 text-neon-green">
                    {icon}
                </div>
                <h3 className="text-xl font-bold mb-2 text-foreground">{title}</h3>
                <p className="text-text-muted text-sm leading-relaxed">{description}</p>
            </div>
        </motion.div>
    );
}

export function ModelSpecsSection() {
    const specs = [
        {
            icon: <Layers className="w-6 h-6" />,
            title: "Xception Backbone",
            description: "State-of-the-art depthwise separable convolutional architecture for efficient feature extraction",
        },
        {
            icon: <ImageIcon className="w-6 h-6" />,
            title: "299×299 Preprocessing",
            description: "Standardized input pipeline with normalization and augmentation for optimal model performance",
        },
        {
            icon: <Eye className="w-6 h-6" />,
            title: "RetinaFace Detection",
            description: "Advanced face detection system ensuring accurate localization before deepfake analysis",
        },
        {
            icon: <Database className="w-6 h-6" />,
            title: "140K Real-vs-Fake Dataset",
            description: "Extensive training on diverse real and synthetic faces from multiple generation methods",
        },
        {
            icon: <Film className="w-6 h-6" />,
            title: "FaceForensics++",
            description: "Industry-standard benchmark dataset for comprehensive deepfake detection validation",
        },
        {
            icon: <Zap className="w-6 h-6" />,
            title: "Fusion Method",
            description: "Multi-frame aggregation using mean, max, and P75 for robust video-level predictions",
        },
    ];

    return (
        <section className="py-20 px-6 relative">
            <div className="max-w-7xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold mb-4">
                        Model Architecture & <span className="text-neon-green">Training Pipeline</span>
                    </h2>
                    <p className="text-text-muted max-w-2xl mx-auto">
                        Built on cutting-edge deep learning architecture with comprehensive training methodology
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
                    {specs.map((spec, index) => (
                        <SpecCard key={spec.title} {...spec} index={index} />
                    ))}
                </div>
            </div>
        </section>
    );
}
