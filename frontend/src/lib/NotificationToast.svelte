<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  
  export let notifications = [];
  
  function removeNotification(id) {
    notifications = notifications.filter(n => n.id !== id);
  }
  
  function getIcon(type) {
    const icons = {
      'lesson_assignment': '📚',
      'quiz_available': '📝',
      'quiz_submission': '✅',
      'results_released': '🎉',
      'module_assigned': '📖',
      'cheating_alert': '⚠️',
      'assignment': '📚',
      'default': '🔔'
    };
    return icons[type] || icons.default;
  }
  
  function getColor(type) {
    const colors = {
      'lesson_assignment': 'from-blue-500 to-blue-600',
      'quiz_available': 'from-green-500 to-green-600',
      'quiz_submission': 'from-purple-500 to-purple-600',
      'results_released': 'from-yellow-500 to-orange-500',
      'module_assigned': 'from-indigo-500 to-indigo-600',
      'cheating_alert': 'from-red-500 to-red-600',
      'assignment': 'from-blue-500 to-indigo-600',
      'default': 'from-gray-500 to-gray-600'
    };
    return colors[type] || colors.default;
  }
  
  function getBorderColor(type) {
    const colors = {
      'lesson_assignment': 'border-blue-400',
      'quiz_available': 'border-green-400',
      'quiz_submission': 'border-purple-400',
      'results_released': 'border-orange-400',
      'module_assigned': 'border-indigo-400',
      'cheating_alert': 'border-red-400',
      'assignment': 'border-blue-400',
      'default': 'border-gray-400'
    };
    return colors[type] || colors.default;
  }
</script>

<div class="fixed top-4 right-4 z-[9999] space-y-3 pointer-events-none max-w-md">
  {#each notifications as notification (notification.id)}
    <div 
      class="pointer-events-auto w-full bg-white rounded-2xl shadow-2xl border-2 {getBorderColor(notification.type)} overflow-hidden transform hover:scale-105 transition-transform duration-200"
      in:fly="{{ x: 400, duration: 400, opacity: 0 }}"
      out:scale="{{ duration: 200, start: 0.8, opacity: 0 }}"
    >
      <!-- Animated pulse border -->
      <div class="absolute inset-0 rounded-2xl animate-pulse opacity-20 bg-gradient-to-r {getColor(notification.type)}"></div>
      
      <div class="relative flex items-start p-4 gap-4">
        <!-- Icon with animation -->
        <div class="flex-shrink-0 animate-bounce">
          <div class="w-14 h-14 rounded-full bg-gradient-to-br {getColor(notification.type)} flex items-center justify-center text-3xl shadow-lg ring-4 ring-white">
            {getIcon(notification.type)}
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <h4 class="text-base font-bold text-gray-900 mb-1 leading-tight">{notification.title}</h4>
          <p class="text-sm text-gray-700 leading-relaxed">{notification.message}</p>
          {#if notification.time}
            <p class="text-xs text-gray-500 mt-2 font-medium">🕒 {notification.time}</p>
          {/if}
        </div>
        
        <!-- Close button -->
        <button 
          class="flex-shrink-0 text-gray-400 hover:text-gray-700 transition-colors p-1 rounded-full hover:bg-gray-100"
          on:click={() => removeNotification(notification.id)}
          aria-label="Close notification"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
      
      <!-- Progress bar -->
      <div class="h-1.5 bg-gray-100">
        <div class="h-full bg-gradient-to-r {getColor(notification.type)} animate-shrink shadow-inner"></div>
      </div>
    </div>
  {/each}
</div>

<style>
  @keyframes shrink {
    from { width: 100%; }
    to { width: 0%; }
  }
  
  .animate-shrink {
    animation: shrink 5s linear forwards;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 0.2; }
    50% { opacity: 0.4; }
  }
</style>
