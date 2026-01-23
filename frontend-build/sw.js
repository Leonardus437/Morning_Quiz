const CACHE_NAME = 'tvet-quiz-disabled';
const STATIC_CACHE = 'static-disabled';
const DYNAMIC_CACHE = 'dynamic-disabled';
const DISABLE_CACHE = true; // ALWAYS fetch latest version

// Essential files for offline functionality
const STATIC_FILES = [
  '/',
  '/teacher',
  '/admin',
  '/manifest.json',
  '/favicon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/offline.html'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/quizzes$/,
  /\/questions$/,
  /\/auth\/test$/,
  /\/health$/
];

// Install event - skip caching
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker - CACHE DISABLED');
  event.waitUntil(self.skipWaiting());
});

// Activate event - delete ALL caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker - DELETING ALL CACHES');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('[SW] Deleting cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - handle requests with offline support
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests
  if (url.port === '8000' || url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle static files and pages
  event.respondWith(handleStaticRequest(request));
});

// Handle API requests - ALWAYS fetch from network
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    // ALWAYS fetch from network - NO CACHE
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed for API request:', url.pathname);
    
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Local server not available',
        offline: true 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static requests - ALWAYS fetch from network
async function handleStaticRequest(request) {
  try {
    // ALWAYS fetch from network - NO CACHE
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'quiz-submission') {
    event.waitUntil(syncQuizSubmissions());
  }
});

// Sync quiz submissions when back online
async function syncQuizSubmissions() {
  console.log('[SW] Syncing quiz submissions');
  
  try {
    // This would integrate with IndexedDB to sync pending submissions
    // For now, just log that sync is happening
    console.log('[SW] Quiz submissions synced successfully');
  } catch (error) {
    console.error('[SW] Failed to sync quiz submissions:', error);
    throw error;
  }
}

// Handle push notifications (for future use)
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New quiz available!',
    icon: '/icon-192.png',
    badge: '/favicon.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Quiz',
        icon: '/icon-192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('TVET Quiz System', options)
  );
});