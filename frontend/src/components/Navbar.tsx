import Link from 'next/link';
import { Presentation, Cpu } from 'lucide-react';

export default function Navbar() {
    return (
        <nav className="border-b border-neon-blue/20 bg-background/80 backdrop-blur-md sticky top-0 z-50">
            <div className="container flex h-16 max-w-screen-2xl items-center px-6 w-full justify-between mx-auto">
                <Link href="/" className="flex items-center space-x-3 group">
                    <div className="relative">
                        <div className="absolute -inset-1 bg-neon-purple/50 rounded-full blur-sm group-hover:blur-md transition-all duration-300" />
                        <Presentation className="relative h-6 w-6 text-neon-blue" />
                    </div>
                    <span className="font-bold text-xl tracking-tighter text-glow bg-clip-text text-transparent bg-gradient-to-r from-neon-blue to-neon-purple">
                        PITCH_PERFECT
                    </span>
                </Link>
                <div className="flex items-center gap-6">
                    <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-neon-blue/70">
                        <Cpu className="h-3 w-3" />
                        <span>SYSTEM: ONLINE</span>
                    </div>
                    <Link
                        href="https://github.com"
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm font-medium text-foreground/80 hover:text-neon-blue transition-colors tracking-wide uppercase"
                    >
                        GitHub
                    </Link>
                </div>
            </div>
        </nav>
    );
}
