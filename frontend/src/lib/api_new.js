import { browser } from '$app/environment';
import { offlineDB, syncStore, offlineData } from './stores.js';

// Dynamic API base for LAN access - use current host IP
function getApiBase() {
  if (!browser) return 'http://backend:8000';
  
  // Use network IP when accessing from network
  const hostname = window.location.hostname;
  const apiBase = hostname === 'localhost' || hostname === '127.0.0.1' 
    ? 'http://localhost:8000'
    : `http://${hostname}:8000`;
  console.log(`[API] Using API base: ${apiBase}`);
  
  return apiBase;
}

const API_BASE = getApiBase();

class ApiClient {
  constructor() {
    this._token = null;
    this.isInitialized = false;
    this.connectionTested = false;
    this.isOffline = false;
    this.offlineData = new Map();
    this.initToken();
    this.initOfflineHandling();
  }

  initOfflineHandling() {
    if (browser) {
      // Load cached data
      const cached = localStorage.getItem('offlineData');
      if (cached) {
        try {
          const data = JSON.parse(cached);
          Object.entries(data).forEach(([key, value]) => {
            this.offlineData.set(key, value);
          });
        } catch (e) {}
      }

      // Listen for online/offline events
      window.addEventListener('online', () => {
        this.isOffline = false;
        this.syncOfflineData();
      });
      
      window.addEventListener('offline', () => {
        this.isOffline = true;
      });
      
      this.isOffline = !navigator.onLine;
    }
  }

  cacheData(key, data) {
    this.offlineData.set(key, { data, timestamp: Date.now() });
    if (browser) {
      const cacheObj = Object.fromEntries(this.offlineData);
      localStorage.setItem('offlineData', JSON.stringify(cacheObj));
    }
  }

  getCachedData(key, maxAge = 300000) { // 5 minutes default
    const cached = this.offlineData.get(key);
    if (cached && (Date.now() - cached.timestamp) < maxAge) {
      return cached.data;
    }
    return null;
  }

  async getOfflineData(endpoint) {
    if (!browser) return null;
    
    try {
      // Map endpoints to store names
      const storeMap = {
        '/quizzes': 'quizzes',
        '/questions': 'questions',
        '/results': 'results',
        '/lessons': 'lessons',
        '/notifications': 'notifications'
      };
      
      const storeName = storeMap[endpoint];
      if (storeName) {
        const data = await offlineDB.getAll(storeName);
        return data.length > 0 ? data : null;
      }
    } catch (error) {
      console.error('Error getting offline data:', error);
    }
    return null;
  }

  async storeOfflineData(endpoint, data) {
    if (!browser) return;
    
    try {
      // Update the appropriate store based on endpoint
      if (endpoint === '/quizzes') {
        await offlineData.updateQuizzes(Array.isArray(data) ? data : [data]);
      } else if (endpoint === '/questions') {
        await offlineData.updateQuestions(Array.isArray(data) ? data : [data]);
      } else if (endpoint.includes('/results')) {
        await offlineData.updateResults(Array.isArray(data) ? data : [data]);
      } else if (endpoint === '/lessons') {
        await offlineData.updateLessons(Array.isArray(data) ? data : [data]);
      } else if (endpoint === '/notifications') {
        await offlineData.updateNotifications(Array.isArray(data) ? data : [data]);
      }
    } catch (error) {
      console.error('Error storing offline data:', error);
    }
  }

  async queueOfflineAction(endpoint, options) {
    if (!browser) return;
    
    try {
      await offlineDB.addToSyncQueue(endpoint, {
        method: options.method,
        body: options.body,
        headers: options.headers
      });
      
      // Update sync store
      const queueLength = (await offlineDB.getSyncQueue()).length;
      syncStore.setPendingItems(queueLength);
    } catch (error) {
      console.error('Error queuing offline action:', error);
    }
  }

  async syncOfflineData() {
    if (!browser || this.isOffline) return;
    
    try {
      syncStore.startSync();
      const syncQueue = await offlineDB.getSyncQueue();
      const pendingItems = syncQueue.filter(item => item.status === 'pending');
      
      for (const item of pendingItems) {
        try {
          const response = await this.request(item.action, {
            method: item.data.method,
            body: item.data.body,
            headers: item.data.headers
          });
          
          // Remove from queue on success
          await offlineDB.delete('sync_queue', item.id);
        } catch (error) {
          // Update retry count
          await offlineDB.updateSyncItem(item.id, {
            status: 'error',
            retries: (item.retries || 0) + 1,
            lastError: error.message
          });
        }
      }
      
      syncStore.endSync(true);
    } catch (error) {
      syncStore.endSync(false, error.message);
    }
  }

  initToken() {
    if (browser) {
      this._token = localStorage.getItem('token');
      this.isInitialized = true;
    }
  }

  setToken(token) {
    this._token = token;
    this.connectionTested = false; // Reset connection test when token changes
    if (browser) {
      localStorage.setItem('token', token);
    }
  }

  clearToken() {
    this._token = null;
    this.connectionTested = false;
    this.isInitialized = false;
    if (browser) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  // Force reinitialize the client
  forceReinit() {
    this.clearToken();
    this.initToken();
    this.connectionTested = false;
  }

  async request(endpoint, options = {}) {
    // Ensure client is initialized
    if (!this.isInitialized) {
      this.initToken();
    }

    const method = options.method || 'GET';
    const cacheKey = `${method}:${endpoint}`;
    
    // Minimal logging to prevent console spam
    if (endpoint !== '/auth/test') { // Skip logging for auth test to reduce noise
      console.log(`[API] ${method} request to ${endpoint}`);
    }
    
    // Critical endpoints that must execute immediately (auth, health checks, admin operations, quiz broadcast)
    const criticalEndpoints = ['/auth/login', '/auth/register', '/auth/test', '/health', '/lessons', '/admin/', '/teacher-lessons', '/announcements', '/schedules', '/broadcast', '/activate'];
    const isCritical = criticalEndpoints.some(critical => endpoint.includes(critical)) || endpoint === '/lessons' || method === 'POST' && endpoint.startsWith('/lessons');
    
    // For POST/PUT/DELETE, queue for later sync EXCEPT for critical endpoints
    if (['POST', 'PUT', 'DELETE'].includes(method) && !isCritical) {
      console.log(`[API] Queueing ${method} request to ${endpoint}`);
      await this.queueOfflineAction(endpoint, options);
      return { 
        queued: true, 
        message: 'Action saved locally',
        offline: true,
        timestamp: Date.now()
      };
    }
    
    // Use clean URL without any parameters to prevent refresh issues
    let url = `${API_BASE}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    // Always sync token from localStorage before request
    if (browser && !this._token) {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        this._token = storedToken;
      }
    }

    if (this._token) {
      config.headers.Authorization = `Bearer ${this._token}`;
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    // Special handling for auth/test endpoint to prevent refresh loops
    if (endpoint === '/auth/test') {
      // For auth test, first check if we have a valid token in localStorage
      if (!this._token) {
        throw new Error('No authentication token');
      }
      
      // Return cached auth test result if available (within last 30 seconds)
      const cached = this.getCachedData(cacheKey, 30000);
      if (cached) {
        return cached;
      }
    }

    try {
      // Make request with a reasonable timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout for LAN
      
      config.signal = controller.signal;
      
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // For auth errors, clear token to force re-login
          if (endpoint !== '/auth/test') { // Don't clear for auth test to prevent loops
            this.clearToken();
          }
          throw new Error('Authentication failed');
        }
        throw new Error(`HTTP ${response.status}`);
      }

      this.connectionTested = true;
      
      const data = await response.json();
      
      // Cache successful responses
      if (!options.method || options.method === 'GET') {
        this.cacheData(cacheKey, data);
        if (endpoint !== '/auth/test') { // Don't store auth test responses
          await this.storeOfflineData(endpoint, data);
        }
      }
      
      return data;
    } catch (err) {
      // Only use cache as last resort
      if (err.name === 'AbortError') {
        console.error(`[API] Request timeout for ${endpoint}`);
      } else if (endpoint !== '/auth/test') { // Skip logging for auth test
        console.error(`[API] Network error for ${endpoint}:`, err.message);
      }
      
      if (method === 'GET') {
        const cached = this.getCachedData(cacheKey);
        if (cached) {
          if (endpoint !== '/auth/test') { // Skip logging for auth test
            console.log(`[API] Using cached fallback for ${endpoint}`);
          }
          return cached;
        }
      }
      
      throw new Error(err.message || 'Local server not available');
    }
  }

  async broadcastQuiz(quizId) {
    console.log('📡 API: Broadcasting quiz', quizId);
    const result = await this.request(`/quizzes/${quizId}/broadcast`, {
      method: 'PUT'
    });
    console.log('📡 API: Broadcast result:', result);
    return result;
  }

  async activateQuiz(quizId) {
    return this.request(`/quizzes/${quizId}/activate`, {
      method: 'PUT'
    });
  }

  // ... rest of the methods remain the same
}

export const api = new ApiClient();
