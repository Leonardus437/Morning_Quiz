# Teacher Portal Modernization - Complete Guide

## The teacher page is 126KB and very complex. Here's how to modernize it:

### Step 1: Update the Login Section
Find the login form section and replace with:

```svelte
<div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
  <div class="w-full max-w-md">
    <div class="bg-white shadow-xl overflow-hidden">
      <div class="teacher-gradient p-8 text-center">
        <div class="w-16 h-16 bg-white/20 backdrop-blur-sm mx-auto mb-4 flex items-center justify-center text-3xl font-black text-white">
          T
        </div>
        <h1 class="text-3xl font-black text-white mb-2 uppercase tracking-wide">Teacher Portal</h1>
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
            <input class="input" type="text" bind:value={username} placeholder="Enter username" disabled={loading} />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Password</label>
            <input class="input" type="password" bind:value={password} placeholder="Enter password" disabled={loading} />
          </div>

          <button class="btn btn-teacher w-full py-4" type="submit" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div class="mt-6 pt-6 border-t border-gray-200 text-center">
          <a href="/" class="text-blue-600 hover:text-blue-800 font-semibold text-sm">← Back to Student Portal</a>
        </div>
      </div>
    </div>
  </div>
</div>
```

### Step 2: Update the Header
Find the header section and replace with:

```svelte
<header class="bg-white shadow-md border-b-2 border-blue-600 sticky top-0 z-40">
  <div class="max-w-7xl mx-auto px-6 py-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-blue-600 flex items-center justify-center text-white font-black text-xl shadow-lg">
          T
        </div>
        <div>
          <h1 class="text-xl font-black text-gray-900 uppercase tracking-wide">Teacher Dashboard</h1>
          <p class="text-sm text-gray-600 font-medium">{$user.full_name || $user.username}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button class="btn btn-teacher text-xs px-4 py-2" on:click={loadData} disabled={loading}>
          {loading ? '↻' : 'Refresh'}
        </button>
        <button class="btn bg-gray-600 hover:bg-gray-700 text-white text-xs px-4 py-2" on:click={handleLogout}>
          Sign Out
        </button>
      </div>
    </div>
  </div>
</header>
```

### Step 3: Update Navigation Tabs
Find the navigation tabs section and replace with:

```svelte
<div class="bg-white shadow-sm border-b border-gray-200 sticky top-[73px] z-30">
  <div class="max-w-7xl mx-auto px-6">
    <div class="flex space-x-1 overflow-x-auto">
      <button class="nav-tab {activeTab === 'dashboard' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'dashboard'}>
        Dashboard
      </button>
      <button class="nav-tab {activeTab === 'notifications' ? 'nav-tab-active' : 'nav-tab-inactive'}" on:click={() => activeTab = 'notifications'}>
        Notifications
        {#if unreadCount > 0}
          <span class="ml-2 bg-red-600 text-white text-xs px-2 py-0.5 rounded-full font-bold">{unreadCount}</span>
        {/if}
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

### Step 4: Update Dashboard Stats
Find the dashboard stats cards and replace with:

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

### Step 5: Update All Cards
Find all instances of cards and update classes:
- Replace `class="bg-white rounded-xl shadow-sm border border-gray-100 p-6"` 
- With `class="card-teacher p-6"`

### Step 6: Update All Buttons
- Primary actions: `class="btn btn-teacher"`
- Secondary actions: `class="btn bg-gray-600 hover:bg-gray-700 text-white"`
- Danger actions: `class="btn bg-red-600 hover:bg-red-700 text-white"`
- Success actions: `class="btn bg-green-600 hover:bg-green-700 text-white"`

### Step 7: Update Forms
Replace all input fields with:
```svelte
<div>
  <label class="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Label</label>
  <input class="input" type="text" placeholder="Enter value" />
</div>
```

### Step 8: Update Tables
Replace table classes with:
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
        <button class="text-blue-600 hover:text-blue-800 font-semibold text-sm uppercase tracking-wide">
          Edit
        </button>
      </td>
    </tr>
  </tbody>
</table>
```

## Quick Find & Replace Commands

Use your text editor's find & replace:

1. `class="bg-white rounded-xl shadow-sm border border-gray-100 p-6"` → `class="card-teacher p-6"`
2. `class="bg-green-600 text-white` → `class="btn btn-teacher`
3. `class="text-2xl font-bold` → `class="text-2xl font-black uppercase tracking-wide`
4. `class="text-gray-600 text-sm"` → `class="text-xs font-bold text-gray-600 uppercase tracking-wide"`

## Result
After applying these changes, your teacher portal will have:
- ✅ Clean, professional French institutional design
- ✅ Modern typography with Montserrat headings
- ✅ Professional blue color scheme
- ✅ Consistent spacing and layout
- ✅ Modern stat cards with icons
- ✅ Clean navigation tabs
- ✅ Professional forms and tables

All CSS classes are already in `app.css` - just apply the HTML changes!
