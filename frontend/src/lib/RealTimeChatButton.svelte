<script>
  import { onMount } from 'svelte';
  import { user } from './stores.js';
  import ModernChatModal from './ModernChatModal.svelte';

  let showModal = false;
  let unreadCount = 0;
  let currentUser;

  user.subscribe(value => {
    currentUser = value;
  });

  function openChat() {
    showModal = true;
  }

  function closeChat() {
    showModal = false;
  }

  // Check for unread messages periodically
  onMount(() => {
    if (!currentUser) return;
    
    const checkUnread = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/chat/unread-count`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          unreadCount = data.count || 0;
        }
      } catch (error) {
        console.log('Error checking unread messages:', error);
      }
    };

    // Check immediately and then every 10 seconds
    checkUnread();
    const interval = setInterval(checkUnread, 10000);
    
    return () => clearInterval(interval);
  });
</script>

{#if currentUser}
  <button
    class="fixed bottom-20 right-6 z-50 bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 flex items-center justify-center animate-pulse hover:animate-none group"
    on:click={openChat}
    title="Vibe Chat 💬"
  >
    <div class="relative">
      <span class="text-3xl group-hover:scale-125 transition-transform">💬</span>
      {#if unreadCount > 0}
        <span class="absolute -top-3 -right-3 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold animate-bounce shadow-lg">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      {/if}
    </div>
  </button>

  {#if showModal}
    <ModernChatModal {closeChat} />
  {/if}
{/if}