<script>
  import { user } from '$lib/stores.js';
  import ChatModal from './ChatModal.svelte';
  
  let showChat = false;
  let hasUnread = false;
  
  function toggleChat() {
    showChat = !showChat;
    if (showChat) {
      hasUnread = false;
    }
  }
</script>

{#if $user}
  <!-- Floating Chat Button -->
  <button
    on:click={toggleChat}
    class="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300 z-[9999] group"
    title="Open Knowledge Hub Chat"
  >
    <div class="relative">
      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
      </svg>
      {#if hasUnread}
        <span class="absolute -top-1 -right-1 bg-red-500 w-3 h-3 rounded-full animate-pulse"></span>
      {/if}
    </div>
    <span class="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
      Knowledge Hub 💬
    </span>
  </button>
  
  <!-- Chat Modal -->
  <ChatModal bind:show={showChat} />
{/if}
