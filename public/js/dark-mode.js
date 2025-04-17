/**
 * Dark Mode Functionality for LocalLift
 * 
 * This script handles dark mode functionality:
 * - Checks for user preferences in localStorage
 * - Provides a toggle function to switch between modes
 * - Syncs with system preference if user hasn't set a preference
 */

(function() {
  // Variables to store preferences
  const STORAGE_KEY = 'locallift_theme_preference';
  const DARK_THEME = 'dark';
  const LIGHT_THEME = 'light';
  const DEFAULT_THEME = LIGHT_THEME;
  
  // Function to set theme on document
  function setTheme(theme) {
    if (theme === DARK_THEME) {
      document.documentElement.setAttribute('data-theme', DARK_THEME);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    
    // Store the preference
    localStorage.setItem(STORAGE_KEY, theme);
    
    // Update any theme toggle buttons
    updateToggleButtons(theme);
  }
  
  // Function to update toggle buttons to reflect current state
  function updateToggleButtons(theme) {
    const toggleButtons = document.querySelectorAll('.theme-toggle');
    
    toggleButtons.forEach(button => {
      const moonIcon = button.querySelector('.fa-moon');
      const sunIcon = button.querySelector('.fa-sun');
      
      if (theme === DARK_THEME) {
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'inline-block';
        button.setAttribute('title', 'Switch to Light Mode');
        button.setAttribute('aria-label', 'Switch to Light Mode');
      } else {
        if (moonIcon) moonIcon.style.display = 'inline-block';
        if (sunIcon) sunIcon.style.display = 'none';
        button.setAttribute('title', 'Switch to Dark Mode');
        button.setAttribute('aria-label', 'Switch to Dark Mode');
      }
    });
  }
  
  // Function to toggle between light and dark mode
  function toggleTheme() {
    const currentTheme = localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME;
    const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    setTheme(newTheme);
    return newTheme;
  }
  
  // Function to initialize theme based on preference
  function initializeTheme() {
    // Remove initialization class to avoid flash
    document.documentElement.classList.remove('js-dark-mode-init');
    
    // Check localStorage first
    const storedTheme = localStorage.getItem(STORAGE_KEY);
    
    if (storedTheme) {
      // User has a stored preference
      setTheme(storedTheme);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark ? DARK_THEME : LIGHT_THEME);
    }
    
    // Add event listeners to all toggle buttons
    setupEventListeners();
  }
  
  // Function to set up event listeners
  function setupEventListeners() {
    // Add listeners to all toggle buttons
    const toggleButtons = document.querySelectorAll('.theme-toggle');
    
    toggleButtons.forEach(button => {
      button.addEventListener('click', function() {
        toggleTheme();
      });
    });
    
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      // Only change if user hasn't set a preference
      if (!localStorage.getItem(STORAGE_KEY)) {
        setTheme(e.matches ? DARK_THEME : LIGHT_THEME);
      }
    });
  }
  
  // Add theme toggle buttons dynamically to header if they don't exist
  function addThemeToggleButtons() {
    // Check if a toggle button already exists in the header
    const header = document.querySelector('header .container');
    
    if (header && !header.querySelector('.theme-toggle')) {
      // Create toggle button
      const toggleButton = document.createElement('button');
      toggleButton.className = 'theme-toggle';
      toggleButton.setAttribute('title', 'Toggle Dark Mode');
      toggleButton.setAttribute('aria-label', 'Toggle Dark Mode');
      
      // Add icons
      toggleButton.innerHTML = `
        <i class="fas fa-moon"></i>
        <i class="fas fa-sun" style="display: none;"></i>
      `;
      
      // Find a good spot to insert it (before any user menu)
      const userMenu = header.querySelector('.nav-links');
      if (userMenu) {
        userMenu.parentNode.insertBefore(toggleButton, userMenu);
      } else {
        header.appendChild(toggleButton);
      }
    }
  }
  
  // Initialize dark mode system on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', function() {
    console.log('Dark mode system initialized');
    
    // Add toggle buttons if none exist
    addThemeToggleButtons();
    
    // Initialize theme
    initializeTheme();
  });
  
  // Make toggle function available globally
  window.toggleDarkMode = toggleTheme;
})();
