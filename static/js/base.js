// Base JavaScript functionality for FreelanceHub
(function() {
    'use strict';

    // Mobile menu toggle
    function initMobileMenu() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
                // Update aria-expanded for accessibility
                const isExpanded = !mobileMenu.classList.contains('hidden');
                mobileMenuButton.setAttribute('aria-expanded', isExpanded);
            });
        }
    }

    // Smooth scroll for anchor links
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Intersection Observer for animations
    function initAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slide-up');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // CSRF token for AJAX requests
    function getCSRFToken() {
        const tokenElement = document.querySelector('meta[name="csrf-token"]');
        return tokenElement ? tokenElement.getAttribute('content') : null;
    }

    // Add CSRF token to all AJAX requests
    function initCSRFProtection() {
        const token = getCSRFToken();
        if (token) {
            // Override fetch to include CSRF token
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                if (options.method && options.method !== 'GET') {
                    options.headers = {
                        ...options.headers,
                        'X-CSRFToken': token
                    };
                }
                return originalFetch(url, options);
            };
        }
    }

    // Initialize all functionality when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initMobileMenu();
        initSmoothScroll();
        initAnimations();
        initCSRFProtection();
    });

    // Export functions for use in other scripts
    window.FreelanceHub = window.FreelanceHub || {};
    window.FreelanceHub.getCSRFToken = getCSRFToken;
})(); 