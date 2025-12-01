"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import styles from './LogoAnimation.module.css';

export function LogoAnimation() {
    const [animationComplete, setAnimationComplete] = useState(false);

    useEffect(() => {
        // Mark animation as complete after 1.1 seconds (faster)
        const timer = setTimeout(() => {
            setAnimationComplete(true);
        }, 1100);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="relative">
            {/* Simplified - removed kanji background */}

            {/* Slash Effect - simplified, no speed lines */}
            <div className={styles.slash} />

            {/* Flash Overlay */}
            <div className={styles.flashOverlay} />

            {/* ACE Logo with Impact */}
            <div className={styles.logoWrapper}>
                <span className={styles.logoBase}>ACE</span>
                <div className={`${styles.logoLayer} ${styles.layerTop}`}>ACE</div>
                <div className={`${styles.logoLayer} ${styles.layerBottom}`}>ACE</div>
            </div>

            {/* 2.4 Engine - Appears after ACE animation */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={animationComplete ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="mt-4 text-center"
            >
                <span className="text-4xl md:text-5xl lg:text-6xl font-bold">
                    <span className="text-foreground">2.4</span>{" "}
                    <span className="text-neon-green neon-glow">Engine</span>
                </span>
            </motion.div>
        </div>
    );
}
