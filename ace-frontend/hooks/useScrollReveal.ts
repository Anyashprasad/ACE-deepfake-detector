"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

export function useScrollReveal(options = { threshold: 0.1, once: true }) {
    const ref = useRef(null);
    const isInView = useInView(ref, options);

    return { ref, isInView };
}
