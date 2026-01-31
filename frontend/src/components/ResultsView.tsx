'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, FileText, BrainCircuit, TrendingUp, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { MetricBar } from './MetricBar';

interface EvaluationResult {
    scores: {
        relevance: number;
        clarity: number;
        technical_accuracy: number;
        structure: number;
        completeness: number;
    };
    overall_score: number;
    strengths: string[];
    weaknesses: string[];
    detailed_analysis: {
        technical_depth: string;
        business_viability: string;
        presentation_flow: string;
    };
    missing_elements: string[];
    summary_evaluation: string;
    // Backward compatibility just in case
    improvement_suggestions?: string[];
}

interface ResultsViewProps {
    result: EvaluationResult;
    onReset: () => void;
}

export default function ResultsView({ result, onReset }: ResultsViewProps) {

    // Ensure we handle detailed_analysis even if it comes back empty/missing (migration safety)
    const analysis = result.detailed_analysis || {
        technical_depth: "Analysis data pending...",
        business_viability: "Analysis data pending...",
        presentation_flow: "Analysis data pending..."
    };

    const metrics = [
        { label: 'Relevance', score: result.scores.relevance, color: 'bg-neon-blue' },
        { label: 'Clarity', score: result.scores.clarity, color: 'bg-neon-purple' },
        { label: 'Tech Accuracy', score: result.scores.technical_accuracy, color: 'bg-emerald-400' },
        { label: 'Structure', score: result.scores.structure, color: 'bg-amber-400' },
        { label: 'Completeness', score: result.scores.completeness, color: 'bg-neon-pink' },
    ];

    return (
        <div className="w-full max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 pb-20">

            {/* 1. Executive HUD */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Verdict Panel */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="lg:col-span-8 glass-panel rounded-lg p-8 relative overflow-hidden flex flex-col justify-between min-h-[250px]"
                >
                    <div className="absolute top-0 right-0 p-6 opacity-10">
                        <BrainCircuit className="h-40 w-40 text-neon-blue" />
                    </div>

                    <div>
                        <div className="flex items-center gap-3 mb-2 text-neon-blue">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-blue opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-neon-blue"></span>
                            </span>
                            <span className="font-mono text-xs tracking-[0.3em] font-bold">LIVE_DIAGNOSTIC</span>
                        </div>
                        <h2 className="text-3xl font-bold text-white mb-6 tracking-tight">Executive Assessment</h2>
                        <div className="prose prose-invert prose-p:text-slate-300 prose-p:leading-relaxed max-w-2xl border-l-[3px] border-neon-blue/50 pl-6">
                            <p className="text-lg">{result.summary_evaluation}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Score Card */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-4 glass-panel rounded-lg p-8 flex flex-col items-center justify-center relative bg-gradient-to-b from-slate-900/50 to-black/50"
                >
                    <span className="font-mono text-xs text-slate-500 uppercase tracking-widest mb-4">Overall Performance</span>

                    <div className="relative flex items-center justify-center">
                        {/* Glowing Ring */}
                        <div className="absolute -inset-4 bg-neon-blue/20 blur-xl rounded-full" />

                        <div className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-400 z-10 tracking-tighter">
                            {result.overall_score}
                        </div>
                        <div className="absolute top-2 -right-8 text-xl text-slate-600 font-mono font-bold">/50</div>
                    </div>

                    <div className="w-full mt-8 bg-black/30 h-2 rounded-full overflow-hidden border border-white/5">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(result.overall_score / 50) * 100}%` }}
                            transition={{ duration: 1.5, ease: "circOut" }}
                            className="h-full bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink"
                        />
                    </div>
                </motion.div>
            </div>

            {/* 2. Detailed Breakdown Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Left Column: Metrics & Analysis */}
                <div className="space-y-8">
                    {/* Metric Bars */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-panel rounded-lg p-6"
                    >
                        <div className="flex items-center gap-2 mb-6 border-b border-white/5 pb-4">
                            <TrendingUp className="h-5 w-5 text-neon-purple" />
                            <h3 className="font-bold text-sm uppercase tracking-widest text-slate-300">Metric Breakdown</h3>
                        </div>
                        <div className="space-y-6">
                            {metrics.map((m, i) => (
                                <MetricBar
                                    key={m.label}
                                    {...m}
                                    maxScore={10}
                                    delay={0.3 + (i * 0.1)}
                                />
                            ))}
                        </div>
                    </motion.div>

                    {/* Detailed Text Analysis */}
                    <div className="space-y-4">
                        <AnalysisCard
                            title="Technical Depth"
                            content={analysis.technical_depth}
                            delay={0.4}
                            type="tech"
                        />
                        <AnalysisCard
                            title="Business Viability"
                            content={analysis.business_viability}
                            delay={0.5}
                            type="biz"
                        />
                        <AnalysisCard
                            title="Presentation Flow"
                            content={analysis.presentation_flow}
                            delay={0.6}
                            type="flow"
                        />
                    </div>
                </div>

                {/* Right Column: Strengths, Weaknesses, Missing */}
                <div className="space-y-6">

                    {/* Strengths */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="glass-panel rounded-lg p-6 border-l-4 border-l-neon-green"
                    >
                        <div className="flex items-center gap-3 mb-4">
                            <CheckCircle2 className="h-5 w-5 text-neon-green" />
                            <h3 className="font-bold text-neon-green uppercase tracking-widest text-sm">Vital Strengths</h3>
                        </div>
                        <ul className="space-y-3">
                            {result.strengths.map((item, i) => (
                                <li key={i} className="flex gap-3 text-sm text-slate-300 leading-relaxed">
                                    <span className="mt-1.5 h-1.5 w-1.5 bg-neon-green rounded-full shrink-0 opacity-50" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </motion.div>

                    {/* Weaknesses */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="glass-panel rounded-lg p-6 border-l-4 border-l-neon-pink"
                    >
                        <div className="flex items-center gap-3 mb-4">
                            <XCircle className="h-5 w-5 text-neon-pink" />
                            <h3 className="font-bold text-neon-pink uppercase tracking-widest text-sm">Critical Flaws</h3>
                        </div>
                        <ul className="space-y-3">
                            {result.weaknesses.map((item, i) => (
                                <li key={i} className="flex gap-3 text-sm text-slate-300 leading-relaxed">
                                    <span className="mt-1.5 h-1.5 w-1.5 bg-neon-pink rounded-full shrink-0 opacity-50" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </motion.div>

                    {/* Missing Elements */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        className="glass-panel rounded-lg p-6 border-l-4 border-l-amber-500 bg-amber-500/5"
                    >
                        <div className="flex items-center gap-3 mb-4">
                            <AlertTriangle className="h-5 w-5 text-amber-500" />
                            <h3 className="font-bold text-amber-500 uppercase tracking-widest text-sm">Missing Components</h3>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {result.missing_elements.map((item, i) => (
                                <span key={i} className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded text-xs font-mono text-amber-500/80 uppercase">
                                    [{item}]
                                </span>
                            ))}
                        </div>
                    </motion.div>

                </div>
            </div>

            <div className="flex justify-center pt-10">
                <button
                    onClick={onReset}
                    className="px-8 py-3 rounded border border-white/10 hover:bg-white/5 hover:border-neon-blue/50 hover:text-neon-blue transition-all font-mono text-sm uppercase tracking-widest"
                >
                    Process New Deck
                </button>
            </div>
        </div>
    );
}

function AnalysisCard({ title, content, delay, type }: { title: string, content: string, delay: number, type: 'tech' | 'biz' | 'flow' }) {
    const colors = {
        tech: "text-blue-400 border-blue-400/20",
        biz: "text-emerald-400 border-emerald-400/20",
        flow: "text-purple-400 border-purple-400/20"
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className={`glass-panel p-5 rounded-lg border-l-2 ${colors[type].replace('text-', 'border-l-')}`}
        >
            <h4 className={`font-mono text-xs font-bold uppercase mb-2 ${colors[type].split(' ')[0]}`}>{title}</h4>
            <p className="text-sm text-slate-400 leading-relaxed">{content}</p>
        </motion.div>
    );
}
