'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Download, Sparkles, Wand2, Bot, User, FileText, Loader2 } from 'lucide-react';

interface ReconstructionPanelProps {
    summary: string;
    problemStatement: string;
    analysis: any;
}

export default function ReconstructionPanel({ summary, problemStatement, analysis }: ReconstructionPanelProps) {
    const [status, setStatus] = useState<'idle' | 'generating' | 'ready'>('idle');
    const [downloadUrl, setDownloadUrl] = useState('');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [structure, setStructure] = useState<any>(null);
    const [chatInput, setChatInput] = useState('');
    const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'system', content: string }[]>([
        { role: 'system', content: 'I have reconstructed your presentation based on the analysis. You can ask me to make further adjustments, like "Add a slide about market size" or "Make the title slide more professional".' }
    ]);
    const [isChatting, setIsChatting] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [chatHistory]);

    const handleGenerate = async () => {
        setStatus('generating');
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        try {
            console.log("Sending reconstruction request to:", `${apiUrl}/reconstruct`);
            const response = await fetch(`${apiUrl}/reconstruct`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    presentation_summary: summary,
                    problem_statement: problemStatement,
                    analysis: analysis,
                    custom_instructions: "Make it better."
                })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Failed to generate PPT: ${response.status} ${errText}`);
            }

            const data = await response.json();
            console.log("Reconstruction success:", data);
            setStructure(data.structure);
            setDownloadUrl(data.download_url);
            setStatus('ready');
        } catch (error) {
            console.error("Reconstruction error:", error);
            setStatus('idle');
            alert("Failed to generate PPT. Check console for details.");
        }
    };

    const handleChat = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!chatInput.trim() || isChatting) return;

        const userMsg = chatInput;
        setChatInput('');
        setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsChatting(true);

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        try {
            console.log("Sending chat refinement to:", `${apiUrl}/reconstruct/chat`);
            const response = await fetch(`${apiUrl}/reconstruct/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_structure: structure,
                    user_message: userMsg,
                    presentation_summary: summary
                })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Failed to refine PPT: ${response.status} ${errText}`);
            }

            const data = await response.json();
            setStructure(data.structure);
            setDownloadUrl(data.download_url); // Update download link to new version
            setChatHistory(prev => [...prev, { role: 'system', content: 'I have updated the presentation based on your request. You can download the new version.' }]);
        } catch (error) {
            console.error("Chat refinement error:", error);
            setChatHistory(prev => [...prev, { role: 'system', content: 'Sorry, I encountered an error while processing your request. Please try again.' }]);
        } finally {
            setIsChatting(false);
        }
    };

    return (
        <div className="w-full max-w-7xl mx-auto mt-12 glass-panel rounded-lg overflow-hidden border border-white/10 relative">

            {/* Background Glow */}
            <div className="absolute top-0 right-0 p-20 opacity-5 pointer-events-none">
                <Wand2 className="h-64 w-64 text-neon-purple" />
            </div>

            <div className="p-8 relative z-10">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 rounded-full bg-neon-purple/20 flex items-center justify-center border border-neon-purple/30">
                        <Sparkles className="h-5 w-5 text-neon-purple" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">AI Reconstruction Studio</h2>
                        <p className="text-slate-400 text-sm">Automatically rebuild your deck with improvements applied.</p>
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    {status === 'idle' && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-slate-900/50 rounded-lg p-8 border border-white/5 text-center"
                        >
                            <div className="max-w-md mx-auto space-y-6">
                                <p className="text-slate-300">
                                    Our AI can reconstruct your presentation to address the identified weaknesses, improve the flow, and apply professional styling.
                                </p>
                                <button
                                    onClick={handleGenerate}
                                    className="group relative inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-neon-purple rounded-full overflow-hidden transition-all hover:bg-neon-purple/80 hover:shadow-[0_0_20px_rgba(168,85,247,0.5)]"
                                >
                                    <span className="relative flex items-center gap-2">
                                        <Wand2 className="h-5 w-5" />
                                        Reconstruct Deck Now
                                    </span>
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {status === 'generating' && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col items-center justify-center py-20 gap-4"
                        >
                            <Loader2 className="h-12 w-12 text-neon-purple animate-spin" />
                            <p className="text-neon-purple font-mono animate-pulse">GENERATING_MAGICAL_DECK...</p>
                        </motion.div>
                    )}

                    {status === 'ready' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="grid grid-cols-1 lg:grid-cols-2 gap-8"
                        >
                            {/* Left: Chat Interface */}
                            <div className="flex flex-col h-[500px] bg-slate-950/50 rounded-lg border border-white/10 overflow-hidden">
                                <div className="p-4 border-b border-white/5 bg-white/5 flex items-center gap-2">
                                    <Bot className="h-4 w-4 text-neon-purple" />
                                    <span className="font-mono text-xs font-bold uppercase tracking-widest text-slate-300">Design Assistant</span>
                                </div>

                                <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                                    {chatHistory.map((msg, i) => (
                                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div
                                                className={`max-w-[80%] p-3 rounded-lg text-sm leading-relaxed ${msg.role === 'user'
                                                    ? 'bg-neon-purple/20 text-white border border-neon-purple/30 rounded-br-none'
                                                    : 'bg-slate-800 text-slate-200 border border-white/10 rounded-bl-none'
                                                    }`}
                                            >
                                                {msg.content}
                                            </div>
                                        </div>
                                    ))}
                                    {isChatting && (
                                        <div className="flex justify-start">
                                            <div className="bg-slate-800 p-3 rounded-lg rounded-bl-none border border-white/10">
                                                <div className="flex gap-1">
                                                    <span className="h-2 w-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                                    <span className="h-2 w-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                                    <span className="h-2 w-2 bg-slate-500 rounded-full animate-bounce"></span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <form onSubmit={handleChat} className="p-4 border-t border-white/5 bg-white/5 flex gap-2">
                                    <input
                                        type="text"
                                        value={chatInput}
                                        onChange={(e) => setChatInput(e.target.value)}
                                        placeholder="Ask for changes (e.g., 'Add a Team slide')..."
                                        className="flex-1 bg-slate-900 border border-white/10 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-purple/50 transition-colors"
                                        disabled={isChatting}
                                    />
                                    <button
                                        type="submit"
                                        disabled={!chatInput.trim() || isChatting}
                                        className="p-2 bg-neon-purple/20 text-neon-purple border border-neon-purple/30 rounded hover:bg-neon-purple/30 disabled:opacity-50 transition-all"
                                    >
                                        <Send className="h-4 w-4" />
                                    </button>
                                </form>
                            </div>

                            {/* Right: Download & Preview Info */}
                            <div className="space-y-6 flex flex-col justify-center">
                                <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-lg">
                                    <h3 className="text-emerald-400 font-bold mb-2 flex items-center gap-2">
                                        <FileText className="h-5 w-5" />
                                        Deck Ready for Download
                                    </h3>
                                    <p className="text-slate-400 text-sm mb-6">
                                        Your reconstructed presentation is ready. You can download it now or use the chat to make further refinements.
                                    </p>

                                    <a
                                        href={process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}${downloadUrl}` : `http://127.0.0.1:8000${downloadUrl}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded transition-colors w-full justify-center"
                                    >
                                        <Download className="h-5 w-5" />
                                        Download Current Version (.pptx)
                                    </a>
                                </div>

                                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                                    <h4 className="text-xs font-mono font-bold uppercase text-slate-500 mb-3">Reconstruction Highlight</h4>
                                    <ul className="space-y-2 text-sm text-slate-400">
                                        <li className="flex gap-2">
                                            <span className="text-neon-green">✓</span>
                                            addressed critical weaknesses
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="text-neon-green">✓</span>
                                            improved narrative flow
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="text-neon-green">✓</span>
                                            professional layout applied
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
