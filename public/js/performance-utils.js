/**
 * LocalLift Performance Utilities
 * Advanced performance optimizations for the LocalLift platform
 */

const PerformanceUtils = (function() {
    'use strict';
    
    // Private cache for memoization
    const _memoizationCache = new Map();
    
    // Resource loading status tracker
    const _loadedResources = new Set();
    
    // Performance metrics collection
    const _metrics = {
        navigationStart: performance.now(),
        resourceLoadTimes: {},
        interactionTimes: {},
        apiCallTimes: {}
    };
    
    /**
     * Initialize performance monitoring
     */
    function init() {
        // Track page load performance
        window.addEventListener('load', () => {
            _metrics.pageLoadTime = performance.now() - _metrics.navigationStart;
            console.log(`Page loaded in ${_metrics.pageLoadTime.toFixed(2)}ms`);
            
            // Report to analytics if available
            if (window.LocalLift && window.LocalLift.analytics) {
                window.LocalLift.analytics.trackPerformance('page_load', _metrics.pageLoadTime);
            }
            
            // Analyze performance and suggest improvements
            analyzePerformance();
        });
        
        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        // Log tasks that block the main thread for more than 50ms
                        if (entry.duration > 50) {
                            console.warn(`Long task detected: ${entry.duration.toFixed(2)}ms`, entry);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                console.warn('PerformanceObserver for long tasks not supported');
            }
        }
        
        // Set up custom performance timing events
        interceptFetch();
        trackUserInteractions();
    }
    
    /**
     * Intercept fetch calls to measure API performance
     */
    function interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = function(...args) {
            const startTime = performance.now();
            const url = args[0] instanceof Request ? args[0].url : args[0];
            
            return originalFetch.apply(this, args)
                .then(response => {
                    const endTime = performance.now();
                    const duration = endTime - startTime;
                    
                    // Store API call timing data
                    const apiEndpoint = new URL(url).pathname;
                    _metrics.apiCallTimes[apiEndpoint] = duration;
                    
                    // Log slow API calls (over 1 second)
                    if (duration > 1000) {
                        console.warn(`Slow API call to ${apiEndpoint}: ${duration.toFixed(2)}ms`);
                    }
                    
                    return response;
                });
        };
    }
    
    /**
     * Track user interaction responsiveness
     */
    function trackUserInteractions() {
        ['click', 'input', 'keydown', 'scroll'].forEach(eventType => {
            document.addEventListener(eventType, () => {
                // Measure time until next frame render
                const startTime = performance.now();
                
                requestAnimationFrame(() => {
                    const renderTime = performance.now() - startTime;
                    
                    // Log slow interactions (taking more than 100ms to render)
                    if (renderTime > 100) {
                        console.warn(`Slow ${eventType} response: ${renderTime.toFixed(2)}ms`);
                    }
                    
                    // Track average interaction time by type
                    if (!_metrics.interactionTimes[eventType]) {
                        _metrics.interactionTimes[eventType] = [];
                    }
                    
                    _metrics.interactionTimes[eventType].push(renderTime);
                });
            }, { passive: true });
        });
    }
    
    /**
     * Preload critical resources
     * @param {Array<string>} resources - URLs of resources to preload
     */
    function preloadResources(resources) {
        if (!resources || !resources.length) return;
        
        resources.forEach(url => {
            // Skip if already loaded or preloaded
            if (_loadedResources.has(url)) return;
            
            const extension = url.split('.').pop().toLowerCase();
            let type;
            
            // Determine resource type based on extension
            switch (extension) {
                case 'css': type = 'style'; break;
                case 'js': type = 'script'; break;
                case 'woff':
                case 'woff2':
                case 'ttf': type = 'font'; break;
                case 'jpg':
                case 'jpeg':
                case 'png':
                case 'gif':
                case 'webp':
                case 'svg': type = 'image'; break;
                default: type = 'fetch'; break;
            }
            
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = url;
            link.as = type;
            
            if (type === 'font') {
                link.crossOrigin = 'anonymous';
            }
            
            document.head.appendChild(link);
            _loadedResources.add(url);
        });
    }
    
    /**
     * Lazy load non-critical resources
     * @param {Array<Object>} resources - Resources to lazy load
     * @param {string} resources[].url - Resource URL
     * @param {string} resources[].type - Resource type (script, style, image)
     * @param {Function} resources[].callback - Optional callback after loading
     */
    function lazyLoadResources(resources) {
        if (!resources || !resources.length) return;
        
        // Use Intersection Observer if available
        if ('IntersectionObserver' in window) {
            const options = {
                rootMargin: '200px 0px', // Load when within 200px of viewport
                threshold: 0.01
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const resourceId = entry.target.dataset.resourceId;
                        const resource = resources.find(r => r.id === resourceId);
                        
                        if (resource) {
                            loadResource(resource);
                            observer.unobserve(entry.target);
                        }
                    }
                });
            }, options);
            
            // Create placeholder elements to observe
            resources.forEach(resource => {
                const placeholder = document.createElement('div');
                placeholder.style.height = '1px';
                placeholder.style.width = '1px';
                placeholder.style.position = 'absolute';
                placeholder.style.pointerEvents = 'none';
                placeholder.dataset.resourceId = resource.id;
                
                document.body.appendChild(placeholder);
                observer.observe(placeholder);
            });
        } else {
            // Fallback for browsers without Intersection Observer
            window.addEventListener('scroll', debounce(() => {
                const viewportHeight = window.innerHeight;
                const scrollPosition = window.scrollY;
                
                resources.forEach(resource => {
                    // Load resource when user scrolls near it
                    if (!_loadedResources.has(resource.url) && 
                        scrollPosition + viewportHeight + 200 >= resource.position) {
                        loadResource(resource);
                    }
                });
            }, 100));
        }
    }
    
    /**
     * Load a resource dynamically
     * @param {Object} resource - Resource configuration
     */
    function loadResource(resource) {
        if (_loadedResources.has(resource.url)) return;
        
        const startTime = performance.now();
        
        switch(resource.type) {
            case 'script':
                const script = document.createElement('script');
                script.src = resource.url;
                script.async = true;
                script.onload = () => {
                    _loadedResources.add(resource.url);
                    _metrics.resourceLoadTimes[resource.url] = performance.now() - startTime;
                    if (typeof resource.callback === 'function') {
                        resource.callback();
                    }
                };
                document.head.appendChild(script);
                break;
                
            case 'style':
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = resource.url;
                link.onload = () => {
                    _loadedResources.add(resource.url);
                    _metrics.resourceLoadTimes[resource.url] = performance.now() - startTime;
                    if (typeof resource.callback === 'function') {
                        resource.callback();
                    }
                };
                document.head.appendChild(link);
                break;
                
            case 'image':
                const img = new Image();
                img.onload = () => {
                    _loadedResources.add(resource.url);
                    _metrics.resourceLoadTimes[resource.url] = performance.now() - startTime;
                    if (typeof resource.callback === 'function') {
                        resource.callback(img);
                    }
                };
                img.src = resource.url;
                break;
        }
    }
    
    /**
     * Memoize function results to avoid redundant calculations
     * @param {Function} fn - Function to memoize
     * @param {Function} keyFn - Function to generate cache key
     * @returns {Function} - Memoized function
     */
    function memoize(fn, keyFn) {
        return function(...args) {
            const key = keyFn ? keyFn(...args) : JSON.stringify(args);
            
            if (_memoizationCache.has(key)) {
                return _memoizationCache.get(key);
            }
            
            const result = fn.apply(this, args);
            _memoizationCache.set(key, result);
            return result;
        };
    }
    
    /**
     * Debounce function calls
     * @param {Function} fn - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} - Debounced function
     */
    function debounce(fn, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), wait);
        };
    }
    
    /**
     * Throttle function calls to limit execution frequency
     * @param {Function} fn - Function to throttle
     * @param {number} limit - Minimum time between executions
     * @returns {Function} - Throttled function
     */
    function throttle(fn, limit) {
        let lastCall = 0;
        return function(...args) {
            const now = Date.now();
            if (now - lastCall >= limit) {
                lastCall = now;
                return fn.apply(this, args);
            }
        };
    }
    
    /**
     * Request Idle Callback polyfill and wrapper
     * @param {Function} fn - Function to execute during idle time
     * @param {Object} options - Timeout options
     */
    function runWhenIdle(fn, options = { timeout: 1000 }) {
        if ('requestIdleCallback' in window) {
            return window.requestIdleCallback(fn, options);
        } else {
            // Polyfill for browsers without requestIdleCallback
            return setTimeout(() => {
                const start = Date.now();
                fn({
                    didTimeout: false,
                    timeRemaining: () => Math.max(0, 50 - (Date.now() - start))
                });
            }, options.timeout);
        }
    }
    
    /**
     * Analyze performance and suggest improvements
     */
    function analyzePerformance() {
        runWhenIdle(() => {
            // Analyze API calls
            const slowApiCalls = Object.entries(_metrics.apiCallTimes)
                .filter(([_, time]) => time > 500)
                .sort((a, b) => b[1] - a[1]);
                
            if (slowApiCalls.length > 0) {
                console.warn('Performance: Slow API calls detected:', 
                    slowApiCalls.map(([endpoint, time]) => `${endpoint}: ${time.toFixed(2)}ms`));
            }
            
            // Analyze interaction responsiveness
            Object.entries(_metrics.interactionTimes).forEach(([type, times]) => {
                if (times.length > 0) {
                    const avg = times.reduce((sum, time) => sum + time, 0) / times.length;
                    if (avg > 50) {
                        console.warn(`Performance: Slow ${type} response (avg: ${avg.toFixed(2)}ms)`);
                    }
                }
            });
            
            // Check page load time
            if (_metrics.pageLoadTime > 3000) {
                console.warn(`Performance: Slow page load (${_metrics.pageLoadTime.toFixed(2)}ms). Consider optimizing critical rendering path.`);
            }
        });
    }
    
    /**
     * Get current performance metrics
     * @returns {Object} - Performance metrics
     */
    function getMetrics() {
        return JSON.parse(JSON.stringify(_metrics)); // Return deep copy
    }
    
    /**
     * Apply CSS containment for performance
     * @param {Array<string>} selectors - CSS selectors to apply containment to
     * @param {string} type - Containment type (content, size, layout, paint, strict)
     */
    function applyCSSContainment(selectors, type = 'content') {
        if (!selectors || !selectors.length) return;
        
        const style = document.createElement('style');
        style.textContent = selectors.map(selector => 
            `${selector} { contain: ${type}; }`
        ).join('\n');
        
        document.head.appendChild(style);
    }
    
    /**
     * Use optimized requestAnimationFrame for animations
     * @param {Function} callback - Animation callback
     * @returns {Object} - Animation controller
     */
    function createOptimizedAnimation(callback) {
        let rafId = null;
        let lastTimestamp = 0;
        const targetFps = 60;
        const frameBudget = 1000 / targetFps;
        
        function tick(timestamp) {
            rafId = requestAnimationFrame(tick);
            
            // Skip frames to maintain target FPS
            const elapsed = timestamp - lastTimestamp;
            if (elapsed < frameBudget) return;
            
            // Calculate delta time for smooth animations regardless of frame rate
            const delta = elapsed / frameBudget;
            
            // Execute animation callback
            callback(delta, timestamp);
            
            lastTimestamp = timestamp;
        }
        
        return {
            start() {
                if (rafId === null) {
                    lastTimestamp = performance.now();
                    rafId = requestAnimationFrame(tick);
                }
                return this;
            },
            stop() {
                if (rafId !== null) {
                    cancelAnimationFrame(rafId);
                    rafId = null;
                }
                return this;
            }
        };
    }
    
    // Public API
    return {
        init,
        preloadResources,
        lazyLoadResources,
        memoize,
        debounce,
        throttle,
        runWhenIdle,
        getMetrics,
        applyCSSContainment,
        createOptimizedAnimation
    };
})();

// Auto-initialize if the global namespace exists
if (window.LocalLift) {
    window.LocalLift.performance = PerformanceUtils;
    document.addEventListener('DOMContentLoaded', PerformanceUtils.init);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceUtils;
}
