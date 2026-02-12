// frontend/components/LoadingSpinner.tsx

'use client';

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    message?: string;
}

export default function LoadingSpinner({
    size = 'md',
    message
}: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: 'w-5 h-5',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
    };

    return (
        <div className="flex flex-col items-center justify-center gap-3">
            <div
                className={`${sizeClasses[size]} border-2 border-neutral-200 border-t-neutral-800 rounded-full animate-spin`}
            />
            {message && (
                <p className="text-sm text-neutral-500">{message}</p>
            )}
        </div>
    );
}