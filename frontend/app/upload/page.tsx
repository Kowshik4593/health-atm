'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import supabase from '../../lib/supabaseClient';
import { api } from '../../lib/api';
import { formatFileSize, isValidCTScanFile } from '../../lib/supabase-storage';

interface Profile {
    id: string;
    full_name: string;
    role: string;
}

interface NewPatientData {
    full_name: string;
    phone: string;
    dob: string;
    gender: 'male' | 'female' | 'other';
}

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'success' | 'error';

export default function UploadPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<Profile | null>(null);

    // File state
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    // Upload state
    const [status, setStatus] = useState<UploadStatus>('idle');
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [resultScanId, setResultScanId] = useState<string | null>(null);

    // Patient context (from operator flow)
    const [patientId, setPatientId] = useState<string | null>(null);
    const [patientName, setPatientName] = useState<string>('');
    const [isNewPatient, setIsNewPatient] = useState(false);
    const [newPatientData, setNewPatientData] = useState<NewPatientData | null>(null);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        setTheme(mediaQuery.matches ? 'dark' : 'light');
        const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light');
        mediaQuery.addEventListener('change', handler);
        return () => mediaQuery.removeEventListener('change', handler);
    }, []);

    useEffect(() => {
        loadUserAndContext();
    }, []);

    async function loadUserAndContext() {
        setLoading(true);
        try {
            const { data: { user: authUser }, error: authError } = await supabase.auth.getUser();
            if (authError || !authUser) {
                router.push('/login');
                return;
            }

            const { data: profile } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', authUser.id)
                .single();

            if (!profile) {
                router.push('/complete-profile');
                return;
            }

            setUser(profile);

            // Handle Operator -> Patient Context
            const patientParam = searchParams.get('patient');
            const modeParam = searchParams.get('mode');

            if (patientParam) {
                setPatientId(patientParam);

                // Use Backend API to avoid 406 RLS Error
                try {
                    const patientProfile = await api.getPatientProfile(patientParam);
                    if (patientProfile) setPatientName(patientProfile.full_name);
                } catch (err) {
                    console.warn("Could not fetch patient name:", err);
                    setPatientName("Patient ID: " + patientParam.substring(0, 8));
                }

            } else if (modeParam === 'new-patient') {
                const storedData = sessionStorage.getItem('newPatientData');
                if (storedData) {
                    setNewPatientData(JSON.parse(storedData));
                    setIsNewPatient(true);
                    sessionStorage.removeItem('newPatientData');
                }
            } else if (profile.role === 'patient') {
                // Self-upload
                setPatientId(authUser.id);
                setPatientName(profile.full_name);
            }

        } catch (e) {
            console.error('Load error:', e);
            setError('Failed to load page');
        } finally {
            setLoading(false);
        }
    }

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        if (status === 'idle') setIsDragging(true);
    }, [status]);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (status !== 'idle') return;

        const file = e.dataTransfer.files[0];
        if (file && isValidCTScanFile(file)) {
            setSelectedFile(file);
            setError(null);
        } else {
            setError('Invalid file type. Please upload .zip or .npy files only.');
        }
    }, [status]);

    const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file && isValidCTScanFile(file)) {
            setSelectedFile(file);
            setError(null);
        } else if (file) {
            setError('Invalid file type. Please upload .zip or .npy files only.');
        }
    }, []);

    const handleRemoveFile = useCallback(() => {
        setSelectedFile(null);
        setError(null);
    }, []);

    async function handleStartAnalysis() {
        if (!selectedFile || !user) return;

        let finalPatientId = patientId;

        // 1. Handle Walk-in Patient Creation
        if (isNewPatient && newPatientData) {
            try {
                // Generate a temporary email/pass if none provided
                const email = `walkin.${newPatientData.phone}.${Date.now()}@lungatm.com`;
                const password = `Temp${Date.now()}!`;

                const { success, patientId: newId, error: createError } = await api.createWalkInPatient({
                    ...newPatientData,
                    email,
                    password
                });

                if (!success || !newId) {
                    throw new Error(createError || "Failed to create patient");
                }

                finalPatientId = newId;
                setPatientName(newPatientData.full_name);
            } catch (e: any) {
                console.error("Creation error:", e);
                setStatus('error');
                setError(`Failed to create patient: ${e.message}`);
                return;
            }
        }

        // 2. Handle Self-Upload Fallback
        if (!finalPatientId && user.role === 'patient') {
            finalPatientId = user.id;
        }

        // 3. Validation
        if (!finalPatientId) {
            setStatus('error');
            setError('No patient selected');
            return;
        }

        // 4. Start Upload
        setStatus('uploading');
        setError(null);
        setProgress(10);

        try {
            const progressInterval = setInterval(() => {
                setProgress(p => Math.min(p + 5, 90));
            }, 200);

            // API Call
            const result = await api.uploadScan(selectedFile, finalPatientId);

            clearInterval(progressInterval);
            setProgress(100);

            if (!result.scan_id) {
                throw new Error("Upload failed: No Scan ID returned from server.");
            }

            // 5. Trigger Processing (FOR EVERYONE - Patients, Operators, Doctors)
            setStatus('processing');

            // Fire and Forget: Do NOT await this promise.
            // This prevents the frontend from timing out while the backend processes.
            api.processCase(result.scan_id).catch(err => {
                console.log("Background processing started (or polling will handle errors).");
            });

            // 6. Start Polling (This will wait for the result)
            pollScanStatus(result.scan_id);

        } catch (e: any) {
            console.error("Upload/Process error:", e);
            setStatus('error');
            setError(e.message || 'Upload failed. Please try again.');
        }
    }

    async function pollScanStatus(scanId: string) {
        // --- FIX: INCREASED TIMEOUT TO 20 MINUTES ---
        // 400 attempts * 3 seconds = 1200 seconds = 20 minutes
        const maxAttempts = 400;
        let attempts = 0;

        const poll = async () => {
            attempts++;
            try {
                const { status: scanStatus } = await api.getScanStatus(scanId);

                if (scanStatus === 'completed') {
                    setResultScanId(scanId);
                    setStatus('success');
                    return;
                }

                if (scanStatus === 'failed') {
                    setStatus('error');
                    setError('Analysis failed. The system could not process this scan.');
                    return;
                }

                if (attempts >= maxAttempts) {
                    setStatus('error');
                    setError('Analysis timed out. Please check dashboard later.');
                    return;
                }

                // Poll every 3 seconds
                setTimeout(poll, 3000);
            } catch (e) {
                setTimeout(poll, 3000);
            }
        };

        poll();
    }

    function handleViewResults() {
        if (resultScanId) {
            router.push(`/results/${resultScanId}`);
        }
    }

    function handleReset() {
        setSelectedFile(null);
        setStatus('idle');
        setProgress(0);
        setError(null);
        setResultScanId(null);
    }

    async function handleSignOut() {
        await supabase.auth.signOut();
        router.push('/login');
    }

    function getBackLink(): string {
        if (!user) return '/';
        return `/dashboard/${user.role}`;
    }

    const isDark = theme === 'dark';

    // --- STYLES ---
    const styles = {
        container: { minHeight: '100vh', backgroundColor: isDark ? '#000000' : '#ffffff', color: isDark ? '#fff' : '#000', fontFamily: '"Google Sans", sans-serif' },
        wrapper: { display: 'flex', minHeight: '100vh' },

        // Sidebar
        sidebar: {
            width: '280px', backgroundColor: isDark ? '#121212' : '#ffffff',
            borderRight: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            display: 'flex', flexDirection: 'column' as const,
            position: 'fixed' as const, height: '100vh', left: 0, top: 0, zIndex: 50
        },
        sidebarHeader: { padding: '24px', borderBottom: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}` },
        logo: { display: 'flex', alignItems: 'center', gap: '12px' },
        logoIcon: {
            width: '36px', height: '36px', borderRadius: '8px',
            backgroundColor: '#2563eb', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 700, fontSize: '20px'
        },
        logoText: { fontSize: '20px', fontWeight: 700, letterSpacing: '-0.5px' },
        nav: { flex: 1, padding: '24px 16px' },
        navItem: {
            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px',
            borderRadius: '12px', fontSize: '15px', fontWeight: 500,
            cursor: 'pointer', textDecoration: 'none', marginBottom: '8px',
            color: isDark ? '#a1a1aa' : '#6b7280'
        },
        navItemActive: { backgroundColor: isDark ? '#27272a' : '#eff6ff', color: isDark ? '#ffffff' : '#2563eb' },
        userSection: { padding: '20px', borderTop: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`, backgroundColor: isDark ? '#18181b' : '#f9fafb' },
        userInfo: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' },
        userAvatar: {
            width: '40px', height: '40px', borderRadius: '50%',
            backgroundColor: isDark ? '#3f3f46' : '#dbeafe', color: isDark ? '#fff' : '#1e40af',
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: 600
        },
        userName: { fontSize: '14px', fontWeight: 600 },
        userRole: { fontSize: '12px', color: isDark ? '#a1a1aa' : '#6b7280', textTransform: 'capitalize' as const },
        signOutBtn: { width: '100%', textAlign: 'left' as const, background: 'none', border: 'none', color: '#ef4444', fontSize: '13px', cursor: 'pointer', padding: 0 },

        // Main
        main: { flex: 1, marginLeft: '280px', padding: '40px', maxWidth: '1600px' },
        content: { maxWidth: '720px', margin: '0 auto' },
        backLink: { display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: isDark ? '#a1a1aa' : '#6b7280', textDecoration: 'none', marginBottom: '32px' },

        header: { marginBottom: '40px', textAlign: 'center' as const },
        headerTitle: { fontSize: '32px', fontWeight: 800, marginBottom: '12px' },
        headerSubtitle: { fontSize: '16px', color: isDark ? '#a1a1aa' : '#6b7280' },

        // Patient Badge
        patientBadge: {
            display: 'inline-flex', alignItems: 'center', gap: '12px',
            padding: '12px 20px', borderRadius: '12px',
            backgroundColor: isDark ? '#18181b' : '#f3f4f6',
            border: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            marginBottom: '32px', margin: '0 auto 32px',
        },
        patientLabel: { fontSize: '12px', color: isDark ? '#a1a1aa' : '#6b7280', textTransform: 'uppercase' as const, fontWeight: 700, letterSpacing: '0.5px' },
        patientName: { fontSize: '16px', fontWeight: 600, color: isDark ? '#ffffff' : '#111827' },

        // Upload Card
        card: {
            padding: '40px', borderRadius: '24px',
            backgroundColor: isDark ? '#121212' : '#ffffff',
            border: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        },
        dropzone: {
            padding: '60px 40px', borderRadius: '16px',
            border: `2px dashed ${isDark ? '#3f3f46' : '#d1d5db'}`,
            backgroundColor: isDark ? '#18181b' : '#f9fafb',
            textAlign: 'center' as const, cursor: 'pointer', transition: 'all 0.2s ease',
        },
        dropzoneActive: { borderColor: '#2563eb', backgroundColor: isDark ? '#1e1e24' : '#eff6ff' },
        dropzoneIcon: { width: '64px', height: '64px', color: isDark ? '#525252' : '#9ca3af', margin: '0 auto 24px' },
        dropzoneTitle: { fontSize: '18px', fontWeight: 600, marginBottom: '8px' },
        dropzoneText: { fontSize: '14px', color: isDark ? '#a1a1aa' : '#6b7280', marginBottom: '8px' },

        fileSelected: {
            padding: '24px', borderRadius: '16px',
            backgroundColor: isDark ? '#18181b' : '#f9fafb',
            border: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            marginBottom: '32px'
        },
        fileInfo: { display: 'flex', alignItems: 'center', gap: '20px' },
        fileIcon: {
            width: '56px', height: '56px', borderRadius: '12px',
            backgroundColor: isDark ? '#27272a' : '#ffffff',
            border: `1px solid ${isDark ? '#3f3f46' : '#e5e7eb'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563eb'
        },
        fileDetails: { flex: 1 },
        fileName: { fontSize: '16px', fontWeight: 600, marginBottom: '4px' },
        fileSize: { fontSize: '13px', color: isDark ? '#a1a1aa' : '#6b7280' },
        removeBtn: { padding: '8px', cursor: 'pointer', background: 'none', border: 'none', color: '#ef4444' },

        // Progress
        progressContainer: { padding: '40px', textAlign: 'center' as const },
        progressBar: {
            height: '8px', backgroundColor: isDark ? '#27272a' : '#e5e7eb',
            borderRadius: '100px', overflow: 'hidden', maxWidth: '320px', margin: '24px auto 12px'
        },
        progressFill: { height: '100%', backgroundColor: '#2563eb', transition: 'width 0.3s ease' },
        progressTitle: { fontSize: '20px', fontWeight: 700, marginBottom: '8px' },
        progressText: { fontSize: '14px', color: isDark ? '#a1a1aa' : '#6b7280' },

        // Buttons
        startBtn: {
            width: '100%', padding: '16px', borderRadius: '12px',
            fontSize: '16px', fontWeight: 600, cursor: 'pointer', border: 'none',
            backgroundColor: '#2563eb', color: '#ffffff',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
            transition: 'transform 0.1s ease',
            marginTop: '24px'
        },
        btnGroup: { display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '32px' },
        btn: { padding: '12px 24px', borderRadius: '12px', fontSize: '14px', fontWeight: 600, cursor: 'pointer', border: 'none' },
        btnPrimary: { backgroundColor: '#2563eb', color: '#ffffff' },
        btnSecondary: { backgroundColor: isDark ? '#27272a' : '#f3f4f6', color: isDark ? '#ffffff' : '#1f2937' },

        // Success / Error
        successContainer: { textAlign: 'center' as const, padding: '40px' },
        successIcon: { width: '80px', height: '80px', margin: '0 auto 24px', color: '#22c55e' },
        successTitle: { fontSize: '24px', fontWeight: 700, marginBottom: '12px' },
        successText: { fontSize: '16px', color: isDark ? '#a1a1aa' : '#6b7280', marginBottom: '32px' },
        scanId: { display: 'inline-block', padding: '8px 16px', borderRadius: '8px', backgroundColor: isDark ? '#27272a' : '#f3f4f6', fontFamily: 'monospace', fontSize: '14px', color: isDark ? '#a1a1aa' : '#6b7280' },

        errorContainer: { textAlign: 'center' as const, padding: '40px' },
        errorIcon: { width: '80px', height: '80px', margin: '0 auto 24px', color: '#ef4444' },
        errorTitle: { fontSize: '24px', fontWeight: 700, marginBottom: '12px' },
        errorText: { fontSize: '16px', color: '#ef4444', marginBottom: '32px' },

        loadingContainer: { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: isDark ? '#000000' : '#ffffff' },
        spinner: { width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: '#2563eb', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 20px' },
        formats: { marginTop: '20px', fontSize: '13px', color: isDark ? '#a1a1aa' : '#6b7280' }
    };

    if (loading) {
        return (
            <div style={styles.loadingContainer}>
                <div style={styles.spinner}></div>
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

            <div style={styles.wrapper}>
                {/* Sidebar */}
                <aside style={styles.sidebar}>
                    <div style={styles.sidebarHeader}>
                        <div style={styles.logo}>
                            <div style={styles.logoIcon}>+</div>
                            <span style={styles.logoText}>Lung ATM</span>
                        </div>
                    </div>
                    <nav style={styles.nav}>
                        <Link href={getBackLink()} style={styles.navItem}>
                            Dashboard
                        </Link>
                        <div style={{ ...styles.navItem, backgroundColor: isDark ? '#27272a' : '#eff6ff', color: isDark ? '#ffffff' : '#2563eb' }}>
                            Upload Scan
                        </div>
                    </nav>
                    <div style={styles.userSection}>
                        <div style={styles.userInfo}>
                            <div style={styles.userAvatar}>{user?.full_name?.charAt(0)}</div>
                            <div>
                                <div style={styles.userName}>{user?.full_name}</div>
                                <div style={styles.userRole}>{user?.role}</div>
                            </div>
                        </div>
                        <button style={styles.signOutBtn} onClick={handleSignOut}>Sign Out</button>
                    </div>
                </aside>

                {/* Main Content */}
                <main style={styles.main}>
                    <div style={styles.content}>
                        <Link href={getBackLink()} style={styles.backLink}>← Back to Dashboard</Link>

                        <div style={styles.header}>
                            <h1 style={styles.headerTitle}>Upload CT Scan</h1>
                            <p style={styles.headerSubtitle}>Supported formats: ZIP (DICOM series) or NPY (Preprocessed)</p>
                        </div>

                        {/* Patient Badge */}
                        {(patientName || isNewPatient) && (
                            <div style={styles.patientBadge}>
                                <div>
                                    <div style={styles.patientLabel}>Uploading For Patient</div>
                                    <div style={styles.patientName}>
                                        {isNewPatient ? newPatientData?.full_name : patientName}
                                    </div>
                                </div>
                            </div>
                        )}

                        <div style={styles.card}>
                            {/* IDLE STATE */}
                            {status === 'idle' && !selectedFile && (
                                <div
                                    style={{ ...styles.dropzone, ...(isDragging ? styles.dropzoneActive : {}) }}
                                    onDragOver={handleDragOver}
                                    onDragLeave={handleDragLeave}
                                    onDrop={handleDrop}
                                >
                                    <input type="file" accept=".zip,.npy" onChange={handleFileInput} style={{ display: 'none' }} id="fileInput" />
                                    <label htmlFor="fileInput">
                                        <div style={styles.dropzoneIcon}>
                                            <svg width="100%" height="100%" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                                        </div>
                                        <div style={styles.dropzoneTitle}>Drag & Drop file here</div>
                                        <div style={styles.dropzoneText}>or click to browse computer</div>
                                    </label>
                                </div>
                            )}

                            {/* SELECTED STATE */}
                            {status === 'idle' && selectedFile && (
                                <div>
                                    {/* ERROR ALERT */}
                                    {error && (
                                        <div style={{
                                            padding: '12px',
                                            backgroundColor: '#fef2f2',
                                            color: '#ef4444',
                                            borderRadius: '8px',
                                            marginBottom: '16px',
                                            border: '1px solid #fecaca',
                                            fontSize: '14px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px'
                                        }}>
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <circle cx="12" cy="12" r="10"></circle>
                                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                                            </svg>
                                            {error}
                                        </div>
                                    )}

                                    <div style={styles.fileSelected}>
                                        <div style={styles.fileInfo}>
                                            <div style={styles.fileIcon}>📄</div>
                                            <div style={styles.fileDetails}>
                                                <div style={styles.fileName}>{selectedFile.name}</div>
                                                <div style={styles.fileSize}>{formatFileSize(selectedFile.size)}</div>
                                            </div>
                                            <button style={styles.removeBtn} onClick={handleRemoveFile}>✕</button>
                                        </div>
                                    </div>
                                    <button style={styles.startBtn} onClick={handleStartAnalysis}>
                                        Start Analysis
                                    </button>
                                </div>
                            )}

                            {/* UPLOADING */}
                            {status === 'uploading' && (
                                <div style={styles.progressContainer}>
                                    <div style={styles.spinner}></div>
                                    <div style={styles.progressTitle}>Uploading...</div>
                                    <div style={styles.progressBar}>
                                        <div style={{ ...styles.progressFill, width: `${progress}%` }}></div>
                                    </div>
                                    <div style={styles.progressText}>{progress}% complete</div>
                                </div>
                            )}

                            {/* PROCESSING */}
                            {status === 'processing' && (
                                <div style={styles.progressContainer}>
                                    <div style={styles.spinner}></div>
                                    <div style={styles.progressTitle}>AI Processing...</div>
                                    <div style={{
                                        display: 'flex', flexDirection: 'column', gap: '8px',
                                        marginTop: '20px', alignItems: 'center'
                                    }}>
                                        <div style={{ fontSize: '13px', color: isDark ? '#a1a1aa' : '#6b7280', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ color: '#22c55e', fontSize: '16px' }}>✓</span> Upload Complete
                                        </div>
                                        <div style={{ fontSize: '13px', color: isDark ? '#a1a1aa' : '#6b7280', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <div style={{ width: '12px', height: '12px', border: '2px solid #2563eb', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                                            Running 3D UNet Inference...
                                        </div>
                                        <div style={{ fontSize: '13px', color: isDark ? '#52525b' : '#d1d5db', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ fontSize: '16px' }}>○</span> Nodule Detection &amp; Classification
                                        </div>
                                        <div style={{ fontSize: '13px', color: isDark ? '#52525b' : '#d1d5db', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ fontSize: '16px' }}>○</span> XAI GradCAM Generation
                                        </div>
                                        <div style={{ fontSize: '13px', color: isDark ? '#52525b' : '#d1d5db', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ fontSize: '16px' }}>○</span> Report Generation
                                        </div>
                                    </div>
                                    <div style={{ ...styles.progressText, marginTop: '20px' }}>This may take 2-5 minutes. Please do not close the tab.</div>
                                </div>
                            )}

                            {/* SUCCESS */}
                            {status === 'success' && (
                                <div style={styles.successContainer}>
                                    <div style={styles.successIcon}>
                                        <svg width="100%" height="100%" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                                    </div>
                                    <div style={styles.successTitle}>Analysis Complete</div>
                                    <div style={styles.successText}>The scan has been successfully processed.</div>
                                    <div style={styles.scanId}>ID: {resultScanId?.substring(0, 8)}</div>
                                    <div style={styles.btnGroup}>
                                        <button style={{ ...styles.btn, ...styles.btnPrimary }} onClick={handleViewResults}>View Results</button>
                                        <button style={{ ...styles.btn, ...styles.btnSecondary }} onClick={handleReset}>Upload Another</button>
                                    </div>
                                </div>
                            )}

                            {/* ERROR */}
                            {status === 'error' && (
                                <div style={styles.errorContainer}>
                                    <div style={styles.errorIcon}>
                                        <svg width="100%" height="100%" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                                    </div>
                                    <div style={styles.errorTitle}>Upload Failed</div>
                                    <div style={styles.errorText}>{error}</div>
                                    <button style={{ ...styles.btn, ...styles.btnPrimary }} onClick={handleReset}>Try Again</button>
                                </div>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}