// frontend/components/Chat/MessageList.tsx

'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { useAuth } from '@/hooks/useAuth';

interface MessageListProps {
    messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
    const { user } = useAuth();
    const bottomRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Format time (e.g., 10:30 AM)
    function formatTime(dateStr: string) {
        return new Date(dateStr).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-neutral-900">
            {messages.length === 0 ? (
                <div className="flex h-full items-center justify-center text-gray-400">
                    <p>No messages yet. Start the conversation.</p>
                </div>
            ) : (
                messages.map((msg) => {
                    const isMe = msg.sender_id === user?.id;

                    return (
                        <div
                            key={msg.id}
                            className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[75%] rounded-2xl px-4 py-2 shadow-sm ${isMe
                                        ? 'bg-blue-600 text-white rounded-br-none'
                                        : 'bg-white dark:bg-neutral-800 text-gray-800 dark:text-gray-200 rounded-bl-none border border-gray-100 dark:border-neutral-700'
                                    }`}
                            >
                                {/* Message Content */}
                                <p className="text-sm whitespace-pre-wrap">{msg.message}</p>

                                {/* Attachment Link (if any) */}
                                {msg.attachment_url && (
                                    <div className="mt-2">
                                        <a
                                            href={msg.attachment_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className={`text-xs underline flex items-center gap-1 ${isMe ? 'text-blue-100' : 'text-blue-500'
                                                }`}
                                        >
                                            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                                            View Attachment
                                        </a>
                                    </div>
                                )}

                                {/* Timestamp */}
                                <p className={`text-[10px] mt-1 text-right ${isMe ? 'text-blue-100' : 'text-gray-400'
                                    }`}>
                                    {formatTime(msg.sent_at)}
                                </p>
                            </div>
                        </div>
                    );
                })
            )}
            <div ref={bottomRef} />
        </div>
    );
}