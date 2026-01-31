'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Terminal, CheckCircle2, CircleDashed } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoaderProps {
    steps?: string[];
}

const DEFAULT_STEPS = [
    "Initializing analysis protocol...",
    "Extracting slide metadata and content...",
    "Running BART-Large-CNN summarization...",
    "Computing semantic embeddings (MiniLM-L6-v2)...",
    "Evaluating logical coherence...",
    "Cross-referencing with scoring rubrics...",
    "Generating final evaluation report..."
];

export default function AnalysisLoader({ steps = DEFAULT_STEPS }: LoaderProps) {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        if (currentStep < steps.length - 1) {
            const timeout = setTimeout(() => {
                setCurrentStep(prev => prev + 1);
            }, 1500); // 1.5s per step
            return () => clearTimeout(timeout);
        }
    }, [currentStep, steps.length]);

    return (
        <div className="w-full flex flex-col items-center justify-center p-8 space-y-6">
            <div className="relative">
                <div className="absolute -inset-4 bg-neon-blue/20 blur-xl rounded-full animate-pulse" />
                <div className="relative h-24 w-24 rounded-full border-2 border-neon-blue flex items-center justify-center bg-black/50 backdrop-blur-sm neon-border">
                    <CircleDashed className="h-12 w-12 text-neon-blue animate-[spin_3s_linear_infinite]" />
                </div>
            </div>

            <div className="w-full max-w-md glass-panel rounded-lg p-4 font-mono text-sm overflow-hidden relative">
                <div className="flex items-center gap-2 border-b border-white/10 pb-2 mb-3 text-neon-blue">
                    <Terminal className="h-4 w-4" />
                    <span className="text-xs tracking-wider">SYSTEM_LOG // LIVE_FEED</span>
                </div>

                <div className="space-y-3">
                    {steps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: idx <= currentStep ? 1 : 0.3, x: 0 }}
                            className={cn(
                                "flex items-center gap-3 transition-colors duration-300",
                                idx === currentStep ? "text-neon-blue" : idx < currentStep ? "text-neon-green" : "text-slate-600"
                            )}
                        >
                            {idx < currentStep ? (
                                <CheckCircle2 className="h-4 w-4 shrink-0" />
                            ) : idx === currentStep ? (
                                <span className="h-4 w-4 shrink-0 flex items-center justify-center">
                                    <span className="w-1.5 h-1.5 bg-neon-blue rounded-full animate-ping" />
                                </span>
                            ) : (
                                <span className="w-4 h-4 shrink-0" />
                            )}
                            <span>{step}</span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
