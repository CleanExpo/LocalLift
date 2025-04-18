/**
 * LocalLift Dropdown Handler
 * Provides consistent dropdown behavior throughout the application
 */

(function() {
    'use strict';
    
    // Configuration for behavior
    const config = {
        // Time in ms before closing a dropdown when mouse leaves
        closeDelay: 150,
        // Add event listeners to close dropdowns when clicking outside
        closeOnOutsideClick: true,
        // CSS class applied to open dropdowns
        activeClass: 'show',
        // Automatically close other dropdowns when opening a new one
        autoClose: true
    };

    // Store all dropdowns and their timeouts
    const dropdowns = new Map();
    let closeTimeouts = {};

    /**
     * Initialize a dropdown element
     * @param {HTMLElement} dropdown - The dropdown container element
     */
    function initDropdown(dropdown) {
        if (!dropdown || dropdowns.has(dropdown)) return;
        
        const trigger = dropdown.querySelector('[data-dropdown-trigger]') || dropdown;
        const content = dropdown.querySelector('[data-dropdown-content]') || 
                        dropdown.querySelector('.dropdown-content');
        
        if (!content) return;

        // Store references to DOM elements
        dropdowns.set(dropdown, {
            trigger: trigger,
            content: content,
            isOpen: false,
            closeOnHoverOut: dropdown.getAttribute('data-close-on-hover') !== 'false'
        });

        // Add click handler to trigger
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            toggleDropdown(dropdown);
        });

        // Add keyboard accessibility
        trigger.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleDropdown(dropdown);
            } else if (e.key === 'Escape' && isDropdownOpen(dropdown)) {
                e.preventDefault();
                closeDropdown(dropdown);
            }
        });

        // Ensure we have appropriate ARIA attributes
        if (!trigger.hasAttribute('aria-expanded')) {
            trigger.setAttribute('aria-expanded', 'false');
        }
        
        if (!trigger.hasAttribute('aria-haspopup')) {
            trigger.setAttribute('aria-haspopup', 'true');
        }
        
        if (content.id) {
            trigger.setAttribute('aria-controls', content.id);
        } else {
            // Generate an ID if one doesn't exist
            const newId = `dropdown-content-${Math.floor(Math.random() * 10000)}`;
            content.id = newId;
            trigger.setAttribute('aria-controls', newId);
        }

        // Add hover behavior if specified
        if (dropdown.getAttribute('data-trigger') === 'hover') {
            dropdown.addEventListener('mouseenter', () => {
                clearTimeout(closeTimeouts[dropdown.id]);
                openDropdown(dropdown);
            });

            dropdown.addEventListener('mouseleave', () => {
                const dropdownData = dropdowns.get(dropdown);
                if (dropdownData && dropdownData.closeOnHoverOut) {
                    closeTimeouts[dropdown.id] = setTimeout(() => {
                        closeDropdown(dropdown);
                    }, config.closeDelay);
                }
            });
        }
    }

    /**
     * Check if a dropdown is open
     * @param {HTMLElement} dropdown - The dropdown container
     * @returns {boolean} - Whether the dropdown is open
     */
    function isDropdownOpen(dropdown) {
        const data = dropdowns.get(dropdown);
        return data && data.isOpen;
    }

    /**
     * Toggle a dropdown's open/closed state
     * @param {HTMLElement} dropdown - The dropdown container
     */
    function toggleDropdown(dropdown) {
        if (isDropdownOpen(dropdown)) {
            closeDropdown(dropdown);
        } else {
            openDropdown(dropdown);
        }
    }

    /**
     * Open a dropdown
     * @param {HTMLElement} dropdown - The dropdown container
     */
    function openDropdown(dropdown) {
        // Don't do anything if already open
        if (isDropdownOpen(dropdown)) return;
        
        const data = dropdowns.get(dropdown);
        if (!data) return;

        // Auto-close other dropdowns if configured
        if (config.autoClose) {
            closeAllDropdowns(dropdown);
        }

        // Show the dropdown content
        data.content.classList.add(config.activeClass);
        data.trigger.setAttribute('aria-expanded', 'true');
        
        // Update state
        data.isOpen = true;
        
        // Dispatch custom event
        dropdown.dispatchEvent(new CustomEvent('dropdownOpened', {
            bubbles: true
        }));
    }

    /**
     * Close a dropdown
     * @param {HTMLElement} dropdown - The dropdown container
     */
    function closeDropdown(dropdown) {
        // Don't do anything if already closed
        if (!isDropdownOpen(dropdown)) return;
        
        const data = dropdowns.get(dropdown);
        if (!data) return;

        // Hide the dropdown content
        data.content.classList.remove(config.activeClass);
        data.trigger.setAttribute('aria-expanded', 'false');
        
        // Update state
        data.isOpen = false;
        
        // Dispatch custom event
        dropdown.dispatchEvent(new CustomEvent('dropdownClosed', {
            bubbles: true
        }));
    }

    /**
     * Close all open dropdowns
     * @param {HTMLElement} [except] - Optional dropdown to exclude from closing
     */
    function closeAllDropdowns(except) {
        dropdowns.forEach((data, dropdown) => {
            if (dropdown !== except && data.isOpen) {
                closeDropdown(dropdown);
            }
        });
    }

    /**
     * Initialize all dropdowns on the page
     */
    function initAllDropdowns() {
        document.querySelectorAll('.dropdown, [data-dropdown]').forEach(dropdown => {
            initDropdown(dropdown);
        });
    }

    /**
     * Set up document-level event handlers
     */
    function setupGlobalHandlers() {
        // Close dropdowns when clicking outside
        if (config.closeOnOutsideClick) {
            document.addEventListener('click', (e) => {
                dropdowns.forEach((data, dropdown) => {
                    // Check if click is outside both the trigger and content
                    if (data.isOpen && 
                        !data.trigger.contains(e.target) && 
                        !data.content.contains(e.target)) {
                        closeDropdown(dropdown);
                    }
                });
            });
        }

        // Close dropdowns on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeAllDropdowns();
            }
        });

        // Handle dynamically added dropdowns
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            // Check if the added node is a dropdown
                            if (node.classList && (node.classList.contains('dropdown') || 
                                node.hasAttribute('data-dropdown'))) {
                                initDropdown(node);
                            }
                            
                            // Check for dropdowns within the added node
                            if (node.querySelectorAll) {
                                node.querySelectorAll('.dropdown, [data-dropdown]').forEach(dropdown => {
                                    initDropdown(dropdown);
                                });
                            }
                        }
                    });
                }
            });
        });
        
        // Observe the entire document for dynamically added dropdowns
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Initialize dropdown functionality
     */
    function init() {
        // Create global API
        window.LocalLift = window.LocalLift || {};
        window.LocalLift.dropdowns = {
            init: initAllDropdowns,
            initDropdown: initDropdown,
            open: openDropdown,
            close: closeDropdown,
            toggle: toggleDropdown,
            closeAll: closeAllDropdowns,
            isOpen: isDropdownOpen,
            configure: (newConfig) => {
                Object.assign(config, newConfig);
            }
        };
        
        // Initialize all dropdowns
        initAllDropdowns();
        
        // Set up global event handlers
        setupGlobalHandlers();
        
        console.log('LocalLift dropdown handler initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
