/**
 * Supabase Client Configuration
 * 
 * This file initializes the Supabase client for browser-side access.
 * It establishes a connection to the Supabase backend using the project URL
 * and API key, which should be set in environment variables.
 */

import { createClient } from '@supabase/supabase-js'

// Supabase project URL
const supabaseUrl = 'https://rsooolwhapkkkwbmybdb.supabase.co'

// The API key should be set in environment variables
// In production, this will come from Railway environment variables
// In development, it should be in .env file
const supabaseKey = process.env.SUPABASE_KEY || window.SUPABASE_KEY

// Initialize the Supabase client
const supabase = createClient(supabaseUrl, supabaseKey)

export default supabase
