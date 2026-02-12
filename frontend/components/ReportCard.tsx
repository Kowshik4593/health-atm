// frontend/components/ReportCard.tsx

'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import supabase from '@/lib/supabaseClient';

interface ReportCardProps {
    studyId: string;
    type: 'clinician' | 'patient';
    disabled?: boolean;
}

const LANGUAGES = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'te', name: 'Telugu' },
    { code: 'ta', name: 'Tamil' },
    { code: 'kn', name: 'Kannada' },
    { code: 'ml', name: 'Malayalam' },
    { code: 'mr', name: 'Marathi' },
    { code: 'bn', name: 'Bengali' },
    { code: 'gu', name: 'Gujarati' },
];

export default function ReportCard({ studyId, type, disabled }: ReportCardProps) {
    const [loading, setLoading] = useState(false);
    const [selectedLang, setSelectedLang] = useState('en');
    const [statusMessage, setStatusMessage] = useState<string | null>(null);

    const isClinician = type === 'clinician';

    async function handleDownload() {
        setLoading(true);
        setStatusMessage(null);

        try {
            // 1. Get path from API
            const urls = await api.getReportUrls(studyId);
            const reportPath = isClinician
                ? urls.clinician_report?.url
                : urls.patient_report?.url;

            if (!reportPath) {
                throw new Error("Report not generated yet.");
            }

            // 2. Get Public URL from Supabase
            const { data } = supabase.storage
                .from('reports') // Bucket name
                .getPublicUrl(reportPath);

            if (!data.publicUrl) {
                throw new Error("Could not generate public URL.");
            }

            // 3. Open in new tab
            window.open(data.publicUrl, '_blank');
            setStatusMessage('Report opened in new tab');

        } catch (err: any) {
            console.error("Download failed:", err);
            setStatusMessage(err.message || "Download failed");
        } finally {
            setLoading(false);
            setTimeout(() => setStatusMessage(null), 3000);
        }
    }

    return (
        <div className="p-6 rounded-xl border border-neutral-200 bg-white shadow-sm relative overflow-hidden">

            {/* Status Toast (Notification Overlay) */}
            {statusMessage && (
                <div className="absolute inset-0 bg-green-50/90 backdrop-blur-sm flex items-center justify-center p-4 z-10 animate-fade-in">
                    <div className="flex items-center gap-2 text-green-700 font-medium text-sm">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {statusMessage}
                    </div>
                </div>
            )}

            <div className="flex items-start gap-4">
                {/* Icon */}
                <div
                    className={`w-12 h-12 rounded-lg flex items-center justify-center ${isClinician ? 'bg-blue-100' : 'bg-green-100'
                        }`}
                >
                    <svg
                        className={`w-6 h-6 ${isClinician ? 'text-blue-600' : 'text-green-600'}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                </div>

                {/* Content */}
                <div className="flex-1">
                    <h3 className="font-semibold text-neutral-900">
                        {isClinician ? 'Clinician Report' : 'Patient Report'}
                    </h3>
                    <p className="text-sm text-neutral-500 mt-1">
                        {isClinician
                            ? 'Detailed technical report for medical professionals'
                            : 'Easy-to-understand summary for patients'}
                    </p>

                    {/* Language selector for patient report */}
                    {!isClinician && (
                        <div className="mt-3">
                            <label className="block text-xs text-neutral-500 mb-1">
                                Select Language
                            </label>
                            <select
                                value={selectedLang}
                                onChange={(e) => setSelectedLang(e.target.value)}
                                disabled={disabled || loading}
                                className="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-neutral-200 cursor-pointer"
                            >
                                {LANGUAGES.map((lang) => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Download button */}
                    <button
                        onClick={handleDownload}
                        disabled={disabled || loading}
                        className={`mt-4 w-full px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2 ${disabled || loading
                            ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                            : 'bg-neutral-900 text-white hover:bg-neutral-800'
                            }`}
                    >
                        {loading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-neutral-400 border-t-white rounded-full animate-spin"></div>
                                Generating...
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download PDF
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}