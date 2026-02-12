// frontend/components/Chat/ChatInput.tsx

'use client';

import { useState, useRef } from 'react';

interface ChatInputProps {
    onSend: (message: string) => Promise<void>;
    disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    async function handleSubmit(e?: React.FormEvent) {
        e?.preventDefault();
        if (!message.trim() || sending) return;

        setSending(true);
        try {
            await onSend(message);
            setMessage('');
            // Reset height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        } finally {
            setSending(false);
        }
    }

    // Auto-resize textarea
    function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
        setMessage(e.target.value);
        e.target.style.height = 'auto';
        e.target.style.height = `${e.target.scrollHeight}px`;
    }

    function handleKeyDown(e: React.KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    }

    return (
        <form
            onSubmit={handleSubmit}
            className="p-4 bg-white dark:bg-neutral-800 border-t border-gray-200 dark:border-neutral-700"
        >
            <div className="flex items-end gap-2">
                {/* Attachment Button (Placeholder for Phase 2) */}
                <button
                    type="button"
                    className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                    title="Attach file (Coming Soon)"
                >
                    <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                </button>

                {/* Text Area */}
                <div className="flex-1 relative">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a message..."
                        disabled={disabled || sending}
                        rows={1}
                        className="w-full resize-none rounded-xl border border-gray-200 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-900 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-32"
                    />
                </div>

                {/* Send Button */}
                <button
                    type="submit"
                    disabled={!message.trim() || disabled || sending}
                    className={`p-2.5 rounded-full transition-all ${message.trim() && !sending
                            ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                            : 'bg-gray-100 dark:bg-neutral-700 text-gray-400 cursor-not-allowed'
                        }`}
                >
                    {sending ? (
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                    )}
                </button>
            </div>
        </form>
    );
}