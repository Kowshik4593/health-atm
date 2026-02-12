// frontend/components/CaseCard.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import CaseStatusBadge from './CaseStatusBadge';

interface CaseCardProps {
    caseData: {
        id: string;
        status: 'uploaded' | 'processing' | 'completed' | 'failed';
        uploaded_at: string;
        patient?: {
            id: string;
            full_name: string;
            phone?: string;
            gender?: string;
        };
        results?: {
            findings_json?: any;
        };
        assignment?: {
            doctor_id: string;
            status: string;
            doctor?: {
                full_name: string;
            };
        };
    };
    userRole: 'doctor' | 'operator' | 'patient';
    onAccept?: (caseId: string) => void;
    onView?: (caseId: string) => void;
    showPatientInfo?: boolean;
    showDoctorInfo?: boolean;
    isDark?: boolean;
}

export default function CaseCard({
    caseData,
    userRole,
    onAccept,
    onView,
    showPatientInfo = true,
    showDoctorInfo = false,
    isDark = false,
}: CaseCardProps) {
    const router = useRouter();
    const [accepting, setAccepting] = useState(false);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const handleAccept = async () => {
        if (onAccept && !accepting) {
            setAccepting(true);
            await onAccept(caseData.id);
            setAccepting(false);
        }
    };

    const handleView = () => {
        if (onView) {
            onView(caseData.id);
        } else {
            router.push(`/results/${caseData.id}`);
        }
    };

    const noduleCount = caseData.results?.findings_json?.num_nodules || 0;
    const highRiskCount = caseData.results?.findings_json?.nodules?.filter(
        (n: any) => n.prob_malignant >= 0.7
    ).length || 0;

    const isAssigned = !!caseData.assignment;
    const canAccept = userRole === 'doctor' && !isAssigned && caseData.status === 'completed';
    const canView = caseData.status === 'completed' || caseData.status === 'processing';

    const styles = {
        card: {
            padding: '20px',
            borderRadius: '12px',
            border: `1px solid ${isDark ? '#262626' : '#e5e5e5'}`,
            backgroundColor: isDark ? '#171717' : '#ffffff',
            marginBottom: '12px',
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '16px',
        },
        scanId: {
            fontSize: '11px',
            fontFamily: 'monospace',
            color: isDark ? '#737373' : '#a3a3a3',
            marginBottom: '4px',
        },
        date: {
            fontSize: '12px',
            color: isDark ? '#737373' : '#a3a3a3',
        },
        patientInfo: {
            marginBottom: '16px',
        },
        patientName: {
            fontSize: '16px',
            fontWeight: 600,
            color: isDark ? '#ffffff' : '#171717',
            marginBottom: '4px',
        },
        patientMeta: {
            fontSize: '13px',
            color: isDark ? '#a3a3a3' : '#525252',
        },
        stats: {
            display: 'flex',
            gap: '16px',
            marginBottom: '16px',
            padding: '12px',
            borderRadius: '8px',
            backgroundColor: isDark ? '#0a0a0a' : '#f5f5f5',
        },
        stat: {
            textAlign: 'center' as const,
        },
        statValue: {
            fontSize: '18px',
            fontWeight: 700,
            color: isDark ? '#ffffff' : '#171717',
        },
        statLabel: {
            fontSize: '11px',
            color: isDark ? '#737373' : '#a3a3a3',
            textTransform: 'uppercase' as const,
        },
        statHighRisk: {
            color: '#ef4444',
        },
        doctorInfo: {
            fontSize: '13px',
            color: isDark ? '#a3a3a3' : '#525252',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        },
        actions: {
            display: 'flex',
            gap: '8px',
        },
        btn: {
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            border: 'none',
            transition: 'all 0.15s',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
        },
        btnPrimary: {
            backgroundColor: isDark ? '#ffffff' : '#171717',
            color: isDark ? '#000000' : '#ffffff',
        },
        btnSecondary: {
            backgroundColor: isDark ? '#262626' : '#f5f5f5',
            color: isDark ? '#ffffff' : '#171717',
        },
        btnDisabled: {
            opacity: 0.5,
            cursor: 'not-allowed',
        },
    };

    return (
        <div style={styles.card}>
            <div style={styles.header}>
                <div>
                    <div style={styles.scanId}>ID: {caseData.id.substring(0, 8)}</div>
                    <div style={styles.date}>{formatDate(caseData.uploaded_at)}</div>
                </div>
                <CaseStatusBadge status={isAssigned ? 'assigned' : caseData.status} />
            </div>

            {showPatientInfo && caseData.patient && (
                <div style={styles.patientInfo}>
                    <div style={styles.patientName}>{caseData.patient.full_name}</div>
                    <div style={styles.patientMeta}>
                        {caseData.patient.gender && (
                            <span style={{ textTransform: 'capitalize' }}>
                                {caseData.patient.gender}
                            </span>
                        )}
                        {caseData.patient.phone && (
                            <span> • {caseData.patient.phone}</span>
                        )}
                    </div>
                </div>
            )}

            {caseData.status === 'completed' && caseData.results && (
                <div style={styles.stats}>
                    <div style={styles.stat}>
                        <div style={styles.statValue}>{noduleCount}</div>
                        <div style={styles.statLabel}>Nodules</div>
                    </div>
                    <div style={styles.stat}>
                        <div style={{ ...styles.statValue, ...styles.statHighRisk }}>
                            {highRiskCount}
                        </div>
                        <div style={styles.statLabel}>High Risk</div>
                    </div>
                </div>
            )}

            {showDoctorInfo && caseData.assignment?.doctor && (
                <div style={styles.doctorInfo}>
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Dr. {caseData.assignment.doctor.full_name}
                </div>
            )}

            <div style={styles.actions}>
                {canAccept && (
                    <button
                        style={{
                            ...styles.btn,
                            ...styles.btnPrimary,
                            ...(accepting ? styles.btnDisabled : {}),
                        }}
                        onClick={handleAccept}
                        disabled={accepting}
                    >
                        {accepting ? 'Accepting...' : 'Accept Case'}
                    </button>
                )}
                {canView && (
                    <button
                        style={{ ...styles.btn, ...styles.btnSecondary }}
                        onClick={handleView}
                    >
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        {caseData.status === 'processing' ? 'Check Progress' : 'View Results'}
                    </button>
                )}
            </div>
        </div>
    );
}