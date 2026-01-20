<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores.js';

  let score = 0;
  let totalQuestions = 0;
  let percentage = 0;
  let showModal = false;
<<<<<<< HEAD
  let isUnderReview = false;
  let quizTitle = '';

  $: quizId = parseInt($page.params.id);
  $: statusFromUrl = $page.url.searchParams.get('status');
  $: scoreFromUrl = parseInt($page.url.searchParams.get('score')) || 0;
  $: totalFromUrl = parseInt($page.url.searchParams.get('total')) || 1;
  $: quizTitleFromUrl = $page.url.searchParams.get('quiz_title') || 'Quiz';
=======

  $: quizId = parseInt($page.params.id);
  $: scoreFromUrl = parseInt($page.url.searchParams.get('score')) || 0;
  $: totalFromUrl = parseInt($page.url.searchParams.get('total')) || 1;
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9

  onMount(() => {
    if (!$user) {
      goto('/');
      return;
    }

<<<<<<< HEAD
    if (statusFromUrl === 'under_review') {
      isUnderReview = true;
      quizTitle = decodeURIComponent(quizTitleFromUrl);
    } else {
      score = scoreFromUrl;
      totalQuestions = totalFromUrl;
      percentage = totalQuestions > 0 ? Math.round((score / totalQuestions) * 100) : 0;
      if (percentage > 100) percentage = 100;
    }
=======
    score = scoreFromUrl;
    totalQuestions = totalFromUrl;
    percentage = totalQuestions > 0 ? Math.round((score / totalQuestions) * 100) : 0;
    if (percentage > 100) percentage = 100;
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
    
    showModal = true;
  });

  function getGrade(percentage) {
    if (percentage >= 90) return { grade: 'A+', color: 'text-green-600' };
    if (percentage >= 80) return { grade: 'A', color: 'text-green-600' };
    if (percentage >= 70) return { grade: 'B', color: 'text-blue-600' };
    if (percentage >= 60) return { grade: 'C', color: 'text-yellow-600' };
    if (percentage >= 50) return { grade: 'D', color: 'text-orange-600' };
    return { grade: 'F', color: 'text-red-600' };
  }

  function closeModal() {
    showModal = false;
    goto('/');
  }

  $: gradeInfo = getGrade(percentage);
</script>

<svelte:head>
  <title>Quiz Results</title>
</svelte:head>

{#if showModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeModal}>
    <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4 text-center" on:click|stopPropagation>
<<<<<<< HEAD
      {#if isUnderReview}
        <div class="text-6xl mb-4">⏳</div>
        
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Quiz Submitted Successfully!</h2>
        
        <div class="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl p-6 mb-6 border-2 border-orange-300">
          <div class="text-orange-800 mb-4">
            <div class="text-lg font-semibold mb-2">📋 Under Review</div>
            <p class="text-sm">Your answers are being reviewed by your teacher.</p>
          </div>
          
          <div class="bg-white rounded-lg p-4 mb-4">
            <div class="text-sm text-gray-600 mb-1">Quiz</div>
            <div class="font-bold text-gray-900">{quizTitle}</div>
          </div>
          
          <div class="text-sm text-orange-700">
            <p class="mb-2">✓ Your submission has been recorded</p>
            <p class="mb-2">✓ Teacher will review your answers</p>
            <p>✓ Results will be available soon</p>
          </div>
        </div>

        <div class="text-gray-600 mb-6 text-sm">
          You will be able to see your results once your teacher completes the review and releases the grades.
        </div>

        <button class="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors" on:click={closeModal}>
          Back to Dashboard
        </button>
      {:else}
        <div class="text-6xl mb-4">🎉</div>
        
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Quiz Completed!</h2>
        
        <div class="bg-gray-50 rounded-xl p-6 mb-6">
          <div class="text-5xl font-black text-blue-600 mb-4">{percentage}%</div>
          
          <div class="flex items-center justify-center gap-4 mb-4">
            <div>
              <div class="text-xl font-bold text-blue-600">{score}</div>
              <div class="text-sm text-gray-500">Correct</div>
            </div>
            <div class="text-gray-300">/</div>
            <div>
              <div class="text-xl font-bold text-gray-600">{totalQuestions}</div>
              <div class="text-sm text-gray-500">Total</div>
            </div>
          </div>

          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 {gradeInfo.color} font-semibold">
            Grade: {gradeInfo.grade}
          </div>
        </div>

        <div class="text-gray-600 mb-6">
          {#if percentage >= 90}
            Outstanding performance! 🌟
          {:else if percentage >= 80}
            Excellent work! 👏
          {:else if percentage >= 70}
            Good job! 👍
          {:else if percentage >= 60}
            Not bad! Keep practicing 📚
          {:else}
            Keep studying! You'll do better next time 💪
          {/if}
        </div>

        <button class="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors" on:click={closeModal}>
          Back to Dashboard
        </button>
      {/if}
=======
      <div class="text-6xl mb-4">🎉</div>
      
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Quiz Completed!</h2>
      
      <div class="bg-gray-50 rounded-xl p-6 mb-6">
        <div class="text-5xl font-black text-blue-600 mb-4">{percentage}%</div>
        
        <div class="flex items-center justify-center gap-4 mb-4">
          <div>
            <div class="text-xl font-bold text-blue-600">{score}</div>
            <div class="text-sm text-gray-500">Correct</div>
          </div>
          <div class="text-gray-300">/</div>
          <div>
            <div class="text-xl font-bold text-gray-600">{totalQuestions}</div>
            <div class="text-sm text-gray-500">Total</div>
          </div>
        </div>

        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 {gradeInfo.color} font-semibold">
          Grade: {gradeInfo.grade}
        </div>
      </div>

      <div class="text-gray-600 mb-6">
        {#if percentage >= 90}
          Outstanding performance! 🌟
        {:else if percentage >= 80}
          Excellent work! 👏
        {:else if percentage >= 70}
          Good job! 👍
        {:else if percentage >= 60}
          Not bad! Keep practicing 📚
        {:else}
          Keep studying! You'll do better next time 💪
        {/if}
      </div>

      <button class="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors" on:click={closeModal}>
        Back to Dashboard
      </button>
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
    </div>
  </div>
{/if}