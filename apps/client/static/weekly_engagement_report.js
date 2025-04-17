// DOM elements
const generateReportBtn = document.getElementById('generate-report-btn');
const weekNumberEl = document.getElementById('week-number');
const yearEl = document.getElementById('year');
const dateRangeEl = document.getElementById('date-range');
const metricsGrid = document.getElementById('metrics-grid');
const insightsContainer = document.getElementById('insights-container');
const recommendationsContainer = document.getElementById('recommendations-container');
const historyTableBody = document.getElementById('history-table-body');
const loadingOverlay = document.getElementById('loading-overlay');

// Chart instances
let trafficChart = null;
let engagementChart = null;

// Current report data
let currentReport = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', init);

async function init() {
  showLoading();
  try {
    // Fetch report history
    await fetchReportHistory();
    
    // Generate or fetch the latest report
    await generateReport();
  } catch (error) {
    console.error('Error initializing page:', error);
    alert('An error occurred while loading the page. Please try again.');
  } finally {
    hideLoading();
  }

  // Add event listeners
  generateReportBtn.addEventListener('click', generateReport);
}

async function fetchReportHistory() {
  try {
    const response = await fetch('/api/client/engagement-reports/');
    const data = await response.json();
    
    if (data.status === 'success') {
      renderReportHistory(data.reports);
    } else {
      console.error('Error fetching report history:', data.message);
    }
  } catch (error) {
    console.error('Error fetching report history:', error);
  }
}

async function generateReport() {
  showLoading();
  try {
    const response = await fetch('/api/client/engagement-reports/generate');
    const data = await response.json();
    
    if (data.status === 'success') {
      currentReport = data.report;
      renderReport(currentReport);
      await fetchReportHistory(); // Refresh history after generating a new report
    } else {
      console.error('Error generating report:', data.message);
      alert('Failed to generate report. Please try again.');
    }
  } catch (error) {
    console.error('Error generating report:', error);
    alert('An error occurred while generating the report. Please try again.');
  } finally {
    hideLoading();
  }
}

async function fetchReportDetail(reportId) {
  showLoading();
  try {
    const response = await fetch(`/api/client/engagement-reports/${reportId}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      currentReport = data.report;
      renderReport(currentReport);
      await fetchReportHistory(); // Refresh history to update viewed status
    } else {
      console.error('Error fetching report detail:', data.message);
      alert('Failed to load report. Please try again.');
    }
  } catch (error) {
    console.error('Error fetching report detail:', error);
    alert('An error occurred while loading the report. Please try again.');
  } finally {
    hideLoading();
  }
}

function renderReport(report) {
  renderReportHeader(report);
  renderMetrics(report.metrics, report.trends);
  renderCharts(report.metrics, report.previous_metrics);
  renderInsights(report.insights);
  renderRecommendations(report.recommendations);
}

function renderReportHeader(report) {
  weekNumberEl.textContent = report.week_number;
  yearEl.textContent = report.year;
  
  // Format date range
  const startDate = new Date(report.period.start_date);
  const endDate = new Date(report.period.end_date);
  
  const formatOptions = { month: 'short', day: 'numeric' };
  const formattedStartDate = startDate.toLocaleDateString('en-US', formatOptions);
  const formattedEndDate = endDate.toLocaleDateString('en-US', formatOptions);
  
  dateRangeEl.textContent = `${formattedStartDate} - ${formattedEndDate}`;
}

function renderMetrics(metrics, trends) {
  // Clear existing metrics
  metricsGrid.innerHTML = '';
  
  // Define the metrics to display
  const keyMetrics = [
    { id: 'views', name: 'Profile Views', format: value => value.toLocaleString() },
    { id: 'clicks', name: 'Total Clicks', format: value => value.toLocaleString() },
    { id: 'calls', name: 'Phone Calls', format: value => value.toLocaleString() },
    { id: 'engagement_rate', name: 'Engagement Rate', format: value => value.toFixed(1) + '%' },
    { id: 'conversion_rate', name: 'Conversion Rate', format: value => value.toFixed(1) + '%' },
    { id: 'average_response_time', name: 'Avg. Response Time', format: value => value.toFixed(1) + ' hours' }
  ];
  
  // Create and append metric cards
  keyMetrics.forEach(metric => {
    const value = metrics[metric.id] || 0;
    const trend = trends[metric.id] || { direction: 'stable', change_percentage: 0 };
    
    const metricCard = document.createElement('div');
    metricCard.className = 'metric-card';
    
    let trendHtml = '';
    if (trend.direction === 'up') {
      trendHtml = `<div class="metrics-trend trend-up">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        ${Math.abs(trend.change_percentage).toFixed(1)}%
      </div>`;
    } else if (trend.direction === 'down') {
      trendHtml = `<div class="metrics-trend trend-down">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        ${Math.abs(trend.change_percentage).toFixed(1)}%
      </div>`;
    } else {
      trendHtml = `<div class="metrics-trend trend-stable">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a1 1 0 01-1 1H3a1 1 0 110-2h14a1 1 0 011 1z" clip-rule="evenodd" />
        </svg>
        No change
      </div>`;
    }
    
    metricCard.innerHTML = `
      <div class="metric-value">${metric.format(value)}</div>
      <div class="metric-name">${metric.name}</div>
      ${trendHtml}
    `;
    
    metricsGrid.appendChild(metricCard);
  });
}

function renderCharts(currentMetrics, previousMetrics) {
  // Destroy existing charts if they exist
  if (trafficChart) {
    trafficChart.destroy();
  }
  if (engagementChart) {
    engagementChart.destroy();
  }
  
  // Traffic Chart - showing views, clicks, calls, direction requests
  const trafficCtx = document.getElementById('traffic-chart').getContext('2d');
  trafficChart = new Chart(trafficCtx, {
    type: 'bar',
    data: {
      labels: ['Views', 'Clicks', 'Calls', 'Direction Requests', 'Messages'],
      datasets: [
        {
          label: 'Previous Week',
          data: [
            previousMetrics.views || 0,
            previousMetrics.clicks || 0,
            previousMetrics.calls || 0,
            previousMetrics.direction_requests || 0,
            previousMetrics.messages || 0
          ],
          backgroundColor: 'rgba(156, 163, 175, 0.5)',
          borderColor: 'rgba(156, 163, 175, 1)',
          borderWidth: 1
        },
        {
          label: 'Current Week',
          data: [
            currentMetrics.views || 0,
            currentMetrics.clicks || 0,
            currentMetrics.calls || 0,
            currentMetrics.direction_requests || 0,
            currentMetrics.messages || 0
          ],
          backgroundColor: 'rgba(79, 70, 229, 0.5)',
          borderColor: 'rgba(79, 70, 229, 1)',
          borderWidth: 1
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
        title: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toLocaleString();
              }
              return label;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
  
  // Engagement Chart - showing engagement rate, conversion rate
  const engagementCtx = document.getElementById('engagement-chart').getContext('2d');
  engagementChart = new Chart(engagementCtx, {
    type: 'line',
    data: {
      labels: ['Engagement Rate', 'Conversion Rate'],
      datasets: [
        {
          label: 'Previous Week',
          data: [
            previousMetrics.engagement_rate || 0,
            previousMetrics.conversion_rate || 0
          ],
          backgroundColor: 'rgba(156, 163, 175, 0.5)',
          borderColor: 'rgba(156, 163, 175, 1)',
          borderWidth: 2,
          fill: false,
          tension: 0.1
        },
        {
          label: 'Current Week',
          data: [
            currentMetrics.engagement_rate || 0,
            currentMetrics.conversion_rate || 0
          ],
          backgroundColor: 'rgba(79, 70, 229, 0.5)',
          borderColor: 'rgba(79, 70, 229, 1)',
          borderWidth: 2,
          fill: false,
          tension: 0.1
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
        title: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(1) + '%';
              }
              return label;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
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

function renderInsights(insights) {
  // Clear existing insights
  insightsContainer.innerHTML = '';
  
  // Create and append insight cards
  insights.forEach(insight => {
    const insightCard = document.createElement('div');
    insightCard.className = `insight-card ${insight.type}`;
    
    insightCard.innerHTML = `
      <span class="category-badge ${insight.category}">${insight.category}</span>
      <h3 class="insight-title">${insight.title}</h3>
      <p class="insight-description">${insight.description}</p>
    `;
    
    insightsContainer.appendChild(insightCard);
  });
  
  // If no insights, show a message
  if (!insights || insights.length === 0) {
    insightsContainer.innerHTML = '<p class="text-gray-500">No insights available for this period.</p>';
  }
}

function renderRecommendations(recommendations) {
  // Clear existing recommendations
  recommendationsContainer.innerHTML = '';
  
  // Create and append recommendation cards
  recommendations.forEach(recommendation => {
    const recommendationCard = document.createElement('div');
    recommendationCard.className = 'recommendation-card';
    
    let actionItems = '';
    if (recommendation.actions && recommendation.actions.length > 0) {
      actionItems = '<ul class="actions-list">';
      recommendation.actions.forEach(action => {
        actionItems += `
          <li class="action-item">
            <span class="action-icon">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </span>
            <span class="action-text">${action}</span>
          </li>
        `;
      });
      actionItems += '</ul>';
    }
    
    recommendationCard.innerHTML = `
      <div class="recommendation-header">
        <span class="recommendation-icon">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </span>
        <h3 class="recommendation-title">${recommendation.title}</h3>
      </div>
      <p class="recommendation-description">${recommendation.description}</p>
      ${actionItems}
    `;
    
    recommendationsContainer.appendChild(recommendationCard);
  });
  
  // If no recommendations, show a message
  if (!recommendations || recommendations.length === 0) {
    recommendationsContainer.innerHTML = '<p class="text-gray-500">No recommendations available for this period.</p>';
  }
}

function renderReportHistory(reports) {
  // Clear existing history
  historyTableBody.innerHTML = '';
  
  // Sort reports by date (newest first)
  const sortedReports = reports.sort((a, b) => {
    if (a.year !== b.year) {
      return b.year - a.year;
    }
    return b.week_number - a.week_number;
  });
  
  // Create and append history rows
  sortedReports.forEach(report => {
    const row = document.createElement('tr');
    
    // Format period dates
    const startDate = new Date(report.period.start_date);
    const endDate = new Date(report.period.end_date);
    
    const formatOptions = { month: 'short', day: 'numeric' };
    const formattedStartDate = startDate.toLocaleDateString('en-US', formatOptions);
    const formattedEndDate = endDate.toLocaleDateString('en-US', formatOptions);
    
    // Get key metrics
    const views = report.key_metrics?.views || 0;
    const engagementRate = report.key_metrics?.engagement_rate || 0;
    
    // Create row content
    row.innerHTML = `
      <td>Week ${report.week_number}, ${report.year}</td>
      <td>${formattedStartDate} - ${formattedEndDate}</td>
      <td>${views.toLocaleString()}</td>
      <td>${engagementRate.toFixed(1)}%</td>
      <td>
        <span class="status-badge ${report.viewed ? 'viewed' : 'unviewed'}">
          ${report.viewed ? 'Viewed' : 'New'}
        </span>
      </td>
      <td>
        <button class="view-report-btn" data-report-id="${report.id}">
          View Report
        </button>
      </td>
    `;
    
    // Add event listener to view report button
    const viewButton = row.querySelector('.view-report-btn');
    viewButton.addEventListener('click', () => {
      fetchReportDetail(report.id);
    });
    
    historyTableBody.appendChild(row);
  });
  
  // If no reports, show a message
  if (!sortedReports || sortedReports.length === 0) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = `
      <td colspan="6" class="text-center py-4 text-gray-500">
        No report history available. Generate your first report above.
      </td>
    `;
    historyTableBody.appendChild(emptyRow);
  }
}

// Helper functions
function showLoading() {
  loadingOverlay.style.display = 'flex';
}

function hideLoading() {
  loadingOverlay.style.display = 'none';
}
