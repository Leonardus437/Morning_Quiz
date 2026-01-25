<script>
  import { onMount, onDestroy } from 'svelte';
  import { user } from './stores.js';
  import ModernChatModal from './ModernChatModal.svelte';

  let showModal = false;
  let unreadCount = 0;
  let previousCount = 0;
  let currentUser;
  let theme = 'light';
  let interval;
  let showPulse = false;

  user.subscribe(value => {
    currentUser = value;
  });

  function openChat() {
    showModal = true;
    unreadCount = 0;
    showPulse = false;
  }

  function closeChat() {
    showModal = false;
  }

  const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://tvet-quiz-backend.onrender.com';

  async function checkUnread() {
    if (!currentUser || showModal) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const response = await fetch(`${API_BASE}/chat/unread-count`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        const newCount = data.count || 0;
        
        if (newCount > previousCount) {
          showPulse = true;
          setTimeout(() => showPulse = false, 2000);
        }
        
        previousCount = unreadCount;
        unreadCount = newCount;
      }
    } catch (error) {
      console.log('Error checking unread:', error);
    }
  }

  onMount(() => {
    const savedTheme = localStorage.getItem('chatTheme');
    if (savedTheme) theme = savedTheme;
    
    checkUnread();
    interval = setInterval(checkUnread, 5000);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
</script>

{#if currentUser}
  <button
    class="fixed bottom-20 right-6 z-50 {theme === 'light' ? 'bg-black text-white border-black' : 'bg-white text-black border-white'} border-2 p-4 shadow-lg transition-all flex items-center justify-center group hover:scale-110 {showPulse ? 'animate-bounce' : ''}"
    on:click={openChat}
    title="Chat {unreadCount > 0 ? `(${unreadCount} unread)` : ''}"
  >
    <div class="relative">
      <span class="text-2xl">💬</span>
      {#if unreadCount > 0}
        <span class="absolute -top-3 -right-3 {theme === 'light' ? 'bg-red-600' : 'bg-red-500'} text-white text-xs min-w-[20px] h-5 px-1.5 flex items-center justify-center font-bold rounded-full shadow-lg border-2 {theme === 'light' ? 'border-black' : 'border-white'} {showPulse ? 'animate-ping-once' : ''}">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      {/if}
    </div>
  </button>

  {#if showModal}
    <ModernChatModal {closeChat} />
  {/if}
{/if}

<style>
  @keyframes ping-once {
    0% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.3);
      opacity: 0.8;
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
  
  .animate-ping-once {
    animation: ping-once 0.6s ease-in-out;
  }
</style>