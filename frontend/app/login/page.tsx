// frontend/app/login/page.tsx

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import supabase from '../../lib/supabaseClient';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Detect system theme
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setTheme(mediaQuery.matches ? 'dark' : 'light');

    const handler = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const isDark = theme === 'dark';

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setStatus(null);
    setLoading(true);

    try {
      // Sign in with email + password (no OTP)
      const { data: authData, error: signErr } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signErr) {
        setStatus(`Sign-in error: ${signErr.message}`);
        setLoading(false);
        return;
      }

      if (!authData.user) {
        setStatus('Login failed. Please try again.');
        setLoading(false);
        return;
      }

      setStatus('Checking profile...');

      // Fetch User Profile to get Role
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('role')
        .eq('id', authData.user.id)
        .single();

      // Handle Missing Profile (New User) vs Existing User
      if (profileError || !profile) {
        setStatus('New account detected. Redirecting to profile setup...');
        router.replace('/complete-profile');
      } else {
        setStatus(`Welcome! Redirecting to ${profile.role} dashboard...`);
        router.replace(`/dashboard/${profile.role}`);
      }

    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Unknown error occurred.');
      setLoading(false);
    }
  }

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-colors ${isDark ? 'bg-black' : 'bg-white'
      }`}>
      <main className="w-full max-w-md">
        <div className={`rounded-2xl border p-8 ${isDark
          ? 'bg-neutral-900 border-neutral-800'
          : 'bg-white border-gray-200 shadow-sm'
          }`}>
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
              <svg className={`w-7 h-7 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className={`text-2xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Welcome Back
            </h1>
            <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
              Sign in to your account
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label htmlFor="email" className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'
                }`}>
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                placeholder="you@example.com"
                className={`w-full px-4 py-3 rounded-lg border transition-colors outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                  ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                  } disabled:opacity-50`}
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'
                }`}>
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                  placeholder="••••••••"
                  className={`w-full px-4 py-3 rounded-lg border transition-colors outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                    ? 'bg-neutral-800 border-neutral-700 text-white focus:ring-neutral-600'
                    : 'bg-white border-gray-300 text-gray-900 focus:ring-gray-900'
                    } disabled:opacity-50`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute right-3 top-1/2 -translate-y-1/2 ${isDark ? 'text-neutral-500 hover:text-neutral-300' : 'text-gray-400 hover:text-gray-600'
                    }`}
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 ${isDark
                ? 'bg-white text-black hover:bg-neutral-100'
                : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Status */}
          {status && (
            <div className={`mt-4 p-3 rounded-lg text-sm ${status.includes('error') || status.includes('Failed')
              ? isDark
                ? 'bg-red-950/50 text-red-400 border border-red-900'
                : 'bg-red-50 text-red-700 border border-red-200'
              : isDark
                ? 'bg-neutral-800 text-neutral-300 border border-neutral-700'
                : 'bg-gray-50 text-gray-700 border border-gray-200'
              }`}>
              {status}
            </div>
          )}

          {/* Footer */}
          <div className={`mt-6 pt-6 text-center text-sm border-t ${isDark ? 'border-neutral-800 text-neutral-400' : 'border-gray-200 text-gray-600'
            }`}>
            Don't have an account?{' '}
            <Link
              href="/signup"
              className={`font-semibold ${isDark ? 'text-white hover:text-neutral-200' : 'text-gray-900 hover:text-gray-700'
                }`}
            >
              Sign up
            </Link>
          </div>
        </div>
      </main>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');
        
        * {
          font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
      `}</style>
    </div>
  );
}