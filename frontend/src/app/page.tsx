'use client';

import { useState } from 'react';
import Navbar from '@/components/Navbar';
import UploadSection from '@/components/UploadSection';
import ResultsView from '@/components/ResultsView';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldCheck, Zap } from 'lucide-react';

export default function Home() {
  const [view, setView] = useState<'upload' | 'results'>('upload');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null); // Type this properly if sharing types

  const handleAnalyze = async (file: File, problemStatement: string) => {
    setIsAnalyzing(true);

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    formData.append('problem_statement', problemStatement);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    try {
      const response = await fetch(`${apiUrl}/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      setResult(data);
      setView('results');
    } catch (error: any) {
      console.error('Error analyzing presentation:', error);
      alert(`Analysis Failed: ${error.message || "Unknown Network Error"}. \n\nCheck if backend is running on port 8000.`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setView('upload');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-neon-blue/30 text-slate-200">
      <Navbar />

      <main className="flex-1 container max-w-7xl mx-auto px-4 py-8 flex flex-col">
        <AnimatePresence mode="wait">
          {view === 'upload' ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 flex flex-col items-center justify-center gap-12"
            >
              <div className="text-center space-y-6 max-w-3xl relative z-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neon-blue/10 border border-neon-blue/20 text-neon-blue text-xs font-mono tracking-widest uppercase mb-4">
                  <Activity className="h-3 w-3" />
                  System Ready
                </div>
                <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-white to-neon-purple text-glow">
                    Pitch Perfect
                  </span>
                </h1>
                <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
                  Advanced AI-driven analysis for your presentations.
                  Optimize flow, clarity, and impact with instant diagnostic feedback.
                </p>

                <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-slate-500 font-mono mt-4">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-neon-green" />
                    <span>SECURE_UPLOAD</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-neon-blue" />
                    <span>REALTIME_ANALYSIS</span>
                  </div>
                </div>
              </div>

              <div className="w-full max-w-xl relative z-10">
                <UploadSection onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
              </div>
            </motion.div>
          ) : (
            <ResultsView result={result} onReset={handleReset} />
          )}
        </AnimatePresence>
      </main>

      {view === 'upload' && (
        <footer className="py-8 text-center text-xs text-slate-600 font-mono uppercase tracking-widest">
          <p>SYSTEM_VERSION 2.0.4 // PITCH_PERFECT_AI</p>
        </footer>
      )}
    </div>
  );
}
