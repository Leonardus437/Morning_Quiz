<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api.js';

  let pendingReviews = [];
  let loading = false;
  let error = '';

  onMount(async () => {
    await loadPendingReviews();
  });

  async function loadPendingReviews() {
    try {
      loading = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/pending-reviews`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load pending reviews');
      }
      
      pendingReviews = await response.json();
    } catch (err) {
      error = err.message;
      console.error('Load pending reviews error:', err);
    } finally {
      loading = false;
    }
  }

  function viewReview(attemptId) {
    goto(`/teacher/reviews/${attemptId}`);
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
  }
</script>

<svelte:head>
  <title>Pending Reviews - Teacher Dashboard</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">📋 Pending Reviews</h1>
          <p class="text-gray-600">Review student quiz submissions and release results</p>
        </div>
        <div class="flex items-center space-x-4">
          <button 
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            on:click={loadPendingReviews}
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

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center">
          <div class="text-3xl mr-4">⏳</div>
          <div>
            <div class="text-2xl font-bold text-orange-600">{pendingReviews.length}</div>
            <div class="text-gray-600 text-sm">Pending Reviews</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center">
          <div class="text-3xl mr-4">📝</div>
          <div>
            <div class="text-2xl font-bold text-blue-600">{new Set(pendingReviews.map(r => r.quiz_title)).size}</div>
            <div class="text-gray-600 text-sm">Unique Quizzes</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center">
          <div class="text-3xl mr-4">👥</div>
          <div>
            <div class="text-2xl font-bold text-green-600">{new Set(pendingReviews.map(r => r.student_name)).size}</div>
            <div class="text-gray-600 text-sm">Students</div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {#if loading}
        <div class="text-center py-12">
          <div class="text-4xl mb-4">⏳</div>
          <p class="text-gray-600">Loading pending reviews...</p>
        </div>
      {:else if pendingReviews.length === 0}
        <div class="text-center py-12">
          <div class="text-6xl mb-4">✅</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">All Caught Up!</h3>
          <p class="text-gray-600">No pending reviews at the moment.</p>
        </div>
      {:else}
        <div class="space-y-4">
          {#each pendingReviews as review}
            <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all bg-gradient-to-r from-orange-50 to-yellow-50">
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center mb-3">
                    <span class="text-2xl mr-3">📝</span>
                    <div>
                      <h3 class="text-lg font-semibold text-gray-900">{review.quiz_title}</h3>
                      <p class="text-sm text-gray-600">Student: <span class="font-medium">{review.student_name}</span></p>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">AI Score</div>
                      <div class="text-lg font-bold text-blue-600">{review.score}</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Submitted</div>
                      <div class="text-sm font-medium text-gray-700">{formatDate(review.submitted_at)}</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Status</div>
                      <div class="text-sm font-medium text-orange-600">⏳ Pending Review</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                      <div class="text-xs text-gray-500 mb-1">Attempt ID</div>
                      <div class="text-sm font-medium text-gray-700">#{review.attempt_id}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-end">
                <button 
                  class="bg-gradient-to-r from-green-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105"
                  on:click={() => viewReview(review.attempt_id)}
                >
                  🔍 Review Submission →
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
