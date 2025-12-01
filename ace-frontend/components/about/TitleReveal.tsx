"use client";

import { motion } from "framer-motion";
import styles from "./TitleReveal.module.css";

export function TitleReveal() {
    return (
        <div className={styles.container}>
            {/* Year Badge */}
            <motion.p
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: false }}
                transition={{ duration: 0.2 }}
                className="text-sm absolute -top-4 left-4 md:left-20 font-medium tracking-wider text-neon-green"
            >
                2024
            </motion.p>

            {/* Phase 1 & 2: Primary Text with Glitch */}
            <div className={styles.primaryTextWrapper}>
                <motion.h1
                    initial={{ x: -100, opacity: 0 }}
                    whileInView={{ x: 0, opacity: 1 }}
                    viewport={{ once: false }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className={styles.primaryLeft}
                >
                    CYBERSECURITY X AI
                </motion.h1>
                <motion.h1
                    initial={{ x: 100, opacity: 0 }}
                    whileInView={{ x: 0, opacity: 1 }}
                    viewport={{ once: false }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className={styles.primaryRight}
                >
                    RESEARCHER
                </motion.h1>
            </div>

            {/* Glitch Overlay Effect */}
            <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: [0, 1, 1, 0] }}
                viewport={{ once: false }}
                transition={{
                    duration: 0.15,
                    delay: 0.4,
                    times: [0, 0.5, 0.8, 1]
                }}
                className={styles.glitchOverlay}
            />

            {/* Phase 3: Secondary Text */}
            <motion.p
                initial={{ y: -50, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                viewport={{ once: false }}
                transition={{
                    duration: 0.4,
                    delay: 0.6,
                    type: "spring",
                    stiffness: 300,
                    damping: 20
                }}
                className={styles.secondaryText}
            >
                ANYASH PRASAD
            </motion.p>
        </div>
    );
}
