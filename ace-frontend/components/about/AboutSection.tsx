"use client";

import { motion } from "framer-motion";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { Github, Linkedin, Mail, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TimelineItemProps {
    title: string;
    index: number;
}

function TimelineItem({ title, index }: TimelineItemProps) {
    const { ref, isInView } = useScrollReveal();

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, x: -20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="flex items-center gap-3 mb-3"
        >
            <div className="w-2 h-2 rounded-full bg-neon-green" />
            <span className="text-text-muted">{title}</span>
        </motion.div>
    );
}

export function AboutSection() {
    const timeline = [
        "SAIL Intern",
        "Cybervault Core Member",
        "Eduskills Fortinet Intern",
    ];

    return (
        <section className="py-20 px-6 relative">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left Column - Profile Card */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="relative"
                    >
                        {/* Neon Glow Blob Behind Card */}
                        <div className="absolute inset-0 bg-neon-green/30 rounded-full blur-[100px] scale-150 -z-10" />

                        <div className="glass-card p-8 rounded-3xl">
                            <div className="w-32 h-32 mx-auto mb-6 rounded-full bg-gradient-to-br from-neon-green to-neon-teal flex items-center justify-center text-4xl font-bold text-background">
                                AP
                            </div>
                            <h3 className="text-2xl font-bold text-center mb-2">Anyash Prasad</h3>
                            <p className="text-neon-green text-center mb-6">Developer & Researcher</p>

                            <div className="space-y-2 text-sm text-text-muted">
                                <p>🎓 Cybersecurity × AI Specialist</p>
                                <p>🔒 Digital Forensics Researcher</p>
                                <p>🤖 AI Prompting & Security Research</p>
                                <p>📜 Fortinet Certified Professional</p>
                            </div>

                            <div className="flex gap-3 mt-6 justify-center">
                                <Button variant="outline" size="icon" asChild>
                                    <a href="https://github.com/anyashprasad" target="_blank" rel="noopener noreferrer">
                                        <Github className="w-5 h-5" />
                                    </a>
                                </Button>
                                <Button variant="outline" size="icon" asChild>
                                    <a href="https://www.linkedin.com/in/anyash-prasad-03699a284/" target="_blank" rel="noopener noreferrer">
                                        <Linkedin className="w-5 h-5" />
                                    </a>
                                </Button>
                                <Button variant="outline" size="icon" asChild>
                                    <a href="mailto:anyashprasad.work@gmail.com">
                                        <Mail className="w-5 h-5" />
                                    </a>
                                </Button>
                            </div>
                        </div>
                    </motion.div>

                    {/* Right Column - Content */}
                    <motion.div
                        initial={{ opacity: 0, x: 50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="text-4xl md:text-5xl font-bold mb-4">
                            Anyash Prasad
                        </h2>
                        <h3 className="text-2xl md:text-3xl text-neon-green mb-6">
                            Cybersecurity × AI
                        </h3>

                        <p className="text-text-muted mb-8 leading-relaxed">
                            Specializing in digital forensics, AI-powered security solutions, and deepfake detection.
                            Certified in Fortinet network security with hands-on experience in threat analysis and
                            AI prompting techniques for advanced cybersecurity applications.
                        </p>

                        <div className="mb-8">
                            <div className="flex items-center gap-2 mb-4">
                                <Briefcase className="w-5 h-5 text-neon-green" />
                                <h4 className="font-semibold text-lg">Experience</h4>
                            </div>
                            {timeline.map((item, index) => (
                                <TimelineItem key={item} title={item} index={index} />
                            ))}
                        </div>

                        <Button
                            size="lg"
                            className="group"
                            onClick={() => window.open('https://drive.google.com/drive/folders/1e8I1b8LqUaCgO_3HkAokVKpdA5jDxacb?usp=drive_link', '_blank')}
                        >
                            View Full Resume
                            <motion.span
                                className="inline-block ml-2"
                                animate={{ x: [0, 5, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            >
                                →
                            </motion.span>
                        </Button>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
