// frontend/app/ai-assistant/page.tsx
'use client';

import { Suspense } from 'react';
import Sidebar from '@/components/Sidebar';
import AIChatPanel from '@/components/AIChatPanel';
import { useAuth } from '@/hooks/useAuth';

function AIChatPageContent() {
    const { user } = useAuth();

    return (
        <div className="flex min-h-screen bg-neutral-50 dark:bg-black font-sans">
            <Sidebar />
            <main className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12">
                <div className="w-full max-w-4xl h-[85vh] flex flex-col">
                    <div className="mb-8 text-center">
                        <h1 className="text-3xl font-bold tracking-tight text-neutral-900 dark:text-white mb-2">
                            Medical AI Assistant
                        </h1>
                        <p className="text-neutral-500 dark:text-neutral-400 max-w-2xl mx-auto">
                            Your personal health companion. Ask about your timeline, general medical questions, or review past scan insights.
                        </p>
                    </div>

                    <div className="flex-1 bg-white dark:bg-neutral-900 rounded-3xl shadow-xl overflow-hidden border border-neutral-200 dark:border-neutral-800 relative">
                        {/* We use the embedded mode of AIChatPanel */}
                        <AIChatPanel
                            isOpen={true}
                            onClose={() => { }}
                            scanId="general"
                            patientId={user?.id || 'anonymous'}
                            userRole={user?.role === 'doctor' ? 'doctor' : 'patient'}
                            embedded={true}
                        />
                    </div>
                </div>
            </main>
        </div>
    );
}

export default function AIChatPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-neutral-50" />}>
            <AIChatPageContent />
        </Suspense>
    );
}
