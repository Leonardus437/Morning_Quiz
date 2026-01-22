<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';
  import { notificationStore } from '$lib/notificationStore.js';

  let username = '';
  let password = '';
  let loading = false;
  let error = '';
  let quizzes = [];
  let showLoginModal = false;
  let isUpdating = false;
  let lastUpdateTime = new Date();

  let isLoggedIn = false;
  let quizRefreshInterval;
  let notificationInterval;
  let seenNotificationIds = new Set();
  
  // Carousel state
  let currentSlide = 0;
  let carouselInterval;
  const slides = [
    { image: '/images/IMG-20241006-WA0047.jpg', title: 'Excellence in Assessment', subtitle: 'Professional Quiz Platform for Modern Education' },
    { image: '/images/IMG-20241006-WA0050.jpg', title: 'Real-Time Results', subtitle: 'Instant Feedback & Performance Analytics' },
    { image: '/images/IMG-20241006-WA0051.jpg', title: 'Advanced Testing', subtitle: 'Comprehensive Knowledge Evaluation System' },
    { image: '/images/IMG-20241006-WA0079.jpg', title: 'Smart Learning', subtitle: 'Technology-Driven Educational Excellence' }
  ];
  
  // Update login status manually to prevent reactive loops
  user.subscribe(userData => {
    isLoggedIn = userData !== null;
  });

  onMount(async () => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      try {
        const userData = JSON.parse(storedUser);
        if (userData.role === 'student') {
          api.setToken(storedToken);
          user.login(userData);
          await loadQuizzes();
          startQuizRefresh();
          startNotificationPolling();
        }
      } catch (err) {
        console.error('Session restore failed:', err);
      }
    } else if (isLoggedIn) {
      await loadQuizzes();
      startQuizRefresh();
      startNotificationPolling();
    }
    
    // Start carousel auto-rotation
    startCarousel();
    
    return () => {
      if (quizRefreshInterval) {
        clearInterval(quizRefreshInterval);
      }
      if (notificationInterval) {
        clearInterval(notificationInterval);
      }
      if (carouselInterval) {
        clearInterval(carouselInterval);
      }
    };
  });
  
  function startCarousel() {
    carouselInterval = setInterval(() => {
      currentSlide = (currentSlide + 1) % slides.length;
    }, 4000);
  }
  
  function goToSlide(index) {
    currentSlide = index;
    clearInterval(carouselInterval);
    startCarousel();
  }

  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password';
      return;
    }

    loading = true;
    error = '';

    try {
      console.log(' Attempting login for:', username);
      
      // Clear any existing tokens first
      api.clearToken();
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      const result = await api.login(username, password);
      console.log(' Login successful:', result);
      
      if (!result || !result.access_token || !result.user) {
        throw new Error('Invalid login response from server');
      }
      
      api.setToken(result.access_token);
      user.login(result.user);
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('token', result.access_token);
      
      if (result.user.role === 'admin') {
        goto('/admin');
      } else if (result.user.role === 'teacher') {
        goto('/teacher');
      } else {
        showLoginModal = false;
        await loadQuizzes();
        startNotificationPolling();
      }
    } catch (err) {
      console.error(' Login error:', err);
      error = err.message || 'Login failed. Please try again.';
      
      // Clear any partial state
      api.clearToken();
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } finally {
      loading = false;
    }
  }

  async function loadQuizzes() {
    try {
      console.log(' Loading quizzes for student:', $user?.username);
      const rawQuizzes = await api.getQuizzes();
      console.log(' Received quizzes from API:', rawQuizzes.length, 'quizzes');
      
      // Log debug info from backend
      rawQuizzes.forEach(quiz => {
        if (quiz.debug_info) {
          console.log(`DEBUG ${quiz.title}:`, quiz.debug_info);
        }
      });
      
      const processedQuizzes = rawQuizzes.map(quiz => {
        // Use backend's is_expired calculation - it's already correct
        console.log(` Quiz: ${quiz.title} | Active: ${quiz.is_active} | Expired: ${quiz.is_expired}`);
        
        return quiz;
      });
      
      quizzes = processedQuizzes;
      console.log(' Quizzes updated in UI:', quizzes.length);
    } catch (err) {
      console.error(' Quiz loading error:', err);
    }
  }

  function startQuizRefresh() {
    if (quizRefreshInterval) {
      clearInterval(quizRefreshInterval);
    }
    
    console.log(' Starting quiz auto-refresh every 2 seconds');
    
    quizRefreshInterval = setInterval(async () => {
      if (isLoggedIn) {
        try {
          await loadQuizzes();
        } catch (err) {
          console.error(' Auto-refresh error:', err);
        }
      }
    }, 2000);
  }

  function startNotificationPolling() {
    if (notificationInterval) {
      clearInterval(notificationInterval);
    }
    
    // Initialize with existing notification IDs to avoid showing old ones on first load
    api.getNotifications().then(notifications => {
      notifications.forEach(n => seenNotificationIds.add(n.id));
    }).catch(() => {});
    
    notificationInterval = setInterval(async () => {
      if (isLoggedIn) {
        try {
          const notifications = await api.getNotifications();
          
          // Show only NEW unread notifications (ones we haven't seen before)
          const newNotifications = notifications.filter(n => 
            !n.is_read && !seenNotificationIds.has(n.id)
          );
          
          if (newNotifications.length > 0) {
            newNotifications.forEach(notification => {
              seenNotificationIds.add(notification.id);
              notificationStore.add({
                type: notification.type,
                title: notification.title,
                message: notification.message
              });
            });
          }
        } catch (err) {
          console.error('Notification polling error:', err);
        }
      }
    }, 5000);
  }

  function handleLogout() {
    if (quizRefreshInterval) {
      clearInterval(quizRefreshInterval);
    }
    if (notificationInterval) {
      clearInterval(notificationInterval);
    }
    api.logout();
    user.logout();
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    quizzes = [];
  }

  async function startQuiz(quiz) {
    // Double-check if quiz is still available before starting
    if (quiz.is_expired) {
      alert(' This quiz has ended and is no longer available.');
      return;
    }
    if (!quiz.is_active) {
      alert(' This quiz is not currently active.');
      return;
    }
    goto(`/quiz/${quiz.id}`);
  }
  
  async function refreshQuizzes() {
    await loadQuizzes();
  }
</script>

<svelte:head>
  <title>Quiz System - Excellence in Education</title>
  <style>
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInLeft {
      from { opacity: 0; transform: translateX(-50px); }
      to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
      from { opacity: 0; transform: translateX(50px); }
      to { opacity: 1; transform: translateX(0); }
    }
    @keyframes zoomRotate {
      0% { transform: scale(1) rotate(0deg); }
      50% { transform: scale(1.05) rotate(0.5deg); }
      100% { transform: scale(1.1) rotate(1deg); }
    }
    .animate-fadeInUp { animation: fadeInUp 0.8s ease-out forwards; }
    .animate-slideInLeft { animation: slideInLeft 0.8s ease-out forwards; }
    .animate-slideInRight { animation: slideInRight 0.8s ease-out forwards; }
    .animate-zoomRotate { animation: zoomRotate 6s ease-in-out infinite; }
  </style>
</svelte:head>

{#if !isLoggedIn}
  <div class="relative min-h-screen bg-white overflow-hidden">
    <!-- Modern Navigation -->
    <nav class="absolute top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-lg shadow-lg">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-gradient-to-br from-red-600 via-blue-600 to-green-600 rounded-2xl flex items-center justify-center shadow-xl transform hover:rotate-12 transition-transform duration-300">
              <span class="text-white font-black text-2xl"></span>
            </div>
            <div>
              <h1 class="text-gray-900 font-black text-2xl tracking-tight">TVET QUIZ</h1>
              <p class="text-blue-600 text-xs font-bold uppercase tracking-widest">Professional Assessment Platform</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <button on:click={() => showLoginModal = true} class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-3 rounded-full font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
              Student Login
            </button>
            <a href="/teacher" class="text-gray-700 hover:text-blue-600 font-bold transition-colors duration-300">
              Teacher
            </a>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Carousel Section -->
    <div class="relative h-screen">
      <!-- Enhanced Carousel Images -->
      <div class="absolute inset-0 overflow-hidden">
        {#each slides as slide, i}
          <div class="absolute inset-0 transition-all duration-1500 ease-in-out {i === currentSlide ? 'opacity-100 scale-100' : 'opacity-0 scale-110'}">
            <div class="absolute inset-0 bg-gradient-to-r from-blue-900/90 via-blue-800/70 to-purple-900/60 z-10"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent z-10"></div>
            <img 
              src={slide.image} 
              alt={slide.title}
              class="w-full h-full object-cover {i === currentSlide ? 'animate-zoomRotate' : ''}"
              style="filter: brightness(0.9) contrast(1.1) saturate(1.2);"
              on:error={(e) => {
                e.target.style.display = 'none';
                e.target.parentElement.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
              }}
            />
            <!-- Floating particles -->
            <div class="absolute inset-0 z-20 pointer-events-none">
              <div class="absolute top-1/4 left-1/4 w-2 h-2 bg-white/30 rounded-full animate-ping" style="animation-delay: 0s; animation-duration: 3s;"></div>
              <div class="absolute top-1/3 right-1/3 w-1 h-1 bg-blue-300/40 rounded-full animate-pulse" style="animation-delay: 1s; animation-duration: 4s;"></div>
              <div class="absolute bottom-1/3 left-1/2 w-1.5 h-1.5 bg-purple-300/30 rounded-full animate-bounce" style="animation-delay: 2s; animation-duration: 5s;"></div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Hero Content -->
      <div class="relative z-20 h-full flex items-center">
        <div class="max-w-7xl mx-auto px-6 w-full">
          <div class="max-w-3xl">
            {#each slides as slide, i}
              <div class="transition-all duration-1000 ease-out {i === currentSlide ? 'opacity-100 translate-x-0 translate-y-0' : 'opacity-0 -translate-x-20 translate-y-10 absolute'}">

                <h1 class="text-5xl md:text-7xl font-black text-white mb-6 leading-tight transform {i === currentSlide ? 'animate-slideInLeft' : ''}" style="animation-delay: 0.5s; text-shadow: 3px 3px 8px rgba(0,0,0,0.7); letter-spacing: -0.02em;">
                  {slide.title}
                </h1>
                <p class="text-xl md:text-3xl text-blue-50 mb-12 font-light tracking-wide transform {i === currentSlide ? 'animate-slideInRight' : ''}" style="animation-delay: 0.7s; text-shadow: 2px 2px 4px rgba(0,0,0,0.6);">
                  {slide.subtitle}
                </p>
                <div class="flex flex-wrap gap-6 transform {i === currentSlide ? 'animate-fadeInUp' : ''}" style="animation-delay: 0.9s;">
                  <button on:click={() => showLoginModal = true} class="group relative bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 text-white px-16 py-5 rounded-full font-bold text-lg shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-500 overflow-hidden">
                    <span class="relative z-10 flex items-center gap-3">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                      START ASSESSMENT
                    </span>
                    <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  </button>
                  <button on:click={() => goto('/teacher')} class="bg-white/10 backdrop-blur-md hover:bg-white/20 text-white px-12 py-5 rounded-full font-semibold text-lg border-2 border-white/30 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
                    Teacher Portal →
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Enhanced Carousel Indicators -->
      <div class="absolute bottom-12 left-0 right-0 z-30">
        <div class="max-w-7xl mx-auto px-6">
          <div class="flex justify-center gap-4">
            {#each slides as _, i}
              <button 
                on:click={() => goToSlide(i)}
                class="relative h-3 rounded-full transition-all duration-500 transform hover:scale-125 {i === currentSlide ? 'w-20 bg-gradient-to-r from-white via-blue-200 to-white shadow-lg' : 'w-10 bg-white/60 hover:bg-white/80'}"
              >
                {#if i === currentSlide}
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent rounded-full animate-pulse"></div>
                {/if}
              </button>
            {/each}
          </div>
          <div class="text-center mt-4">
            <p class="text-white/80 text-sm font-medium">
              {currentSlide + 1} of {slides.length}
            </p>
          </div>
        </div>
      </div>
    </div>

    <footer class="relative z-10 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white py-12">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 class="font-black text-xl mb-4">TVET QUIZ SYSTEM</h3>
            <p class="text-gray-400 text-sm leading-relaxed">Professional assessment platform for technical and vocational education excellence.</p>
          </div>
          <div>
            <h4 class="font-bold text-sm uppercase tracking-wider mb-4 text-blue-400">Quick Links</h4>
            <div class="space-y-2">
              <a href="/teacher" class="block text-gray-400 hover:text-white transition-colors text-sm">Teacher Portal</a>
              <a href="/admin" class="block text-gray-400 hover:text-white transition-colors text-sm">Admin Dashboard</a>
            </div>
          </div>
          <div>
            <h4 class="font-bold text-sm uppercase tracking-wider mb-4 text-blue-400">Contact</h4>
            <p class="text-gray-400 text-sm">Developed by Trainer Leonard</p>
            <p class="text-gray-500 text-xs mt-2">Technical & Vocational Education</p>
          </div>
        </div>
        <div class="border-t border-gray-700 pt-6 text-center">
          <p class="text-gray-400 text-sm">&copy; 2025 TVET Quiz System. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>

  {#if showLoginModal}
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" on:click={() => showLoginModal = false}>
      <div class="bg-white max-w-md w-full shadow-2xl rounded-2xl border border-gray-100 transform hover:scale-105 transition-all duration-300" on:click|stopPropagation>
        <div class="text-center p-8 pb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-green-600 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span class="text-2xl text-white"></span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Student Login</h2>
          <p class="text-gray-600 text-sm font-medium">Access your quiz dashboard</p>
        </div>
        
        <div class="px-8 pb-8">
          {#if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div class="flex items-start">
                <div class="text-red-500 text-lg mr-3"></div>
                <div class="text-red-700 text-sm font-medium">{error}</div>
              </div>
            </div>
          {/if}

          <form on:submit|preventDefault={handleLogin} class="space-y-6">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-700">Username</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors bg-white text-gray-900 placeholder-gray-500 font-medium"
                type="text"
                bind:value={username}
                placeholder="Enter your username"
                disabled={loading}
              />
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-700">Password</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors bg-white text-gray-900 placeholder-gray-500 font-medium"
                type="password"
                bind:value={password}
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            <button class="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:transform-none shadow-lg" type="submit" disabled={loading}>
              {#if loading}
                <div class="flex items-center justify-center">
                  <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3"></div>
                  <span>Signing In...</span>
                </div>
              {:else}
                <span class="flex items-center justify-center">
                  Sign In to Dashboard
                </span>
              {/if}
            </button>
          </form>

          <div class="mt-6 text-center">
            <button 
              class="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors"
              on:click={() => showLoginModal = false}
            >
               Close
            </button>
          </div>
          
          <div class="mt-6 pt-4 border-t border-gray-100">
            <p class="text-center text-sm text-gray-600 mb-3 font-medium">
              Need access to other portals?
            </p>
            <div class="flex justify-center space-x-6">
              <a href="/teacher" class="inline-flex items-center text-green-600 hover:text-green-800 font-semibold text-sm transition-colors">
                Teacher Portal
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
{:else}
  <div class="min-h-screen bg-gray-50">
    <div class="cpfc-nav">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary flex items-center justify-center font-black text-light">TQ</div>
            <div>
              <h1 class="text-primary font-black text-lg">QUIZ SYSTEM</h1>
              <p class="text-secondary text-xs">Welcome, {$user.full_name || $user.username}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <button class="btn-cpfc-red" on:click={handleLogout}>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-12">
      <div class="mb-12">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-4xl font-black text-primary mb-2">AVAILABLE QUIZZES</h2>
            <p class="text-secondary text-lg">Select a quiz to begin your assessment</p>
          </div>
          <a href="/performance" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
             My Performance
          </a>
        </div>
      </div>

      {#if quizzes.length === 0}
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-16 text-center">
          <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center text-5xl mx-auto mb-6">
            <span class="text-blue-600"></span>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">NO ACTIVE QUIZZES</h3>
          <p class="text-gray-600">Check back later for new assessments</p>
          <button on:click={refreshQuizzes} class="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
             Refresh Now
          </button>
        </div>
      {:else}
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {#each quizzes as quiz}
            <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div class="bg-gradient-to-r from-blue-600 to-blue-800 p-6 text-white">
                <div class="flex items-start justify-between mb-3">
                  <h3 class="text-xl font-bold leading-tight">{quiz.title}</h3>
                  {#if quiz.is_active}
                    <span class="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                       Active
                    </span>
                  {:else}
                    <span class="bg-gray-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                       Inactive
                    </span>
                  {/if}
                </div>
                <div class="text-blue-100 text-sm font-medium">
                   Assessment Ready
                </div>
              </div>
              
              <div class="p-6">
                <p class="text-gray-700 mb-6 leading-relaxed">{quiz.description}</p>
                
                <div class="space-y-4 mb-6">
                  <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span class="text-blue-600 font-bold text-sm"></span>
                    </div>
                    <div>
                      <div class="text-gray-900 font-semibold text-sm">Duration</div>
                      <div class="text-gray-600 text-sm">{quiz.duration_minutes} minutes</div>
                    </div>
                  </div>
                  
                  <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <span class="text-green-600 font-bold text-sm"></span>
                    </div>
                    <div>
                      <div class="text-gray-900 font-semibold text-sm">Scheduled</div>
                      <div class="text-gray-600 text-sm">{new Date(quiz.scheduled_time).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>

                <!-- Quiz Status Info -->
                {#if quiz.already_attempted}
                  <div class="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200 mb-4">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span class="text-blue-600 font-bold text-sm"></span>
                    </div>
                    <div>
                      <div class="text-blue-900 font-semibold text-sm">Already Completed</div>
                      <div class="text-blue-700 text-xs">You have submitted this quiz</div>
                    </div>
                  </div>
                {:else if quiz.is_expired}
                  <div class="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200 mb-4">
                    <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                      <span class="text-red-600 font-bold text-sm"></span>
                    </div>
                    <div>
                      <div class="text-red-900 font-semibold text-sm">Quiz Ended</div>
                      <div class="text-red-700 text-xs">Time expired</div>
                    </div>
                  </div>
                {:else if quiz.is_active}
                  <div class="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200 mb-4">
                    <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <span class="text-green-600 font-bold text-sm"></span>
                    </div>
                    <div>
                      <div class="text-green-900 font-semibold text-sm">Available Now</div>
                      <div class="text-green-700 text-xs">Start immediately</div>
                    </div>
                  </div>
                {/if}

                <button
                  class="w-full py-4 px-6 rounded-lg font-bold text-base transition-all duration-300 {quiz.is_active && !quiz.is_expired && !quiz.already_attempted ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}"
                  on:click={() => startQuiz(quiz)}
                  disabled={!quiz.is_active || quiz.is_expired || quiz.already_attempted}
                >
                  {#if quiz.already_attempted}
                     Completed
                  {:else if quiz.is_expired}
                     Quiz Ended
                  {:else if quiz.is_active}
                     Start Quiz Now
                  {:else}
                     Not Available
                  {/if}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}