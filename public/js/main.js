/**
 * LocalLift main JavaScript file
 */

// Load configuration and authenticate user
document.addEventListener('DOMContentLoaded', function() {
  console.log('LocalLift application initialized');

  // Handle dropdown menus with improved functionality
  const accountDropdown = document.querySelector('.dropdown');
  if (accountDropdown) {
    const dropdownBtn = accountDropdown.querySelector('.btn-primary');
    const dropdownContent = accountDropdown.querySelector('.dropdown-content');

    // Add necessary styles for the dropdown content to be properly positioned and styled
    if (dropdownContent) {
      dropdownContent.style.position = 'absolute';
      dropdownContent.style.backgroundColor = '#fff';
      dropdownContent.style.minWidth = '180px';
      dropdownContent.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
      dropdownContent.style.zIndex = '1000';
      dropdownContent.style.borderRadius = '0.375rem';
      dropdownContent.style.overflow = 'hidden';
      dropdownContent.style.marginTop = '0.25rem';
      dropdownContent.style.right = '0';
      dropdownContent.style.display = 'none';  // Hidden by default
    }

    // Toggle dropdown visibility
    dropdownBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      // Toggle between hiding and showing
      if (dropdownContent.style.display === 'block') {
        dropdownContent.style.display = 'none';
      } else {
        dropdownContent.style.display = 'block';

        // Style each dropdown item
        const items = dropdownContent.querySelectorAll('.dropdown-item');
        items.forEach(item => {
          item.style.display = 'block';
          item.style.padding = '10px 16px';
          item.style.textDecoration = 'none';
          item.style.color = '#374151';
          item.style.borderBottom = '1px solid #e5e7eb';

          // Hover effect
          item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f3f4f6';
          });
          item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '#fff';
          });
        });
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!accountDropdown.contains(e.target)) {
        dropdownContent.style.display = 'none';
      }
    });
  }

  // TODO: Implement proper user session check using Supabase client
  // Example (needs integration with supabase-client.js and UI updates):
  /*
  import { auth } from '../static/js/supabase-client.js'; // Adjust path if needed

  async function checkAuthStatus() {
    const session = await auth.getSession();
    const user = await auth.getUser();
    const apiStatusElements = document.querySelectorAll('#api-status-text');
    const apiStatusValues = document.querySelectorAll('.api-status');

    if (session && user) {
      console.log('User logged in:', user.email);
      // Update UI to show logged-in state (e.g., show user email, logout button)
      apiStatusElements.forEach(element => {
        element.textContent = `Logged in as ${user.email}`;
        element.classList.remove('text-red-500');
        element.classList.add('text-green-500');
      });
      apiStatusValues.forEach(element => {
        element.textContent = 'Connected';
      });
    } else {
      console.log('User not logged in.');
      // Update UI to show logged-out state (e.g., show login button)
       apiStatusElements.forEach(element => {
        element.textContent = 'Not logged in';
        element.classList.remove('text-green-500');
        element.classList.add('text-red-500'); // Or neutral color
      });
       apiStatusValues.forEach(element => {
        element.textContent = 'Disconnected';
      });
    }
  }
  checkAuthStatus();

  // Listen for auth state changes
  supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event, session);
    checkAuthStatus(); // Re-check status on change
  });
  */

  // Handle mobile menu
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');
  if (mobileMenuToggle && mobileNav) {
    mobileMenuToggle.addEventListener('click', function() {
      mobileNav.classList.toggle('hidden');
    });
  }

  // Initialize tabs if present
  const tabButtons = document.querySelectorAll('.tabs-nav .tab-button');
  const tabContents = document.querySelectorAll('.tabs-content .tab-content');
  if (tabButtons.length > 0 && tabContents.length > 0) {
    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        const tab = button.getAttribute('data-tab');
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.add('hidden'));
        button.classList.add('active');
        document.getElementById(tab + '-tab').classList.remove('hidden');
      });
    });
  }

  // Handle report generation - TODO: Replace alert with actual API call using auth token
  const generateReportBtn = document.getElementById('generate-report-btn');
  if (generateReportBtn) {
    generateReportBtn.addEventListener('click', async function() {
      // Example: Fetch session/token before making API call
      // const session = await auth.getSession();
      // if (session) {
      //   const token = session.access_token;
      //   // Make API call to backend report endpoint with token
      //   console.log("Attempting report generation with token:", token);
           alert("Report generation feature needs backend integration.");
      // } else {
      //   alert("You must be logged in to generate reports.");
      // }
    });
  }

  // Handle logout - TODO: Integrate with Supabase signout
  const logoutBtn = document.getElementById('logout-btn'); // Assuming this ID exists on a logout button
  const logoutBtnMobile = document.getElementById('logout-btn-mobile'); // Assuming this ID exists

  async function handleLogout() {
      // Example: Call Supabase signout
      // const { error } = await auth.signOut();
      // if (error) {
      //   console.error('Error logging out:', error);
      //   alert('Logout failed. Please try again.');
      // } else {
           alert('You have been logged out.'); // Placeholder
           // Clear any local session info if needed
           // localStorage.removeItem(window.LOCALLIFT_CONFIG.AUTH.TOKEN_KEY);
           window.location.href = '/'; // Redirect to home
      // }
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  if (logoutBtnMobile) {
    logoutBtnMobile.addEventListener('click', handleLogout);
  }

});

// Initialize engagement chart if available
function initializeEngagementChart() {
  const engagementChartCanvas = document.getElementById('engagement-chart');
  if (engagementChartCanvas && typeof Chart !== 'undefined') {
    const ctx = engagementChartCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Engagement',
          data: [12, 19, 3, 5, 2, 3, 7],
          backgroundColor: 'rgba(0, 118, 255, 0.2)',
          borderColor: 'rgba(0, 118, 255, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  } else if (engagementChartCanvas) {
    console.warn("Chart.js library is not loaded. Engagement chart is not available.");
  }
}

// Call chart initialization after DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  // Attempt to initialize chart with a slight delay to ensure DOM is fully ready
  setTimeout(initializeEngagementChart, 100);
});
