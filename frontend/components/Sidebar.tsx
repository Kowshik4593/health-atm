'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import NotificationBell from './NotificationBell';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { LayoutDashboard, UploadCloud, FileText, Bot, LogOut, User } from 'lucide-react';

interface NavItem {
    label: string;
    href: string;
    icon: React.ElementType;
    roles?: ('doctor' | 'operator' | 'patient')[];
}

const navItems: NavItem[] = [
    {
        label: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
    },
    {
        label: 'Upload Scan',
        href: '/upload',
        icon: UploadCloud,
        roles: ['doctor', 'operator'],
    },
    {
        label: 'All Scans',
        href: '/scans',
        icon: FileText,
    },
    {
        label: 'AI Assistant',
        href: '/ai-assistant',
        icon: Bot,
        roles: ['patient', 'doctor'],
    },
];

export default function Sidebar() {
    const pathname = usePathname();
    const { user, signOut } = useAuth();

    const filteredItems = navItems.filter((item) => {
        if (!item.roles) return true;
        return user && item.roles.includes(user.role);
    });

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-72 border-r border-slate-200/60 bg-white/80 backdrop-blur-xl transition-all dark:border-slate-800 dark:bg-slate-950/80">
            {/* Logo Section */}
            <div className="flex h-20 items-center justify-between px-6 border-b border-slate-100 dark:border-slate-900">
                <Link href="/dashboard" className="flex items-center gap-3 group">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/20 transition-transform group-hover:scale-105">
                        <span className="text-xl font-bold text-white">L</span>
                    </div>
                    <div>
                        <span className="block text-lg font-bold text-slate-900 dark:text-white leading-none">Lung ATM</span>
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Premium AI Diagnostics</span>
                    </div>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto px-4 py-6">
                <ul className="space-y-2">
                    {filteredItems.map((item) => {
                        const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

                        return (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        "relative flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
                                        isActive
                                            ? "text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400"
                                            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-900/50 dark:hover:text-slate-200"
                                    )}
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeNav"
                                            className="absolute left-0 h-8 w-1 rounded-r-full bg-blue-600"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ duration: 0.2 }}
                                        />
                                    )}
                                    <item.icon className={cn("h-5 w-5 transition-colors", isActive ? "text-blue-600 dark:text-blue-400" : "text-slate-400 group-hover:text-slate-600")} />
                                    <span>{item.label}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* User Section */}
            {user && (
                <div className="border-t border-slate-100 p-4 dark:border-slate-900">
                    <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3 dark:bg-slate-900/50">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200 text-slate-700 dark:bg-slate-800 dark:ring-slate-700 dark:text-slate-200">
                            {user.full_name?.charAt(0) || <User className="h-5 w-5" />}
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">
                                {user.full_name || 'User'}
                            </p>
                            <p className="truncate text-xs font-medium text-slate-500 capitalize dark:text-slate-400">
                                {user.role}
                            </p>
                        </div>
                        <button
                            onClick={signOut}
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-white hover:text-red-500 hover:shadow-sm transition-all dark:hover:bg-slate-800"
                            title="Sign out"
                        >
                            <LogOut className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}
        </aside>
    );
}