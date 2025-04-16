/**
 * LocalLift Frontend Main JavaScript
 * This file handles core frontend functionality for the LocalLift application
 */

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('LocalLift application initialized');
    
    // Get API base URL from config
    const CONFIG = window.LOCALLIFT_CONFIG || {};
    const API_BASE = CONFIG.API_BASE_URL || 'http://localhost:8000';
    console.log('Using API base URL:', API_BASE);
    
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
            const healthCheckUrl = CONFIG.HEALTH_CHECK_URL || `${API_BASE}/api/health`;
            console.log('Checking API health at:', healthCheckUrl);
            
            const response = await fetch(healthCheckUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                // Adding credentials to ensure cookies are sent
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('API status:', data);
                document.querySelector('.api-status')?.classList.add('connected');
                return true;
            } else {
                console.warn('API connection issues detected - status:', response.status);
                document.querySelector('.api-status')?.classList.add('error');
                return false;
            }
        } catch (error) {
            console.warn('Could not connect to LocalLift API', error);
            document.querySelector('.api-status')?.classList.add('error');
            return false;
        }
    }
    
    // Initialize API check
    checkApiStatus().then(isConnected => {
        if (isConnected) {
            console.log('API connection established successfully');
        } else {
            console.warn('Using offline mode due to API connection issues');
        }
    });
    
    // Initialize feature animations
    const features = document.querySelectorAll('.feature');
    features.forEach((feature, index) => {
        // Add a slight delay to each feature for a staggered animation
        setTimeout(() => {
            feature.classList.add('show');
        }, 200 * (index + 1));
    });
    
    // Handle testimonial clicks
    document.querySelectorAll('.testimonial').forEach(testimonial => {
        testimonial.addEventListener('click', function() {
            this.classList.toggle('expanded');
        });
    });
});
