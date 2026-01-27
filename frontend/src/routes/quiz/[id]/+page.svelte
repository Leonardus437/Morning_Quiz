<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';
  import QuestionTypes from '$lib/components/QuestionTypes.svelte';

  let questions = [];
  let currentQuestionIndex = 0;
  let answers = {};
  let timeLeft = 0;
  let questionTimeLeft = 0;
  let timer = null;
  let questionTimer = null;
  let loading = true;
  let submitting = false;
  let error = '';
  let quiz = null;
  let questionStartTime = null;
  let questionTimes = {};
  let completedQuestions = new Set();
  let quizStartTime = null;
  let isQuizExpired = false;
  let cheatingWarnings = 0;
  let isFullscreen = false;
  let showWarningModal = false;
  let warningMessage = '';
  let quizTerminated = false;

  $: quizId = parseInt($page.params.id);
  $: currentQuestion = questions[currentQuestionIndex];
  $: progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  $: isLastQuestion = currentQuestionIndex === questions.length - 1;

  onMount(async () => {
    enableAntiCheat();
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      try {
        const userData = JSON.parse(storedUser);
        api.setToken(storedToken);
        user.login(userData);
      } catch (err) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        goto('/');
        return;
      }
    }

    if (!$user) {
      goto('/');
      return;
    }

    const quizStateKey = `quiz_${quizId}_${$user.id}`;
    const savedState = localStorage.getItem(quizStateKey);
    
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        questions = state.questions;
        answers = state.answers;
        currentQuestionIndex = state.currentQuestionIndex;
        timeLeft = state.timeLeft;
        quiz = state.quiz;
        
        if (timeLeft > 0) {
          startTimer();
          startQuestionTimer();
        } else {
          error = 'Quiz time has expired';
          loading = false;
          return;
        }
        
        loading = false;
        return;
      } catch (err) {
        localStorage.removeItem(quizStateKey);
      }
    }

    try {
      const questionsResponse = await api.getQuizQuestions(quizId);
      
      if (questionsResponse && questionsResponse.quiz_already_attempted) {
        error = questionsResponse.detail || 'You have already completed this quiz.';
        loading = false;
        return;
      }
      
      if (questionsResponse && questionsResponse.quiz_ended) {
        isQuizExpired = true;
        error = questionsResponse.detail || 'Quiz has ended. Please wait for your teacher to rebroadcast.';
        loading = false;
        return;
      }
      
      questions = shuffleArray([...questionsResponse]);
      
      const quizzes = await api.getQuizzes();
      quiz = quizzes.find(q => q.id === quizId);
      
      if (quiz) {
        if (quiz.countdown_started_at) {
          const startTime = new Date(quiz.countdown_started_at);
          const now = new Date();
          const elapsedSeconds = Math.floor((now - startTime) / 1000);
          const totalQuizTime = quiz.duration_minutes * 60;
          timeLeft = Math.max(0, totalQuizTime - elapsedSeconds);
        } else {
          timeLeft = quiz.duration_minutes * 60;
        }
        
        quizStartTime = Date.now();
        startTimer();
        startQuestionTimer();
        saveQuizState();
      }
      
      loading = false;
    } catch (err) {
      if (err.message.includes('410') || err.message.includes('expired') || err.message.includes('ended')) {
        isQuizExpired = true;
        error = '⏰ Quiz has ended. Please wait for your teacher to rebroadcast the quiz.';
      } else {
        error = err.message;
      }
      loading = false;
    }
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
    if (questionTimer) clearInterval(questionTimer);
    disableAntiCheat();
  });

  function enableAntiCheat() {
    setTimeout(() => enterFullscreen(), 100);
    document.addEventListener('contextmenu', preventRightClick);
    document.addEventListener('copy', preventCopy);
    document.addEventListener('cut', preventCopy);
    document.addEventListener('paste', preventPaste);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('keydown', preventDevTools);
  }

  function disableAntiCheat() {
    document.removeEventListener('contextmenu', preventRightClick);
    document.removeEventListener('copy', preventCopy);
    document.removeEventListener('cut', preventCopy);
    document.removeEventListener('paste', preventPaste);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('blur', handleWindowBlur);
    document.removeEventListener('fullscreenchange', handleFullscreenChange);
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
    document.removeEventListener('keydown', preventDevTools);
    exitFullscreen();
  }

  function enterFullscreen() {
    try {
      const elem = document.documentElement;
      const promise = elem.requestFullscreen ? elem.requestFullscreen() : 
                     elem.webkitRequestFullscreen ? elem.webkitRequestFullscreen() :
                     elem.mozRequestFullScreen ? elem.mozRequestFullScreen() : null;
      
      if (promise) {
        promise.then(() => { 
          isFullscreen = true; 
        }).catch((err) => { 
          console.log('Fullscreen not available:', err);
          isFullscreen = false; 
        });
      }
    } catch (e) {
      console.log('Fullscreen error:', e);
      isFullscreen = false;
    }
  }

  function exitFullscreen() {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(() => {});
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen().catch(() => {});
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen().catch(() => {});
    }
  }

  function preventRightClick(e) {
    e.preventDefault();
    return false;
  }

  function preventCopy(e) {
    e.preventDefault();
    return false;
  }

  function preventPaste(e) {
    e.preventDefault();
    return false;
  }

  function preventDevTools(e) {
    if (quizTerminated) return;
    
    const restrictedKeys = [
      27,  // ESC
      112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, // F1-F12
      44,  // Print Screen
      46,  // Delete
      36,  // Home
      35,  // End
      33,  // Page Up
      34,  // Page Down
      91,  // Windows Key Left
      92,  // Windows Key Right
      93   // Context Menu Key
    ];
    
    if (restrictedKeys.includes(e.keyCode)) {
      e.preventDefault();
      e.stopPropagation();
      recordCheatingAttempt(`You pressed a restricted key (${e.key || 'Key ' + e.keyCode})`);
      return false;
    }
    
    if (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74)) {
      e.preventDefault();
      e.stopPropagation();
      recordCheatingAttempt('You tried to open developer tools');
      return false;
    }
    
    if (e.ctrlKey && e.keyCode === 85) {
      e.preventDefault();
      e.stopPropagation();
      recordCheatingAttempt('You tried to view page source');
      return false;
    }
  }

  function handleVisibilityChange() {
    if (document.hidden && !quizTerminated && !submitting && !loading && !showWarningModal) {
      recordCheatingAttempt('You switched to another tab or window');
    }
  }

  function handleWindowBlur() {
    if (!quizTerminated && !submitting && !loading && !showWarningModal) {
      recordCheatingAttempt('You switched to another application');
    }
  }

  function handleFullscreenChange() {
    const isCurrentlyFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement);
    isFullscreen = isCurrentlyFullscreen;
  }

  async function recordCheatingAttempt(reason) {
    cheatingWarnings++;
    
    if (cheatingWarnings === 1) {
      warningMessage = `⚠️ WARNING #1: ${reason}. This is your first warning. Two more violations will result in automatic quiz termination.`;
      showWarningModal = true;
    } else if (cheatingWarnings === 2) {
      warningMessage = `⚠️ FINAL WARNING #2: ${reason}. One more violation and your quiz will be automatically submitted and your teacher will be notified.`;
      showWarningModal = true;
    } else if (cheatingWarnings >= 3) {
      warningMessage = `❌ QUIZ TERMINATED: ${reason}. Your quiz has been automatically submitted due to multiple cheating attempts. You will be redirected shortly.`;
      showWarningModal = true;
      quizTerminated = true;
      
      await submitQuiz();
      
      try {
        await api.reportCheating({
          quiz_id: quizId,
          warnings: cheatingWarnings,
          reason: reason,
          auto_submitted: true
        });
      } catch (err) {
        console.error('Failed to report cheating:', err);
      }
      
      setTimeout(() => {
        goto(`/results/${quizId}?status=terminated&quiz_title=${encodeURIComponent(quiz?.title || 'Quiz')}`);
      }, 3000);
    }
  }

  function closeWarningModal() {
    if (quizTerminated) return;
    showWarningModal = false;
    enterFullscreen();
  }

  function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
      timeLeft--;
      if (timeLeft <= 0) {
        clearInterval(timer);
        submitQuiz();
      }
      saveQuizState();
    }, 1000);
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function handleAnswer(questionId, answer) {
    answers = { ...answers, [questionId]: answer };
    saveQuizState();
  }

  function nextQuestion() {
    recordQuestionTime();
    
    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex++;
      startQuestionTimer();
      saveQuizState();
    }
  }

  function startQuestionTimer() {
    if (questionTimer) clearInterval(questionTimer);
    questionTimeLeft = quiz?.question_time_seconds || 60;
    questionStartTime = Date.now();
    
    questionTimer = setInterval(() => {
      questionTimeLeft--;
      if (questionTimeLeft <= 0) {
        clearInterval(questionTimer);
        autoNextQuestion();
      }
    }, 1000);
  }

  function autoNextQuestion() {
    completedQuestions.add(currentQuestionIndex);
    recordQuestionTime();
    completedQuestions = completedQuestions;
    
    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex++;
      startQuestionTimer();
      saveQuizState();
    } else {
      submitQuiz();
    }
  }

  function recordQuestionTime() {
    if (questionStartTime && currentQuestion) {
      questionTimes[currentQuestion.id] = Math.floor((Date.now() - questionStartTime) / 1000);
    }
  }

  function saveQuizState() {
    if (!$user || !quiz) return;
    
    const quizStateKey = `quiz_${quizId}_${$user.id}`;
    const state = {
      questions,
      answers,
      currentQuestionIndex,
      timeLeft,
      quiz,
      questionTimes
    };
    
    localStorage.setItem(quizStateKey, JSON.stringify(state));
  }

  function clearQuizState() {
    if (!$user) return;
    const quizStateKey = `quiz_${quizId}_${$user.id}`;
    localStorage.removeItem(quizStateKey);
  }

  function prevQuestion() {
    if (completedQuestions.has(currentQuestionIndex - 1)) {
      return;
    }
    
    recordQuestionTime();
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
      startQuestionTimer();
      saveQuizState();
    }
  }

  async function submitQuiz() {
    if (submitting) return;
    
    submitting = true;
    recordQuestionTime();
    clearInterval(timer);
    if (questionTimer) clearInterval(questionTimer);

    try {
      const answeredCount = Object.keys(answers).length;
      const totalQuestions = questions.length;
      
      const submission = {
        quiz_id: quizId,
        answers: Object.entries(answers)
          .filter(([_, answer]) => answer !== undefined && answer !== null && answer !== '')
          .map(([question_id, answer]) => ({
            question_id: parseInt(question_id),
            answer: typeof answer === 'string' ? answer.trim() : answer
          }))
      };

      console.log(`📊 Submitting ${answeredCount}/${totalQuestions} answers`);
      const result = await api.submitQuiz(submission);
      console.log('✅ Quiz submitted successfully:', result);
      
      clearQuizState();
      disableAntiCheat();
      
      if (quizTerminated) {
        showWarningModal = false;
        setTimeout(() => {
          goto(`/results/${quizId}?status=terminated&quiz_title=${encodeURIComponent(quiz?.title || 'Quiz')}`);
        }, 500);
      } else {
        goto(`/results/${quizId}?status=completed&quiz_title=${encodeURIComponent(quiz?.title || 'Quiz')}`);
      }
    } catch (err) {
      console.error('❌ Submit failed:', err);
      
      if (err.message && err.message.includes('already')) {
        clearQuizState();
        goto('/');
        return;
      }
      
      error = err.message || 'Failed to submit quiz. Please try again.';
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Quiz - {quiz?.title || 'Loading...'}</title>
</svelte:head>

{#if showWarningModal}
  <div class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" style="z-index: 9999;">
    <div class="bg-white rounded-lg p-8 max-w-md mx-4 shadow-2xl border-4 {cheatingWarnings >= 3 ? 'border-red-600' : 'border-yellow-500'}">
      <div class="text-center">
        <div class="text-6xl mb-4">{cheatingWarnings >= 3 ? '❌' : '⚠️'}</div>
        <h2 class="text-2xl font-bold mb-4 {cheatingWarnings >= 3 ? 'text-red-600' : 'text-yellow-600'}">
          {cheatingWarnings >= 3 ? 'Quiz Terminated' : `Warning #${cheatingWarnings}`}
        </h2>
        <p class="text-gray-700 mb-6 leading-relaxed">{warningMessage}</p>
        {#if !quizTerminated}
          <button 
            class="btn bg-blue-600 text-white hover:bg-blue-700 w-full"
            on:click={closeWarningModal}
          >
            I Understand - Continue Quiz
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<div class="min-h-screen bg-white">
  <div class="max-w-4xl mx-auto px-6 py-8">
    {#if loading}
      <div class="text-center py-20">
        <div class="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">Loading quiz...</p>
      </div>
    {:else if error}
      <div class="card text-center">
        {#if isQuizExpired}
          <div class="w-16 h-16 bg-yellow-50 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">⏰</div>
          <h2 class="text-xl font-semibold mb-2 text-gray-900">Quiz Time Expired</h2>
          <p class="text-gray-700 mb-2">{error}</p>
          <p class="text-sm text-gray-500 mb-6">Your teacher can rebroadcast this quiz to give you another chance.</p>
        {:else}
          <div class="w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">❌</div>
          <h2 class="text-xl font-semibold mb-2 text-gray-900">Error</h2>
          <p class="text-red-600 mb-6">{error}</p>
        {/if}
        <button class="btn btn-primary" on:click={() => goto('/')}>
          Back to Home
        </button>
      </div>
    {:else if questions.length === 0}
      <div class="card text-center">
        <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">📝</div>
        <h2 class="text-xl font-semibold mb-2 text-gray-900">No Questions</h2>
        <p class="text-gray-600 mb-6">This quiz has no questions</p>
        <button class="btn btn-primary" on:click={() => goto('/')}>
          Back to Home
        </button>
      </div>
    {:else}
      <div class="bg-white shadow-lg p-6 mb-6 border-l-4 border-blue-600">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-black text-gray-900 uppercase tracking-wide">{quiz?.title}</h1>
          <div class="text-right">
            <div class="text-2xl font-black {timeLeft < 300 ? 'text-red-600' : 'text-blue-600'}">
              {formatTime(timeLeft)}
            </div>
            <div class="text-xs font-bold text-gray-600 uppercase tracking-wide">
              Question {currentQuestionIndex + 1} of {questions.length}
            </div>
          </div>
        </div>
        
        <div class="w-full bg-gray-200 h-2 overflow-hidden">
          <div 
            class="h-full bg-blue-600 transition-all duration-300"
            style="width: {progress}%"
          ></div>
        </div>
      </div>

      {#if currentQuestion}
        <div class="bg-white shadow-lg p-8 mb-6">
          <div class="flex items-center justify-between mb-6">
            <span class="bg-blue-600 text-white px-4 py-2 font-bold text-sm uppercase tracking-wide">Question {currentQuestionIndex + 1}</span>
            <span class="text-xl font-black {questionTimeLeft < 10 ? 'text-red-600' : 'text-blue-600'}">
              {formatTime(questionTimeLeft)}
            </span>
          </div>

          <h2 class="text-xl font-bold text-gray-900 mb-8 leading-relaxed">
            {currentQuestion.question_text}
          </h2>

          <QuestionTypes 
            question={currentQuestion}
            bind:answer={answers[currentQuestion.id]}
            disabled={completedQuestions.has(currentQuestionIndex)}
          />
        </div>
      {/if}

      <div class="flex items-center justify-between">
        <button
          class="btn btn-secondary"
          on:click={prevQuestion}
          disabled={currentQuestionIndex === 0 || completedQuestions.has(currentQuestionIndex - 1)}
        >
          ← Previous
        </button>

        <div class="flex gap-2">
          {#each questions as _, index}
            <button
              class="w-8 h-8 rounded-lg text-xs font-medium transition-colors
                {index === currentQuestionIndex 
                  ? 'bg-blue-600 text-white' 
                  : completedQuestions.has(index)
                    ? 'bg-red-100 text-red-600'
                    : answers[questions[index].id] 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-gray-100 text-gray-600'}"
              on:click={() => {
                if (!completedQuestions.has(index)) {
                  recordQuestionTime();
                  currentQuestionIndex = index;
                  startQuestionTimer();
                  saveQuizState();
                }
              }}
              disabled={completedQuestions.has(index)}
            >
              {index + 1}
            </button>
          {/each}
        </div>

        {#if isLastQuestion}
          <button
            class="btn bg-green-600 text-white hover:bg-green-700 active:scale-95"
            on:click={submitQuiz}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit'}
          </button>
        {:else}
          <button
            class="btn btn-primary"
            on:click={nextQuestion}
          >
            Next →
          </button>
        {/if}
      </div>
    {/if}
  </div>
</div>
