/**
 * Tab Handler for LocalLift UI
 * Handles tab switching functionality for tabbed interfaces
 */

document.addEventListener('DOMContentLoaded', function() {
  // Tab switching functionality for standard tab interfaces
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  if (tabButtons.length && tabContents.length) {
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Get the tab's data-tab attribute
        const tabTarget = this.getAttribute('data-tab');

        // Remove active class from all tabs and tab contents
        tabButtons.forEach(t => t.classList.remove('active'));
        tabContents.forEach(content => content.classList.add('hidden'));

        // Add active class to current tab and corresponding content
        this.classList.add('active');
        const targetContent = document.getElementById(`${tabTarget}-tab`);
        if (targetContent) {
          targetContent.classList.remove('hidden');
        }
      });
    });
  }

  // Initialize the first tab as active if none is active
  if (tabButtons.length && !document.querySelector('.tab-button.active')) {
    const firstTab = tabButtons[0];
    const firstTabTarget = firstTab.getAttribute('data-tab');

    firstTab.classList.add('active');
    const firstContent = document.getElementById(`${firstTabTarget}-tab`);
    if (firstContent) {
      firstContent.classList.remove('hidden');
    }
  }
});
