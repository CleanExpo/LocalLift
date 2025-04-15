/**
 * Badge Admin Dashboard JavaScript
 * 
 * This script provides interactive functionality for the badge admin dashboard,
 * including data loading, filtering, and visualization.
 */

// Global state to track dashboard data and filters
const state = {
  timeframe: 'all',
  region: '',
  leaderboardData: [],
  regionalData: [],
  weeklyTrendData: []
};

// Chart instances
let weeklyTrendChart = null;
let regionalChart = null;

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Load initial data
  loadLeaderboardData();
  loadDashboardStats();
  
  // Set up UI interactions
  setupEventListeners();
  initializeCharts();
});

/**
 * Load the badge leaderboard data and populate the table
 */
async function loadLeaderboardData() {
  try {
    // Show loading state
    const tableBody = document.getElementById("badge-rows");
    tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4">Loading data...</td></tr>';
    
    // Apply filters if set
    let url = "/api/admin/badges/leaderboard";
    const params = new URLSearchParams();
    
    if (state.timeframe !== 'all') {
      params.append('timeframe', state.timeframe);
    }
    
    if (state.region) {
      params.append('region', state.region);
    }
    
    if (params.toString()) {
      url += '?' + params.toString();
    }
    
    // Fetch data from API
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to load leaderboard: ${response.status}`);
    }
    
    const data = await response.json();
    state.leaderboardData = data;
    
    // Clear and populate table
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4">No badge data available</td></tr>';
      return;
    }
    
    // Populate table rows
    data.forEach(client => {
      const row = document.createElement('tr');
      const lastBadgeDate = client.last_earned ? new Date(client.last_earned).toLocaleDateString() : 'Never';
      
      row.innerHTML = `
        <td class="px-4 py-2 border">${client.rank || '-'}</td>
        <td class="px-4 py-2 border">${client.client_name || client.client_email}</td>
        <td class="px-4 py-2 border">${client.region || 'Unknown'}</td>
        <td class="px-4 py-2 border">${client.badge_count}</td>
        <td class="px-4 py-2 border">${client.streak || 0}</td>
        <td class="px-4 py-2 border">${lastBadgeDate}</td>
        <td class="px-4 py-2 border">
          <button 
            class="text-blue-600 hover:text-blue-800 recalc-btn"
            data-client-id="${client.client_id}"
            data-client-name="${client.client_name || client.client_email}"
          >
            Recalculate
          </button>
        </td>
      `;
      
      tableBody.appendChild(row);
    });
    
    // Add event listeners to recalculate buttons
    document.querySelectorAll('.recalc-btn').forEach(btn => {
      btn.addEventListener('click', openRecalculateModal);
    });
    
  } catch (error) {
    console.error('Error loading leaderboard:', error);
    document.getElementById("badge-rows").innerHTML = 
      `<tr><td colspan="7" class="text-center py-4 text-red-500">
        Error loading data: ${error.message}
      </td></tr>`;
  }
}

/**
 * Load dashboard summary statistics
 */
async function loadDashboardStats() {
  try {
    const response = await fetch(`/api/admin/badges/statistics?timeframe=${state.timeframe}`);
    
    if (!response.ok) {
      throw new Error(`Failed to load statistics: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update dashboard metrics
    document.getElementById("total-badges").textContent = data.total_badges_earned || 0;
    document.getElementById("active-clients").textContent = data.clients_with_badges || 0;
    document.getElementById("weekly-rate").textContent = `${data.current_week_completion || 0}%`;
    
    // Also fetch region data for the chart
    await loadRegionalData();
    await loadWeeklyTrendData();
    
  } catch (error) {
    console.error('Error loading statistics:', error);
  }
}

/**
 * Load regional performance data
 */
async function loadRegionalData() {
  try {
    const response = await fetch(`/api/admin/badges/by-region?timeframe=${state.timeframe}`);
    
    if (!response.ok) {
      throw new Error(`Failed to load regional data: ${response.status}`);
    }
    
    const data = await response.json();
    state.regionalData = data.regions || [];
    
    // Update the region filter dropdown
    const regionFilter = document.getElementById('region-filter');
    
    // Keep the "All Regions" option
    regionFilter.innerHTML = '<option value="">All Regions</option>';
    
    // Add options for each region
    if (state.regionalData.length > 0) {
      state.regionalData.forEach(region => {
        const option = document.createElement('option');
        option.value = region.name;
        option.textContent = region.name;
        regionFilter.appendChild(option);
      });
    }
    
    // Update the regional chart
    updateRegionalChart();
    
  } catch (error) {
    console.error('Error loading regional data:', error);
  }
}

/**
 * Load weekly trend data
 */
async function loadWeeklyTrendData() {
  try {
    const response = await fetch('/api/admin/badges/trends?weeks=12');
    
    if (!response.ok) {
      throw new Error(`Failed to load trend data: ${response.status}`);
    }
    
    const data = await response.json();
    state.weeklyTrendData = data.trends || [];
    
    // Update the weekly trend chart
    updateWeeklyTrendChart();
    
  } catch (error) {
    console.error('Error loading trend data:', error);
  }
}

/**
 * Set up event listeners for interactive components
 */
function setupEventListeners() {
  // Timeframe selector
  const timeframeSelect = document.getElementById('timeframe-select');
  if (timeframeSelect) {
    timeframeSelect.addEventListener('change', (e) => {
      state.timeframe = e.target.value;
      loadDashboardData();
    });
  }
  
  // Refresh button
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      loadDashboardData();
    });
  }
  
  // Non-compliant client analysis
  const analyzeBtn = document.getElementById('analyze-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', loadNonCompliantData);
  }
  
  // Modal actions
  const cancelRecalcBtn = document.getElementById('cancel-recalc');
  if (cancelRecalcBtn) {
    cancelRecalcBtn.addEventListener('click', closeRecalculateModal);
  }
  
  const confirmRecalcBtn = document.getElementById('confirm-recalc');
  if (confirmRecalcBtn) {
    confirmRecalcBtn.addEventListener('click', recalculateBadge);
  }
}

/**
 * Set up the tab navigation
 */
function setupTabs() {
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs and contents
      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      
      // Add active class to current tab and content
      tab.classList.add('active');
      const tabId = tab.getAttribute('data-tab');
      document.getElementById(tabId).classList.add('active');
      
      state.activeTab = tabId;
      
      // Load tab-specific data if needed
      if (tabId === 'non-compliant') {
        loadNonCompliantData();
      }
    });
  });
}

/**
 * Load all dashboard data based on the selected timeframe
 */
function loadDashboardData() {
  // Show loading state
  updateLoadingState(true);
  
  // Load global statistics
  fetch(`/api/admin/badges/statistics?timeframe=${state.timeframe}`)
    .then(response => response.json())
    .then(data => {
      updateOverviewMetrics(data);
    })
    .catch(error => {
      console.error('Error fetching badge statistics:', error);
    });
  
  // Load trends data
  fetch('/api/admin/badges/trends?weeks=12')
    .then(response => response.json())
    .then(data => {
      state.trendsData = data.trends;
      updateTrendsChart();
      updateTrendsTable();
    })
    .catch(error => {
      console.error('Error fetching badge trends:', error);
    });
  
  // Load regional data
  fetch(`/api/admin/badges/by-region?timeframe=${state.timeframe}`)
    .then(response => response.json())
    .then(data => {
      state.regionData = data.regions;
      updateRegionsChart();
      updateRegionsTable();
    })
    .catch(error => {
      console.error('Error fetching regional statistics:', error);
    });
  
  // Load client leaderboard
  fetch(`/api/leaderboard`)
    .then(response => response.json())
    .then(data => {
      state.clientData = data;
      updateClientsTable();
    })
    .catch(error => {
      console.error('Error fetching leaderboard:', error);
    })
    .finally(() => {
      updateLoadingState(false);
    });
}

/**
 * Load non-compliant clients data
 */
function loadNonCompliantData() {
  const weeksThreshold = document.getElementById('weeks-threshold').value;
  const complianceThreshold = document.getElementById('compliance-threshold').value;
  
  fetch(`/api/admin/badges/non-compliant-clients?weeks_threshold=${weeksThreshold}&compliance_threshold=${complianceThreshold}`)
    .then(response => response.json())
    .then(data => {
      updateNonCompliantTable(data.clients);
    })
    .catch(error => {
      console.error('Error fetching non-compliant clients:', error);
    });
}

/**
 * Update the overview metrics cards
 */
function updateOverviewMetrics(data) {
  // Update total badges
  const totalBadgesEl = document.getElementById('total-badges');
  if (totalBadgesEl) {
    totalBadgesEl.textContent = data.total_badges_earned || 0;
  }
  
  // Update compliance rate
  const complianceRateEl = document.getElementById('compliance-rate');
  if (complianceRateEl) {
    complianceRateEl.textContent = `${data.compliance_rate || 0}%`;
  }
  
  // Update participation rate
  const participationRateEl = document.getElementById('participation-rate');
  if (participationRateEl) {
    participationRateEl.textContent = `${data.client_participation_rate || 0}%`;
  }
  
  // Update current week completion
  const currentWeekEl = document.getElementById('current-week');
  if (currentWeekEl) {
    currentWeekEl.textContent = `${data.current_week_completion || 0}%`;
  }
}

/**
 * Update the badge earning trends chart
 */
function updateTrendsChart() {
  const ctx = document.getElementById('trends-chart');
  if (!ctx) return;
  
  // Prepare chart data
  const weeks = state.trendsData.map(item => item.date_range);
  const badgeRates = state.trendsData.map(item => item.badge_rate || 0);
  const complianceRates = state.trendsData.map(item => item.compliance_rate || 0);
  
  // Destroy existing chart if it exists
  if (trendsChart) {
    trendsChart.destroy();
  }
  
  // Create new chart
  trendsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: weeks,
      datasets: [
        {
          label: 'Badge Earning Rate',
          data: badgeRates,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.2,
          fill: true
        },
        {
          label: 'Compliance Rate',
          data: complianceRates,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.2,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%';
            }
          }
        }
      }
    }
  });
}

/**
 * Update the trends data table
 */
function updateTrendsTable() {
  const table = document.getElementById('trends-table');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  if (state.trendsData.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="6" class="text-center py-4">No data available</td>`;
    tbody.appendChild(row);
    return;
  }
  
  state.trendsData.forEach(week => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${week.date_range}</td>
      <td>${week.badges_earned}</td>
      <td>${week.total_clients}</td>
      <td>${week.badge_rate || 0}%</td>
      <td>${week.compliance_rate || 0}%</td>
      <td>${week.total_posts}</td>
    `;
    tbody.appendChild(row);
  });
}

/**
 * Update the regions chart
 */
function updateRegionsChart() {
  const ctx = document.getElementById('regions-chart');
  if (!ctx) return;
  
  // Prepare chart data
  const regions = state.regionData.map(item => item.name);
  const badges = state.regionData.map(item => item.total_badges);
  const clients = state.regionData.map(item => item.total_clients);
  
  // Generate colors based on the number of regions
  const backgroundColors = generateColors(regions.length);
  
  // Destroy existing chart if it exists
  if (regionsChart) {
    regionsChart.destroy();
  }
  
  // Create new chart
  regionsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: regions,
      datasets: [
        {
          label: 'Total Badges',
          data: badges,
          backgroundColor: backgroundColors,
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            afterLabel: function(context) {
              const index = context.dataIndex;
              return `${clients[index]} clients in region`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Badges'
          }
        }
      }
    }
  });
}

/**
 * Update the regions data table
 */
function updateRegionsTable() {
  const table = document.getElementById('regions-table');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  if (state.regionData.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="5" class="text-center py-4">No data available</td>`;
    tbody.appendChild(row);
    return;
  }
  
  state.regionData.forEach(region => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${region.name}</td>
      <td>${region.total_badges}</td>
      <td>${region.total_clients}</td>
      <td>${region.participation_rate}%</td>
      <td>${region.avg_badges_per_client}</td>
    `;
    tbody.appendChild(row);
  });
  
  // Update region filter options
  const regionFilter = document.getElementById('region-filter');
  if (regionFilter) {
    // Keep the first "All Regions" option
    regionFilter.innerHTML = '<option value="">All Regions</option>';
    
    // Add an option for each region
    state.regionData.forEach(region => {
      const option = document.createElement('option');
      option.value = region.name;
      option.textContent = region.name;
      regionFilter.appendChild(option);
    });
  }
}

/**
 * Update the clients data table
 */
function updateClientsTable() {
  const table = document.getElementById('clients-table');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  if (state.clientData.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="6" class="text-center py-4">No data available</td>`;
    tbody.appendChild(row);
    return;
  }
  
  // Get client search and region filter values
  const searchTerm = document.getElementById('client-search')?.value?.toLowerCase() || '';
  const selectedRegion = document.getElementById('region-filter')?.value || '';
  
  // Filter and map client data
  state.clientData
    .filter(client => {
      const matchesSearch = client.client_name?.toLowerCase().includes(searchTerm);
      const matchesRegion = !selectedRegion || client.region === selectedRegion;
      return matchesSearch && matchesRegion;
    })
    .forEach(client => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${client.rank || '--'}</td>
        <td>${client.client_name || 'Unknown'}</td>
        <td>${client.region || 'Unknown'}</td>
        <td>${client.badge_count || 0}</td>
        <td>${client.compliance_rate || 0}%</td>
        <td>
          <button 
            class="text-blue-600 hover:text-blue-800 recalc-btn"
            data-client-id="${client.client_id}"
            data-client-name="${client.client_name || 'Unknown'}"
          >
            Recalculate
          </button>
        </td>
      `;
      tbody.appendChild(row);
    });
  
  // Add event listeners for recalculate buttons
  const recalcButtons = document.querySelectorAll('.recalc-btn');
  recalcButtons.forEach(btn => {
    btn.addEventListener('click', openRecalculateModal);
  });
  
  // Add event listeners for search and filter
  const clientSearch = document.getElementById('client-search');
  if (clientSearch) {
    clientSearch.addEventListener('input', updateClientsTable);
  }
  
  const regionFilter = document.getElementById('region-filter');
  if (regionFilter) {
    regionFilter.addEventListener('change', updateClientsTable);
  }
}

/**
 * Update the non-compliant clients table
 */
function updateNonCompliantTable(clients) {
  const table = document.getElementById('non-compliant-table');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  if (!clients || clients.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="6" class="text-center py-4">No non-compliant clients found</td>`;
    tbody.appendChild(row);
    return;
  }
  
  clients.forEach(client => {
    const row = document.createElement('tr');
    const complianceClass = client.compliance_rate < 25 ? 'compliance-warning' : '';
    
    row.innerHTML = `
      <td>${client.name || 'Unknown'}</td>
      <td>${client.region || 'Unknown'}</td>
      <td class="${complianceClass}">${client.compliance_rate}%</td>
      <td>${client.badges_earned}/${client.weeks_tracked}</td>
      <td>${client.weeks_tracked}</td>
      <td>
        <button 
          class="text-blue-600 hover:text-blue-800 recalc-btn"
          data-client-id="${client.client_id}"
          data-client-name="${client.name || 'Unknown'}"
        >
          Recalculate
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });
  
  // Add event listeners for recalculate buttons
  const recalcButtons = document.querySelectorAll('.recalc-btn');
  recalcButtons.forEach(btn => {
    btn.addEventListener('click', openRecalculateModal);
  });
}

/**
 * Open the badge recalculation modal
 */
function openRecalculateModal(e) {
  const clientId = e.target.getAttribute('data-client-id');
  const clientName = e.target.getAttribute('data-client-name');
  
  // Set client info in modal
  document.getElementById('recalc-client-name').textContent = clientName;
  
  // Populate week dropdown with last 12 weeks
  const weekSelect = document.getElementById('recalc-week');
  weekSelect.innerHTML = '';
  
  // Get the last 12 weeks
  const now = new Date();
  for (let i = 0; i < 12; i++) {
    const weekDate = new Date(now);
    weekDate.setDate(now.getDate() - (i * 7));
    
    const year = weekDate.getFullYear();
    const weekNumber = getWeekNumber(weekDate);
    const weekId = `${year}-W${weekNumber.toString().padStart(2, '0')}`;
    
    const weekStart = new Date(weekDate);
    weekStart.setDate(weekDate.getDate() - weekDate.getDay() + 1);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    
    const formattedRange = `${formatDate(weekStart)} - ${formatDate(weekEnd)}`;
    const option = document.createElement('option');
    option.value = weekId;
    option.textContent = `${weekId} (${formattedRange})`;
    
    if (i === 0) {
      option.selected = true;
    }
    
    weekSelect.appendChild(option);
  }
  
  // Store client ID for recalculation
  weekSelect.setAttribute('data-client-id', clientId);
  
  // Clear previous results
  document.getElementById('recalc-result').classList.add('hidden');
  document.getElementById('recalc-result-content').innerHTML = '';
  
  // Show modal
  document.getElementById('recalculate-modal').classList.remove('hidden');
}

/**
 * Close the badge recalculation modal
 */
function closeRecalculateModal() {
  document.getElementById('recalculate-modal').classList.add('hidden');
}

/**
 * Recalculate badge for client and week
 */
function recalculateBadge() {
  const weekSelect = document.getElementById('recalc-week');
  const clientId = weekSelect.getAttribute('data-client-id');
  const weekId = weekSelect.value;
  
  // Show loading state
  const resultDiv = document.getElementById('recalc-result');
  const resultContent = document.getElementById('recalc-result-content');
  resultDiv.classList.remove('hidden');
  resultContent.innerHTML = 'Recalculating badge...';
  
  // Call API to recalculate
  fetch(`/api/admin/badges/recalculate/${clientId}/${weekId}`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(data => {
      // Show result
      resultContent.innerHTML = `
        <p><strong>Recalculation complete:</strong></p>
        <p>Badge earned: ${data.badge ? 'Yes ✅' : 'No ❌'}</p>
        <p>Compliant posts: ${data.compliant}/${data.total}</p>
      `;
      
      // Reload dashboard data after recalculation
      loadDashboardData();
    })
    .catch(error => {
      console.error('Error recalculating badge:', error);
      resultContent.innerHTML = `<p class="text-red-600">Error: ${error.message || 'Failed to recalculate'}</p>`;
    });
}

/**
 * Update loading state of tables
 */
function updateLoadingState(isLoading) {
  const loadingMessage = isLoading ? 'Loading data...' : 'No data available';
  
  // Update tables with loading state if they're empty
  const tables = ['trends-table', 'regions-table', 'clients-table', 'non-compliant-table'];
  tables.forEach(tableId => {
    const table = document.getElementById(tableId);
    if (table) {
      const tbody = table.querySelector('tbody');
      if (tbody.children.length === 1 && tbody.children[0].cells.length === 1) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4">${loadingMessage}</td></tr>`;
      }
    }
  });
}

// --- Utility Functions ---

/**
 * Generate an array of colors for charts
 */
function generateColors(count) {
  const baseColors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#f97316', // orange
  ];
  
  // If we have fewer colors than needed, repeat them
  const colors = [];
  for (let i = 0; i < count; i++) {
    colors.push(baseColors[i % baseColors.length]);
  }
  
  return colors;
}

/**
 * Get ISO week number for a date
 */
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
}

/**
 * Format date as MMM DD (e.g., Apr 15)
 */
function formatDate(date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[date.getMonth()]} ${date.getDate()}`;
}
