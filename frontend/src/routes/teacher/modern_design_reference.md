# Modern Teacher Portal Design Reference

## Apply these changes to +page.svelte

### 1. LOGIN SECTION (Replace existing login UI)
```svelte
<!-- Modern Login -->
<div class="min-h-screen bg-gray-50 flex items-center justify-center">
  <div class="max-w-md w-full">
    <div class="bg-white shadow-xl overflow-hidden">
      <div class="teacher-gradient p-8 text-center">
        <h1 class="text-3xl font-black text-white mb-2">TEACHER PORTAL</h1>
        <p class="text-blue-100">Professional Dashboard Access</p>
      </div>
      
      <div class="p-8">
        {#if error}
          <div class="bg-red-50 border-l-4 border-red-600 p-4 mb-6">
            <p class="text-red-800 font-semibold text-sm">{error}</p>
          </div>
        {/if}

        <form on:submit|preventDefault={handleLogin} class="space-y-6">
          <div>
            <label class="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Username</label>
            <input class="input" type="text" bind:value={username} placeholder="Enter username" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Password</label>
            <input class="input" type="password" bind:value={password} placeholder="Enter password" />
          </div>

          <button class="btn btn-teacher w-full py-4" type="submit" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  </div>
</div>
```

### 2. HEADER (Replace existing header)
```svelte
<header class="bg-white shadow-md border-b-2 border-blue-600">
  <div class="max-w-7xl mx-auto px-6 py-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-blue-600 flex items-center justify-center text-white font-black text-xl">T</div>
        <div>
          <h1 class="text-xl font-black text-gray-900">TEACHER DASHBOARD</h1>
          <p class="text-sm text-gray-600">{$user.full_name || $user.username}</p>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button class="btn btn-teacher text-xs px-4 py-2" on:click={loadData}>
          Refresh
        </button>
        <button class="btn bg-gray-600 hover:bg-gray-700 text-white text-xs px-4 py-2" on:click={handleLogout}>
          Sign Out
        </button>
      </div>
    </div>
  </div>
</header>
```

### 3. NAVIGATION TABS (Replace existing tabs)
```svelte
<div class="bg-white shadow-sm border-b border-gray-200 mb-8">
  <div class="max-w-7xl mx-auto px-6">
    <div class="flex space-x-1 overflow-x-auto">
      <button class="nav-tab {activeTab === 'dashboard' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'dashboard'}>
        Dashboard
      </button>
      <button class="nav-tab {activeTab === 'notifications' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'notifications'}>
        Notifications {#if unreadCount > 0}<span class="ml-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full">{unreadCount}</span>{/if}
      </button>
      <button class="nav-tab {activeTab === 'create-question' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'create-question'}>
        Questions
      </button>
      <button class="nav-tab {activeTab === 'create-quiz' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'create-quiz'}>
        Create Quiz
      </button>
      <button class="nav-tab {activeTab === 'quizzes' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'quizzes'}>
        My Quizzes
      </button>
      <button class="nav-tab {activeTab === 'courses' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => { activeTab = 'courses'; loadMyCourses(); }}>
        Courses
      </button>
      <button class="nav-tab {activeTab === 'students' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'students'}>
        Students
      </button>
    </div>
  </div>
</div>
```

### 4. DASHBOARD STATS (Replace existing stats)
```svelte
<div class="grid md:grid-cols-4 gap-6 mb-8">
  <div class="stat-card border-blue-600">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-1">Questions</p>
        <p class="text-3xl font-black text-blue-600">{questions.filter(q => q.created_by === $user?.id).length}</p>
      </div>
      <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
        <span class="text-2xl">📝</span>
      </div>
    </div>
  </div>
  
  <div class="stat-card border-green-600">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-1">Quizzes</p>
        <p class="text-3xl font-black text-green-600">{quizzes.filter(q => q.created_by === $user?.id).length}</p>
      </div>
      <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
        <span class="text-2xl">🎯</span>
      </div>
    </div>
  </div>
  
  <div class="stat-card border-purple-600">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-1">Courses</p>
        <p class="text-3xl font-black text-purple-600">{myCourses.length}</p>
      </div>
      <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
        <span class="text-2xl">📚</span>
      </div>
    </div>
  </div>
  
  <div class="stat-card border-orange-600">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-1">Students</p>
        <p class="text-3xl font-black text-orange-600">{myClasses.length}</p>
      </div>
      <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
        <span class="text-2xl">👥</span>
      </div>
    </div>
  </div>
</div>
```

### 5. CARDS (Replace card styling)
```svelte
<div class="card-teacher p-6">
  <h2 class="text-xl font-black text-gray-900 mb-4 uppercase tracking-wide">Section Title</h2>
  <!-- Content -->
</div>
```

### 6. BUTTONS (Update button classes)
- Primary actions: `btn btn-teacher`
- Secondary actions: `btn bg-gray-600 hover:bg-gray-700 text-white`
- Danger actions: `btn bg-red-600 hover:bg-red-700 text-white`

### 7. FORMS (Update input styling)
```svelte
<div class="space-y-4">
  <div>
    <label class="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Label</label>
    <input class="input" type="text" placeholder="Enter value" />
  </div>
</div>
```

### 8. TABLES (Update table styling)
```svelte
<table class="table-modern">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
      <td>
        <button class="text-blue-600 hover:text-blue-800 font-semibold text-sm">Edit</button>
      </td>
    </tr>
  </tbody>
</table>
```

## Color Scheme
- Primary Blue: #0066CC
- Dark Blue: #003D7A
- Success Green: #00A651
- Warning Orange: #FF9900
- Danger Red: #CC0000
- Gray Background: #F5F5F5

## Typography
- All headings: UPPERCASE, Bold, Tracking-wide
- Labels: Uppercase, Small, Bold
- Body text: Regular weight, Gray-900

## Spacing
- Section padding: p-6 or p-8
- Card gaps: gap-6
- Form spacing: space-y-4 or space-y-6
