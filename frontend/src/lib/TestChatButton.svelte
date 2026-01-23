<script>
  import { user } from '$lib/stores.js';
  import { onMount } from 'svelte';
  
  let debugInfo = {
    userLoggedIn: false,
    userRole: null,
    tokenExists: false,
    currentUrl: '',
    chatButtonExists: false
  };
  
  onMount(() => {
    // Debug information
    debugInfo.userLoggedIn = !!$user;
    debugInfo.userRole = $user?.role || null;
    debugInfo.tokenExists = !!localStorage.getItem('token');
    debugInfo.currentUrl = window.location.href;
    debugInfo.chatButtonExists = !!document.querySelector('button[title*="Chat"]');
    
    console.log('🔍 Chat Debug Info:', debugInfo);
  });
  
  function testChatButton() {
    alert(`Chat Test Results:
    
✅ User Logged In: ${debugInfo.userLoggedIn}
👤 User Role: ${debugInfo.userRole || 'None'}
🔑 Token Exists: ${debugInfo.tokenExists}
🌐 Current URL: ${debugInfo.currentUrl}
💬 Chat Button Found: ${debugInfo.chatButtonExists}

${debugInfo.userLoggedIn ? '✅ You should see the chat button!' : '❌ Please log in first to see the chat button.'}`);
  }
</script>

{#if $user}
  <!-- Test Chat Button - Only shows when logged in -->
  <button
    on:click={testChatButton}
    class="fixed bottom-20 right-6 bg-red-600 text-white p-3 rounded-full shadow-lg hover:bg-red-700 transition-all z-[9998]"
    title="Test Chat System"
  >
    🔍 TEST
  </button>
{/if}

<!-- Always visible debug button for troubleshooting -->
<button
  on:click={testChatButton}
  class="fixed bottom-32 right-6 bg-yellow-600 text-white p-2 rounded-full shadow-lg hover:bg-yellow-700 transition-all z-[9998] text-xs"
  title="Debug Chat System"
>
  🐛
</button>