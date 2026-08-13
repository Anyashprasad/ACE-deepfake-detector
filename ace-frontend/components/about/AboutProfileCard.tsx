/* eslint-disable @next/next/no-img-element */
"use client";

import React from "react";
import { motion } from "framer-motion";
import { ArrowDownRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TitleReveal } from "./TitleReveal";

export function AboutProfileCard() {
    return (
        <section className="min-h-screen overflow-hidden relative py-20">
            <div className="mx-auto max-w-7xl relative z-20 px-6">
                {/* Animated Title Reveal */}
                <TitleReveal />

                <div className="grid relative">
                    <div className="space-y-8 pt-20 flex gap-6 justify-center">
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: false }}
                            transition={{ duration: 0.3, delay: 0.8 }}
                            className="flex gap-6 bg-secondary/10 backdrop-blur-sm border border-white/10 w-full max-w-xl h-fit p-6 md:p-10 items-end space-y-2 text-lg md:text-2xl lg:text-3xl"
                        >
                            <div className="font-semibold text-lg md:text-xl text-text-muted">
                                <motion.div
                                    initial={{ opacity: 0, x: -30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: false }}
                                    transition={{ duration: 0.2, delay: 0.9 }}
                                    className="flex items-center gap-2"
                                >
                                    <span className="text-neon-green">/</span> DEEPFAKE DETECTION
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, x: -30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: false }}
                                    transition={{ duration: 0.2, delay: 1.0 }}
                                    className="flex items-center gap-2"
                                >
                                    <span className="text-neon-green">/</span> WEB SECURITY (UX/UI)
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, x: -30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: false }}
                                    transition={{ duration: 0.2, delay: 1.1 }}
                                    className="flex items-center gap-2"
                                >
                                    <span className="text-neon-green">/</span> AI DEVELOPMENT
                                </motion.div>
                            </div>
                            <motion.div
                                initial={{ opacity: 0, scale: 0.8, rotateZ: -5 }}
                                whileInView={{ opacity: 1, scale: 1, rotateZ: 0 }}
                                viewport={{ once: false }}
                                transition={{ duration: 0.4, delay: 0.7, type: "spring", stiffness: 200 }}
                                className="absolute hidden md:flex left-1/2 -top-10 w-fit overflow-hidden bg-black border border-white/10 shadow-2xl shadow-neon-green/10"
                            >
                                <img
                                    src="/profile-photo.jpg"
                                    alt="Anyash Prasad"
                                    className="h-[400px] w-auto object-cover grayscale hover:grayscale-0 transition-all duration-500"
                                />
                                <div className="text-left p-2 rotate-180 [writing-mode:vertical-rl] text-xs font-medium tracking-widest text-neon-green bg-black/50">
                                    BASED IN INDIA
                                </div>
                            </motion.div>
                        </motion.div>
                    </div>
                    <div className="flex md:hidden left-1/2 -top-10 w-full md:w-fit overflow-hidden bg-black border border-white/10 mt-8">
                        <img
                            src="/profile-photo.jpg"
                            alt="Anyash Prasad"
                            className="h-[300px] w-full object-cover grayscale hover:grayscale-0 transition-all duration-500"
                        />
                        <div className="text-left p-2 rotate-180 [writing-mode:vertical-rl] text-xs font-medium tracking-widest text-neon-green bg-black/50">
                            BASED IN INDIA
                        </div>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: false }}
                    transition={{ duration: 0.3, delay: 1.2 }}
                    className="md:mt-48 mt-16"
                >
                    <p className="mx-auto max-w-2xl font-mono text-center text-sm font-medium tracking-wide md:text-base text-text-muted">
                        I&apos;M A CYBERSECURITY STUDENT & SOFTWARE DEVELOPER,
                        <br />
                        WHO BUILDS SECURE AND INTELLIGENT WEB EXPERIENCES FOR
                        <br />
                        THE FUTURE OF AI
                    </p>
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: false }}
                    transition={{ duration: 0.3, delay: 1.3 }}
                    className="flex justify-center pt-6 gap-4"
                >
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Button size={"lg"} onClick={() => window.open('https://github.com/AnyashPrasad', '_blank')}>
                            GitHub
                        </Button>
                    </motion.div>
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Button size={"lg"} variant="outline" onClick={() => window.open('https://www.linkedin.com/in/anyash-prasad-03699a284/', '_blank')}>
                            LinkedIn
                        </Button>
                    </motion.div>
                </motion.div>

                <div className="md:flex mt-20 items-end justify-between">
                    <div className="relative h-48 w-80 mx-auto md:mx-0">
                        <div className="w-60 h-36 shadow-lg border border-glass-border rounded-md overflow-hidden mb-8 md:mb-0 bg-background/90 backdrop-blur absolute left-0 top-0 z-30">
                            <div className="p-4 h-full flex flex-col justify-center">
                                <h3 className="text-neon-green font-bold text-lg mb-2">ACE 2.4</h3>
                                <p className="text-xs text-text-muted">Deepfake Detection</p>
                            </div>
                        </div>
                        <div className="w-60 h-36 absolute left-6 -top-6 shadow-lg border border-glass-border rounded-md overflow-hidden mb-8 md:mb-0 bg-background/90 backdrop-blur z-20">
                            <div className="p-4 h-full flex flex-col justify-center">
                                <h3 className="text-neon-teal font-bold text-lg mb-2">WikiScan</h3>
                                <p className="text-xs text-text-muted">Vulnerability Scanner</p>
                            </div>
                        </div>
                        <div className="w-60 h-36 absolute left-12 -top-12 shadow-lg border border-glass-border rounded-md overflow-hidden mb-8 md:mb-0 bg-background/90 backdrop-blur z-10">
                            <div className="p-4 h-full flex flex-col justify-center">
                                <h3 className="text-neon-green font-bold text-lg mb-2">Security Tools</h3>
                                <p className="text-xs text-text-muted">AI × Cyber Projects</p>
                            </div>
                        </div>
                    </div>
                    <div className="mt-12 md:mt-0">
                        <a
                            href="https://www.wikiscan.dev"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block group cursor-pointer"
                        >
                            <div className="flex items-center justify-center md:justify-end gap-2 transition-all group-hover:gap-4">
                                <span className="text-lg font-medium tracking-wider text-text-muted group-hover:text-neon-green transition-colors">
                                    RECENT WORK
                                </span>
                                <ArrowDownRight className="size-6 text-neon-green transition-transform group-hover:translate-x-1 group-hover:translate-y-1" />
                            </div>

                            <div className="mt-3 text-center md:text-right">
                                <h2
                                    className="text-4xl md:text-5xl uppercase tracking-[-4px] text-white group-hover:text-neon-green transition-colors"
                                >
                                    Security without Limits
                                </h2>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
            <div
                className="absolute block inset-0 z-0 pointer-events-none"
                style={{
                    backgroundImage: `
        linear-gradient(to right, #ffffff10 1px, transparent 1px),
        linear-gradient(to bottom, #ffffff10 1px, transparent 1px)
      `,
                    backgroundSize: "20px 20px",
                    backgroundPosition: "0 0, 0 0",
                    maskImage: `
        repeating-linear-gradient(
              to right,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            repeating-linear-gradient(
              to bottom,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            radial-gradient(ellipse 70% 60% at 50% 0%, #000 60%, transparent 100%)
      `,
                    WebkitMaskImage: `
 repeating-linear-gradient(
              to right,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            repeating-linear-gradient(
              to bottom,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            radial-gradient(ellipse 70% 60% at 50% 0%, #000 60%, transparent 100%)
      `,
                    maskComposite: "intersect",
                    WebkitMaskComposite: "source-in",
                }}
            />
        </section>
    );
}
