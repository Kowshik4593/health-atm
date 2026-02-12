// frontend/components/AIChatPanel.tsx
// AI-powered chat panel using LangGraph agent via /chat/ai endpoint
// Styled with Tailwind CSS for premium corporate feel

'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    tools_used?: string[];
    timestamp?: string;
}

interface AIChatPanelProps {
    isOpen: boolean;
    onClose: () => void;
    scanId?: string;
    patientId: string;
    userRole?: 'patient' | 'doctor';
    embedded?: boolean; // If true, renders inline instead of fixed overlay
}

export default function AIChatPanel({
    isOpen,
    onClose,
    scanId = 'general',
    patientId,
    userRole = 'patient',
    embedded = false
}: AIChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isInitialized, setIsInitialized] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Initial Load
    useEffect(() => {
        if ((isOpen || embedded) && !isInitialized) {
            loadInitialData();
        }
    }, [isOpen, embedded, isInitialized]);

    // Scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Auto-focus input
    useEffect(() => {
        if (isOpen && !embedded) {
            setTimeout(() => inputRef.current?.focus(), 300);
        }
    }, [isOpen]);

    const loadInitialData = async () => {
        try {
            // 1. Load conversation history
            const historyRes = await fetch(`${API_BASE}/chat/ai/history/${patientId}/${scanId}`);
            const historyData = await historyRes.json();

            if (historyData.messages && historyData.messages.length > 0) {
                setMessages(historyData.messages.map((m: any) => ({
                    role: m.role,
                    content: m.content,
                    timestamp: new Date().toISOString()
                })));
            } else {
                // 2. Load greeting
                const greetRes = await fetch(`${API_BASE}/chat/ai/greeting/${userRole}`);
                const greetData = await greetRes.json();
                setMessages([{
                    role: 'assistant',
                    content: greetData.greeting || getDefaultGreeting(),
                    timestamp: new Date().toISOString()
                }]);
            }
        } catch {
            setMessages([{
                role: 'assistant',
                content: getDefaultGreeting(),
                timestamp: new Date().toISOString()
            }]);
        }
        setIsInitialized(true);
    };

    const getDefaultGreeting = () => {
        return userRole === 'doctor'
            ? "HealthATM Clinical AI Assistant ready. Ask about findings, nodule characterization, or longitudinal comparison."
            : "Hello! I'm the HealthATM AI Assistant. I can help you understand your CT scan results. What would you like to know?";
    };

    const sendMessage = useCallback(async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: Message = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const res = await fetch(`${API_BASE}/chat/ai`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMsg.content,
                    patient_id: patientId,
                    scan_id: scanId,
                    role: userRole
                })
            });

            const data = await res.json();

            const assistantMsg: Message = {
                role: 'assistant',
                content: data.response || "I'm sorry, I couldn't process that request.",
                tools_used: data.tools_used || [],
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, assistantMsg]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm sorry, I'm experiencing a connection issue. Please try again.",
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, patientId, scanId, userRole]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const quickActions = userRole === 'patient'
        ? ["What does my scan show?", "Explain my risk level", "What should I do next?"]
        : ["Summarize findings", "Risk stratification", "Compare with previous"];

    const Container = embedded ? 'div' : motion.div;
    const containerProps = embedded ? { className: "h-full flex flex-col bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden" } : {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: 20 },
        className: "fixed bottom-8 right-8 w-[420px] max-h-[600px] h-[80vh] bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-800 shadow-2xl flex flex-col overflow-hidden z-50 font-sans"
    };

    return (
        <AnimatePresence>
            {(isOpen || embedded) && (
                /* @ts-ignore - container props vary by type */
                <Container {...containerProps}>
                    {/* Header */}
                    <div className="p-4 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 flex justify-between items-center shrink-0">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="font-semibold text-neutral-900 dark:text-white text-sm">HealthATM AI</h3>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                                    {isLoading ? 'Thinking...' : 'Powered by LangGraph'}
                                </p>
                            </div>
                        </div>
                        {!embedded && (
                            <button
                                onClick={onClose}
                                className="p-1.5 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-800 text-neutral-500 transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        )}
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                        {messages.map((msg, i) => (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                key={i}
                                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex-shrink-0 flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-xs font-bold border border-indigo-200 dark:border-indigo-800">
                                        AI
                                    </div>
                                )}
                                <div className={`max-w-[85%] p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                                        ? 'bg-indigo-600 text-white rounded-tr-md'
                                        : 'bg-white dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 border border-neutral-100 dark:border-neutral-700 rounded-tl-md'
                                    }`}>
                                    <div className="whitespace-pre-wrap">{msg.content}</div>
                                    {msg.tools_used && msg.tools_used.length > 0 && (
                                        <div className="mt-2 pt-2 border-t border-dashed border-neutral-200 dark:border-neutral-700">
                                            <div className="flex flex-wrap gap-1.5">
                                                {msg.tools_used.map((tool, t) => (
                                                    <span key={t} className="px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-900 text-[10px] font-medium text-neutral-500 uppercase tracking-wider">
                                                        {tool.replace(/_/g, ' ')}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}

                        {isLoading && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex-shrink-0 flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-xs border border-indigo-200 dark:border-indigo-800">AI</div>
                                <div className="bg-white dark:bg-neutral-800 p-4 rounded-2xl rounded-tl-md border border-neutral-100 dark:border-neutral-700 shadow-sm flex gap-1.5 items-center h-10">
                                    {[0, 1, 2].map((i) => (
                                        <motion.div
                                            key={i}
                                            className="w-1.5 h-1.5 bg-neutral-400 rounded-full"
                                            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                                            transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                                        />
                                    ))}
                                </div>
                            </motion.div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Quick Actions (only show if few messages) */}
                    {messages.length <= 2 && (
                        <div className="px-4 pb-2 flex flex-wrap gap-2">
                            {quickActions.map((action, i) => (
                                <button
                                    key={i}
                                    onClick={() => setInput(action)}
                                    className="px-3 py-1.5 rounded-full bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-600 dark:text-neutral-400 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 dark:hover:bg-indigo-900/30 dark:hover:text-indigo-400 transition-colors"
                                >
                                    {action}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shrink-0">
                        <div className="relative flex items-center">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask follow-up questions..."
                                disabled={isLoading}
                                className="w-full pl-4 pr-12 py-3 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-neutral-400"
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                className="absolute right-2 p-1.5 bg-indigo-600 text-white rounded-lg disabled:opacity-50 disabled:bg-neutral-300 disabled:cursor-not-allowed hover:bg-indigo-700 transition-colors shadow-sm"
                            >
                                <svg className="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                                </svg>
                            </button>
                        </div>
                        <div className="text-center mt-2">
                            <p className="text-[10px] text-neutral-400">
                                AI can make mistakes. Verify critical medical info.
                            </p>
                        </div>
                    </div>
                </Container>
            )}
        </AnimatePresence>
    );
}
