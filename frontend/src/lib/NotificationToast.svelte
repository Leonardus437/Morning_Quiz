<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
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
      'default': 'from-gray-500 to-gray-600'
    };
    return colors[type] || colors.default;
  }
</script>

<div class="fixed top-4 right-4 z-[9999] space-y-3 pointer-events-none">
  {#each notifications as notification (notification.id)}
    <div 
      class="pointer-events-auto w-96 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden"
      in:fly="{{ x: 400, duration: 300 }}"
      out:fade="{{ duration: 200 }}"
    >
      <div class="flex items-start p-4">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br {getColor(notification.type)} flex items-center justify-center text-2xl shadow-lg">
            {getIcon(notification.type)}
          </div>
        </div>
        <div class="ml-4 flex-1">
          <h4 class="text-sm font-bold text-gray-900 mb-1">{notification.title}</h4>
          <p class="text-sm text-gray-600">{notification.message}</p>
          {#if notification.time}
            <p class="text-xs text-gray-400 mt-1">{notification.time}</p>
          {/if}
        </div>
        <button 
          class="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
          on:click={() => removeNotification(notification.id)}
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
      <div class="h-1 bg-gradient-to-r {getColor(notification.type)} animate-shrink"></div>
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
</style>
