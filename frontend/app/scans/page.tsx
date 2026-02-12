// frontend/app/scans/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { Case, ScanResult } from '@/types';

export default function ScansPage() {
    const router = useRouter();
    const { user, loading: authLoading, signOut } = useAuth();

    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const [loading, setLoading] = useState(true);

    // Data State
    const [scans, setScans] = useState<Case[]>([]);
    const [filter, setFilter] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
    const [error, setError] = useState<string | null>(null);

    // Detect system theme
    useEffect(() => {
        if (typeof window === 'undefined') return;
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        setTheme(mediaQuery.matches ? 'dark' : 'light');
        const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light');
        mediaQuery.addEventListener('change', handler);
        return () => mediaQuery.removeEventListener('change', handler);
    }, []);

    // Auth & Load
    useEffect(() => {
        if (!authLoading) {
            if (!user) {
                router.push('/login');
            } else if (user.role === 'patient') {
                // Patients should not see the global scan list
                router.push('/dashboard/patient');
            } else {
                loadScans();
            }
        }
    }, [user, authLoading, router]);

    async function loadScans() {
        setLoading(true);
        try {
            // Using getOperatorCases because it returns the full list with patient details
            const data = await api.getOperatorCases();
            setScans(data);
        } catch (e) {
            console.error(e);
            setError('Failed to load scan registry');
        } finally {
            setLoading(false);
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

    // Filter Logic
    const filteredScans = filter === 'all'
        ? scans
        : scans.filter(s => s.status === filter);

    const isDark = theme === 'dark';

    // --- STYLES (Health ATM Design System) ---
    const styles = {
        container: {
            minHeight: '100vh',
            backgroundColor: isDark ? '#000000' : '#f9fafb',
            color: isDark ? '#ffffff' : '#111827',
            fontFamily: '"Google Sans", sans-serif',
        },
        wrapper: { display: 'flex', minHeight: '100vh' },

        // Sidebar
        sidebar: {
            width: '280px',
            backgroundColor: isDark ? '#121212' : '#ffffff',
            borderRight: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            display: 'flex', flexDirection: 'column' as const,
            position: 'fixed' as const, height: '100vh', left: 0, top: 0, zIndex: 50
        },
        sidebarHeader: { padding: '24px 32px', borderBottom: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}` },
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
            cursor: 'pointer', transition: 'all 0.2s ease', textDecoration: 'none', marginBottom: '8px',
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

        header: { marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
        headerTitle: { fontSize: '32px', fontWeight: 800, marginBottom: '8px' },
        headerSubtitle: { fontSize: '15px', color: isDark ? '#a1a1aa' : '#6b7280' },

        newBtn: {
            padding: '12px 24px', borderRadius: '10px', backgroundColor: isDark ? '#ffffff' : '#111827',
            color: isDark ? '#000000' : '#ffffff', border: 'none', fontWeight: 600, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', fontSize: '14px'
        },

        // Filters
        filterBar: { display: 'flex', gap: '8px', marginBottom: '24px' },
        filterBtn: {
            padding: '8px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: 600,
            cursor: 'pointer', border: 'none', transition: 'all 0.2s', textTransform: 'capitalize' as const
        },
        filterBtnActive: { backgroundColor: isDark ? '#ffffff' : '#111827', color: isDark ? '#000000' : '#ffffff' },
        filterBtnInactive: { backgroundColor: isDark ? '#27272a' : '#ffffff', color: isDark ? '#a1a1aa' : '#6b7280', border: `1px solid ${isDark ? '#3f3f46' : '#e5e7eb'}` },

        // Table
        tableCard: {
            backgroundColor: isDark ? '#18181b' : '#ffffff',
            borderRadius: '16px', border: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            overflow: 'hidden', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        },
        table: { width: '100%', borderCollapse: 'collapse' as const },
        th: {
            padding: '16px 24px', textAlign: 'left' as const, fontSize: '12px',
            textTransform: 'uppercase' as const, fontWeight: 700,
            color: isDark ? '#a1a1aa' : '#6b7280',
            borderBottom: `1px solid ${isDark ? '#27272a' : '#e5e7eb'}`,
            backgroundColor: isDark ? '#27272a' : '#f9fafb'
        },
        td: {
            padding: '20px 24px', borderBottom: `1px solid ${isDark ? '#27272a' : '#f3f4f6'}`,
            fontSize: '14px', verticalAlign: 'middle'
        },

        statusBadge: { padding: '6px 12px', borderRadius: '100px', fontSize: '12px', fontWeight: 600, display: 'inline-block' },
        viewBtn: { color: isDark ? '#a1a1aa' : '#6b7280', textDecoration: 'none', fontSize: '13px', fontWeight: 500, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' },

        loadingContainer: { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: isDark ? '#000000' : '#ffffff' },
        spinner: { width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: '#2563eb', borderRadius: '50%', animation: 'spin 0.8s linear infinite' },
        emptyState: { padding: '64px', textAlign: 'center' as const, color: isDark ? '#a1a1aa' : '#6b7280' }
    };

    if (loading || authLoading) {
        return (
            <div style={styles.loadingContainer}>
                <div style={styles.spinner}></div>
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <div style={styles.wrapper}>
                {/* Sidebar */}
                <aside style={styles.sidebar}>
                    <div style={styles.sidebarHeader}>
                        <div style={styles.logo}>
                            <div style={styles.logoIcon}>≡</div>
                            <span style={styles.logoText}>Lung ATM</span>
                        </div>
                    </div>
                    <nav style={styles.nav}>
                        <Link href={`/dashboard/${user?.role || 'operator'}`} style={styles.navItem}>
                            Dashboard
                        </Link>
                        <div style={{ ...styles.navItem, ...styles.navItemActive }}>
                            All Scans
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
                        <button style={styles.signOutBtn} onClick={signOut}>Sign Out</button>
                    </div>
                </aside>

                {/* Main Content */}
                <main style={styles.main}>
                    <div style={styles.header}>
                        <div>
                            <h1 style={styles.headerTitle}>Scan Registry</h1>
                            <p style={styles.headerSubtitle}>Total {scans.length} records found in database.</p>
                        </div>
                        <Link href="/upload" style={styles.newBtn}>+ New Scan</Link>
                    </div>

                    {/* Filters */}
                    <div style={styles.filterBar}>
                        {(['all', 'completed', 'processing', 'failed'] as const).map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                style={filter === f ? styles.filterBtnActive : styles.filterBtnInactive}
                                className="filter-btn" // For simple class targeting if needed
                                // Override CSS class with inline style
                                // @ts-ignore
                                style2={{ ...styles.filterBtn, ...(filter === f ? styles.filterBtnActive : styles.filterBtnInactive) }}
                            >
                                {f}
                            </button>
                        ))}
                        {/* Fix for mapping style properly above */}
                        <style>{`
                            .filter-btn {
                                padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600;
                                cursor: pointer; border: none; transition: all 0.2s; text-transform: capitalize;
                                background-color: ${isDark ? '#27272a' : '#ffffff'};
                                color: ${isDark ? '#a1a1aa' : '#6b7280'};
                                border: 1px solid ${isDark ? '#3f3f46' : '#e5e7eb'};
                            }
                        `}</style>
                    </div>

                    {/* Table */}
                    <div style={styles.tableCard}>
                        {filteredScans.length === 0 ? (
                            <div style={styles.emptyState}>No scans match this filter.</div>
                        ) : (
                            <table style={styles.table}>
                                <thead>
                                    <tr>
                                        <th style={styles.th}>Patient</th>
                                        <th style={styles.th}>Study ID</th>
                                        <th style={styles.th}>Uploaded</th>
                                        <th style={styles.th}>Nodules</th>
                                        <th style={styles.th}>Status</th>
                                        <th style={styles.th}></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredScans.map((scan) => {
                                        const noduleCount = getNoduleCount(scan.results);
                                        const highRisk = getHighRiskCount(scan.results);

                                        return (
                                            <tr key={scan.id}>
                                                <td style={styles.td}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                        <div style={{
                                                            width: '32px', height: '32px', borderRadius: '50%',
                                                            backgroundColor: isDark ? '#27272a' : '#f3f4f6',
                                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                            fontSize: '12px', fontWeight: 600
                                                        }}>
                                                            {scan.patient?.full_name.charAt(0) || 'U'}
                                                        </div>
                                                        <span style={{ fontWeight: 600, color: isDark ? '#fff' : '#111827' }}>
                                                            {scan.patient?.full_name || 'Unknown'}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td style={{ ...styles.td, fontFamily: 'monospace', color: isDark ? '#a1a1aa' : '#6b7280' }}>
                                                    {scan.id.substring(0, 8)}
                                                </td>
                                                <td style={{ ...styles.td, color: isDark ? '#a1a1aa' : '#6b7280' }}>
                                                    {formatDate(scan.uploaded_at)}
                                                </td>
                                                <td style={styles.td}>
                                                    {scan.status === 'completed' ? (
                                                        <span>
                                                            {noduleCount}
                                                            {highRisk > 0 && (
                                                                <span style={{ color: '#ef4444', marginLeft: '6px', fontSize: '12px', fontWeight: 600 }}>
                                                                    ({highRisk} High Risk)
                                                                </span>
                                                            )}
                                                        </span>
                                                    ) : (
                                                        <span style={{ color: '#71717a' }}>—</span>
                                                    )}
                                                </td>
                                                <td style={styles.td}>
                                                    <span style={{
                                                        ...styles.statusBadge,
                                                        backgroundColor: scan.status === 'completed' ? 'rgba(34, 197, 94, 0.1)' : scan.status === 'processing' ? 'rgba(234, 179, 8, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                                                        color: scan.status === 'completed' ? '#22c55e' : scan.status === 'processing' ? '#eab308' : '#3b82f6'
                                                    }}>
                                                        {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                                                    </span>
                                                </td>
                                                <td style={styles.td}>
                                                    {scan.status === 'completed' && (
                                                        <Link href={`/results/${scan.id}`} style={styles.viewBtn}>
                                                            View Report →
                                                        </Link>
                                                    )}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}