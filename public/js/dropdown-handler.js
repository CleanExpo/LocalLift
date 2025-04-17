/**
 * Dropdown Handler for LocalLift UI
 * Handles dropdown functionality for selecting content modules
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get dropdown elements
  const moduleDropdown = document.getElementById('module-dropdown');
  const dropdownContent = document.querySelector('.dropdown-content');
  const dropdownOptions = document.querySelectorAll('.dropdown-option');
  const moduleContainers = document.querySelectorAll('.module-wrapper');
  
  // General dropdown handling for navigation
  const allDropdowns = document.querySelectorAll('.dropdown');
  
  if (allDropdowns.length) {
    allDropdowns.forEach(dropdown => {
      const button = dropdown.querySelector('button, a');
      const content = dropdown.querySelector('.dropdown-content');
      
      if (button && content) {
        // Toggle dropdown visibility when clicking the dropdown button
        button.addEventListener('click', function(e) {
          e.stopPropagation();
          content.classList.toggle('show');
        });
      }
    });
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function() {
      document.querySelectorAll('.dropdown-content').forEach(content => {
        content.classList.remove('show');
      });
    });
  }

  // Specific handling for module selection dropdowns
  if (moduleDropdown && dropdownContent && dropdownOptions.length) {
    // Toggle dropdown visibility when clicking the dropdown button
    moduleDropdown.addEventListener('click', function(e) {
      e.stopPropagation();
      dropdownContent.classList.toggle('show');
    });

    // Handle dropdown option selection
    dropdownOptions.forEach(option => {
      option.addEventListener('click', function(e) {
        e.stopPropagation();

        // Get the selected module ID
        const moduleId = this.getAttribute('data-module');

        // Update dropdown button text
        const selectedText = this.textContent;
        moduleDropdown.querySelector('.dropdown-text').textContent = selectedText;

        // Hide dropdown after selection
        dropdownContent.classList.remove('show');

        // Show the selected module hide others
        moduleContainers.forEach(container => {
          if (container.id === moduleId) {
            container.classList.add('active');
          } else {
            container.classList.remove('active');
          }
        });
      });
    });
  }
  
  // Mobile menu toggle functionality
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');
  
  if (mobileMenuToggle && mobileNav) {
    mobileMenuToggle.addEventListener('click', function() {
      mobileNav.classList.toggle('hidden');
      this.classList.toggle('active');
    });
  }
});
