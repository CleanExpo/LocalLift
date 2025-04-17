// LocalLift main JavaScript file

// Load configuration and authenticate user
document.addEventListener('DOMContentLoaded', function() {
  console.log('LocalLift application initialized');
  
  // Check for developer credentials
  fetch('/developer_credentials.json')
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Developer credentials not found');
      }
    })
    .then(data => {
      console.log('Developer account connected:', data.username);
      // Update all API status indicators
      const apiStatusElements = document.querySelectorAll('#api-status-text');
      apiStatusElements.forEach(element => {
        element.textContent = 'Developer account connected';
        element.classList.remove('text-red-500');
        element.classList.add('text-green-500');
      });
      
      // Update API status values
      const apiStatusValues = document.querySelectorAll('.api-status');
      apiStatusValues.forEach(element => {
        element.textContent = 'Connected';
      });
    })
    .catch(error => {
      console.error('Error loading developer credentials:', error);
      // Update status to show error
      const apiStatusElements = document.querySelectorAll('#api-status-text');
      apiStatusElements.forEach(element => {
        element.textContent = 'Backend integration disabled';
        element.classList.remove('text-green-500');
        element.classList.add('text-red-500');
      });
    });
  
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
  
  // Handle report generation
  const generateReportBtn = document.getElementById('generate-report-btn');
  if (generateReportBtn) {
    generateReportBtn.addEventListener('click', function() {
      // Check if we have developer credentials first
      fetch('/developer_credentials.json')
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error('Developer credentials not found');
          }
        })
        .then(data => {
          // We have credentials, so show a success message
          alert("Report generation started for " + data.username);
        })
        .catch(error => {
          // No credentials, show the error message
          alert("Report generation is currently disabled due to backend integration issues.");
        });
    });
  }
  
  // Handle logout
  const logoutBtn = document.getElementById('logout-btn');
  const logoutBtnMobile = document.getElementById('logout-btn-mobile');
  
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function() {
      alert('You have been logged out.');
      window.location.href = '/';
    });
  }
  
  if (logoutBtnMobile) {
    logoutBtnMobile.addEventListener('click', function() {
      alert('You have been logged out.');
      window.location.href = '/';
    });
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
