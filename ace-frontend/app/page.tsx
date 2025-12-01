"use client";

import { useState } from "react";
import EnhancedFileUpload from "@/components/upload/FileUpload";
import { EnhancedResultCard } from "@/components/results/EnhancedResultCard";
import { AboutProfileCard } from "@/components/about/AboutProfileCard";
import { AboutSection } from "@/components/about/AboutSection";
import { ModelSpecsSection } from "@/components/metrics/ModelSpecsSection";
import { ModelPerformanceCard } from "@/components/metrics/ModelPerformanceCard";
import { DetailedMetricsSection } from "@/components/metrics/DetailedMetricsSection";
import { MetricsVisualizations } from "@/components/metrics/MetricsVisualizations";
import { SmoothScroll } from "@/components/effects/SmoothScroll";
import { ScrollIndicator } from "@/components/effects/ScrollIndicator";
import { ParticleBackground } from "@/components/effects/ParticleBackground";
import { ZoomParallax } from "@/components/effects/ZoomParallax";
import { LogoAnimation } from "@/components/logo/LogoAnimation";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [results, setResults] = useState<any[]>([]);

  const handleResultsUpdate = (files: any[]) => {
    const processedResults = files
      .filter(f => f.result)
      .map(f => ({
        prediction: f.result.prediction,
        confidence: f.result.confidence,
        inference_time: f.result.inference_time,
        filename: f.name,
      }));

    setResults(processedResults);
  };

  // Parallax images for effect section
  const parallaxImages = [
    { src: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80", alt: "AI Technology" },
    { src: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80", alt: "Neural Network" },
    { src: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80", alt: "Data Science" },
    { src: "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80", alt: "Deep Learning" },
    { src: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&q=80", alt: "AI Research" },
    { src: "https://images.unsplash.com/photo-1677756119517-756a188d2d94?w=800&q=80", alt: "Machine Learning" },
    { src: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80", alt: "Technology" },
  ];

  return (
    <SmoothScroll>
      <ScrollIndicator />
      <ParticleBackground />

      <main className="min-h-screen relative">
        {/* Background Effects */}
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-neon-green/20 rounded-full blur-[140px] -translate-x-1/2 -translate-y-1/2 animate-pulse" style={{ animationDuration: "8s" }} />
          <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-neon-teal/20 rounded-full blur-[140px] translate-x-1/2 translate-y-1/2 animate-pulse" style={{ animationDuration: "10s", animationDelay: "2s" }} />
          <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-neon-green/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2 animate-pulse" style={{ animationDuration: "12s", animationDelay: "4s" }} />
        </div>

        {/* SECTION 1: Hero Upload */}
        <section className="min-h-screen flex flex-col items-center justify-center px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12 max-w-4xl"
          >
            {/* Animated Logo replacing static title */}
            <LogoAnimation />

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.6 }}
              className="text-xl md:text-2xl text-text-muted max-w-2xl mx-auto mt-6"
            >
              Deepfake detection using Xception CNN trained on 140K images. Upload images or videos for analysis.
            </motion.p>
          </motion.div>

          {/* Upload Component */}
          <EnhancedFileUpload onResultsUpdate={handleResultsUpdate} />

          {/* Enhanced Results Grid */}
          <AnimatePresence>
            {results.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-12 w-full max-w-6xl mx-auto"
              >
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-bold mb-6 text-center"
                >
                  Analysis Results <span className="text-neon-green">({results.length})</span>
                </motion.h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.map((result, index) => (
                    <EnhancedResultCard key={index} {...result} index={index} />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        {/* Model Performance Card (Left Side) */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-stretch">
            <ModelPerformanceCard
              imageUrl="https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80"
              title="ACE 2.4"
              subtitle="Deepfake Detector"
              description="Fine-tuned Xception CNN on FaceForensics++ and 140K real/fake face dataset. Achieves 95.7% test accuracy on the validation set."
              highlights={["Xception CNN", "140K+ dataset", "12 epochs", "AdamW optimizer"]}
              accuracy={0.957}
              precision={0.945}
              recall={0.952}
              f1Score={0.948}
            />

            {/* Custom Metrics Visualizations */}
            <div className="flex items-center justify-center h-full">
              <MetricsVisualizations />
            </div>
          </div>
        </section>

        {/* SECTION 2: Model Specs */}
        <ModelSpecsSection />

        {/* Zoom Parallax Effect Section */}
        <section className="relative">
          <div className="text-center py-20 px-6">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold mb-4"
            >
              Computer Vision <span className="text-neon-green">Techniques</span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-text-muted max-w-2xl mx-auto"
            >
              Combining convolutional networks with face detection for deepfake analysis
            </motion.p>
          </div>
          <ZoomParallax images={parallaxImages} />
        </section>

        {/* Detailed Metrics Tables */}
        <DetailedMetricsSection />

        {/* SECTION 3: About Profile */}
        <AboutProfileCard />

        {/* About Section with Experience Timeline */}
        <AboutSection />

        {/* Footer Spacer */}
        <div className="h-32" />
      </main>
    </SmoothScroll>
  );
}
