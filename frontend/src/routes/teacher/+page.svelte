<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores.js';
  import { api } from '$lib/api.js';

  let username = ''
  let password = ''
  let loading = false
  let error = ''
  let activeTab = 'dashboard'
  
  // Data
  let questions = []
  let quizzes = []
  let results = []
  let currentQuizId = null
  let schedules = []
  let announcements = []
  let lessons = []
  let notifications = []
  let unreadCount = 0
  let showNotificationWidget = false
  let notificationInterval
  let latestNotifications = []
  let myCourses = []
  let myClasses = []
  let showBulkUpload = false
  let showTemplates = false
  let showManualBuilder = false
  let selectedFile = null
  let uploadingFile = false
  let questionForms = []
  let bulkMode = false
  let studentUploadText = ''
  let uploadingStudents = false
  let showStudentFileUpload = false
  let selectedStudentFile = null
  let uploadingStudentFile = false
  let studentDepartment = ''
  let studentLevel = ''
  let newStudentName = ''
  let newStudentDept = ''
  let newStudentLevel = ''
  
  // Debug reactive statements
  $: console.log('studentDepartment:', studentDepartment);
  $: console.log('studentLevel:', studentLevel);
  $: console.log('selectedStudentFile:', selectedStudentFile);
  $: canUpload = studentDepartment && studentLevel && selectedStudentFile;
  let editingQuestion = null
  let showEditModal = false
  let showAllQuestions = false
  let editForm = {
    question_text: '',
    question_type: 'mcq',
    options: ['', '', '', ''],
    correct_answer: '',
    points: 1,
    department: '',
    level: '',
    lesson_id: null,
    // Advanced question type fields
    blanks: [],
    pairs: [],
    items_to_order: [],
    scale_min: 1,
    scale_max: 10,
    programming_language: 'python',
    expected_output: '',
    grid_rows: '',
    grid_columns: ''
  }
  
  // Question types - All 13 Advanced Types
  const questionTypes = {
    mcq: 'Multiple Choice',
    true_false: 'True/False',
    short_answer: 'Short Answer',
    essay: 'Essay Question',
    multiple_select: 'Multiple Select',
    dropdown_select: 'Dropdown Select',
    fill_in_blanks: 'Fill in the Blanks',
    matching_pairs: 'Matching Pairs',
    drag_drop_ordering: 'Drag & Drop Ordering',
    linear_scale: 'Linear Scale',
    code_writing: 'Code Writing',
    sql_query: 'SQL Query',
    multi_grid: 'Multi-Grid'
  };
  
  function initializeQuestionForms() {
    questionForms = []
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
      lesson_id: null,
      // Advanced question type fields
      blanks: [],
      pairs: [],
      items_to_order: [],
      scale_min: 1,
      scale_max: 10,
      programming_language: 'python',
      expected_output: '',
      grid_rows: '',
      grid_columns: ''
    }
    
    if (type === 'mcq') {
      template.question_text = 'What is the correct answer?'
      template.options = ['Option A', 'Option B', 'Option C', 'Option D']
    } else if (type === 'true_false') {
      template.question_text = 'This statement is true. True or False?'
    } else if (type === 'short_answer') {
      template.question_text = 'Explain or define the following:'
      template.correct_answer = 'Sample answer'
    } else if (type === 'multiple_select') {
      template.question_text = 'Select all correct answers:'
      template.options = ['Option A', 'Option B', 'Option C', 'Option D']
    } else if (type === 'dropdown_select') {
      template.question_text = 'Select the correct option from dropdown:'
      template.options = ['Option A', 'Option B', 'Option C']
    } else if (type === 'fill_in_blanks') {
      template.question_text = 'The capital of France is _____ and it is located in _____.'
      template.correct_answer = 'Paris,Europe'
    } else if (type === 'matching_pairs') {
      template.question_text = 'Match the following items:'
      template.correct_answer = 'Python:Programming Language,HTML:Markup Language,MySQL:Database'
    } else if (type === 'drag_drop_ordering') {
      template.question_text = 'Arrange the following steps in correct order:'
      template.correct_answer = 'First Step,Second Step,Third Step,Final Step'
    } else if (type === 'linear_scale') {
      template.question_text = 'Rate this on a scale of 1-10:'
      template.correct_answer = '8'
    } else if (type === 'code_writing') {
      template.question_text = 'Write a Python function to calculate factorial:'
      template.correct_answer = 'def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)'
      template.programming_language = 'python'
    } else if (type === 'sql_query') {
      template.question_text = 'Write a SQL query to select all students with grade > 80:'
      template.correct_answer = 'SELECT * FROM students WHERE grade > 80;'
    } else if (type === 'multi_grid') {
      template.question_text = 'Rate each aspect:'
      template.grid_rows = 'User Interface\nPerformance\nDocumentation'
      template.grid_columns = 'Excellent\nGood\nFair\nPoor'
      template.correct_answer = 'User Interface:Excellent\nPerformance:Good\nDocumentation:Fair'
    }
    
    questionForms = [...questionForms, template]
    showTemplates = false
    showManualBuilder = true
  }
  
  onMount(() => {
    initializeQuestionForms()
  })
  
  const departments = [
    'Software Development',
    'Computer System and Architecture', 
    'Land Surveying',
    'Building Construction'
  ]
  
  const levels = ['Level 3', 'Level 4', 'Level 5']
  
  let newQuiz = {
    title: '',
    description: '',
    scheduled_time: '',
    duration_minutes: 30,
    question_time_seconds: 60,
    department: '',
    level: '',
    question_ids: []
  }

  $: isLoggedIn = $user !== null && $user.role === 'teacher'

  let refreshInterval
  
  onMount(async () => {
    console.log('Teacher page mounted')
    
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')
    
    if (storedUser && storedToken) {
      try {
        const userData = JSON.parse(storedUser)
        console.log('Found stored user:', userData)
        
        if (userData.role === 'teacher') {
          // Test token validity
          const testResponse = await api.testAuth()
          
          if (testResponse) {
            console.log('Token is valid, logging in user')
            api.setToken(storedToken)
            user.login(userData)
            await loadData()
            startAutoRefresh()
          } else {
            console.log('Token expired, clearing storage')
            localStorage.removeItem('user')
            localStorage.removeItem('token')
          }
        }
      } catch (err) {
        console.log('Session validation failed:', err.message)
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
    
    // Start notification polling
    startNotificationPolling()
    
    // Cleanup on component destroy
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
      if (notificationInterval) {
        clearInterval(notificationInterval)
      }
    }
  })
  
  function startAutoRefresh() {
    // Auto-refresh data every 30 seconds
    refreshInterval = setInterval(async () => {
      if (isLoggedIn) {
        await loadData()
      }
    }, 30000)
  }

  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password'
      return
    }

    loading = true
    error = ''

    try {
      console.log('Attempting login for:', username)
      
      const result = await api.login(username, password)
      console.log('Login successful:', result.user)
      
      if (result.user.role !== 'teacher') {
        throw new Error('Teacher access required')
      }
      
      // Store authentication data
      localStorage.setItem('user', JSON.stringify(result.user))
      localStorage.setItem('token', result.access_token)
      
      // Update stores
      api.setToken(result.access_token)
      user.login(result.user)
      
      // Load data and start refresh
      await loadData()
      startAutoRefresh()
      
      username = ''
      password = ''
      
      console.log('Login process completed successfully')
    } catch (err) {
      error = err.message
      console.error('❌ Login error:', err)
    } finally {
      loading = false
    }
  }

  async function loadData() {
    try {
      loading = true
      error = ''
      
      const token = localStorage.getItem('token')
      if (!token) {
        console.log('No token found, skipping data load')
        return
      }
      
      // Use API client methods instead of direct fetch
      const [questionsData, quizzesData, schedulesData, announcementsData, lessonsData, notificationsData] = await Promise.all([
        api.getQuestions().catch(() => []),
        api.getQuizzes().catch(() => []),
        api.getSchedules().catch(() => []),
        api.getAnnouncements().catch(() => []),
        api.getLessons().catch(() => []),
        api.getNotifications().catch(() => [])
      ])
      
      questions = [...questionsData]
      quizzes = [...quizzesData]
      schedules = [...schedulesData]
      announcements = [...announcementsData]
      lessons = [...lessonsData]
      notifications = [...notificationsData]
      unreadCount = notifications.filter(n => !n.is_read).length
      
      console.log('Data loaded:', { questions: questions.length, quizzes: quizzes.length, lessons: lessons.length })
      
      // Skip loading classes to avoid auth errors
      myClasses = []
    } catch (err) {
      console.error('Load data error:', err)
    } finally {
      loading = false
    }
  }

  function handleLogout() {
    if (notificationInterval) {
      clearInterval(notificationInterval)
    }
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }
    
    api.clearToken()
    user.logout()
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    
    username = ''
    password = ''
    error = ''
    
    questions = []
    quizzes = []
    results = []
    schedules = []
    announcements = []
    lessons = []
    notifications = []
    unreadCount = 0
  }

  function startNotificationPolling() {
    if (notificationInterval) clearInterval(notificationInterval)
    
    notificationInterval = setInterval(async () => {
      if (isLoggedIn) {
        try {
          const newNotifications = await api.getNotifications()
          const newUnreadCount = newNotifications.filter(n => !n.is_read).length
          
          // Show widget if new notifications arrived
          if (newUnreadCount > unreadCount && newUnreadCount > 0) {
            latestNotifications = newNotifications.filter(n => !n.is_read).slice(0, 3)
            showNotificationWidget = true
            setTimeout(() => {
              showNotificationWidget = false
            }, 5000)
          }
          
          notifications = newNotifications
          unreadCount = newUnreadCount
        } catch (err) {
          console.error('Notification polling error:', err)
        }
      }
    }, 1000) // Increased frequency to 1 second for better real-time feel
  }

  function dismissWidget() {
    showNotificationWidget = false
  }

  async function loadMyCourses() {
    try {
      myCourses = await api.getMyCourses()
    } catch (err) {
      error = 'Failed to load courses: ' + err.message
    }
  }

  async function loadMyClasses() {
    try {
      myClasses = await api.getMyClasses()
      console.log('Loaded classes:', myClasses)
    } catch (err) {
      console.error('Failed to load classes:', err)
      myClasses = []
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
      lesson_id: null,
      // Advanced question type fields
      blanks: [],
      pairs: [],
      items_to_order: [],
      scale_min: 1,
      scale_max: 10,
      programming_language: 'python',
      expected_output: '',
      grid_rows: '',
      grid_columns: ''
    }]
  }

  function removeQuestionForm(index) {
    if (questionForms.length > 1) {
      questionForms = questionForms.filter((_, i) => i !== index)
    }
  }

  function handleFileUpload(event) {
    selectedFile = event.target.files[0]
  }
  async function uploadQuestions() {
    if (!selectedFile) return
    
    uploadingFile = true
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      const apiBase = api.baseURL
      const response = await fetch(`${apiBase}/upload-questions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }
      
      const result = await response.json()
      
      if (!result.questions || result.questions.length === 0) {
        throw new Error('No questions found in the document. Please check the format.')
      }
      
      // Process and populate forms with parsed questions
      questionForms = result.questions.slice(0, 20).map((questionObj, index) => {
        let formattedOptions = ['', '', '', '']
        
        // Handle different option formats
        if (questionObj.options && Array.isArray(questionObj.options)) {
          if (questionObj.options.length > 0) {
            // Use extracted options and ensure we have at least 4 slots for MCQ
            formattedOptions = [...questionObj.options]
            while (formattedOptions.length < 4) {
              formattedOptions.push('')
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
          lesson_id: null,
          // Advanced question type fields
          blanks: questionObj.blanks || [],
          pairs: questionObj.pairs || [],
          items_to_order: questionObj.items_to_order || [],
          scale_min: questionObj.scale_min || 1,
          scale_max: questionObj.scale_max || 10,
          programming_language: questionObj.programming_language || 'python',
          expected_output: questionObj.expected_output || '',
          grid_rows: questionObj.grid_rows || '',
          grid_columns: questionObj.grid_columns || ''
        }
      })
      
      // Show success with detailed breakdown
      const mcqCount = questionForms.filter(q => q.question_type === 'mcq').length
      const tfCount = questionForms.filter(q => q.question_type === 'true_false').length
      const saCount = questionForms.filter(q => q.question_type === 'short_answer').length
      const advancedCount = questionForms.filter(q => !['mcq', 'true_false', 'short_answer', 'essay'].includes(q.question_type)).length
      
      // Auto-show manual builder with extracted questions
      showBulkUpload = false
      showManualBuilder = true
      
      alert(`🤖 AI Extraction Complete!\\n\\n📊 Processed ${questionForms.length} questions:\\n• ${mcqCount} Multiple Choice\\n• ${tfCount} True/False\\n• ${saCount} Short Answer\\n• ${advancedCount} Advanced Types\\n\\n✅ All 13 question types supported\\n📝 Complete department, level & lesson to finish`)
      
      selectedFile = null
    } catch (err) {
      error = 'AI Processing failed: ' + err.message
      console.error('Document upload error:', err)
    } finally {
      uploadingFile = false
    }
  }

  async function createBulkQuestions() {
    try {
      loading = true
      error = ''
      
      // Filter and validate questions
      const validQuestions = questionForms.filter(q => {
        return q.question_text.trim() && 
               q.department && 
               q.level && 
               q.lesson_id && 
               q.correct_answer.trim()
      })
      
      if (validQuestions.length === 0) {
        error = 'No valid questions found. Please fill all required fields.'
        return
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
      }))
      
      const response = await fetch(`${api.baseURL}/questions/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ questions: questionsToCreate })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create questions')
      }
      
      const result = await response.json()
      alert(`✅ Successfully created ${result.count} questions!`)
      initializeQuestionForms()
      await loadData()
      activeTab = 'questions'
    } catch (err) {
      error = err.message || 'Failed to create questions'
      console.error('Bulk question creation error:', err)
    } finally {
      loading = false
    }
  }

  async function createQuestion(formIndex = null) {
    try {
      loading = true
      error = ''
      
      if (formIndex !== null) {
        // Create single question
        const form = questionForms[formIndex]
        await createSingleQuestion(form)
        alert('Question created successfully!')
      } else {
        // Create all questions
        let created = 0
        for (let i = 0; i < questionForms.length; i++) {
          try {
            await createSingleQuestion(questionForms[i])
            created++
          } catch (err) {
            console.error(`Failed to create question ${i + 1}:`, err)
          }
        }
        
        if (created > 0) {
          alert(`Successfully created ${created} out of ${questionForms.length} questions!`)
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
          }]
          activeTab = 'questions'
        }
      }
      
      await loadData()
    } catch (err) {
      error = err.message || 'Failed to create question'
      console.error('Create question error:', err)
    } finally {
      loading = false
    }
  }

  async function createSingleQuestion(questionData) {
    // Validate form
    if (!questionData.question_text.trim()) {
      throw new Error('Question text is required')
    }
    if (!questionData.department) {
      throw new Error('Department is required')
    }
    if (!questionData.level) {
      throw new Error('Level is required')
    }
    if (!questionData.correct_answer.trim()) {
      throw new Error('Correct answer is required')
    }
    if (!questionData.lesson_id) {
      throw new Error('Lesson selection is required')
    }
    
    // Validate options for MCQ and related types
    if (['mcq', 'multiple_select', 'dropdown_select'].includes(questionData.question_type)) {
      const validOptions = questionData.options.filter(opt => opt.trim())
      if (validOptions.length < 2) {
        throw new Error('At least 2 options are required for this question type')
      }
      if (questionData.question_type === 'mcq' && !validOptions.includes(questionData.correct_answer)) {
        throw new Error('Correct answer must be one of the provided options')
      }
    }
    
    const payload = {
      question_text: questionData.question_text.trim(),
      question_type: questionData.question_type,
      options: ['short_answer', 'essay', 'fill_in_blanks', 'matching_pairs', 'drag_drop_ordering', 'linear_scale', 'code_writing', 'sql_query', 'multi_grid'].includes(questionData.question_type) ? [] : questionData.options.filter(opt => opt.trim()),
      correct_answer: questionData.correct_answer.trim(),
      points: parseInt(questionData.points) || 1,
      department: questionData.department,
      level: questionData.level,
      lesson_id: parseInt(questionData.lesson_id),
      // Advanced question type fields
      blanks: questionData.blanks || [],
      pairs: questionData.pairs || [],
      items_to_order: questionData.items_to_order || [],
      scale_min: questionData.scale_min || 1,
      scale_max: questionData.scale_max || 10,
      programming_language: questionData.programming_language || 'python',
      expected_output: questionData.expected_output || '',
      grid_rows: questionData.grid_rows || '',
      grid_columns: questionData.grid_columns || ''
    }
    
    const token = localStorage.getItem('token')
    const response = await fetch(`${api.baseURL}/questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to create question')
    }
    
    return await response.json()
  }
  async function createQuiz() {
    try {
      loading = true
      error = ''
      
      // Validate form first
      if (!newQuiz.title.trim()) {
        throw new Error('Quiz title is required')
      }
      if (!newQuiz.department) {
        throw new Error('Department is required')
      }
      if (!newQuiz.level) {
        throw new Error('Level is required')
      }
      if (!newQuiz.scheduled_time) {
        throw new Error('Scheduled time is required')
      }
      if (newQuiz.question_ids.length === 0) {
        throw new Error('At least one question must be selected')
      }
      
      // Check authentication
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('Please login again - session expired')
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
      }
      
      console.log('Creating quiz with data:', quizData)
      
      // Direct fetch with better error handling
      const response = await fetch(`${api.baseURL}/quizzes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        body: JSON.stringify(quizData)
      })
      
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        let errorMessage = 'Failed to create quiz'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch (e) {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        
        if (response.status === 401 || response.status === 403) {
          errorMessage = 'Authentication failed. Please login again.'
          handleLogout()
        }
        
        throw new Error(errorMessage)
      }
      
      const result = await response.json()
      console.log('Quiz created successfully:', result)
      
      await loadData()
      
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
      }
      
      activeTab = 'quizzes'
      alert('✅ Quiz created successfully!')
    } catch (err) {
      error = err.message || 'Failed to create quiz'
      console.error('❌ Create quiz error:', err)
      alert('❌ Error: ' + error)
    } finally {
      loading = false
    }
  }

  async function activateQuiz(quizId) {
    try {
      loading = true
      error = ''
      
      const result = await api.activateQuiz(quizId)
      console.log('Quiz activated:', result)
      await loadData()
      alert('Quiz activated successfully!')
    } catch (err) {
      error = err.message || 'Failed to activate quiz'
      console.error('Activate quiz error:', err)
    } finally {
      loading = false
    }
  }

  async function viewResults(quizId) {
    try {
      loading = true
      error = ''
      
      results = await api.getQuizResults(quizId)
      currentQuizId = quizId
      activeTab = 'results'
    } catch (err) {
      error = err.message || 'Failed to load quiz results'
      console.error('View results error:', err)
      results = []
      currentQuizId = null
    } finally {
      loading = false
    }
  }

  async function broadcastQuiz(quizId) {
    try {
      loading = true
      error = ''
      
      const result = await api.broadcastQuiz(quizId)
      console.log('Quiz broadcasted:', result)
      await loadData()
      alert('Quiz broadcasted to all students immediately!')
    } catch (err) {
      error = err.message || 'Failed to broadcast quiz'
      console.error('Broadcast quiz error:', err)
    } finally {
      loading = false
    }
  }

  function toggleQuestionSelection(questionId) {
    const index = newQuiz.question_ids.indexOf(questionId)
    if (index > -1) {
      newQuiz.question_ids = newQuiz.question_ids.filter(id => id !== questionId)
    } else {
      newQuiz.question_ids = [...newQuiz.question_ids, questionId]
    }
  }

  function selectAllQuestions() {
    const availableQuestions = questions.filter(q => q.department === newQuiz.department && q.level === newQuiz.level)
    newQuiz.question_ids = availableQuestions.map(q => q.id)
  }

  function deselectAllQuestions() {
    newQuiz.question_ids = []
  }

  function selectQuestionsByType(type) {
    const questionsOfType = questions.filter(q => 
      q.department === newQuiz.department && 
      q.level === newQuiz.level && 
      q.question_type === type
    )
    const typeQuestionIds = questionsOfType.map(q => q.id)
    newQuiz.question_ids = [...new Set([...newQuiz.question_ids, ...typeQuestionIds])]
  }

  $: availableQuestions = questions.filter(q => q.department === newQuiz.department && q.level === newQuiz.level)
  $: allSelected = availableQuestions.length > 0 && availableQuestions.every(q => newQuiz.question_ids.includes(q.id))
  $: noneSelected = newQuiz.question_ids.length === 0
  $: mcqQuestions = availableQuestions.filter(q => q.question_type === 'mcq')
  $: tfQuestions = availableQuestions.filter(q => q.question_type === 'true_false')
  $: saQuestions = availableQuestions.filter(q => q.question_type === 'short_answer')

  async function exportResults(quizId, format) {
    try {
      loading = true
      error = ''
      
      let blob
      let filename
      
      if (format === 'pdf') {
        blob = await api.exportQuizPDF(quizId)
        filename = `quiz_${quizId}_results.pdf`
      } else {
        blob = await api.exportQuizExcel(quizId)
        filename = `quiz_${quizId}_results.xlsx`
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      alert(`${format.toUpperCase()} exported successfully!`)
    } catch (err) {
      error = err.message || `Failed to export ${format.toUpperCase()}`
      console.error('Export error:', err)
    } finally {
      loading = false
    }
  }

  async function markNotificationRead(notificationId) {
    try {
      await api.markNotificationRead(notificationId)
      await loadData()
    } catch (err) {
      error = err.message
    }
  }

  async function forwardResults(quizId) {
    try {
      await api.forwardQuizResults(quizId)
      alert('Quiz results forwarded to DOS successfully!')
    } catch (err) {
      error = err.message
    }
  }

  async function uploadStudents() {
    try {
      uploadingStudents = true
      error = ''
      
      if (!studentUploadText.trim()) {
        error = 'Please enter student data'
        return
      }
      
      // Parse student data from text
      const lines = studentUploadText.trim().split('\\n')
      const students = []
      
      for (const line of lines) {
        const parts = line.split(',').map(p => p.trim())
        if (parts.length >= 4) {
          students.push({
            username: parts[0],
            full_name: parts[1],
            department: parts[2],
            level: parts[3],
            password: parts[4] || 'student123'
          })
        }
      }
      
      if (students.length === 0) {
        error = 'No valid student data found. Please check the format.'
        return
      }
      
      const result = await api.uploadStudents(students)
      alert(result.message)
      studentUploadText = ''
    } catch (err) {
      error = err.message
    } finally {
      uploadingStudents = false
    }
  }

  function handleStudentFileUpload(event) {
    const file = event.target.files[0]
    if (file) {
      selectedStudentFile = file
      console.log('File selected:', file.name, 'Size:', file.size)
    } else {
      selectedStudentFile = null
    }
  }

  function getDeptCode(department) {
    const codes = {
      'Software Development': 'SWD',
      'Building Construction': 'BDC',
      'Computer System and Architecture': 'CSA',
      'Land Surveying': 'LSV'
    }
    return codes[department] || 'STU'
  }

  async function addSingleStudent() {
    if (!newStudentName || !newStudentDept || !newStudentLevel) return
    
    uploadingStudentFile = true
    try {
      const deptCode = getDeptCode(newStudentDept)
      const levelNum = newStudentLevel.replace('Level ', '')
      const timestamp = Date.now().toString().slice(-4)
      const username = `${deptCode}${levelNum}${timestamp}`
      const student = {
        username,
        full_name: newStudentName,
        department: newStudentDept,
        level: newStudentLevel,
        password: 'student123'
      }
      
      const response = await fetch(`${api.baseURL}/teacher/upload-students`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ students: [student] })
      })
      
      if (response.ok) {
        alert(`✅ Student added!\\nUsername: ${username}\\nPassword: student123`)
        newStudentName = ''
        newStudentDept = ''
        newStudentLevel = ''
      }
    } catch (err) {
      alert('❌ Failed to add student')
    } finally {
      uploadingStudentFile = false
    }
  }
  async function uploadStudentFile() {
    console.log('uploadStudentFile called')
    console.log('Department:', studentDepartment)
    console.log('Level:', studentLevel)
    console.log('File:', selectedStudentFile)
    
    if (!studentDepartment || !studentLevel) {
      alert('⚠️ Please select both department and level first')
      return
    }
    
    if (!selectedStudentFile) {
      alert('⚠️ Please select a document file')
      return
    }
    
    uploadingStudentFile = true
    error = ''
    
    try {
      console.log('Processing file:', selectedStudentFile.name)
      
      const formData = new FormData()
      formData.append('file', selectedStudentFile)
      
      console.log('Sending file to backend...')
      const response = await fetch(`${api.baseURL}/teacher/upload-students-file`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      })
      
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Upload failed:', errorText)
        throw new Error(`Upload failed: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('File processed, students found:', result.students?.length || 0)
      
      if (!result.students || result.students.length === 0) {
        throw new Error('No students found in the document')
      }
      
      // Assign department and level to all students with proper username format
      const deptCode = getDeptCode(studentDepartment)
      const levelNum = studentLevel.replace('Level ', '')
      const studentsToUpload = result.students.map((student, index) => {
        const seqNum = String(index + 1).padStart(3, '0')
        return {
          username: `${deptCode}${levelNum}${seqNum}`,
          full_name: student.full_name,
          department: studentDepartment,
          level: studentLevel,
          password: student.password || 'student123'
        }
      })
      
      console.log('Uploading', studentsToUpload.length, 'students to database...')
      
      const uploadResponse = await fetch(`${api.baseURL}/teacher/upload-students`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ students: studentsToUpload })
      })
      
      console.log('Upload response status:', uploadResponse.status)
      
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text()
        console.error('Database upload failed:', errorText)
        throw new Error(`Failed to save students: ${uploadResponse.status}`)
      }
      
      const uploadResult = await uploadResponse.json()
      console.log('Upload complete:', uploadResult)
      
      alert(`✅ Success!\\n\\n${uploadResult.message}\\n\\nUploaded ${studentsToUpload.length} students to:\\n${studentDepartment} - ${studentLevel}`)
      
      // Reset form
      selectedStudentFile = null
      studentDepartment = ''
      studentLevel = ''
      
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
      
    } catch (err) {
      console.error('Upload error:', err)
      error = err.message
      alert(`❌ Upload Failed\\n\\n${err.message}\\n\\nPlease check the file format and try again.`)
    } finally {
      uploadingStudentFile = false
    }
  }

  function editQuestion(question) {
    editingQuestion = question
    editForm = {
      question_text: question.question_text,
      question_type: question.question_type,
      options: question.options && question.options.length > 0 ? [...question.options] : ['', '', '', ''],
      correct_answer: question.correct_answer,
      points: question.points,
      department: question.department,
      level: question.level,
      lesson_id: question.lesson_id,
      // Advanced question type fields
      blanks: question.blanks || [],
      pairs: question.pairs || [],
      items_to_order: question.items_to_order || [],
      scale_min: question.scale_min || 1,
      scale_max: question.scale_max || 10,
      programming_language: question.programming_language || 'python',
      expected_output: question.expected_output || '',
      grid_rows: question.grid_rows || '',
      grid_columns: question.grid_columns || ''
    }
    showEditModal = true
  }

  async function saveEditedQuestion() {
    try {
      loading = true
      error = ''
      
      const questionData = {
        question_text: editForm.question_text.trim(),
        question_type: editForm.question_type,
        options: editForm.question_type === 'short_answer' ? [] : editForm.options.filter(opt => opt.trim()),
        correct_answer: editForm.correct_answer.trim(),
        points: parseInt(editForm.points) || 1,
        department: editForm.department,
        level: editForm.level,
        lesson_id: parseInt(editForm.lesson_id)
      }
      
      await api.updateQuestion(editingQuestion.id, questionData)
      await loadData()
      showEditModal = false
      editingQuestion = null
      alert('Question updated successfully!')
    } catch (err) {
      error = err.message || 'Failed to update question'
    } finally {
      loading = false
    }
  }

  async function deleteQuestion(questionId) {
    if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
      return
    }
    
    try {
      loading = true
      error = ''
      
      await api.deleteQuestion(questionId)
      await loadData()
      alert('Question deleted successfully!')
    } catch (err) {
      error = err.message || 'Failed to delete question'
      if (err.message.includes('used in a quiz')) {
        alert('Cannot delete this question because it is used in a quiz.')
      }
    } finally {
      loading = false
    }
  }

  function cancelEdit() {
    showEditModal = false
    editingQuestion = null
    editForm = {
      question_text: '',
      question_type: 'mcq',
      options: ['', '', '', ''],
      correct_answer: '',
      points: 1,
      department: '',
      level: '',
      lesson_id: null,
      // Advanced question type fields
      blanks: [],
      pairs: [],
      items_to_order: [],
      scale_min: 1,
      scale_max: 10,
      programming_language: 'python',
      expected_output: '',
      grid_rows: '',
      grid_columns: ''
    }
  }

</script>