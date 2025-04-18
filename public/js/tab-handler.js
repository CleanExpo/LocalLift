/**
 * LocalLift Tab Handler
 * Manages tabbed interfaces throughout the application
 */

(function() {
    'use strict';

    /**
     * Initialize tabs functionality for a container
     * @param {HTMLElement} tabContainer - The container element for the tabs
     */
    function initTabs(tabContainer) {
        const tabs = tabContainer.querySelectorAll('[role="tab"]');
        const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]')).filter(panel => {
            // Only get panels that belong to this tab container
            const controlledBy = panel.getAttribute('aria-labelledby');
            return controlledBy && tabContainer.querySelector(`#${controlledBy}`);
        });

        // Hide all tab panels initially
        tabPanels.forEach(panel => {
            panel.hidden = true;
        });

        // Set up click handlers for tabs
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                activateTab(tab, tabs, tabPanels);
            });

            // Handle keyboard navigation
            tab.addEventListener('keydown', (e) => {
                handleTabKeydown(e, tabs);
            });
        });

        // Activate the first tab by default or a tab specified by URL hash
        const hashId = window.location.hash.substring(1);
        let defaultTab = tabs[0];
        
        if (hashId) {
            // Check if there's a tab matching the hash
            const hashTab = Array.from(tabs).find(tab => tab.id === hashId 
                                              || tab.getAttribute('data-tab-id') === hashId);
            if (hashTab) {
                defaultTab = hashTab;
            }
        } else {
            // Try to find a tab marked as default
            const markedDefault = Array.from(tabs).find(tab => tab.getAttribute('data-default') === 'true');
            if (markedDefault) {
                defaultTab = markedDefault;
            }
        }
        
        // Activate the default tab
        if (defaultTab) {
            activateTab(defaultTab, tabs, tabPanels);
        }
    }

    /**
     * Activate a tab and show its panel
     * @param {HTMLElement} tab - The tab to activate
     * @param {NodeList} allTabs - All tabs in the container
     * @param {Array} allPanels - All panels in the container
     */
    function activateTab(tab, allTabs, allPanels) {
        // Deactivate all tabs
        allTabs.forEach(t => {
            t.setAttribute('aria-selected', 'false');
            t.setAttribute('tabindex', '-1');
            t.classList.remove('active');
        });

        // Hide all panels
        allPanels.forEach(panel => {
            panel.hidden = true;
        });

        // Activate the selected tab
        tab.setAttribute('aria-selected', 'true');
        tab.setAttribute('tabindex', '0');
        tab.classList.add('active');
        tab.focus();

        // Show the selected panel
        const panelId = tab.getAttribute('aria-controls');
        if (panelId) {
            const panel = document.getElementById(panelId);
            if (panel) {
                panel.hidden = false;
                
                // Update URL hash if needed
                if (tab.getAttribute('data-update-hash') !== 'false') {
                    const hashId = tab.getAttribute('data-tab-id') || tab.id;
                    if (hashId) {
                        history.replaceState(null, null, `#${hashId}`);
                    }
                }
                
                // Dispatch custom event
                const event = new CustomEvent('tabChanged', {
                    detail: {
                        tab: tab,
                        panel: panel
                    },
                    bubbles: true
                });
                tab.dispatchEvent(event);
            }
        }
    }

    /**
     * Handle keyboard navigation for tabs
     * @param {KeyboardEvent} event - The keyboard event
     * @param {NodeList} tabs - All tabs in the container
     */
    function handleTabKeydown(event, tabs) {
        const key = event.key;
        const tabsArray = Array.from(tabs);
        const index = tabsArray.indexOf(event.target);

        // Navigate with arrow keys
        switch (key) {
            case 'ArrowRight':
            case 'ArrowDown':
                event.preventDefault();
                const nextTab = tabsArray[(index + 1) % tabsArray.length];
                nextTab.click();
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
                event.preventDefault();
                const prevTab = tabsArray[(index - 1 + tabsArray.length) % tabsArray.length];
                prevTab.click();
                break;
            case 'Home':
                event.preventDefault();
                tabsArray[0].click();
                break;
            case 'End':
                event.preventDefault();
                tabsArray[tabsArray.length - 1].click();
                break;
        }
    }

    /**
     * Initialize all tab containers on the page
     */
    function initAllTabs() {
        const tabContainers = document.querySelectorAll('[role="tablist"]');
        tabContainers.forEach(container => {
            initTabs(container);
        });
    }
    
    /**
     * Initialize event listeners for dynamic tab creation
     */
    function initDynamicTabListeners() {
        // Listen for custom event when new tabs are added to the DOM
        document.addEventListener('tabsCreated', (event) => {
            const container = event.detail.container;
            if (container) {
                initTabs(container);
            } else {
                // If no specific container, reinitialize all tabs
                initAllTabs();
            }
        });
    }

    /**
     * Main initialization function
     */
    function init() {
        // Create global tab API
        window.LocalLift = window.LocalLift || {};
        window.LocalLift.tabs = {
            init: initAllTabs,
            initContainer: initTabs,
            activateTab: (tabId) => {
                const tab = document.getElementById(tabId);
                if (tab && tab.getAttribute('role') === 'tab') {
                    const container = tab.closest('[role="tablist"]');
                    if (container) {
                        const tabs = container.querySelectorAll('[role="tab"]');
                        const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]')).filter(panel => {
                            const controlledBy = panel.getAttribute('aria-labelledby');
                            return controlledBy && container.querySelector(`#${controlledBy}`);
                        });
                        activateTab(tab, tabs, tabPanels);
                    }
                }
            }
        };
        
        // Initialize all tabs on the page
        initAllTabs();
        
        // Set up event listeners for dynamic tabs
        initDynamicTabListeners();
        
        console.log('LocalLift tab handler initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
