// frontend/components/UploadZone.tsx

'use client';

import { useState, useCallback } from 'react';

interface UploadZoneProps {
    onFileSelect: (file: File) => void;
    accept?: string;
    disabled?: boolean;
}

export default function UploadZone({
    onFileSelect,
    accept = '.zip,.npy,.npz,.dcm',
    disabled = false,
}: UploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
    }, [disabled]);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setIsDragging(false);

            if (disabled) return;

            const file = e.dataTransfer.files[0];
            if (file && isValidFile(file)) {
                setSelectedFile(file);
                onFileSelect(file);
            }
        },
        [disabled, onFileSelect]
    );

    const handleFileInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (file && isValidFile(file)) {
                setSelectedFile(file);
                onFileSelect(file);
            }
        },
        [onFileSelect]
    );

    function isValidFile(file: File): boolean {
        const validExtensions = ['.zip', '.npy', '.npz', '.dcm'];
        return validExtensions.some((ext) =>
            file.name.toLowerCase().endsWith(ext)
        );
    }

    function formatFileSize(bytes: number): string {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${disabled
                ? 'bg-neutral-50 border-neutral-200 cursor-not-allowed'
                : isDragging
                    ? 'bg-neutral-100 border-neutral-400'
                    : 'bg-white border-neutral-300 hover:border-neutral-400'
                }`}
        >
            {selectedFile ? (
                // File selected state
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
                        <svg
                            className="w-6 h-6 text-green-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                            />
                        </svg>
                    </div>
                    <div>
                        <p className="font-medium text-neutral-900">{selectedFile.name}</p>
                        <p className="text-sm text-neutral-500">
                            {formatFileSize(selectedFile.size)}
                        </p>
                    </div>
                    <button
                        onClick={() => setSelectedFile(null)}
                        className="text-sm text-neutral-500 hover:text-neutral-700 underline"
                    >
                        Choose different file
                    </button>
                </div>
            ) : (
                // Empty state
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center">
                        <svg
                            className="w-8 h-8 text-neutral-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>

                    <div>
                        <p className="font-medium text-neutral-900">
                            Drag and drop your CT scan file
                        </p>
                        <p className="text-sm text-neutral-500 mt-1">
                            or click to browse (.dcm, .zip, .npy)
                        </p>
                    </div>

                    <input
                        type="file"
                        accept={accept}
                        onChange={handleFileInput}
                        disabled={disabled}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                </div>
            )}
        </div>
    );
}