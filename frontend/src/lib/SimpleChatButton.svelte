<script>
  import { user } from '$lib/stores.js';
  import ChatModal from './ChatModal.svelte';
  
  let showChat = false;
  
  function toggleChat() {
    showChat = !showChat;
  }
</script>

<!-- Always visible chat button (for debugging) -->
<button
  on:click={toggleChat}
  class="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg z-[9999] transition-all duration-300"
  title="Knowledge Hub Chat"
  style="width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;"
>
  💬
</button>

<!-- Status indicator -->
{#if $user}
  <div class="fixed bottom-20 right-6 bg-green-500 text-white px-3 py-1 rounded-full text-xs z-[9998]">
    ✅ Logged in as {$user.role}
  </div>
{:else}
  <div class="fixed bottom-20 right-6 bg-red-500 text-white px-3 py-1 rounded-full text-xs z-[9998]">
    ❌ Not logged in
  </div>
{/if}

<!-- Chat Modal -->
<ChatModal bind:show={showChat} />