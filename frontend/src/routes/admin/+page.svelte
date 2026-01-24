<script>
  import { onMount } from 'svelte';
  import AnimatedBackground from '$lib/components/AnimatedBackground.svelte';
  import ClassTeacherManager from '$lib/ClassTeacherManager.svelte';
  import { api } from '$lib/api.js';
  
  let username = '';
  let password = '';
  let loading = false;
  let error = '';
  let success = '';
  let isLoggedIn = false;
  let user = null;
  let activeTab = 'overview';
  
  // Data
  let lessons = [];
  let teachers = [];
  let students = [];
  let teacherLessons = [];
  let selectedTeacher = null;
  let selectedDepartment = '';
  let filteredLessons = [];
  
  // Student management
  let studentFilter = {
    department: '',
    level: ''
  };
  
  $: filteredStudents = students.filter(student => {
    if (studentFilter.department && student.department !== studentFilter.department) return false;
    if (studentFilter.level && student.level !== studentFilter.level) return false;
    return true;
  });
  

  
  // Forms
  let newLesson = {
    title: '',
    code: '',
    description: '',
    department: '',
    level: '',
    classification: 'Core'
  };
  
  let newTeacher = {
    username: '',
    password: '',
    full_name: '',
    departments: []
  };
  
  const departments = [
    'Land Surveying',
    'Software Development',
    'Computer System and Architecture',
    'Building Construction'
  ];
  
  // Map full department names to short codes used in database
  function getDepartmentCode(fullName) {
    const mapping = {
      'Software Development': 'SWD',
      'Computer System and Architecture': 'CSA',
      'Land Surveying': 'LSV',
      'Building Construction': 'BDC'
    };
    return mapping[fullName] || fullName;
  }
  
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  const classifications = ['Core', 'Specific', 'General'];
  
  onMount(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        if (userData.role === 'admin') {
          user = userData;
          isLoggedIn = true;
          api.setToken(storedToken);
          loadData();
        }
      } catch (e) {
        console.error('Auth error:', e);
      }
    }
  });

  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password';
      return;
    }

    loading = true;
    error = '';

    try {
      const result = await api.login(username, password);
      
      if (result.user.role !== 'admin') {
        throw new Error('DOS access required');
      }
      
      user = result.user;
      isLoggedIn = true;
      
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      api.setToken(result.access_token);
      
      await loadData();
      
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function handleLogout() {
    api.logout();
    isLoggedIn = false;
    user = null;
  }
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      console.log(' Loading admin data...');
      
      // Load data sequentially to better handle errors
      try {
        lessons = await api.getLessons();
        console.log(' Lessons loaded:', lessons.length);
      } catch (err) {
        console.error(' Failed to load lessons:', err);
        lessons = [];
      }
      
      try {
        teachers = await api.getTeachers();
        console.log(' Teachers loaded:', teachers.length);
      } catch (err) {
        console.error(' Failed to load teachers:', err);
        teachers = [];
      }
      
      try {
        students = await api.getStudents();
        console.log(' Students loaded:', students.length);
      } catch (err) {
        console.error(' Failed to load students:', err);
        students = [];
      }
      
      console.log(' Admin data loading complete');
      
    } catch (err) {
      console.error(' Load data error:', err);
      error = 'Failed to load some data. Please refresh the page.';
    } finally {
      loading = false;
    }
  }
  
  async function createLesson() {
    if (!newLesson.title || !newLesson.department || !newLesson.level) {
      error = 'Please fill all required fields: Title, Department, and Level';
      return;
    }
    
    if (!newLesson.code) {
      error = 'Lesson code is required';
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      console.log(' Creating lesson:', newLesson);
      
      const result = await api.createLesson(newLesson);
      
      console.log(' Lesson created:', result);
      
      // Reset form
      newLesson = {
        title: '',
        code: '',
        description: '',
        department: '',
        level: '',
        classification: 'Core'
      };
      
      // Reload lessons data
      await loadData();
      
      success = 'Lesson created successfully!';
      setTimeout(() => success = '', 3000);
      
    } catch (err) {
      console.error(' Create lesson error:', err);
      error = err.message || 'Failed to create lesson';
    } finally {
      loading = false;
    }
  }
  
  async function registerTeacher() {
    if (!newTeacher.username || !newTeacher.password || !newTeacher.full_name) {
      error = 'Please fill all required fields: Username, Password, and Full Name';
      return;
    }
    
    if (newTeacher.departments.length === 0) {
      error = 'Please select at least one department for the teacher';
      return;
    }
    
    if (newTeacher.username.length < 3) {
      error = 'Username must be at least 3 characters long';
      return;
    }
    
    if (newTeacher.password.length < 6) {
      error = 'Password must be at least 6 characters long';
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      console.log(' Registering teacher:', {
        username: newTeacher.username,
        full_name: newTeacher.full_name,
        departments: newTeacher.departments
      });
      
      const result = await api.registerTeacher(
        newTeacher.username,
        newTeacher.password,
        newTeacher.full_name,
        newTeacher.departments
      );
      
      console.log(' Teacher registered:', result);
      
      // Show success message immediately
      success = `✅ Teacher "${newTeacher.full_name}" registered successfully!\nUsername: ${newTeacher.username}`;
      
      // Reset form
      newTeacher = {
        username: '',
        password: '',
        full_name: '',
        departments: []
      };
      
      // Reload teachers data in background
      loadData().catch(err => console.error('Background reload failed:', err));
      
      setTimeout(() => success = '', 5000);
      
    } catch (err) {
      console.error(' Register teacher error:', err);
      error = err.message || 'Failed to register teacher';
    } finally {
      loading = false;
    }
  }
  
  async function selectTeacher(teacher) {
    selectedTeacher = teacher;
    selectedDepartment = '';
    filteredLessons = [];
    await loadTeacherLessons(teacher.id);
  }
  
  async function loadTeacherLessons(teacherId) {
    try {
      const result = await api.getTeacherLessons(teacherId);
      teacherLessons = result || [];
    } catch (err) {
      console.error('Failed to load teacher lessons:', err);
      teacherLessons = [];
    }
  }
  
  function filterLessonsByDepartment() {
    if (!selectedDepartment) {
      filteredLessons = [];
      return;
    }
    filteredLessons = lessons.filter(l => 
      l.department === selectedDepartment && 
      !teacherLessons.some(tl => tl.lesson.id === l.id)
    );
  }
  
  async function assignLessonToTeacher(teacherId, lessonId) {
    try {
      loading = true;
      error = '';
      
      console.log(' Assigning lesson to teacher:', { teacherId, lessonId });
      
      const result = await api.assignLessonToTeacher(teacherId, lessonId);
      
      console.log(' Lesson assigned:', result);
      
      // Show success immediately
      success = '✅ Lesson assigned successfully! Teacher will receive a notification.';
      setTimeout(() => success = '', 5000);
      
      // Reload teacher lessons in background
      loadTeacherLessons(teacherId).then(() => {
        filterLessonsByDepartment();
      }).catch(err => console.error('Failed to reload:', err));
      
    } catch (err) {
      console.error(' Assign lesson error:', err);
      error = err.message || 'Failed to assign lesson';
    } finally {
      loading = false;
    }
  }
  
  async function removeTeacherLesson(assignmentId) {
    if (!confirm('Are you sure you want to remove this lesson assignment?')) return;
    
    try {
      loading = true;
      error = '';
      
      console.log(' Removing lesson assignment:', assignmentId);
      
      const result = await api.removeTeacherLesson(assignmentId);
      
      console.log(' Assignment removed:', result);
      
      // Reload teacher lessons
      if (selectedTeacher) {
        await loadTeacherLessons(selectedTeacher.id);
        filterLessonsByDepartment();
      }
      
      success = 'Assignment removed successfully!';
      setTimeout(() => success = '', 3000);
      
    } catch (err) {
      console.error(' Remove assignment error:', err);
      error = err.message || 'Failed to remove assignment';
    } finally {
      loading = false;
    }
  }
  
  function toggleTeacherDepartment(department) {
    const index = newTeacher.departments.indexOf(department);
    if (index > -1) {
      newTeacher.departments = newTeacher.departments.filter(d => d !== department);
    } else {
      newTeacher.departments = [...newTeacher.departments, department];
    }
  }
  
  // Student upload and credentials variables
  let showStudentUpload = false;
  let showCredentialsModal = false;
  let uploadFile = null;
  let uploadedStudents = [];
  let uploadSelectedDepartment = '';
  let uploadSelectedLevel = '';
  let isProcessingFile = false;
  let fileUploadError = '';
  
  // File upload handling
  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check file type - Only Excel and PDF supported
    const allowedTypes = ['.pdf', '.xlsx', '.xls'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      fileUploadError = ` Only Excel (.xlsx, .xls) and PDF (.pdf) files are supported`;
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      fileUploadError = 'File size must be less than 10MB';
      return;
    }
    
    uploadFile = file;
    fileUploadError = '';
    processStudentFile();
  }
  
  async function processStudentFile() {
    if (!uploadFile) return;
    
    try {
      isProcessingFile = true;
      fileUploadError = '';
      
      console.log(' Processing file:', uploadFile.name, 'Size:', uploadFile.size);
      
      // Validate department and level are selected
      if (!uploadSelectedDepartment || !uploadSelectedLevel) {
        fileUploadError = ' Please select both Department and Level before uploading';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('department', uploadSelectedDepartment);
      formData.append('level', uploadSelectedLevel);
      
      console.log(' Upload parameters:', {
        department: uploadSelectedDepartment,
        level: uploadSelectedLevel,
        fileName: uploadFile.name,
        fileSize: uploadFile.size,
        fileType: uploadFile.type
      });
      
      // Call backend to process the file (supports both Excel and PDF)
      const endpoint = '/admin/upload-students-excel';
      const url = `${api.API_BASE || 'http://localhost:8000'}${endpoint}`;
      
      console.log(' Sending request to:', url);
      console.log(' Token:', api.token ? 'Present' : 'Missing');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${api.token || localStorage.getItem('token')}`
        },
        body: formData
      });
      
      console.log(' Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        let errorMessage = 'File processing failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log(' Upload result:', result);
      
      // Clear browser cache to show fresh data
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
      }
      
      // Handle successful upload response
      if (result.success) {
        let successMsg = ` ${result.message}\n\n`;
        successMsg += ` Statistics:\n`;
        successMsg += ` Total Students: ${result.total || 0}\n`;
        successMsg += ` New Students: ${result.created || 0}\n`;
        successMsg += ` Updated Students: ${result.updated || 0}\n`;
        successMsg += ` Department: ${uploadSelectedDepartment}\n`;
        successMsg += ` Level: ${uploadSelectedLevel}\n`;
        successMsg += ` File Type: ${uploadFile.name.split('.').pop().toUpperCase()}`;
        
        success = successMsg;
        setTimeout(() => success = '', 10000);
        
        // Close modal and reload data
        showStudentUpload = false;
        uploadFile = null;
        uploadedStudents = [];
        uploadSelectedDepartment = '';
        uploadSelectedLevel = '';
        
        // Force reload data with cache clear
        await loadData();
        return;
      }
      
      // Handle preview mode (for files that need department/level selection)
      if (result.students && result.students.length > 0) {
        uploadedStudents = result.students;
        uploadSelectedDepartment = result.department || '';
        uploadSelectedLevel = result.level || '';
        
        success = `Successfully extracted ${uploadedStudents.length} students from file`;
        setTimeout(() => success = '', 3000);
      } else {
        fileUploadError = 'No valid student data found in the file. Please check the format.';
      }
      
    } catch (err) {
      console.error(' File processing error:', err);
      
      // Provide more specific error messages
      let errorMsg = err.message || 'Failed to process file';
      
      if (errorMsg.includes('Unsupported file format')) {
        errorMsg = 'Unsupported file format. Please use Excel (.xlsx, .xls), CSV, or text files.';
      } else if (errorMsg.includes('File is empty')) {
        errorMsg = 'The selected file is empty. Please choose a file with student data.';
      } else if (errorMsg.includes('No valid student data')) {
        errorMsg = 'No student names found in the file. Please check the file format and content.';
      } else if (errorMsg.includes('Failed to read file')) {
        errorMsg = 'Could not read the file. Please ensure the file is not corrupted.';
      } else if (errorMsg.includes('File size must be less than')) {
        errorMsg = 'File is too large. Please use a file smaller than 10MB.';
      }
      
      fileUploadError = errorMsg;
    } finally {
      isProcessingFile = false;
    }
  }
  
  async function uploadStudentsToSystem() {
    if (uploadedStudents.length === 0) {
      error = 'No students to upload';
      return;
    }
    
    if (!uploadSelectedDepartment || !uploadSelectedLevel) {
      error = 'Please select department and level';
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      // Update students with selected department and level
      const studentsToUpload = uploadedStudents.map(student => ({
        ...student,
        department: uploadSelectedDepartment,
        level: uploadSelectedLevel
      }));
      
      const result = await api.uploadStudents(studentsToUpload);
      
      success = result.message || `Successfully uploaded ${studentsToUpload.length} students`;
      setTimeout(() => success = '', 5000);
      
      // Reset form
      showStudentUpload = false;
      uploadFile = null;
      uploadedStudents = [];
      uploadSelectedDepartment = '';
      uploadSelectedLevel = '';
      
      // Reload data
      await loadData();
      
    } catch (err) {
      console.error('Upload error:', err);
      error = err.message || 'Failed to upload students';
    } finally {
      loading = false;
    }
  }
  
  async function generateCredentials() {
    if (!uploadSelectedDepartment || !uploadSelectedLevel) {
      error = 'Please select department and level';
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      // Use FULL department name (students are stored with full names, not codes)
      console.log(' Generating credentials for:', uploadSelectedDepartment, uploadSelectedLevel);
      
      const blob = await api.generateStudentCredentialsPDF(uploadSelectedDepartment, uploadSelectedLevel);
      
      // Download the PDF
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Student_Credentials_${uploadSelectedDepartment.replace(' ', '_')}_${uploadSelectedLevel.replace(' ', '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      success = 'Student credentials PDF generated successfully!';
      setTimeout(() => success = '', 3000);
      
      showCredentialsModal = false;
      uploadSelectedDepartment = '';
      uploadSelectedLevel = '';
      
    } catch (err) {
      console.error('Credentials generation error:', err);
      error = err.message || 'Failed to generate credentials';
    } finally {
      loading = false;
    }
  }
  
  // Clear all students (for testing)
  async function clearAllStudents() {
    if (!confirm(' WARNING: This will permanently delete ALL students from the system. This action cannot be undone. Are you sure?')) {
      return;
    }
    
    if (!confirm('This is your final confirmation. All student data will be lost. Continue?')) {
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      console.log(' Clearing all students...');
      
      const result = await api.clearAllStudents();
      
      console.log(' Students cleared:', result);
      
      // Reload data
      await loadData();
      
      success = `Successfully cleared ${result.count} students from the system`;
      setTimeout(() => success = '', 5000);
      
    } catch (err) {
      console.error(' Clear students error:', err);
      error = err.message || 'Failed to clear students';
    } finally {
      loading = false;
    }
  }
  

</script>

<svelte:head>
  <title>DOS Dashboard - TVET Quiz System</title>
</svelte:head>

<div class="min-h-screen relative overflow-hidden">
  <AnimatedBackground variant="blue" />
  {#if !isLoggedIn}
    <div class="flex items-center justify-center min-h-screen p-4 relative z-10">
      <div class="w-full max-w-md">
        <div class="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
          <div class="text-center mb-8">
            <div class="w-20 h-20 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl animate-pulse">
              <span class="text-3xl text-white">🎓</span>
            </div>
            <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">DOS Portal</h1>
            <p class="text-gray-600">Deputy of Studies Dashboard</p>
          </div>
          
          {#if error}
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
              <div class="text-red-700 text-sm font-medium">{error}</div>
            </div>
          {/if}

          <form on:submit|preventDefault={handleLogin} class="space-y-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Username</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                type="text"
                bind:value={username}
                placeholder="Enter DOS username"
                disabled={loading}
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Password</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                type="password"
                bind:value={password}
                placeholder="Enter DOS password"
                disabled={loading}
              />
            </div>

            <button 
              class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all transform hover:scale-105" 
              type="submit" 
              disabled={loading}
            >
              {loading ? ' Signing in...' : ' Sign In'}
            </button>
          </form>

          <div class="mt-8 text-center">
            <a href="/teacher" class="text-blue-600 hover:text-blue-800 text-sm font-medium mr-4">
              Teacher Portal 
            </a>
            <a href="/" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
               Student Portal
            </a>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="min-h-screen relative z-10">
      <!-- Header -->
      <header class="bg-white/80 backdrop-blur-xl shadow-lg border-b border-white/20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center py-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <span class="text-2xl text-white"></span>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">TVET Quiz System</h1>
                <p class="text-gray-600">Deputy of Studies Dashboard</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="text-right">
                <div class="text-lg font-semibold text-gray-900">{user.full_name || user.username}</div>
                <div class="text-sm text-gray-600">Deputy of Studies</div>
              </div>
              <button 
                class="bg-red-500 text-white px-6 py-2 rounded-xl hover:bg-red-600 transition-all"
                on:click={handleLogout}
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {#if error}
          <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
            <div class="text-red-700 font-medium">{error}</div>
          </div>
        {/if}

        {#if success}
          <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-r-lg">
            <div class="text-green-700 font-medium">{success}</div>
          </div>
        {/if}

        <!-- Navigation -->
        <div class="bg-white/90 backdrop-blur-xl rounded-2xl shadow-lg mb-8 p-2 border border-white/20">
          <div class="flex flex-wrap gap-2">
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'overview' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'overview'}
            >
               Overview
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'lessons' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'lessons'}
            >
               Lessons
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'teachers' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'teachers'}
            >
               Teachers
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'assignments' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'assignments'}
            >
               Assignments
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'students' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'students'}
            >
               Students
            </button>
            <button
              class="px-6 py-3 rounded-xl font-medium transition-all {activeTab === 'class-teachers' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-600 hover:bg-gray-100'}"
              on:click={() => activeTab = 'class-teachers'}
            >
              🎓 Class Teachers
            </button>
          </div>
        </div>

        <!-- Overview Tab -->
        {#if activeTab === 'overview'}
          <div class="mb-6">
            <div class="flex justify-between items-center">
              <h2 class="text-2xl font-bold text-gray-900">System Overview</h2>
              <button 
                class="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-all disabled:opacity-50"
                on:click={loadData}
                disabled={loading}
              >
                {loading ? ' Refreshing...' : ' Refresh Data'}
              </button>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-blue-100">Total Lessons</p>
                  <p class="text-3xl font-bold">{lessons.length}</p>
                </div>
                <div class="text-4xl opacity-80"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-green-100">Teachers</p>
                  <p class="text-3xl font-bold">{teachers.length}</p>
                </div>
                <div class="text-4xl opacity-80"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-purple-100">Students</p>
                  <p class="text-3xl font-bold">{students.length}</p>
                </div>
                <div class="text-4xl opacity-80"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-orange-100">Departments</p>
                  <p class="text-3xl font-bold">{departments.length}</p>
                </div>
                <div class="text-4xl opacity-80"></div>
              </div>
            </div>
          </div>



          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-2xl shadow-lg p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4"> Department Statistics</h3>
              <div class="space-y-4">
                {#each departments as dept}
                  <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span class="text-gray-700 font-medium">{dept}</span>
                    <div class="flex space-x-4">
                      <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {lessons.filter(l => l.department === dept).length} lessons
                      </span>
                      <span class="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                        {students.filter(s => s.department === dept).length} students
                      </span>
                      <span class="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">
                        {teachers.filter(t => t.departments && t.departments.includes(dept)).length} teachers
                      </span>
                    </div>
                  </div>
                {/each}
              </div>
            </div>

            <div class="bg-white rounded-2xl shadow-lg p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4"> System Status</h3>
              <div class="space-y-3">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-gray-700">Backend Connected</span>
                </div>
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-gray-700">Database Operational</span>
                </div>
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-gray-700">All Portals Accessible</span>
                </div>
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-gray-700">Offline Support Enabled</span>
                </div>
              </div>
            </div>
          </div>
        {/if}
        
        <!-- Lessons Tab -->
        {#if activeTab === 'lessons'}
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1">
              <div class="bg-white rounded-2xl shadow-lg p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-6"> Create New Lesson</h3>
                <div class="space-y-4">
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    bind:value={newLesson.title}
                    placeholder="Lesson Title"
                  />
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    bind:value={newLesson.code}
                    placeholder="Lesson Code"
                  />
                  <select class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500" bind:value={newLesson.department}>
                    <option value="">Select Department</option>
                    {#each departments as dept}
                      <option value={dept}>{dept}</option>
                    {/each}
                  </select>
                  <select class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500" bind:value={newLesson.level}>
                    <option value="">Select Level</option>
                    {#each levels as level}
                      <option value={level}>{level}</option>
                    {/each}
                  </select>
                  <select class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500" bind:value={newLesson.classification}>
                    {#each classifications as classification}
                      <option value={classification}>{classification}</option>
                    {/each}
                  </select>
                  <textarea
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    bind:value={newLesson.description}
                    placeholder="Lesson Description"
                    rows="3"
                  ></textarea>
                  <button
                    class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all"
                    on:click={createLesson}
                    disabled={loading}
                  >
                    {loading ? 'Creating...' : 'Create Lesson'}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="lg:col-span-2">
              <div class="bg-white rounded-2xl shadow-lg p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-6">All Lessons ({lessons.length})</h3>
                <div class="space-y-4 max-h-96 overflow-y-auto">
                  {#each lessons as lesson}
                    <div class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all">
                      <div class="flex justify-between items-start">
                        <div>
                          <h4 class="font-bold text-gray-900">{lesson.title}</h4>
                          <p class="text-sm text-gray-600">{lesson.code} - {lesson.department} - {lesson.level}</p>
                          <p class="text-sm text-gray-500 mt-1">{lesson.description}</p>
                          <span class="inline-block mt-2 px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">{lesson.classification}</span>
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Teachers Tab -->
        {#if activeTab === 'teachers'}
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1">
              <div class="bg-white rounded-2xl shadow-lg p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-6"> Register Teacher</h3>
                <div class="space-y-4">
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    bind:value={newTeacher.username}
                    placeholder="Username"
                  />
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    type="password"
                    bind:value={newTeacher.password}
                    placeholder="Password"
                  />
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    bind:value={newTeacher.full_name}
                    placeholder="Full Name"
                  />
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Departments</label>
                    <div class="grid grid-cols-1 gap-2">
                      {#each departments as dept}
                        <label class="flex items-center p-2 border border-gray-200 rounded-lg hover:bg-gray-50">
                          <input
                            type="checkbox"
                            class="mr-3 text-blue-600 focus:ring-blue-500"
                            checked={newTeacher.departments.includes(dept)}
                            on:change={() => toggleTeacherDepartment(dept)}
                          />
                          <span class="text-sm">{dept}</span>
                        </label>
                      {/each}
                    </div>
                  </div>
                  
                  <button
                    class="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-green-700 hover:to-blue-700 disabled:opacity-50 transition-all"
                    on:click={registerTeacher}
                    disabled={loading}
                  >
                    {loading ? 'Registering...' : 'Register Teacher'}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="lg:col-span-2">
              <div class="bg-white rounded-2xl shadow-lg p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-6">All Teachers ({teachers.length})</h3>
                <div class="space-y-4 max-h-96 overflow-y-auto">
                  {#each teachers as teacher}
                    <div class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all">
                      <div class="flex justify-between items-start">
                        <div>
                          <h4 class="font-bold text-gray-900">{teacher.full_name}</h4>
                          <p class="text-sm text-gray-600">@{teacher.username}</p>
                          {#if teacher.departments}
                            <div class="flex flex-wrap gap-1 mt-2">
                              {#each teacher.departments as dept}
                                <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">{dept}</span>
                              {/each}
                            </div>
                          {/if}
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Assignments Tab -->
        {#if activeTab === 'assignments'}
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-2xl shadow-lg p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-6">Select Teacher</h3>
              <div class="space-y-2 max-h-96 overflow-y-auto">
                {#each teachers as teacher}
                  <div 
                    class="border border-gray-200 rounded-xl p-4 cursor-pointer hover:bg-gray-50 transition-all {selectedTeacher?.id === teacher.id ? 'bg-blue-50 border-blue-300' : ''}"
                    on:click={() => selectTeacher(teacher)}
                  >
                    <h4 class="font-bold text-gray-900">{teacher.full_name}</h4>
                    <p class="text-sm text-gray-600">@{teacher.username}</p>
                  </div>
                {/each}
              </div>
            </div>
            
            <div class="bg-white rounded-2xl shadow-lg p-6">
              {#if selectedTeacher}
                <h3 class="text-xl font-bold text-gray-900 mb-6">{selectedTeacher.full_name}'s Lessons</h3>
                
                <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                  <h4 class="font-bold text-blue-900 mb-2">Assign New Lesson</h4>
                  <select 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm mb-2"
                    bind:value={selectedDepartment}
                    on:change={filterLessonsByDepartment}
                  >
                    <option value="">Select Department</option>
                    {#each departments as dept}
                      <option value={dept}>{dept}</option>
                    {/each}
                  </select>
                  
                  {#if filteredLessons.length > 0}
                    <div class="space-y-1">
                      {#each filteredLessons as lesson}
                        <div class="flex justify-between items-center p-2 bg-white rounded border">
                          <span class="text-sm">{lesson.title} ({lesson.code})</span>
                          <button
                            class="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-all"
                            on:click={() => assignLessonToTeacher(selectedTeacher.id, lesson.id)}
                          >
                            Assign
                          </button>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
                
                <div class="space-y-2">
                  <h4 class="font-bold text-gray-900">Current Assignments ({teacherLessons.length})</h4>
                  {#each teacherLessons as assignment}
                    <div class="flex justify-between items-center p-3 border border-gray-200 rounded-xl">
                      <div>
                        <div class="font-medium">{assignment.lesson.title}</div>
                        <div class="text-sm text-gray-600">{assignment.lesson.code} - {assignment.lesson.department}</div>
                      </div>
                      <button
                        class="bg-red-500 text-white px-3 py-1 rounded text-xs hover:bg-red-600 transition-all"
                        on:click={() => removeTeacherLesson(assignment.id)}
                      >
                        Remove
                      </button>
                    </div>
                  {/each}
                </div>
              {:else}
                <p class="text-gray-600 text-center py-8">Select a teacher to manage their lesson assignments</p>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Class Teachers Tab -->
        {#if activeTab === 'class-teachers'}
          <ClassTeacherManager />
        {/if}

        <!-- Students Tab -->
        {#if activeTab === 'students'}
          <div class="space-y-6">
            <div class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-gray-900"> Student Management</h3>
                <div class="flex space-x-3">
                  <button 
                    class="bg-green-600 text-white px-4 py-2 rounded-xl hover:bg-green-700 transition-all"
                    on:click={() => showStudentUpload = true}
                  >
                     Upload Students
                  </button>
                  <button 
                    class="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-all"
                    on:click={() => showCredentialsModal = true}
                  >
                     Generate Credentials
                  </button>
                  <button 
                    class="bg-red-600 text-white px-4 py-2 rounded-xl hover:bg-red-700 transition-all"
                    on:click={clearAllStudents}
                    disabled={loading}
                  >
                     Clear All
                  </button>
                </div>
              </div>
            </div>
            
            <div class="bg-white rounded-2xl shadow-lg p-6">
              <h4 class="text-lg font-bold text-gray-900 mb-4">All Students ({students.length})</h4>
              
              {#if students.length === 0}
                <div class="text-center py-8">
                  <div class="text-6xl mb-4"></div>
                  <p class="text-gray-600">No students registered yet</p>
                  <p class="text-sm text-gray-500 mt-2">Use the "Upload Students" button to add students to the system</p>
                </div>
              {:else}
                <div class="overflow-x-auto">
                  <table class="w-full">
                    <thead>
                      <tr class="border-b border-gray-200 bg-gray-50">
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Student ID</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Full Name</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Department</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Level</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Registered</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each students.slice(0, 50) as student}
                        <tr class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                          <td class="py-3 px-4 font-mono text-sm">{student.username}</td>
                          <td class="py-3 px-4">{student.full_name || 'N/A'}</td>
                          <td class="py-3 px-4">
                            <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                              {student.department || 'N/A'}
                            </span>
                          </td>
                          <td class="py-3 px-4">
                            <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                              {student.level || 'N/A'}
                            </span>
                          </td>
                          <td class="py-3 px-4 text-sm text-gray-500">
                            {student.created_at ? new Date(student.created_at).toLocaleDateString() : 'N/A'}
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                  
                  {#if students.length > 50}
                    <div class="mt-4 text-center text-sm text-gray-500">
                      Showing first 50 students out of {students.length} total
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
        {/if}


      </div>
    </div>
  {/if}
  
  <!-- Student Upload Modal -->
  {#if showStudentUpload}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900"> Upload Student List</h3>
          <button 
            class="text-gray-500 hover:text-gray-700 text-2xl"
            on:click={() => {
              showStudentUpload = false;
              uploadFile = null;
              uploadedStudents = [];
              fileUploadError = '';
              uploadSelectedDepartment = '';
              uploadSelectedLevel = '';
            }}
          >
            
          </button>
        </div>
        
        <div class="space-y-6">
          <!-- File Upload Section -->
          <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center">
            <div class="text-4xl mb-4"></div>
            <h4 class="text-lg font-semibold mb-2">Select Student List File</h4>
            <p class="text-gray-600 mb-4">Supported formats: Excel (.xlsx, .xls) and PDF (.pdf) files</p>
            <div class="text-sm text-gray-500 mb-4">
              <p><strong> File Format Tips:</strong></p>
              <ul class="list-disc list-inside space-y-1">
                <li> Excel: Names in column B, header row with "S/N" or "Names"</li>
                <li> PDF: Numbered student list (1. Name, 2. Name, etc.)</li>
                <li> Make sure names are clearly visible and properly formatted</li>
                <li> File size limit: 10MB</li>
              </ul>
            </div>
            
            <input 
              type="file" 
              accept=".xlsx,.xls,.pdf" 
              on:change={handleFileSelect}
              class="hidden"
              id="studentFileInput"
            />
            <label 
              for="studentFileInput" 
              class="inline-block bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 cursor-pointer transition-all"
            >
              Choose File
            </label>
            
            {#if uploadFile}
              <div class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-green-800"> {uploadFile.name}</p>
                <p class="text-sm text-green-600">{(uploadFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            {/if}
            
            {#if fileUploadError}
              <div class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-red-800"> {fileUploadError}</p>
              </div>
            {/if}
            
            {#if isProcessingFile}
              <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-center space-x-2">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <p class="text-blue-800">Processing file... Please wait</p>
                </div>
                <p class="text-sm text-blue-600 mt-1">Parsing student data and validating format</p>
              </div>
            {/if}
          </div>
          
          <!-- Department and Level Selection - Always Show -->
          <div class="bg-yellow-50 border-2 border-yellow-400 rounded-xl p-4">
            <div class="flex items-center space-x-2 mb-3">
              <span class="text-2xl"></span>
              <h4 class="font-bold text-yellow-900"> IMPORTANT: Select Department and Level FIRST!</h4>
            </div>
            <p class="text-sm text-yellow-800 mb-3">You MUST select both Department and Level BEFORE uploading the file. These values will be assigned to all students in the file.</p>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Department</label>
                <select bind:value={uploadSelectedDepartment} class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="">Select Department</option>
                  {#each departments as dept}
                    <option value={dept}>{dept}</option>
                  {/each}
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Level</label>
                <select bind:value={uploadSelectedLevel} class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="">Select Level</option>
                  {#each levels as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
            </div>
          </div>
          
          <!-- Preview Students -->
          {#if uploadedStudents.length > 0}
            <div class="bg-gray-50 rounded-xl p-4">
              <h4 class="font-semibold mb-3"> Preview ({uploadedStudents.length} students found)</h4>
              <div class="max-h-40 overflow-y-auto">
                <div class="grid grid-cols-2 gap-2 text-sm">
                  {#each uploadedStudents.slice(0, 10) as student}
                    <div class="bg-white p-2 rounded border">
                      <div class="font-medium">{student.full_name}</div>
                      <div class="text-gray-600">{student.username}</div>
                    </div>
                  {/each}
                </div>
                {#if uploadedStudents.length > 10}
                  <p class="text-center text-gray-600 mt-2">... and {uploadedStudents.length - 10} more students</p>
                {/if}
              </div>
            </div>
          {/if}
          
          <!-- Upload Button -->
            <div class="flex space-x-4">
              <button 
                class="flex-1 bg-green-600 text-white py-3 px-6 rounded-xl hover:bg-green-700 disabled:opacity-50 transition-all"
                on:click={uploadStudentsToSystem}
                disabled={loading || !uploadSelectedDepartment || !uploadSelectedLevel}
              >
                {loading ? ' Uploading...' : ' Upload Students'}
              </button>
              <button 
                class="px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all"
                on:click={() => {
                  showStudentUpload = false;
                  uploadFile = null;
                  uploadedStudents = [];
                  fileUploadError = '';
                }}
              >
                Cancel
              </button>
            </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Credentials Generation Modal -->
  {#if showCredentialsModal}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900"> Generate Credentials</h3>
          <button 
            class="text-gray-500 hover:text-gray-700 text-2xl"
            on:click={() => {
              showCredentialsModal = false;
              uploadSelectedDepartment = '';
              uploadSelectedLevel = '';
            }}
          >
            
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Department</label>
            <select bind:value={uploadSelectedDepartment} class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="">Select Department</option>
              {#each departments as dept}
                <option value={dept}>{dept}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Level</label>
            <select bind:value={uploadSelectedLevel} class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="">Select Level</option>
              {#each levels as level}
                <option value={level}>{level}</option>
              {/each}
            </select>
          </div>
          
          <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div class="flex items-start space-x-3">
              <div class="text-blue-600 text-xl"></div>
              <div class="text-sm text-blue-800">
                <p class="font-semibold mb-1">This will generate:</p>
                <ul class="list-disc list-inside space-y-1">
                  <li>Professional PDF with all student credentials</li>
                  <li>Login instructions for students</li>
                  <li>Security guidelines</li>
                  <li>Class teacher instructions</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-4">
            <button 
              class="flex-1 bg-blue-600 text-white py-3 px-6 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-all"
              on:click={generateCredentials}
              disabled={loading || !uploadSelectedDepartment || !uploadSelectedLevel}
            >
              {loading ? ' Generating...' : ' Generate PDF'}
            </button>
            <button 
              class="px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all"
              on:click={() => {
                showCredentialsModal = false;
                uploadSelectedDepartment = '';
                uploadSelectedLevel = '';
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>



<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  @keyframes blob {
    0% { transform: translate(0px, 0px) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
    100% { transform: translate(0px, 0px) scale(1); }
  }
  
  :global(.animate-blob) {
    animation: blob 7s infinite;
  }
  
  :global(.animation-delay-2000) {
    animation-delay: 2s;
  }
  
  :global(.animation-delay-4000) {
    animation-delay: 4s;
  }
</style>



