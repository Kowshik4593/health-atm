// frontend/components/Chat/ChatDrawer.tsx

'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Message } from '@/types';
import { useAuth } from '@/hooks/useAuth';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

interface ChatDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    assignmentId: string; // Required to fetch specific chat
    caseId?: string;      // Optional, for context
}

export default function ChatDrawer({ isOpen, onClose, assignmentId }: ChatDrawerProps) {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(true);

    // Poll for new messages every 5s (Simulates Realtime)
    useEffect(() => {
        if (!isOpen || !assignmentId) return;

        loadMessages();
        const interval = setInterval(loadMessages, 5000);

        return () => clearInterval(interval);
    }, [isOpen, assignmentId]);

    async function loadMessages() {
        try {
            const data = await api.getChatMessages(assignmentId);
            setMessages(data);
        } catch (e) {
            console.error('Failed to load chat');
        } finally {
            setLoading(false);
        }
    }

    async function handleSendMessage(text: string) {
        if (!user) return;

        // optimistic update (UI shows message immediately)
        const tempId = crypto.randomUUID();
        const newMessage: Message = {
            id: tempId,
            assignment_id: assignmentId,
            sender_id: user.id,
            message: text,
            sent_at: new Date().toISOString(),
        };

        setMessages(prev => [...prev, newMessage]);

        // Actual API call
        const { success } = await api.sendMessage(assignmentId, text, user.id);

        if (!success) {
            // Revert on failure (simple version: just reload)
            loadMessages();
        }
    }

    // Prevent body scroll when open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => { document.body.style.overflow = 'unset'; };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex justify-end">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            />

            {/* Drawer Panel */}
            <div className="relative w-full max-w-md bg-white dark:bg-neutral-900 shadow-2xl flex flex-col h-full transform transition-transform duration-300 ease-in-out">
                {/* Header */}
                <div className="px-4 py-4 border-b border-gray-100 dark:border-neutral-800 flex items-center justify-between bg-white dark:bg-neutral-900 z-10">
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">Case Discussion</h3>
                        <p className="text-xs text-gray-500">
                            ID: {assignmentId.substring(0, 8)}...
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-full transition-colors"
                    >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>

                {/* Body */}
                {loading ? (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-blue-600" />
                    </div>
                ) : (
                    <MessageList messages={messages} />
                )}

                {/* Footer Input */}
                <ChatInput onSend={handleSendMessage} />
            </div>
        </div>
    );
}