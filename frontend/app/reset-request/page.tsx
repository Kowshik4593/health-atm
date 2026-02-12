'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import supabase from '../../lib/supabaseClient';

export default function ResetRequestPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleRequest(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return setStatus('Enter an email');
    setStatus(null);
    setLoading(true);

    try {
      // prefer resetPasswordForEmail if present in this SDK version
      // many versions expect a string argument: resetPasswordForEmail(email)
      // fallback to signInWithOtp({ email }) if not available
      // @ts-ignore
      const hasResetFn = typeof (supabase.auth as any).resetPasswordForEmail === 'function';

      if (hasResetFn) {
        // PASS A STRING (not an object)
        // @ts-ignore
        const { error } = await (supabase.auth as any).resetPasswordForEmail(email);
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signInWithOtp({ email });
        if (error) throw error;
      }

      setStatus('Reset code sent. Check your email.');
      router.push(`/reset-verify?email=${encodeURIComponent(email)}`);
    } catch (err: any) {
      setStatus(err?.message ?? 'Error requesting reset');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 640, margin: '40px auto', padding: 20 }}>
      <h1>Reset password</h1>

      <form onSubmit={handleRequest} style={{ display: 'grid', gap: 12 }}>
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

        <button type="submit" disabled={loading || !email} style={{ padding: 10 }}>
          {loading ? 'Sending...' : 'Send reset code'}
        </button>
      </form>

      {status && <p style={{ marginTop: 12 }}>{status}</p>}
    </main>
  );
}
