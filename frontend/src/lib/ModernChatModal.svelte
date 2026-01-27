<script>
  import { onMount, onDestroy } from 'svelte';
  import { user } from './stores.js';
  import { Sun, Moon, Palette, Send, Paperclip, Smile, X, Reply, Trash2, FileText, Image as ImageIcon, Video, File, Download, Eye } from 'lucide-svelte';

  export let closeChat;

  let currentUser;
  let rooms = [];
  let selectedRoom = null;
  let messages = [];
  let newMessage = '';
  let messageContainer;
  let loading = false;
  let showCreateRoom = false;
  let showEmojiPicker = false;
  let showEditRoom = false;
  let replyingTo = null;
  let fileInput;
  let uploadingFile = false;
  let theme = 'light'; // 'light', 'dark'
  let typingUsers = new Set();
  let typingTimeout = null;
  let previewFile = null;
  let showPreview = false;
  let showFormatting = false;
  let textFormat = {
    bold: false,
    italic: false,
    underline: false,
    size: 'normal',
    color: 'default'
  };
  
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

  // Popular emojis for quick reactions
  const quickEmojis = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎉', '👏'];
  const allEmojis = ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '🥲', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '🧐', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '👇', '☝️', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁️', '👅', '👄', '💋', '🩸', '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❤️‍🔥', '❤️‍🩹', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️', '📴', '📳', '🈶', '🈚', '🈸', '🈺', '🈷️', '✴️', '🆚', '💮', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '❌', '⭕', '🛑', '⛔', '📛', '🚫', '💯', '💢', '♨️', '🚷', '🚯', '🚳', '🚱', '🔞', '📵', '🚭', '❗', '❕', '❓', '❔', '‼️', '⁉️', '🔅', '🔆', '〽️', '⚠️', '🚸', '🔱', '⚜️', '🔰', '♻️', '✅', '🈯', '💹', '❇️', '✳️', '❎', '🌐', '💠', '🔠', '🔡', '🔢', '🔣', '🔤', '🅿️', '🚾', '🔽', '🔼', '🔺', '🔻', '🆗', '🆙', '🆒', '🆕', '🆓', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '#️⃣', '*️⃣', '⏏️', '▶️', '⏸️', '⏯️', '⏹️', '⏺️', '⏭️', '⏮️', '⏩', '⏪', '⏫', '⏬', '◀️', '🔼', '🔽', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '↕️', '↔️', '↪️', '↩️', '⤴️', '⤵️', '🔀', '🔁', '🔂', '🔄', '🔃', '🎵', '🎶', '➕', '➖', '➗', '✖️', '♾️', '💲', '💱', '™️', '©️', '®️', '〰️', '➰', '➿', '🔚', '🔙', '🔛', '🔝', '🔜', '✔️', '☑️', '🔘', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤', '🔺', '🔻', '🔸', '🔹', '🔶', '🔷', '🔳', '🔲', '▪️', '▫️', '◾', '◽', '◼️', '◻️', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫', '🔈', '🔇', '🔉', '🔊', '🔔', '🔕', '📣', '📢', '👁️‍🗨️', '💬', '💭', '🗯️', '♠️', '♣️', '♥️', '♦️', '🃏', '🎴', '🀄', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛', '🕜', '🕝', '🕞', '🕟', '🕠', '🕡', '🕢', '🕣', '🕤', '🕥', '🕦', '🕧', '🎯', '🔥', '💧', '🌊', '🎄', '✨', '🎈', '🎉', '🎊', '🎁', '🏆', '🥇', '🥈', '🥉', '⚽', '⚾', '🥎', '🏀', '🏐', '🏈', '🏉', '🎾', '🥏', '🎳', '🏏', '🏑', '🏒', '🥍', '🏓', '🏸', '🥊', '🥋', '🥅', '⛳', '⛸️', '🎣', '🤿', '🎽', '🎿', '🛷', '🥌'];

  user.subscribe(value => {
    currentUser = value;
    if (value) {
      newRoomData.department = value.department || '';
      newRoomData.level = value.level || '';
    }
  });

  const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://tvet-quiz-backend.onrender.com';

  // Minimal Theme configurations - Black & White only
  const themes = {
    light: {
      bg: 'bg-white',
      card: 'bg-white',
      border: 'border-black',
      text: 'text-black',
      accent: 'bg-black'
    },
    dark: {
      bg: 'bg-black',
      card: 'bg-black',
      border: 'border-white',
      text: 'text-white',
      accent: 'bg-white'
    }
  };

  $: currentTheme = themes[theme];

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

  async function loadMessages(roomId) {
    try {
      messages = await apiCall(`/chat/rooms/${roomId}/messages`);
      scrollToBottom();
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  }

  function handleTyping() {
    if (!selectedRoom) return;
    
    // Clear existing timeout
    if (typingTimeout) clearTimeout(typingTimeout);
    
    // Broadcast typing indicator (in real app, use WebSocket)
    // For now, just simulate locally
    typingTimeout = setTimeout(() => {
      // Stop typing after 3 seconds of inactivity
    }, 3000);
  }

  async function sendMessage() {
    if (!newMessage.trim() || !selectedRoom) return;
    
    try {
      const formattedMessage = applyFormatting(newMessage.trim());
      const message = await apiCall(`/chat/rooms/${selectedRoom.id}/messages`, {
        method: 'POST',
        body: JSON.stringify({
          message: formattedMessage,
          message_type: 'text',
          reply_to_id: replyingTo?.id
        })
      });
      
      messages = [...messages, message];
      newMessage = '';
      replyingTo = null;
      resetFormatting();
      scrollToBottom();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  function applyFormatting(text) {
    let formatted = text;
    const styles = [];
    
    if (textFormat.bold) styles.push('font-weight:bold');
    if (textFormat.italic) styles.push('font-style:italic');
    if (textFormat.underline) styles.push('text-decoration:underline');
    if (textFormat.size === 'small') styles.push('font-size:0.75rem');
    if (textFormat.size === 'large') styles.push('font-size:1.25rem');
    if (textFormat.size === 'xlarge') styles.push('font-size:1.5rem');
    if (textFormat.color !== 'default') styles.push(`color:${textFormat.color}`);
    
    if (styles.length > 0) {
      formatted = `<span style="${styles.join(';')}">${text}</span>`;
    }
    
    return formatted;
  }

  function resetFormatting() {
    textFormat = {
      bold: false,
      italic: false,
      underline: false,
      size: 'normal',
      color: 'default'
    };
  }

  function cycleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('chatTheme', theme);
  }

  onMount(() => {
    const savedTheme = localStorage.getItem('chatTheme');
    if (savedTheme && themes[savedTheme]) {
      theme = savedTheme;
    }
  });

  function getFileIcon(fileName) {
    const ext = fileName.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return '🖼️';
    if (['mp4', 'webm', 'mov', 'avi', 'mkv'].includes(ext)) return '🎥';
    if (['pdf'].includes(ext)) return '📄';
    if (['doc', 'docx'].includes(ext)) return '📝';
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return '📦';
    if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) return '🎵';
    if (['xls', 'xlsx', 'csv'].includes(ext)) return '📊';
    if (['ppt', 'pptx'].includes(ext)) return '📽️';
    return '📎';
  }

  function getFileType(fileName) {
    const ext = fileName.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return 'image';
    if (['mp4', 'webm', 'mov', 'avi', 'mkv'].includes(ext)) return 'video';
    if (['pdf'].includes(ext)) return 'pdf';
    if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) return 'audio';
    return 'file';
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function openPreview(message) {
    previewFile = message;
    showPreview = true;
  }

  function closePreview() {
    showPreview = false;
    previewFile = null;
  }

  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
      alert('File too large! Maximum size is 100MB');
      return;
    }
    
    try {
      uploadingFile = true;
      const formData = new FormData();
      formData.append('file', file);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/chat/upload-file`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) throw new Error('Upload failed');
      
      const { file_url, file_name } = await response.json();
      
      // Send message with file
      const message = await apiCall(`/chat/rooms/${selectedRoom.id}/messages`, {
        method: 'POST',
        body: JSON.stringify({
          message: file_name,
          message_type: 'file',
          file_url,
          file_name,
          reply_to_id: replyingTo?.id
        })
      });
      
      messages = [...messages, message];
      replyingTo = null;
      scrollToBottom();
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file');
    } finally {
      uploadingFile = false;
      if (fileInput) fileInput.value = '';
    }
  }

  async function reactToMessage(messageId, emoji) {
    try {
      await apiCall(`/chat/messages/${messageId}/react`, {
        method: 'POST',
        body: JSON.stringify({ emoji })
      });
      
      // Reload messages to get updated reactions
      await loadMessages(selectedRoom.id);
    } catch (error) {
      console.error('Error reacting to message:', error);
    }
  }

  function setReply(message) {
    replyingTo = message;
  }

  function cancelReply() {
    replyingTo = null;
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
          if (JSON.stringify(newMessages) !== JSON.stringify(messages)) {
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

  function canManageRoom(room) {
    return room.created_by === currentUser?.id;
  }

  async function deleteMessage(messageId) {
    if (!confirm('⚠️ Delete this message? This cannot be undone!')) return;
    
    try {
      await apiCall(`/chat/messages/${messageId}`, {
        method: 'DELETE'
      });
      
      messages = messages.filter(m => m.id !== messageId);
    } catch (error) {
      console.error('Error deleting message:', error);
      alert('❌ Failed to delete message.');
    }
  }

  async function deleteRoom(roomId) {
    if (!confirm('⚠️ Delete this chat room? All messages will be lost forever!')) {
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
      alert('✅ Chat room deleted!');
    } catch (error) {
      console.error('Error deleting room:', error);
      alert('❌ Failed to delete chat room.');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadRooms();
  });

  onDestroy(() => {
    if (messagePolling) clearInterval(messagePolling);
  });
</script>

<!-- Minimal Black & White Chat -->
<div class="fixed inset-0 {theme === 'light' ? 'bg-white/95' : 'bg-black/95'} flex items-center justify-center z-[50] p-4">
  <div class="{currentTheme.bg} w-full max-w-5xl h-[90vh] flex flex-col border-2 {currentTheme.border}">
    
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b-2 {currentTheme.border}">
      <div class="flex items-center space-x-3">
        <div class="text-2xl">💬</div>
        <div>
          <h2 class="text-xl font-bold {currentTheme.text}">Chat</h2>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <button
          on:click={cycleTheme}
          class="w-10 h-10 border-2 {currentTheme.border} flex items-center justify-center transition-all"
          title="Toggle theme"
        >
          {#if theme === 'dark'}
            <Moon size={20} class="{currentTheme.text}" />
          {:else}
            <Sun size={20} class="{currentTheme.text}" />
          {/if}
        </button>
        <button on:click={closeChat} class="w-10 h-10 border-2 {currentTheme.border} flex items-center justify-center transition-all">
          <X size={20} class="{currentTheme.text}" />
        </button>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar - Room List -->
      <div class="w-full sm:w-80 border-r-2 {currentTheme.border} {currentTheme.bg} flex flex-col">
        {#if currentUser?.role === 'admin' || currentUser?.role === 'teacher'}
          <div class="p-3 border-b-2 {currentTheme.border}">
            <button
              on:click={() => showCreateRoom = true}
              class="w-full {currentTheme.accent} {theme === 'light' ? 'text-white' : 'text-black'} px-4 py-3 transition-all font-semibold"
            >
              + Create Room
            </button>
          </div>
        {/if}

        <div class="flex-1 overflow-y-auto">
          {#if loading}
            <div class="p-4 text-center">
              <div class="inline-block w-8 h-8 border-4 {currentTheme.border} border-t-transparent animate-spin"></div>
              <p class="{currentTheme.text} mt-2 text-sm">Loading...</p>
            </div>
          {:else if rooms.length === 0}
            <div class="p-6 text-center">
              <div class="text-6xl mb-3">💬</div>
              <p class="{currentTheme.text} text-sm">No chat rooms</p>
            </div>
          {:else}
            {#each rooms as room}
              <button
                class="w-full text-left p-4 border-b {currentTheme.border} transition-all {selectedRoom?.id === room.id ? 'border-l-4' : ''}"
                on:click={() => selectRoom(room)}
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1 min-w-0">
                    <div class="font-semibold {currentTheme.text} text-sm truncate">{room.name}</div>
                    <div class="text-xs {theme === 'light' ? 'text-gray-600' : 'text-gray-400'} mt-1">{getRoomTypeDisplay(room.room_type)}</div>
                    {#if room.department && room.level}
                      <div class="text-xs {theme === 'light' ? 'text-gray-500' : 'text-gray-500'} mt-0.5">{room.department} - {room.level}</div>
                    {/if}
                  </div>
                </div>
              </button>
            {/each}
          {/if}
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col bg-gradient-to-br {currentTheme.bg} transition-all duration-500">
        {#if selectedRoom}
          <!-- Chat Header -->
          <div class="p-4 border-b {currentTheme.border} {currentTheme.card} backdrop-blur-sm transition-all duration-500">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-2xl shadow-lg">
                  {selectedRoom.room_type === 'student-student' ? '👥' : selectedRoom.room_type === 'student-teacher' ? '🎓' : selectedRoom.room_type === 'teacher-teacher' ? '👨🏫' : '🏛️'}
                </div>
                <div>
                  <h3 class="font-bold {currentTheme.text} text-lg">{selectedRoom.name}</h3>
                  <p class="text-sm {theme === 'light' ? 'text-gray-600' : 'text-gray-400'}">{getRoomTypeDisplay(selectedRoom.room_type)}</p>
                  {#if typingUsers.size > 0}
                    <p class="text-xs text-green-500 animate-pulse mt-1">
                      {Array.from(typingUsers).join(', ')} {typingUsers.size === 1 ? 'is' : 'are'} typing...
                    </p>
                  {/if}
                </div>
              </div>
              {#if canManageRoom(selectedRoom)}
                <button
                  on:click={() => deleteRoom(selectedRoom.id)}
                  class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 text-sm rounded-xl transition-all border border-red-500/30"
                  title="Delete Room"
                >
                  🗑️ Delete
                </button>
              {/if}
            </div>
          </div>

          <!-- Messages -->
          <div bind:this={messageContainer} class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar transition-all duration-500">
            {#each messages as message}
              <div class="flex {message.sender_id === currentUser?.id ? 'justify-end' : 'justify-start'} animate-slideUp">
                <div class="max-w-[75%] sm:max-w-md group">
                  <!-- Sender Info (for others' messages) -->
                  {#if message.sender_id !== currentUser?.id}
                    <div class="flex items-center space-x-2 mb-1 ml-2">
                      <div class="w-6 h-6 rounded-full bg-gradient-to-br {message.sender_role === 'admin' ? 'from-red-500 to-orange-500' : message.sender_role === 'teacher' ? 'from-green-500 to-blue-500' : 'from-purple-500 to-pink-500'} flex items-center justify-center text-xs">
                        {message.sender_name.charAt(0)}
                      </div>
                      <span class="text-xs font-medium {message.sender_role === 'admin' ? 'text-red-400' : message.sender_role === 'teacher' ? 'text-green-400' : 'text-purple-400'}">
                        {message.sender_name}
                      </span>
                    </div>
                  {/if}

                  <!-- Reply Preview -->
                  {#if message.reply_to}
                    <div class="ml-2 mb-1 p-2 bg-gray-800/50 border-l-2 border-purple-500 rounded-r-lg text-xs text-gray-400">
                      <div class="font-semibold text-purple-400">↩️ {message.reply_to.sender_name}</div>
                      <div class="truncate">{message.reply_to.message}</div>
                    </div>
                  {/if}

                  <!-- Message Bubble -->
                  <div class="relative {message.sender_id === currentUser?.id ? `bg-gradient-to-br ${currentTheme.accent} text-white rounded-3xl rounded-tr-md` : theme === 'light' ? 'bg-gray-100 text-gray-900 rounded-3xl rounded-tl-md' : 'bg-gray-800 text-gray-100 rounded-3xl rounded-tl-md'} px-4 py-3 shadow-lg transition-all duration-300">
                    {#if message.message_type === 'file'}
                      <div class="space-y-2">
                        {#if getFileType(message.file_name) === 'image'}
                          <div class="relative group cursor-pointer" on:click={() => openPreview(message)}>
                            <img src="{API_BASE}{message.file_url}" alt={message.file_name} class="max-w-full rounded-lg max-h-64 object-cover" />
                            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                              <Eye size={32} class="text-white" />
                            </div>
                          </div>
                        {:else if getFileType(message.file_name) === 'video'}
                          <video controls class="max-w-full rounded-lg max-h-64">
                            <source src="{API_BASE}{message.file_url}" />
                            Your browser doesn't support video.
                          </video>
                        {:else if getFileType(message.file_name) === 'audio'}
                          <audio controls class="w-full">
                            <source src="{API_BASE}{message.file_url}" />
                            Your browser doesn't support audio.
                          </audio>
                        {:else if getFileType(message.file_name) === 'pdf'}
                          <div class="bg-white/10 rounded-lg p-3 cursor-pointer hover:bg-white/20 transition-all" on:click={() => openPreview(message)}>
                            <div class="flex items-center space-x-3">
                              <FileText size={32} class="text-red-400" />
                              <div class="flex-1 min-w-0">
                                <div class="text-sm font-medium truncate">{message.file_name}</div>
                                <div class="text-xs opacity-70">Click to preview PDF</div>
                              </div>
                              <Eye size={20} />
                            </div>
                          </div>
                        {:else}
                          <div class="bg-white/10 rounded-lg p-3">
                            <div class="flex items-center space-x-3">
                              <span class="text-3xl">{getFileIcon(message.file_name)}</span>
                              <div class="flex-1 min-w-0">
                                <div class="text-sm font-medium truncate">{message.file_name}</div>
                              </div>
                            </div>
                          </div>
                        {/if}
                        
                        <a href="{API_BASE}{message.file_url}" download={message.file_name} class="flex items-center space-x-2 text-xs opacity-70 hover:opacity-100 transition-opacity">
                          <Download size={14} />
                          <span>Download</span>
                        </a>
                      </div>
                    {:else}
                      <div class="text-sm break-words">{@html message.message}</div>
                    {/if}
                    
                    <div class="flex items-center justify-between mt-1 space-x-2">
                      <div class="text-xs opacity-70">
                        {new Date(message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </div>
                      
                      <!-- Quick Reactions & Admin Controls -->
                      <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {#each quickEmojis.slice(0, 4) as emoji}
                          <button
                            on:click={() => reactToMessage(message.id, emoji)}
                            class="hover:scale-125 transition-transform text-sm"
                            title="React with {emoji}"
                          >
                            {emoji}
                          </button>
                        {/each}
                        <button
                          on:click={() => setReply(message)}
                          class="text-xs px-2 py-0.5 bg-white/10 hover:bg-white/20 rounded-full transition-all"
                          title="Reply"
                        >
                          ↩️
                        </button>
                        {#if currentUser?.role === 'admin'}
                          <button
                            on:click={() => deleteMessage(message.id)}
                            class="text-xs px-2 py-0.5 bg-red-500/20 hover:bg-red-500/40 rounded-full transition-all text-red-400"
                            title="Delete (Admin)"
                          >
                            🗑️
                          </button>
                        {/if}
                      </div>
                    </div>

                    <!-- Reactions Display -->
                    {#if message.reactions && Object.keys(message.reactions).length > 0}
                      <div class="flex flex-wrap gap-1 mt-2">
                        {#each Object.entries(message.reactions) as [emoji, data]}
                          <button
                            on:click={() => reactToMessage(message.id, emoji)}
                            class="px-2 py-1 bg-white/10 hover:bg-white/20 rounded-full text-xs flex items-center space-x-1 transition-all {data.user_reacted ? 'ring-2 ring-yellow-400' : ''}"
                            title="{data.users.join(', ')}"
                          >
                            <span>{emoji}</span>
                            <span class="font-semibold">{data.count}</span>
                          </button>
                        {/each}
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>

          <!-- Reply Preview Bar -->
          {#if replyingTo}
            <div class="px-4 py-2 bg-purple-900/30 border-t border-purple-500/30 flex items-center justify-between">
              <div class="flex items-center space-x-2 flex-1 min-w-0">
                <span class="text-purple-400">↩️</span>
                <div class="flex-1 min-w-0">
                  <div class="text-xs text-purple-400 font-semibold">Replying to {replyingTo.sender_name}</div>
                  <div class="text-xs text-gray-400 truncate">{replyingTo.message}</div>
                </div>
              </div>
              <button on:click={cancelReply} class="text-gray-400 hover:text-white ml-2">✕</button>
            </div>
          {/if}

          <!-- Message Input -->
          <div class="p-4 border-t {currentTheme.border} {currentTheme.card} backdrop-blur-sm transition-all duration-500">
            <div class="flex items-end space-x-2">
              <!-- File Upload -->
              <input
                type="file"
                bind:this={fileInput}
                on:change={handleFileUpload}
                class="hidden"
                accept="*"
              />
              <button
                on:click={() => fileInput.click()}
                disabled={uploadingFile}
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 rounded-xl flex items-center justify-center transition-all transform hover:scale-110 disabled:opacity-50 shadow-lg"
                title="Upload file"
              >
                {#if uploadingFile}
                  <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {:else}
                  <span class="text-xl">📎</span>
                {/if}
              </button>

              <!-- Formatting Button -->
              <button
                on:click={() => showFormatting = !showFormatting}
                class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-xl flex items-center justify-center transition-all transform hover:scale-110 shadow-lg"
                title="Format text"
              >
                <span class="text-xl font-bold">A</span>
              </button>

              <!-- Emoji Picker Button -->
              <button
                on:click={() => { showEmojiPicker = !showEmojiPicker; showFormatting = false; }}
                class="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 rounded-xl flex items-center justify-center transition-all transform hover:scale-110 shadow-lg"
                title="Add emoji"
              >
                <span class="text-xl">😊</span>
              </button>

              <!-- Message Input -->
              <div class="flex-1 relative">
                <textarea
                  bind:value={newMessage}
                  on:keypress={handleKeyPress}
                  on:input={handleTyping}
                  placeholder="Type your vibe... 💭"
                  class="w-full {theme === 'light' ? 'bg-white text-gray-900 border-gray-300' : 'bg-gray-800 text-white border-gray-700'} border-2 focus:border-purple-500 rounded-2xl px-4 py-3 resize-none focus:outline-none transition-all {theme === 'light' ? 'placeholder-gray-400' : 'placeholder-gray-500'}"
                  rows="1"
                  style="max-height: 120px;"
                ></textarea>
              </div>

              <!-- Send Button -->
              <button
                on:click={sendMessage}
                disabled={!newMessage.trim()}
                class="w-12 h-12 bg-gradient-to-br {currentTheme.accent} hover:opacity-90 rounded-xl flex items-center justify-center transition-all transform hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                <Send size={20} class="text-white" />
              </button>
            </div>

            <!-- Formatting Toolbar -->
            {#if showFormatting}
              <div class="mt-2 p-3 {theme === 'light' ? 'bg-white border-gray-300' : 'bg-gray-800 border-purple-500/30'} rounded-2xl border-2 transition-all duration-300">
                <div class="space-y-3">
                  <!-- Text Style -->
                  <div class="flex items-center space-x-2">
                    <button
                      on:click={() => textFormat.bold = !textFormat.bold}
                      class="px-3 py-2 rounded-lg font-bold transition-all {textFormat.bold ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}"
                      title="Bold"
                    >
                      B
                    </button>
                    <button
                      on:click={() => textFormat.italic = !textFormat.italic}
                      class="px-3 py-2 rounded-lg italic transition-all {textFormat.italic ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}"
                      title="Italic"
                    >
                      I
                    </button>
                    <button
                      on:click={() => textFormat.underline = !textFormat.underline}
                      class="px-3 py-2 rounded-lg underline transition-all {textFormat.underline ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}"
                      title="Underline"
                    >
                      U
                    </button>
                  </div>
                  
                  <!-- Font Size -->
                  <div class="flex items-center space-x-2">
                    <span class="text-xs {currentTheme.text} font-semibold">Size:</span>
                    <button on:click={() => textFormat.size = 'small'} class="px-2 py-1 text-xs rounded-lg transition-all {textFormat.size === 'small' ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}">Small</button>
                    <button on:click={() => textFormat.size = 'normal'} class="px-2 py-1 text-sm rounded-lg transition-all {textFormat.size === 'normal' ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}">Normal</button>
                    <button on:click={() => textFormat.size = 'large'} class="px-2 py-1 text-base rounded-lg transition-all {textFormat.size === 'large' ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}">Large</button>
                    <button on:click={() => textFormat.size = 'xlarge'} class="px-2 py-1 text-lg rounded-lg transition-all {textFormat.size === 'xlarge' ? 'bg-purple-500 text-white' : theme === 'light' ? 'bg-gray-200 text-gray-900' : 'bg-gray-700 text-white'}">XL</button>
                  </div>
                  
                  <!-- Colors -->
                  <div class="flex items-center space-x-2">
                    <span class="text-xs {currentTheme.text} font-semibold">Color:</span>
                    <button on:click={() => textFormat.color = 'default'} class="w-8 h-8 rounded-full border-2 transition-all {textFormat.color === 'default' ? 'ring-2 ring-purple-500' : ''} {theme === 'light' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-300'}"></button>
                    <button on:click={() => textFormat.color = '#ef4444'} class="w-8 h-8 rounded-full bg-red-500 border-2 border-red-600 transition-all {textFormat.color === '#ef4444' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#f97316'} class="w-8 h-8 rounded-full bg-orange-500 border-2 border-orange-600 transition-all {textFormat.color === '#f97316' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#eab308'} class="w-8 h-8 rounded-full bg-yellow-500 border-2 border-yellow-600 transition-all {textFormat.color === '#eab308' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#22c55e'} class="w-8 h-8 rounded-full bg-green-500 border-2 border-green-600 transition-all {textFormat.color === '#22c55e' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#3b82f6'} class="w-8 h-8 rounded-full bg-blue-500 border-2 border-blue-600 transition-all {textFormat.color === '#3b82f6' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#a855f7'} class="w-8 h-8 rounded-full bg-purple-500 border-2 border-purple-600 transition-all {textFormat.color === '#a855f7' ? 'ring-2 ring-purple-500' : ''}"></button>
                    <button on:click={() => textFormat.color = '#ec4899'} class="w-8 h-8 rounded-full bg-pink-500 border-2 border-pink-600 transition-all {textFormat.color === '#ec4899' ? 'ring-2 ring-purple-500' : ''}"></button>
                  </div>
                  
                  <!-- Reset Button -->
                  <button
                    on:click={resetFormatting}
                    class="w-full px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm transition-all"
                  >
                    🔄 Reset Formatting
                  </button>
                </div>
              </div>
            {/if}

            <!-- Emoji Picker -->
            {#if showEmojiPicker}
              <div class="mt-2 p-3 {theme === 'light' ? 'bg-white border-gray-300' : 'bg-gray-800 border-purple-500/30'} rounded-2xl border-2 max-h-48 overflow-y-auto custom-scrollbar transition-all duration-300">
                <div class="grid grid-cols-8 sm:grid-cols-10 gap-1">
                  {#each allEmojis as emoji}
                    <button
                      on:click={() => {
                        newMessage += emoji;
                        showEmojiPicker = false;
                      }}
                      class="text-2xl hover:scale-125 transition-transform p-1"
                    >
                      {emoji}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <div class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <div class="text-8xl mb-4 animate-bounce">💬</div>
              <p class="text-gray-400 text-lg font-semibold">Select a vibe to start chatting</p>
              <p class="text-gray-500 text-sm mt-2">Choose a room from the sidebar 👈</p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<!-- Create Room Modal -->
{#if showCreateRoom}
  <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-fadeIn">
    <div class="bg-gradient-to-br {currentTheme.bg} rounded-3xl shadow-2xl w-full max-w-lg p-6 border-2 {currentTheme.border} animate-slideUp transition-all duration-500">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-2xl font-bold {currentTheme.text}">✨ Create New Vibe</h3>
        <button on:click={() => showCreateRoom = false} class="{theme === 'light' ? 'text-gray-600 hover:text-gray-900' : 'text-gray-400 hover:text-white'} text-3xl transition-all hover:rotate-90 duration-300">&times;</button>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-purple-400 mb-2">📝 Room Name</label>
          <input
            bind:value={newRoomData.name}
            type="text"
            placeholder="e.g., Level 5 BDC Squad 🔥"
            class="w-full bg-gray-800 text-white border-2 border-gray-700 focus:border-purple-500 rounded-xl px-4 py-3 focus:outline-none transition-all placeholder-gray-500"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-purple-400 mb-2">🏷️ Room Type</label>
          <select bind:value={newRoomData.room_type} class="w-full bg-gray-800 text-white border-2 border-gray-700 focus:border-purple-500 rounded-xl px-4 py-3 focus:outline-none transition-all">
            {#each getRoomTypeOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        {#if newRoomData.room_type.includes('student')}
          <div class="bg-purple-900/20 border-2 border-purple-500/30 rounded-xl p-4 space-y-3">
            <div>
              <label class="block text-sm font-semibold text-purple-400 mb-2">🏗️ Trade / Department</label>
              <select
                bind:value={newRoomData.department}
                class="w-full bg-gray-800 text-white border-2 border-gray-700 focus:border-purple-500 rounded-xl px-4 py-3 focus:outline-none transition-all"
              >
                <option value="">-- Select --</option>
                {#each availableDepartments as dept}
                  <option value={dept}>{dept}</option>
                {/each}
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-purple-400 mb-2">📊 Level</label>
              <select
                bind:value={newRoomData.level}
                class="w-full bg-gray-800 text-white border-2 border-gray-700 focus:border-purple-500 rounded-xl px-4 py-3 focus:outline-none transition-all"
              >
                <option value="">-- Select --</option>
                {#each availableLevels as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>
          </div>
        {/if}
      </div>

      <div class="flex justify-end space-x-3 mt-6">
        <button
          on:click={() => showCreateRoom = false}
          class="px-6 py-3 text-gray-400 hover:text-white border-2 border-gray-700 hover:border-gray-600 rounded-xl transition-all font-semibold"
        >
          Cancel
        </button>
        <button
          on:click={createRoom}
          disabled={!newRoomData.name.trim() || loading}
          class="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg transform hover:scale-105"
        >
          {loading ? '⏳ Creating...' : '✨ Create Vibe'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(31, 41, 55, 0.5);
    border-radius: 10px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, #a855f7, #ec4899);
    border-radius: 10px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(to bottom, #9333ea, #db2777);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }

  .animate-slideUp {
    animation: slideUp 0.3s ease-out;
  }
</style>

<!-- File Preview Modal -->
{#if showPreview && previewFile}
  <div class="fixed inset-0 bg-black/95 backdrop-blur-sm flex items-center justify-center z-[70] p-4 animate-fadeIn" on:click={closePreview}>
    <div class="relative w-full max-w-5xl max-h-[90vh] flex flex-col" on:click|stopPropagation>
      <!-- Header -->
      <div class="flex items-center justify-between p-4 bg-gray-900/90 rounded-t-2xl">
        <div class="flex items-center space-x-3">
          <span class="text-2xl">{getFileIcon(previewFile.file_name)}</span>
          <div>
            <h3 class="text-white font-semibold">{previewFile.file_name}</h3>
            <p class="text-gray-400 text-sm">Sent by {previewFile.sender_name}</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <a href="{API_BASE}{previewFile.file_url}" download={previewFile.file_name} class="p-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-all" title="Download">
            <Download size={20} class="text-white" />
          </a>
          <button on:click={closePreview} class="p-2 bg-red-500 hover:bg-red-600 rounded-lg transition-all" title="Close">
            <X size={20} class="text-white" />
          </button>
        </div>
      </div>
      
      <!-- Preview Content -->
      <div class="flex-1 overflow-auto bg-gray-900/90 rounded-b-2xl p-4">
        {#if getFileType(previewFile.file_name) === 'image'}
          <img src="{API_BASE}{previewFile.file_url}" alt={previewFile.file_name} class="max-w-full max-h-full mx-auto rounded-lg" />
        {:else if getFileType(previewFile.file_name) === 'video'}
          <video controls class="max-w-full max-h-full mx-auto rounded-lg">
            <source src="{API_BASE}{previewFile.file_url}" />
            Your browser doesn't support video.
          </video>
        {:else if getFileType(previewFile.file_name) === 'pdf'}
          <iframe src="{API_BASE}{previewFile.file_url}" class="w-full h-full min-h-[600px] rounded-lg bg-white" title="PDF Preview"></iframe>
        {:else if getFileType(previewFile.file_name) === 'audio'}
          <div class="flex items-center justify-center h-full">
            <div class="text-center">
              <div class="text-6xl mb-4">🎵</div>
              <audio controls class="mx-auto">
                <source src="{API_BASE}{previewFile.file_url}" />
                Your browser doesn't support audio.
              </audio>
            </div>
          </div>
        {:else}
          <div class="flex items-center justify-center h-full">
            <div class="text-center">
              <div class="text-6xl mb-4">{getFileIcon(previewFile.file_name)}</div>
              <p class="text-white text-lg mb-2">{previewFile.file_name}</p>
              <p class="text-gray-400 mb-4">Preview not available for this file type</p>
              <a href="{API_BASE}{previewFile.file_url}" download={previewFile.file_name} class="inline-flex items-center space-x-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all">
                <Download size={20} />
                <span>Download File</span>
              </a>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
