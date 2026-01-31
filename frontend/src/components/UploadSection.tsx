'use client';

import { useState, useRef } from 'react';
import { UploadCloud, File, X, AlertCircle, ScanLine } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import AnalysisLoader from './AnalysisLoader';

interface UploadSectionProps {
    onAnalyze: (file: File, problemStatement: string) => void;
    isAnalyzing: boolean;
}

export default function UploadSection({ onAnalyze, isAnalyzing }: UploadSectionProps) {
    const [file, setFile] = useState<File | null>(null);
    const [problemStatement, setProblemStatement] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            validateAndSetFile(droppedFile);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setError(null);
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (file: File) => {
        if (!file.name.endsWith('.pptx')) {
            setError('Please upload a valid .pptx file.');
            return;
        }
        setFile(file);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a presentation file.');
            return;
        }
        if (!problemStatement.trim()) {
            setError('Please enter a problem statement.');
            return;
        }
        onAnalyze(file, problemStatement);
    };

    if (isAnalyzing) {
        return <AnalysisLoader />;
    }

    return (
        <div className="w-full max-w-xl mx-auto p-1 rounded-xl bg-gradient-to-b from-neon-blue/30 to-neon-purple/30 shadow-[0_0_40px_rgba(0,243,255,0.1)]">
            <div className="bg-[#0a0a1a] rounded-xl p-8 border border-white/5 relative overflow-hidden backdrop-blur-xl">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-neon-blue via-neon-purple to-neon-blue opacity-50" />

                <h2 className="text-2xl font-bold mb-8 text-center tracking-wider text-glow">
                    INITIATE_ANALYSIS
                </h2>

                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* File Upload Area */}
                    <div
                        className={cn(
                            "relative border-2 border-dashed rounded-lg p-10 transition-all duration-300 cursor-pointer flex flex-col items-center justify-center gap-4 text-center group overflow-hidden",
                            isDragging
                                ? "border-neon-blue bg-neon-blue/10 scale-[1.02]"
                                : "border-white/10 hover:border-neon-blue/50 hover:bg-white/5",
                            file ? "border-neon-green/50 bg-neon-green/5" : ""
                        )}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        {/* Scanline Effect */}
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-neon-blue/5 to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000 ease-in-out pointer-events-none" />

                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept=".pptx"
                            className="hidden"
                        />

                        <AnimatePresence mode="wait">
                            {file ? (
                                <motion.div
                                    key="file-selected"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="flex flex-col items-center gap-3 z-10"
                                >
                                    <div className="h-16 w-16 rounded-full bg-neon-green/10 flex items-center justify-center text-neon-green border border-neon-green/30 shadow-[0_0_15px_rgba(10,255,10,0.2)]">
                                        <File className="h-8 w-8" />
                                    </div>
                                    <div className="space-y-1">
                                        <p className="font-mono text-neon-green text-sm truncate max-w-[200px]">{file.name}</p>
                                        <p className="text-xs text-slate-400 font-mono">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setFile(null);
                                        }}
                                        className="absolute top-2 right-2 p-2 rounded-full hover:bg-red-500/20 hover:text-red-400 transition-colors"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="upload-prompt"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="flex flex-col items-center gap-4 z-10"
                                >
                                    <div className="h-14 w-14 rounded-full bg-white/5 flex items-center justify-center group-hover:text-neon-blue group-hover:shadow-[0_0_20px_rgba(0,243,255,0.3)] transition-all duration-300">
                                        <UploadCloud className="h-7 w-7" />
                                    </div>
                                    <div>
                                        <p className="font-bold text-lg tracking-wide uppercase">Upload Deck</p>
                                        <p className="text-sm text-slate-400 font-mono mt-1">.PPTX files supported</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Problem Statement Input */}
                    <div className="space-y-3">
                        <label htmlFor="problem-statement" className="text-xs font-mono text-neon-blue uppercase tracking-widest flex items-center gap-2">
                            <ScanLine className="h-3 w-3" />
                            Evaluation Parameters
                        </label>
                        <textarea
                            id="problem-statement"
                            placeholder="DEFINE PROBLEM STATEMENT OR EVALUATION CONTEXT..."
                            className="w-full min-h-[100px] p-4 rounded-lg border border-white/10 bg-black/20 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all font-mono"
                            value={problemStatement}
                            onChange={(e) => setProblemStatement(e.target.value)}
                        />
                    </div>

                    {/* Error Message */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="flex items-center gap-3 text-red-400 text-sm bg-red-950/30 border border-red-500/30 p-3 rounded-md font-mono"
                            >
                                <AlertCircle className="h-4 w-4" />
                                <p>{error}</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Action Button */}
                    <button
                        type="submit"
                        disabled={!file}
                        className={cn(
                            "w-full py-4 px-4 rounded-lg font-bold uppercase tracking-widest transition-all duration-300 relative overflow-hidden",
                            !file
                                ? "bg-white/5 text-white/20 cursor-not-allowed"
                                : "bg-neon-blue text-black hover:shadow-[0_0_30px_rgba(0,243,255,0.6)] hover:scale-[1.01]"
                        )}
                    >
                        Run Diagnostics
                    </button>
                </form>
            </div>
        </div>
    );
}
