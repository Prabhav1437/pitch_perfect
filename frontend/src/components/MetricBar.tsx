'use client';

import { motion } from 'framer-motion';

interface MetricBarProps {
    label: string;
    score: number;
    maxScore: number;
    color: string;
    delay?: number;
}

export function MetricBar({ label, score, maxScore, color, delay = 0 }: MetricBarProps) {
    const percentage = (score / maxScore) * 100;

    return (
        <div className="space-y-2">
            <div className="flex justify-between items-end">
                <span className="font-mono text-xs text-slate-400 uppercase tracking-widest">{label}</span>
                <span className={`font-mono text-sm font-bold ${color.replace('bg-', 'text-')}`}>
                    {score}/{maxScore}
                </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden relative">
                {/* Background Grid Lines for easier reading */}
                <div className="absolute inset-0 flex">
                    {[...Array(10)].map((_, i) => (
                        <div key={i} className="flex-1 border-r border-slate-700/30 last:border-none" />
                    ))}
                </div>

                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 1, delay, ease: "easeOut" }}
                    className={`h-full ${color} shadow-[0_0_10px_currentColor] rounded-full`}
                />
            </div>
        </div>
    );
}
