import { createClient } from '@supabase/supabase-js'

// Initialize the Supabase browser client using environment variables that
// should already be configured in Vercel / Render settings (or a local .env).
// NEXT_PUBLIC_-prefixed variables are exposed to the browser by Next.js.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  // eslint-disable-next-line no-console
  console.warn('Supabase credentials are missing. Make sure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are defined in your environment.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey) 