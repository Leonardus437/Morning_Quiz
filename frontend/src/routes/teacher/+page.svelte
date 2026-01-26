<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';

  let username = '';
  let password = '';
  let loading = false;
  let error = '';
  let activeTab = 'dashboard';
  
  // Data
  let questions = [];
  let quizzes = [];
  let results = [];
  let currentQuizId = null;
  let schedules = [];
  let announcements = [];
  let lessons = [];
  let notifications = [];
  let unreadCount = 0;
  let showNotificationWidget = false;
  let notificationInterval;
  let latestNotifications = [];
  let myCourses = [];
  let myClasses = [];
  let showBulkUpload = false;
  let showTemplates = false;
  let showManualBuilder = false;
  let selectedFile = null;
  let uploadingFile = false;
  let questionForms = [];
  let bulkMode = false;
  let studentUploadText = '';
  let uploadingStudents = false;
  let showStudentFileUpload = false;
  let selectedStudentFile = null;
  let uploadingStudentFile = false;
  let studentDepartment = '';
  let studentLevel = '';
  let newStudentName = '';
  let newStudentDept = '';
  let newStudentLevel = '';
  
  // Debug reactive statements
  $: console.log('studentDepartment:', studentDepartment);
  $: console.log('studentLevel:', studentLevel);
  $: console.log('selectedStudentFile:', selectedStudentFile);
  $: canUpload = studentDepartment && studentLevel && selectedStudentFile;
  let editingQuestion = null;
  let showEditModal = false;
  let showAllQuestions = false;
  let editForm = {
    question_text: '',
    question_type: 'mcq',
    options: ['', '', '', ''],
    correct_answer: '',
    points: 1,
    department: '',
    level: '',
    lesson_id: null
  };
  
  function initializeQuestionForms() {
    questionForms = [];
  }
  
  function useTemplate(type) {
    const template = {
      question_text: '',
      question_type: type,
      options: type === 'mcq' ? ['', '', '', ''] : [],
      correct_answer: '',
      points: 1,
      department: '',
      level: '',
      lesson_id: null
    };
    
    if (type === 'mcq') {
      template.question_text = 'What is the correct answer?';
      template.options = ['Option A', 'Option B', 'Option C', 'Option D'];
    } else if (type === 'true_false') {
      template.question_text = 'This statement is true. True or False?';
    } else if (type === 'short_answer') {
      template.question_text = 'Explain or define the following:';
      template.correct_answer = 'Sample answer';
    }
    
    questionForms = [...questionForms, template];
    showTemplates = false;
    showManualBuilder = true;
  }
  
  onMount(() => {
    initializeQuestionForms();
  });
  
  // Forms - removed as we now use questionForms array

  const departments = [
    'Software Development',
    'Computer System and Architecture', 
    'Land Surveying',
    'Building Construction'
  ];
  
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  
  let newQuiz = {
    title: '',
    description: '',
    scheduled_time: '',
    duration_minutes: 30,
    question_time_seconds: 60,
    department: '',
    level: '',
    question_ids: []
  };

  $: isLoggedIn = $user !== null && $user.role === 'teacher';

  let refreshInterval;
  let lastNotificationCheck = 0; // Track last notification timestamp
  
  onMount(async () => {
    console.log('Teacher page mounted');
    
    // Check URL parameters for tab
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    const reloadParam = urlParams.get('reload');
    
    if (tabParam) {
      activeTab = tabParam;
    }
    
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      try {
        const userData = JSON.parse(storedUser);
        console.log('Found stored user:', userData);
        
        if (userData.role === 'teacher') {
          // Test token validity
          const testResponse = await fetch(`${api.baseURL}/auth/test`, {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          if (testResponse.ok) {
            console.log('Token is valid, logging in user');
            api.setToken(storedToken);
            user.login(userData);
            await loadData();
            
            // If reload parameter is present, force reload questions
            if (reloadParam === '1') {
              console.log('Reload parameter detected, refreshing questions...');
              await loadData();
              // Clean URL by removing reload parameter
              window.history.replaceState({}, '', '/teacher?tab=' + (tabParam || 'dashboard'));
            }
            
            startAutoRefresh();
          } else {
            console.log('Token expired, clearing storage');
            localStorage.removeItem('user');
            localStorage.removeItem('token');
          }
        }
      } catch (err) {
        console.log('Session validation failed:', err.message);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
    
    // Start notification polling
    startNotificationPolling();
    
    // Cleanup on component destroy
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
      if (notificationInterval) {
        clearInterval(notificationInterval);
      }
    };
  });
  
  function startAutoRefresh() {
    // Auto-refresh data every 30 seconds
    refreshInterval = setInterval(async () => {
      if (isLoggedIn) {
        await loadData();
      }
    }, 30000);
  }

  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password';
      return;
    }

    loading = true;
    error = '';

    try {
      console.log('Attempting login for:', username);
      
      const result = await api.login(username, password);
      console.log('Login successful:', result.user);
      
      if (result.user.role !== 'teacher') {
        throw new Error('Teacher access required');
      }
      
      // Store authentication data
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('token', result.access_token);
      
      // Update stores
      api.setToken(result.access_token);
      user.login(result.user);
      
      // Load data and start refresh
      await loadData();
      startAutoRefresh();
      
      username = '';
      password = '';
      
      console.log('Login process completed successfully');
    } catch (err) {
      error = err.message;
      console.error('❌ Login error:', err);
    } finally {
      loading = false;
    }
  }

  async function loadData() {
    try {
      loading = true;
      error = '';
      
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('No token found, skipping data load');
        return;
      }
      
      const headers = { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      
      // Use api.baseURL to get correct backend URL (Render or localhost)
      const baseURL = api.baseURL;
      
      const [questionsData, quizzesData, schedulesData, announcementsData, lessonsData, notificationsData] = await Promise.all([
        fetch(`${baseURL}/questions`, { headers }).then(r => {
          if (r.status === 401 || r.status === 403) {
            console.log('Auth failed for questions');
            return [];
          }
          return r.ok ? r.json() : [];
        }).catch(() => []),
        fetch(`${baseURL}/quizzes`, { headers }).then(r => {
          if (r.status === 401 || r.status === 403) {
            console.log('Auth failed for quizzes');
            return [];
          }
          return r.ok ? r.json() : [];
        }).catch(() => []),
        fetch(`${baseURL}/schedules`, { headers }).then(r => r.ok ? r.json() : []).catch(() => []),
        fetch(`${baseURL}/announcements`, { headers }).then(r => r.ok ? r.json() : []).catch(() => []),
        fetch(`${baseURL}/lessons`, { headers }).then(r => r.ok ? r.json() : []).catch(() => []),
        fetch(`${baseURL}/notifications`, { headers }).then(r => r.ok ? r.json() : []).catch(() => [])
      ]);
      
      questions = [...questionsData];
      quizzes = [...quizzesData];
      schedules = [...schedulesData];
      announcements = [...announcementsData];
      lessons = [...lessonsData];
      notifications = [...notificationsData];
      unreadCount = notifications.filter(n => !n.is_read).length;
      
      console.log('Data loaded:', { questions: questions.length, quizzes: quizzes.length, lessons: lessons.length });
      
      // Skip loading classes to avoid auth errors
      myClasses = [];
    } catch (err) {
      console.error('Load data error:', err);
    } finally {
      loading = false;
    }
  }

  function handleLogout() {
    if (notificationInterval) {
      clearInterval(notificationInterval);
    }
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    
    api.clearToken();
    user.logout();
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    
    username = '';
    password = '';
    error = '';
    
    questions = [];
    quizzes = [];
    results = [];
    schedules = [];
    announcements = [];
    lessons = [];
    notifications = [];
    unreadCount = 0;
  }

  function startNotificationPolling() {
    if (notificationInterval) clearInterval(notificationInterval);
    
    // Initialize last check time to current time to prevent showing old notifications
    lastNotificationCheck = Date.now();
    
    notificationInterval = setInterval(async () => {
      if (isLoggedIn) {
        try {
          const newNotifications = await api.getNotifications();
          const newUnreadCount = newNotifications.filter(n => !n.is_read).length;
          
          // Only show widget if there are TRULY NEW notifications
          // (notifications created AFTER our last check)
          if (newUnreadCount > 0) {
            // Check if any notifications are actually new (created after last check)
            const trulyNewNotifications = newNotifications.filter(n => {
              if (n.is_read) return false;
              const notifTime = new Date(n.created_at).getTime();
              return notifTime > lastNotificationCheck;
            });
            
            if (trulyNewNotifications.length > 0) {
              latestNotifications = trulyNewNotifications.slice(0, 3);
              showNotificationWidget = true;
              
              // Update last check time BEFORE showing popup
              lastNotificationCheck = Date.now();
              
              setTimeout(() => {
                showNotificationWidget = false;
              }, 5000);
            }
          }
          
          notifications = newNotifications;
          unreadCount = newUnreadCount;
        } catch (err) {
          // Stop polling on authentication errors
          if (err.message && err.message.includes('Authentication')) {
            console.error('Authentication failed, stopping notification polling');
            if (notificationInterval) {
              clearInterval(notificationInterval);
              notificationInterval = null;
            }
          }
        }
      }
    }, 5000); // Changed to 5 seconds to reduce spam
  }

  function dismissWidget() {
    showNotificationWidget = false;
  }

  async function loadMyCourses() {
    try {
      myCourses = await api.getMyCourses();
    } catch (err) {
      error = 'Failed to load courses: ' + err.message;
    }
  }

  async function loadMyClasses() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${api.baseURL}/teacher/my-classes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        myClasses = await response.json();
        console.log('Loaded classes:', myClasses);
      } else {
        console.log('Failed to load classes, status:', response.status);
        myClasses = [];
      }
    } catch (err) {
      console.error('Failed to load classes:', err);
      myClasses = [];
    }
  }

  function addNewQuestionForm() {
    questionForms = [...questionForms, {
      question_text: '',
      question_type: 'mcq',
      options: ['', '', '', ''],
      correct_answer: '',
      points: 1,
      department: '',
      level: '',
      lesson_id: null
    }];
  }

  function removeQuestionForm(index) {
    if (questionForms.length > 1) {
      questionForms = questionForms.filter((_, i) => i !== index);
    }
  }

  function handleFileUpload(event) {
    selectedFile = event.target.files[0];
  }

  async function uploadQuestions() {
    if (!selectedFile) return;
    
    uploadingFile = true;
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch(`${api.baseURL}/upload-questions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const result = await response.json();
      
      if (!result.questions || result.questions.length === 0) {
        throw new Error('No questions found in the document. Please check the format.');
      }
      
      // Process and populate forms with parsed questions
      questionForms = result.questions.slice(0, 20).map((questionObj, index) => {
        let formattedOptions = ['', '', '', ''];
        
        // Handle different option formats
        if (questionObj.options && Array.isArray(questionObj.options)) {
          if (questionObj.options.length > 0) {
            // Use extracted options and ensure we have at least 4 slots for MCQ
            formattedOptions = [...questionObj.options];
            while (formattedOptions.length < 4) {
              formattedOptions.push('');
            }
          }
        }
        
        return {
          question_text: questionObj.question_text || '',
          question_type: questionObj.question_type || 'short_answer',
          options: formattedOptions,
          correct_answer: questionObj.correct_answer || '',
          points: 1,
          department: '',
          level: '',
          lesson_id: null
        };
      });
      
      // Show success with detailed breakdown
      const mcqCount = questionForms.filter(q => q.question_type === 'mcq').length;
      const tfCount = questionForms.filter(q => q.question_type === 'true_false').length;
      const saCount = questionForms.filter(q => q.question_type === 'short_answer').length;
      
      // Auto-show manual builder with extracted questions
      showBulkUpload = false;
      showManualBuilder = true;
      
      alert(`🤖 AI Extraction Complete!\n\n📊 Processed ${questionForms.length} questions:\n• ${mcqCount} Multiple Choice (with real options)\n• ${tfCount} True/False\n• ${saCount} Short Answer\n\n✅ Options and answers extracted\n📝 Complete department, level & lesson to finish`);
      
      selectedFile = null;
    } catch (err) {
      error = 'AI Processing failed: ' + err.message;
      console.error('Document upload error:', err);
    } finally {
      uploadingFile = false;
    }
  }

  async function createBulkQuestions() {
    try {
      loading = true;
      error = '';
      
      // Filter and validate questions
      const validQuestions = questionForms.filter(q => {
        return q.question_text.trim() && 
               q.department && 
               q.level && 
               q.lesson_id && 
               q.correct_answer.trim();
      });
      
      if (validQuestions.length === 0) {
        error = 'No valid questions found. Please fill all required fields.';
        return;
      }
      
      // Prepare questions for API
      const questionsToCreate = validQuestions.map(q => ({
        question_text: q.question_text.trim(),
        question_type: q.question_type,
        options: q.question_type === 'short_answer' ? [] : q.options.filter(opt => opt.trim()),
        correct_answer: q.correct_answer.trim(),
        points: parseInt(q.points) || 1,
        department: q.department,
        level: q.level,
        lesson_id: parseInt(q.lesson_id)
      }));
      
      const response = await fetch(`${api.baseURL}/questions/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ questions: questionsToCreate })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create questions');
      }
      
      const result = await response.json();
      alert(`✅ Successfully created ${result.count} questions!`);
      initializeQuestionForms();
      await loadData();
      activeTab = 'questions';
    } catch (err) {
      error = err.message || 'Failed to create questions';
      console.error('Bulk question creation error:', err);
    } finally {
      loading = false;
    }
  }

  async function createQuestion(formIndex = null) {
    try {
      loading = true;
      error = '';
      
      if (formIndex !== null) {
        // Create single question
        const form = questionForms[formIndex];
        await createSingleQuestion(form);
        alert('Question created successfully!');
      } else {
        // Create all questions
        let created = 0;
        for (let i = 0; i < questionForms.length; i++) {
          try {
            await createSingleQuestion(questionForms[i]);
            created++;
          } catch (err) {
            console.error(`Failed to create question ${i + 1}:`, err);
          }
        }
        
        if (created > 0) {
          alert(`Successfully created ${created} out of ${questionForms.length} questions!`);
          // Reset forms
          questionForms = [{
            question_text: '',
            question_type: 'mcq',
            options: ['', '', '', ''],
            correct_answer: '',
            points: 1,
            department: '',
            level: '',
            lesson_id: null
          }];
          activeTab = 'questions';
        }
      }
      
      await loadData();
    } catch (err) {
      error = err.message || 'Failed to create question';
      console.error('Create question error:', err);
    } finally {
      loading = false;
    }
  }

  async function createSingleQuestion(questionData) {
    // Validate form
    if (!questionData.question_text.trim()) {
      throw new Error('Question text is required');
    }
    if (!questionData.department) {
      throw new Error('Department is required');
    }
    if (!questionData.level) {
      throw new Error('Level is required');
    }
    if (!questionData.correct_answer.trim()) {
      throw new Error('Correct answer is required');
    }
    if (!questionData.lesson_id) {
      throw new Error('Lesson selection is required');
    }
    
    // Validate options for MCQ
    if (questionData.question_type === 'mcq') {
      const validOptions = questionData.options.filter(opt => opt.trim());
      if (validOptions.length < 2) {
        throw new Error('At least 2 options are required for multiple choice questions');
      }
      if (!validOptions.includes(questionData.correct_answer)) {
        throw new Error('Correct answer must be one of the provided options');
      }
    }
    
    const payload = {
      question_text: questionData.question_text.trim(),
      question_type: questionData.question_type,
      options: questionData.question_type === 'short_answer' ? [] : questionData.options.filter(opt => opt.trim()),
      correct_answer: questionData.correct_answer.trim(),
      points: parseInt(questionData.points) || 1,
      department: questionData.department,
      level: questionData.level,
      lesson_id: parseInt(questionData.lesson_id)
    };
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${api.baseURL}/questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create question');
    }
    
    return await response.json();
  }

  async function createQuiz() {
    try {
      loading = true;
      error = '';
      
      // Validate form first
      if (!newQuiz.title.trim()) {
        throw new Error('Quiz title is required');
      }
      if (!newQuiz.department) {
        throw new Error('Department is required');
      }
      if (!newQuiz.level) {
        throw new Error('Level is required');
      }
      if (!newQuiz.scheduled_time) {
        throw new Error('Scheduled time is required');
      }
      if (newQuiz.question_ids.length === 0) {
        throw new Error('At least one question must be selected');
      }
      
      // Check authentication
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login again - session expired');
      }
      
      const quizData = {
        title: newQuiz.title.trim(),
        description: newQuiz.description.trim(),
        scheduled_time: new Date(newQuiz.scheduled_time).toISOString(),
        duration_minutes: parseInt(newQuiz.duration_minutes) || 30,
        question_time_seconds: parseInt(newQuiz.question_time_seconds) || 60,
        department: newQuiz.department,
        level: newQuiz.level,
        question_ids: newQuiz.question_ids
      };
      
      console.log('Creating quiz with data:', quizData);
      
      // Direct fetch with better error handling
      const response = await fetch(`${api.baseURL}/quizzes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        body: JSON.stringify(quizData)
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        let errorMessage = 'Failed to create quiz';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        
        if (response.status === 401 || response.status === 403) {
          errorMessage = 'Authentication failed. Please login again.';
          handleLogout();
        }
        
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('Quiz created successfully:', result);
      
      await loadData();
      
      // Reset form
      newQuiz = {
        title: '',
        description: '',
        scheduled_time: '',
        duration_minutes: 30,
        question_time_seconds: 60,
        department: '',
        level: '',
        question_ids: []
      };
      
      activeTab = 'quizzes';
      alert('✅ Quiz created successfully!');
    } catch (err) {
      error = err.message || 'Failed to create quiz';
      console.error('❌ Create quiz error:', err);
      alert('❌ Error: ' + error);
    } finally {
      loading = false;
    }
  }

  async function activateQuiz(quizId) {
    try {
      loading = true;
      error = '';
      
      const result = await api.activateQuiz(quizId);
      console.log('Quiz activated:', result);
      await loadData();
      alert('Quiz activated successfully!');
    } catch (err) {
      error = err.message || 'Failed to activate quiz';
      console.error('Activate quiz error:', err);
    } finally {
      loading = false;
    }
  }

  async function viewResults(quizId) {
    try {
      loading = true;
      error = '';
      
      results = await api.getQuizResults(quizId);
      currentQuizId = quizId;
      activeTab = 'results';
    } catch (err) {
      error = err.message || 'Failed to load quiz results';
      console.error('View results error:', err);
      results = [];
      currentQuizId = null;
    } finally {
      loading = false;
    }
  }

  async function broadcastQuiz(quizId) {
    try {
      loading = true;
      error = '';
      
      const result = await api.broadcastQuiz(quizId);
      console.log('Quiz broadcasted:', result);
      await loadData();
      alert('Quiz broadcasted to all students immediately!');
    } catch (err) {
      error = err.message || 'Failed to broadcast quiz';
      console.error('Broadcast quiz error:', err);
    } finally {
      loading = false;
    }
  }

  function toggleQuestionSelection(questionId) {
    const index = newQuiz.question_ids.indexOf(questionId);
    if (index > -1) {
      newQuiz.question_ids = newQuiz.question_ids.filter(id => id !== questionId);
    } else {
      newQuiz.question_ids = [...newQuiz.question_ids, questionId];
    }
  }

  function selectAllQuestions() {
    const availableQuestions = questions.filter(q => q.department === newQuiz.department && q.level === newQuiz.level);
    newQuiz.question_ids = availableQuestions.map(q => q.id);
  }

  function deselectAllQuestions() {
    newQuiz.question_ids = [];
  }

  function selectQuestionsByType(type) {
    const questionsOfType = questions.filter(q => 
      q.department === newQuiz.department && 
      q.level === newQuiz.level && 
      q.question_type === type
    );
    const typeQuestionIds = questionsOfType.map(q => q.id);
    newQuiz.question_ids = [...new Set([...newQuiz.question_ids, ...typeQuestionIds])];
  }

  $: availableQuestions = questions.filter(q => q.department === newQuiz.department && q.level === newQuiz.level);
  $: allSelected = availableQuestions.length > 0 && availableQuestions.every(q => newQuiz.question_ids.includes(q.id));
  $: noneSelected = newQuiz.question_ids.length === 0;
  $: mcqQuestions = availableQuestions.filter(q => q.question_type === 'mcq');
  $: tfQuestions = availableQuestions.filter(q => q.question_type === 'true_false');
  $: saQuestions = availableQuestions.filter(q => q.question_type === 'short_answer');

  async function exportResults(quizId, format) {
    try {
      loading = true;
      error = '';
      
      let blob;
      let filename;
      
      if (format === 'pdf') {
        blob = await api.exportQuizPDF(quizId);
        filename = `quiz_${quizId}_results.pdf`;
      } else {
        blob = await api.exportQuizExcel(quizId);
        filename = `quiz_${quizId}_results.xlsx`;
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert(`${format.toUpperCase()} exported successfully!`);
    } catch (err) {
      error = err.message || `Failed to export ${format.toUpperCase()}`;
      console.error('Export error:', err);
    } finally {
      loading = false;
    }
  }

  async function markNotificationRead(notificationId) {
    try {
      await api.markNotificationRead(notificationId);
      await loadData();
    } catch (err) {
      error = err.message;
    }
  }

  async function forwardResults(quizId) {
    try {
      await api.forwardQuizResults(quizId);
      alert('Quiz results forwarded to DOS successfully!');
    } catch (err) {
      error = err.message;
    }
  }



  async function uploadStudents() {
    try {
      uploadingStudents = true;
      error = '';
      
      if (!studentUploadText.trim()) {
        error = 'Please enter student data';
        return;
      }
      
      // Parse student data from text
      const lines = studentUploadText.trim().split('\n');
      const students = [];
      
      for (const line of lines) {
        const parts = line.split(',').map(p => p.trim());
        if (parts.length >= 4) {
          students.push({
            username: parts[0],
            full_name: parts[1],
            department: parts[2],
            level: parts[3],
            password: parts[4] || 'student123'
          });
        }
      }
      
      if (students.length === 0) {
        error = 'No valid student data found. Please check the format.';
        return;
      }
      
      const result = await api.uploadStudents(students);
      alert(result.message);
      studentUploadText = '';
    } catch (err) {
      error = err.message;
    } finally {
      uploadingStudents = false;
    }
  }

  function handleStudentFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
      selectedStudentFile = file;
      console.log('File selected:', file.name, 'Size:', file.size);
    } else {
      selectedStudentFile = null;
    }
  }

  function getDeptCode(department) {
    const codes = {
      'Software Development': 'SWD',
      'Building Construction': 'BDC',
      'Computer System and Architecture': 'CSA',
      'Land Surveying': 'LSV'
    };
    return codes[department] || 'STU';
  }

  async function addSingleStudent() {
    if (!newStudentName || !newStudentDept || !newStudentLevel) return;
    
    uploadingStudentFile = true;
    try {
      const deptCode = getDeptCode(newStudentDept);
      const levelNum = newStudentLevel.replace('Level ', '');
      const timestamp = Date.now().toString().slice(-4);
      const username = `${deptCode}${levelNum}${timestamp}`;
      const student = {
        username,
        full_name: newStudentName,
        department: newStudentDept,
        level: newStudentLevel,
        password: 'student123'
      };
      
      const response = await fetch(`${api.baseURL}/teacher/upload-students`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ students: [student] })
      });
      
      if (response.ok) {
        alert(`✅ Student added!\nUsername: ${username}\nPassword: student123`);
        newStudentName = '';
        newStudentDept = '';
        newStudentLevel = '';
      }
    } catch (err) {
      alert('❌ Failed to add student');
    } finally {
      uploadingStudentFile = false;
    }
  }

  async function uploadStudentFile() {
    console.log('uploadStudentFile called');
    console.log('Department:', studentDepartment);
    console.log('Level:', studentLevel);
    console.log('File:', selectedStudentFile);
    
    if (!studentDepartment || !studentLevel) {
      alert('⚠️ Please select both department and level first');
      return;
    }
    
    if (!selectedStudentFile) {
      alert('⚠️ Please select a document file');
      return;
    }
    
    uploadingStudentFile = true;
    error = '';
    
    try {
      console.log('Processing file:', selectedStudentFile.name);
      
      const formData = new FormData();
      formData.append('file', selectedStudentFile);
      
      console.log('Sending file to backend...');
      const response = await fetch(`${api.baseURL}/teacher/upload-students-file`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload failed:', errorText);
        throw new Error(`Upload failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('File processed, students found:', result.students?.length || 0);
      
      if (!result.students || result.students.length === 0) {
        throw new Error('No students found in the document');
      }
      
      // Assign department and level to all students with proper username format
      const deptCode = getDeptCode(studentDepartment);
      const levelNum = studentLevel.replace('Level ', '');
      const studentsToUpload = result.students.map((student, index) => {
        const seqNum = String(index + 1).padStart(3, '0');
        return {
          username: `${deptCode}${levelNum}${seqNum}`,
          full_name: student.full_name,
          department: studentDepartment,
          level: studentLevel,
          password: student.password || 'student123'
        };
      });
      
      console.log('Uploading', studentsToUpload.length, 'students to database...');
      
      const uploadResponse = await fetch(`${api.baseURL}/teacher/upload-students`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ students: studentsToUpload })
      });
      
      console.log('Upload response status:', uploadResponse.status);
      
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        console.error('Database upload failed:', errorText);
        throw new Error(`Failed to save students: ${uploadResponse.status}`);
      }
      
      const uploadResult = await uploadResponse.json();
      console.log('Upload complete:', uploadResult);
      
      alert(`✅ Success!\n\n${uploadResult.message}\n\nUploaded ${studentsToUpload.length} students to:\n${studentDepartment} - ${studentLevel}`);
      
      // Reset form
      selectedStudentFile = null;
      studentDepartment = '';
      studentLevel = '';
      
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = '';
      
    } catch (err) {
      console.error('Upload error:', err);
      error = err.message;
      alert(`❌ Upload Failed\n\n${err.message}\n\nPlease check the file format and try again.`);
    } finally {
      uploadingStudentFile = false;
    }
  }

  function editQuestion(question) {
    editingQuestion = question;
    editForm = {
      question_text: question.question_text,
      question_type: question.question_type,
      options: question.options && question.options.length > 0 ? [...question.options] : ['', '', '', ''],
      correct_answer: question.correct_answer,
      points: question.points,
      department: question.department,
      level: question.level,
      lesson_id: question.lesson_id
    };
    showEditModal = true;
  }

  async function saveEditedQuestion() {
    try {
      loading = true;
      error = '';
      
      const questionData = {
        question_text: editForm.question_text.trim(),
        question_type: editForm.question_type,
        options: editForm.question_type === 'short_answer' ? [] : editForm.options.filter(opt => opt.trim()),
        correct_answer: editForm.correct_answer.trim(),
        points: parseInt(editForm.points) || 1,
        department: editForm.department,
        level: editForm.level,
        lesson_id: parseInt(editForm.lesson_id)
      };
      
      await api.updateQuestion(editingQuestion.id, questionData);
      await loadData();
      showEditModal = false;
      editingQuestion = null;
      alert('Question updated successfully!');
    } catch (err) {
      error = err.message || 'Failed to update question';
    } finally {
      loading = false;
    }
  }

  async function deleteQuestion(questionId) {
    if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
      return;
    }
    
    try {
      loading = true;
      error = '';
      
      await api.deleteQuestion(questionId);
      await loadData();
      alert('Question deleted successfully!');
    } catch (err) {
      error = err.message || 'Failed to delete question';
      if (err.message.includes('used in a quiz')) {
        alert('Cannot delete this question because it is used in a quiz.');
      }
    } finally {
      loading = false;
    }
  }

  function cancelEdit() {
    showEditModal = false;
    editingQuestion = null;
    editForm = {
      question_text: '',
      question_type: 'mcq',
      options: ['', '', '', ''],
      correct_answer: '',
      points: 1,
      department: '',
      level: '',
      lesson_id: null
    };
  }


</script>

<svelte:head>
  <title>Teacher Dashboard - Morning Quiz</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
  {#if !isLoggedIn}
    <!-- Teacher Login -->
    <div class="flex items-center justify-center min-h-screen px-4">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <div class="text-center mb-8">
            <div class="text-4xl mb-4">👨🏫</div>
            <h1 class="text-3xl font-bold text-gray-800">Teacher Portal</h1>
            <p class="text-gray-600 mt-2">Morning Quiz System</p>
          </div>
          
          {#if error}
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg">
              <div class="flex">
                <div class="text-red-400">⚠️</div>
                <div class="ml-3">
                  <div class="text-red-700 text-sm font-semibold mb-1">Authentication Error</div>
                  <div class="text-red-600 text-sm">{error}</div>
                  {#if error.includes('Not authenticated')}
                    <div class="text-red-500 text-xs mt-2">
                      Try refreshing the page or contact your administrator if the problem persists.
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          {/if}

          <form on:submit|preventDefault={handleLogin} class="space-y-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Username</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                type="text"
                bind:value={username}
                placeholder="Enter your username"
                disabled={loading}
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Password</label>
              <input
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                type="password"
                bind:value={password}
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            <button 
              class="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:transform-none" 
              type="submit" 
              disabled={loading}
            >
              {loading ? '🔄 Signing in...' : '🚀 Sign In'}
            </button>
          </form>

          <div class="mt-8 text-center">
            <a href="/admin" class="text-green-600 hover:text-green-800 text-sm font-medium mr-4">
              DOS Portal →
            </a>
            <a href="/" class="text-green-600 hover:text-green-800 text-sm font-medium">
              ← Student Portal
            </a>
          </div>
          
          <!-- Debug Section -->
          {#if error.includes('Not authenticated')}
            <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 class="text-sm font-semibold text-yellow-800 mb-2">🔧 Troubleshooting</h4>
              <div class="space-y-2">
                <button 
                  class="w-full bg-yellow-600 text-white px-4 py-2 rounded text-sm hover:bg-yellow-700 transition-colors disabled:opacity-50"
                  on:click={async () => {
                    try {
                      loading = true;
                      const response = await fetch(`${api.baseURL}/reset-teacher-password?username=` + encodeURIComponent(username), {
                        method: 'POST'
                      });
                      if (response.ok) {
                        alert('✅ Password reset to "pass123". Please try logging in again.');
                        password = 'pass123';
                        error = '';
                      } else {
                        alert('❌ Failed to reset password. Please contact administrator.');
                      }
                    } catch (err) {
                      alert('❌ Error: ' + err.message);
                    } finally {
                      loading = false;
                    }
                  }}
                  disabled={!username || loading}
                >
                  {loading ? '⏳ Resetting...' : '🔄 Reset My Password'}
                </button>
                <p class="text-xs text-yellow-700">
                  If you're having login issues, try resetting your password to the default "pass123"
                </p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {:else}
    <!-- Teacher Dashboard -->
    <div class="min-h-screen">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center py-6">
            <div class="flex items-center">
              <div class="text-3xl mr-3">👨🏫</div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Morning Quiz</h1>
                <p class="text-sm text-gray-600">Teacher Dashboard</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <!-- Notifications -->
              <div class="relative">
                <button 
                  class="relative p-2 text-gray-600 hover:text-gray-800 transition-colors"
                  on:click={() => activeTab = 'notifications'}
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path>
                  </svg>
                  {#if unreadCount > 0}
                    <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
                      {unreadCount}
                    </span>
                  {/if}
                </button>
              </div>
              
              <button 
                class="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg transition-colors flex items-center"
                on:click={loadData}
                disabled={loading}
              >
                {loading ? '🔄' : '↻'} Refresh
              </button>
              
              <div class="text-right">
                <div class="text-sm font-medium text-gray-900">{$user.full_name || $user.username}</div>
                <div class="text-xs text-gray-500">Teacher</div>
              </div>
              <button 
                class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
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
            <div class="flex">
              <div class="text-red-400">⚠️</div>
              <div class="ml-3 text-red-700">{error}</div>
            </div>
          </div>
        {/if}

        <!-- Navigation Tabs -->
        <div class="flex space-x-1 mb-8 bg-white p-2 rounded-xl shadow-sm">
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'dashboard' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'dashboard'}
          >
            📊 Dashboard
          </button>
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'notifications' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'notifications'}
          >
            🔔 Notifications {#if unreadCount > 0}<span class="ml-1 bg-red-500 text-white text-xs px-2 py-1 rounded-full">{unreadCount}</span>{/if}
          </button>
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'questions' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'questions'}
          >
            📝 My Questions
          </button>
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'create-quiz' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'create-quiz'}
          >
            🎯 Create Quiz
          </button>
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'quizzes' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'quizzes'}
          >
            🎮 My Quizzes
          </button>
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'courses' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => { activeTab = 'courses'; loadMyCourses(); }}
          >
            📚 My Courses
          </button>
          <a
            href="/teacher/question-types"
            class="flex-1 px-6 py-3 rounded-lg font-medium text-center transition-all text-gray-600 hover:text-gray-800 hover:bg-gray-50 no-underline flex items-center justify-center"
          >
            🎨 Question Types
          </a>
          <a
            href="/teacher/reviews"
            class="flex-1 px-6 py-3 rounded-lg font-medium text-center transition-all text-gray-600 hover:text-gray-800 hover:bg-gray-50 no-underline flex items-center justify-center"
          >
            📋 Review
          </a>
        </div>

        <!-- Notifications Tab -->
        {#if activeTab === 'notifications'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-2xl font-bold mb-6 flex items-center">
              <span class="text-3xl mr-3">🔔</span>
              Notifications
            </h2>
            
            {#if notifications.length === 0}
              <div class="text-center py-12">
                <div class="text-6xl mb-4">📭</div>
                <p class="text-gray-600">No notifications yet</p>
              </div>
            {:else}
              <div class="space-y-4">
                {#each notifications as notification}
                  <div class="border border-gray-200 rounded-lg p-4 {notification.is_read ? 'bg-gray-50' : 'bg-blue-50 border-blue-200'} hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start">
                      <div class="flex-1">
                        <div class="flex items-center mb-2">
                          <span class="text-lg mr-2">
                            {#if notification.type === 'lesson_assignment'}
                              📚
                            {:else if notification.type === 'quiz_available'}
                              🎯
                            {:else if notification.type === 'quiz_submission'}
                              📊
                            {:else if notification.type === 'lesson_removed'}
                              🚫
                            {:else}
                              ℹ️
                            {/if}
                          </span>
                          <h3 class="font-semibold text-gray-900 mr-3">{notification.title}</h3>
                          <span class="px-2 py-1 text-xs rounded-full {notification.type === 'lesson_assignment' ? 'bg-green-100 text-green-800' : notification.type === 'quiz_available' ? 'bg-blue-100 text-blue-800' : notification.type === 'quiz_submission' ? 'bg-purple-100 text-purple-800' : notification.type === 'lesson_removed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}">
                            {notification.type.replace('_', ' ')}
                          </span>
                          {#if !notification.is_read}
                            <span class="ml-2 w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                          {/if}
                        </div>
                        <p class="text-gray-600 mb-2">{notification.message}</p>
                        <p class="text-xs text-gray-400">
                          {new Date(notification.created_at).toLocaleString()}
                        </p>
                      </div>
                      {#if !notification.is_read}
                        <button 
                          class="text-blue-600 hover:text-blue-800 text-sm px-3 py-1 rounded border border-blue-300 hover:bg-blue-50 transition-colors"
                          on:click={() => markNotificationRead(notification.id)}
                        >
                          Mark Read
                        </button>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Dashboard Tab -->
        {#if activeTab === 'dashboard'}
         

          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div class="flex items-center">
                <div class="text-3xl mr-4">📝</div>
                <div>
                  <div class="text-2xl font-bold text-green-600">{questions.length}</div>
                  <div class="text-gray-600 text-sm">My Questions</div>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div class="flex items-center">
                <div class="text-3xl mr-4">🎯</div>
                <div>
                  <div class="text-2xl font-bold text-blue-600">{quizzes.length}</div>
                  <div class="text-gray-600 text-sm">My Quizzes</div>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div class="flex items-center">
                <div class="text-3xl mr-4">✅</div>
                <div>
                  <div class="text-2xl font-bold text-purple-600">{quizzes.filter(q => q.is_active).length}</div>
                  <div class="text-gray-600 text-sm">Active Quizzes</div>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div class="flex items-center">
                <div class="text-3xl mr-4">📢</div>
                <div>
                  <div class="text-2xl font-bold text-orange-600">{announcements.length}</div>
                  <div class="text-gray-600 text-sm">Announcements</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Weekly Timetable -->
          {#if schedules.filter(s => s.file_data).length > 0}
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-sm border-2 border-blue-200 p-6 mb-6">
              <h2 class="text-xl font-bold mb-4 flex items-center">
                <span class="text-2xl mr-2">📅</span>
                Weekly Timetable
              </h2>
              <div class="space-y-3">
                {#each schedules.filter(s => s.file_data).slice(0, 3) as schedule}
                  <div class="bg-white p-4 rounded-lg shadow-sm flex justify-between items-center">
                    <div>
                      <div class="font-semibold text-gray-900">{schedule.title}</div>
                      <div class="text-sm text-gray-600">
                        {schedule.description || 'Morning Quiz Schedule'}
                      </div>
                      <div class="text-xs text-gray-500 mt-1">
                        Uploaded: {new Date(schedule.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <a 
                      href="{api.baseURL}/schedules/{schedule.id}/download"
                      target="_blank"
                      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                    >
                      📥 Download
                    </a>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Recent Quizzes -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-xl font-bold mb-6 flex items-center">
                <span class="text-2xl mr-2">🎯</span>
                Recent Quizzes
              </h2>
              {#if quizzes.length === 0}
                <div class="text-center py-8">
                  <div class="text-4xl mb-2">🎯</div>
                  <p class="text-gray-600 mb-4">No quizzes created yet</p>
                  <button 
                    class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    on:click={() => activeTab = 'create-quiz'}
                  >
                    Create Your First Quiz
                  </button>
                </div>
              {:else}
                <div class="space-y-4">
                  {#each quizzes.slice(0, 3) as quiz}
                    <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div class="flex items-center">
                        <div class="text-2xl mr-4">{quiz.is_active ? '🟢' : '⚪'}</div>
                        <div>
                          <div class="font-semibold text-gray-900">{quiz.title}</div>
                          <div class="text-sm text-gray-600">
                            {quiz.department} - {quiz.level}
                          </div>
                        </div>
                      </div>
                      <button 
                        class="text-green-600 hover:text-green-800 text-sm font-medium"
                        on:click={() => viewResults(quiz.id)}
                      >
                        View Results →
                      </button>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- DOS Announcements -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-xl font-bold mb-6 flex items-center">
                <span class="text-2xl mr-2">📢</span>
                DOS Announcements
              </h2>
              {#if announcements.length === 0}
                <p class="text-gray-600">No announcements from DOS.</p>
              {:else}
                <div class="space-y-3">
                  {#each announcements.slice(0, 3) as announcement}
                    <div class="p-3 bg-gray-50 rounded-lg">
                      <div class="flex justify-between items-start mb-2">
                        <div class="font-semibold">{announcement.title}</div>
                        <span class="px-2 py-1 text-xs rounded-full {announcement.priority === 'urgent' ? 'bg-red-100 text-red-800' : announcement.priority === 'high' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}">
                          {announcement.priority}
                        </span>
                      </div>
                      <div class="text-sm text-gray-600">
                        {announcement.content.substring(0, 100)}...
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Advanced Question Builder Tab -->
        {#if activeTab === 'create-question'}
          <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl shadow-lg border border-blue-200 p-8">
            <div class="text-center mb-8">
              <h2 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                🚀 Advanced Question Builder
              </h2>
              <p class="text-gray-600">Create questions with AI assistance, smart templates, and bulk processing</p>
            </div>
            
            <!-- Quick Action Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <!-- Smart Upload Card -->
              <div class="bg-white rounded-xl p-6 shadow-md border border-blue-200 hover:shadow-lg transition-all cursor-pointer" on:click={() => showBulkUpload = !showBulkUpload}>
                <div class="text-center">
                  <div class="text-4xl mb-3">🤖</div>
                  <h3 class="font-bold text-gray-800 mb-2">AI Document Parser</h3>
                  <p class="text-sm text-gray-600 mb-3">Upload documents and let AI extract questions automatically</p>
                  <div class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">Smart • Fast • Accurate</div>
                </div>
              </div>
              
              <!-- Quick Templates Card -->
              <div class="bg-white rounded-xl p-6 shadow-md border border-green-200 hover:shadow-lg transition-all cursor-pointer" on:click={() => showTemplates = !showTemplates}>
                <div class="text-center">
                  <div class="text-4xl mb-3">📋</div>
                  <h3 class="font-bold text-gray-800 mb-2">Question Templates</h3>
                  <p class="text-sm text-gray-600 mb-3">Use pre-built templates for common question types</p>
                  <div class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-medium">Templates • Quick • Professional</div>
                </div>
              </div>
              
              <!-- Manual Builder Card -->
              <div class="bg-white rounded-xl p-6 shadow-md border border-purple-200 hover:shadow-lg transition-all cursor-pointer" on:click={() => showManualBuilder = !showManualBuilder}>
                <div class="text-center">
                  <div class="text-4xl mb-3">✏️</div>
                  <h3 class="font-bold text-gray-800 mb-2">Manual Builder</h3>
                  <p class="text-sm text-gray-600 mb-3">Create questions manually with advanced options</p>
                  <div class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-medium">Custom • Flexible • Detailed</div>
                </div>
              </div>
            </div>
            
            <!-- AI Document Parser Section -->
            {#if showBulkUpload}
              <div class="bg-white rounded-xl p-6 mb-8 border border-blue-200 shadow-md">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="text-xl font-bold text-blue-900 flex items-center">
                    <span class="text-2xl mr-2">🤖</span>
                    AI Document Parser
                  </h3>
                  <button class="text-gray-400 hover:text-gray-600" on:click={() => showBulkUpload = false}>✕</button>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div class="space-y-6">
                    <div class="border-2 border-dashed border-blue-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors bg-blue-50">
                      <input type="file" accept=".doc,.docx,.pdf,.txt" class="hidden" id="aiUpload" on:change={handleFileUpload}/>
                      <label for="aiUpload" class="cursor-pointer">
                        <div class="text-6xl mb-4">📎</div>
                        <h4 class="text-lg font-semibold text-blue-800 mb-2">Drop or Click to Upload</h4>
                        <p class="text-blue-600 mb-4">Supports: Word, PDF, Text files</p>
                        {#if selectedFile}
                          <div class="bg-green-100 border border-green-300 rounded-lg p-3 inline-block">
                            <p class="text-green-800 font-medium">📄 {selectedFile.name}</p>
                          </div>
                        {/if}
                      </label>
                    </div>
                    
                    <button 
                      class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:transform-none shadow-lg"
                      on:click={uploadQuestions}
                      disabled={!selectedFile || uploadingFile}
                    >
                      {uploadingFile ? '🔄 AI Processing Magic...' : '🚀 Extract Questions with AI'}
                    </button>
                  </div>
                  
                  <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
                    <h4 class="font-bold text-blue-900 mb-4 flex items-center">
                      <span class="text-xl mr-2">✨</span>
                      AI Magic Features
                    </h4>
                    <div class="space-y-4 text-sm">
                      <div class="flex items-start space-x-3">
                        <span class="text-green-500 text-lg">🎯</span>
                        <div>
                          <p class="font-semibold text-gray-800">Smart Type Detection</p>
                          <p class="text-gray-600">Automatically identifies MCQ, True/False, and Short Answer questions</p>
                        </div>
                      </div>
                      <div class="flex items-start space-x-3">
                        <span class="text-blue-500 text-lg">🔍</span>
                        <div>
                          <p class="font-semibold text-gray-800">Option Extraction</p>
                          <p class="text-gray-600">Extracts real option text from various formats (a), A., a:, etc.</p>
                        </div>
                      </div>
                      <div class="flex items-start space-x-3">
                        <span class="text-purple-500 text-lg">✅</span>
                        <div>
                          <p class="font-semibold text-gray-800">Answer Mapping</p>
                          <p class="text-gray-600">Maps letter answers to actual option text automatically</p>
                        </div>
                      </div>
                      <div class="flex items-start space-x-3">
                        <span class="text-orange-500 text-lg">⚡</span>
                        <div>
                          <p class="font-semibold text-gray-800">Bulk Processing</p>
                          <p class="text-gray-600">Process hundreds of questions in seconds</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            {/if}
            
            <!-- Question Templates Section -->
            {#if showTemplates}
              <div class="bg-white rounded-xl p-6 mb-8 border border-green-200 shadow-md">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="text-xl font-bold text-green-900 flex items-center">
                    <span class="text-2xl mr-2">📋</span>
                    Quick Templates
                  </h3>
                  <button class="text-gray-400 hover:text-gray-600" on:click={() => showTemplates = false}>✕</button>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="border border-blue-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer" on:click={() => useTemplate('mcq')}>
                    <div class="text-center">
                      <div class="text-3xl mb-2">🔘</div>
                      <h4 class="font-semibold text-gray-800 mb-2">Multiple Choice</h4>
                      <p class="text-xs text-gray-600 mb-3">Question with 4 options</p>
                      <div class="bg-blue-50 border border-blue-200 rounded p-2 text-xs text-left">
                        <p class="font-mono">What is...?</p>
                        <p class="font-mono text-gray-500">a) Option 1</p>
                        <p class="font-mono text-gray-500">b) Option 2</p>
                        <p class="font-mono text-gray-500">c) Option 3</p>
                        <p class="font-mono text-gray-500">d) Option 4</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="border border-green-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer" on:click={() => useTemplate('true_false')}>
                    <div class="text-center">
                      <div class="text-3xl mb-2">✅</div>
                      <h4 class="font-semibold text-gray-800 mb-2">True/False</h4>
                      <p class="text-xs text-gray-600 mb-3">Simple yes/no question</p>
                      <div class="bg-green-50 border border-green-200 rounded p-2 text-xs text-left">
                        <p class="font-mono">Statement is true?</p>
                        <p class="font-mono text-gray-500">□ True</p>
                        <p class="font-mono text-gray-500">□ False</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="border border-purple-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer" on:click={() => useTemplate('short_answer')}>
                    <div class="text-center">
                      <div class="text-3xl mb-2">📝</div>
                      <h4 class="font-semibold text-gray-800 mb-2">Short Answer</h4>
                      <p class="text-xs text-gray-600 mb-3">Open-ended response</p>
                      <div class="bg-purple-50 border border-purple-200 rounded p-2 text-xs text-left">
                        <p class="font-mono">Explain...</p>
                        <p class="font-mono text-gray-500">_____________</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            {/if}
            
            <!-- Manual Builder Section -->
            {#if showManualBuilder || questionForms.length > 0}
              <div class="bg-white rounded-xl p-6 border border-purple-200 shadow-md">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="text-xl font-bold text-purple-900 flex items-center">
                    <span class="text-2xl mr-2">✏️</span>
                    Manual Question Builder
                  </h3>
                  <div class="flex space-x-2">
                    <button class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm" on:click={addNewQuestionForm}>
                      ➕ Add Question
                    </button>
                    {#if showManualBuilder}
                      <button class="text-gray-400 hover:text-gray-600" on:click={() => showManualBuilder = false}>✕</button>
                    {/if}
                  </div>
                </div>
                
                {#if questionForms.length === 0}
                  <div class="text-center py-12">
                    <div class="text-6xl mb-4">📝</div>
                    <p class="text-gray-600 mb-4">No questions yet. Start building!</p>
                    <button class="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors" on:click={addNewQuestionForm}>
                      Create First Question
                    </button>
                  </div>
                {:else}
                  <div class="space-y-6">
                    {#each questionForms as form, index}
                      <div class="border border-gray-200 rounded-xl p-6 bg-gray-50 relative">
                        <div class="flex justify-between items-center mb-4">
                          <h4 class="text-lg font-semibold text-gray-800">Question {index + 1}</h4>
                          {#if questionForms.length > 1}
                            <button class="text-red-500 hover:text-red-700 text-xl" on:click={() => removeQuestionForm(index)}>🗑️</button>
                          {/if}
                        </div>
                        
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div class="space-y-4">
                            <div>
                              <label class="block text-sm font-semibold text-gray-700 mb-2">Question Text</label>
                              <textarea class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none h-24" bind:value={form.question_text} placeholder="Enter your question here..."></textarea>
                            </div>
                            
                            <div class="grid grid-cols-2 gap-4">
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Type</label>
                                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" bind:value={form.question_type}>
                                  <option value="mcq">Multiple Choice</option>
                                  <option value="true_false">True/False</option>
                                  <option value="short_answer">Short Answer</option>
                                </select>
                              </div>
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Points</label>
                                <input class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" type="number" bind:value={form.points} min="1" max="10"/>
                              </div>
                            </div>
                            
                            <div class="grid grid-cols-3 gap-4">
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Department</label>
                                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm" bind:value={form.department}>
                                  <option value="">Select</option>
                                  {#each departments as dept}<option value={dept}>{dept}</option>{/each}
                                </select>
                              </div>
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Level</label>
                                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm" bind:value={form.level}>
                                  <option value="">Select</option>
                                  {#each levels as level}<option value={level}>{level}</option>{/each}
                                </select>
                              </div>
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Lesson</label>
                                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm" bind:value={form.lesson_id}>
                                  <option value={null}>Select</option>
                                  {#each lessons.filter(lesson => lesson.department === form.department && lesson.level === form.level) as lesson}
                                    <option value={lesson.id}>{lesson.title}</option>
                                  {/each}
                                </select>
                              </div>
                            </div>
                          </div>
                          
                          <div class="space-y-4">
                            {#if form.question_type === 'mcq'}
                              <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Options</label>
                                <div class="space-y-2">
                                  {#each form.options as option, optIndex}
                                    <input class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm" bind:value={form.options[optIndex]} placeholder="Option {optIndex + 1}"/>
                                  {/each}
                                </div>
                              </div>
                            {/if}
                            
                            <div>
                              <label class="block text-sm font-semibold text-gray-700 mb-2">Correct Answer</label>
                              {#if form.question_type === 'true_false'}
                                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" bind:value={form.correct_answer}>
                                  <option value="">Select</option>
                                  <option value="True">True</option>
                                  <option value="False">False</option>
                                </select>
                              {:else if form.question_type === 'mcq'}
                                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" bind:value={form.correct_answer}>
                                  <option value="">Select</option>
                                  {#each form.options as option}
                                    {#if option.trim()}<option value={option}>{option}</option>{/if}
                                  {/each}
                                </select>
                              {:else}
                                <input class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" bind:value={form.correct_answer} placeholder="Enter correct answer"/>
                              {/if}
                            </div>
                            
                            <div class="bg-gray-100 rounded-lg p-3">
                              <div class="text-xs text-gray-600 space-y-1">
                                <p><span class="font-semibold">Status:</span> {form.question_text.trim() && form.department && form.level && form.lesson_id && form.correct_answer.trim() ? '✅ Ready' : '⚠️ Incomplete'}</p>
                                <p><span class="font-semibold">Type:</span> {form.question_type.replace('_', ' ').toUpperCase()}</p>
                                <p><span class="font-semibold">Points:</span> {form.points}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    {/each}
                    
                    <div class="text-center pt-6">
                      <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200 inline-block">
                        <p class="text-sm text-purple-800 mb-4">
                          📊 <span class="font-bold">{questionForms.filter(q => q.question_text.trim() && q.department && q.level && q.lesson_id && q.correct_answer.trim()).length}</span> questions ready • 
                          <span class="font-bold">{questionForms.filter(q => !q.question_text.trim() || !q.department || !q.level || !q.lesson_id || !q.correct_answer.trim()).length}</span> incomplete
                        </p>
                        <button 
                          class="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:transform-none shadow-lg"
                          on:click={createBulkQuestions}
                          disabled={loading || questionForms.filter(q => q.question_text.trim() && q.department && q.level && q.lesson_id && q.correct_answer.trim()).length === 0}
                        >
                          {loading ? '⏳ Creating...' : '🚀 Create Questions'}
                        </button>
                      </div>
                    </div>
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Create Quiz Tab -->
        {#if activeTab === 'create-quiz'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
            <h2 class="text-2xl font-bold mb-8 flex items-center">
              <span class="text-3xl mr-3">🎯</span>
              Create New Quiz
            </h2>
            
            <form on:submit|preventDefault={createQuiz} class="space-y-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Quiz Title</label>
                <input
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  bind:value={newQuiz.title}
                  placeholder="Enter quiz title"
                  required
                />
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                <textarea
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none h-20"
                  bind:value={newQuiz.description}
                  placeholder="Enter quiz description"
                ></textarea>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Department</label>
                  <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent" bind:value={newQuiz.department} required>
                    <option value="">Select department</option>
                    {#each departments as dept}
                      <option value={dept}>{dept}</option>
                    {/each}
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Level</label>
                  <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent" bind:value={newQuiz.level} required>
                    <option value="">Select level</option>
                    {#each levels as level}
                      <option value={level}>{level}</option>
                    {/each}
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Scheduled Time</label>
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    type="datetime-local"
                    bind:value={newQuiz.scheduled_time}
                    required
                  />
                </div>
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Total Duration (minutes)</label>
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    type="number"
                    bind:value={newQuiz.duration_minutes}
                    min="1"
                    max="180"
                  />
                </div>
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">Time per Question (seconds)</label>
                  <input
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    type="number"
                    bind:value={newQuiz.question_time_seconds}
                    min="30"
                    max="300"
                    placeholder="60"
                  />
                  <p class="text-xs text-gray-500 mt-1">⏱️ Auto-submit when time expires</p>
                </div>
              </div>

              <div>
                <div class="flex justify-between items-center mb-4">
                  <label class="text-sm font-semibold text-gray-700">
                    📋 Question Selection ({newQuiz.question_ids.length} of {availableQuestions.length} selected)
                  </label>
                  <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500">Quick Actions:</span>
                    <button 
                      type="button"
                      class="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors disabled:opacity-50"
                      on:click={selectAllQuestions}
                      disabled={availableQuestions.length === 0 || allSelected}
                    >
                      ✅ All
                    </button>
                    <button 
                      type="button"
                      class="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full hover:bg-red-200 transition-colors disabled:opacity-50"
                      on:click={deselectAllQuestions}
                      disabled={noneSelected}
                    >
                      ❌ None
                    </button>
                  </div>
                </div>
                
                <!-- Question Type Filters -->
                {#if availableQuestions.length > 0}
                  <div class="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                    <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                      <span class="text-lg mr-2">🎯</span>
                      Select by Question Type
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {#if mcqQuestions.length > 0}
                        <button 
                          type="button"
                          class="flex items-center justify-between p-3 bg-white rounded-lg border border-blue-200 hover:border-blue-400 hover:shadow-md transition-all"
                          on:click={() => selectQuestionsByType('mcq')}
                        >
                          <div class="flex items-center">
                            <span class="text-2xl mr-2">🔘</span>
                            <div class="text-left">
                              <div class="text-sm font-semibold text-gray-800">Multiple Choice</div>
                              <div class="text-xs text-gray-600">{mcqQuestions.length} questions</div>
                            </div>
                          </div>
                          <span class="text-blue-600 text-sm">+ Add All</span>
                        </button>
                      {/if}
                      
                      {#if tfQuestions.length > 0}
                        <button 
                          type="button"
                          class="flex items-center justify-between p-3 bg-white rounded-lg border border-green-200 hover:border-green-400 hover:shadow-md transition-all"
                          on:click={() => selectQuestionsByType('true_false')}
                        >
                          <div class="flex items-center">
                            <span class="text-2xl mr-2">✅</span>
                            <div class="text-left">
                              <div class="text-sm font-semibold text-gray-800">True/False</div>
                              <div class="text-xs text-gray-600">{tfQuestions.length} questions</div>
                            </div>
                          </div>
                          <span class="text-green-600 text-sm">+ Add All</span>
                        </button>
                      {/if}
                      
                      {#if saQuestions.length > 0}
                        <button 
                          type="button"
                          class="flex items-center justify-between p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-400 hover:shadow-md transition-all"
                          on:click={() => selectQuestionsByType('short_answer')}
                        >
                          <div class="flex items-center">
                            <span class="text-2xl mr-2">📝</span>
                            <div class="text-left">
                              <div class="text-sm font-semibold text-gray-800">Short Answer</div>
                              <div class="text-xs text-gray-600">{saQuestions.length} questions</div>
                            </div>
                          </div>
                          <span class="text-purple-600 text-sm">+ Add All</span>
                        </button>
                      {/if}
                    </div>
                  </div>
                {/if}
                
                <!-- Question List -->
                <div class="max-h-80 overflow-y-auto border border-gray-300 rounded-lg bg-white">
                  {#if questions.length === 0}
                    <div class="text-center py-12">
                      <div class="text-6xl mb-4">📝</div>
                      <p class="text-gray-600 mb-4">No questions available</p>
                      <button 
                        type="button"
                        class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
                        on:click={() => activeTab = 'create-question'}
                      >
                        Create Questions First →
                      </button>
                    </div>
                  {:else if availableQuestions.length === 0}
                    <div class="text-center py-12">
                      <div class="text-6xl mb-4">🎯</div>
                      <p class="text-gray-600 mb-2">No questions available for</p>
                      <p class="text-gray-800 font-semibold">{newQuiz.department} - {newQuiz.level}</p>
                      <button 
                        type="button"
                        class="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        on:click={() => activeTab = 'create-question'}
                      >
                        Create Questions for This Level →
                      </button>
                    </div>
                  {:else}
                    <div class="p-2">
                      {#each availableQuestions as question, index}
                        <label class="flex items-start p-4 hover:bg-gray-50 rounded-lg cursor-pointer transition-all border-b border-gray-100 last:border-b-0 {newQuiz.question_ids.includes(question.id) ? 'bg-green-50 border-green-200' : ''}">
                          <input
                            type="checkbox"
                            class="mt-1 mr-4 w-4 h-4 text-green-600 rounded focus:ring-green-500"
                            checked={newQuiz.question_ids.includes(question.id)}
                            on:change={() => toggleQuestionSelection(question.id)}
                          />
                          <div class="flex-1">
                            <div class="flex items-start justify-between mb-2">
                              <div class="font-medium text-gray-900 flex-1 mr-4">
                                <span class="text-sm text-gray-500 mr-2">Q{index + 1}.</span>
                                {question.question_text}
                              </div>
                              <div class="flex items-center space-x-2">
                                <span class="px-2 py-1 text-xs rounded-full font-medium {question.question_type === 'mcq' ? 'bg-blue-100 text-blue-800' : question.question_type === 'true_false' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}">
                                  {question.question_type === 'mcq' ? '🔘 MCQ' : question.question_type === 'true_false' ? '✅ T/F' : '📝 SA'}
                                </span>
                                <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full font-medium">
                                  {question.points} pts
                                </span>
                              </div>
                            </div>
                            {#if question.options && question.options.length > 0 && question.question_type === 'mcq'}
                              <div class="text-xs text-gray-600 mt-2">
                                <span class="font-semibold">Options:</span> 
                                {#if typeof question.options === 'string'}
                                  {JSON.parse(question.options).slice(0, 2).join(', ')}...
                                {:else}
                                  {question.options.slice(0, 2).join(', ')}...
                                {/if}
                              </div>
                            {/if}
                            <div class="text-xs text-green-600 mt-1">
                              <span class="font-semibold">Answer:</span> {question.correct_answer.length > 50 ? question.correct_answer.substring(0, 50) + '...' : question.correct_answer}
                            </div>
                          </div>
                        </label>
                      {/each}
                    </div>
                  {/if}
                </div>
                
                <!-- Selection Summary -->
                {#if newQuiz.question_ids.length > 0}
                  <div class="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-4">
                        <div class="text-sm font-semibold text-green-800">
                          📊 Selection Summary:
                        </div>
                        <div class="flex items-center space-x-3 text-xs">
                          <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                            🔘 {newQuiz.question_ids.filter(id => availableQuestions.find(q => q.id === id)?.question_type === 'mcq').length} MCQ
                          </span>
                          <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            ✅ {newQuiz.question_ids.filter(id => availableQuestions.find(q => q.id === id)?.question_type === 'true_false').length} T/F
                          </span>
                          <span class="px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                            📝 {newQuiz.question_ids.filter(id => availableQuestions.find(q => q.id === id)?.question_type === 'short_answer').length} SA
                          </span>
                        </div>
                      </div>
                      <div class="text-sm font-bold text-green-700">
                        Total: {newQuiz.question_ids.reduce((sum, id) => sum + (availableQuestions.find(q => q.id === id)?.points || 0), 0)} points
                      </div>
                    </div>
                  </div>
                {/if}
              </div>

              <div class="flex justify-end">
                <button 
                  class="bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:transform-none"
                  type="submit"
                  disabled={loading || newQuiz.question_ids.length === 0}
                >
                  {loading ? '⏳ Creating...' : '🚀 Create Quiz'}
                </button>
              </div>
            </form>
          </div>
        {/if}

        <!-- Questions Tab -->
        {#if activeTab === 'questions'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl font-bold flex items-center">
                <span class="text-3xl mr-3">📝</span>
                My Questions
              </h2>
              <button 
                class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                on:click={() => activeTab = 'create-question'}
              >
                ➕ Add Question
              </button>
            </div>
            
            <!-- Recently Added Questions -->
            {#if questions.length > 0}
              <div class="mb-8">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <span class="text-2xl mr-2">🆕</span>
                  Recently Added (Last 5)
                </h3>
                <div class="grid grid-cols-1 gap-3">
                  {#each questions.slice(0, 5) as question}
                    <div class="border border-green-200 rounded-lg p-4 bg-green-50 hover:shadow-md transition-shadow">
                      <div class="flex justify-between items-start mb-2">
                        <h4 class="font-medium text-gray-900 flex-1 mr-4 text-sm">{question.question_text}</h4>
                        <div class="flex items-center space-x-2">
                          <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full font-medium">
                            {question.question_type.replace('_', ' ').toUpperCase()}
                          </span>
                          <button 
                            class="text-blue-600 hover:text-blue-800 p-1 rounded transition-colors" 
                            on:click={() => editQuestion(question)}
                            title="Edit question"
                          >
                            ✏️
                          </button>
                          <button 
                            class="text-red-600 hover:text-red-800 p-1 rounded transition-colors" 
                            on:click={() => deleteQuestion(question.id)}
                            title="Delete question"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                      <div class="flex justify-between items-center text-xs text-gray-600">
                        <span>Answer: {question.correct_answer}</span>
                        <span>{question.department} - {question.level}</span>
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
            
            <!-- All Questions Section -->
            <div class="border-t pt-6">
              <div 
                class="flex items-center justify-between w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
                on:click={() => { showAllQuestions = !showAllQuestions; console.log('Clicked! showAllQuestions:', showAllQuestions); }}
                role="button"
                tabindex="0"
              >
                <div class="flex items-center">
                  <span class="text-2xl mr-3">📝</span>
                  <span class="text-lg font-semibold">All My Questions ({questions.length})</span>
                </div>
                <span class="text-xl">{showAllQuestions ? '▼' : '▶'}</span>
              </div>
              
              {#if showAllQuestions}
                <div class="mt-4">
                  {#if questions.length === 0}
                    <div class="text-center py-8">
                      <div class="text-4xl mb-2">📝</div>
                      <p class="text-gray-600 mb-4">No questions created yet</p>
                      <button 
                        class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                        on:click={() => activeTab = 'create-question'}
                      >
                        Create Your First Question
                      </button>
                    </div>
                  {:else}
                    <div class="space-y-4">
                      {#each questions as question}
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div class="flex justify-between items-start mb-3">
                            <h3 class="font-semibold text-gray-900 flex-1 mr-4">{question.question_text}</h3>
                            <div class="flex items-center space-x-2">
                              <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full font-medium">
                                {question.question_type.replace('_', ' ').toUpperCase()}
                              </span>
                              <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full font-medium">
                                {question.points} pts
                              </span>
                              <button 
                                class="text-blue-600 hover:text-blue-800 p-1 rounded transition-colors" 
                                on:click={() => editQuestion(question)}
                                title="Edit question"
                              >
                                ✏️
                              </button>
                              <button 
                                class="text-red-600 hover:text-red-800 p-1 rounded transition-colors" 
                                on:click={() => deleteQuestion(question.id)}
                                title="Delete question"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                          
                          {#if question.options && question.options.length > 0}
                            <div class="text-sm text-gray-600 mb-2">
                              <strong>Options:</strong> 
                              {#if typeof question.options === 'string'}
                                {JSON.parse(question.options).join(', ')}
                              {:else}
                                {question.options.join(', ')}
                              {/if}
                            </div>
                          {/if}
                          
                          <div class="flex justify-between items-center">
                            <div class="text-sm text-green-600">
                              <strong>Answer:</strong> {question.correct_answer}
                            </div>
                            <div class="text-xs text-gray-500">
                              {question.department} - {question.level}
                            </div>
                          </div>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Quizzes Tab -->
        {#if activeTab === 'quizzes'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl font-bold flex items-center">
                <span class="text-3xl mr-3">🎮</span>
                My Quizzes
              </h2>
              <button 
                class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                on:click={() => activeTab = 'create-quiz'}
              >
                🎯 Create Quiz
              </button>
            </div>
            
            {#if quizzes.length === 0}
              <div class="text-center py-12">
                <div class="text-6xl mb-4">🎯</div>
                <p class="text-gray-600 mb-4">No quizzes created yet</p>
                <button 
                  class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  on:click={() => activeTab = 'create-quiz'}
                >
                  Create Your First Quiz
                </button>
              </div>
            {:else}
              <div class="space-y-4">
                {#each quizzes as quiz}
                  <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start mb-4">
                      <div class="flex-1">
                        <div class="flex items-center mb-2">
                          <h3 class="text-lg font-semibold text-gray-900 mr-3">{quiz.title}</h3>
                          <span class="px-3 py-1 text-xs rounded-full font-medium {quiz.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                            {quiz.is_active ? '🟢 Active' : '⚪ Draft'}
                          </span>
                        </div>
                        <p class="text-gray-600 mb-2">{quiz.description}</p>
                        <div class="text-sm text-gray-500">
                          📅 {new Date(quiz.scheduled_time).toLocaleString()} | 
                          ⏱️ {quiz.duration_minutes} min | 
                          ⏰ {quiz.question_time_seconds || 60}s per question | 
                          🏢 {quiz.department} - {quiz.level}
                        </div>
                      </div>
                    </div>
                    
                    <div class="flex flex-wrap gap-2">
                      {#if !quiz.is_active}
                        <button 
                          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50"
                          on:click={() => activateQuiz(quiz.id)}
                          disabled={loading}
                        >
                          🟢 Activate
                        </button>
                        <button 
                          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50"
                          on:click={() => broadcastQuiz(quiz.id)}
                          disabled={loading}
                        >
                          📡 Broadcast Now
                        </button>
                      {:else}
                        <span class="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
                          ✅ Live & Broadcasting
                        </span>
                      {/if}
                      
                      <button 
                        class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium disabled:opacity-50"
                        on:click={() => viewResults(quiz.id)}
                        disabled={loading}
                      >
                        📈 View Results
                      </button>
                      
                      
                      
                     
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- My Courses Tab -->
        {#if activeTab === 'courses'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-2xl font-bold mb-6 flex items-center">
              <span class="text-3xl mr-3">📚</span>
              My Assigned Courses
            </h2>
            
            {#if myCourses.length === 0}
              <div class="text-center py-12">
                <div class="text-6xl mb-4">📚</div>
                <p class="text-gray-600">No courses assigned yet</p>
                <p class="text-sm text-gray-500 mt-2">Contact DOS to get lesson assignments</p>
              </div>
            {:else}
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each myCourses as course}
                  <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div class="flex items-start justify-between mb-4">
                      <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">{course.lesson.title}</h3>
                        <p class="text-sm text-gray-600 mb-2">{course.lesson.code}</p>
                        <p class="text-sm text-gray-700">{course.lesson.description}</p>
                      </div>
                      <span class="px-2 py-1 text-xs rounded-full font-medium {course.lesson.classification === 'Core' ? 'bg-red-100 text-red-800' : course.lesson.classification === 'Specific' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}">
                        {course.lesson.classification}
                      </span>
                    </div>
                    
                    <div class="border-t pt-4">
                      <div class="flex justify-between items-center text-sm text-gray-600 mb-2">
                        <span>🏢 {course.lesson.department}</span>
                        <span>🎓 {course.lesson.level}</span>
                      </div>
                      <div class="text-xs text-gray-500">
                        Assigned: {new Date(course.assigned_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Students Tab -->
        {#if activeTab === 'students'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-2xl font-bold mb-6 flex items-center">
              <span class="text-3xl mr-3">👥</span>
              Student Management
            </h2>
            
            <div class="space-y-6">
              <!-- Quick Add -->
              <div class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <span class="text-2xl mr-2">➕</span>
                  Quick Add Student
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <input type="text" placeholder="Full Name" bind:value={newStudentName} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500" />
                  <select bind:value={newStudentDept} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500">
                    <option value="">Department</option>
                    {#each departments as dept}<option value={dept}>{dept}</option>{/each}
                  </select>
                  <select bind:value={newStudentLevel} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500">
                    <option value="">Level</option>
                    {#each levels as level}<option value={level}>{level}</option>{/each}
                  </select>
                  <button class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 font-semibold" on:click={addSingleStudent} disabled={!newStudentName || !newStudentDept || !newStudentLevel || uploadingStudentFile}>
                    {uploadingStudentFile ? '⏳' : '➕ Add'}
                  </button>
                </div>
              </div>

              <!-- Bulk Upload -->
              <div class="bg-purple-50 rounded-lg p-6 border border-purple-200">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <span class="text-2xl mr-2">📋</span>
                  Bulk Upload from Document
                </h3>
                <div class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select bind:value={studentDepartment} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500">
                      <option value="">Department</option>
                      {#each departments as dept}<option value={dept}>{dept}</option>{/each}
                    </select>
                    <select bind:value={studentLevel} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500">
                      <option value="">Level</option>
                      {#each levels as level}<option value={level}>{level}</option>{/each}
                    </select>
                    <input type="file" accept=".doc,.docx,.pdf" on:change={handleStudentFileUpload} class="px-4 py-2 border border-gray-300 rounded-lg" />
                  </div>
                  <button class="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 font-semibold" on:click={uploadStudentFile} disabled={!canUpload || uploadingStudentFile}>
                    {uploadingStudentFile ? '⏳ Uploading...' : '🚀 Upload Students'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Results Tab -->
        {#if activeTab === 'results'}
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl font-bold flex items-center">
                <span class="text-3xl mr-3">📈</span>
                Quiz Results
              </h2>
              {#if results.length > 0}
                <div class="flex gap-2">
                  <button 
                    class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50 flex items-center"
                    on:click={async () => {
                      try {
                        loading = true;
                        if (currentQuizId) {
                          const blob = await api.downloadQuizStudentsResults(currentQuizId);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `Quiz_Results_Ranked.xlsx`;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          document.body.removeChild(a);
                          alert('📊 Ranked student results downloaded successfully!');
                        }
                      } catch (err) {
                        error = 'Failed to download results: ' + err.message;
                      } finally {
                        loading = false;
                      }
                    }}
                    disabled={loading}
                  >
                    📊 Download Excel
                  </button>
                  <button 
                    class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium disabled:opacity-50 flex items-center"
                    on:click={async () => {
                      try {
                        loading = true;
                        if (currentQuizId) {
                          const blob = await api.exportQuizPDF(currentQuizId);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `Quiz_Results_Ranked.pdf`;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          document.body.removeChild(a);
                          alert('📄 Ranked student results downloaded successfully!');
                        }
                      } catch (err) {
                        error = 'Failed to download PDF: ' + err.message;
                      } finally {
                        loading = false;
                      }
                    }}
                    disabled={loading}
                  >
                    📄 Download PDF
                  </button>
                </div>
              {/if}
            </div>
            
            {#if results.length === 0}
              <div class="text-center py-12">
                <div class="text-6xl mb-4">📊</div>
                <p class="text-gray-600">No submissions yet for this quiz</p>
              </div>
            {:else}
              <div class="overflow-x-auto">
                <table class="w-full">
                  <thead>
                    <tr class="border-b border-gray-200">
                      <th class="text-left py-3 px-4 font-semibold text-gray-700">Rank</th>
                      <th class="text-left py-3 px-4 font-semibold text-gray-700">Student</th>
                      <th class="text-left py-3 px-4 font-semibold text-gray-700">Score</th>
                      <th class="text-left py-3 px-4 font-semibold text-gray-700">Percentage</th>
                      <th class="text-left py-3 px-4 font-semibold text-gray-700">Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each results as result, index}
                      <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-3 px-4">
                          <span class="font-bold text-lg {index === 0 ? 'text-yellow-600' : index === 1 ? 'text-gray-500' : index === 2 ? 'text-orange-600' : 'text-gray-700'}">
                            {index + 1}
                          </span>
                        </td>
                        <td class="py-3 px-4 font-medium">{result.full_name || result.username}</td>
                        <td class="py-3 px-4">
                          <span class="font-semibold">{result.score}</span>
                          <span class="text-gray-500">/{result.total_questions}</span>
                        </td>
                        <td class="py-3 px-4">
                          <span class="px-2 py-1 rounded-full text-sm font-medium {Math.round((result.score / result.total_questions) * 100) >= 80 ? 'bg-green-100 text-green-800' : Math.round((result.score / result.total_questions) * 100) >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
                            {Math.round((result.score / result.total_questions) * 100)}%
                          </span>
                        </td>
                        <td class="py-3 px-4 text-gray-600 text-sm">
                          {new Date(result.completed_at).toLocaleString()}
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Edit Question Modal -->
  {#if showEditModal && editingQuestion}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-2xl font-bold text-gray-900">Edit Question</h3>
            <button class="text-gray-400 hover:text-gray-600 text-2xl" on:click={cancelEdit}>×</button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Question Text</label>
              <textarea 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none h-24" 
                bind:value={editForm.question_text} 
                placeholder="Enter your question here..."
              ></textarea>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Type</label>
                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" bind:value={editForm.question_type}>
                  <option value="mcq">Multiple Choice</option>
                  <option value="true_false">True/False</option>
                  <option value="short_answer">Short Answer</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Points</label>
                <input class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" type="number" bind:value={editForm.points} min="1" max="10"/>
              </div>
            </div>
            
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Department</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={editForm.department}>
                  <option value="">Select</option>
                  {#each departments as dept}<option value={dept}>{dept}</option>{/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Level</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={editForm.level}>
                  <option value="">Select</option>
                  {#each levels as level}<option value={level}>{level}</option>{/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Lesson</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={editForm.lesson_id}>
                  <option value={null}>Select</option>
                  {#each lessons.filter(lesson => lesson.department === editForm.department && lesson.level === editForm.level) as lesson}
                    <option value={lesson.id}>{lesson.title}</option>
                  {/each}
                </select>
              </div>
            </div>
            
            {#if editForm.question_type === 'mcq'}
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Options</label>
                <div class="space-y-2">
                  {#each editForm.options as option, optIndex}
                    <input class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={editForm.options[optIndex]} placeholder="Option {optIndex + 1}"/>
                  {/each}
                </div>
              </div>
            {/if}
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Correct Answer</label>
              {#if editForm.question_type === 'true_false'}
                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" bind:value={editForm.correct_answer}>
                  <option value="">Select</option>
                  <option value="True">True</option>
                  <option value="False">False</option>
                </select>
              {:else if editForm.question_type === 'mcq'}
                <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" bind:value={editForm.correct_answer}>
                  <option value="">Select</option>
                  {#each editForm.options as option}
                    {#if option.trim()}<option value={option}>{option}</option>{/if}
                  {/each}
                </select>
              {:else}
                <input class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" bind:value={editForm.correct_answer} placeholder="Enter correct answer"/>
              {/if}
            </div>
          </div>
          
          <div class="flex justify-end space-x-4 mt-6 pt-6 border-t">
            <button 
              class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              on:click={cancelEdit}
            >
              Cancel
            </button>
            <button 
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              on:click={saveEditedQuestion}
              disabled={loading || !editForm.question_text.trim() || !editForm.department || !editForm.level || !editForm.lesson_id || !editForm.correct_answer.trim()}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Notification Widget -->
  {#if showNotificationWidget && latestNotifications.length > 0}
    <div class="fixed top-4 right-4 z-50 bg-white rounded-xl shadow-2xl border border-gray-200 p-4 max-w-sm animate-bounce">
      <div class="flex justify-between items-start mb-3">
        <div class="flex items-center">
          <span class="text-2xl mr-2">🔔</span>
          <h3 class="font-bold text-gray-900">New Notifications</h3>
        </div>
        <button 
          class="text-gray-400 hover:text-gray-600 transition-colors"
          on:click={dismissWidget}
        >
          ✕
        </button>
      </div>
      
      <div class="space-y-2">
        {#each latestNotifications as notification}
          <div class="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-lg">
            <div class="flex items-start">
              <span class="text-lg mr-2">
                {#if notification.type === 'lesson_assignment'}
                  📚
                {:else if notification.type === 'quiz_available'}
                  🎯
                {:else if notification.type === 'quiz_submission'}
                  📊
                {:else if notification.type === 'lesson_removed'}
                  🚫
                {:else}
                  ℹ️
                {/if}
              </span>
              <div class="flex-1">
                <h4 class="font-semibold text-sm text-gray-900">{notification.title}</h4>
                <p class="text-xs text-gray-600 mt-1">{notification.message.substring(0, 80)}...</p>
              </div>
            </div>
          </div>
        {/each}
      </div>
      
      <button 
        class="w-full mt-3 bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        on:click={() => { activeTab = 'notifications'; showNotificationWidget = false; }}
      >
        View All Notifications
      </button>
    </div>
  {/if}
</div>

<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
</style>