import React from "react";
import clsx from "clsx";
import { Loader } from "lucide-react";

const bars = Array.from({ length: 12 }, (_, i) => ({
    animationDelay: `-${1.2 - i * 0.1}s`,
    transform: `rotate(${i * 30}deg) translate(146%)`,
}));

interface SpinnerProps {
    size?: number;
    color?: string;
}

export const Spinner = ({ size = 20, color = "#39FF8A" }: SpinnerProps) => {
    return (
        <div style={{ width: size, height: size }} className="relative">
            <div className="relative top-1/2 left-1/2" style={{ width: size, height: size }}>
                {bars.map((item, index) => (
                    <div
                        key={index}
                        className="absolute h-[8%] w-[24%] -left-[10%] -top-[3.9%] rounded-[5px]"
                        style={{
                            backgroundColor: color,
                            ...item,
                            animation: "fade-spin 1.2s linear infinite",
                        }}
                    />
                ))}
            </div>
        </div>
    );
};
