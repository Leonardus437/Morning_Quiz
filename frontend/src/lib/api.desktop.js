// Desktop-optimized API configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

class DesktopAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Auth methods
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  }

  logout() {
    this.clearToken();
  }

  // Quiz methods
  async getQuizzes() {
    return this.request('/quizzes');
  }

  async getQuizQuestions(quizId) {
    return this.request(`/quizzes/${quizId}/questions`);
  }

  async submitQuiz(submission) {
    return this.request('/quizzes/submit', {
      method: 'POST',
      body: JSON.stringify(submission)
    });
  }

  // Health check for desktop
  async checkConnection() {
    try {
      await this.request('/health');
      return true;
    } catch {
      return false;
    }
  }
}

export const api = new DesktopAPI();