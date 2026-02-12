'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { Notification } from '@/types';
import NotificationListComponent from './NotificationListComponent';
import { Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function NotificationBell() {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Load notifications when user logs in
    useEffect(() => {
        if (user) {
            loadNotifications();
            // Poll every 30s for new alerts
            const interval = setInterval(loadNotifications, 30000);
            return () => clearInterval(interval);
        }
    }, [user]);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    async function loadNotifications() {
        if (!user) return;
        try {
            const data = await api.getNotifications(user.id);
            setNotifications(data);
        } catch (e) {
            console.error('Failed to load notifications');
        }
    }

    // Mark as read in UI immediately, then sync with backend
    async function handleMarkRead(id: string) {
        // UI Optimistic Update
        setNotifications(prev => prev.map(n =>
            n.id === id ? { ...n, is_read: true } : n
        ));

        // API Call
        await api.markNotificationRead(id);
    }

    const unreadCount = notifications.filter(n => !n.is_read).length;

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`relative rounded-full p-2 transition-all duration-200 hover:bg-slate-100 dark:hover:bg-slate-800 ${isOpen ? 'bg-slate-100 dark:bg-slate-800' : ''}`}
                aria-label="Notifications"
            >
                <Bell className={`h-5 w-5 transition-colors ${isOpen || unreadCount > 0 ? 'text-blue-600 dark:text-blue-400' : 'text-slate-500 dark:text-slate-400'}`} />

                {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-slate-950 animate-pulse" />
                )}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.1 }}
                        className="absolute right-0 mt-2 w-80 z-50 origin-top-right md:right-[-10px] sm:right-0" // Adjusted alignment
                    >
                        <NotificationListComponent
                            notifications={notifications}
                            onMarkRead={handleMarkRead}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}