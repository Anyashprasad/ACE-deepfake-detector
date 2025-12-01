"use client";

import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export function ProfileSection() {
    return (
        <section className="min-h-screen overflow-hidden relative py-20">
            <div className="mx-auto max-w-7xl relative z-20 px-6">
                <div className="relative">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="z-20 text-foreground relative font-bold text-center tracking-[-7px] text-7xl md:text-9xl xl:text-[10rem]"
                    >
                        <span className="text-neon-green neon-glow">ACE 2.4</span>
                        <br />
                        <span className="text-foreground/80">ENGINE</span>
                    </motion.h1>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="grid relative mt-16"
                >
                    <div className="space-y-8 pt-10 flex gap-6 justify-center">
                        <div className="flex gap-6 glass-card w-full max-w-xl h-fit p-10 items-end">
                            <div className="font-semibold text-xl text-neon-teal">
                                <div>/ DEEPFAKE DETECTION</div>
                                <div>/ IMAGE ANALYSIS</div>
                                <div>/ VIDEO FORENSICS</div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="md:mt-20 mt-10"
                >
                    <p className="mx-auto max-w-2xl font-mono text-center text-sm font-medium tracking-wide md:text-base text-text-muted">
                        ADVANCED COUNTER-DEEPFAKE ENGINE
                        <br />
                        POWERED BY STATE-OF-THE-ART DEEP LEARNING
                        <br />
                        DETECTING SYNTHETIC MEDIA IN REAL-TIME
                    </p>
                </motion.div>
            </div>

            {/* Grid Background Effect */}
            <div
                className="absolute inset-0 z-0"
                style={{
                    backgroundImage: `
            linear-gradient(to right, rgba(57, 255, 138, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(57, 255, 138, 0.03) 1px, transparent 1px)
          `,
                    backgroundSize: "40px 40px",
                    backgroundPosition: "0 0, 0 0",
                    maskImage: `radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%)`,
                    WebkitMaskImage: `radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%)`,
                }}
            />
        </section>
    );
}
