// frontend/components/StatsCard.tsx

'use client';

interface StatsCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    icon?: React.ReactNode;
    trend?: 'up' | 'down' | 'neutral';
}

export default function StatsCard({
    title,
    value,
    subtitle,
    icon,
    trend,
}: StatsCardProps) {
    return (
        <div className="p-6 rounded-xl border border-neutral-200 bg-white">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-neutral-500 mb-1">{title}</p>
                    <p className="text-2xl font-bold text-neutral-900">{value}</p>
                    {subtitle && (
                        <p className="text-xs text-neutral-400 mt-1">{subtitle}</p>
                    )}
                </div>
                {icon && (
                    <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center">
                        {icon}
                    </div>
                )}
            </div>
        </div>
    );
}