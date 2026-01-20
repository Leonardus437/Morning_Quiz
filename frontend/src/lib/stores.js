import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Offline Database Manager
class OfflineDB {
  constructor() {
    this.db = null;
    this.isReady = false;
    this.init();
  }

  async init() {
    if (!browser) return;
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('MorningQuizDB', 3);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        this.isReady = true;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create stores
        const stores = ['users', 'quizzes', 'questions', 'results', 'lessons', 'notifications', 'sync_queue'];
        
        stores.forEach(storeName => {
          if (!db.objectStoreNames.contains(storeName)) {
            const store = db.createObjectStore(storeName, { keyPath: 'id', autoIncrement: true });
            store.createIndex('timestamp', 'timestamp');
            if (storeName === 'sync_queue') {
              store.createIndex('status', 'status');
              store.createIndex('type', 'type');
            }
          }
        });
      };
    });
  }

  async store(storeName, data) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction([storeName], 'readwrite');
    const store = tx.objectStore(storeName);
    return store.put({ ...data, timestamp: Date.now() });
  }

  async get(storeName, id) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction([storeName], 'readonly');
    return tx.objectStore(storeName).get(id);
  }

  async getAll(storeName) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction([storeName], 'readonly');
    return tx.objectStore(storeName).getAll();
  }

  async delete(storeName, id) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction([storeName], 'readwrite');
    return tx.objectStore(storeName).delete(id);
  }

  async clear(storeName) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction([storeName], 'readwrite');
    return tx.objectStore(storeName).clear();
  }

  async addToSyncQueue(action, data, type = 'api') {
    return this.store('sync_queue', {
      action,
      data,
      type,
      status: 'pending',
      retries: 0,
      timestamp: Date.now()
    });
  }

  async getSyncQueue() {
    return this.getAll('sync_queue');
  }

  async updateSyncItem(id, updates) {
    if (!this.isReady) await this.init();
    const tx = this.db.transaction(['sync_queue'], 'readwrite');
    const store = tx.objectStore('sync_queue');
    const item = await store.get(id);
    if (item) {
      return store.put({ ...item, ...updates });
    }
  }
}

const offlineDB = new OfflineDB();

// Connection Status Store
function createConnectionStore() {
  const { subscribe, set } = writable(browser ? navigator.onLine : true);
  
  if (browser) {
    window.addEventListener('online', () => set(true));
    window.addEventListener('offline', () => set(false));
  }
  
  return { subscribe };
}

// Sync Status Store
function createSyncStore() {
  const { subscribe, set, update } = writable({
    isSyncing: false,
    lastSync: null,
    pendingItems: 0,
    errors: []
  });

  return {
    subscribe,
    startSync: () => update(state => ({ ...state, isSyncing: true })),
    endSync: (success = true, error = null) => update(state => ({
      ...state,
      isSyncing: false,
      lastSync: success ? Date.now() : state.lastSync,
      errors: error ? [...state.errors, error] : state.errors
    })),
    setPendingItems: (count) => update(state => ({ ...state, pendingItems: count })),
    clearErrors: () => update(state => ({ ...state, errors: [] }))
  };
}

// Enhanced User Store with Offline Support
function createUserStore() {
  const { subscribe, set, update } = writable(null);

  return {
    subscribe,
    login: async (user) => {
      set(user);
      if (browser) {
        localStorage.setItem('user', JSON.stringify(user));
        await offlineDB.store('users', { ...user, current: true });
      }
    },
    logout: async () => {
      set(null);
      if (browser) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        await offlineDB.clear('users');
        window.location.href = '/';
      }
    },
    init: async () => {
      if (browser) {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = localStorage.getItem('user');
          if (userData) {
            const user = JSON.parse(userData);
            set(user);
            await offlineDB.store('users', { ...user, current: true });
          }
        }
      }
    }
  };
}

// Offline Data Store
function createOfflineDataStore() {
  const { subscribe, set, update } = writable({
    quizzes: [],
    questions: [],
    results: [],
    lessons: [],
    notifications: []
  });

  return {
    subscribe,
    loadFromCache: async () => {
      if (!browser) return;
      
      const [quizzes, questions, results, lessons, notifications] = await Promise.all([
        offlineDB.getAll('quizzes'),
        offlineDB.getAll('questions'),
        offlineDB.getAll('results'),
        offlineDB.getAll('lessons'),
        offlineDB.getAll('notifications')
      ]);
      
      set({ quizzes, questions, results, lessons, notifications });
    },
    updateQuizzes: async (quizzes) => {
      update(state => ({ ...state, quizzes }));
      if (browser) {
        await offlineDB.clear('quizzes');
        for (const quiz of quizzes) {
          await offlineDB.store('quizzes', quiz);
        }
      }
    },
    updateQuestions: async (questions) => {
      update(state => ({ ...state, questions }));
      if (browser) {
        await offlineDB.clear('questions');
        for (const question of questions) {
          await offlineDB.store('questions', question);
        }
      }
    },
    updateResults: async (results) => {
      update(state => ({ ...state, results }));
      if (browser) {
        await offlineDB.clear('results');
        for (const result of results) {
          await offlineDB.store('results', result);
        }
      }
    },
    updateLessons: async (lessons) => {
      update(state => ({ ...state, lessons }));
      if (browser) {
        await offlineDB.clear('lessons');
        for (const lesson of lessons) {
          await offlineDB.store('lessons', lesson);
        }
      }
    },
    updateNotifications: async (notifications) => {
      update(state => ({ ...state, notifications }));
      if (browser) {
        await offlineDB.clear('notifications');
        for (const notification of notifications) {
          await offlineDB.store('notifications', notification);
        }
      }
    },
    addToSyncQueue: async (action, data) => {
      await offlineDB.addToSyncQueue(action, data);
      syncStore.setPendingItems((await offlineDB.getSyncQueue()).length);
    }
  };
}

// Sync Manager
class SyncManager {
  constructor() {
    this.isOnline = browser ? navigator.onLine : true;
    this.syncInProgress = false;
    
    if (browser) {
      window.addEventListener('online', () => {
        this.isOnline = true;
        this.performSync();
      });
      window.addEventListener('offline', () => {
        this.isOnline = false;
      });
    }
  }

  async performSync() {
    if (!this.isOnline || this.syncInProgress) return;
    
    this.syncInProgress = true;
    syncStore.startSync();
    
    try {
      const syncQueue = await offlineDB.getSyncQueue();
      const pendingItems = syncQueue.filter(item => item.status === 'pending');
      
      for (const item of pendingItems) {
        try {
          await this.processSyncItem(item);
          await offlineDB.delete('sync_queue', item.id);
        } catch (error) {
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
    } finally {
      this.syncInProgress = false;
      const remainingItems = await offlineDB.getSyncQueue();
      syncStore.setPendingItems(remainingItems.length);
    }
  }

  async processSyncItem(item) {
    // This would integrate with your API client
    // For now, we'll just simulate the sync
    console.log('Syncing item:', item);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // In real implementation, you'd call the appropriate API method
    // based on item.action and item.data
  }

  async forcSync() {
    if (this.isOnline) {
      await this.performSync();
    }
  }
}

const syncManager = new SyncManager();

// Create store instances
export const user = createUserStore();
export const connectionStatus = createConnectionStore();
export const syncStore = createSyncStore();
export const offlineData = createOfflineDataStore();
export const currentQuiz = writable(null);
export const quizTimer = writable(null);

// Derived stores
export const isOffline = derived(connectionStatus, $connectionStatus => !$connectionStatus);
export const canSync = derived([connectionStatus, syncStore], ([$connectionStatus, $syncStore]) => 
  $connectionStatus && !$syncStore.isSyncing && $syncStore.pendingItems > 0
);

// Export utilities
export { offlineDB, syncManager };

// Auto-load cached data on initialization
if (browser) {
  offlineData.loadFromCache();
  user.init();
}