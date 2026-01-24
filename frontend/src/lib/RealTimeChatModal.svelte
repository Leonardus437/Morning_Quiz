<script>
  import { onMount, onDestroy } from 'svelte';
  import { user } from './stores.js';

  export let closeChat;

  let currentUser;
  let rooms = [];
  let selectedRoom = null;
  let messages = [];
  let newMessage = '';
  let messageContainer;
  let loading = false;
  let showCreateRoom = false;
  let showEditRoom = false;
  let newRoomData = {
    name: '',
    room_type: 'student-student',
    department: '',
    level: ''
  };
  let editRoomData = {
    id: null,
    name: '',
    room_type: '',
    department: '',
    level: ''
  };
  let availableDepartments = [
    'Software Development',
    'Building Construction',
    'Land Surveying',
    'Computer System and Architecture'
  ];
  let availableLevels = ['Level 3', 'Level 4', 'Level 5'];
  let estimatedParticipants = 0;
  let messagePolling;

  user.subscribe(value => {
    currentUser = value;
    if (value) {
      newRoomData.department = value.department || '';
      newRoomData.level = value.level || '';
    }
  });

  const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://tvet-quiz-backend.onrender.com';

  async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  async function loadRooms() {
    try {
      loading = true;
      rooms = await apiCall('/chat/rooms');
    } catch (error) {
      console.error('Error loading rooms:', error);
    } finally {
      loading = false;
    }
  }

  async function estimateParticipantCount() {
    if (!newRoomData.department || !newRoomData.level) {
      estimatedParticipants = 0;
      return;
    }
    try {
      const students = await apiCall('/students');
      const count = students.filter(s => 
        s.department === newRoomData.department && 
        s.level === newRoomData.level
      ).length;
      estimatedParticipants = count;
    } catch (error) {
      estimatedParticipants = 0;
    }
  }

  async function loadMessages(roomId) {
    try {
      messages = await apiCall(`/chat/rooms/${roomId}/messages`);
      scrollToBottom();
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  }

  async function sendMessage() {
    if (!newMessage.trim() || !selectedRoom) return;
    
    try {
      const message = await apiCall(`/chat/rooms/${selectedRoom.id}/messages`, {
        method: 'POST',
        body: JSON.stringify({
          message: newMessage.trim(),
          message_type: 'text'
        })
      });
      
      messages = [...messages, message];
      newMessage = '';
      scrollToBottom();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  async function deleteRoom(roomId) {
    if (!confirm('⚠️ Are you sure you want to delete this chat room? All messages will be permanently deleted.')) {
      return;
    }
    
    try {
      loading = true;
      await apiCall(`/chat/rooms/${roomId}`, {
        method: 'DELETE'
      });
      
      rooms = rooms.filter(r => r.id !== roomId);
      if (selectedRoom?.id === roomId) {
        selectedRoom = null;
        messages = [];
      }
      alert('✅ Chat room deleted successfully!');
    } catch (error) {
      console.error('Error deleting room:', error);
      alert('❌ Failed to delete chat room. You may not have permission.');
    } finally {
      loading = false;
    }
  }

  async function openEditRoom(room) {
    editRoomData = {
      id: room.id,
      name: room.name,
      room_type: room.room_type,
      department: room.department || '',
      level: room.level || ''
    };
    showEditRoom = true;
  }

  async function updateRoom() {
    if (!editRoomData.name.trim()) return;
    
    try {
      loading = true;
      const updatedRoom = await apiCall(`/chat/rooms/${editRoomData.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          name: editRoomData.name,
          room_type: editRoomData.room_type,
          department: editRoomData.department,
          level: editRoomData.level
        })
      });
      
      rooms = rooms.map(r => r.id === editRoomData.id ? {...r, ...updatedRoom} : r);
      if (selectedRoom?.id === editRoomData.id) {
        selectedRoom = {...selectedRoom, ...updatedRoom};
      }
      showEditRoom = false;
      alert('✅ Chat room updated successfully!');
    } catch (error) {
      console.error('Error updating room:', error);
      alert('❌ Failed to update chat room. You may not have permission.');
    } finally {
      loading = false;
    }
  }

  function canManageRoom(room) {
    return room.created_by === currentUser?.id;
  }

  async function createRoom() {
    if (!newRoomData.name.trim()) return;
    if (newRoomData.room_type.includes('student') && (!newRoomData.department || !newRoomData.level)) {
      alert('Please select both Trade/Department and Level for student rooms');
      return;
    }
    
    try {
      loading = true;
      const room = await apiCall('/chat/rooms', {
        method: 'POST',
        body: JSON.stringify({
          ...newRoomData,
          notify_participants: true
        })
      });
      
      rooms = [...rooms, room];
      showCreateRoom = false;
      estimatedParticipants = 0;
      newRoomData = {
        name: '',
        room_type: 'student-student',
        department: currentUser?.department || '',
        level: currentUser?.level || ''
      };
      
      alert(`✅ Chat room created! ${room.participants_added || 0} participants added and notified.`);
    } catch (error) {
      console.error('Error creating room:', error);
      alert('Failed to create chat room. Please try again.');
    } finally {
      loading = false;
    }
  }

  function selectRoom(room) {
    selectedRoom = room;
    loadMessages(room.id);
    startMessagePolling();
  }

  function startMessagePolling() {
    if (messagePolling) clearInterval(messagePolling);
    
    messagePolling = setInterval(async () => {
      if (selectedRoom) {
        try {
          const newMessages = await apiCall(`/chat/rooms/${selectedRoom.id}/messages`);
          if (newMessages.length !== messages.length) {
            messages = newMessages;
            scrollToBottom();
          }
        } catch (error) {
          console.log('Polling error:', error);
        }
      }
    }, 3000);
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
    }, 100);
  }

  function getRoomTypeDisplay(roomType) {
    const types = {
      'student-student': '👥 Student Discussion',
      'student-teacher': '🎓 Student-Teacher',
      'teacher-teacher': '👨‍🏫 Teacher Lounge',
      'teacher-dos': '🏛️ Teacher-DOS'
    };
    return types[roomType] || roomType;
  }

  function getRoomTypeOptions() {
    if (currentUser?.role === 'admin') {
      return [
        { value: 'student-student', label: '👥 Student Discussion' },
        { value: 'student-teacher', label: '🎓 Student-Teacher' },
        { value: 'teacher-teacher', label: '👨‍🏫 Teacher Lounge' },
        { value: 'teacher-dos', label: '🏛️ Teacher-DOS' }
      ];
    } else if (currentUser?.role === 'teacher') {
      return [
        { value: 'student-teacher', label: '🎓 Student-Teacher' },
        { value: 'teacher-teacher', label: '👨‍🏫 Teacher Lounge' },
        { value: 'teacher-dos', label: '🏛️ Teacher-DOS' }
      ];
    } else {
      return [
        { value: 'student-student', label: '👥 Student Discussion' },
        { value: 'student-teacher', label: '🎓 Ask Teachers' }
      ];
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  onMount(() => {
    loadRooms();
  });

  $: if (newRoomData.department && newRoomData.level && newRoomData.room_type.includes('student')) {
    estimateParticipantCount();
  }

  onDestroy(() => {
    if (messagePolling) clearInterval(messagePolling);
  });
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[50] p-4">
  <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-t-lg">
      <h2 class="text-xl font-bold">💬 Real-Time Chat</h2>
      <button on:click={closeChat} class="text-white hover:text-gray-200 text-2xl">&times;</button>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar - Room List -->
      <div class="w-1/3 border-r bg-gray-50 flex flex-col">
        {#if currentUser?.role === 'admin' || currentUser?.role === 'teacher'}
          <div class="p-4 border-b">
            <button
              on:click={() => showCreateRoom = true}
              class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              ➕ Create Room
            </button>
          </div>
        {/if}

        <div class="flex-1 overflow-y-auto">
          {#if loading}
            <div class="p-4 text-center text-gray-500">Loading rooms...</div>
          {:else if rooms.length === 0}
            <div class="p-4 text-center text-gray-500">No chat rooms available</div>
          {:else}
            {#each rooms as room}
              <button
                class="w-full text-left p-3 border-b hover:bg-gray-100 transition-colors {selectedRoom?.id === room.id ? 'bg-blue-100 border-l-4 border-l-blue-500' : ''}"
                on:click={() => selectRoom(room)}
              >
                <div class="font-medium text-sm">{room.name}</div>
                <div class="text-xs text-gray-500">{getRoomTypeDisplay(room.room_type)}</div>
                {#if room.department && room.level}
                  <div class="text-xs text-gray-400">{room.department} - {room.level}</div>
                {/if}
              </button>
            {/each}
          {/if}
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col">
        {#if selectedRoom}
          <!-- Chat Header -->
          <div class="p-4 border-b bg-gray-50 flex items-center justify-between">
            <div>
              <h3 class="font-bold">{selectedRoom.name}</h3>
              <p class="text-sm text-gray-600">{getRoomTypeDisplay(selectedRoom.room_type)}</p>
              {#if selectedRoom.department && selectedRoom.level}
                <p class="text-xs text-gray-500">{selectedRoom.department} - {selectedRoom.level}</p>
              {/if}
            </div>
            {#if canManageRoom(selectedRoom)}
              <div class="flex space-x-2">
                <button
                  on:click={() => openEditRoom(selectedRoom)}
                  class="px-3 py-1.5 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                  title="Edit Room"
                >
                  ✏️ Edit
                </button>
                <button
                  on:click={() => deleteRoom(selectedRoom.id)}
                  class="px-3 py-1.5 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                  title="Delete Room"
                >
                  🗑️ Delete
                </button>
              </div>
            {/if}
          </div>

          <!-- Messages -->
          <div bind:this={messageContainer} class="flex-1 overflow-y-auto p-4 space-y-3">
            {#each messages as message}
              <div class="flex {message.sender_id === currentUser?.id ? 'justify-end' : 'justify-start'}">
                <div class="max-w-xs lg:max-w-md {message.sender_id === currentUser?.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'} rounded-lg px-4 py-2">
                  {#if message.sender_id !== currentUser?.id}
                    <div class="text-xs font-medium mb-1 {message.sender_role === 'admin' ? 'text-red-600' : message.sender_role === 'teacher' ? 'text-green-600' : 'text-blue-600'}">
                      {message.sender_name} ({message.sender_role})
                    </div>
                  {/if}
                  <div class="text-sm">{message.message}</div>
                  <div class="text-xs opacity-75 mt-1">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            {/each}
          </div>

          <!-- Message Input -->
          <div class="p-4 border-t">
            <div class="flex space-x-2">
              <textarea
                bind:value={newMessage}
                on:keypress={handleKeyPress}
                placeholder="Type your message..."
                class="flex-1 border rounded-lg px-3 py-2 resize-none"
                rows="2"
              ></textarea>
              <button
                on:click={sendMessage}
                disabled={!newMessage.trim()}
                class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        {:else}
          <div class="flex-1 flex items-center justify-center text-gray-500">
            <div class="text-center">
              <div class="text-4xl mb-4">💬</div>
              <p>Select a room to start chatting</p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<!-- Create Room Modal -->
{#if showCreateRoom}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold text-gray-800">🎯 Create New Chat Room</h3>
        <button on:click={() => showCreateRoom = false} class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">📝 Room Name *</label>
          <input
            bind:value={newRoomData.name}
            type="text"
            placeholder="e.g., Building Construction Discussion"
            class="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">🏷️ Room Type *</label>
          <select bind:value={newRoomData.room_type} class="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            {#each getRoomTypeOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        {#if newRoomData.room_type.includes('student')}
          <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 space-y-3">
            <p class="text-sm font-medium text-blue-800 mb-3">🎓 Class-Based Group Chat</p>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">🏗️ Trade / Department *</label>
              <select
                bind:value={newRoomData.department}
                class="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">-- Select Trade/Department --</option>
                {#each availableDepartments as dept}
                  <option value={dept}>{dept}</option>
                {/each}
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">📊 Level *</label>
              <select
                bind:value={newRoomData.level}
                class="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">-- Select Level --</option>
                {#each availableLevels as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>

            {#if estimatedParticipants > 0}
              <div class="bg-green-100 border border-green-300 rounded-lg p-3 mt-3">
                <p class="text-sm font-medium text-green-800">
                  👥 Estimated Participants: <span class="font-bold">{estimatedParticipants} students</span>
                  {#if newRoomData.room_type === 'student-teacher'}
                    + teachers + class teacher
                  {/if}
                </p>
                <p class="text-xs text-green-700 mt-1">✅ All participants will be notified automatically</p>
              </div>
            {/if}
          </div>

          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p class="text-xs text-yellow-800">
              <span class="font-semibold">ℹ️ Note:</span> All students in <span class="font-semibold">{newRoomData.department || 'selected trade'} - {newRoomData.level || 'selected level'}</span> will be automatically added.
              {#if newRoomData.room_type === 'student-teacher'}
                <br/>The assigned class teacher will also be notified and added.
              {/if}
            </p>
          </div>
        {/if}
      </div>

      <div class="flex justify-end space-x-3 mt-6">
        <button
          on:click={() => {
            showCreateRoom = false;
            estimatedParticipants = 0;
            newRoomData = {
              name: '',
              room_type: 'student-student',
              department: currentUser?.department || '',
              level: currentUser?.level || ''
            };
          }}
          class="px-5 py-2.5 text-gray-700 font-medium hover:text-gray-900 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          on:click={createRoom}
          disabled={!newRoomData.name.trim() || loading}
          class="bg-gradient-to-r from-blue-500 to-green-500 text-white font-semibold px-6 py-2.5 rounded-lg hover:from-blue-600 hover:to-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
        >
          {loading ? '⏳ Creating...' : '✨ Create Room'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Edit Room Modal -->
{#if showEditRoom}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold text-gray-800">✏️ Edit Chat Room</h3>
        <button on:click={() => showEditRoom = false} class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">📝 Room Name *</label>
          <input
            bind:value={editRoomData.name}
            type="text"
            class="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p class="text-xs text-gray-600">
            <span class="font-semibold">ℹ️ Note:</span> Room type, department, and level cannot be changed after creation.
          </p>
        </div>
      </div>

      <div class="flex justify-end space-x-3 mt-6">
        <button
          on:click={() => showEditRoom = false}
          class="px-5 py-2.5 text-gray-700 font-medium hover:text-gray-900 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          on:click={updateRoom}
          disabled={!editRoomData.name.trim() || loading}
          class="bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
        >
          {loading ? '⏳ Updating...' : '💾 Save Changes'}
        </button>
      </div>
    </div>
  </div>
{/if}