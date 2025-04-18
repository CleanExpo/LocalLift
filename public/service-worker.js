/**
 * LocalLift Service Worker
 * Provides offline functionality, caching, and performance optimizations
 * v1.0.0 - 2025-04-18
 */

// Cache name versions
const CACHE_NAMES = {
  static: 'locallift-static-v1',
  dynamic: 'locallift-dynamic-v1',
  images: 'locallift-images-v1',
  api: 'locallift-api-v1'
};

// Resources to cache immediately on install
const STATIC_CACHE_URLS = [
  '/',
  '/index.html',
  '/login/index.html',
  '/dashboard/index.html',
  '/style.css',
  '/js/main.js',
  '/js/performance-utils.js',
  '/js/dark-mode.js',
  '/js/responsive-utils.js',
  '/js/tab-handler.js',
  '/js/dropdown-handler.js',
  '/js/config.js',
  '/fonts/inter-var.woff2',
  '/img/logo.svg',
  '/img/icons/dashboard.svg',
  '/img/icons/profile.svg',
  '/img/icons/settings.svg',
  '/offline.html',
  '/404.html'
];

// Maximum number of items in dynamic cache
const DYNAMIC_CACHE_SIZE = 100;

// API endpoints that should be cached (but with network-first strategy)
const API_CACHE_URLS = [
  '/api/health',
  '/api/settings'
];

// Default offline response
const OFFLINE_PAGE = '/offline.html';

/**
 * Install event handler - pre-cache static assets
 */
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  
  // Skip waiting to ensure the latest service worker activates immediately
  self.skipWaiting();
  
  // Pre-cache static resources
  event.waitUntil(
    caches.open(CACHE_NAMES.static)
      .then(cache => {
        console.log('[Service Worker] Pre-caching static assets');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .catch(error => {
        console.error('[Service Worker] Pre-cache error:', error);
      })
  );
});

/**
 * Activate event handler - clean up old caches
 */
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  
  // Clean up old cache versions
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            // Delete caches that are not in our current version
            const isCurrent = Object.values(CACHE_NAMES).includes(cacheName);
            if (!isCurrent) {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
            return Promise.resolve();
          })
        );
      })
      .then(() => {
        console.log('[Service Worker] Activation complete');
        // Claim clients to take control immediately
        return self.clients.claim();
      })
  );
});

/**
 * Fetch event handler - respond with cached resources or network
 */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Skip non-GET requests and browser extensions
  if (event.request.method !== 'GET' || 
      url.protocol !== 'https:' && url.protocol !== 'http:') {
    return;
  }
  
  // Handle different resource types with appropriate strategies
  if (isStaticAsset(url)) {
    // Static assets: Cache first, network fallback
    event.respondWith(cacheFirstStrategy(event.request, CACHE_NAMES.static));
  } else if (isAPIRequest(url)) {
    // API requests: Network first, cache fallback
    event.respondWith(networkFirstStrategy(event.request, CACHE_NAMES.api));
  } else if (isImageRequest(url)) {
    // Images: Cache first with fallback to network and default image
    event.respondWith(imageStrategy(event.request));
  } else {
    // Everything else: Network first with dynamic caching
    event.respondWith(networkWithCacheFallbackStrategy(event.request));
  }
});

/**
 * Push notification event handler
 */
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received:', event);
  
  let notificationData = {};
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'LocalLift Notification',
        body: event.data.text()
      };
    }
  }
  
  const title = notificationData.title || 'LocalLift Notification';
  const options = {
    body: notificationData.body || 'New update from LocalLift',
    icon: '/img/logo-192.png',
    badge: '/img/badge.png',
    data: notificationData.data || {},
    actions: notificationData.actions || [],
    vibrate: [100, 50, 100]
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

/**
 * Notification click event handler
 */
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click:', event);
  
  event.notification.close();
  
  // Handle notification action clicks
  if (event.action) {
    console.log('[Service Worker] Action clicked:', event.action);
    // Handle specific actions here
  }
  
  // Default action - open or focus the app
  const urlToOpen = event.notification.data.url || '/dashboard';
  
  event.waitUntil(
    clients.matchAll({ type: 'window' })
      .then(windowClients => {
        // Check if a window is already open
        for (const client of windowClients) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            return client.focus();
          }
        }
        // If no window is open, open a new one
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

/**
 * Background sync event handler
 */
self.addEventListener('sync', event => {
  console.log('[Service Worker] Sync event:', event);
  
  if (event.tag === 'sync-pending-data') {
    event.waitUntil(syncPendingData());
  }
});

/**
 * Check if a URL is for a static asset
 * @param {URL} url - URL to check
 * @returns {boolean} - Whether URL is for a static asset
 */
function isStaticAsset(url) {
  const staticExtensions = ['.html', '.css', '.js', '.woff2', '.svg', '.json'];
  const path = url.pathname;
  
  // Check if path matches a static extension
  return staticExtensions.some(ext => path.endsWith(ext)) ||
         STATIC_CACHE_URLS.includes(path);
}

/**
 * Check if a URL is for an API request
 * @param {URL} url - URL to check
 * @returns {boolean} - Whether URL is for an API request
 */
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/') ||
         API_CACHE_URLS.some(endpoint => url.pathname.includes(endpoint));
}

/**
 * Check if a URL is for an image
 * @param {URL} url - URL to check
 * @returns {boolean} - Whether URL is for an image
 */
function isImageRequest(url) {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico', '.svg'];
  const path = url.pathname;
  
  return imageExtensions.some(ext => path.endsWith(ext)) ||
         path.includes('/img/') ||
         path.includes('/images/');
}

/**
 * Cache-first strategy - try cache, fallback to network
 * @param {Request} request - The fetch request
 * @param {string} cacheName - Cache to check
 * @returns {Promise<Response>} - Response from cache or network
 */
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Not in cache, get from network
    const networkResponse = await fetch(request);
    
    // Cache the new response
    const cache = await caches.open(cacheName);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] Cache first strategy error:', error);
    
    // If it's a navigation request, return the offline page
    if (request.mode === 'navigate') {
      return caches.match(OFFLINE_PAGE);
    }
    
    // For other requests, return an empty response
    return new Response('', { status: 408, statusText: 'Request timed out' });
  }
}

/**
 * Network-first strategy - try network, fallback to cache
 * @param {Request} request - The fetch request
 * @param {string} cacheName - Cache for fallback
 * @returns {Promise<Response>} - Response from network or cache
 */
async function networkFirstStrategy(request, cacheName) {
  try {
    // Try to get fresh data from network
    const networkResponse = await fetch(request);
    
    // Cache the new response
    const cache = await caches.open(cacheName);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.log('[Service Worker] Network error, falling back to cache:', error);
    
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // No cache either, return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match(OFFLINE_PAGE);
    }
    
    // For API requests, return an appropriate JSON error
    if (isAPIRequest(new URL(request.url))) {
      return new Response(JSON.stringify({
        error: 'network_error',
        message: 'You appear to be offline',
        offline: true
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // For other requests, return a simple error
    return new Response('Network error', { status: 503, statusText: 'Service Unavailable' });
  }
}

/**
 * Network with cache fallback and dynamic caching
 * @param {Request} request - The fetch request
 * @returns {Promise<Response>} - Response from network or cache
 */
async function networkWithCacheFallbackStrategy(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Clone and cache the response
    await updateDynamicCache(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.log('[Service Worker] Network error, falling back to cache');
    
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // No cache either, show offline page for navigation
    if (request.mode === 'navigate') {
      return caches.match(OFFLINE_PAGE);
    }
    
    // For other requests, return an error
    return new Response('Network error', { status: 503, statusText: 'Service Unavailable' });
  }
}

/**
 * Image-specific strategy with placeholder fallback
 * @param {Request} request - The fetch request for an image
 * @returns {Promise<Response>} - Response with the image
 */
async function imageStrategy(request) {
  try {
    // Check cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Not in cache, get from network
    const networkResponse = await fetch(request);
    
    // Cache the new response
    const cache = await caches.open(CACHE_NAMES.images);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.log('[Service Worker] Image fetch error, using placeholder');
    
    // Return a placeholder image from cache
    const placeholderImage = '/img/placeholder.svg';
    const placeholder = await caches.match(placeholderImage);
    
    if (placeholder) {
      return placeholder;
    }
    
    // If placeholder not in cache, return empty transparent gif
    return new Response(
      'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
      {
        status: 200,
        statusText: 'OK',
        headers: {
          'Content-Type': 'image/gif',
          'Cache-Control': 'no-store'
        }
      }
    );
  }
}

/**
 * Update the dynamic cache and manage its size
 * @param {Request} request - The request to cache
 * @param {Response} response - The response to cache
 */
async function updateDynamicCache(request, response) {
  // Only cache valid responses
  if (!response || response.status !== 200) {
    return;
  }
  
  const cache = await caches.open(CACHE_NAMES.dynamic);
  
  // Clean up the cache if needed
  const keys = await cache.keys();
  if (keys.length >= DYNAMIC_CACHE_SIZE) {
    console.log('[Service Worker] Dynamic cache full, removing oldest items');
    await cache.delete(keys[0]);
  }
  
  // Add new response to cache
  await cache.put(request, response);
}

/**
 * Sync pending data from the IndexedDB to the server
 * @returns {Promise} - Promise resolving when sync is complete
 */
async function syncPendingData() {
  console.log('[Service Worker] Syncing pending data');
  
  // This would typically involve:
  // 1. Opening IndexedDB
  // 2. Getting pending items
  // 3. Sending them to the server
  // 4. Clearing successfully synced items
  
  // For demonstration, we'll just check localStorage
  if ('clients' in self) {
    const windowClients = await self.clients.matchAll({ type: 'window' });
    windowClients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETED',
        timestamp: new Date().toISOString()
      });
    });
  }
  
  return Promise.resolve();
}

// Log service worker initialization
console.log('[Service Worker] Initialized');
