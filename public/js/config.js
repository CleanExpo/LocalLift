// Configuration for LocalLift
const API_CONFIG = {
  baseUrl: "https://humorous-serenity-locallift.up.railway.app",
  apiVersion: "v1",
  timeout: 10000
};

// Expose config globally for other scripts
window.config = {
  API_BASE_URL: API_CONFIG.baseUrl + '/api',
  API_VERSION: API_CONFIG.apiVersion,
  API_TIMEOUT: API_CONFIG.timeout
};

// API status check function - now makes a real request
async function checkApiStatus() {
  console.log("Checking API status at: " + API_CONFIG.baseUrl);
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      timeout: API_CONFIG.timeout
    });
    
    if (response.ok) {
      console.log("API is operational");
      return true;
    } else {
      console.error("API returned status:", response.status);
      return false;
    }
  } catch (error) {
    console.error("API connection error:", error);
    return false;
  }
}

// Auto-check API status on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log("Config loaded - using API at:", window.config.API_BASE_URL);
  checkApiStatus().then(result => {
    console.log("API connection check:", result ? "Success" : "Failed");
  });
});
