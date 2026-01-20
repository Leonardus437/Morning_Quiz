<script>
  import { onMount } from 'svelte';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';
  import { goto } from '$app/navigation';

  let loading = true;
  let progress = null;
  let error = '';

  onMount(async () => {
    if (!$user || $user.role !== 'student') {
      goto('/');
      return;
    }

    try {
      console.log(' Fetching student progress...');
      progress = await api.getStudentProgress();
      console.log(' Progress data:', progress);
      loading = false;
    } catch (err) {
      console.error(' Performance page error:', err);
      error = err.message || 'Failed to load performance data';
      loading = false;
    }
  });

  function getGradeColor(grade) {
    if (grade === 'A+' || grade === 'A') return 'text-green-600 bg-green-50';
    if (grade === 'B' || grade === 'C') return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  }

  async function downloadReport(quizId) {
    try {
      const token = api.token || localStorage.getItem('token');
      if (!token) {
        alert('Please login again');
        return;
      }
      
      const baseURL = api.baseURL || 'http://localhost:8000';
      const url = `${baseURL}/student-report/${quizId}`;
      
      console.log(' Downloading report:', url);
      console.log(' Token:', token ? 'Present' : 'Missing');
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(' Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(' Error response:', errorText);
        throw new Error('Failed to generate report');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `quiz_${quizId}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
      
      console.log(' Download complete');
    } catch (err) {
      console.error(' Download error:', err);
      alert('Failed to download report: ' + err.message);
    }
  }
</script>

<svelte:head>
  <title>My Performance</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <div class="max-w-6xl mx-auto px-6 py-8">
    <div class="mb-8">
<<<<<<< HEAD
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2"> My Performance</h1>
          <p class="text-gray-600">Track your quiz results and download detailed reports</p>
        </div>
        <button 
          on:click={() => goto('/')} 
          class="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span>←</span>
          <span>Back to Home</span>
        </button>
      </div>
=======
      <h1 class="text-3xl font-bold text-gray-900 mb-2"> My Performance</h1>
      <p class="text-gray-600">Track your quiz results and download detailed reports</p>
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
    </div>

    {#if loading}
      <div class="text-center py-20">
        <div class="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">Loading your performance data...</p>
      </div>
    {:else if error}
      <div class="card text-center">
        <p class="text-red-600">{error}</p>
      </div>
    {:else if progress}
      <!-- Overall Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card">
          <div class="text-sm text-gray-600 mb-1">Overall Score</div>
          <div class="text-3xl font-bold text-blue-600">{progress.overall_percentage}%</div>
        </div>
        <div class="card">
          <div class="text-sm text-gray-600 mb-1">Quizzes Completed</div>
          <div class="text-3xl font-bold text-green-600">{progress.total_quizzes}</div>
        </div>
        <div class="card">
          <div class="text-sm text-gray-600 mb-1">Average Grade</div>
          <div class="text-3xl font-bold {progress.overall_percentage >= 70 ? 'text-green-600' : 'text-yellow-600'}">
            {progress.overall_percentage >= 90 ? 'A+' : progress.overall_percentage >= 80 ? 'A' : progress.overall_percentage >= 70 ? 'B' : progress.overall_percentage >= 60 ? 'C' : 'D'}
          </div>
        </div>
      </div>

      <!-- Improvement Tips -->
      {#if progress.improvement_tips && progress.improvement_tips.length > 0}
        <div class="card mb-8 bg-blue-50 border-l-4 border-blue-600">
          <h3 class="font-bold text-gray-900 mb-3"> Tips for Improvement</h3>
          <ul class="space-y-2">
            {#each progress.improvement_tips as tip}
              <li class="text-gray-700 flex items-start">
                <span class="mr-2"></span>
                <span>{tip}</span>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Quiz History -->
      <div class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-6">Quiz History</h2>
        
        {#if progress.recent_quizzes && progress.recent_quizzes.length > 0}
          <div class="space-y-4">
            {#each progress.recent_quizzes as quiz}
              <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex-1">
                    <h3 class="font-bold text-gray-900">{quiz.quiz_title}</h3>
                    <div class="text-sm text-gray-600 mt-1">
                      {quiz.department} - {quiz.level}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-bold {getGradeColor(quiz.grade)} px-3 py-1 rounded-lg inline-block">
                      {quiz.grade}
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-3 gap-4 mb-3">
                  <div>
                    <div class="text-xs text-gray-600">Score</div>
                    <div class="font-bold text-gray-900">{quiz.score}/{quiz.total_questions}</div>
                  </div>
                  <div>
                    <div class="text-xs text-gray-600">Percentage</div>
                    <div class="font-bold text-gray-900">{quiz.percentage}%</div>
                  </div>
                  <div>
                    <div class="text-xs text-gray-600">Completed</div>
                    <div class="font-bold text-gray-900">{new Date(quiz.completed_at).toLocaleDateString()}</div>
                  </div>
                </div>

                <button
                  class="btn btn-sm btn-primary w-full"
                  on:click={() => downloadReport(quiz.quiz_id)}
                >
                   Download Detailed Report
                </button>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-12 text-gray-500">
            <div class="text-4xl mb-3"></div>
            <p>No quizzes completed yet</p>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>
