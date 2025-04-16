/**
 * API Configuration
 * 
 * This file centralizes API endpoint configuration for the LocalLift frontend.
 * It automatically detects whether we're in a production or development environment
 * and sets the appropriate base URL for API calls.
 */

const CONFIG = {
  // Production API URL (Railway deployment)
  PRODUCTION_API_URL: "https://local-lift-production.up.railway.app",
  
  // Local development API URL
  DEVELOPMENT_API_URL: "http://localhost:8000",
  
  // Determine if we're in production based on the hostname
  isProduction() {
    return window.location.hostname.includes('vercel.app') || 
           !window.location.hostname.includes('localhost');
  },
  
  // Get the appropriate API base URL
  getApiBaseUrl() {
    return this.isProduction() ? this.PRODUCTION_API_URL : this.DEVELOPMENT_API_URL;
  }
};

// Export the API base URL for use in other JS files
const apiBase = CONFIG.getApiBaseUrl();
