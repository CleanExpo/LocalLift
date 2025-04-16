/**
 * LocalLift Frontend Configuration
 * This file provides configuration settings for the LocalLift frontend
 */

// API configuration
const API_CONFIG = {
  BASE_URL: "https://locallift-production.up.railway.app",
  API_VERSION: "v1",
  
  // Full API endpoint
  get ENDPOINT() {
    return `${this.BASE_URL}/api/${this.API_VERSION}`;
  },
  
  // Health check endpoint
  get HEALTH_CHECK_URL() {
    return `${this.BASE_URL}/api/health`;
  }
};

// Export the configuration
window.LOCALLIFT_API = API_CONFIG;
