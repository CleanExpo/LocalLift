/**
 * Post Notifications Component
 * 
 * This script manages a dynamic list of new post notifications with:
 * - 60-minute countdown timers
 * - Direct links to posts
 * - Automatic removal upon interaction
 * 
 * It uses Supabase's real-time functionality to receive notifications
 * about new posts as they are created.
 */

class PostNotificationsManager {
  constructor(containerId = 'post-notifications-container') {
    // Container for notifications
    this.containerId = containerId;
    this.container = null;
    
    // Track active notifications and their timers
    this.activeNotifications = new Map(); // postId -> {element, timer, expiryTime}
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', () => this.initialize());
  }
  
  /**
   * Initialize the notifications component
   */
  initialize() {
    // Create container if it doesn't exist
    this.ensureContainer();
    
    // Set up Supabase real-time subscription for new posts
    this.setupRealtimeSubscription();
    
    // Load any existing recent posts (last hour)
    this.loadRecentPosts();
    
    console.log('Post notifications system initialized');
  }
  
  /**
   * Ensure the notifications container exists in the DOM
   */
  ensureContainer() {
    this.container = document.getElementById(this.containerId);
    
    if (!this.container) {
      // Create the container if it doesn't exist
      this.container = document.createElement('div');
      this.container.id = this.containerId;
      this.container.className = 'fixed top-20 right-4 w-80 z-50 space-y-2 max-h-[70vh] overflow-y-auto';
      document.body.appendChild(this.container);
    }
  }
  
  /**
   * Set up Supabase real-time subscription for new posts
   */
  setupRealtimeSubscription() {
    // This requires the Supabase client to be initialized elsewhere
    if (typeof supabase !== 'undefined') {
      const channel = supabase
        .channel('posts-notifications')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'posts' },
          (payload) => {
            const post = payload.new;
            this.addNotification(post);
          }
        )
        .subscribe();
        
      console.log('Realtime subscription for new posts established');
    } else {
      console.warn('Supabase client not found. Falling back to polling for new posts.');
      // Fall back to polling if Supabase is not available
      this.setupPolling();
    }
  }
  
  /**
   * Fall back to polling for new posts if real-time is not available
   */
  setupPolling() {
    // Check for new posts every 30 seconds
    setInterval(() => this.checkForNewPosts(), 30000);
  }
  
  /**
   * Poll for new posts (fallback method)
   */
  async checkForNewPosts() {
    try {
      const response = await fetch('/api/posts/recent');
      if (!response.ok) throw new Error('Failed to fetch recent posts');
      
      const posts = await response.json();
      const now = new Date();
      
      // Filter for posts in the last minute that we haven't shown yet
      const oneMinuteAgo = new Date(now.getTime() - 60000);
      const newPosts = posts.filter(post => {
        const postDate = new Date(post.created_at);
        return postDate > oneMinuteAgo && !this.activeNotifications.has(post.id);
      });
      
      // Add notifications for new posts
      newPosts.forEach(post => this.addNotification(post));
      
    } catch (error) {
      console.error('Error checking for new posts:', error);
    }
  }
  
  /**
   * Load recent posts from the last hour
   */
  async loadRecentPosts() {
    try {
      const response = await fetch('/api/posts/recent');
      if (!response.ok) throw new Error('Failed to fetch recent posts');
      
      const posts = await response.json();
      const now = new Date();
      
      // Filter for posts in the last hour
      const oneHourAgo = new Date(now.getTime() - 3600000);
      const recentPosts = posts.filter(post => {
        const postDate = new Date(post.created_at);
        return postDate > oneHourAgo;
      });
      
      // Add notifications for recent posts
      recentPosts.forEach(post => this.addNotification(post));
      
    } catch (error) {
      console.error('Error loading recent posts:', error);
    }
  }
  
  /**
   * Add a new post notification
   * 
   * @param {Object} post - The post object
   */
  addNotification(post) {
    // Skip if we already have this notification
    if (this.activeNotifications.has(post.id)) return;
    
    // Create notification element
    const notificationEl = document.createElement('div');
    notificationEl.className = 'bg-white rounded-lg shadow-md border border-gray-200 p-3 flex items-center transition-all duration-300 hover:shadow-lg';
    notificationEl.dataset.postId = post.id;
    
    // Calculate expiry time (60 minutes from now)
    const now = new Date();
    const expiryTime = new Date(now.getTime() + 3600000); // 60 minutes
    
    // For posts loaded from history, adjust the expiry time based on creation time
    if (post.created_at) {
      const createdAt = new Date(post.created_at);
      const elapsedMs = now.getTime() - createdAt.getTime();
      const remainingMs = Math.max(3600000 - elapsedMs, 0);
      
      if (remainingMs <= 0) {
        // Skip this post if it's already expired
        return;
      }
      
      // Adjust expiry time
      expiryTime.setTime(now.getTime() + remainingMs);
    }
    
    // Create timer element
    const timerEl = document.createElement('span');
    timerEl.className = 'text-sm font-medium bg-gray-100 text-gray-800 rounded-full px-2 py-1 mr-2 min-w-[48px] text-center';
    
    // Create link element
    const linkEl = document.createElement('a');
    linkEl.href = post.url || `/posts/${post.id}`;
    linkEl.className = 'text-primary-700 hover:text-primary-900 flex-grow font-medium text-sm';
    linkEl.textContent = post.title || 'New post available';
    
    // Create document icon
    const iconEl = document.createElement('span');
    iconEl.className = 'mr-2 text-gray-500';
    iconEl.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>';
    
    // Assemble notification
    notificationEl.appendChild(timerEl);
    linkEl.prepend(iconEl);
    notificationEl.appendChild(linkEl);
    
    // Add to container
    this.container.appendChild(notificationEl);
    
    // Set up timer
    const timerId = setInterval(() => {
      const now = new Date();
      const remainingMs = expiryTime.getTime() - now.getTime();
      
      if (remainingMs <= 0) {
        // Time's up, remove notification
        this.removeNotification(post.id);
        return;
      }
      
      // Update timer display
      const remainingMinutes = Math.ceil(remainingMs / 60000);
      timerEl.textContent = `${remainingMinutes}m`;
      
    }, 30000); // Update every 30 seconds
    
    // Initial timer update
    const remainingMs = expiryTime.getTime() - now.getTime();
    const remainingMinutes = Math.ceil(remainingMs / 60000);
    timerEl.textContent = `${remainingMinutes}m`;
    
    // Add click handler to remove notification when clicked
    linkEl.addEventListener('click', (e) => {
      // Don't prevent default - let the link work normally
      // But remove the notification
      this.removeNotification(post.id);
    });
    
    // Store reference to notification and timer
    this.activeNotifications.set(post.id, {
      element: notificationEl,
      timer: timerId,
      expiryTime
    });
  }
  
  /**
   * Remove a notification
   * 
   * @param {string} postId - ID of the post to remove notification for
   */
  removeNotification(postId) {
    const notification = this.activeNotifications.get(postId);
    if (!notification) return;
    
    // Clear the timer
    clearInterval(notification.timer);
    
    // Add fade-out animation
    notification.element.classList.add('opacity-0');
    
    // Remove after animation completes
    setTimeout(() => {
      if (notification.element.parentNode) {
        notification.element.parentNode.removeChild(notification.element);
      }
      this.activeNotifications.delete(postId);
    }, 300);
  }
}

// Initialize the notifications manager
const postNotifications = new PostNotificationsManager();

// Export for potential use in other modules
export default postNotifications;
