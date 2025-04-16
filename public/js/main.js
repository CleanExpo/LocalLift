/**
 * LocalLift Frontend Main JavaScript
 * This file handles core frontend functionality for the LocalLift application
 */

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('LocalLift application initialized');
    
    // Get API base URL from config
    const API_BASE = window.apiBase || 'http://localhost:8000';
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            // Only apply smooth scroll for same-page links
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // CTA button animation
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        ctaButton.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
        });
    }
    
    // Check API connectivity
    async function checkApiStatus() {
        try {
            const response = await fetch(`${API_BASE}/api/health`);
            if (response.ok) {
                console.log('Connected to LocalLift API successfully');
            } else {
                console.warn('API connection issues detected');
            }
        } catch (error) {
            console.warn('Could not connect to LocalLift API', error);
        }
    }
    
    // Initialize API check
    checkApiStatus();
});
