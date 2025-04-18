/**
 * LocalLift Configuration
 * This file contains configuration settings for the LocalLift application
 * It is used by all frontend components to connect to the backend API
 */

window.LOCALLIFT_CONFIG = {
  // Updated API base URL to point to the correct backend endpoint
  API_BASE_URL: 'https://locallift-production.up.railway.app',

  // Version information
  VERSION: '1.0.0',

  // Feature flags
  FEATURES: {
    GAMIFICATION: true,
    ACHIEVEMENTS: true,
    LEADERBOARDS: true,
    CERTIFICATIONS: true
  },

  // Authentication configuration
  AUTH: {
    TOKEN_KEY: 'locallift_auth_token',
    REFRESH_TOKEN_KEY: 'locallift_refresh_token',
    EXPIRY_KEY: 'locallift_token_expiry',
    SESSION_DURATION: 86400 // 24 hours in seconds
  },

  // Environment - will be 'production' for deployed app
  ENVIRONMENT: 'production',

  // Default health check endpoint
  HEALTH_CHECK_ENDPOINT: '/api/health',

  // Routes configuration
  ROUTES: {
    HOME: '/',
    DASHBOARD: '/dashboard',
    LOGIN: '/login',
    GUIDE: '/admin/guide',
    PROFILE: '/profile',
    SETTINGS: '/settings'
  },

  // Default error page
  ERROR_PAGE: '/404.html',
  
  // Supabase configuration
  SUPABASE: {
    PROJECT_ID: 'rsooolwhapkkkwbmybdb',
    API_URL: 'https://rsooolwhapkkkwbmybdb.supabase.co'
  }
};
