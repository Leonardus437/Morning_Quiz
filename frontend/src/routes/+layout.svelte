<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { user, connectionStatus, syncStore } from '$lib/stores.js';
  import { api } from '$lib/api.js';
  import OfflineStatus from '$lib/OfflineStatus.svelte';
  import NotificationToast from '$lib/NotificationToast.svelte';
  import { notificationStore } from '$lib/notificationStore.js';
  
  let isOffline = false;
  let showOfflineToast = false;
  let offlineToastMessage = '';
  let notifications = [];
  
  $: notifications = $notificationStore || [];
  
  onMount(() => {
    user.init();
  });
  
  function dismissToast() {
    showOfflineToast = false;
  }
  
  function refreshApp() {
    window.location.reload();
  }
</script>

<svelte:head>
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
</svelte:head>

<!-- Offline Status Component re-enabled with clean state -->
<OfflineStatus />

<!-- Notification Toast -->
<NotificationToast {notifications} />

<!-- Connection Status Toast -->
{#if showOfflineToast}
  <div class="fixed top-4 right-4 z-50 max-w-sm">
    <div class="bg-white border border-gray-200 rounded-lg shadow-lg p-4 flex items-start space-x-3">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-900">{offlineToastMessage}</p>
        {#if offlineToastMessage.includes('updated')}
          <button 
            class="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
            on:click={refreshApp}
          >
            Refresh Now
          </button>
        {/if}
      </div>
      <button 
        class="text-gray-400 hover:text-gray-600"
        on:click={dismissToast}
      >
        
      </button>
    </div>
  </div>
{/if}

<!-- Offline Banner -->
{#if isOffline}
  <div class="bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-center py-3 px-4 text-sm font-medium shadow-lg">
    <div class="flex items-center justify-center space-x-2">
      <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
      <span> Offline Mode Active - Limited functionality available</span>
      <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
    </div>
  </div>
{/if}

<main class="min-h-screen bg-white {isOffline ? 'pt-12' : ''}">
  <slot />
</main>

<style>
  /* Ensure smooth transitions */
  main {
    transition: padding-top 0.3s ease;
  }
</style>
