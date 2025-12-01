"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";
import {
    UploadCloud,
    File as FileIcon,
    Trash2,
    Loader,
    CheckCircle,
    Plus,
} from "lucide-react";
import { predictImage, predictVideo } from "@/lib/api";

interface FileWithPreview {
    id: string;
    preview: string;
    progress: number;
    name: string;
    size: number;
    type: string;
    lastModified?: number;
    file: File;
    result?: {
        prediction: string;
        confidence: number;
        inference_time: number;
    };
}

export default function EnhancedFileUpload({ onResultsUpdate }: { onResultsUpdate?: (files: FileWithPreview[]) => void }) {
    const [files, setFiles] = useState<FileWithPreview[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const MAX_FILES = 5;

    // Process dropped or selected files
    const handleFiles = (fileList: FileList) => {
        const currentCount = files.length;
        const newFilesArray = Array.from(fileList).slice(0, MAX_FILES - currentCount);

        const newFiles = newFilesArray.map((file) => ({
            id: `${URL.createObjectURL(file)}-${Date.now()}`,
            preview: URL.createObjectURL(file),
            progress: 0,
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: file.lastModified,
            file,
        }));

        setFiles((prev) => [...prev, ...newFiles]);
        // Don't auto-upload - wait for user to click Analyze button
    };

    // Analyze all uploaded files
    const handleAnalyze = () => {
        setIsAnalyzing(true);
        const unanalyzedFiles = files.filter(f => f.progress === 0 && !f.result);

        unanalyzedFiles.forEach((f) => {
            uploadFile(f.id, f.file);
        });
    };

    // Real upload to backend
    const uploadFile = async (id: string, file: File) => {
        try {
            const isImage = file.type.startsWith("image/");
            const isVideo = file.type.startsWith("video/");

            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 20;
                setFiles((prev) =>
                    prev.map((f) =>
                        f.id === id ? { ...f, progress: Math.min(progress, 90) } : f
                    )
                );
                if (progress >= 90) clearInterval(progressInterval);
            }, 200);

            let result;
            if (isImage) {
                result = await predictImage(file);
            } else if (isVideo) {
                result = await predictVideo(file);
            } else {
                throw new Error("Unsupported file type");
            }

            clearInterval(progressInterval);

            const updatedFiles = files.map((f) =>
                f.id === id ? { ...f, progress: 100, result } : f
            );
            setFiles(updatedFiles);

            // Check if all files are done analyzing
            const allDone = updatedFiles.every(f => f.progress === 100 || f.result);
            if (allDone) {
                setIsAnalyzing(false);
            }

            // Notify parent with updated files
            onResultsUpdate?.(updatedFiles);

        } catch (error) {
            console.error("Upload error:", error);
            const errorMessage = error instanceof Error ? error.message : "Analysis failed";
            const updatedFiles = files.map((f) =>
                f.id === id ? {
                    ...f,
                    progress: -1, // Use -1 to indicate error state
                    result: {
                        prediction: "ERROR",
                        confidence: 0,
                        inference_time: 0
                    }
                } : f
            );
            setFiles(updatedFiles);
            setIsAnalyzing(false);
        }
    };

    const onDrop = (e: DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (files.length < MAX_FILES) {
            handleFiles(e.dataTransfer.files);
        }
    };

    const onDragOver = (e: DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const onDragLeave = () => setIsDragging(false);

    const onSelect = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && files.length < MAX_FILES) handleFiles(e.target.files);
    };

    const formatFileSize = (bytes: number): string => {
        if (!bytes) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
    };

    return (
        <div className="w-full max-w-4xl mx-auto p-4 md:p-6">
            {/* Drop zone */}
            <motion.div
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
                onClick={() => inputRef.current?.click()}
                initial={false}
                animate={{
                    borderColor: isDragging ? "#39FF8A" : "rgba(57, 255, 138, 0.2)",
                    scale: isDragging ? 1.02 : 1,
                }}
                whileHover={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
                className={clsx(
                    "relative rounded-3xl p-8 md:p-12 text-center cursor-pointer glass-card",
                    isDragging && "ring-4 ring-neon-green/30 border-neon-green",
                )}
            >
                <div className="flex flex-col items-center gap-5">
                    <motion.div
                        animate={{ y: isDragging ? [-5, 0, -5] : 0 }}
                        transition={{
                            duration: 1.5,
                            repeat: isDragging ? Infinity : 0,
                            ease: "easeInOut",
                        }}
                        className="relative"
                    >
                        <UploadCloud
                            className={clsx(
                                "w-16 h-16 md:w-20 md:h-20",
                                isDragging
                                    ? "text-neon-green"
                                    : "text-text-muted group-hover:text-neon-green transition-colors duration-300",
                            )}
                        />
                    </motion.div>

                    <div className="space-y-2">
                        <h3 className="text-xl md:text-2xl font-semibold text-foreground">
                            {isDragging
                                ? "Drop files here"
                                : files.length
                                    ? `Add more (${files.length}/${MAX_FILES})`
                                    : "Upload files for detection"}
                        </h3>
                        <p className="text-text-muted md:text-lg max-w-md mx-auto">
                            {isDragging ? (
                                <span className="font-medium text-neon-green">
                                    Release to upload
                                </span>
                            ) : (
                                <>
                                    Drag & drop or{" "}
                                    <span className="text-neon-green font-medium">browse</span>
                                </>
                            )}
                        </p>
                        <p className="text-sm text-text-muted">
                            Images and videos • Max {MAX_FILES} files
                        </p>
                    </div>

                    <input
                        ref={inputRef}
                        type="file"
                        multiple
                        hidden
                        onChange={onSelect}
                        accept="image/*,video/*"
                        disabled={files.length >= MAX_FILES}
                    />
                </div>

                {/* Small blue progress bar at bottom */}
                {files.length > 0 && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-glass-border rounded-b-3xl overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{
                                width: `${(files.filter(f => f.progress === 100).length / files.length) * 100}%`
                            }}
                            className="h-full bg-blue-500"
                            transition={{ duration: 0.3 }}
                        />
                    </div>
                )}
            </motion.div>

            {/* Uploaded files grid */}
            <AnimatePresence>
                {files.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mt-8"
                    >
                        <div className="flex justify-between items-center mb-4 px-2">
                            <h3 className="font-semibold text-lg text-foreground">
                                Files ({files.length}/{MAX_FILES})
                            </h3>
                            {files.length < MAX_FILES && (
                                <button
                                    onClick={() => inputRef.current?.click()}
                                    className="flex items-center gap-2 text-sm font-medium px-3 py-2 bg-neon-green/10 hover:bg-neon-green/20 rounded-lg text-neon-green transition-colors"
                                >
                                    <Plus className="w-4 h-4" />
                                    Add More
                                </button>
                            )}
                        </div>

                        {/* Analyze Button - only show if there are unanalyzed files */}
                        {files.some(f => f.progress === 0 && !f.result) && (
                            <div className="mb-6">
                                <motion.button
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    whileHover={!isAnalyzing ? { scale: 1.02 } : {}}
                                    whileTap={!isAnalyzing ? { scale: 0.98 } : {}}
                                    onClick={handleAnalyze}
                                    disabled={isAnalyzing}
                                    className={`w-full py-4 px-6 font-bold text-lg rounded-xl transition-all ${isAnalyzing
                                        ? 'bg-gray-600 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-neon-green to-neon-teal text-background hover:shadow-lg hover:shadow-neon-green/50'
                                        }`}
                                >
                                    {isAnalyzing ? (
                                        <span className="flex items-center justify-center gap-2">
                                            <Loader className="w-5 h-5 animate-spin" />
                                            Analyzing...
                                        </span>
                                    ) : (
                                        `🔍 Analyze ${files.filter(f => f.progress === 0 && !f.result).length} File${files.filter(f => f.progress === 0 && !f.result).length > 1 ? 's' : ''}`
                                    )}
                                </motion.button>
                                {isAnalyzing && (
                                    <p className="text-center text-sm text-neon-green mt-2 animate-pulse">
                                        Processing files with ACE 2.4 model...
                                    </p>
                                )}
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <AnimatePresence>
                                {files.map((file) => (
                                    <motion.div
                                        key={file.id}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                        className="glass-card p-4 rounded-2xl"
                                    >
                                        {/* Preview */}
                                        <div className="relative w-full h-32 mb-3 rounded-lg overflow-hidden bg-background/50">
                                            {file.type.startsWith("image/") ? (
                                                <img
                                                    src={file.preview}
                                                    alt={file.name}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : file.type.startsWith("video/") ? (
                                                <video
                                                    src={file.preview}
                                                    className="w-full h-full object-cover"
                                                    muted
                                                    loop
                                                    playsInline
                                                />
                                            ) : (
                                                <FileIcon className="w-full h-full p-8 text-text-muted" />
                                            )}
                                            {file.progress === 100 && (
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.5 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    className="absolute top-2 right-2 bg-background/90 rounded-full p-1"
                                                >
                                                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                                                </motion.div>
                                            )}
                                        </div>

                                        {/* File info */}
                                        <div>
                                            <p className="font-medium text-sm truncate text-foreground" title={file.name}>
                                                {file.name}
                                            </p>
                                            <div className="flex items-center justify-between text-xs text-text-muted mt-1">
                                                <span>{formatFileSize(file.size)}</span>
                                                <span className="flex items-center gap-1">
                                                    {file.progress === -1 ? (
                                                        <span className="text-red-500 font-medium flex items-center gap-1">
                                                            ❌ Error
                                                        </span>
                                                    ) : file.progress < 100 && file.progress > 0 ? (
                                                        <>
                                                            {Math.round(file.progress)}%
                                                            <Loader className="w-3 h-3 animate-spin text-blue-500" />
                                                        </>
                                                    ) : file.progress === 100 && file.result ? (
                                                        <Trash2
                                                            className="w-4 h-4 cursor-pointer hover:text-red-500 transition-colors"
                                                            onClick={() => setFiles((prev) => prev.filter((f) => f.id !== file.id))}
                                                        />
                                                    ) : null}
                                                </span>
                                            </div>

                                            {/* Progress bar */}
                                            <div className="w-full h-1 bg-glass-border rounded-full overflow-hidden mt-2">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: file.progress === -1 ? "100%" : `${file.progress}%` }}
                                                    className={clsx(
                                                        "h-full rounded-full",
                                                        file.progress === -1 ? "bg-red-500" :
                                                            file.progress < 100 ? "bg-blue-500" : "bg-emerald-500"
                                                    )}
                                                />
                                            </div>

                                            {/* Show result if available */}
                                            {file.result && file.result.prediction !== "ERROR" && (
                                                <div className="mt-3 p-2 bg-background/50 rounded-lg">
                                                    <div className="flex items-center justify-between">
                                                        <span className={`font-bold ${file.result.prediction === "FAKE" ? "text-red-500" : "text-emerald-500"}`}>
                                                            {file.result.prediction}
                                                        </span>
                                                        <span className="text-xs text-text-muted">
                                                            {(file.result.confidence * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                    <p className="text-xs text-text-muted mt-1">
                                                        {file.result.inference_time.toFixed(2)}s
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
