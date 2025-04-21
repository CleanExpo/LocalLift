/**
 * LocalLift Authentication Module
 * Handles authentication, authorization and role-based access control
 */

// Auth state
let currentUser = null;
let userRole = null;
let userPermissions = [];

// Cached JWT token
let authToken = localStorage.getItem('auth_token');
let tokenExpiry = localStorage.getItem('token_expiry');

// Authentication endpoints
const AUTH_API = {
  BASE_URL: window.config?.API_BASE_URL || 'https://humorous-serenity-locallift.up.railway.app/api',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
  ME: '/users/me'
};

// Debug message to help troubleshoot
console.log('Auth module initialized with API URL:', AUTH_API.BASE_URL);

/**
 * Initialize the authentication system
 * Checks for existing session and sets up auth state
 */
async function initAuth() {
  console.log('Initializing authentication...');
  
  // Check if we have a valid token
  if (authToken && tokenExpiry && new Date(tokenExpiry) > new Date()) {
    try {
      // Validate the token with the server
      await validateToken();
      console.log('Existing session restored');
    } catch (error) {
      console.error('Token validation failed:', error);
      clearAuthState();
    }
  } else if (authToken) {
    // Token expired, try to refresh
    try {
      await refreshToken();
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuthState();
    }
  }

  // Update UI based on auth state
  updateAuthUI();
}

/**
 * Login with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Resolves with user data or rejects with error
 */
async function login(email, password) {
  try {
    const response = await fetch(`${AUTH_API.BASE_URL}${AUTH_API.LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    const data = await response.json();
    
    // Store token and user data
    setAuthData(data);
    
    // Update UI
    updateAuthUI();
    
    return data.user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Register a new user
 * @param {object} userData - User registration data
 * @returns {Promise} - Resolves with user data or rejects with error
 */
async function register(userData) {
  try {
    const response = await fetch(`${AUTH_API.BASE_URL}${AUTH_API.REGISTER}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }

    const data = await response.json();
    
    // Store token and user data
    setAuthData(data);
    
    // Update UI
    updateAuthUI();
    
    return data.user;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

/**
 * Refresh the authentication token
 * @returns {Promise} - Resolves with new token or rejects with error
 */
async function refreshToken() {
  try {
    const response = await fetch(`${AUTH_API.BASE_URL}${AUTH_API.REFRESH}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    
    // Update token data
    authToken = data.token;
    tokenExpiry = new Date(Date.now() + data.expiresIn * 1000).toISOString();
    
    // Save to local storage
    localStorage.setItem('auth_token', authToken);
    localStorage.setItem('token_expiry', tokenExpiry);
    
    return authToken;
  } catch (error) {
    console.error('Token refresh error:', error);
    clearAuthState();
    throw error;
  }
}

/**
 * Logout the current user
 * @returns {Promise} - Resolves when logout is complete
 */
async function logout() {
  try {
    // Only call the logout API if we have a token
    if (authToken) {
      await fetch(`${AUTH_API.BASE_URL}${AUTH_API.LOGOUT}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear auth state regardless of API success
    clearAuthState();
    
    // Update UI
    updateAuthUI();
    
    // Redirect to login page
    window.location.href = '/login/';
  }
}

/**
 * Validate the current token and get user data
 * @returns {Promise} - Resolves with user data or rejects with error
 */
async function validateToken() {
  try {
    const response = await fetch(`${AUTH_API.BASE_URL}${AUTH_API.ME}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Invalid token');
    }

    const userData = await response.json();
    
    // Update user state
    currentUser = userData;
    userRole = userData.role || 'user';
    
    // Load permissions based on role
    await loadUserPermissions();
    
    return userData;
  } catch (error) {
    console.error('Token validation error:', error);
    clearAuthState();
    throw error;
  }
}

/**
 * Load user permissions based on role
 * @returns {Promise} - Resolves when permissions are loaded
 */
async function loadUserPermissions() {
  // Define role-based permissions
  const rolePermissions = {
    'user': ['view_dashboard', 'edit_profile', 'view_learning'],
    'staff': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports'],
    'manager': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users'],
    'admin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs'],
    'superadmin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs']
  };
  
  // Set permissions based on role
  userPermissions = rolePermissions[userRole] || [];
}

/**
 * Check if user has a specific permission
 * @param {string} permission - The permission to check
 * @returns {boolean} - True if user has permission, false otherwise
 */
function hasPermission(permission) {
  return userPermissions.includes(permission);
}

/**
 * Set authentication data after successful login/register
 * @param {object} data - Authentication data from server
 */
function setAuthData(data) {
  // Store token
  authToken = data.token;
  tokenExpiry = new Date(Date.now() + data.expiresIn * 1000).toISOString();
  
  // Save to local storage
  localStorage.setItem('auth_token', authToken);
  localStorage.setItem('token_expiry', tokenExpiry);
  
  // Store user data
  currentUser = data.user;
  userRole = data.user.role || 'user';
  
  // Load permissions
  loadUserPermissions();
}

/**
 * Clear authentication state on logout or error
 */
function clearAuthState() {
  // Clear memory state
  authToken = null;
  tokenExpiry = null;
  currentUser = null;
  userRole = null;
  userPermissions = [];
  
  // Clear local storage
  localStorage.removeItem('auth_token');
  localStorage.removeItem('token_expiry');
}

/**
 * Update UI elements based on authentication state
 */
function updateAuthUI() {
  // Get auth-related elements
  const authLinks = document.querySelectorAll('[data-auth-link]');
  const userProfileElements = document.querySelectorAll('[data-user-profile]');
  const roleBasedElements = document.querySelectorAll('[data-requires-role]');
  const permissionBasedElements = document.querySelectorAll('[data-requires-permission]');
  
  // Update authentication links
  authLinks.forEach(link => {
    const authState = link.getAttribute('data-auth-link');
    
    if (authState === 'logged-in' && currentUser) {
      link.style.display = '';
    } else if (authState === 'logged-out' && !currentUser) {
      link.style.display = '';
    } else {
      link.style.display = 'none';
    }
  });
  
  // Update user profile elements
  if (currentUser) {
    userProfileElements.forEach(element => {
      const field = element.getAttribute('data-user-profile');
      
      if (field === 'name') {
        element.textContent = currentUser.name || currentUser.email;
      } else if (field === 'email') {
        element.textContent = currentUser.email;
      } else if (field === 'role') {
        element.textContent = userRole.charAt(0).toUpperCase() + userRole.slice(1);
      } else if (field === 'avatar' && element.tagName === 'IMG') {
        element.src = currentUser.avatar_url || '/images/default-avatar.png';
        element.alt = currentUser.name || 'User Avatar';
      }
    });
  }
  
  // Update role-based elements
  roleBasedElements.forEach(element => {
    const requiredRole = element.getAttribute('data-requires-role');
    const roleHierarchy = ['user', 'staff', 'manager', 'admin', 'superadmin'];
    
    const requiredRoleIndex = roleHierarchy.indexOf(requiredRole);
    const userRoleIndex = roleHierarchy.indexOf(userRole);
    
    if (userRoleIndex >= requiredRoleIndex && userRoleIndex !== -1) {
      element.style.display = '';
    } else {
      element.style.display = 'none';
    }
  });
  
  // Update permission-based elements
  permissionBasedElements.forEach(element => {
    const requiredPermission = element.getAttribute('data-requires-permission');
    
    if (hasPermission(requiredPermission)) {
      element.style.display = '';
    } else {
      element.style.display = 'none';
    }
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initAuth);

// Expose API
window.auth = {
  login,
  register,
  logout,
  hasPermission,
  getCurrentUser: () => currentUser,
  getUserRole: () => userRole,
  isAuthenticated: () => !!currentUser
};
