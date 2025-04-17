/**
 * GMB Post Tracker JavaScript
 * Client dashboard widget showing GMB post engagement, badge status, and compliance timeline
 */

// Main controller for the post tracker widget
class PostTrackerWidget {
  constructor(clientId) {
    this.clientId = clientId || 'default';
    this.data = null;
    this.chart = null;
    this.initialized = false;
    
    // Bind event handlers
    document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData());
    
    // Initialize the widget
    this.initialize();
  }
  
  async initialize() {
    try {
      this.showLoading(true);
      await this.fetchData();
      this.renderWidgets();
      this.initialized = true;
      this.showLoading(false);
    } catch (error) {
      console.error('Failed to initialize post tracker:', error);
      this.showError('Failed to load post tracker data. Please try again later.');
    }
  }
  
  async fetchData() {
    try {
      const response = await fetch(`/api/post-tracker/${this.clientId}`);
      
      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`);
      }
      
      this.data = await response.json();
      console.log('Fetched post tracker data:', this.data);
      return this.data;
    } catch (error) {
      console.error('Error fetching post tracker data:', error);
      throw error;
    }
  }
  
  async refreshData() {
    try {
      this.showLoading(true);
      await this.fetchData();
      this.renderWidgets();
      this.showLoading(false);
      
      // Show success message
      this.showNotification('Data refreshed successfully!', 'success');
    } catch (error) {
      console.error('Failed to refresh data:', error);
      this.showNotification('Failed to refresh data. Please try again.', 'error');
      this.showLoading(false);
    }
  }
  
  renderWidgets() {
    if (!this.data) return;
    
    this.renderPostEngagement();
    this.renderBadgeStatus();
    this.renderComplianceStatus();
  }
  
  renderPostEngagement() {
    // Render engagement chart
    this.renderEngagementChart();
    
    // Render recent posts
    const postsContainer = document.getElementById('recent-posts-container');
    postsContainer.innerHTML = '';
    
    const recentPosts = this.data.post_engagement.recent_posts || [];
    const scheduledPosts = this.data.post_engagement.scheduled_posts || [];
    
    if (recentPosts.length === 0 && scheduledPosts.length === 0) {
      postsContainer.innerHTML = `
        <div class="bg-gray-50 p-4 rounded-lg text-center text-gray-500">
          No posts available. Create your first GMB post to get started!
        </div>
      `;
      return;
    }
    
    // Render recent published posts
    recentPosts.forEach(post => {
      const postDate = new Date(post.date);
      
      const postElement = document.createElement('div');
      postElement.className = 'post-card bg-white border border-gray-200 p-4 rounded-lg';
      postElement.innerHTML = `
        <div class="flex justify-between mb-2">
          <span class="text-sm font-medium text-indigo-600">${postDate.toLocaleDateString()}</span>
          <span class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">${post.status}</span>
        </div>
        <p class="text-gray-700 mb-3 text-sm">${post.content}</p>
        <div class="flex justify-between text-sm">
          <span class="flex items-center text-gray-500">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            ${post.views} views
          </span>
          <span class="flex items-center text-gray-500">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            ${post.clicks} clicks
          </span>
        </div>
      `;
      
      postsContainer.appendChild(postElement);
    });
    
    // Render scheduled posts if any
    scheduledPosts.forEach(post => {
      const scheduleDate = new Date(post.scheduled_date);
      
      const postElement = document.createElement('div');
      postElement.className = 'post-card bg-blue-50 border border-blue-200 p-4 rounded-lg';
      postElement.innerHTML = `
        <div class="flex justify-between mb-2">
          <span class="text-sm font-medium text-blue-600">Scheduled for ${scheduleDate.toLocaleDateString()}</span>
          <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">${post.status}</span>
        </div>
        <p class="text-gray-700 mb-2 text-sm">${post.content}</p>
      `;
      
      postsContainer.appendChild(postElement);
    });
  }
  
  renderEngagementChart() {
    const ctx = document.getElementById('engagement-chart').getContext('2d');
    
    const engagementData = this.data.post_engagement.engagement_trend;
    
    if (!engagementData || !engagementData.dates || !engagementData.views || !engagementData.clicks) {
      return;
    }
    
    // Destroy existing chart if any
    if (this.chart) {
      this.chart.destroy();
    }
    
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: engagementData.dates,
        datasets: [
          {
            label: 'Views',
            data: engagementData.views,
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            borderColor: 'rgba(79, 70, 229, 1)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: 'rgba(79, 70, 229, 1)'
          },
          {
            label: 'Clicks',
            data: engagementData.clicks,
            backgroundColor: 'rgba(245, 158, 11, 0.2)',
            borderColor: 'rgba(245, 158, 11, 1)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: 'rgba(245, 158, 11, 1)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            position: 'top'
          }
        }
      }
    });
  }
  
  renderBadgeStatus() {
    if (!this.data.badge_status) return;
    
    // Render earned badges
    const badgesContainer = document.getElementById('badges-container');
    badgesContainer.innerHTML = '';
    
    const earnedBadges = this.data.badge_status.earned_badges || [];
    const badgeIcons = {
      'consistent_poster': '📝',
      'engagement_pro': '👍',
      'quick_responder': '⚡',
      'content_creator': '🎨',
      'local_expert': '🏆'
    };
    
    if (earnedBadges.length === 0) {
      badgesContainer.innerHTML = `
        <div class="text-center py-3 text-gray-500">
          No badges earned yet. Complete actions to earn badges!
        </div>
      `;
    } else {
      earnedBadges.forEach(badge => {
        const badgeElement = document.createElement('div');
        badgeElement.className = 'badge-item flex items-center space-x-3 pl-3 py-2';
        badgeElement.innerHTML = `
          <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-lg">
            ${badgeIcons[badge] || '🔶'}
          </div>
          <div>
            <div class="font-medium">${this.formatBadgeName(badge)}</div>
            <div class="text-sm text-gray-500">Earned</div>
          </div>
        `;
        
        badgesContainer.appendChild(badgeElement);
      });
    }
    
    // Render badge progress
    const progressContainer = document.getElementById('badge-progress-container');
    progressContainer.innerHTML = '';
    
    const progressBadges = this.data.badge_status.progress || {};
    
    Object.entries(progressBadges).forEach(([badge, progress]) => {
      const progressElement = document.createElement('div');
      progressElement.className = 'mb-4';
      progressElement.innerHTML = `
        <div class="flex justify-between items-center mb-1">
          <div class="font-medium">${this.formatBadgeName(badge)}</div>
          <div class="text-xs font-medium">${progress.progress}%</div>
        </div>
        <div class="text-xs text-gray-500 mb-2">${progress.requirements}</div>
        <div class="badge-progress">
          <div class="badge-progress-bar" style="width: ${progress.progress}%"></div>
        </div>
      `;
      
      progressContainer.appendChild(progressElement);
    });
  }
  
  renderComplianceStatus() {
    if (!this.data.compliance) return;
    
    // Render compliance status
    const complianceContainer = document.getElementById('compliance-status');
    const complianceData = this.data.compliance;
    
    // Determine status level
    let statusClass = 'compliance-good';
    let statusIcon = '✅';
    
    if (complianceData.score < 70) {
      statusClass = 'compliance-danger';
      statusIcon = '❌';
    } else if (complianceData.score < 90) {
      statusClass = 'compliance-warning';
      statusIcon = '⚠️';
    }
    
    complianceContainer.innerHTML = `
      <div class="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
        <div class="text-3xl ${statusClass}">${statusIcon}</div>
        <div>
          <div class="text-lg font-medium ${statusClass}">
            ${complianceData.score}% - ${complianceData.status.toUpperCase()}
          </div>
          <div class="text-sm text-gray-500">
            Last updated: ${new Date(this.data.last_updated).toLocaleDateString()}
          </div>
        </div>
      </div>
    `;
    
    // Render compliance timeline
    const timelineContainer = document.getElementById('compliance-timeline');
    timelineContainer.innerHTML = '';
    
    const timeline = complianceData.timeline || [];
    
    if (timeline.length === 0) {
      timelineContainer.innerHTML = `
        <div class="text-center py-3 text-gray-500">
          No compliance events recorded yet.
        </div>
      `;
      return;
    }
    
    // Create a timeline element for each event
    timeline.forEach(event => {
      const eventDate = new Date(event.date);
      
      const timelineElement = document.createElement('div');
      timelineElement.className = 'timeline-item pb-5';
      
      let eventItems = '';
      event.events.forEach(item => {
        eventItems += `<li class="text-sm">${item}</li>`;
      });
      
      timelineElement.innerHTML = `
        <div class="timeline-marker"></div>
        <div class="mb-1 text-sm font-medium">${eventDate.toLocaleDateString()}</div>
        <div class="mb-2 text-xs text-gray-500">Score: ${event.score}%</div>
        <ul class="ml-2 list-disc list-inside text-gray-700">
          ${eventItems}
        </ul>
      `;
      
      timelineContainer.appendChild(timelineElement);
    });
    
    // Add recommendations
    const recommendations = complianceData.recommendations || [];
    
    if (recommendations.length > 0) {
      const recommendationsElement = document.createElement('div');
      recommendationsElement.className = 'mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200';
      
      let recommendationItems = '';
      recommendations.forEach(item => {
        recommendationItems += `<li class="text-sm mb-1">${item}</li>`;
      });
      
      recommendationsElement.innerHTML = `
        <div class="font-medium mb-2">Recommendations:</div>
        <ul class="ml-4 list-disc list-outside text-gray-700">
          ${recommendationItems}
        </ul>
      `;
      
      timelineContainer.appendChild(recommendationsElement);
    }
  }
  
  formatBadgeName(badgeName) {
    return badgeName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  showLoading(isLoading) {
    const loadingIndicator = document.getElementById('loading-indicator');
    const content = document.getElementById('post-tracker-content');
    
    if (isLoading) {
      loadingIndicator.classList.remove('hidden');
      content.classList.add('opacity-50');
    } else {
      loadingIndicator.classList.add('hidden');
      content.classList.remove('opacity-50');
    }
  }
  
  showError(message) {
    const contentElement = document.getElementById('post-tracker-content');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'bg-red-50 text-red-800 p-4 rounded-lg border border-red-200 text-center';
    errorElement.innerHTML = `
      <div class="font-bold mb-2">Error</div>
      <div>${message}</div>
      <button id="retry-btn" class="mt-3 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded">
        Retry
      </button>
    `;
    
    contentElement.innerHTML = '';
    contentElement.appendChild(errorElement);
    
    document.getElementById('retry-btn').addEventListener('click', () => {
      this.initialize();
    });
  }
  
  showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
      type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`;
    
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 500);
    }, 3000);
  }
}

// Initialize widget when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Get client ID from data attribute or use default
  const clientId = document.getElementById('post-tracker-content').dataset.clientId || 'client-12345';
  const widget = new PostTrackerWidget(clientId);
});
