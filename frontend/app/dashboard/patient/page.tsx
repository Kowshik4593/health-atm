'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { Case, ScanResult } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, FileText, Activity, Clock, RefreshCw, UploadCloud, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function PatientDashboardPage() {
    const router = useRouter();
    const { user, loading: authLoading } = useAuth();
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [cases, setCases] = useState<Case[]>([]);
    const [error, setError] = useState<string | null>(null);

    // --- Auth & Initial Load ---
    useEffect(() => {
        if (!authLoading) {
            if (!user) {
                router.push('/login');
            } else if (user.role !== 'patient') {
                router.push(`/dashboard/${user.role}`);
            } else {
                loadDashboardData(user.id);
            }
        }
    }, [user, authLoading, router]);

    // --- Data Fetching ---
    async function loadDashboardData(patientId: string) {
        setError(null);
        try {
            const data = await api.getPatientScans(patientId);
            setCases(data);
        } catch (e) {
            console.error('Dashboard load error:', e);
            setError('Unable to load your scans. Please check your connection.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }

    const handleRefresh = () => {
        if (user) {
            setRefreshing(true);
            loadDashboardData(user.id);
        }
    };

    // --- Helpers ---
    function formatDate(dateString?: string): string {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    }

    function getStatusBadge(status: string) {
        switch (status) {
            case 'completed':
                return <Badge variant="success">Report Ready</Badge>;
            case 'processing':
                return <Badge variant="warning">Analyzing</Badge>;
            case 'failed':
                return <Badge variant="destructive">Failed</Badge>;
            default:
                return <Badge variant="default">Uploaded</Badge>;
        }
    }

    function getHighRiskCount(result?: ScanResult): number {
        return result?.findings_json?.nodules?.filter(n => n.prob_malignant >= 0.7).length || 0;
    }

    function getNoduleCount(result?: ScanResult): number {
        return result?.findings_json?.nodules?.length || 0;
    }

    if (loading || authLoading) {
        return (
            <div className="flex h-96 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"></div>
            </div>
        );
    }

    const completedCases = cases.filter(c => c.status === 'completed');
    const pendingCases = cases.filter(c => c.status === 'processing' || c.status === 'uploaded');

    return (
        <div className="space-y-8">
            {/* AI Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 to-blue-600 p-8 shadow-xl shadow-blue-500/20"
            >
                <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="text-white max-w-xl">
                        <div className="flex items-center gap-3 mb-2">
                            <Bot className="h-6 w-6 text-blue-200" />
                            <h2 className="text-2xl font-bold">Medical AI Assistant</h2>
                        </div>
                        <p className="text-blue-100/90 leading-relaxed">
                            Analyze your health timeline, understand risk factors, and get personalized insights directly from your scan reports.
                        </p>
                    </div>
                    <Link href="/ai-assistant">
                        <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 border-none shadow-lg">
                            Launch Assistant
                        </Button>
                    </Link>
                </div>
                {/* Background Pattern */}
                <div className="absolute right-0 top-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
                <div className="absolute bottom-0 left-0 -ml-16 -mb-16 h-48 w-48 rounded-full bg-indigo-500/20 blur-2xl" />
            </motion.div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200">
                    {error}
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Total Scans</CardTitle>
                        <FileText className="h-4 w-4 text-slate-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{cases.length}</div>
                        <p className="text-xs text-slate-500 mt-1">Lifetime uploads</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Reports Ready</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{completedCases.length}</div>
                        <p className="text-xs text-slate-500 mt-1">Completed analysis</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Processing</CardTitle>
                        <Activity className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{pendingCases.length}</div>
                        <p className="text-xs text-slate-500 mt-1">In progress</p>
                    </CardContent>
                </Card>
                <Card className="border-dashed border-2 bg-transparent hover:bg-slate-50 dark:hover:bg-slate-900/50 cursor-pointer transition-colors group">
                    <Link href="/upload" className="flex flex-col items-center justify-center h-full py-2">
                        <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 mb-2 group-hover:scale-110 transition-transform">
                            <UploadCloud className="h-5 w-5" />
                        </div>
                        <span className="font-semibold text-blue-600">New Upload</span>
                    </Link>
                </Card>
            </div>

            {/* Recent Scans List */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">Recent Scans</h3>
                    <Button variant="ghost" size="sm" onClick={handleRefresh} disabled={refreshing}>
                        <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                </div>

                {cases.length === 0 ? (
                    <Card className="border-dashed py-12 text-center">
                        <div className="flex flex-col items-center justify-center">
                            <div className="h-16 w-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 mb-4">
                                <FileText className="h-8 w-8" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-900">No scans yet</h3>
                            <p className="text-slate-500 max-w-sm mt-2 mb-6">
                                Upload your first CT scan to get an AI-powered analysis of your lung health.
                            </p>
                            <Link href="/upload">
                                <Button>Upload First Scan</Button>
                            </Link>
                        </div>
                    </Card>
                ) : (
                    <div className="grid gap-4">
                        {cases.map((item) => {
                            const noduleCount = getNoduleCount(item.results);
                            const highRisk = getHighRiskCount(item.results);

                            return (
                                <motion.div
                                    key={item.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <Card className="overflow-hidden hover:shadow-md transition-shadow">
                                        <div className="p-6">
                                            <div className="flex items-center justify-between mb-4">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-lg dark:bg-slate-800 dark:text-slate-400">
                                                        {item.patient?.full_name?.charAt(0) || 'P'}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-slate-900 dark:text-white">
                                                            {item.patient?.full_name || 'Patient Scan'}
                                                        </h4>
                                                        <div className="flex items-center gap-2 text-sm text-slate-500">
                                                            <Clock className="h-3 w-3" />
                                                            {formatDate(item.uploaded_at)}
                                                            <span className="text-slate-300">•</span>
                                                            ID: {item.id.substring(0, 8)}
                                                        </div>
                                                    </div>
                                                </div>
                                                {getStatusBadge(item.status)}
                                            </div>

                                            {item.status === 'completed' && (
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">Nodules Found</p>
                                                        <p className="text-lg font-bold text-slate-900 dark:text-white">{noduleCount}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">High Risk</p>
                                                        <p className={`text-lg font-bold ${highRisk > 0 ? 'text-red-500' : 'text-slate-900 dark:text-white'}`}>
                                                            {highRisk}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">Assigned Doctor</p>
                                                        <p className="text-sm font-medium text-slate-900 truncate dark:text-white">
                                                            {item.assignment?.doctor ? `Dr. ${item.assignment.doctor.full_name}` : 'Pending Assignment'}
                                                        </p>
                                                    </div>
                                                    <div className="flex items-end justify-end">
                                                        <Link href={`/results/${item.id}`}>
                                                            <Button size="sm" variant="outline" className="w-full">
                                                                View Report
                                                            </Button>
                                                        </Link>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </Card>
                                </motion.div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}