/**
 * LocalLift Main JavaScript Handler
 * This file coordinates module initialization and dependency loading
 */

(function() {
    'use strict';

    // Configuration
    const REQUIRED_MODULES = [
        // Core utilities
        '/js/dark-mode.js',
        '/js/responsive-utils.js',
        '/js/tab-handler.js',
        '/js/dropdown-handler.js'
    ];

    // Optional modules based on page
    const PAGE_SPECIFIC_MODULES = {
        '/dashboard': [
            '/js/dashboard.js'
        ],
        '/profile': [
            '/js/profile.js'
        ],
        '/login': [
            '/js/login.js'
        ],
        '/settings': [
            '/js/settings.js'
        ]
    };

    /**
     * Check which page-specific modules to load
     */
    function determinePageModules() {
        const path = window.location.pathname;
        const modules = [];

        // Check if current path matches any page-specific modules
        for (const pagePath in PAGE_SPECIFIC_MODULES) {
            if (path === pagePath || path.startsWith(pagePath + '/')) {
                modules.push(...PAGE_SPECIFIC_MODULES[pagePath]);
            }
        }

        return modules;
    }

    /**
     * Dynamically load a JavaScript file
     * @param {string} src - Path to JavaScript file
     * @returns {Promise} - Promise that resolves when file is loaded
     */
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            // Skip if already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.async = true;

            script.onload = () => resolve();
            script.onerror = () => {
                console.error(`Failed to load script: ${src}`);
                reject(new Error(`Failed to load script: ${src}`));
            };

            document.head.appendChild(script);
        });
    }

    /**
     * Load all required scripts in parallel
     * @param {Array<string>} scripts - Array of script paths to load
     * @returns {Promise} - Promise that resolves when all scripts are loaded
     */
    function loadScripts(scripts) {
        const uniqueScripts = Array.from(new Set(scripts)); // Remove duplicates
        const promises = uniqueScripts.map(src => loadScript(src));
        return Promise.all(promises);
    }

    /**
     * Initialize the LocalLift application
     */
    function initApp() {
        // Setup global namespace
        window.LocalLift = window.LocalLift || {};
        
        // Detect environment (development or production)
        const isProduction = window.location.hostname !== 'localhost' && 
                            !window.location.hostname.includes('127.0.0.1');
        
        window.LocalLift.config = {
            environment: isProduction ? 'production' : 'development',
            apiBaseUrl: isProduction ? '/api' : 'http://localhost:8000/api',
            version: '1.0.0'
        };
        
        // Add utility functions to the global namespace
        window.LocalLift.utils = {
            loadScript,
            loadScripts,
            
            // Add a debounce function for performance optimization
            debounce: function(func, wait) {
                let timeout;
                return function(...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), wait);
                };
            },
            
            // Sanitize user input to prevent XSS attacks
            sanitizeInput: function(input) {
                const element = document.createElement('div');
                element.textContent = input;
                return element.innerHTML;
            }
        };
        
        // Initialize event tracking if available
        if (typeof window.LocalLift.analytics !== 'undefined') {
            window.LocalLift.analytics.init();
        }
        
        console.log(`LocalLift application initialized (${window.LocalLift.config.environment})`);
    }

    /**
     * Initialize the application
     */
    function init() {
        // Determine which modules to load based on the current page
        const pageDependencies = determinePageModules();
        const allDependencies = [...REQUIRED_MODULES, ...pageDependencies];
        
        // Show loading indicator
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        // Load all required modules
        loadScripts(allDependencies)
            .then(() => {
                console.log('All modules loaded successfully');
                
                // Initialize the application
                initApp();
                
                // Hide loading indicator
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }
                
                // Dispatch ready event
                window.dispatchEvent(new CustomEvent('LocalLiftReady'));
            })
            .catch(error => {
                console.error('Failed to load all modules', error);
                
                // Still hide loading indicator even on error
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }
                
                // Show error message
                const errorElement = document.getElementById('error-message');
                if (errorElement) {
                    errorElement.textContent = 'Failed to load application resources. Please refresh the page.';
                    errorElement.style.display = 'block';
                }
            });
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
