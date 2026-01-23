<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api.js';

  let quizzes = [];
  let loading = false;
  let error = '';
  let pendingReviews = 0;
  let uniqueQuizzes = 0;
  let totalStudents = 0;

  onMount(async () => {
    await loadQuizzes();
  });

  async function loadQuizzes() {
    try {
      loading = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      // Get all teacher's quizzes
      const response = await fetch(`${apiBase}/quizzes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load quizzes');
      }
      
      quizzes = await response.json();
      
      // Calculate statistics from quizzes
      uniqueQuizzes = quizzes.length;
      
      // Count pending reviews (quizzes with submissions but results not released)
      let pending = 0;
      let students = new Set();
      
      for (const quiz of quizzes) {
        try {
          const submissionsResponse = await fetch(`${apiBase}/teacher/quiz-submissions/${quiz.id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (submissionsResponse.ok) {
            const data = await submissionsResponse.json();
            if (data.submissions && data.submissions.length > 0) {
              if (!data.results_released) {
                pending += data.submissions.length;
              }
              data.submissions.forEach(sub => students.add(sub.student_id));
            }
          }
        } catch (err) {
          console.error(`Failed to load submissions for quiz ${quiz.id}:`, err);
        }
      }
      
      pendingReviews = pending;
      totalStudents = students.size;
      
    } catch (err) {
      error = err.message;
      console.error('Load quizzes error:', err);
    } finally {
      loading = false;
    }
  }

  function viewSubmissions(quizId) {
    goto(`/teacher/reviews/quiz/${quizId}`);
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
  }
</script>

<svelte:head>
  <title>Review Submissions - Teacher Dashboard</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">📋 Review Quiz Submissions</h1>
          <p class="text-gray-600">Review student submissions and release results</p>
        </div>
        <div class="flex items-center space-x-4">
          <button 
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            on:click={loadQuizzes}
            disabled={loading}
          >
            {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
          </button>
          <a 
            href="/teacher" 
            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back to Dashboard
          </a>
        </div>
      </div>
    </div>

    {#if error}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
        <div class="flex">
          <div class="text-red-400">⚠️</div>
          <div class="ml-3 text-red-700">{error}</div>
        </div>
      </div>
    {/if}

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center">
          <div class="text-4xl mr-4">⏳</div>
          <div>
            <div class="text-3xl font-bold text-orange-600">{pendingReviews}</div>
            <div class="text-gray-600 text-sm">Pending Reviews</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center">
          <div class="text-4xl mr-4">📝</div>
          <div>
            <div class="text-3xl font-bold text-blue-600">{uniqueQuizzes}</div>
            <div class="text-gray-600 text-sm">Unique Quizzes</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center">
          <div class="text-4xl mr-4">👥</div>
          <div>
            <div class="text-3xl font-bold text-green-600">{totalStudents}</div>
            <div class="text-gray-600 text-sm">Students</div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {#if loading}
        <div class="text-center py-12">
          <div class="text-4xl mb-4">⏳</div>
          <p class="text-gray-600">Loading quizzes...</p>
        </div>
      {:else if quizzes.length === 0}
        <div class="text-center py-12">
          <div class="text-6xl mb-4">📝</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No Quizzes Yet</h3>
          <p class="text-gray-600">Create a quiz first to see submissions here.</p>
        </div>
      {:else}
        <div class="space-y-4">
          {#each quizzes as quiz}
            <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all">
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center mb-3">
                    <span class="text-2xl mr-3">📝</span>
                    <div>
                      <h3 class="text-lg font-semibold text-gray-900">{quiz.title}</h3>
                      <p class="text-sm text-gray-600">{quiz.department} - {quiz.level}</p>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Status</div>
                      <div class="text-sm font-medium {quiz.is_active ? 'text-green-600' : 'text-gray-600'}">
                        {quiz.is_active ? '✅ Active' : '⏸️ Inactive'}
                      </div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Results</div>
                      <div class="text-sm font-medium {quiz.results_released ? 'text-green-600' : 'text-orange-600'}">
                        {quiz.results_released ? '✅ Released' : '⏳ Pending'}
                      </div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Created</div>
                      <div class="text-sm font-medium text-gray-700">{formatDate(quiz.created_at)}</div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Quiz ID</div>
                      <div class="text-sm font-medium text-gray-700">#{quiz.id}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-end">
                <button 
                  class="bg-gradient-to-r from-green-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105"
                  on:click={() => viewSubmissions(quiz.id)}
                >
                  🔍 View Submissions →
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
</style>
