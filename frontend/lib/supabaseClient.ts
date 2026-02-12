// frontend/lib/supabaseClient.ts

import { createBrowserClient } from '@supabase/ssr';

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!url || !anonKey) {
  throw new Error('Missing Supabase environment variables');
}

// Create a singleton instance for the browser
const supabase = createBrowserClient(url, anonKey);

export default supabase;