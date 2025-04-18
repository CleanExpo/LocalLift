/**
 * LocalLift Responsive Design Utilities
 * This file provides consistent responsive behavior across all pages
 */

(function() {
    'use strict';

    // Responsive breakpoints that match our CSS media queries
    const BREAKPOINTS = {
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280,
        '2xl': 1536
    };

    /**
     * Detect current breakpoint
     * @returns {string} Current breakpoint name
     */
    function getCurrentBreakpoint() {
        const width = window.innerWidth;
        
        if (width < BREAKPOINTS.sm) return 'xs';
        if (width < BREAKPOINTS.md) return 'sm';
        if (width < BREAKPOINTS.lg) return 'md';
        if (width < BREAKPOINTS.xl) return 'lg';
        if (width < BREAKPOINTS['2xl']) return 'xl';
        return '2xl';
    }

    /**
     * Check if the viewport is at or above a specific breakpoint
     * @param {string} breakpoint - Breakpoint name ('sm', 'md', 'lg', 'xl', '2xl')
     * @returns {boolean} Whether current viewport width is at or above the specified breakpoint
     */
    function isBreakpoint(breakpoint) {
        return window.innerWidth >= BREAKPOINTS[breakpoint];
    }

    /**
     * Setup responsive handlers for elements
     * This helps ensure consistent behavior across browsers
     */
    function setupResponsiveHandlers() {
        // Handle mobile menu toggle
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (menuToggle && navLinks) {
            menuToggle.addEventListener('click', function() {
                this.classList.toggle('active');
                navLinks.classList.toggle('hidden');
            });
            
            // Hide mobile menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!menuToggle.contains(event.target) && !navLinks.contains(event.target)) {
                    menuToggle.classList.remove('active');
                    navLinks.classList.add('hidden');
                }
            });
        }
        
        // Ensure proper menu visibility on resize
        window.addEventListener('resize', function() {
            if (isBreakpoint('md') && navLinks) {
                navLinks.classList.remove('hidden');
            } else if (navLinks && !menuToggle.classList.contains('active')) {
                navLinks.classList.add('hidden');
            }
        });
        
        // Setup dropdown behavior
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            const content = dropdown.querySelector('.dropdown-content');
            if (content) {
                dropdown.addEventListener('mouseenter', () => {
                    content.classList.add('show');
                });
                dropdown.addEventListener('mouseleave', () => {
                    content.classList.remove('show');
                });
                
                // Touch device support
                dropdown.addEventListener('touchstart', (e) => {
                    if (!content.classList.contains('show')) {
                        e.preventDefault();
                        content.classList.add('show');
                        // Close other dropdowns
                        dropdowns.forEach(other => {
                            if (other !== dropdown) {
                                const otherContent = other.querySelector('.dropdown-content');
                                if (otherContent) otherContent.classList.remove('show');
                            }
                        });
                    }
                });
                
                // Close dropdowns when clicking outside
                document.addEventListener('touchstart', (e) => {
                    if (!dropdown.contains(e.target)) {
                        content.classList.remove('show');
                    }
                });
            }
        });
    }

    /**
     * Ensure images scale properly and don't break layouts
     */
    function setupResponsiveImages() {
        const images = document.querySelectorAll('img:not(.fixed-size)');
        images.forEach(img => {
            // Set default styles for responsive images
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            
            // Check if image loads correctly
            img.addEventListener('error', () => {
                console.warn('Image failed to load:', img.src);
                img.style.display = 'none'; // Hide broken images
            });
        });
    }

    /**
     * Adjust font sizes for better readability on small screens
     */
    function setupResponsiveFonts() {
        if (window.innerWidth < BREAKPOINTS.sm) {
            document.querySelectorAll('.text-xl, .text-2xl, .text-3xl, .text-4xl').forEach(el => {
                // Reduce font size by one level on smallest screens
                if (el.classList.contains('text-4xl')) {
                    el.classList.remove('text-4xl');
                    el.classList.add('text-3xl');
                } else if (el.classList.contains('text-3xl')) {
                    el.classList.remove('text-3xl');
                    el.classList.add('text-2xl');
                } else if (el.classList.contains('text-2xl')) {
                    el.classList.remove('text-2xl');
                    el.classList.add('text-xl');
                } else if (el.classList.contains('text-xl')) {
                    el.classList.remove('text-xl');
                    el.classList.add('text-lg');
                }
            });
        }
    }

    /**
     * Initialize all responsive features
     */
    function init() {
        window.LocalLift = window.LocalLift || {};
        window.LocalLift.responsive = {
            getCurrentBreakpoint,
            isBreakpoint,
            BREAKPOINTS
        };
        
        setupResponsiveHandlers();
        setupResponsiveImages();
        setupResponsiveFonts();
        
        // Re-check on window resize
        window.addEventListener('resize', () => {
            setupResponsiveFonts();
        });
        
        console.log('LocalLift responsive utilities initialized');
    }
    
    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
