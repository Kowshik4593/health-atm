'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { Case, DoctorAssignment, ScanResult } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { User, Activity, FileText, CheckCircle, Clock, AlertTriangle, Stethoscope } from 'lucide-react';
import { motion } from 'framer-motion';

export default function DoctorDashboardPage() {
    const router = useRouter();
    const { user, loading: authLoading } = useAuth();

    // Data State
    const [loading, setLoading] = useState(true);
    const [pendingCases, setPendingCases] = useState<Case[]>([]);
    const [acceptedCases, setAcceptedCases] = useState<DoctorAssignment[]>([]);

    // UI State
    const [activeTab, setActiveTab] = useState<'pending' | 'accepted'>('pending');
    const [acceptingId, setAcceptingId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Auth & Initial Load
    useEffect(() => {
        if (!authLoading) {
            if (!user) {
                router.push('/login');
            } else if (user.role !== 'doctor') {
                router.push(`/dashboard/${user.role}`);
            } else {
                loadDashboardData(user.id);
            }
        }
    }, [user, authLoading, router]);

    async function loadDashboardData(userId: string) {
        setLoading(true);
        setError(null);
        try {
            const [pending, accepted] = await Promise.all([
                api.getPendingCases(),
                api.getDoctorCases(userId)
            ]);
            setPendingCases(pending);
            setAcceptedCases(accepted);
        } catch (e) {
            console.error('Dashboard load error:', e);
            setError('Failed to load dashboard data. Please refresh.');
        } finally {
            setLoading(false);
        }
    }

    async function handleAcceptCase(scanId: string) {
        if (!user) return;

        setAcceptingId(scanId);
        setError(null);

        try {
            const { success, error: apiError } = await api.acceptCase(scanId, user.id);

            if (!success) {
                setError(apiError || 'Failed to accept case');
                loadDashboardData(user.id);
                return;
            }

            await loadDashboardData(user.id);
            setActiveTab('accepted');

        } catch (e) {
            console.error('Accept case error:', e);
            setError('An unexpected error occurred');
        } finally {
            setAcceptingId(null);
        }
    }

    // --- Helpers ---
    function formatDate(dateString?: string): string {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
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

    return (
        <div className="space-y-8">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Pending Assignment</CardTitle>
                        <User className="h-4 w-4 text-slate-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{pendingCases.length}</div>
                        <p className="text-xs text-slate-500 mt-1">Cases needing review</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">My Patients</CardTitle>
                        <Stethoscope className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{acceptedCases.length}</div>
                        <p className="text-xs text-slate-500 mt-1">Active cases</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">High Risk</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-red-600 dark:text-red-400">
                            {pendingCases.filter(c => getHighRiskCount(c.results) > 0).length +
                                acceptedCases.filter(c => getHighRiskCount(c.scan?.results) > 0).length}
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Requiring immediate attention</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Completed</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                            {acceptedCases.filter(c => c.status === 'completed').length}
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Reports finalized</p>
                    </CardContent>
                </Card>
            </div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200">
                    {error}
                </div>
            )}

            {/* List Section */}
            <div>
                <div className="flex gap-2 mb-6 border-b border-slate-200 dark:border-slate-800 pb-1">
                    <Button
                        variant={activeTab === 'pending' ? 'primary' : 'ghost'}
                        onClick={() => setActiveTab('pending')}
                        className="rounded-b-none"
                    >
                        Unassigned Cases <Badge variant="secondary" className="ml-2">{pendingCases.length}</Badge>
                    </Button>
                    <Button
                        variant={activeTab === 'accepted' ? 'primary' : 'ghost'}
                        onClick={() => setActiveTab('accepted')}
                        className="rounded-b-none"
                    >
                        My Patients <Badge variant="secondary" className="ml-2">{acceptedCases.length}</Badge>
                    </Button>
                </div>

                {activeTab === 'pending' && (
                    <div className="space-y-4">
                        {pendingCases.length === 0 ? (
                            <Card className="py-12 text-center">
                                <CardContent className="flex flex-col items-center">
                                    <div className="h-16 w-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 mb-4 dark:bg-slate-900">
                                        <CheckCircle className="h-8 w-8" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">All Caught Up</h3>
                                    <p className="text-slate-500 mt-2">There are no pending cases requiring assignment.</p>
                                </CardContent>
                            </Card>
                        ) : (
                            pendingCases.map(caseItem => {
                                const highRisk = getHighRiskCount(caseItem.results);
                                return (
                                    <motion.div
                                        key={caseItem.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Card className="hover:shadow-md transition-shadow">
                                            <div className="p-6 flex flex-col md:flex-row items-center justify-between gap-6">
                                                <div className="flex items-center gap-4 flex-1">
                                                    <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-lg dark:bg-slate-800 dark:text-slate-400">
                                                        {caseItem.patient?.full_name?.charAt(0) || 'P'}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-slate-900 dark:text-white">
                                                            {caseItem.patient?.full_name || 'Unknown Patient'}
                                                        </h4>
                                                        <div className="flex items-center gap-2 text-sm text-slate-500">
                                                            <Clock className="h-3 w-3" />
                                                            {formatDate(caseItem.uploaded_at)}
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex gap-8 text-center">
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">Nodules</p>
                                                        <p className="font-bold text-lg">{getNoduleCount(caseItem.results)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">High Risk</p>
                                                        <p className={`font-bold text-lg ${highRisk > 0 ? 'text-red-500' : ''}`}>{highRisk}</p>
                                                    </div>
                                                </div>

                                                <div>
                                                    <Button
                                                        onClick={() => handleAcceptCase(caseItem.id)}
                                                        disabled={acceptingId === caseItem.id}
                                                        className="w-full md:w-auto"
                                                    >
                                                        {acceptingId === caseItem.id ? 'Accepting...' : 'Accept Case'}
                                                    </Button>
                                                </div>
                                            </div>
                                        </Card>
                                    </motion.div>
                                );
                            })
                        )}
                    </div>
                )}

                {activeTab === 'accepted' && (
                    <div className="space-y-4">
                        {acceptedCases.length === 0 ? (
                            <Card className="py-12 text-center">
                                <CardContent className="flex flex-col items-center">
                                    <div className="h-16 w-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 mb-4 dark:bg-slate-900">
                                        <User className="h-8 w-8" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">No Patients Yet</h3>
                                    <p className="text-slate-500 mt-2">Accept a pending case to start managing patients.</p>
                                </CardContent>
                            </Card>
                        ) : (
                            acceptedCases.map(assignment => {
                                const highRisk = getHighRiskCount(assignment.scan?.results);
                                return (
                                    <motion.div
                                        key={assignment.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Card className="hover:shadow-md transition-shadow">
                                            <div className="p-6 flex flex-col md:flex-row items-center justify-between gap-6">
                                                <div className="flex items-center gap-4 flex-1">
                                                    <div className="h-12 w-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 font-bold text-lg dark:bg-blue-900/20 dark:text-blue-400">
                                                        {assignment.scan?.patient?.full_name?.charAt(0) || 'P'}
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <h4 className="font-semibold text-slate-900 dark:text-white">
                                                                {assignment.scan?.patient?.full_name}
                                                            </h4>
                                                            <Badge variant={assignment.status === 'completed' ? 'success' : 'info'}>
                                                                {assignment.status === 'completed' ? 'Completed' : 'Active'}
                                                            </Badge>
                                                        </div>
                                                        <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                                                            <Clock className="h-3 w-3" />
                                                            Accepted: {formatDate(assignment.accepted_at)}
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex gap-8 text-center">
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">Nodules</p>
                                                        <p className="font-bold text-lg">{getNoduleCount(assignment.scan?.results)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase text-slate-400 mb-1">High Risk</p>
                                                        <p className={`font-bold text-lg ${highRisk > 0 ? 'text-red-500' : ''}`}>{highRisk}</p>
                                                    </div>
                                                </div>

                                                <div>
                                                    <Link href={`/results/${assignment.scan?.id}`}>
                                                        <Button variant="outline" className="w-full md:w-auto">
                                                            View Report
                                                        </Button>
                                                    </Link>
                                                </div>
                                            </div>
                                        </Card>
                                    </motion.div>
                                );
                            })
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}