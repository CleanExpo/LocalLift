/**
 * LocalLift Frontend Configuration
 *
 * This file contains configuration settings for the LocalLift frontend application.
 * It specifies API endpoints and other important settings for the application.
 */

// API endpoint configuration
const CONFIG = {
  // Base URL for API requests (default points to Railway deployment)
  API_BASE_URL: "https://locallift-production.up.railway.app",
  
  // API version
  API_VERSION: "v1",
  
  // Full API URL with version
  get API_URL() {
    return `${this.API_BASE_URL}/api/${this.API_VERSION}`;
  },
  
  // Health check endpoint
  get HEALTH_CHECK_URL() {
    return `${this.API_BASE_URL}/api/health`;
  },
  
  // Authentication settings
  AUTH: {
    TOKEN_KEY: "locallift_auth_token",
    REFRESH_TOKEN_KEY: "locallift_refresh_token",
    EXPIRY_KEY: "locallift_token_expiry",
    SESSION_DURATION: 3600 * 24 // 24 hours in seconds
  },
  
  // Feature flags
  FEATURES: {
    ENABLE_NOTIFICATIONS: true,
    ENABLE_ANALYTICS: true,
    DARK_MODE: true
  }
};

// Export the configuration for use in other modules
window.LOCALLIFT_CONFIG = CONFIG;
