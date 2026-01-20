<script>
  import { LayoutDashboard, Bell, RefreshCw, LogOut, BookOpen, Users, FileQuestion, Target, GraduationCap } from 'lucide-svelte';
  
  export let user;
  export let activeTab;
  export let unreadCount = 0;
  export let loading = false;
  export let onRefresh;
  export let onLogout;
  export let onTabChange;
</script>

<!-- Modern Professional Header -->
<header class="bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 shadow-2xl border-b-4 border-blue-500">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center py-6">
      <!-- Logo & Branding -->
      <div class="flex items-center space-x-4">
        <div class="relative">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-400 via-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300 border-2 border-white/20">
            <GraduationCap class="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
          <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 rounded-full border-2 border-slate-900 animate-pulse"></div>
        </div>
        <div>
          <h1 class="text-3xl font-black text-white tracking-tight">TVET Quiz System</h1>
          <p class="text-blue-200 text-sm font-semibold flex items-center gap-2">
            <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            Teacher Dashboard
          </p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center space-x-4">
        <!-- Notifications -->
        <button 
          class="relative p-3 text-white/80 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group"
          on:click={() => onTabChange('notifications')}
        >
          <Bell class="w-6 h-6 group-hover:animate-bounce" />
          {#if unreadCount > 0}
            <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold animate-pulse shadow-lg">
              {unreadCount}
            </span>
          {/if}
        </button>
        
        <!-- Refresh -->
        <button 
          class="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-4 py-3 rounded-xl transition-all duration-300 backdrop-blur-sm border border-white/20 hover:border-white/40 group"
          on:click={onRefresh}
          disabled={loading}
        >
          <RefreshCw class="w-5 h-5 {loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}" />
          <span class="font-semibold">Refresh</span>
        </button>
        
        <!-- User Info -->
        <div class="flex items-center gap-3 bg-white/10 px-4 py-3 rounded-xl backdrop-blur-sm border border-white/20">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'T'}
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-white">{user?.full_name || user?.username}</div>
            <div class="text-xs text-blue-200 font-medium">Teacher Account</div>
          </div>
        </div>
        
        <!-- Logout -->
        <button 
          class="flex items-center gap-2 bg-red-500/20 hover:bg-red-500 text-white px-4 py-3 rounded-xl transition-all duration-300 border border-red-500/50 hover:border-red-500 group"
          on:click={onLogout}
        >
          <LogOut class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          <span class="font-semibold">Sign Out</span>
        </button>
      </div>
    </div>
  </div>
</header>

<!-- Modern Navigation Tabs -->
<div class="bg-white shadow-md border-b border-gray-200">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex space-x-1 py-2">
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'dashboard' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('dashboard')}
      >
        <LayoutDashboard class="w-5 h-5" />
        Dashboard
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'notifications' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('notifications')}
      >
        <Bell class="w-5 h-5" />
        Notifications
        {#if unreadCount > 0}
          <span class="ml-1 bg-red-500 text-white text-xs px-2 py-1 rounded-full font-bold">{unreadCount}</span>
        {/if}
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'create-question' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('create-question')}
      >
        <FileQuestion class="w-5 h-5" />
        Add Question
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'create-quiz' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('create-quiz')}
      >
        <Target class="w-5 h-5" />
        Create Quiz
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'quizzes' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('quizzes')}
      >
        <Target class="w-5 h-5" />
        My Quizzes
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'courses' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('courses')}
      >
        <BookOpen class="w-5 h-5" />
        My Courses
      </button>
      
      <button
        class="flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-300 {activeTab === 'students' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
        on:click={() => onTabChange('students')}
      >
        <Users class="w-5 h-5" />
        Students
      </button>
    </div>
  </div>
</div>

<style>
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  button {
    animation: slideIn 0.3s ease-out;
  }
</style>
