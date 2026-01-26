import { browser } from '$app/environment';
import { offlineDB, syncStore, offlineData } from './stores.js';

// Dynamic API base - MUST be called at runtime, not at module load
function getApiBase() {
  if (!browser) return 'http://backend:8000';
  
  const hostname = window.location.hostname;
  console.log('[API] Detecting hostname:', hostname);
  
  // Check if we're on Cloudflare Pages (production)
  if (hostname.includes('pages.dev') || hostname.includes('tsskwizi')) {
    console.log('[API] Using Render backend for Cloudflare Pages');
    return 'https://tvet-quiz-backend.onrender.com';
  }
  
  // Use network IP when accessing from network (local development)
  const apiBase = hostname === 'localhost' || hostname === '127.0.0.1' 
    ? 'http://localhost:8000'
    : `http://${hostname}:8000`;
  
  console.log('[API] Using local backend:', apiBase);
  return apiBase;
}

// DO NOT cache API_BASE at module level - call getApiBase() each time
let API_BASE = null;

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

    // CRITICAL: Always sync token from localStorage FIRST before any request
    if (browser) {
      const storedToken = localStorage.getItem('token');
      if (storedToken && storedToken !== this._token) {
        this._token = storedToken;
        console.log('[API] Token synced from localStorage');
      }
    }

    const method = options.method || 'GET';
    const cacheKey = `${method}:${endpoint}`;
    
    // Minimal logging to prevent console spam
    if (endpoint !== '/auth/test') { // Skip logging for auth test to reduce noise
      console.log(`[API] ${method} request to ${endpoint}`);
    }
    
    // Critical endpoints that must execute immediately (auth, health checks, admin operations, quiz broadcast, QUIZ SUBMIT)
    const criticalEndpoints = ['/auth/login', '/auth/register', '/auth/test', '/health', '/lessons', '/admin/', '/teacher-lessons', '/announcements', '/schedules', '/broadcast', '/quizzes', '/questions', '/submit'];
    const isCritical = criticalEndpoints.some(critical => endpoint.includes(critical)) || endpoint === '/lessons' || method === 'POST' && endpoint.startsWith('/lessons') || endpoint.includes('/broadcast') || endpoint.includes('/questions') || endpoint.includes('/submit');
    
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
    const apiBase = getApiBase();
    let url = `${apiBase}${endpoint}`;
    console.log(`[API] Request URL: ${url}`);
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

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
      // Use 120s timeout for production (Render cold start + file processing), 10s for local
      const isProduction = browser && (window.location.hostname.includes('pages.dev') || window.location.hostname.includes('tsskwizi'));
      const timeout = isProduction ? 120000 : 10000;
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      config.signal = controller.signal;
      
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // For auth errors, clear token to force re-login
          // BUT: Don't clear on first 401 - token might just need to be refreshed
          if (endpoint !== '/auth/test' && endpoint !== '/auth/login') {
            console.warn('[API] 401 Unauthorized - Token may be expired');
            // Try to get fresh token from localStorage one more time
            if (browser) {
              const freshToken = localStorage.getItem('token');
              if (freshToken && freshToken !== this._token) {
                console.log('[API] Found different token in localStorage, will retry');
                this._token = freshToken;
                // Don't clear yet - let the caller retry
              } else {
                // Only clear if we're sure the token is invalid
                this.clearToken();
              }
            }
          }
          throw new Error('Invalid token. Please login again.');
        }
        
        // For 400 errors, try to get the error message from response
        if (response.status === 400) {
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
          } catch (e) {
            if (e.message.includes('HTTP')) throw e;
            throw new Error(`HTTP ${response.status}`);
          }
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

  // Auth
  async login(username, password) {
    console.log('🔐 API: Starting login for user:', username);
    console.log('🔐 API: Username length:', username.length, 'Password length:', password.length);
    
    // Trim whitespace from credentials
    const trimmedUsername = username.trim();
    const trimmedPassword = password.trim();
    
    console.log('🔐 API: Trimmed username:', trimmedUsername, 'Trimmed password length:', trimmedPassword.length);
    
    // Clear any existing state first
    this.clearToken();
    
    try {
      // Force direct API call for login - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/auth/login`;
      
      console.log(`🔐 API: Making direct login request to ${url}`);
      console.log('🔐 API: Request body:', { username: trimmedUsername, password: '***' });
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: trimmedUsername, password: trimmedPassword })
      });
      
      console.log('🔐 API: Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Login HTTP error:', response.status, errorText);
        
        // Try to parse error message
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || 'Invalid username or password');
        } catch {
          throw new Error('Invalid username or password');
        }
      }
      
      const result = await response.json();
      
      console.log('✅ API: Login response received:', {
        hasToken: !!result.access_token,
        hasUser: !!result.user,
        userRole: result.user?.role,
        username: result.user?.username
      });
      
      if (!result.access_token) {
        throw new Error('No access token received from server');
      }
      
      if (!result.user) {
        throw new Error('No user data received from server');
      }
      
      this.setToken(result.access_token);
      
      // Store user with token in localStorage
      if (browser) {
        const userWithToken = {
          ...result.user,
          token: result.access_token,
          access_token: result.access_token
        };
        localStorage.setItem('user', JSON.stringify(userWithToken));
        localStorage.setItem('token', result.access_token); // Double-ensure token is saved
        console.log('🔐 API: User with token stored in localStorage');
        console.log('🔐 API: Token verified in storage:', localStorage.getItem('token') === result.access_token);
      }
      
      return result;
    } catch (error) {
      console.error('❌ API: Login failed:', error);
      this.clearToken();
      
      // Provide more specific error messages
      if (error.message.includes('Invalid username or password')) {
        throw new Error('Invalid username or password. Please check your credentials.');
      } else if (error.message.includes('Failed to fetch')) {
        throw new Error('Connection failed. Please check your network connection.');
      } else {
        throw error;
      }
    }
  }

  async register(username, password, fullName, role = 'student', department = null, level = null, departments = []) {
    const body = { username, password, full_name: fullName, role };
    
    if (role === 'student') {
      body.department = department;
      body.level = level;
    } else if (role === 'teacher' || role === 'admin') {
      body.departments = departments;
    }
    
    const result = await this.request('/auth/register', {
      method: 'POST',
      body
    });
    this.setToken(result.access_token);
    return result;
  }

  logout() {
    this.clearToken();
  }

  // Questions
  async getQuestions() {
    return this.request('/questions');
  }

  async createQuestion(question) {
    return this.request('/questions', {
      method: 'POST',
      body: question
    });
  }

  async updateQuestion(questionId, question) {
    return this.request(`/questions/${questionId}`, {
      method: 'PUT',
      body: question
    });
  }

  async deleteQuestion(questionId) {
    return this.request(`/questions/${questionId}`, {
      method: 'DELETE'
    });
  }

  async clearAllTeacherQuestions() {
    return this.request('/teacher/questions/clear', {
      method: 'DELETE'
    });
  }

  async deleteQuiz(quizId) {
    return this.request(`/quizzes/${quizId}`, {
      method: 'DELETE'
    });
  }

  // Quizzes
  async getQuizzes() {
    // Always bypass cache for quiz list to show live updates
    const apiBase = getApiBase();
    const url = `${apiBase}/quizzes?t=${Date.now()}`;
    const config = {
      headers: {
        'Content-Type': 'application/json'
      }
    };
    if (this._token) {
      config.headers.Authorization = `Bearer ${this._token}`;
    }
    const response = await fetch(url, config);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async createQuiz(quiz) {
    return this.request('/quizzes', {
      method: 'POST',
      body: quiz
    });
  }

  async getQuizQuestions(quizId) {
    // Special handling for quiz questions - backend may return JSON instead of HTTP error
    try {
      const apiBase = getApiBase();
      const url = `${apiBase}/quizzes/${quizId}/questions`;
      const config = {
        headers: {
          'Content-Type': 'application/json'
        }
      };
      if (this._token) {
        config.headers.Authorization = `Bearer ${this._token}`;
      }
      
      const response = await fetch(url, config);
      
      // Always try to parse JSON response first
      const data = await response.json();
      
      // Check if it's a friendly error response (quiz_ended, quiz_already_attempted)
      if (data.quiz_ended || data.quiz_already_attempted) {
        return data; // Return the friendly JSON response
      }
      
      // If not OK and not a friendly response, throw error
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return data;
    } catch (err) {
      // If JSON parsing fails, fall back to regular error
      throw err;
    }
  }

  async submitQuiz(submission) {
    console.log('📤 API: Submitting quiz with data:', {
      quiz_id: submission.quiz_id,
      answers_count: submission.answers?.length || 0
    });
    
    try {
      const result = await this.request('/quizzes/submit', {
        method: 'POST',
        body: submission
      });
      console.log('✅ API: Quiz submission successful:', result);
      return result;
    } catch (error) {
      console.error('❌ API: Quiz submission failed:', error);
      throw error;
    }
  }

  async activateQuiz(quizId) {
    return this.request(`/quizzes/${quizId}/activate`, {
      method: 'PUT'
    });
  }

  async broadcastQuiz(quizId) {
    console.log('📡 API: Broadcasting quiz', quizId);
    const result = await this.request(`/quizzes/${quizId}/broadcast`, {
      method: 'PUT'
    });
    console.log('📡 API: Broadcast result:', result);
    return result;
  }

  async exportQuizPDF(quizId) {
    const apiBase = getApiBase();
    const token = this.token || this._token;
    if (!token) {
      throw new Error('Authentication required');
    }
    const response = await fetch(`${apiBase}/quizzes/${quizId}/export`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      const errorText = await response.text();
      console.error('PDF export failed:', response.status, errorText);
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async exportQuizExcel(quizId) {
    const apiBase = getApiBase();
    const token = this.token || this._token;
    if (!token) {
      throw new Error('Authentication required');
    }
    const response = await fetch(`${apiBase}/quizzes/${quizId}/export/excel`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Excel export failed:', response.status, errorText);
      throw new Error('Export failed');
    }
    return response.blob();
  }

  // Results
  async getLeaderboard(quizId) {
    return this.request(`/leaderboard/${quizId}`);
  }

  async getQuizResults(quizId) {
    return this.request(`/results/${quizId}`);
  }

  // Schedules (DOS)
  async getSchedules() {
    return this.request('/schedules');
  }

  async createSchedule(schedule) {
    return this.request('/schedules', {
      method: 'POST',
      body: schedule
    });
  }

  // Announcements (DOS)
  async getAnnouncements() {
    return this.request('/announcements');
  }

  async createAnnouncement(announcement) {
    return this.request('/announcements', {
      method: 'POST',
      body: announcement
    });
  }

  async deactivateAnnouncement(announcementId) {
    return this.request(`/announcements/${announcementId}/deactivate`, {
      method: 'PUT'
    });
  }

  // Lessons
  async getLessons() {
    return this.request('/lessons');
  }

  async createLesson(lesson) {
    console.log('🔧 API: Creating lesson with data:', lesson);
    
    try {
      // Force direct API call for lesson creation - bypass offline queuing completely
      const apiBase = getApiBase();
      const url = `${apiBase}/lessons`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Authentication required. Please login again.');
        }
      }
      
      console.log(`🔧 API: Making direct lesson creation request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify(lesson)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Lesson creation HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 403) {
          throw new Error('Permission denied. Admin access required.');
        } else {
          throw new Error(`Lesson creation failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: Lesson created successfully:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: Lesson creation failed:', error);
      throw error;
    }
  }

  async deactivateLesson(lessonId) {
    return this.request(`/lessons/${lessonId}/deactivate`, {
      method: 'PUT'
    });
  }

  // Teacher assignments
  async getTeachers() {
    return this.request('/teachers');
  }

  async registerTeacher(username, password, fullName, departments, isClassTeacher = false, classDepartment = '', classLevel = '') {
    console.log('🔧 API: Registering teacher with data:', {
      username,
      fullName,
      departments,
      isClassTeacher,
      classDepartment,
      classLevel
    });
    
    // Validate input data
    if (!username || !password || !fullName) {
      throw new Error('Username, password, and full name are required');
    }
    
    if (!departments || departments.length === 0) {
      throw new Error('At least one department must be selected');
    }
    
    if (isClassTeacher && (!classDepartment || !classLevel)) {
      throw new Error('Class department and level are required for class teachers');
    }
    
    try {
      // Force direct API call for teacher registration - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/admin/register-teacher`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Admin authentication required. Please login again.');
        }
      }
      
      console.log(`🔧 API: Making direct teacher registration request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify({
          username: username.trim(),
          password,
          full_name: fullName.trim(),
          departments: departments
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Teacher registration HTTP error:', response.status, errorText);
        
        // Parse error message from response
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || errorData.message || 'Registration failed');
        } catch {
          // If not JSON, use status-based messages
          if (response.status === 400) {
            throw new Error('Username already exists or invalid data provided');
          } else if (response.status === 401) {
            throw new Error('Authentication failed. Please login as DOS again.');
          } else if (response.status === 403) {
            throw new Error('DOS access required. Only administrators can register teachers.');
          } else {
            throw new Error(`Registration failed with status ${response.status}`);
          }
        }
      }
      
      const result = await response.json();
      
      console.log('✅ API: Teacher registration successful:', {
        teacherId: result.teacher?.id,
        username: result.teacher?.username,
        fullName: result.teacher?.full_name,
        departments: result.teacher?.departments
      });
      
      return result;
    } catch (error) {
      console.error('❌ API: Teacher registration failed:', error);
      
      // Provide more specific error messages
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Connection failed. Please check your network connection and ensure the backend is running.');
      } else if (error.message.includes('Authentication')) {
        throw new Error('Authentication failed. Please logout and login again as DOS.');
      } else {
        throw error;
      }
    }
  }

  async assignLessonToTeacher(teacherId, lessonId) {
    console.log('🔧 API: Assigning lesson to teacher:', { teacherId, lessonId });
    
    try {
      // Force direct API call for lesson assignment - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/teacher-lessons`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Authentication required. Please login again.');
        }
      }
      
      console.log(`🔧 API: Making direct lesson assignment request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify({ teacher_id: teacherId, lesson_id: lessonId })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Lesson assignment HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 403) {
          throw new Error('Permission denied. DOS access required.');
        } else if (response.status === 400) {
          throw new Error('Assignment failed. Teacher may already be assigned to this lesson.');
        } else {
          throw new Error(`Assignment failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: Lesson assignment successful:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: Lesson assignment failed:', error);
      throw error;
    }
  }

  async getTeacherLessons(teacherId) {
    return this.request(`/teacher-lessons/${teacherId}`);
  }

  async removeTeacherLesson(assignmentId) {
    console.log('🔧 API: Removing teacher lesson assignment:', assignmentId);
    
    try {
      // Force direct API call for lesson removal - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/teacher-lessons/${assignmentId}`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Authentication required. Please login again.');
        }
      }
      
      console.log(`🔧 API: Making direct lesson removal request to ${url}`);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Lesson removal HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 403) {
          throw new Error('Permission denied. DOS access required.');
        } else if (response.status === 404) {
          throw new Error('Assignment not found.');
        } else {
          throw new Error(`Removal failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: Lesson removal successful:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: Lesson removal failed:', error);
      throw error;
    }
  }

  // Notifications
  async getNotifications() {
    return this.request('/notifications');
  }

  async markNotificationRead(notificationId) {
    return this.request(`/notifications/${notificationId}/read`, {
      method: 'PUT'
    });
  }

  // Quiz results forwarding
  async forwardQuizResults(quizId) {
    return this.request(`/quiz-results/${quizId}/forward`, {
      method: 'POST'
    });
  }

  // My courses (for teachers)
  async getMyCourses() {
    return this.request('/my-courses');
  }

  // Student management (DOS)
  async getStudents(department = null, level = null) {
    let url = '/admin/students';
    const params = new URLSearchParams();
    
    if (department) params.append('department', department);
    if (level) params.append('level', level);
    
    if (params.toString()) {
      url += '?' + params.toString();
    }
    
    const response = await this.request(url);
    return response.students || [];
  }

  // Download all results
  async downloadAllResultsExcel() {
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/admin/results/download/excel`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) throw new Error('Download failed');
    return response.blob();
  }

  async generateStudentCredentialsPDF(department, level) {
    console.log('🔑 API: Generating student credentials PDF:', { department, level });
    
    try {
      const apiBase = getApiBase();
      const url = `${apiBase}/admin/generate-student-credentials/${encodeURIComponent(department)}/${encodeURIComponent(level)}`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Admin authentication required. Please login again.');
        }
      }
      
      console.log(`🔑 API: Making credentials generation request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Credentials generation HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login as DOS again.');
        } else if (response.status === 403) {
          throw new Error('DOS access required. Only administrators can generate credentials.');
        } else if (response.status === 404) {
          throw new Error(`No students found for ${department} - ${level}`);
        } else {
          throw new Error(`Credentials generation failed: ${response.status}`);
        }
      }
      
      const blob = await response.blob();
      console.log('✅ API: Credentials PDF generated successfully');
      
      return blob;
    } catch (error) {
      console.error('❌ API: Credentials generation failed:', error);
      throw error;
    }
  }

  async downloadAllResultsPDF() {
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/admin/results/download/pdf`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) throw new Error('Download failed');
    return response.blob();
  }

  // Student report download
  async downloadStudentReport(quizId) {
    // Ensure we have a valid token
    let token = this._token;
    if (browser && !token) {
      token = localStorage.getItem('token');
      if (token) {
        this._token = token;
      }
    }
    
    if (!token) {
      throw new Error('Authentication required. Please login again.');
    }
    
    const apiBase = getApiBase();
    const url = `${apiBase}/student-report/${quizId}`;
    
    console.log('📥 Downloading student report for quiz:', quizId);
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.text();
      console.error('❌ Report download failed:', response.status, error);
      throw new Error(error || 'Report generation failed');
    }
    
    console.log('✅ Report downloaded successfully');
    return response.blob();
  }

  // Class teacher management
  async assignClassTeacher(teacherId, department, level) {
    return this.request('/admin/assign-class-teacher', {
      method: 'POST',
      body: { teacher_id: teacherId, department, level }
    });
  }

  async getClassTeachers() {
    return this.request('/admin/class-teachers');
  }

  async uploadStudents(students) {
    console.log('📤 API: Uploading students:', students.length);
    
    try {
      // Force direct API call for student upload - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/teacher/upload-students`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Authentication required. Please login again.');
        }
      }
      
      console.log(`📤 API: Making direct student upload request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify({ students })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Student upload HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 403) {
          throw new Error('Permission denied. Admin access required.');
        } else {
          throw new Error(`Upload failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: Student upload successful:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: Student upload failed:', error);
      throw error;
    }
  }
  
  async uploadStudentFile(file) {
    console.log('📄 API: Processing student file:', file.name);
    
    try {
      const apiBase = getApiBase();
      const url = `${apiBase}/teacher/upload-students-file`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Authentication required. Please login again.');
        }
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      console.log(`📄 API: Making file upload request to ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ File upload HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 400) {
          throw new Error('Invalid file format or content.');
        } else {
          throw new Error(`File processing failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: File processing successful:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: File upload failed:', error);
      throw error;
    }
  }

  async getMyClasses() {
    return this.request('/teacher/my-classes');
  }

  async clearAllStudents() {
    console.log('🗑️ API: Clearing all students');
    
    try {
      // Force direct API call for clearing students - bypass offline queuing
      const apiBase = getApiBase();
      const url = `${apiBase}/admin/clear-all-students`;
      
      // Ensure we have a valid token
      if (browser && !this.token) {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          this.token = storedToken;
        } else {
          throw new Error('Admin authentication required. Please login again.');
        }
      }
      
      console.log(`🗑️ API: Making clear students request to ${url}`);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Clear students HTTP error:', response.status, errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login as DOS again.');
        } else if (response.status === 403) {
          throw new Error('DOS access required. Only administrators can clear students.');
        } else {
          throw new Error(`Clear operation failed: ${response.status}`);
        }
      }
      
      const result = await response.json();
      console.log('✅ API: Students cleared successfully:', result);
      
      return result;
    } catch (error) {
      console.error('❌ API: Clear students failed:', error);
      throw error;
    }
  }

  async downloadQuizStudentsResults(quizId) {
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/quizzes/${quizId}/export`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) throw new Error('Download failed');
    return response.blob();
  }

  // Test authentication and connection
  async testAuth() {
    try {
      const result = await this.request('/auth/test');
      this.connectionTested = true;
      return result;
    } catch (err) {
      this.connectionTested = false;
      throw err;
    }
  }

  // Test basic connection without auth
  async testConnection() {
    try {
      const apiBase = getApiBase();
      const response = await fetch(`${apiBase}/health`, {
        method: 'GET'
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  // Get connection status
  isConnected() {
    return this.connectionTested && !this.isOffline;
  }
  
  // Get API base URL (expose for direct fetch calls)
  get API_BASE() {
    return getApiBase();
  }

  get baseURL() {
    return getApiBase();
  }

  // Get offline status
  getOfflineStatus() {
    return this.isOffline || !navigator.onLine;
  }
  
  // Get current token (expose for direct fetch calls)
  get token() {
    if (browser && !this._token) {
      this._token = localStorage.getItem('token');
    }
    return this._token;
  }
  
  set token(value) {
    this._token = value;
  }

  // Reset teacher password
  async resetTeacherPassword(username) {
    return this.request('/reset-teacher-password', {
      method: 'POST',
      body: { username }
    });
  }

  // Reset teacher password by ID (for DOS)
  async resetTeacherPasswordById(teacherId, newPassword) {
    return this.request(`/admin/reset-teacher-password/${teacherId}?new_password=${encodeURIComponent(newPassword)}`, {
      method: 'POST'
    });
  }

  // Update teacher info
  async updateTeacher(teacherId, teacherData) {
    return this.request(`/admin/teacher/${teacherId}`, {
      method: 'PUT',
      body: teacherData
    });
  }

  // Student performance tracking
  async getStudentProgress() {
    return this.request('/student/progress');
  }

  // Department reports
  async downloadDepartmentReport(params) {
    const query = new URLSearchParams(params).toString();
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/admin/reports/department?${query}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) throw new Error('Report generation failed');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${params.department}_${params.level}_${params.reportType}_report.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    return blob;
  }

  async downloadDepartmentReportExcel(params) {
    const query = new URLSearchParams(params).toString();
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/admin/reports/department/excel?${query}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) throw new Error('Excel report generation failed');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${params.department}_${params.level}_${params.reportType}_report.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    return blob;
  }

  // Review Quiz Endpoints
  async getPendingReviews() {
    return this.request('/teacher/pending-reviews');
  }

  async getAttemptForReview(attemptId) {
    return this.request(`/teacher/review/${attemptId}`);
  }

  async submitReview(attemptId, grades) {
    return this.request(`/teacher/review/${attemptId}/grade`, {
      method: 'POST',
      body: { grades }
    });
  }

  async releaseQuizResults(quizId) {
    return this.request(`/teacher/quiz/${quizId}/release-results`, {
      method: 'POST'
    });
  }

  async getReviewStatus(quizId) {
    return this.request(`/teacher/quiz/${quizId}/review-status`);
  }

  // Report cheating
  async reportCheating(data) {
    return this.request('/report-cheating', {
      method: 'POST',
      body: data
    });
  }
}

export const api = new ApiClient();
