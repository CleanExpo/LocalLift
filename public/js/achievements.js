/**
 * Achievements Display JavaScript
 * 
 * This file handles loading and displaying client achievements
 * as part of the badge gamification system.
 */

// Track loaded achievements to detect new ones
let loadedAchievements = [];

/**
 * Initialize the achievements display components
 */
function initAchievements() {
  // Set up event listeners for achievement-related UI
  document.addEventListener('DOMContentLoaded', () => {
    const achievementsList = document.getElementById('achievements-list');
    const clientId = getClientId();
    
    if (achievementsList && clientId) {
      loadAchievements(clientId);
      
      // Refresh achievements every 5 minutes (if user stays on page)
      setInterval(() => {
        loadAchievements(clientId, true);
      }, 5 * 60 * 1000);
    }
    
    // Setup achievements info toggle if it exists
    const infoToggle = document.querySelector('.achievements-info-toggle');
    if (infoToggle) {
      infoToggle.addEventListener('click', toggleAchievementsInfo);
    }
  });
}

/**
 * Load achievements for a client from the API
 * 
 * @param {string} clientId - The client's unique ID
 * @param {boolean} silent - If true, don't show loading indicators
 */
async function loadAchievements(clientId, silent = false) {
  try {
    if (!silent) {
      showAchievementsLoading();
    }
    
    const response = await fetch(`/api/client/${clientId}/achievements`);
    
    if (!response.ok) {
      throw new Error(`Failed to load achievements: ${response.status}`);
    }
    
    const achievements = await response.json();
    
    // Check for new achievements
    const newAchievements = findNewAchievements(achievements);
    
    // Display all achievements
    displayAchievements(achievements);
    
    // If there are new achievements and this isn't the first load, show notifications
    if (newAchievements.length > 0 && loadedAchievements.length > 0) {
      showAchievementNotifications(newAchievements);
    }
    
    // Update the loaded achievements reference
    loadedAchievements = achievements;
    
  } catch (error) {
    console.error('Error loading achievements:', error);
    displayAchievementError(error.message);
  }
}

/**
 * Display achievements in the UI
 * 
 * @param {Array} achievements - Array of achievement objects
 */
function displayAchievements(achievements) {
  const list = document.getElementById('achievements-list');
  
  if (!list) return;
  
  // Clear current list
  list.innerHTML = '';
  
  if (achievements.length === 0) {
    list.innerHTML = '<li class="no-achievements">No achievements yet. Keep earning badges!</li>';
    return;
  }
  
  // Group achievements by type
  const grouped = groupAchievementsByType(achievements);
  
  // Create sections for each type
  Object.entries(grouped).forEach(([type, items]) => {
    // Add section title
    const sectionTitle = document.createElement('h3');
    sectionTitle.className = 'achievement-type';
    sectionTitle.textContent = formatAchievementType(type);
    list.appendChild(sectionTitle);
    
    // Add achievements for this type
    items.forEach(achievement => {
      const li = document.createElement('li');
      li.className = 'achievement-item';
      
      // Format date
      const earnedDate = new Date(achievement.earned_at);
      const formattedDate = earnedDate.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
      
      // Create achievement HTML
      li.innerHTML = `
        <div class="achievement-icon ${type}">
          <span class="icon">${getAchievementIcon(type)}</span>
        </div>
        <div class="achievement-details">
          <div class="achievement-label">${achievement.label}</div>
          <div class="achievement-date">Earned ${formattedDate}</div>
        </div>
      `;
      
      list.appendChild(li);
    });
  });
  
  // Show the achievement container
  const container = document.getElementById('achievements-container');
  if (container) {
    container.classList.remove('loading');
  }
}

/**
 * Group achievements by their type
 * 
 * @param {Array} achievements - Array of achievement objects
 * @returns {Object} Object with type keys containing arrays of achievements
 */
function groupAchievementsByType(achievements) {
  return achievements.reduce((groups, achievement) => {
    const type = achievement.type || 'other';
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(achievement);
    return groups;
  }, {});
}

/**
 * Format achievement type for display
 * 
 * @param {string} type - Achievement type (e.g., 'milestone', 'streak')
 * @returns {string} Formatted type name
 */
function formatAchievementType(type) {
  switch (type) {
    case 'milestone':
      return 'Badge Milestones';
    case 'streak':
      return 'Streak Achievements';
    default:
      return type.charAt(0).toUpperCase() + type.slice(1);
  }
}

/**
 * Get appropriate icon for achievement type
 * 
 * @param {string} type - Achievement type
 * @returns {string} Icon HTML
 */
function getAchievementIcon(type) {
  switch (type) {
    case 'milestone':
      return '🏆';
    case 'streak':
      return '🔥';
    default:
      return '✨';
  }
}

/**
 * Find new achievements comparing to previously loaded ones
 * 
 * @param {Array} currentAchievements - Currently fetched achievements
 * @returns {Array} Newly earned achievements
 */
function findNewAchievements(currentAchievements) {
  if (loadedAchievements.length === 0) return [];
  
  // Get the most recent earned date from loaded achievements
  const mostRecentLoaded = loadedAchievements.reduce((recent, achievement) => {
    const date = new Date(achievement.earned_at);
    return date > recent ? date : recent;
  }, new Date(0));
  
  // Filter current achievements to find any with earned dates after the most recent loaded
  return currentAchievements.filter(achievement => {
    const earnedDate = new Date(achievement.earned_at);
    return earnedDate > mostRecentLoaded;
  });
}

/**
 * Show notifications for newly earned achievements
 * 
 * @param {Array} newAchievements - Array of newly earned achievements
 */
function showAchievementNotifications(newAchievements) {
  newAchievements.forEach(achievement => {
    showNotification(
      '🎉 New Achievement!',
      `You've earned: ${achievement.label}`,
      'achievement-notification'
    );
  });
}

/**
 * Show a notification toast
 * 
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 * @param {string} className - Additional CSS class
 */
function showNotification(title, message, className = '') {
  // Check if notification container exists, create if not
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    document.body.appendChild(container);
  }
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${className}`;
  notification.innerHTML = `
    <div class="notification-title">${title}</div>
    <div class="notification-message">${message}</div>
  `;
  
  // Add close button
  const closeButton = document.createElement('button');
  closeButton.className = 'notification-close';
  closeButton.innerHTML = '&times;';
  closeButton.addEventListener('click', () => {
    notification.classList.add('closing');
    setTimeout(() => {
      notification.remove();
    }, 300);
  });
  notification.appendChild(closeButton);
  
  // Add to container
  container.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    notification.classList.add('closing');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 5000);
}

/**
 * Show loading state for achievements list
 */
function showAchievementsLoading() {
  const list = document.getElementById('achievements-list');
  const container = document.getElementById('achievements-container');
  
  if (list) {
    list.innerHTML = '<li class="loading-item">Loading achievements...</li>';
  }
  
  if (container) {
    container.classList.add('loading');
  }
}

/**
 * Display an error message in the achievements list
 * 
 * @param {string} message - Error message to display
 */
function displayAchievementError(message) {
  const list = document.getElementById('achievements-list');
  
  if (list) {
    list.innerHTML = `<li class="error">Error: ${message}</li>`;
  }
}

/**
 * Toggle achievements info panel
 */
function toggleAchievementsInfo() {
  const infoPanel = document.getElementById('achievements-info');
  
  if (infoPanel) {
    infoPanel.classList.toggle('show');
  }
}

/**
 * Get client ID from the page
 * 
 * @returns {string|null} Client ID if found
 */
function getClientId() {
  // First try to get from data attribute
  const dashboardElement = document.getElementById('client-dashboard');
  if (dashboardElement && dashboardElement.dataset.clientId) {
    return dashboardElement.dataset.clientId;
  }
  
  // Try to get from global variable
  if (window.CLIENT_ID) {
    return window.CLIENT_ID;
  }
  
  return null;
}

// Initialize when included in a page
initAchievements();
