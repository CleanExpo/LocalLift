/**
 * Supabase Client Configuration
 *
 * This file initializes the Supabase client for browser-side access.
 * It establishes a connection to the Supabase backend using the project URL
 * and API key which should be set in environment variables.
 */

// Import from CDN for direct browser usage without a build step
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// Supabase project configuration
export const SUPABASE_URL = 'https://rsooolwhapkkkwbmybdb.supabase.co'
export const SUPABASE_PROJECT_ID = 'rsooolwhapkkkwbmybdb'

// The API key should be set in environment variables
// In production this will come from Railway environment variables
// In development it should be in .env file or injected by the server
const supabaseAnonKey = process.env.SUPABASE_KEY ||
                        window.SUPABASE_KEY ||
                        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MDg1NDYsImV4cCI6MjA2MDI4NDU0Nn0.hKGvTKiT0c8270__roY4C66P5haZuXwBpbRSvmpYa34'

// Client options with better defaults for web applications
const supabaseOptions = {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
}

// Initialize the Supabase client
const supabase = createClient(SUPABASE_URL, supabaseAnonKey, supabaseOptions)

// Export the initialized client as the default export
export default supabase

// Auth utility functions
export const auth = {
  /**
   * Sign up a new user
   * @param {string} email - User's email
   * @param {string} password - User's password
   * @param {Object} metadata - Optional user metadata
   * @returns {Promise} - Auth response
   */
  signUp: async (email, password, metadata = {}) => {
    return await supabase.auth.signUp({
      email,
      password,
      options: { data: metadata }
    })
  },

  /**
   * Sign in with email and password
   * @param {string} email - User's email
   * @param {string} password - User's password
   * @returns {Promise} - Auth response
   */
  signIn: async (email, password) => {
    return await supabase.auth.signInWithPassword({
      email,
      password
    })
  },

  /**
   * Sign out the current user
   * @returns {Promise} - Auth response
   */
  signOut: async () => {
    return await supabase.auth.signOut()
  },

  /**
   * Get the current user session
   * @returns {Object|null} - User session or null
   */
  getSession: async () => {
    const { data } = await supabase.auth.getSession()
    return data.session
  },

  /**
   * Get the current user
   * @returns {Object|null} - User object or null
   */
  getUser: async () => {
    const { data } = await supabase.auth.getUser()
    return data.user
  }
}

// Database utility functions
export const db = {
  /**
   * Fetch data from a table
   * @param {string} table - Table name
   * @param {Object} options - Query options (filters, order, limit, etc.)
   * @returns {Promise} - Query response
   */
  fetch: async (table, options = {}) => {
    let query = supabase.from(table).select(options.columns || '*')

    if (options.filters) {
      Object.entries(options.filters).forEach(([field, value]) => {
        query = query.eq(field, value)
      })
    }

    if (options.order) {
      Object.entries(options.order).forEach(([column, direction]) => {
        query = query.order(column, { ascending: direction === 'asc' })
      })
    }

    if (options.limit) {
      query = query.limit(options.limit)
    }

    if (options.offset) {
      query = query.range(options.offset, options.offset + (options.limit || 10) - 1)
    }

    return await query
  },

  /**
   * Insert data into a table
   * @param {string} table - Table name
   * @param {Object|Array} data - Data to insert
   * @returns {Promise} - Insert response
   */
  insert: async (table, data) => {
    return await supabase.from(table).insert(data)
  },

  /**
   * Update data in a table
   * @param {string} table - Table name
   * @param {Object} data - Data to update
   * @param {Object} filters - Filters to match records
   * @returns {Promise} - Update response
   */
  update: async (table, data, filters = {}) => {
    let query = supabase.from(table).update(data)

    Object.entries(filters).forEach(([field, value]) => {
      query = query.eq(field, value)
    })

    return await query
  },

  /**
   * Delete data from a table
   * @param {string} table - Table name
   * @param {Object} filters - Filters to match records
   * @returns {Promise} - Delete response
   */
  delete: async (table, filters = {}) => {
    let query = supabase.from(table).delete()

    Object.entries(filters).forEach(([field, value]) => {
      query = query.eq(field, value)
    })

    return await query
  }
}

// File storage utility functions
export const storage = {
  /**
   * Upload a file to storage
   * @param {string} bucket - Storage bucket
   * @param {string} path - File path
   * @param {File} file - File to upload
   * @param {Object} options - Upload options
   * @returns {Promise} - Upload response
   */
  upload: async (bucket, path, file, options = {}) => {
    return await supabase.storage.from(bucket).upload(path, file, options)
  },

  /**
   * Get a public URL for a file
   * @param {string} bucket - Storage bucket
   * @param {string} path - File path
   * @returns {string} - Public URL
   */
  getPublicUrl: (bucket, path) => {
    return supabase.storage.from(bucket).getPublicUrl(path).data.publicUrl
  },

  /**
   * Download a file
   * @param {string} bucket - Storage bucket
   * @param {string} path - File path
   * @returns {Promise} - Download response
   */
  download: async (bucket, path) => {
    return await supabase.storage.from(bucket).download(path)
  },

  /**
   * Delete one or more files
   * @param {string} bucket - Storage bucket
   * @param {string|Array} paths - File path or array of paths
   * @returns {Promise} - Delete response
   */
  delete: async (bucket, paths) => {
    return await supabase.storage.from(bucket).remove(
      Array.isArray(paths) ? paths : [paths]
    )
  }
}
