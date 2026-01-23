<script>
  import { onMount, onDestroy } from 'svelte';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';

  export let show = false;
  
  let rooms = [];
  let selectedRoom = null;
  let messages = [];
  let newMessage = '';
  let loading = false;
  let messagePolling = null;
  let showRoomList = true;
  let createRoomMode = false;
  
  // Create room form
  let newRoomName = '';
  let newRoomType = 'student-student';
  let newRoomDept = '';
  let newRoomLevel = '';
  
  const departments = [
    'Software Development',
    'Computer System and Architecture',
    'Land Surveying',
    'Building Construction'
  ];
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  
  $: if (show) {
    loadRooms();
  }
  
  $: if (selectedRoom) {
    loadMessages();
    startMessagePolling();
  } else {
    stopMessagePolling();
  }
  
  onDestroy(() => {
    stopMessagePolling();
  });
  
  async function loadRooms() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${api.baseURL}/chat/rooms`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        rooms = await response.json();
      }
    } catch (err) {
      console.error('Failed to load chat rooms:', err);
    }
  }
  
  async function loadMessages() {
    if (!selectedRoom) return;
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${api.baseURL}/chat/rooms/${selectedRoom.id}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        messages = await response.json();
        setTimeout(scrollToBottom, 100);
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  }
  
  function startMessagePolling() {
    stopMessagePolling();
    messagePolling = setInterval(loadMessages, 2000); // Poll every 2 seconds
  }
  
  function stopMessagePolling() {
    if (messagePolling) {
      clearInterval(messagePolling);
      messagePolling = null;
    }
  }
  
  async function sendMessage() {
    if (!newMessage.trim() || !selectedRoom) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${api.baseURL}/chat/rooms/${selectedRoom.id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: newMessage.trim(),
          message_type: 'text'
        })
      });
      
      if (response.ok) {
        newMessage = '';
        await loadMessages();
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  }
  
  async function createRoom() {
    if (!newRoomName.trim()) return;
    
    try {
      loading = true;
      const token = localStorage.getItem('token');
      const response = await fetch(`${api.baseURL}/chat/rooms`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newRoomName.trim(),
          room_type: newRoomType,
          department: newRoomDept,
          level: newRoomLevel
        })
      });
      
      if (response.ok) {
        newRoomName = '';
        newRoomDept = '';
        newRoomLevel = '';
        createRoomMode = false;
        await loadRooms();
      }
    } catch (err) {
      console.error('Failed to create room:', err);
    } finally {
      loading = false;
    }
  }
  
  function selectRoom(room) {
    selectedRoom = room;
    showRoomList = false;
  }
  
  function backToRooms() {
    selectedRoom = null;
    showRoomList = true;
    stopMessagePolling();
  }
  
  function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }
  
  function getRoomTypeLabel(type) {
    const labels = {
      'student-student': '👥 Students',
      'student-teacher': '👨‍🎓 Students & Teachers',
      'teacher-teacher': '👨‍🏫 Teachers Only',
      'teacher-dos': '🏛️ Teachers & DOS'
    };
    return labels[type] || type;
  }
  
  function getRoomTypeColor(type) {
    const colors = {
      'student-student': 'bg-blue-100 text-blue-800',
      'student-teacher': 'bg-green-100 text-green-800',
      'teacher-teacher': 'bg-purple-100 text-purple-800',
      'teacher-dos': 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  }
</script>

{#if show}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9998] p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[600px] flex flex-col">
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
        <div class="flex items-center space-x-3">
          {#if selectedRoom}
            <button on:click={backToRooms} class="hover:bg-white/20 p-2 rounded-lg transition-colors">
              ← Back
            </button>
            <div>
              <h2 class="text-xl font-bold">{selectedRoom.name}</h2>
              <p class="text-sm opacity-90">{getRoomTypeLabel(selectedRoom.room_type)}</p>
            </div>
          {:else}
            <span class="text-3xl">💬</span>
            <div>
              <h2 class="text-xl font-bold">Knowledge Hub</h2>
              <p class="text-sm opacity-90">Connect, Share, Learn Together</p>
            </div>
          {/if}
        </div>
        <button on:click={() => show = false} class="hover:bg-white/20 p-2 rounded-lg transition-colors text-2xl">
          ×
        </button>
      </div>
      
      <!-- Content -->
      <div class="flex-1 overflow-hidden flex">
        {#if showRoomList}
          <!-- Room List -->
          <div class="flex-1 flex flex-col">
            <div class="p-4 border-b flex justify-between items-center">
              <h3 class="font-semibold text-gray-700">Chat Rooms</h3>
              <button 
                on:click={() => createRoomMode = !createRoomMode}
                class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                + New Room
              </button>
            </div>
            
            {#if createRoomMode}
              <div class="p-4 bg-blue-50 border-b">
                <h4 class="font-semibold mb-3">Create New Room</h4>
                <div class="space-y-3">
                  <input
                    type="text"
                    bind:value={newRoomName}
                    placeholder="Room name"
                    class="w-full px-3 py-2 border rounded-lg"
                  />
                  <select bind:value={newRoomType} class="w-full px-3 py-2 border rounded-lg">
                    {#if $user?.role === 'student'}
                      <option value="student-student">Students Only</option>
                      <option value="student-teacher">Students & Teachers</option>
                    {:else if $user?.role === 'teacher'}
                      <option value="student-teacher">Students & Teachers</option>
                      <option value="teacher-teacher">Teachers Only</option>
                      <option value="teacher-dos">Teachers & DOS</option>
                    {:else}
                      <option value="teacher-dos">Teachers & DOS</option>
                    {/if}
                  </select>
                  {#if newRoomType.includes('student')}
                    <select bind:value={newRoomDept} class="w-full px-3 py-2 border rounded-lg">
                      <option value="">Select Department</option>
                      {#each departments as dept}
                        <option value={dept}>{dept}</option>
                      {/each}
                    </select>
                    <select bind:value={newRoomLevel} class="w-full px-3 py-2 border rounded-lg">
                      <option value="">Select Level</option>
                      {#each levels as level}
                        <option value={level}>{level}</option>
                      {/each}
                    </select>
                  {/if}
                  <div class="flex space-x-2">
                    <button 
                      on:click={createRoom}
                      disabled={loading || !newRoomName.trim()}
                      class="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      Create
                    </button>
                    <button 
                      on:click={() => createRoomMode = false}
                      class="px-4 py-2 border rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            {/if}
            
            <div class="flex-1 overflow-y-auto p-4 space-y-2">
              {#if rooms.length === 0}
                <div class="text-center py-12 text-gray-500">
                  <p class="text-4xl mb-2">💬</p>
                  <p>No chat rooms yet</p>
                  <p class="text-sm">Create one to start chatting!</p>
                </div>
              {:else}
                {#each rooms as room}
                  <button
                    on:click={() => selectRoom(room)}
                    class="w-full text-left p-4 rounded-lg border hover:bg-gray-50 transition-colors"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="font-semibold text-gray-900">{room.name}</h4>
                      {#if room.unread_count > 0}
                        <span class="bg-red-500 text-white text-xs px-2 py-1 rounded-full">{room.unread_count}</span>
                      {/if}
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="text-xs px-2 py-1 rounded-full {getRoomTypeColor(room.room_type)}">
                        {getRoomTypeLabel(room.room_type)}
                      </span>
                      {#if room.department}
                        <span class="text-xs text-gray-500">{room.department} - {room.level}</span>
                      {/if}
                    </div>
                  </button>
                {/each}
              {/if}
            </div>
          </div>
        {:else if selectedRoom}
          <!-- Chat Messages -->
          <div class="flex-1 flex flex-col">
            <div id="chat-messages" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
              {#each messages as message}
                <div class="flex {message.sender_id === $user?.id ? 'justify-end' : 'justify-start'}">
                  <div class="max-w-[70%]">
                    {#if message.sender_id !== $user?.id}
                      <div class="text-xs text-gray-600 mb-1 flex items-center space-x-2">
                        <span class="font-semibold">{message.sender_name}</span>
                        <span class="px-2 py-0.5 rounded-full text-xs {message.sender_role === 'admin' ? 'bg-red-100 text-red-800' : message.sender_role === 'teacher' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}">
                          {message.sender_role}
                        </span>
                      </div>
                    {/if}
                    <div class="px-4 py-2 rounded-2xl {message.sender_id === $user?.id ? 'bg-blue-600 text-white' : 'bg-white border'}">
                      <p class="text-sm">{message.message}</p>
                      <p class="text-xs opacity-70 mt-1">{new Date(message.created_at).toLocaleTimeString()}</p>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
            
            <!-- Message Input -->
            <div class="p-4 border-t bg-white">
              <form on:submit|preventDefault={sendMessage} class="flex space-x-2">
                <input
                  type="text"
                  bind:value={newMessage}
                  placeholder="Type your message..."
                  class="flex-1 px-4 py-3 border rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  class="bg-blue-600 text-white px-6 py-3 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
                >
                  Send 📤
                </button>
              </form>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
