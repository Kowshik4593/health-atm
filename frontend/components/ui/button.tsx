'use client';

import * as React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "children"> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'link';
    size?: 'sm' | 'md' | 'lg' | 'icon';
    loading?: boolean;
    children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', loading, children, ...props }, ref) => {

        const baseStyles = "inline-flex items-center justify-center whitespace-nowrap rounded-xl font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 select-none";

        const variants = {
            primary: "bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 border border-blue-500",
            secondary: "bg-white text-slate-900 shadow-sm border border-slate-200 hover:bg-slate-50 hover:border-slate-300",
            outline: "border border-slate-200 bg-transparent hover:bg-slate-100 text-slate-700",
            ghost: "hover:bg-slate-100 text-slate-600 hover:text-slate-900",
            destructive: "bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg shadow-red-500/25 hover:shadow-red-500/40",
            link: "text-blue-600 underline-offset-4 hover:underline"
        };

        const sizes = {
            sm: "h-8 px-3 text-xs",
            md: "h-10 px-4 py-2 text-sm",
            lg: "h-12 px-8 text-base",
            icon: "h-10 w-10 p-2"
        };

        return (
            <motion.button
                ref={ref}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(baseStyles, variants[variant], sizes[size], className)}
                disabled={loading || props.disabled}
                {...props}
            >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </motion.button>
        );
    }
);
Button.displayName = "Button";

export { Button };
