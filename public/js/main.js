/**
 * LocalLift Main JavaScript Handler
 * This file coordinates module initialization and dependency loading
 * with enhanced performance optimizations
 */

(function() {
    'use strict';

    // Configuration - Performance optimized loading order
    const CRITICAL_MODULES = [
        // Essential for initial render
        '/js/performance-utils.js'
    ];
    
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

    // Deferred modules loaded after critical path is complete
    const DEFERRED_MODULES = [
        '/js/analytics.js',
        '/js/feedback.js'
    ];

    /**
     * Check which page-specific modules to load
     * @returns {Array} Modules to load for current page
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
     * Identify critical resources for current page
     * @returns {Array} Critical resources to preload
     */
    function identifyCriticalResources() {
        const path = window.location.pathname;
        const resources = [
            // Critical CSS
            '/style.css',
            // Critical fonts
            '/fonts/inter-var.woff2'
        ];
        
        // Page-specific critical resources
        if (path.startsWith('/dashboard')) {
            resources.push('/img/logo.svg', '/img/icons/dashboard.svg');
        } else if (path.startsWith('/login')) {
            resources.push('/img/logo.svg', '/img/login-bg.webp');
        }
        
        return resources;
    }

    /**
     * Dynamically load a JavaScript file with priority
     * @param {string} src - Path to JavaScript file
     * @param {Object} options - Loading options
     * @returns {Promise} - Promise that resolves when file is loaded
     */
    function loadScript(src, options = {}) {
        return new Promise((resolve, reject) => {
            // Skip if already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            
            // Set script attributes based on options
            if (options.defer) {
                script.defer = true;
            } else if (options.async) {
                script.async = true;
            }
            
            // Add priority hints if supported
            if ('fetchPriority' in HTMLScriptElement.prototype) {
                script.fetchPriority = options.priority || 'auto';
            }

            script.onload = () => resolve();
            script.onerror = () => {
                console.error(`Failed to load script: ${src}`);
                reject(new Error(`Failed to load script: ${src}`));
            };

            document.head.appendChild(script);
        });
    }

    /**
     * Load modules in priority order
     * @param {Array<string>} criticalScripts - Highest priority scripts
     * @param {Array<string>} requiredScripts - Regular priority scripts
     * @param {Array<string>} deferredScripts - Low priority scripts to load last
     * @returns {Promise} - Promise that resolves when critical and required scripts are loaded
     */
    function loadModules(criticalScripts, requiredScripts, deferredScripts) {
        // First load critical scripts sequentially for predictable execution
        return criticalScripts.reduce((chain, src) => 
            chain.then(() => loadScript(src, { priority: 'high' })),
            Promise.resolve()
        ).then(() => {
            // Then load required scripts in parallel
            const requiredPromises = requiredScripts.map(src => 
                loadScript(src, { async: true })
            );
            
            // Defer non-critical scripts
            if (window.requestIdleCallback) {
                window.requestIdleCallback(() => {
                    deferredScripts.forEach(src => 
                        loadScript(src, { defer: true, priority: 'low' })
                    );
                }, { timeout: 2000 });
            } else {
                // Fallback for browsers without requestIdleCallback
                setTimeout(() => {
                    deferredScripts.forEach(src => 
                        loadScript(src, { defer: true, priority: 'low' })
                    );
                }, 1000);
            }
            
            // Return a promise that resolves when required scripts are loaded
            return Promise.all(requiredPromises);
        });
    }

    /**
     * Initialize the LocalLift application with performance optimizations
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
            version: '1.0.0',
            isFirstVisit: !localStorage.getItem('localLift_visited'),
            buildTime: '2025-04-18',
            enablePerformanceMonitoring: true
        };
        
        // Record first visit
        if (window.LocalLift.config.isFirstVisit) {
            localStorage.setItem('localLift_visited', Date.now());
        }
        
        // Use the optimized utils if available, or fallback to basic functions
        const perf = window.LocalLift.performance || {};
        
        // Add utility functions to the global namespace
        window.LocalLift.utils = {
            loadScript,
            loadModules,
            
            // Add performance-optimized utilities with fallbacks
            debounce: perf.debounce || function(func, wait) {
                let timeout;
                return function(...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), wait);
                };
            },
            
            throttle: perf.throttle || function(func, limit) {
                let lastCall = 0;
                return function(...args) {
                    const now = Date.now();
                    if (now - lastCall >= limit) {
                        lastCall = now;
                        return func.apply(this, args);
                    }
                };
            },
            
            memoize: perf.memoize || function(fn) {
                const cache = new Map();
                return function(...args) {
                    const key = JSON.stringify(args);
                    if (cache.has(key)) return cache.get(key);
                    const result = fn.apply(this, args);
                    cache.set(key, result);
                    return result;
                };
            },
            
            // Sanitize user input to prevent XSS attacks
            sanitizeInput: function(input) {
                const element = document.createElement('div');
                element.textContent = input;
                return element.innerHTML;
            }
        };
        
        // Apply CSS containment to improve rendering performance
        if (perf.applyCSSContainment) {
            perf.applyCSSContainment([
                '.card', 
                '.sidebar', 
                '.modal', 
                '.list-item',
                '.chart-container'
            ]);
        }
        
        // Initialize event tracking if available
        if (typeof window.LocalLift.analytics !== 'undefined') {
            window.LocalLift.analytics.init();
        }
        
        console.log(`LocalLift application initialized (${window.LocalLift.config.environment})`);
        
        // Register service worker if in production
        if (isProduction && 'serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/service-worker.js')
                    .then(registration => {
                        console.log('ServiceWorker registration successful');
                    })
                    .catch(error => {
                        console.log('ServiceWorker registration failed: ', error);
                    });
            });
        }
    }

    /**
     * Initialize the application with performance optimizations
     */
    function init() {
        // Performance optimizations: Mark navigation start time
        if (window.performance && window.performance.mark) {
            window.performance.mark('localLift_navigationStart');
        }
        
        // Apply critical CSS containment for faster first paint
        const style = document.createElement('style');
        style.textContent = `
            body * { contain: content; }
            .main-content, .header, .footer { content-visibility: auto; }
            @media (prefers-reduced-motion: reduce) {
                * { animation-duration: 0.001s !important; transition-duration: 0.001s !important; }
            }
        `;
        document.head.appendChild(style);
        
        // Show loading indicator
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        // Preload critical resources
        const criticalResources = identifyCriticalResources();
        if ('PerformanceUtils' in window && window.PerformanceUtils.preloadResources) {
            window.PerformanceUtils.preloadResources(criticalResources);
        }
        
        // Determine which modules to load based on the current page
        const pageDependencies = determinePageModules();
        
        // Performance optimized module loading based on priority
        loadModules(
            CRITICAL_MODULES, 
            [...REQUIRED_MODULES, ...pageDependencies],
            DEFERRED_MODULES
        )
        .then(() => {
            console.log('Core modules loaded successfully');
            
            // Initialize the application
            initApp();
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Performance measurement: Mark app ready
            if (window.performance && window.performance.mark) {
                window.performance.mark('localLift_appReady');
                window.performance.measure(
                    'localLift_initialLoad', 
                    'localLift_navigationStart', 
                    'localLift_appReady'
                );
                
                const measures = window.performance.getEntriesByName('localLift_initialLoad');
                if (measures.length > 0) {
                    console.log(`Application ready in ${measures[0].duration.toFixed(2)}ms`);
                }
            }
            
            // Pre-connect to API domain for faster subsequent requests
            const apiDomain = new URL(window.LocalLift.config.apiBaseUrl).origin;
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = apiDomain;
            document.head.appendChild(link);
            
            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('LocalLiftReady'));
        })
        .catch(error => {
            console.error('Failed to load core modules', error);
            
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
