<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  
  let username = '';
  let password = '';
  let loading = false;
  let error = '';
  let success = '';
  let isLoggedIn = false;
  let user = null;
  let activeTab = 'overview';
  
  // Data
  let lessons = [];
  let teachers = [];
  let students = [];
  let teacherLessons = [];
  let selectedTeacher = null;
  let selectedDepartment = '';
  let filteredLessons = [];
  
  const departments = [
    'Software Development',
    'Computer System and Architecture', 
    'Land Surveying',
    'Building Construction'
  ];
  
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  
  onMount(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        if (userData.role === 'admin') {
          user = userData;
          isLoggedIn = true;
          api.setToken(storedToken);
          loadData();
        }
      } catch (e) {
        console.error('Auth error:', e);
      }
    }
  });

  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password';
      return;
    }

    loading = true;
    error = '';

    try {
      const result = await api.login(username, password);
      
      if (result.user.role !== 'admin') {
        throw new Error('DOS access required');
      }
      
      user = result.user;
      isLoggedIn = true;
      
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      api.setToken(result.access_token);
      
      await loadData();
      
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function handleLogout() {
    api.logout();
    isLoggedIn = false;
    user = null;
  }
  
  async function loadData() {
    try {
      loading = true;
      lessons = await api.getLessons();
      teachers = await api.getTeachers();
      students = await api.getStudents();
    } catch (err) {
      error = 'Failed to load data';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>NEW DOS Dashboard - Clean Version</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
  {#if !isLoggedIn}
    <div class="flex items-center justify-center min-h-screen p-4">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-3xl shadow-2xl p-8">
          <div class="text-center mb-8">
            <div class="w-20 h-20 bg-gradient-to-br from-green-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span class="text-3xl text-white"></span>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">NEW DOS Portal</h1>
            <p class="text-green-600 font-bold">Clean Version - No Quiz Management</p>
          </div>
          
          {#if error}
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
              <div class="text-red-700 text-sm font-medium">{error}</div>
            </div>
          {/if}

          <form on:submit|preventDefault={handleLogin} class="space-y-6">
            <input
              class="w-full px-4 py-3 border rounded-xl"
              type="text"
              bind:value={username}
              placeholder="Username"
              disabled={loading}
            />
            <input
              class="w-full px-4 py-3 border rounded-xl"
              type="password"
              bind:value={password}
              placeholder="Password"
              disabled={loading}
            />
            <button 
              class="w-full bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700" 
              type="submit" 
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  {:else}
    <div class="min-h-screen">
      <header class="bg-white shadow-lg border-b">
        <div class="max-w-7xl mx-auto px-4 py-6">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-2xl font-bold text-green-600"> NEW DOS Dashboard</h1>
              <p class="text-gray-600">Clean Version - {user.full_name}</p>
            </div>
            <button 
              class="bg-red-500 text-white px-6 py-2 rounded-xl hover:bg-red-600"
              on:click={handleLogout}
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div class="max-w-7xl mx-auto px-4 py-8">
        {#if error}
          <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
            <div class="text-red-700 font-medium">{error}</div>
          </div>
        {/if}

        {#if success}
          <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-r-lg">
            <div class="text-green-700 font-medium">{success}</div>
          </div>
        {/if}

        <div class="bg-white rounded-2xl shadow-lg mb-8 p-2">
          <div class="flex gap-2">
            <button
              class="px-6 py-3 rounded-xl font-medium {activeTab === 'overview' ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'overview'}
            >
               Overview
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium {activeTab === 'lessons' ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'lessons'}
            >
               Lessons
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium {activeTab === 'teachers' ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'teachers'}
            >
               Teachers
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium {activeTab === 'students' ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'students'}
            >
               Students
            </button>
          </div>
        </div>

        {#if activeTab === 'overview'}
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
              <p class="text-blue-100">Total Lessons</p>
              <p class="text-3xl font-bold">{lessons.length}</p>
            </div>
            <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
              <p class="text-green-100">Teachers</p>
              <p class="text-3xl font-bold">{teachers.length}</p>
            </div>
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
              <p class="text-purple-100">Students</p>
              <p class="text-3xl font-bold">{students.length}</p>
            </div>
            <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
              <p class="text-orange-100">Departments</p>
              <p class="text-3xl font-bold">{departments.length}</p>
            </div>
          </div>
        {/if}

        {#if activeTab === 'lessons'}
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-xl font-bold mb-4">All Lessons ({lessons.length})</h3>
            <div class="space-y-2">
              {#each lessons as lesson}
                <div class="border p-4 rounded-xl">
                  <h4 class="font-bold">{lesson.title}</h4>
                  <p class="text-sm text-gray-600">{lesson.code} - {lesson.department}</p>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        {#if activeTab === 'teachers'}
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-xl font-bold mb-4">All Teachers ({teachers.length})</h3>
            <div class="space-y-2">
              {#each teachers as teacher}
                <div class="border p-4 rounded-xl">
                  <h4 class="font-bold">{teacher.full_name}</h4>
                  <p class="text-sm text-gray-600">@{teacher.username}</p>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        {#if activeTab === 'students'}
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-xl font-bold mb-4">All Students ({students.length})</h3>
            {#if students.length === 0}
              <p class="text-gray-600 text-center py-8">No students registered yet</p>
            {:else}
              <div class="space-y-2">
                {#each students.slice(0, 20) as student}
                  <div class="border p-4 rounded-xl">
                    <h4 class="font-bold">{student.full_name || student.username}</h4>
                    <p class="text-sm text-gray-600">{student.department} - {student.level}</p>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
