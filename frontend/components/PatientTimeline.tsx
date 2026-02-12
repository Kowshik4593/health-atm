// frontend/components/PatientTimeline.tsx
// Corporate-styled episodic memory timeline component
// Uses standard Tailwind classes

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TimelineEvent {
    timestamp: string;
    type: string;
    summary: string;
    details: Record<string, any>;
    scan_id?: string;
    source: string;
}

interface TimelineData {
    patient_id: string;
    total_events: number;
    summary: {
        total_scans: number;
        total_chats: number;
        total_reports: number;
        first_visit: string | null;
        last_visit: string | null;
    };
    timeline: TimelineEvent[];
}

interface PatientTimelineProps {
    patientId: string;
    isOpen: boolean;
    onClose: () => void;
}

// Icon mapping
const EVENT_ICONS: Record<string, any> = {
    scan_analysis: (
        <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
    ),
    chat_interaction: (
        <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
    ),
    report_generated: (
        <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
    ),
    doctor_consultation: (
        <svg className="w-5 h-5 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
    ),
    default: (
        <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    )
};

export default function PatientTimeline({ patientId, isOpen, onClose }: PatientTimelineProps) {
    const [data, setData] = useState<TimelineData | null>(null);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        if (isOpen && patientId) {
            loadTimeline();
        }
    }, [isOpen, patientId]);

    const loadTimeline = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/chat/timeline/${patientId}`);
            if (res.ok) {
                const json = await res.json();
                setData(json);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (ts: string) => {
        try {
            return new Date(ts).toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch { return ts; }
    };

    const filteredEvents = data?.timeline?.filter(e => filter === 'all' || e.type === filter) || [];

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black z-40"
                    />

                    {/* Drawer Panel */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed top-0 right-0 w-[480px] h-screen bg-white dark:bg-neutral-900 shadow-2xl z-50 flex flex-col border-l border-neutral-200 dark:border-neutral-800 font-sans"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/50 backdrop-blur sticky top-0 z-10">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Patient Timeline</h2>
                                    <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                                        Episodic memory & longitudinal history
                                    </p>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-400 hover:text-neutral-900 transition-colors"
                                >
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            {/* Stats */}
                            {data?.summary && (
                                <div className="grid grid-cols-3 gap-3">
                                    <div className="bg-white dark:bg-neutral-800 p-3 rounded-xl border border-neutral-100 dark:border-neutral-700 shadow-sm text-center">
                                        <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{data.summary.total_scans}</div>
                                        <div className="text-xs text-neutral-500 font-medium uppercase tracking-wide">Scans</div>
                                    </div>
                                    <div className="bg-white dark:bg-neutral-800 p-3 rounded-xl border border-neutral-100 dark:border-neutral-700 shadow-sm text-center">
                                        <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{data.summary.total_chats}</div>
                                        <div className="text-xs text-neutral-500 font-medium uppercase tracking-wide">Dialogues</div>
                                    </div>
                                    <div className="bg-white dark:bg-neutral-800 p-3 rounded-xl border border-neutral-100 dark:border-neutral-700 shadow-sm text-center">
                                        <div className="text-2xl font-bold text-amber-500">{data.summary.total_reports}</div>
                                        <div className="text-xs text-neutral-500 font-medium uppercase tracking-wide">Reports</div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Filter Bar */}
                        <div className="px-6 py-3 border-b border-neutral-100 dark:border-neutral-800 flex gap-2 overflow-x-auto no-scrollbar">
                            {['all', 'scan_analysis', 'chat_interaction', 'report_generated'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors whitespace-nowrap ${filter === f
                                            ? 'bg-neutral-900 text-white dark:bg-white dark:text-black'
                                            : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-400'
                                        }`}
                                >
                                    {f === 'all' ? 'All Events' : f.replace(/_/g, ' ')}
                                </button>
                            ))}
                        </div>

                        {/* Timeline List */}
                        <div className="flex-1 overflow-y-auto p-6 relative bg-white dark:bg-neutral-900">
                            {loading ? (
                                <div className="flex flex-col items-center justify-center h-40 text-neutral-400 gap-3">
                                    <div className="w-6 h-6 border-2 border-neutral-300 border-t-indigo-600 rounded-full animate-spin" />
                                    <span className="text-sm">Loading history...</span>
                                </div>
                            ) : filteredEvents.length === 0 ? (
                                <div className="text-center py-12 text-neutral-400">
                                    <p>No events found for this filter.</p>
                                </div>
                            ) : (
                                <div className="relative pl-4 space-y-8">
                                    {/* Vertical Line */}
                                    <div className="absolute left-4 top-2 bottom-2 w-px bg-neutral-200 dark:bg-neutral-800" />

                                    {filteredEvents.map((event, i) => (
                                        <div key={i} className="relative pl-8">
                                            {/* Icon Dot */}
                                            <div className="absolute left-0 top-1 w-8 h-8 rounded-full border-4 border-white dark:border-neutral-900 bg-neutral-50 dark:bg-neutral-800 flex items-center justify-center shadow-sm z-10">
                                                {EVENT_ICONS[event.type] || EVENT_ICONS.default}
                                            </div>

                                            {/* Content Card */}
                                            <div className="bg-neutral-50 dark:bg-neutral-800/50 rounded-xl p-4 border border-neutral-100 dark:border-neutral-800 hover:border-neutral-200 dark:hover:border-neutral-700 transition-colors group">
                                                <div className="flex justify-between items-start mb-2">
                                                    <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                                                        {event.type.replace(/_/g, ' ')}
                                                    </span>
                                                    <span className="text-[10px] text-neutral-400 tabular-nums">
                                                        {formatDate(event.timestamp)}
                                                    </span>
                                                </div>

                                                <h4 className="text-sm font-medium text-neutral-900 dark:text-neutral-100 mb-2 leading-relaxed">
                                                    {event.summary}
                                                </h4>

                                                {/* Details Overlay */}
                                                {event.details && Object.keys(event.details).length > 0 && (
                                                    <div className="mt-3 flex flex-wrap gap-1.5">
                                                        {Object.entries(event.details)
                                                            .filter(([_, v]) => typeof v !== 'object' && v !== null)
                                                            .slice(0, 3)
                                                            .map(([k, v], j) => (
                                                                <span key={j} className="text-[10px] px-2 py-1 rounded bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 text-neutral-500">
                                                                    <span className="font-medium text-neutral-700 dark:text-neutral-300">{k}:</span> {String(v)}
                                                                </span>
                                                            ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
