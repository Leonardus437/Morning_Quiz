<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api } from '$lib/api.js';

  let attemptId = '';
  let reviewData = null;
  let loading = false;
  let error = '';
  let saving = false;
  let releasing = false;
  let adjustedGrades = {};
  let hasChanges = false;

  $: attemptId = $page.params.attemptId;

  onMount(async () => {
    await loadReviewData();
  });

  async function loadReviewData() {
    try {
      loading = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/review/${attemptId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load review data');
      }
      
      reviewData = await response.json();
      
      adjustedGrades = {};
      reviewData.answers.forEach(answer => {
        adjustedGrades[answer.answer_id] = {
          score: answer.teacher_score !== null ? answer.teacher_score : answer.ai_score,
          feedback: answer.teacher_feedback || ''
        };
      });
    } catch (err) {
      error = err.message;
      console.error('Load review data error:', err);
    } finally {
      loading = false;
    }
  }

  function updateGrade(answerId, field, value) {
    adjustedGrades[answerId] = {
      ...adjustedGrades[answerId],
      [field]: value
    };
    hasChanges = true;
  }

  async function saveGrades() {
    try {
      saving = true;
      error = '';
      
      const grades = Object.entries(adjustedGrades).map(([answerId, data]) => ({
        answer_id: parseInt(answerId),
        score: parseFloat(data.score),
        feedback: data.feedback
      }));
      
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/review/${attemptId}/grade`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ grades })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save grades');
      }
      
      alert('✅ Grades saved successfully!');
      hasChanges = false;
      await loadReviewData();
    } catch (err) {
      error = err.message;
      alert('❌ Failed to save grades: ' + err.message);
    } finally {
      saving = false;
    }
  }

  async function releaseResults() {
    if (!confirm('Are you sure you want to release results for this quiz? Students will be able to see their scores.')) {
      return;
    }
    
    try {
      releasing = true;
      error = '';
      
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/quiz/${reviewData.quiz_id}/release-results`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to release results');
      }
      
      const result = await response.json();
      alert(`✅ ${result.message}`);
      goto('/teacher/reviews');
    } catch (err) {
      error = err.message;
      alert('❌ Failed to release results: ' + err.message);
    } finally {
      releasing = false;
    }
  }

  function calculateTotalScore() {
    return Object.values(adjustedGrades).reduce((sum, grade) => sum + parseFloat(grade.score || 0), 0).toFixed(1);
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
  }
</script>

<svelte:head>
  <title>Review Submission - Teacher Dashboard</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">🔍 Review Submission</h1>
          <p class="text-gray-600">Review AI grades and adjust if needed</p>
        </div>
        <div class="flex items-center space-x-4">
          <a 
            href="/teacher/reviews" 
            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back to Reviews
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

    {#if loading}
      <div class="text-center py-12">
        <div class="text-4xl mb-4">⏳</div>
        <p class="text-gray-600">Loading review data...</p>
      </div>
    {:else if reviewData}
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
            <div class="text-sm text-blue-700 mb-1">Quiz</div>
            <div class="text-lg font-bold text-blue-900">{reviewData.quiz_title}</div>
          </div>
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
            <div class="text-sm text-green-700 mb-1">Student</div>
            <div class="text-lg font-bold text-green-900">{reviewData.student_name}</div>
          </div>
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
            <div class="text-sm text-purple-700 mb-1">AI Score</div>
            <div class="text-lg font-bold text-purple-900">{reviewData.total_score}</div>
          </div>
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
            <div class="text-sm text-orange-700 mb-1">Adjusted Score</div>
            <div class="text-lg font-bold text-orange-900">{calculateTotalScore()}</div>
          </div>
        </div>
      </div>

      <div class="space-y-6 mb-6">
        {#each reviewData.answers as answer, index}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold mr-3">Q{index + 1}</span>
                  <h3 class="text-lg font-semibold text-gray-900">{answer.question_text}</h3>
                </div>
              </div>
              <span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                Max: {answer.max_points} pts
              </span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm font-semibold text-green-800 mb-2">✅ Correct Answer</div>
                <div class="text-gray-900">{answer.correct_answer}</div>
              </div>
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm font-semibold text-blue-800 mb-2">📝 Student Answer</div>
                <div class="text-gray-900">{answer.student_answer || 'No answer provided'}</div>
              </div>
            </div>

            <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200 mb-4">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="text-sm font-semibold text-purple-800 mb-1">🤖 AI Grading</div>
                  <div class="text-gray-700">{answer.ai_feedback}</div>
                </div>
                <div class="ml-4">
                  <div class="text-2xl font-bold text-purple-600">{answer.ai_score}/{answer.max_points}</div>
                </div>
              </div>
            </div>

            <div class="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4 border-2 border-orange-300">
              <div class="text-sm font-semibold text-orange-800 mb-3">👨‍🏫 Teacher Adjustment</div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Adjusted Score</label>
                  <input 
                    type="number" 
                    step="0.1"
                    min="0"
                    max={answer.max_points}
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    value={adjustedGrades[answer.answer_id]?.score || 0}
                    on:input={(e) => updateGrade(answer.answer_id, 'score', e.target.value)}
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Teacher Feedback (Optional)</label>
                  <input 
                    type="text" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    placeholder="Add your feedback..."
                    value={adjustedGrades[answer.answer_id]?.feedback || ''}
                    on:input={(e) => updateGrade(answer.answer_id, 'feedback', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <div class="bg-white rounded-xl shadow-lg border-2 border-green-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Review Complete?</h3>
            <p class="text-gray-600">Save your adjustments and release results to students</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-right mr-4">
              <div class="text-sm text-gray-600">Final Score</div>
              <div class="text-3xl font-bold text-green-600">{calculateTotalScore()}</div>
            </div>
            <button 
              class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all disabled:opacity-50"
              on:click={saveGrades}
              disabled={saving || !hasChanges}
            >
              {saving ? '💾 Saving...' : '💾 Save Grades'}
            </button>
            <button 
              class="bg-gradient-to-r from-green-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105 disabled:opacity-50"
              on:click={releaseResults}
              disabled={releasing || hasChanges}
            >
              {releasing ? '🚀 Releasing...' : '🚀 Release Results'}
            </button>
          </div>
        </div>
        {#if hasChanges}
          <div class="mt-4 bg-yellow-50 border border-yellow-300 rounded-lg p-3">
            <p class="text-sm text-yellow-800">⚠️ You have unsaved changes. Please save before releasing results.</p>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
</style>
