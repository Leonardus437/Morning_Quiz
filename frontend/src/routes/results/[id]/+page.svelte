<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let status = '';
  let quizTitle = '';
  let loading = true;
  
  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    status = params.get('status') || 'completed';
    quizTitle = params.get('quiz_title') || 'Quiz';
    loading = false;
  });
  
  function goHome() {
    goto('/');
  }
</script>

<svelte:head>
  <title>Quiz Results</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
  {#if loading}
    <div class="text-center">
      <div class="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
    </div>
  {:else if status === 'terminated'}
    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
      <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span class="text-5xl">❌</span>
      </div>
      
      <h1 class="text-3xl font-bold text-red-600 mb-4">Quiz Terminated</h1>
      
      <div class="bg-red-50 border-2 border-red-200 rounded-xl p-6 mb-6">
        <p class="text-gray-800 font-semibold mb-3">
          ⚠️ Your quiz "{quizTitle}" has been automatically submitted due to multiple cheating violations.
        </p>
        <div class="bg-white border-l-4 border-red-500 p-4 mb-3">
          <p class="text-red-700 font-bold mb-2">What happened:</p>
          <ul class="list-disc list-inside text-gray-700 text-sm space-y-1">
            <li>You received 3 warnings for attempting to cheat</li>
            <li>Your quiz was automatically submitted</li>
            <li>Your teacher has been notified</li>
          </ul>
        </div>
        <p class="text-gray-700 text-sm mb-2">
          📊 Your answers have been submitted for grading. Results will be available after teacher review.
        </p>
        <p class="text-gray-600 text-sm">
          ⚠️ Please maintain academic integrity in future assessments.
        </p>
      </div>
      
      <div class="space-y-3">
        <button 
          class="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          on:click={goHome}
        >
          Return to Home
        </button>
      </div>
    </div>
  {:else}
    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span class="text-5xl">✅</span>
      </div>
      
      <h1 class="text-3xl font-bold text-green-600 mb-4">Quiz Submitted!</h1>
      
      <div class="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
        <p class="text-gray-800 font-semibold mb-3">
          Your quiz "{quizTitle}" has been successfully submitted.
        </p>
        <p class="text-gray-700 text-sm mb-2">
          📊 Your answers are being reviewed.
        </p>
        <p class="text-gray-600 text-sm">
          Results will be available once your teacher releases them.
        </p>
      </div>
      
      <div class="space-y-3">
        <button 
          class="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          on:click={goHome}
        >
          Return to Home
        </button>
      </div>
    </div>
  {/if}
</div>
