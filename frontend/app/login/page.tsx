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
  const [stage, setStage] = useState<'credentials' | 'code' | 'done'>('credentials');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [code, setCode] = useState('');
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

  async function handleSubmitCredentials(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setStatus(null);
    setLoading(true);

    try {
      // 1. Verify Password First
      const { error: signErr } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signErr) {
        setStatus(`Sign-in error: ${signErr.message}`);
        setLoading(false);
        return;
      }

      // 2. If Password OK, Sign Out immediately to force OTP flow
      await supabase.auth.signOut();

      // 3. Request OTP
      const { error: otpErr } = await supabase.auth.signInWithOtp({ email });
      if (otpErr) {
        setStatus(`Failed to request OTP: ${otpErr.message}`);
        setLoading(false);
        return;
      }

      setStage('code');
      setStatus('OTP sent. Check your email.');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Unknown error occurred.');
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyCode(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setStatus(null);
    setLoading(true);

    try {
      // 1. Verify the OTP code
      // Note: Use 'email' type for standard 6-digit codes in newer Supabase versions
      const { data: authData, error: verifyError } = await supabase.auth.verifyOtp({
        email,
        token: code.trim(),
        type: 'email',
      });

      if (verifyError) {
        throw new Error(verifyError.message);
      }

      if (!authData.user) {
        throw new Error('Verification successful, but user not found.');
      }

      setStatus('Verified. Checking profile...');

      // 2. Fetch User Profile to get Role
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('role')
        .eq('id', authData.user.id)
        .single();

      // Switch to 'done' state immediately to show loading UI
      setStage('done');

      // 3. Handle Missing Profile (New User) vs Existing User
      if (profileError || !profile) {
        // New user or error fetching profile -> Go to Complete Profile
        setStatus('New account detected. Redirecting to profile setup...');
        router.replace('/complete-profile');
      } else {
        // Existing user -> Go to Dashboard
        setStatus(`Welcome! Redirecting to ${profile.role} dashboard...`);
        router.replace(`/dashboard/${profile.role}`);
      }

    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Verification failed.');
      setLoading(false);
      // Stay on code stage if verification fails
      if (stage !== 'done') setStage('code');
    }
  }

  async function handleResend() {
    if (loading) return;
    setLoading(true);
    setStatus(null);
    try {
      const { error } = await supabase.auth.signInWithOtp({ email });
      if (error) {
        throw error;
      }
      setCode('');
      setStatus('OTP resent. Check email.');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Failed to resend OTP.');
    } finally {
      setLoading(false);
    }
  }

  function handleCancel() {
    setStage('credentials');
    setStatus(null);
    setCode('');
    setLoading(false);
  }

  // --- RENDER HELPERS ---

  // 1. DONE STATE (Redirecting...)
  if (stage === 'done') {
    return (
      <div className={`min-h-screen flex items-center justify-center p-4 transition-colors ${isDark ? 'bg-black' : 'bg-white'}`}>
        <main className="w-full max-w-md text-center">
          <div className={`rounded-2xl border p-12 ${isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200 shadow-sm'}`}>
            <div className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-6 ${isDark ? 'border-white' : 'border-gray-900'}`}></div>
            <h2 className={`text-xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Logging you in...
            </h2>
            <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
              {status || 'Please wait while we redirect you.'}
            </p>
          </div>
        </main>
        <style jsx global>{`@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap'); * { font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }`}</style>
      </div>
    );
  }

  // 2. CREDENTIALS STATE (Email/Pass)
  if (stage === 'credentials') {
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
            <form onSubmit={handleSubmitCredentials} className="space-y-4">
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

              {/* Forgot Password */}
              <div className="flex justify-end">
                <Link
                  href="/reset-request"
                  className={`text-sm font-medium ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  Forgot password?
                </Link>
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
                {loading ? 'Checking...' : 'Continue'}
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

  // 3. CODE VERIFICATION STATE
  if (stage === 'code') {
    return (
      <div className={`min-h-screen flex items-center justify-center p-4 transition-colors ${isDark ? 'bg-black' : 'bg-white'
        }`}>
        <main className="w-full max-w-md">
          <div className={`rounded-2xl border p-8 ${isDark
            ? 'bg-neutral-900 border-neutral-800'
            : 'bg-white border-gray-200 shadow-sm'
            }`}>
            {/* Icon */}
            <div className="flex justify-center mb-8">
              <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${isDark ? 'bg-neutral-800' : 'bg-gray-100'
                }`}>
                <svg className={`w-7 h-7 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>

            {/* Header */}
            <div className="text-center mb-8">
              <h1 className={`text-2xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Check your email
              </h1>
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                We sent a code to
              </p>
              <p className={`font-medium mt-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>{email}</p>
            </div>

            {/* Form */}
            <form onSubmit={handleVerifyCode} className="space-y-4">
              <div>
                <label htmlFor="code" className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'
                  }`}>
                  Verification code
                </label>
                <input
                  id="code"
                  value={code}
                  onChange={(e) => setCode(e.target.value.trim())}
                  required
                  disabled={loading}
                  placeholder="Enter code"
                  className={`w-full px-4 py-3 rounded-lg border transition-colors outline-none focus:ring-2 focus:ring-offset-0 text-center ${isDark
                    ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                    } disabled:opacity-50`}
                />
              </div>

              <button
                type="submit"
                disabled={loading || !code.trim()}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 ${isDark
                  ? 'bg-white text-black hover:bg-neutral-100'
                  : 'bg-gray-900 text-white hover:bg-gray-800'
                  }`}
              >
                {loading ? 'Verifying...' : 'Verify'}
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

            {/* Resend/Cancel */}
            <div className="mt-6 text-center space-y-3">
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                Didn't receive it?
              </p>
              <div className="flex gap-3 justify-center text-sm">
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={loading}
                  className={`font-medium disabled:opacity-50 ${isDark ? 'text-white hover:text-neutral-300' : 'text-gray-900 hover:text-gray-700'
                    }`}
                >
                  Resend code
                </button>
                <span className={isDark ? 'text-neutral-700' : 'text-gray-300'}>•</span>
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={loading}
                  className={`font-medium disabled:opacity-50 ${isDark ? 'text-neutral-400 hover:text-neutral-300' : 'text-gray-600 hover:text-gray-700'
                    }`}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </main>
        <style jsx global>{`@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap'); * { font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }`}</style>
      </div>
    );
  }

  // Fallback
  return null;
}