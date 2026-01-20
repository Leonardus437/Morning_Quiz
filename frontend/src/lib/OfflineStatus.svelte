<script>
  import { connectionStatus, syncStore, canSync, syncManager } from './stores.js';
  
  let showDetails = false;
  
  async function handleSync() {
    await syncManager.forcSync();
  }
  
  function formatTime(timestamp) {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
  }
</script>

<!-- Offline Status Bar -->
{#if !$connectionStatus}
  <div class="fixed top-0 left-0 right-0 bg-red-600 text-white px-4 py-2 text-sm font-medium z-50 flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <span class="w-2 h-2 bg-red-300 rounded-full animate-pulse"></span>
      <span>You're offline - Some features may be limited</span>
    </div>
    <button 
      class="text-red-200 hover:text-white"
      on:click={() => showDetails = !showDetails}
    >
      {showDetails ? '' : ''}
    </button>
  </div>
{:else if $syncStore.pendingItems > 0}
  <div class="fixed top-0 left-0 right-0 bg-yellow-600 text-white px-4 py-2 text-sm font-medium z-50 flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <span class="w-2 h-2 bg-yellow-300 rounded-full animate-pulse"></span>
      <span>{$syncStore.pendingItems} items pending sync</span>
      {#if $syncStore.isSyncing}
        <span class="text-yellow-200">Syncing...</span>
      {/if}
    </div>
    <div class="flex items-center space-x-2">
      {#if $canSync && !$syncStore.isSyncing}
        <button 
          class="bg-yellow-700 hover:bg-yellow-800 px-3 py-1 rounded text-xs"
          on:click={handleSync}
        >
          Sync Now
        </button>
      {/if}
      <button 
        class="text-yellow-200 hover:text-white"
        on:click={() => showDetails = !showDetails}
      >
        {showDetails ? '' : ''}
      </button>
    </div>
  </div>
{/if}

<!-- Detailed Status Panel -->
{#if showDetails}
  <div class="fixed top-12 left-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg z-40 p-4 max-w-md mx-auto">
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">Connection Status</h3>
        <button 
          class="text-gray-400 hover:text-gray-600"
          on:click={() => showDetails = false}
        >
          
        </button>
      </div>
      
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-600">Connection:</span>
          <span class="font-medium {$connectionStatus ? 'text-green-600' : 'text-red-600'}">
            {$connectionStatus ? ' Online' : ' Offline'}
          </span>
        </div>
        
        <div class="flex justify-between">
          <span class="text-gray-600">Pending Items:</span>
          <span class="font-medium text-gray-900">{$syncStore.pendingItems}</span>
        </div>
        
        <div class="flex justify-between">
          <span class="text-gray-600">Last Sync:</span>
          <span class="font-medium text-gray-900">{formatTime($syncStore.lastSync)}</span>
        </div>
        
        {#if $syncStore.isSyncing}
          <div class="flex justify-between">
            <span class="text-gray-600">Status:</span>
            <span class="font-medium text-blue-600"> Syncing...</span>
          </div>
        {/if}
        
        {#if $syncStore.errors.length > 0}
          <div class="mt-3 p-2 bg-red-50 border border-red-200 rounded">
            <div class="text-red-800 font-medium text-xs">Recent Errors:</div>
            {#each $syncStore.errors.slice(-3) as error}
              <div class="text-red-600 text-xs mt-1">{error}</div>
            {/each}
          </div>
        {/if}
      </div>
      
      {#if $canSync}
        <button 
          class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm font-medium"
          on:click={handleSync}
        >
          Sync Now
        </button>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Ensure the status bar doesn't interfere with page content */
  :global(body) {
    padding-top: 0;
  }
  
  :global(.offline-aware) {
    padding-top: 48px;
  }
</style>