/**
 * LocalLift Main JavaScript
 * This file contains common functionality used across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize the application
  initApp();
});

/**
 * Initialize the application
 * Sets up common functionality across all pages
 */
function initApp() {
  // Set up navigation
  setupNavigation();
  
  // Check authentication status
  checkAuthStatus();
  
  // Initialize API connectivity test
  checkAPIConnection();
  
  // Set up any common event listeners
  setupEventListeners();
  
  console.log('LocalLift application initialized');
}

/**
 * Set up navigation and mobile menu functionality
 */
function setupNavigation() {
  // Mobile menu toggle if it exists
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (mobileMenuToggle && navLinks) {
    mobileMenuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('hidden');
      navLinks.classList.toggle('flex');
    });
  }
  
  // Add active class to current navigation item
  highlightCurrentNavItem();
}

/**
 * Highlight the current navigation item based on URL
 */
function highlightCurrentNavItem() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-links a');
  
  navLinks.forEach(link => {
    // Remove any existing active classes
    link.classList.remove('text-primary-600', 'font-semibold');
    
    // Add active class to current page link
    const href = link.getAttribute('href');
    if (href === currentPath || 
        (href !== '/' && currentPath.startsWith(href))) {
      link.classList.add('text-primary-600', 'font-semibold');
    }
  });
}

/**
 * Check user authentication status and update UI accordingly
 */
function checkAuthStatus() {
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  
  if (CONFIG.AUTH && CONFIG.AUTH.TOKEN_KEY) {
    const token = localStorage.getItem(CONFIG.AUTH.TOKEN_KEY);
    const expiry = localStorage.getItem(CONFIG.AUTH.EXPIRY_KEY);
    
    if (token && expiry) {
      const expiryDate = new Date(expiry);
      const now = new Date();
      
      if (expiryDate > now) {
        // User is authenticated
        updateUIForAuthenticatedUser();
        return true;
      } else {
        // Token expired, clear it
        clearAuthData();
      }
    }
  }
  
  // User is not authenticated
  updateUIForUnauthenticatedUser();
  return false;
}

/**
 * Update UI elements for authenticated users
 */
function updateUIForAuthenticatedUser() {
  const authStatusElements = document.querySelectorAll('.auth-status');
  const authenticatedElements = document.querySelectorAll('.authenticated-only');
  const unauthenticatedElements = document.querySelectorAll('.unauthenticated-only');
  
  // Update auth status indicators
  authStatusElements.forEach(el => {
    el.innerHTML = '<i class="fas fa-user-check text-green-500"></i> Signed In';
  });
  
  // Show elements that should only be visible to authenticated users
  authenticatedElements.forEach(el => {
    el.classList.remove('hidden');
  });
  
  // Hide elements that should only be visible to unauthenticated users
  unauthenticatedElements.forEach(el => {
    el.classList.add('hidden');
  });
}

/**
 * Update UI elements for unauthenticated users
 */
function updateUIForUnauthenticatedUser() {
  const authStatusElements = document.querySelectorAll('.auth-status');
  const authenticatedElements = document.querySelectorAll('.authenticated-only');
  const unauthenticatedElements = document.querySelectorAll('.unauthenticated-only');
  
  // Update auth status indicators
  authStatusElements.forEach(el => {
    el.innerHTML = '<i class="fas fa-user text-gray-500"></i> Not Signed In';
  });
  
  // Hide elements that should only be visible to authenticated users
  authenticatedElements.forEach(el => {
    el.classList.add('hidden');
  });
  
  // Show elements that should only be visible to unauthenticated users
  unauthenticatedElements.forEach(el => {
    el.classList.remove('hidden');
  });
}

/**
 * Clear authentication data from local storage
 */
function clearAuthData() {
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  
  if (CONFIG.AUTH) {
    localStorage.removeItem(CONFIG.AUTH.TOKEN_KEY);
    localStorage.removeItem(CONFIG.AUTH.REFRESH_TOKEN_KEY);
    localStorage.removeItem(CONFIG.AUTH.EXPIRY_KEY);
  }
}

/**
 * Check API connection and update status indicators
 */
function checkAPIConnection() {
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  const apiStatusElements = document.querySelectorAll('.api-status');
  
  if (!CONFIG.API_BASE_URL) {
    console.error('API base URL not configured');
    updateAPIStatus(false, 'API not configured');
    return;
  }
  
  // Perform a health check request
  const healthCheckURL = `${CONFIG.API_BASE_URL}${CONFIG.HEALTH_CHECK_ENDPOINT || '/api/health'}`;
  
  fetch(healthCheckURL, {
    method: 'GET',
    headers: {
      'Accept': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`API health check failed with status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Health check successful
    updateAPIStatus(true, data.status || 'Connected');
  })
  .catch(error => {
    console.error('API health check failed:', error);
    updateAPIStatus(false, 'Connection failed');
  });
}

/**
 * Update API status indicators in the UI
 */
function updateAPIStatus(isConnected, statusText) {
  const apiStatusElements = document.querySelectorAll('.api-status');
  
  apiStatusElements.forEach(el => {
    if (isConnected) {
      el.innerHTML = `<i class="fas fa-circle text-green-500"></i> API: ${statusText}`;
      el.classList.remove('text-red-500');
      el.classList.add('text-green-500');
    } else {
      el.innerHTML = `<i class="fas fa-exclamation-circle text-red-500"></i> API: ${statusText}`;
      el.classList.remove('text-green-500');
      el.classList.add('text-red-500');
    }
  });
}

/**
 * Set up common event listeners
 */
function setupEventListeners() {
  // Logout buttons
  const logoutButtons = document.querySelectorAll('.logout-button');
  logoutButtons.forEach(button => {
    button.addEventListener('click', handleLogout);
  });
  
  // Add other common event listeners here
}

/**
 * Handle user logout
 */
function handleLogout(event) {
  event.preventDefault();
  
  // Clear authentication data
  clearAuthData();
  
  // Update UI
  updateUIForUnauthenticatedUser();
  
  // Redirect to home page
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  window.location.href = CONFIG.ROUTES?.HOME || '/';
}

/**
 * Get authentication token
 * @returns {string|null} The authentication token or null if not logged in
 */
function getAuthToken() {
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  
  if (CONFIG.AUTH && CONFIG.AUTH.TOKEN_KEY) {
    return localStorage.getItem(CONFIG.AUTH.TOKEN_KEY);
  }
  
  return null;
}

/**
 * Make an authenticated API request
 * @param {string} endpoint - The API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} The fetch promise
 */
function apiRequest(endpoint, options = {}) {
  const CONFIG = window.LOCALLIFT_CONFIG || {};
  
  if (!CONFIG.API_BASE_URL) {
    return Promise.reject(new Error('API base URL not configured'));
  }
  
  const url = `${CONFIG.API_BASE_URL}${endpoint}`;
  
  // Set up headers
  const headers = options.headers || {};
  headers['Accept'] = 'application/json';
  
  // Add authentication token if available
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Update options with headers
  options.headers = headers;
  
  return fetch(url, options)
    .then(response => {
      if (!response.ok) {
        // Handle 401 Unauthorized by clearing auth data
        if (response.status === 401) {
          clearAuthData();
          updateUIForUnauthenticatedUser();
        }
        
        return response.json().then(data => {
          throw new Error(data.message || `API request failed with status: ${response.status}`);
        });
      }
      
      return response.json();
    });
}
