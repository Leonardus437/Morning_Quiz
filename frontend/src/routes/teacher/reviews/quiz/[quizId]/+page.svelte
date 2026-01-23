<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api.js';

  let quizId = $page.params.quizId;
  let submissions = [];
  let quizTitle = '';
  let resultsReleased = false;
  let loading = false;
  let error = '';
  let releasing = false;

  onMount(async () => {
    await loadSubmissions();
  });

  async function loadSubmissions() {
    try {
      loading = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      console.log('[Submissions] Loading for quiz:', quizId);
      console.log('[Submissions] API Base:', apiBase);
      console.log('[Submissions] Token exists:', !!token);
      
      const url = `${apiBase}/teacher/quiz-submissions/${quizId}`;
      console.log('[Submissions] Fetching from:', url);
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      console.log('[Submissions] Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Submissions] Error response:', errorText);
        throw new Error(`Failed to load submissions: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('[Submissions] Data received:', data);
      
      submissions = data.submissions || [];
      quizTitle = data.quiz_title || 'Quiz';
      resultsReleased = data.results_released || false;
      
      console.log('[Submissions] Loaded submissions:', submissions.length);
      
    } catch (err) {
      console.error('[Submissions] Load error:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function releaseResults() {
    if (!confirm('Release results to all students? They will be able to download their reports.')) return;
    
    try {
      releasing = true;
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/release-results/${quizId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to release results');
      
      alert('✅ Results released! Students have been notified.');
      await loadSubmissions();
      
    } catch (err) {
      alert('❌ ' + err.message);
    } finally {
      releasing = false;
    }
  }

  function viewDetails(attemptId) {
    goto(`/teacher/reviews/attempt/${attemptId}`);
  }
</script>

<svelte:head>
  <title>Quiz Submissions - {quizTitle}</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">📝 {quizTitle}</h1>
          <p class="text-gray-600">Review and grade student submissions</p>
        </div>
        <div class="flex items-center space-x-4">
          {#if !resultsReleased && submissions.length > 0}
            <button 
              class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
              on:click={releaseResults}
              disabled={releasing}
            >
              {releasing ? '⏳ Releasing...' : '✅ Release Results'}
            </button>
          {/if}
          <a 
            href="/teacher/reviews" 
            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back
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

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-6">
          <div>
            <div class="text-sm text-gray-500">Total Submissions</div>
            <div class="text-2xl font-bold text-blue-600">{submissions.length}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Results Status</div>
            <div class="text-lg font-semibold {resultsReleased ? 'text-green-600' : 'text-orange-600'}">
              {resultsReleased ? '✅ Released' : '⏳ Pending'}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {#if loading}
        <div class="text-center py-12">
          <div class="text-4xl mb-4">⏳</div>
          <p class="text-gray-600">Loading submissions...</p>
        </div>
      {:else if submissions.length === 0}
        <div class="text-center py-12">
          <div class="text-6xl mb-4">📭</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No Submissions Yet</h3>
          <p class="text-gray-600">Students haven't submitted this quiz yet.</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewed</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each submissions as submission}
                <tr class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{submission.student_name}</div>
                    <div class="text-sm text-gray-500">{submission.student_username}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    {#if submission.final_score !== undefined && submission.total_possible !== undefined}
                      <div class="text-lg font-bold text-blue-600">
                        {submission.final_score.toFixed(1)}/{submission.total_possible.toFixed(1)}
                      </div>
                      <div class="text-xs text-gray-500">
                        {((submission.final_score / submission.total_possible) * 100).toFixed(1)}%
                      </div>
                    {:else}
                      <div class="text-sm text-gray-500">N/A</div>
                    {/if}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(submission.submitted_at).toLocaleString()}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-semibold rounded-full {submission.teacher_reviewed ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}">
                      {submission.teacher_reviewed ? '✅ Reviewed' : '⏳ Pending'}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button 
                      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      on:click={() => viewDetails(submission.attempt_id)}
                    >
                      🔍 Review
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>
</div>
