'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import supabase from '../../lib/supabaseClient';

export default function ResetVerifyPage() {
  const search = useSearchParams();
  const router = useRouter();
  const emailFromQuery = search.get('email') ?? '';
  const [email, setEmail] = useState(emailFromQuery);
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (emailFromQuery) setEmail(emailFromQuery);
  }, [emailFromQuery]);

  async function handleVerifyAndReset(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return setStatus('Email is required');
    if (!code) return setStatus('Enter the code from email');
    if (!newPassword) return setStatus('Enter a new password');
    setStatus(null);
    setLoading(true);

    try {
      // verify OTP with type 'recovery'
      const { error: verifyErr } = await supabase.auth.verifyOtp({
        email,
        token: code.trim(),
        type: 'recovery',
      });

      if (verifyErr) {
        throw verifyErr;
      }

      // after verify success the SDK will have an authenticated session
      // update password for the current session
      const { error: updateErr } = await supabase.auth.updateUser({ password: newPassword });

      if (updateErr) {
        throw updateErr;
      }

      setStatus('Password updated. Redirecting to dashboard...');
      // small delay so user sees the status
      setTimeout(() => router.push('/dashboard'), 800);
    } catch (err: any) {
      setStatus(err?.message ?? 'Failed to verify or update password');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 640, margin: '40px auto', padding: 20 }}>
      <h1>Enter reset code and new password</h1>

      <form onSubmit={handleVerifyAndReset} style={{ display: 'grid', gap: 12 }}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value.trim())}
            required
            style={{ width: '100%', padding: 8 }}
            disabled={loading}
            autoComplete="email"
          />
        </label>

        <label>
          Code
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
            disabled={loading}
          />
        </label>

        <label>
          New password
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
            disabled={loading}
            autoComplete="new-password"
          />
        </label>

        <button type="submit" disabled={loading || !email || !code || !newPassword} style={{ padding: 10 }}>
          {loading ? 'Updating...' : 'Verify and set password'}
        </button>
      </form>

      {status && <p style={{ marginTop: 12 }}>{status}</p>}
    </main>
  );
}
