<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { api } from '$lib/api.js';

  let attemptId = null;
  let submission = null;
  let loading = false;
  let error = '';
  let saving = false;
  let editingAnswerId = null;
  let editScore = 0;
  let editFeedback = '';

  onMount(async () => {
    attemptId = $page.params.attemptId;
    await loadSubmission();
  });

  async function loadSubmission() {
    try {
      loading = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/review-submission/${attemptId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load submission');
      }
      
      submission = await response.json();
    } catch (err) {
      error = err.message;
      console.error('Load submission error:', err);
    } finally {
      loading = false;
    }
  }

  function startEdit(answer) {
    editingAnswerId = answer.answer_id;
    editScore = answer.teacher_score !== null ? answer.teacher_score : answer.points_earned;
    editFeedback = answer.teacher_feedback || answer.ai_feedback || '';
  }

  function cancelEdit() {
    editingAnswerId = null;
    editScore = 0;
    editFeedback = '';
  }

  async function saveGrade(answerId, maxPoints) {
    if (editScore < 0 || editScore > maxPoints) {
      alert(`Score must be between 0 and ${maxPoints}`);
      return;
    }

    try {
      saving = true;
      error = '';
      const token = localStorage.getItem('token');
      const apiBase = api.baseURL;
      
      const response = await fetch(`${apiBase}/teacher/grade-answer/${answerId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          score: parseFloat(editScore),
          feedback: editFeedback.trim()
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save grade');
      }
      
      const result = await response.json();
      alert(`✅ Grade saved! New final score: ${result.final_score}`);
      await loadSubmission();
      cancelEdit();
    } catch (err) {
      error = err.message;
      alert('❌ Failed to save grade: ' + err.message);
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head>
  <title>Review Submission - {submission?.student_name || 'Loading...'}</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            📝 {submission?.quiz_title || 'Loading...'}
          </h1>
          <p class="text-gray-600">Student: {submission?.student_name || 'Loading...'}</p>
        </div>
        <a 
          href="/teacher/reviews" 
          class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Back to Reviews
        </a>
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
      <div class="bg-white rounded-xl shadow-sm p-12 text-center">
        <div class="text-4xl mb-4">⏳</div>
        <p class="text-gray-600">Loading submission...</p>
      </div>
    {:else if submission}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div class="text-sm text-gray-600 mb-1">Initial Score</div>
          <div class="text-2xl font-bold text-blue-600">{submission.initial_score}/{submission.total_questions}</div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div class="text-sm text-gray-600 mb-1">Final Score</div>
          <div class="text-2xl font-bold text-green-600">
            {submission.final_score !== null ? submission.final_score : submission.initial_score}/{submission.total_questions}
          </div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div class="text-sm text-gray-600 mb-1">Submitted</div>
          <div class="text-sm font-medium text-gray-700">{new Date(submission.completed_at).toLocaleString()}</div>
        </div>
      </div>

      <div class="space-y-6">
        {#each submission.answers as answer, index}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Question {index + 1}</h3>
              <span class="px-3 py-1 rounded-full text-xs font-medium {answer.question_type === 'multiple_choice' ? 'bg-blue-100 text-blue-800' : answer.question_type === 'true_false' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}">
                {answer.question_type.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            <div class="mb-4">
              <div class="text-sm font-semibold text-gray-700 mb-2">Question:</div>
              <div class="text-gray-900">{answer.question_text}</div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <div class="text-sm font-semibold text-gray-700 mb-2">Student's Answer:</div>
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div class="text-gray-900">{answer.student_answer || 'No answer provided'}</div>
                </div>
              </div>
              <div>
                <div class="text-sm font-semibold text-gray-700 mb-2">Correct Answer:</div>
                <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div class="text-gray-900">{answer.correct_answer}</div>
                </div>
              </div>
            </div>

            {#if editingAnswerId === answer.answer_id}
              <div class="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
                <h4 class="font-semibold text-gray-900 mb-3">✏️ Edit Grade</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                      Score (0 - {answer.max_points})
                    </label>
                    <input 
                      type="number" 
                      min="0" 
                      max={answer.max_points}
                      step="0.5"
                      bind:value={editScore}
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                      Current: {answer.teacher_score !== null ? answer.teacher_score : answer.points_earned}/{answer.max_points}
                    </label>
                    <div class="text-sm text-gray-600">
                      AI Score: {answer.points_earned}/{answer.max_points}
                    </div>
                  </div>
                </div>
                <div class="mb-4">
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Feedback</label>
                  <textarea 
                    bind:value={editFeedback}
                    rows="3"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Add your feedback for the student..."
                  ></textarea>
                </div>
                <div class="flex space-x-3">
                  <button 
                    class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                    on:click={() => saveGrade(answer.answer_id, answer.max_points)}
                    disabled={saving}
                  >
                    {saving ? '💾 Saving...' : '💾 Save Grade'}
                  </button>
                  <button 
                    class="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                    on:click={cancelEdit}
                    disabled={saving}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            {:else}
              <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start mb-3">
                  <div class="flex-1">
                    <div class="text-sm font-semibold text-gray-700 mb-1">Grading:</div>
                    <div class="flex items-center space-x-4">
                      <div>
                        <span class="text-lg font-bold {answer.teacher_score !== null ? 'text-green-600' : 'text-blue-600'}">
                          {answer.teacher_score !== null ? answer.teacher_score : answer.points_earned}
                        </span>
                        <span class="text-gray-600">/{answer.max_points} points</span>
                      </div>
                      {#if answer.teacher_score !== null}
                        <span class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          ✅ Teacher Reviewed
                        </span>
                      {:else}
                        <span class="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          🤖 AI Graded
                        </span>
                      {/if}
                    </div>
                  </div>
                  <button 
                    class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    on:click={() => startEdit(answer)}
                  >
                    ✏️ Edit Grade
                  </button>
                </div>
                <div class="text-sm text-gray-700">
                  <span class="font-semibold">Feedback:</span> 
                  {answer.teacher_feedback || answer.ai_feedback || 'No feedback'}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
</style>
