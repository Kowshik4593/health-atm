'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { Case, Profile } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { User, Users, FileText, Activity, Search, Plus, UploadCloud, CheckCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function OperatorDashboardPage() {
    const router = useRouter();
    const { user, loading: authLoading } = useAuth();

    // Data State
    const [loading, setLoading] = useState(true);
    const [uploadedCases, setUploadedCases] = useState<Case[]>([]);
    const [patients, setPatients] = useState<Profile[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'upload' | 'cases'>('upload');

    const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

    // Upload mode state
    const [uploadMode, setUploadMode] = useState<'new' | 'existing'>('new');
    const [selectedPatientId, setSelectedPatientId] = useState<string>('');
    const [patientSearch, setPatientSearch] = useState('');
    const [isCreatingPatient, setIsCreatingPatient] = useState(false);

    // New patient form state
    const [newPatient, setNewPatient] = useState({
        full_name: '',
        phone: '',
        dob: '',
        gender: 'male' as 'male' | 'female' | 'other',
        email: '',
        password: '',
    });

    // --- Effects ---
    useEffect(() => {
        if (!authLoading) {
            if (!user) {
                router.push('/login');
            } else if (user.role !== 'operator') {
                router.push(`/dashboard/${user.role}`);
            } else {
                loadDashboardData();
            }
        }
    }, [user, authLoading, router]);

    useEffect(() => {
        if (uploadMode === 'existing') {
            const timer = setTimeout(() => {
                loadPatients(patientSearch);
            }, 300);
            return () => clearTimeout(timer);
        }
    }, [patientSearch, uploadMode]);

    // --- API Calls ---
    async function loadDashboardData() {
        setLoading(true);
        setError(null);
        try {
            const cases = await api.getOperatorCases();
            setUploadedCases(cases);
        } catch (e) {
            console.error('Dashboard load error:', e);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    }

    async function loadPatients(search: string = '') {
        try {
            const data = await api.getPatients(search);
            setPatients(data);
        } catch (e) {
            console.error('Error loading patients', e);
        }
    }

    async function handleProcess(caseId: string) {
        setProcessingIds(prev => new Set(prev).add(caseId));
        try {
            await api.processCase(caseId);
            setUploadedCases(prev => prev.map(c =>
                c.id === caseId ? { ...c, status: 'processing' } : c
            ));
        } catch (e) {
            console.error('Processing error:', e);
            alert('Failed to start processing. Please try again.');
        } finally {
            setProcessingIds(prev => {
                const next = new Set(prev);
                next.delete(caseId);
                return next;
            });
        }
    }

    async function handleContinue() {
        setError(null);

        // FLOW 1: Existing Patient
        if (uploadMode === 'existing') {
            if (!selectedPatientId) {
                setError('Please select a patient from the list');
                return;
            }
            router.push(`/upload?patient=${selectedPatientId}`);
            return;
        }

        // FLOW 2: New Walk-in Patient
        if (uploadMode === 'new') {
            if (!newPatient.full_name || !newPatient.phone || !newPatient.dob) {
                setError('Please fill in Name, Phone, and Date of Birth.');
                return;
            }
            if (!newPatient.email || !newPatient.password) {
                setError('Please provide an Email and Password for the patient account.');
                return;
            }

            setIsCreatingPatient(true);
            try {
                const { success, patientId, error: createError } = await api.createWalkInPatient(newPatient);

                if (!success || !patientId) {
                    throw new Error(createError || 'Failed to create patient account');
                }
                router.push(`/upload?patient=${patientId}`);
            } catch (e: any) {
                console.error('Creation error:', e);
                setError(e.message || 'Failed to register patient');
                setIsCreatingPatient(false);
            }
        }
    }

    // --- Render Helpers ---
    function formatDate(dateString?: string): string {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    }

    if (loading || authLoading) {
        return (
            <div className="flex h-96 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Total Uploads</CardTitle>
                        <UploadCloud className="h-4 w-4 text-slate-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">{uploadedCases.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Pending Process</CardTitle>
                        <Activity className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-slate-900 dark:text-white">
                            {uploadedCases.filter(c => c.status === 'uploaded').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500">Completed</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                            {uploadedCases.filter(c => c.status === 'completed').length}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200">
                    {error}
                </div>
            )}

            {/* Main Action Area */}
            <div className="flex flex-col md:flex-row gap-6">
                {/* Tabs */}
                <div className="w-full md:w-64 flex flex-col gap-2 shrink-0">
                    <Button
                        variant={activeTab === 'upload' ? 'primary' : 'ghost'}
                        className={`justify-start gap-2 ${activeTab === 'upload' ? 'bg-slate-900 text-white hover:bg-slate-800' : 'hover:bg-slate-100'}`}
                        onClick={() => setActiveTab('upload')}
                    >
                        <Plus className="h-4 w-4" /> New Upload
                    </Button>
                    <Button
                        variant={activeTab === 'cases' ? 'primary' : 'ghost'}
                        className={`justify-start gap-2 ${activeTab === 'cases' ? 'bg-slate-900 text-white hover:bg-slate-800' : 'hover:bg-slate-100'}`}
                        onClick={() => setActiveTab('cases')}
                    >
                        <FileText className="h-4 w-4" /> Manage Cases
                    </Button>
                </div>

                {/* Content Area */}
                <div className="flex-1">
                    {activeTab === 'upload' && (
                        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                            <Card>
                                <CardHeader>
                                    <CardTitle>Register Patient</CardTitle>
                                    <CardDescription>Register a new patient or select an existing one.</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div className="flex p-1 bg-slate-100 dark:bg-slate-900 rounded-lg w-max">
                                        <button
                                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${uploadMode === 'new' ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900'}`}
                                            onClick={() => setUploadMode('new')}
                                        >
                                            New Walk-in
                                        </button>
                                        <button
                                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${uploadMode === 'existing' ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900'}`}
                                            onClick={() => setUploadMode('existing')}
                                        >
                                            Existing Patient
                                        </button>
                                    </div>

                                    {uploadMode === 'new' ? (
                                        <div className="space-y-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <label className="text-sm font-medium">Full Name</label>
                                                    <Input placeholder="e.g. Rahul Kumar" value={newPatient.full_name} onChange={e => setNewPatient({ ...newPatient, full_name: e.target.value })} />
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-sm font-medium">Phone</label>
                                                    <Input placeholder="9876543210" value={newPatient.phone} onChange={e => setNewPatient({ ...newPatient, phone: e.target.value.replace(/\D/g, '').slice(0, 10) })} />
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <label className="text-sm font-medium">Date of Birth</label>
                                                    <Input type="date" value={newPatient.dob} onChange={e => setNewPatient({ ...newPatient, dob: e.target.value })} />
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-sm font-medium">Gender</label>
                                                    <select
                                                        className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300"
                                                        value={newPatient.gender}
                                                        onChange={e => setNewPatient({ ...newPatient, gender: e.target.value as any })}
                                                    >
                                                        <option value="male">Male</option>
                                                        <option value="female">Female</option>
                                                        <option value="other">Other</option>
                                                    </select>
                                                </div>
                                            </div>

                                            <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                                                <h4 className="text-sm font-semibold mb-3">Login Credentials</h4>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="space-y-2">
                                                        <label className="text-sm font-medium">Email Address</label>
                                                        <Input type="email" placeholder="patient@example.com" value={newPatient.email} onChange={e => setNewPatient({ ...newPatient, email: e.target.value })} />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <label className="text-sm font-medium">Password</label>
                                                        <Input type="text" placeholder="Temp password" value={newPatient.password} onChange={e => setNewPatient({ ...newPatient, password: e.target.value })} />
                                                    </div>
                                                </div>
                                            </div>

                                            <Button className="w-full mt-4" onClick={handleContinue} disabled={isCreatingPatient}>
                                                {isCreatingPatient ? 'Creating Account...' : 'Create & Continue'}
                                            </Button>
                                        </div>
                                    ) : (
                                        <div className="space-y-4">
                                            <div className="relative">
                                                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                                                <Input
                                                    placeholder="Search by name or phone..."
                                                    className="pl-9"
                                                    value={patientSearch}
                                                    onChange={e => setPatientSearch(e.target.value)}
                                                />
                                            </div>

                                            <div className="max-h-60 overflow-y-auto border border-slate-200 rounded-lg dark:border-slate-800">
                                                {patients.length === 0 ? (
                                                    <div className="p-4 text-center text-sm text-slate-500">
                                                        {patientSearch ? 'No patients found' : 'Type to search...'}
                                                    </div>
                                                ) : patients.map(p => (
                                                    <div
                                                        key={p.id}
                                                        className={`p-3 border-b last:border-0 border-slate-100 cursor-pointer hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900 transition-colors ${selectedPatientId === p.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
                                                        onClick={() => setSelectedPatientId(p.id)}
                                                    >
                                                        <div className="font-medium text-slate-900 dark:text-white">{p.full_name}</div>
                                                        <div className="text-xs text-slate-500">{p.phone}</div>
                                                    </div>
                                                ))}
                                            </div>

                                            <Button className="w-full" onClick={handleContinue} disabled={!selectedPatientId}>
                                                Continue with Selected
                                            </Button>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </motion.div>
                    )}

                    {activeTab === 'cases' && (
                        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                            <Card>
                                <CardHeader>
                                    <CardTitle>Manage Cases</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="rounded-md border border-slate-200 dark:border-slate-800 overflow-hidden">
                                        <table className="w-full text-sm text-left">
                                            <thead className="bg-slate-50 text-slate-500 dark:bg-slate-900 dark:text-slate-400 uppercase text-xs">
                                                <tr>
                                                    <th className="px-6 py-3 font-medium">Patient</th>
                                                    <th className="px-6 py-3 font-medium">Date</th>
                                                    <th className="px-6 py-3 font-medium">Status</th>
                                                    <th className="px-6 py-3 font-medium">Action</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                                                {uploadedCases.map(c => {
                                                    const isProcessing = processingIds.has(c.id);
                                                    return (
                                                        <tr key={c.id} className="bg-white hover:bg-slate-50 dark:bg-slate-950 dark:hover:bg-slate-900 transition-colors">
                                                            <td className="px-6 py-4">
                                                                <div className="font-medium text-slate-900 dark:text-white">{c.patient?.full_name || 'Unknown'}</div>
                                                                <div className="text-xs text-slate-500">{c.patient?.phone}</div>
                                                            </td>
                                                            <td className="px-6 py-4 text-slate-500 flex items-center gap-1">
                                                                <Clock className="w-3 h-3" />
                                                                {formatDate(c.uploaded_at)}
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                {c.status === 'completed' && <Badge variant="success">Completed</Badge>}
                                                                {c.status === 'processing' && <Badge variant="warning">Processing</Badge>}
                                                                {c.status === 'uploaded' && <Badge variant="info">Uploaded</Badge>}
                                                                {c.status === 'failed' && <Badge variant="destructive">Failed</Badge>}
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                {c.status === 'uploaded' && (
                                                                    <Button
                                                                        size="sm"
                                                                        onClick={() => handleProcess(c.id)}
                                                                        disabled={isProcessing}
                                                                        className="bg-indigo-600 hover:bg-indigo-700 text-white"
                                                                    >
                                                                        {isProcessing ? 'Starting...' : '⚡ Process'}
                                                                    </Button>
                                                                )}
                                                                {c.status === 'completed' && (
                                                                    <Button
                                                                        size="sm"
                                                                        variant="outline"
                                                                        onClick={() => router.push(`/results/${c.id}`)}
                                                                        className="text-green-600 hover:text-green-700 hover:bg-green-50 border-green-200"
                                                                    >
                                                                        View Results
                                                                    </Button>
                                                                )}
                                                                {c.status === 'processing' && (
                                                                    <span className="text-xs italic text-orange-500 animate-pulse">AI Analyzing...</span>
                                                                )}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                                {uploadedCases.length === 0 && (
                                                    <tr>
                                                        <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                                                            No cases found. Start by uploading a scan.
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    )}
                </div>
            </div>
        </div>
    );
}