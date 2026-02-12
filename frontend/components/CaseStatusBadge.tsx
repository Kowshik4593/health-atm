// frontend/components/CaseStatusBadge.tsx

'use client';

type CaseStatus = 'uploaded' | 'processing' | 'completed' | 'failed' | 'assigned';

interface CaseStatusBadgeProps {
    status: CaseStatus;
}

export default function CaseStatusBadge({ status }: CaseStatusBadgeProps) {
    const getStatusConfig = (status: CaseStatus) => {
        switch (status) {
            case 'uploaded':
                return {
                    label: 'Uploaded',
                    className: 'bg-amber-50 text-amber-700 border-amber-200 ring-1 ring-amber-200',
                };
            case 'processing':
                return {
                    label: 'Processing',
                    className: 'bg-blue-50 text-blue-700 border-blue-200 ring-1 ring-blue-200',
                };
            case 'completed':
                return {
                    label: 'Completed',
                    className: 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-1 ring-emerald-200',
                };
            case 'assigned':
                return {
                    label: 'Assigned',
                    className: 'bg-purple-50 text-purple-700 border-purple-200 ring-1 ring-purple-200',
                };
            case 'failed':
                return {
                    label: 'Failed',
                    className: 'bg-red-50 text-red-700 border-red-200 ring-1 ring-red-200',
                };
            default:
                return {
                    label: status,
                    className: 'bg-neutral-50 text-neutral-700 border-neutral-200 ring-1 ring-neutral-200',
                };
        }
    };

    const config = getStatusConfig(status);

    return (
        <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
        >
            {config.label}
        </span>
    );
}