'use client';

import { Notification } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, Clock, BellOff } from 'lucide-react';

interface NotificationListComponentProps {
    notifications: Notification[];
    onMarkRead: (id: string) => void;
}

export default function NotificationListComponent({ notifications, onMarkRead }: NotificationListComponentProps) {

    function formatTime(dateString: string) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return date.toLocaleDateString();
    }

    return (
        <Card className="shadow-xl border-slate-200 dark:border-slate-800 bg-white/95 backdrop-blur-sm dark:bg-slate-950/95 overflow-hidden">
            <CardHeader className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                    <span>Notifications</span>
                    {notifications.length > 0 && (
                        <span className="text-xs font-normal text-slate-500">
                            {notifications.filter(n => !n.is_read).length} unread
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="max-h-[350px] overflow-y-auto custom-scrollbar">
                    {notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 px-4 text-center text-slate-500">
                            <BellOff className="h-8 w-8 mb-2 opacity-50" />
                            <p className="text-sm">No new notifications</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-slate-100 dark:divide-slate-800">
                            {notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`relative group flex gap-3 p-4 transition-colors hover:bg-slate-50 dark:hover:bg-slate-900/50 ${!notification.is_read ? 'bg-blue-50/30 dark:bg-blue-900/10' : ''
                                        }`}
                                >
                                    <div className={`mt-1 h-2 w-2 rounded-full shrink-0 ${!notification.is_read ? 'bg-blue-500' : 'bg-transparent'}`} />

                                    <div className="flex-1 space-y-1">
                                        <p className={`text-sm leading-snug ${!notification.is_read ? 'font-medium text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-400'}`}>
                                            {notification.message}
                                        </p>
                                        <div className="flex items-center gap-2 text-xs text-slate-400">
                                            <Clock className="h-3 w-3" />
                                            {formatTime(notification.created_at)}
                                        </div>
                                    </div>

                                    {!notification.is_read && (
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onMarkRead(notification.id);
                                            }}
                                            title="Mark as read"
                                        >
                                            <Check className="h-3 w-3 text-blue-500" />
                                        </Button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </CardContent>
            {notifications.length > 0 && (
                <div className="p-2 bg-slate-50 dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 text-center">
                    <Button variant="ghost" size="sm" className="w-full text-xs h-7 text-slate-500">
                        View All
                    </Button>
                </div>
            )}
        </Card>
    );
}