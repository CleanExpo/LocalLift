/**
 * LocalLift Dark Mode Implementation
 * Provides consistent dark mode across all pages with system preference detection
 * and persistent user preference storage.
 */

(function() {
    'use strict';
    
    // Configuration
    const STORAGE_KEY = 'locallift-theme';
    const AUTO_MODE = 'auto';
    const DARK_MODE = 'dark';
    const LIGHT_MODE = 'light';
    const DARK_CLASS = 'dark-mode';
    const THEME_ATTRIBUTE = 'data-theme';
    
    /**
     * Get user's preferred theme from localStorage
     * @returns {string} 'light', 'dark', or 'auto'
     */
    function getUserPreference() {
        return localStorage.getItem(STORAGE_KEY) || AUTO_MODE;
    }
    
    /**
     * Detect if user's system prefers dark mode
     * @returns {boolean} True if system prefers dark mode
     */
    function systemPrefersDark() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    
    /**
     * Set theme attribute on html element and update body classes
     * @param {string} theme - Theme to set ('light' or 'dark')
     */
    function applyTheme(theme) {
        document.documentElement.setAttribute(THEME_ATTRIBUTE, theme);
        
        if (theme === DARK_MODE) {
            document.body.classList.add(DARK_CLASS);
        } else {
            document.body.classList.remove(DARK_CLASS);
        }
        
        // Update all theme toggles
        updateToggles(theme);
        
        // Dispatch event for components that need to know about theme changes
        window.dispatchEvent(new CustomEvent('themechange', { 
            detail: { theme: theme }
        }));
    }
    
    /**
     * Update all theme toggle buttons to match current theme
     * @param {string} theme - Current theme ('light' or 'dark')
     */
    function updateToggles(theme) {
        // Find all toggle buttons
        const toggles = document.querySelectorAll('.theme-toggle');
        
        toggles.forEach(toggle => {
            // Update any theme toggle icons
            const darkIcon = toggle.querySelector('.dark-icon');
            const lightIcon = toggle.querySelector('.light-icon');
            
            if (darkIcon && lightIcon) {
                if (theme === DARK_MODE) {
                    darkIcon.classList.add('hidden');
                    lightIcon.classList.remove('hidden');
                } else {
                    darkIcon.classList.remove('hidden');
                    lightIcon.classList.add('hidden');
                }
            }
            
            // Update any theme toggle checkboxes
            const checkbox = toggle.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = (theme === DARK_MODE);
            }
            
            // Update theme toggle buttons' aria-pressed state
            if (toggle.hasAttribute('aria-pressed')) {
                toggle.setAttribute('aria-pressed', (theme === DARK_MODE).toString());
            }
        });
    }
    
    /**
     * Set theme based on user preference with consideration for system preference
     */
    function setThemePreference() {
        const userPreference = getUserPreference();
        
        if (userPreference === AUTO_MODE) {
            // Follow system preference
            applyTheme(systemPrefersDark() ? DARK_MODE : LIGHT_MODE);
        } else {
            // Use explicit user preference
            applyTheme(userPreference);
        }
    }
    
    /**
     * Save user preference to localStorage
     * @param {string} theme - Theme to save ('light', 'dark', or 'auto')
     */
    function savePreference(theme) {
        localStorage.setItem(STORAGE_KEY, theme);
    }
    
    /**
     * Toggle between light and dark mode
     */
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute(THEME_ATTRIBUTE);
        const newTheme = currentTheme === DARK_MODE ? LIGHT_MODE : DARK_MODE;
        
        // Save explicit preference
        savePreference(newTheme);
        
        // Apply the new theme
        applyTheme(newTheme);
    }
    
    /**
     * Set up theme toggle listeners
     */
    function setupThemeToggleListeners() {
        const toggles = document.querySelectorAll('.theme-toggle');
        
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                toggleTheme();
            });
        });
        
        // Listen for system preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only update if user has set to auto mode
                if (getUserPreference() === AUTO_MODE) {
                    applyTheme(e.matches ? DARK_MODE : LIGHT_MODE);
                }
            });
        }
    }
    
    /**
     * Initialize theme management
     */
    function init() {
        // Create global theme API
        window.LocalLift = window.LocalLift || {};
        window.LocalLift.theme = {
            toggle: toggleTheme,
            setTheme: (theme) => {
                savePreference(theme);
                setThemePreference();
            },
            getCurrentTheme: () => document.documentElement.getAttribute(THEME_ATTRIBUTE),
            isDarkMode: () => document.documentElement.getAttribute(THEME_ATTRIBUTE) === DARK_MODE
        };
        
        // Apply initial theme immediately to avoid flash
        setThemePreference();
        
        // Setup toggle listeners once DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupThemeToggleListeners);
        } else {
            setupThemeToggleListeners();
        }
        
        // Remove initialization class that might be hiding content
        document.documentElement.classList.remove('js-dark-mode-init');
        
        console.log('LocalLift theme system initialized');
    }
    
    // Run initialization immediately to prevent flash of wrong theme
    init();
})();
