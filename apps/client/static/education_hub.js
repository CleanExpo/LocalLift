/**
 * Education Hub JavaScript
 * 
 * This file provides the client-side functionality for the Education Hub,
 * including loading lessons, tracking progress, and handling user interactions.
 */

// DOM Elements cache
const elements = {
  lessonGrid: document.getElementById('lesson-grid'),
  categoryFilter: document.getElementById('category-filter'),
  difficultyFilter: document.getElementById('difficulty-filter'),
  formatFilter: document.getElementById('format-filter'),
  searchInput: document.getElementById('search-input'),
  progressBar: document.getElementById('overall-progress'),
  loadMoreBtn: document.getElementById('load-more'),
  recommendedCarousel: document.getElementById('recommended-carousel'),
  lessonContent: document.getElementById('lesson-content'),
  bookmarkBtn: document.getElementById('bookmark-btn'),
  progressIndicator: document.getElementById('progress-indicator'),
  completeBtn: document.getElementById('complete-lesson'),
  ratingStars: document.querySelectorAll('.rating-star'),
  categoryTabs: document.querySelectorAll('.category-tab'),
  loadingSpinner: document.getElementById('loading-spinner')
};

// State management
const state = {
  lessons: [],
  currentLesson: null,
  categories: [],
  progress: {},
  recommendations: [],
  filters: {
    category: '',
    difficulty: '',
    format: '',
    searchTerm: ''
  },
  pagination: {
    offset: 0,
    limit: 12,
    hasMore: true
  },
  timeTracker: {
    startTime: null,
    totalSeconds: 0,
    intervalId: null
  }
};

/**
 * Initialize the page
 */
async function init() {
  showLoading();
  try {
    // Load categories for filters
    await loadCategories();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load user progress
    await loadUserProgress();
    
    // Load initial lessons
    await loadLessons();
    
    // Load recommendations
    await loadRecommendedLessons();

    // Check URL for lesson slug
    const urlParams = new URLSearchParams(window.location.search);
    const lessonSlug = urlParams.get('lesson');
    if (lessonSlug) {
      await loadLessonBySlug(lessonSlug);
    }
  } catch (error) {
    console.error('Error initializing Education Hub:', error);
    showErrorMessage('There was an error loading the Education Hub. Please try again later.');
  } finally {
    hideLoading();
  }
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
  // Filter listeners
  elements.categoryFilter?.addEventListener('change', handleFilterChange);
  elements.difficultyFilter?.addEventListener('change', handleFilterChange);
  elements.formatFilter?.addEventListener('change', handleFilterChange);
  elements.searchInput?.addEventListener('input', debounce(handleSearchInput, 500));
  
  // Pagination
  elements.loadMoreBtn?.addEventListener('click', loadMoreLessons);
  
  // Category tabs
  elements.categoryTabs?.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      elements.categoryTabs.forEach(t => t.classList.remove('active'));
      // Add active class to clicked tab
      tab.classList.add('active');
      // Set category filter and reload lessons
      state.filters.category = tab.dataset.category;
      state.pagination.offset = 0;
      loadLessons(true);
    });
  });
  
  // Lesson interaction
  elements.bookmarkBtn?.addEventListener('click', toggleBookmark);
  elements.completeBtn?.addEventListener('click', markLessonCompleted);
  
  // Rating system
  elements.ratingStars?.forEach(star => {
    star.addEventListener('click', () => rateLesson(parseInt(star.dataset.value, 10)));
  });
  
  // Handle tab visibility change (e.g., user switching tabs)
  document.addEventListener('visibilitychange', handleVisibilityChange);
}

/**
 * Load categories for filtering
 */
async function loadCategories() {
  try {
    const response = await fetch('/api/client/education/categories');
    const data = await response.json();
    
    if (data.status === 'success') {
      state.categories = data.categories;
      
      // Populate category filter if it exists
      if (elements.categoryFilter) {
        const options = state.categories.map(category => 
          `<option value="${category.name}">${category.name} (${category.count})</option>`
        );
        elements.categoryFilter.innerHTML = '<option value="">All Categories</option>' + options.join('');
      }
      
      // Populate category tabs if they exist
      if (elements.categoryTabs && elements.categoryTabs.length > 0) {
        // The tabs are already in the DOM, just update the counts
        state.categories.forEach(category => {
          const tab = Array.from(elements.categoryTabs).find(t => t.dataset.category === category.name);
          if (tab) {
            const countElement = tab.querySelector('.count');
            if (countElement) {
              countElement.textContent = category.count;
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Error loading categories:', error);
  }
}

/**
 * Load user progress data
 */
async function loadUserProgress() {
  try {
    const response = await fetch('/api/client/education/progress');
    const data = await response.json();
    
    if (data.status === 'success') {
      state.progress = data.progress;
      
      // Update progress bar if it exists
      if (elements.progressBar) {
        elements.progressBar.style.width = `${state.progress.completion_percentage}%`;
        elements.progressBar.setAttribute('aria-valuenow', state.progress.completion_percentage);
        
        // Update text if there's a label
        const progressLabel = document.getElementById('progress-label');
        if (progressLabel) {
          progressLabel.textContent = `${state.progress.completion_percentage}% Complete`;
        }
        
        // Update counts if they exist
        const completedCount = document.getElementById('completed-count');
        if (completedCount) {
          completedCount.textContent = state.progress.completed_lessons;
        }
        
        const totalCount = document.getElementById('total-count');
        if (totalCount) {
          totalCount.textContent = state.progress.total_lessons;
        }
      }
    }
  } catch (error) {
    console.error('Error loading user progress:', error);
  }
}

/**
 * Load lessons based on current filters and pagination
 * @param {boolean} reset - Whether to reset the current lessons (true when changing filters)
 */
async function loadLessons(reset = false) {
  showLoading();
  
  try {
    const { category, difficulty, format, searchTerm } = state.filters;
    const { offset, limit } = state.pagination;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (difficulty) params.append('difficulty', difficulty);
    if (format) params.append('format_type', format);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    
    const response = await fetch(`/api/client/education/lessons?${params.toString()}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      // If resetting, replace the current lessons, otherwise append
      if (reset) {
        state.lessons = data.lessons;
        if (elements.lessonGrid) {
          elements.lessonGrid.innerHTML = '';
        }
      } else {
        state.lessons = [...state.lessons, ...data.lessons];
      }
      
      // Update UI with the lessons
      renderLessons(reset ? data.lessons : state.lessons);
      
      // Update pagination state
      state.pagination.hasMore = data.lessons.length === limit;
      
      // Show/hide load more button
      if (elements.loadMoreBtn) {
        elements.loadMoreBtn.style.display = state.pagination.hasMore ? 'block' : 'none';
      }
    } else {
      console.error('Error loading lessons:', data.message);
    }
  } catch (error) {
    console.error('Error loading lessons:', error);
    showErrorMessage('There was an error loading lessons. Please try again.');
  } finally {
    hideLoading();
  }
}

/**
 * Load more lessons when the user clicks "Load More"
 */
function loadMoreLessons() {
  state.pagination.offset += state.pagination.limit;
  loadLessons(false);
}

/**
 * Load recommended lessons for the user
 */
async function loadRecommendedLessons() {
  if (!elements.recommendedCarousel) return;
  
  try {
    const response = await fetch('/api/client/education/recommended?limit=5');
    const data = await response.json();
    
    if (data.status === 'success') {
      state.recommendations = data.recommendations;
      renderRecommendedLessons();
    }
  } catch (error) {
    console.error('Error loading recommendations:', error);
  }
}

/**
 * Load a specific lesson by its slug
 * @param {string} slug - The lesson slug
 */
async function loadLessonBySlug(slug) {
  if (!elements.lessonContent) return;
  
  showLoading();
  
  try {
    const response = await fetch(`/api/client/education/lessons/${slug}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      state.currentLesson = data.lesson;
      renderLessonContent(data.lesson);
      startTimeTracking();
    } else {
      console.error('Error loading lesson:', data.message);
      showErrorMessage('The requested lesson could not be loaded.');
    }
  } catch (error) {
    console.error('Error loading lesson:', error);
    showErrorMessage('There was an error loading the lesson. Please try again.');
  } finally {
    hideLoading();
  }
}

/**
 * Render lessons in the grid
 * @param {Array} lessons - Array of lesson objects
 */
function renderLessons(lessons) {
  if (!elements.lessonGrid) return;
  
  if (lessons.length === 0) {
    elements.lessonGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>No lessons found</h3>
        <p>Try changing your filters or check back later for new content.</p>
      </div>
    `;
    return;
  }
  
  const lessonCards = lessons.map(lesson => {
    // Get progress info if available
    const lessonProgress = state.progress.lessons?.find(p => p.id === lesson.id);
    const progressStatus = lessonProgress ? lessonProgress.progress.status : 'not_started';
    const progressPercentage = lessonProgress ? lessonProgress.progress.progress_percentage : 0;
    const isBookmarked = lessonProgress ? lessonProgress.progress.bookmarked : false;
    
    // Determine status badge
    let statusBadge = '';
    if (progressStatus === 'completed') {
      statusBadge = '<span class="badge completed">Completed</span>';
    } else if (progressStatus === 'in_progress') {
      statusBadge = '<span class="badge in-progress">In Progress</span>';
    }
    
    // Format estimated time
    const estimatedTime = lesson.estimated_time < 60 
      ? `${lesson.estimated_time} min` 
      : `${Math.floor(lesson.estimated_time / 60)}h ${lesson.estimated_time % 60}m`;
    
    return `
      <div class="lesson-card ${progressStatus}">
        <a href="?lesson=${lesson.slug}" class="lesson-link">
          <div class="card-header">
            ${statusBadge}
            <span class="difficulty badge ${lesson.difficulty}">${lesson.difficulty}</span>
            ${isBookmarked ? '<span class="bookmark-icon">★</span>' : ''}
          </div>
          <div class="thumbnail">
            <img src="${lesson.thumbnail_url || '/static/img/default-lesson.jpg'}" alt="${lesson.title}">
            ${progressStatus !== 'not_started' ? 
              `<div class="progress-overlay">
                <div class="progress-bar" style="width: ${progressPercentage}%"></div>
              </div>` : ''}
          </div>
          <div class="card-content">
            <h3 class="lesson-title">${lesson.title}</h3>
            <div class="lesson-meta">
              <span class="format">${lesson.format}</span>
              <span class="time">${estimatedTime}</span>
            </div>
            <div class="category-tag">${lesson.category}</div>
          </div>
        </a>
      </div>
    `;
  }).join('');
  
  // If resetting, replace content, otherwise append
  if (state.pagination.offset === 0) {
    elements.lessonGrid.innerHTML = lessonCards;
  } else {
    elements.lessonGrid.insertAdjacentHTML('beforeend', lessonCards);
  }
}

/**
 * Render recommended lessons carousel
 */
function renderRecommendedLessons() {
  if (!elements.recommendedCarousel || state.recommendations.length === 0) return;
  
  const slideHtml = state.recommendations.map(lesson => {
    return `
      <div class="carousel-slide">
        <a href="?lesson=${lesson.slug}" class="recommendation-card">
          <div class="thumb">
            <img src="${lesson.thumbnail_url || '/static/img/default-lesson.jpg'}" alt="${lesson.title}">
          </div>
          <div class="content">
            <h4>${lesson.title}</h4>
            <div class="meta">
              <span class="category">${lesson.category}</span>
              <span class="difficulty ${lesson.difficulty}">${lesson.difficulty}</span>
            </div>
          </div>
        </a>
      </div>
    `;
  }).join('');
  
  elements.recommendedCarousel.innerHTML = slideHtml;
  
  // Initialize carousel if you're using a library or custom implementation
  // For example: initCarousel(elements.recommendedCarousel);
}

/**
 * Render lesson content for a single lesson view
 * @param {Object} lesson - The lesson object
 */
function renderLessonContent(lesson) {
  if (!elements.lessonContent) return;
  
  // Update URL with the lesson slug without reloading the page
  const url = new URL(window.location);
  url.searchParams.set('lesson', lesson.slug);
  window.history.pushState({}, '', url);
  
  // Get progress information
  const progress = lesson.progress || null;
  const isCompleted = progress && progress.status === 'completed';
  const progressPercentage = progress ? progress.progress_percentage : 0;
  const isBookmarked = progress ? progress.bookmarked : false;
  
  // Update page title
  document.title = `${lesson.title} - Education Hub - LocalLift`;
  
  // Content structure with lesson details
  elements.lessonContent.innerHTML = `
    <div class="lesson-header">
      <div class="breadcrumbs">
        <a href="/client/education">Education Hub</a> &raquo; 
        <a href="/client/education?category=${encodeURIComponent(lesson.category)}">${lesson.category}</a> &raquo; 
        <span>${lesson.title}</span>
      </div>
      
      <h1 class="lesson-title">${lesson.title}</h1>
      
      <div class="lesson-meta">
        <span class="format-badge ${lesson.format}">${lesson.format}</span>
        <span class="difficulty-badge ${lesson.difficulty}">${lesson.difficulty}</span>
        <span class="time-estimate"><i class="far fa-clock"></i> ${lesson.estimated_time} min</span>
        <span class="views-count"><i class="far fa-eye"></i> ${lesson.view_count} views</span>
        
        <div class="rating-display">
          ${generateStars(lesson.average_rating)}
          <span class="rating-count">(${lesson.rating_count})</span>
        </div>
      </div>
    </div>
    
    <div class="lesson-progress-bar">
      <div class="progress">
        <div id="progress-indicator" class="progress-bar" role="progressbar" 
             style="width: ${progressPercentage}%" 
             aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100">
          ${progressPercentage}%
        </div>
      </div>
    </div>
    
    <div class="lesson-actions">
      <button id="bookmark-btn" class="btn ${isBookmarked ? 'bookmarked' : ''}">
        <i class="fa${isBookmarked ? 's' : 'r'} fa-bookmark"></i> 
        ${isBookmarked ? 'Bookmarked' : 'Bookmark'}
      </button>
      
      <button id="complete-lesson" class="btn btn-primary ${isCompleted ? 'completed' : ''}">
        <i class="fa${isCompleted ? 's' : 'r'} fa-check-circle"></i>
        ${isCompleted ? 'Completed' : 'Mark as Complete'}
      </button>
    </div>
    
    <div class="lesson-content-main">
      ${lesson.content}
    </div>
    
    <div class="lesson-footer">
      <div class="rating-section">
        <h4>Rate this lesson:</h4>
        <div class="rating-stars">
          ${[1, 2, 3, 4, 5].map(value => 
            `<span class="rating-star ${progress && progress.rating >= value ? 'selected' : ''}" 
                   data-value="${value}">★</span>`
          ).join('')}
        </div>
      </div>
      
      ${lesson.related_lessons && lesson.related_lessons.length > 0 ? `
      <div class="related-lessons">
        <h4>Related Lessons:</h4>
        <ul>
          ${lesson.related_lessons.map(relatedId => {
            // Find the related lesson in all lessons
            const related = state.lessons.find(l => l.id === relatedId) || { title: 'Related Lesson', slug: '' };
            return `<li><a href="?lesson=${related.slug}">${related.title}</a></li>`;
          }).join('')}
        </ul>
      </div>
      ` : ''}
      
      ${lesson.prerequisites && lesson.prerequisites.length > 0 ? `
      <div class="prerequisites">
        <h4>Prerequisites:</h4>
        <ul>
          ${lesson.prerequisites.map(prereqId => {
            // Find the prerequisite lesson in all lessons
            const prereq = state.lessons.find(l => l.id === prereqId) || { title: 'Prerequisite Lesson', slug: '' };
            return `<li><a href="?lesson=${prereq.slug}">${prereq.title}</a></li>`;
          }).join('')}
        </ul>
      </div>
      ` : ''}
    </div>
  `;
  
  // Re-bind event listeners for the new elements
  elements.bookmarkBtn = document.getElementById('bookmark-btn');
  elements.bookmarkBtn?.addEventListener('click', toggleBookmark);
  
  elements.completeBtn = document.getElementById('complete-lesson');
  elements.completeBtn?.addEventListener('click', markLessonCompleted);
  
  elements.progressIndicator = document.getElementById('progress-indicator');
  
  elements.ratingStars = document.querySelectorAll('.rating-star');
  elements.ratingStars?.forEach(star => {
    star.addEventListener('click', () => rateLesson(parseInt(star.dataset.value, 10)));
  });
  
  // If there's an element to scroll to the top, scroll there
  const contentTop = document.getElementById('lesson-content-top');
  if (contentTop) {
    contentTop.scrollIntoView({ behavior: 'smooth' });
  }
}

/**
 * Generate star rating HTML
 * @param {number} rating - The rating value (0-5)
 * @returns {string} HTML for star rating display
 */
function generateStars(rating) {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
  
  return (
    Array(fullStars).fill('<i class="fas fa-star"></i>').join('') +
    (halfStar ? '<i class="fas fa-star-half-alt"></i>' : '') +
    Array(emptyStars).fill('<i class="far fa-star"></i>').join('')
  );
}

/**
 * Toggle bookmark status for the current lesson
 */
async function toggleBookmark() {
  if (!state.currentLesson) return;
  
  try {
    const lessonId = state.currentLesson.id;
    const currentStatus = elements.bookmarkBtn.classList.contains('bookmarked');
    
    // Optimistically update UI
    elements.bookmarkBtn.classList.toggle('bookmarked');
    elements.bookmarkBtn.innerHTML = currentStatus ? 
      '<i class="far fa-bookmark"></i> Bookmark' : 
      '<i class="fas fa-bookmark"></i> Bookmarked';
    
    // Update on server
    const response = await fetch(`/api/client/education/progress/${lessonId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        bookmarked: !currentStatus
      })
    });
    
    const data = await response.json();
    
    if (data.status !== 'success') {
      // Revert UI if server update failed
      elements.bookmarkBtn.classList.toggle('bookmarked');
      elements.bookmarkBtn.innerHTML = !currentStatus ? 
        '<i class="far fa-bookmark"></i> Bookmark' : 
        '<i class="fas fa-bookmark"></i> Bookmarked';
      
      showErrorMessage('Failed to update bookmark status. Please try again.');
    }
  } catch (error) {
    console.error('Error toggling bookmark:', error);
    showErrorMessage('There was an error updating your bookmark. Please try again.');
  }
}

/**
 * Mark the current lesson as completed
 */
async function markLessonCompleted() {
  if (!state.currentLesson) return;
  
  try {
    const lessonId = state.currentLesson.id;
    const isCompleted = elements.completeBtn.classList.contains('completed');
    
    if (isCompleted) {
      // Already completed, nothing to do
      return;
    }
    
    // Optimistically update UI
    elements.completeBtn.classList.add('completed');
    elements.completeBtn.innerHTML = '<i class="fas fa-check-circle"></i> Completed';
    
    if (elements.progressIndicator) {
      elements.progressIndicator.style.width = '100%';
      elements.progressIndicator.setAttribute('aria-valuenow', 100);
      elements.progressIndicator.textContent = '100%';
    }
    
    // Update on server
    const response = await fetch(`/api/client/education/progress/${lessonId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: 'completed',
        progress_percentage: 100
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      // Show success message
      showSuccessMessage('Lesson marked as completed!');
      
      // Update local progress
      await loadUserProgress();
    } else {
      // Revert UI if server update failed
      elements.completeBtn.classList.remove('completed');
      elements.completeBtn.innerHTML = '<i class="far fa-check-circle"></i> Mark as Complete';
      
      showErrorMessage('Failed to mark lesson as completed. Please try again.');
    }
  } catch (error) {
    console.error('Error marking lesson as completed:', error);
    showErrorMessage('There was an error updating your progress. Please try again.');
  }
}

/**
 * Rate a lesson
 * @param {number} rating - Rating value (1-5)
 */
async function rateLesson(rating) {
  if (!state.currentLesson || !rating || rating < 1 || rating > 5) return;
  
  try {
    const lessonId = state.currentLesson.id;
    
    // Update UI immediately
    elements.ratingStars.forEach(star => {
      const value = parseInt(star.dataset.value, 10);
      if (value <= rating) {
        star.classList.add('selected');
      } else {
        star.classList.remove('selected');
      }
    });
    
    // Send rating to server
    const response = await fetch(`/api/client/education/lessons/${lessonId}/rating?rating=${rating}`, {
      method: 'POST'
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      // Update the display with new average
      const ratingDisplay = document.querySelector('.rating-display');
      if (ratingDisplay) {
        ratingDisplay.innerHTML = `
          ${generateStars(data.new_average_rating)}
          <span class="rating-count">(${data.rating_count})</span>
        `;
      }
      
      showSuccessMessage('Thank you for rating this lesson!');
    } else {
      showErrorMessage('Failed to save your rating. Please try again.');
    }
  } catch (error) {
    console.error('Error rating lesson:', error);
    showErrorMessage('There was an error submitting your rating. Please try again.');
  }
}

/**
 * Start tracking time spent on the current lesson
 */
function startTimeTracking() {
  if (!state.currentLesson) return;
  
  // Clear any existing interval
  if (state.timeTracker.intervalId) {
    clearInterval(state.timeTracker.intervalId);
  }
  
  // Reset time tracker
  state.timeTracker.startTime = new Date();
  state.timeTracker.totalSeconds = 0;
  
  // Start interval to track time
  state.timeTracker.intervalId = setInterval(() => {
    trackLessonTime();
  }, 60000); // Track every minute
}

/**
 * Track time spent on lesson and periodically report to server
 */
async function trackLessonTime() {
  if (!state.currentLesson) return;
  
  const now = new Date();
  const elapsedSeconds = Math.floor((now - state.timeTracker.startTime) / 1000);
  
  // Only report if enough time has passed and the page is active
  if (elapsedSeconds > 0 && document.visibilityState === 'visible') {
    state.timeTracker.totalSeconds += elapsedSeconds;
    state.timeTracker.startTime = now;
    
    try {
      await fetch(`/api/client/education/progress/${state.currentLesson.id}/time?seconds=${elapsedSeconds}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error tracking lesson time:', error);
    }
  }
}

/**
 * Handle visibility change (tab switching, etc.)
 */
function handleVisibilityChange() {
  if (document.visibilityState === 'visible') {
    // Resumed viewing, restart time tracking
    if (state.currentLesson) {
      state.timeTracker.startTime = new Date();
    }
  } else {
    // Left the page, track the time spent so far
    if (state.currentLesson) {
      trackLessonTime();
    }
  }
}

/**
 * Handle filter changes
 */
function handleFilterChange() {
  // Get values from filters
  if (elements.categoryFilter) {
    state.filters.category = elements.categoryFilter.value;
  }
  
  if (elements.difficultyFilter) {
    state.filters.difficulty = elements.difficultyFilter.value;
  }
  
  if (elements.formatFilter) {
    state.filters.format = elements.formatFilter.value;
  }
  
  // Reset pagination
  state.pagination.offset = 0;
  
  // Reload lessons
  loadLessons(true);
}

/**
 * Handle search input
 */
function handleSearchInput() {
  if (!elements.searchInput) return;
  
  state.filters.searchTerm = elements.searchInput.value.trim();
  state.pagination.offset = 0;
  loadLessons(true);
}

/**
 * Show loading spinner
 */
function showLoading() {
  if (elements.loadingSpinner) {
    elements.loadingSpinner.style.display = 'flex';
  }
}

/**
 * Hide loading spinner
 */
function hideLoading() {
  if (elements.loadingSpinner) {
    elements.loadingSpinner.style.display = 'none';
  }
}

/**
 * Show success message
 * @param {string} message - Success message to display
 */
function showSuccessMessage(message) {
  // Implement based on your UI toast/notification system
  console.log('Success:', message);
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showErrorMessage(message) {
  // Implement based on your UI toast/notification system
  console.error('Error:', message);
}

/**
 * Debounce function to limit how often a function is called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 */
function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this, args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
