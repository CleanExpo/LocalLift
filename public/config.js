/**
 * LocalLift Frontend Configuration
 * This file provides configuration settings for the LocalLift frontend
 * with robust error handling and connection recovery.
 */

// API configuration with connection resilience
const API_CONFIG = {
  // Primary API URL
  BASE_URL: "https://locallift-production.up.railway.app",
  // Fallback URL if primary is unreachable
  FALLBACK_URL: "https://locallift-backup.up.railway.app",
  // Current API version
  API_VERSION: "v1",
  // Connection timeout in milliseconds
  TIMEOUT: 10000,
  // Maximum number of retries for failed API calls
  MAX_RETRIES: 3,
  // Whether the system is in maintenance mode
  MAINTENANCE_MODE: false,
  // Connection status
  _connectionStatus: "unknown",
  
  // Full API endpoint
  get ENDPOINT() {
    return `${this.BASE_URL}/api/${this.API_VERSION}`;
  },
  
  // Health check endpoint
  get HEALTH_CHECK_URL() {
    return `${this.BASE_URL}/api/health`;
  },
  
  // Fallback API endpoint
  get FALLBACK_ENDPOINT() {
    return `${this.FALLBACK_URL}/api/${this.API_VERSION}`;
  },
  
  // Get current connection status
  get connectionStatus() {
    return this._connectionStatus;
  },
  
  // Update connection status
  set connectionStatus(status) {
    this._connectionStatus = status;
    console.log(`API Connection Status: ${status}`);
    // Dispatch event for UI components to react
    const event = new CustomEvent('api-connection-change', { detail: status });
    window.dispatchEvent(event);
  },
  
  // Check API health and update status
  checkHealth: async function() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.TIMEOUT);
      
      const response = await fetch(this.HEALTH_CHECK_URL, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        this.connectionStatus = "connected";
        return true;
      } else {
        this.connectionStatus = "error";
        return false;
      }
    } catch (error) {
      this.connectionStatus = error.name === 'AbortError' ? "timeout" : "disconnected";
      console.error("API Health Check Failed:", error);
      return false;
    }
  },
  
  // Switch to fallback URL if primary fails
  useFallback: function() {
    const temp = this.BASE_URL;
    this.BASE_URL = this.FALLBACK_URL;
    this.FALLBACK_URL = temp;
    console.log(`Switched to fallback API URL: ${this.BASE_URL}`);
    return this.ENDPOINT;
  },
  
  // Initialize the configuration
  init: async function() {
    console.log("Initializing LocalLift API configuration...");
    await this.checkHealth();
    
    // Set up periodic health checks
    setInterval(() => this.checkHealth(), 60000); // Check every minute
    
    return this;
  }
};

// Export the configuration
window.LOCALLIFT_API = API_CONFIG;

// Initialize when the DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
  API_CONFIG.init().then(() => {
    console.log("LocalLift API configuration initialized");
  });
});

// Handle connection errors
window.addEventListener('api-connection-change', (event) => {
  const status = event.detail;
  const statusIndicator = document.getElementById('api-status-indicator');
  
  if (statusIndicator) {
    statusIndicator.className = `status-indicator status-${status}`;
    statusIndicator.setAttribute('title', `API Status: ${status}`);
  }
  
  // Show toast notification for connection changes
  if (status === 'error' || status === 'disconnected') {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = 'Connection to server lost. Retrying...';
    document.body.appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
      toast.remove();
    }, 5000);
  }
});
