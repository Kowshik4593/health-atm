'use client';

import Sidebar from '@/components/Sidebar';
import NotificationBell from '@/components/NotificationBell';
import ThemeToggle from '@/components/ThemeToggle';
import { usePathname } from 'next/navigation';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    // Convert current route to readable title
    const getPageTitle = () => {
        const segments = pathname.split('/').filter(Boolean);
        const lastSegment = segments[segments.length - 1];
        if (!lastSegment || lastSegment === 'dashboard') return 'Overview';
        // Capitalize and remove hyphens
        return lastSegment
            .replace(/-/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-50 transition-colors duration-300">
            <Sidebar />

            <main className="pl-72 transition-all duration-300 ease-in-out">
                {/* Sticky Header */}
                <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200/60 bg-white/80 px-8 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/80 transition-all">
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white capitalize">
                            {getPageTitle()}
                        </h1>
                    </div>

                    <div className="flex items-center gap-4">
                        <ThemeToggle />

                        <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />

                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:ring-slate-800 hover:ring-slate-300 dark:hover:ring-slate-700 transition-all">
                            <NotificationBell />
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <div className="p-8 animate-fade-in-up">
                    {children}
                </div>
            </main>
        </div>
    );
}
