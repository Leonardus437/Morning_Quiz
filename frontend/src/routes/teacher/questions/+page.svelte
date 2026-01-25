<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let token = '';
  let user = null;
  let questions = [];
  let lessons = [];
  let loading = false;
  let error = '';
  let success = '';

  // Question form
  let showQuestionForm = false;
  let editingQuestion = null;
  let questionForm = {
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
  };

  // Upload options
  let activeTab = 'questions';
  let showUploadModal = false;
  let uploadFile = null;
  let uploadType = 'text';
  let uploadDepartment = '';
  let uploadLevel = '';
  let uploadLessonId = null;
  
  // Question type descriptions and examples
  const questionTypeDetails = {
    mcq: {
      title: 'Multiple Choice',
      icon: '🔘',
      description: 'Students select ONE correct answer from multiple options',
      example: 'What is the capital of France?\nA) London\nB) Paris ✓\nC) Berlin\nD) Madrid',
      features: ['Radio button interface', 'Single correct answer', 'Multiple options (2-6)', 'Auto-grading']
    },
    true_false: {
      title: 'True/False',
      icon: '✅',
      description: 'Students choose between True or False for a statement',
      example: 'JavaScript was created in 1995.\n○ True ✓\n○ False',
      features: ['Simple binary choice', 'Quick to answer', 'Perfect for facts', 'Auto-grading']
    },
    short_answer: {
      title: 'Short Answer',
      icon: '📝',
      description: 'Students provide brief text responses',
      example: 'What is the main purpose of HTML?\nAnswer: To structure web content',
      features: ['Text input field', 'Flexible answers', 'Manual/AI grading', 'Open-ended']
    },
    essay: {
      title: 'Essay Question',
      icon: '📄',
      description: 'Students write detailed, long-form responses',
      example: 'Explain the importance of responsive web design in modern development.',
      features: ['Large text area', 'Detailed responses', 'Manual grading', 'Critical thinking']
    },
    multiple_select: {
      title: 'Multiple Select',
      icon: '☑️',
      description: 'Students can select MULTIPLE correct answers',
      example: 'Which are programming languages?\n☑️ Python ✓\n☑️ HTML\n☑️ JavaScript ✓\n☑️ CSS',
      features: ['Checkbox interface', 'Multiple correct answers', 'Partial credit scoring', 'Complex assessment']
    },
    dropdown_select: {
      title: 'Dropdown Select',
      icon: '📋',
      description: 'Students select from a clean dropdown menu',
      example: 'Select the correct data type:\n[Dropdown: String ✓, Integer, Boolean, Array]',
      features: ['Clean interface', 'Space-saving', 'Single selection', 'Professional look']
    },
    fill_in_blanks: {
      title: 'Fill in the Blanks',
      icon: '📝',
      description: 'Students fill in missing words or phrases',
      example: 'Python is a _____ language and HTML is a _____ language.\nAnswers: programming, markup',
      features: ['Individual input fields', 'Multiple blanks per question', 'Exact match grading', 'Interactive interface']
    },
    matching_pairs: {
      title: 'Matching Pairs',
      icon: '🔗',
      description: 'Students match items from two columns',
      example: 'Match programming languages:\nPython → Programming Language ✓\nHTML → Markup Language ✓\nMySQL → Database ✓',
      features: ['Dropdown selectors', 'Visual pairing', 'Multiple matches', 'Logical connections']
    },
    drag_drop_ordering: {
      title: 'Drag & Drop Ordering',
      icon: '📋',
      description: 'Students arrange items in correct sequence',
      example: 'Order the web development steps:\n1. Plan ↑↓\n2. Design ↑↓\n3. Code ↑↓\n4. Test ↑↓',
      features: ['Interactive reordering', 'Up/down buttons', 'Sequential logic', 'Process understanding']
    },
    linear_scale: {
      title: 'Linear Scale',
      icon: '📊',
      description: 'Students rate on a numerical scale (1-10)',
      example: 'Rate the importance of code documentation:\n1 ⓵ ⓶ ⓷ ⓸ ⓹ ⓺ ⓻ ⓼ ⓽ ⓾ 10',
      features: ['Clickable number buttons', '1-10 scale', 'Opinion assessment', 'Quantitative feedback']
    },
    code_writing: {
      title: 'Code Writing',
      icon: '💻',
      description: 'Students write actual code in various languages',
      example: 'Write a Python function to calculate factorial:\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)',
      features: ['Dark code editor', 'Syntax highlighting', 'Multiple languages', 'Programming assessment']
    },
    sql_query: {
      title: 'SQL Query',
      icon: '🗄️',
      description: 'Students write database queries',
      example: 'Select all students with grade > 80:\nSELECT * FROM students WHERE grade > 80;',
      features: ['SQL-specific editor', 'Database knowledge', 'Query validation', 'Practical skills']
    },
    multi_grid: {
      title: 'Multi-Grid (Matrix)',
      icon: '📊',
      description: 'Students rate multiple items across different criteria',
      example: 'Rate each aspect:\n┌─────────┬─────┬─────┬─────┐\n│ Quality │ ○   │ ○   │ ○   │\n│ Service │ ○   │ ○   │ ○   │\n└─────────┴─────┴─────┴─────┘',
      features: ['Matrix table interface', 'Multiple criteria', 'Comprehensive evaluation', 'Survey-style questions']
    }
  };

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

  const departments = ['Software Development', 'Computer System and Architecture', 'Land Surveying', 'Building Construction'];
  const levels = ['Level 3', 'Level 4', 'Level 5'];

  onMount(async () => {
    token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      goto('/login');
      return;
    }

    user = JSON.parse(userData);
    if (user.role !== 'teacher') {
      goto('/');
      return;
    }

    await loadLessons();
    await loadQuestions();
  });

  async function loadLessons() {
    try {
      const res = await fetch('http://localhost:8000/lessons', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        lessons = await res.json();
      }
    } catch (err) {
      console.error('Failed to load lessons:', err);
    }
  }

  async function loadQuestions() {
    loading = true;
    try {
      const res = await fetch('http://localhost:8000/questions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        questions = await res.json();
      } else {
        error = 'Failed to load questions';
      }
    } catch (err) {
      error = 'Network error';
    } finally {
      loading = false;
    }
  }

  function openQuestionForm(question = null) {
    if (question) {
      editingQuestion = question;
      questionForm = {
        question_text: question.question_text,
        question_type: question.question_type,
        options: question.options || ['', '', '', ''],
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
      };
    } else {
      editingQuestion = null;
      questionForm = {
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
      };
    }
    showQuestionForm = true;
  }

  async function saveQuestion() {
    loading = true;
    error = '';
    success = '';

    try {
      // Validate required fields
      if (!questionForm.question_text.trim()) {
        error = 'Question text is required';
        return;
      }
      if (!questionForm.department || !questionForm.level || !questionForm.lesson_id) {
        error = 'Please select department, level, and lesson';
        return;
      }
      if (!questionForm.correct_answer.trim()) {
        error = 'Correct answer is required';
        return;
      }

      const url = editingQuestion 
        ? `http://localhost:8000/questions/${editingQuestion.id}`
        : 'http://localhost:8000/questions';
      
      const method = editingQuestion ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(questionForm)
      });

      if (res.ok) {
        success = editingQuestion ? 'Question updated!' : 'Question created!';
        showQuestionForm = false;
        // Reset form
        questionForm = {
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
        };
        await loadQuestions();
        activeTab = 'questions';
      } else {
        const data = await res.json();
        error = data.detail || 'Failed to save question';
      }
    } catch (err) {
      error = 'Network error: ' + err.message;
    } finally {
      loading = false;
    }
  }

  async function deleteQuestion(id) {
    if (!confirm('Delete this question?')) return;

    try {
      const res = await fetch(`http://localhost:8000/questions/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        success = 'Question deleted!';
        await loadQuestions();
      } else {
        error = 'Failed to delete question';
      }
    } catch (err) {
      error = 'Network error';
    }
  }

  async function handleFileUpload() {
    if (!uploadFile || !uploadDepartment || !uploadLevel || !uploadLessonId) {
      error = 'Please fill all upload fields';
      return;
    }

    loading = true;
    error = '';
    success = '';

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('department', uploadDepartment);
      formData.append('level', uploadLevel);
      formData.append('lesson_id', uploadLessonId);

      // Use the text question upload endpoint
      const res = await fetch('http://localhost:8000/questions/upload-text', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        success = data.message || `Imported ${data.total} questions successfully!`;
        uploadFile = null;
        uploadDepartment = '';
        uploadLevel = '';
        uploadLessonId = null;
        await loadQuestions();
      } else {
        const data = await res.json();
        error = data.detail || 'Upload failed';
      }
    } catch (err) {
      error = 'Network error: ' + err.message;
    } finally {
      loading = false;
    }
  }

  function addOption() {
    questionForm.options = [...questionForm.options, ''];
  }

  function removeOption(index) {
    questionForm.options = questionForm.options.filter((_, i) => i !== index);
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900"> Question Bank</h1>
          <p class="text-gray-600 mt-1">Manage your quiz questions with multiple formats</p>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white rounded-2xl shadow-xl mb-6">
      <div class="flex border-b border-gray-200">
        <button 
          class="flex-1 px-6 py-4 text-center font-semibold transition-all {activeTab === 'questions' ? 'bg-blue-600 text-white border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'}"
          on:click={() => activeTab = 'questions'}
        >
           Questions
        </button>
        <button 
          class="flex-1 px-6 py-4 text-center font-semibold transition-all {activeTab === 'upload' ? 'bg-blue-600 text-white border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'}"
          on:click={() => activeTab = 'upload'}
        >
           Upload Questions
        </button>
        <button 
          class="flex-1 px-6 py-4 text-center font-semibold transition-all {activeTab === 'create' ? 'bg-blue-600 text-white border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'}"
          on:click={() => activeTab = 'create'}
        >
           Create Question
        </button>
      </div>
    </div>

    <!-- Alerts -->
    {#if error}
      <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
        <p class="text-red-800"> {error}</p>
      </div>
    {/if}

    {#if success}
      <div class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded-lg">
        <p class="text-green-800"> {success}</p>
      </div>
    {/if}

    <!-- Tab Content -->
    {#if activeTab === 'questions'}
      <!-- Questions List -->
      <div class="bg-white rounded-2xl shadow-xl p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">Your Questions ({questions.length})</h2>
          <button 
            on:click={() => activeTab = 'create'}
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all"
          >
             Create New
          </button>
        </div>
        
        {#if loading}
          <div class="text-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p class="text-gray-600 mt-4">Loading questions...</p>
          </div>
        {:else if questions.length === 0}
          <div class="text-center py-12">
            <div class="text-6xl mb-4"></div>
            <p class="text-gray-600 text-lg mb-4">No questions yet. Create your first question!</p>
            <div class="flex justify-center space-x-4">
              <button 
                on:click={() => activeTab = 'create'}
                class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all"
              >
                 Create Question
              </button>
              <button 
                on:click={() => activeTab = 'upload'}
                class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-all"
              >
                 Upload Questions
              </button>
            </div>
          </div>
        {:else}
          <div class="space-y-4">
            {#each questions as question}
              <div class="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center space-x-3 mb-2">
                      <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                        {questionTypes[question.question_type]}
                      </span>
                      <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                        {question.points} {question.points === 1 ? 'point' : 'points'}
                      </span>
                    </div>
                    <p class="text-lg font-semibold text-gray-900 mb-2">{question.question_text}</p>
                    <div class="flex items-center space-x-4 text-sm text-gray-600">
                      <span> {question.department}</span>
                      <span> {question.level}</span>
                    </div>
                    
                    {#if question.options && question.options.length > 0}
                      <div class="mt-3 space-y-1">
                        {#each question.options as option, i}
                          <div class="flex items-center space-x-2">
                            <span class="text-gray-500">{String.fromCharCode(65 + i)}.</span>
                            <span class={option === question.correct_answer ? 'text-green-600 font-semibold' : 'text-gray-700'}>
                              {option}
                              {#if option === question.correct_answer}
                                <span class="ml-2"></span>
                              {/if}
                            </span>
                          </div>
                        {/each}
                      </div>
                    {/if}
                  </div>
                  
                  <div class="flex space-x-2 ml-4">
                    <button 
                      on:click={() => openQuestionForm(question)}
                      class="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 transition-all"
                    >
                       Edit
                    </button>
                    <button 
                      on:click={() => deleteQuestion(question.id)}
                      class="px-4 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200 transition-all"
                    >
                       Delete
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    {#if activeTab === 'upload'}
      <!-- Upload Questions Tab -->
      <div class="bg-white rounded-2xl shadow-xl p-6">
        <h2 class="text-2xl font-bold mb-6 flex items-center">
          <span class="text-3xl mr-3"></span>
          Upload Questions
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Upload Form -->
          <div class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h3 class="font-bold text-blue-900 mb-3"> Supported Format (Text File)</h3>
              <div class="text-sm text-blue-800 space-y-2">
                <p><strong>Example format:</strong></p>
                <div class="bg-white p-3 rounded border font-mono text-xs">
                  <div>1. What is the capital of France?</div>
                  <div>a) London</div>
                  <div>b) Paris</div>
                  <div>c) Berlin</div>
                  <div>d) Madrid</div>
                  <div>Answer: b</div>
                  <div></div>
                  <div>2. JavaScript was created in 1995. True</div>
                  <div></div>
                  <div>3. Fill in the blank: The capital of Kenya is _______.</div>
                  <div>Answer: Nairobi</div>
                </div>
              </div>
            </div>
            
            <div class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
              <input 
                type="file" 
                accept=".txt" 
                class="hidden" 
                id="questionFile" 
                on:change={(e) => uploadFile = e.target.files[0]}
              />
              <label for="questionFile" class="cursor-pointer">
                <div class="text-6xl mb-4"></div>
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Select Text File</h4>
                <p class="text-gray-600 mb-4">Upload .txt file with questions</p>
                {#if uploadFile}
                  <div class="bg-green-100 border border-green-300 rounded-lg p-3 inline-block">
                    <p class="text-green-800 font-medium"> {uploadFile.name}</p>
                  </div>
                {/if}
              </label>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold mb-2">Department</label>
                <select bind:value={uploadDepartment} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select Department</option>
                  {#each departments as dept}
                    <option value={dept}>{dept}</option>
                  {/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Level</label>
                <select bind:value={uploadLevel} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select Level</option>
                  {#each levels as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-semibold mb-2">Lesson</label>
              <select bind:value={uploadLessonId} class="w-full px-4 py-3 border rounded-xl">
                <option value={null}>Select Lesson</option>
                {#if uploadDepartment && uploadLevel}
                  {#each lessons.filter(l => l.department === uploadDepartment && l.level === uploadLevel) as lesson}
                    <option value={lesson.id}>{lesson.title} ({lesson.code})</option>
                  {/each}
                {:else}
                  <option disabled>Select Department & Level first</option>
                {/if}
              </select>
            </div>
            
            <button 
              on:click={handleFileUpload}
              disabled={loading || !uploadFile || !uploadDepartment || !uploadLevel || !uploadLessonId}
              class="w-full bg-green-600 text-white py-4 px-6 rounded-xl hover:bg-green-700 disabled:opacity-50 transition-all font-semibold"
            >
              {loading ? ' Uploading...' : ' Upload Questions'}
            </button>
          </div>
          
          <!-- Instructions -->
          <div class="space-y-6">
            <div class="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
              <h3 class="font-bold text-green-900 mb-4 flex items-center">
                <span class="text-2xl mr-2"></span>
                Question Types Supported
              </h3>
              <div class="space-y-4 text-sm">
                <div class="flex items-start space-x-3">
                  <span class="text-blue-500 text-lg"></span>
                  <div>
                    <p class="font-semibold text-gray-800">Multiple Choice (MCQ)</p>
                    <p class="text-gray-600">Questions with options a), b), c), d)</p>
                  </div>
                </div>
                <div class="flex items-start space-x-3">
                  <span class="text-green-500 text-lg"></span>
                  <div>
                    <p class="font-semibold text-gray-800">True/False</p>
                    <p class="text-gray-600">Statements ending with "True" or "False"</p>
                  </div>
                </div>
                <div class="flex items-start space-x-3">
                  <span class="text-purple-500 text-lg"></span>
                  <div>
                    <p class="font-semibold text-gray-800">Short Answer</p>
                    <p class="text-gray-600">Fill in the blank or open-ended questions</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <h4 class="font-bold text-yellow-900 mb-3"> Important Notes</h4>
              <ul class="text-sm text-yellow-800 space-y-2">
                <li> Number each question (1., 2., 3., etc.)</li>
                <li> Use "Answer: " followed by the correct option letter or text</li>
                <li> For True/False, end the statement with "True" or "False"</li>
                <li> Leave blank lines between questions for better parsing</li>
                <li> Maximum file size: 5MB</li>
              </ul>
            </div>
            
            <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <h4 class="font-bold text-gray-900 mb-3"> Sample File</h4>
              <p class="text-sm text-gray-700 mb-2">You can use the sample file: <strong>ALL_QUESTION_TYPES_SAMPLE.txt</strong></p>
              <p class="text-xs text-gray-600">This file contains examples of all supported question types in the correct format.</p>
            </div>
          </div>
        </div>
      </div>
    {/if}

    {#if activeTab === 'create'}
      <!-- Create Question Tab -->
      <div class="bg-white rounded-2xl shadow-xl p-6">
        <h2 class="text-2xl font-bold mb-6 flex items-center">
          <span class="text-3xl mr-3"></span>
          Create New Question
        </h2>
        
        <div class="max-w-4xl mx-auto">
          <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-semibold mb-2">Question Type</label>
                <select bind:value={questionForm.question_type} class="w-full px-4 py-3 border rounded-xl">
                  {#each Object.entries(questionTypes) as [value, label]}
                    <option {value}>{label}</option>
                  {/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Points</label>
                <input 
                  type="number"
                  bind:value={questionForm.points}
                  min="1"
                  max="10"
                  class="w-full px-4 py-3 border rounded-xl"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold mb-2">Question Text</label>
              <textarea 
                bind:value={questionForm.question_text}
                rows="4"
                class="w-full px-4 py-3 border rounded-xl"
                placeholder="Enter your question..."
              ></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-semibold mb-2">Department</label>
                <select bind:value={questionForm.department} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select Department</option>
                  {#each departments as dept}
                    <option value={dept}>{dept}</option>
                  {/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Level</label>
                <select bind:value={questionForm.level} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select Level</option>
                  {#each levels as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Lesson</label>
                <select bind:value={questionForm.lesson_id} class="w-full px-4 py-3 border rounded-xl">
                  <option value={null}>Select Lesson</option>
                  {#if questionForm.department && questionForm.level}
                    {#each lessons.filter(l => l.department === questionForm.department && l.level === questionForm.level) as lesson}
                      <option value={lesson.id}>{lesson.title} ({lesson.code})</option>
                    {/each}
                  {:else}
                    <option disabled>Select Department & Level first</option>
                  {/if}
                </select>
              </div>
            </div>

            {#if questionForm.question_type === 'mcq'}
              <div>
                <label class="block text-sm font-semibold mb-2">Options</label>
                <div class="space-y-3">
                  {#each questionForm.options as option, i}
                    <div class="flex space-x-2">
                      <span class="px-3 py-2 bg-gray-100 rounded-lg font-semibold text-gray-700">
                        {String.fromCharCode(65 + i)}
                      </span>
                      <input 
                        bind:value={questionForm.options[i]}
                        class="flex-1 px-4 py-2 border rounded-lg"
                        placeholder={`Option ${String.fromCharCode(65 + i)}`}
                      />
                      {#if questionForm.options.length > 2}
                        <button 
                          on:click={() => removeOption(i)} 
                          class="px-3 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200 transition-all"
                        >
                          🗑️
                        </button>
                      {/if}
                    </div>
                  {/each}
                  <button 
                    on:click={addOption} 
                    class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-all"
                  >
                    ➕ Add Option
                  </button>
                </div>
              </div>
            {:else if questionForm.question_type === 'multiple_select'}
              <div>
                <label class="block text-sm font-semibold mb-2">Options (Check all correct answers)</label>
                <div class="space-y-3">
                  {#each questionForm.options as option, i}
                    <div class="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                      <input 
                        type="checkbox" 
                        value={option}
                        checked={questionForm.correct_answer.split(',').includes(option)}
                        on:change={(e) => {
                          let correctAnswers = questionForm.correct_answer ? questionForm.correct_answer.split(',').filter(a => a.trim()) : [];
                          if (e.target.checked) {
                            if (!correctAnswers.includes(option)) correctAnswers.push(option);
                          } else {
                            correctAnswers = correctAnswers.filter(a => a !== option);
                          }
                          questionForm.correct_answer = correctAnswers.join(',');
                        }}
                        class="w-4 h-4 text-blue-600"
                      />
                      <input 
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg" 
                        bind:value={questionForm.options[i]} 
                        placeholder="Option {i + 1}"
                      />
                      <span class="text-sm text-gray-500">← Check if correct</span>
                    </div>
                  {/each}
                  <button 
                    on:click={addOption} 
                    class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-all"
                  >
                    ➕ Add Option
                  </button>
                </div>
              </div>
            {:else if questionForm.question_type === 'dropdown_select'}
              <div>
                <label class="block text-sm font-semibold mb-2">Dropdown Options</label>
                <div class="space-y-3">
                  {#each questionForm.options as option, i}
                    <div class="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                      <input 
                        type="radio" 
                        name="correct_answer_dropdown" 
                        value={option} 
                        bind:group={questionForm.correct_answer}
                        class="w-4 h-4 text-blue-600"
                      />
                      <input 
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg" 
                        bind:value={questionForm.options[i]} 
                        placeholder="Option {i + 1}"
                      />
                      <span class="text-sm text-gray-500">← Click radio to mark as correct</span>
                    </div>
                  {/each}
                  <button 
                    on:click={addOption} 
                    class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-all"
                  >
                    ➕ Add Option
                  </button>
                </div>
              </div>
            {:else if questionForm.question_type === 'fill_in_blanks'}
              <div>
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <h4 class="font-semibold text-yellow-800 mb-2">💡 Fill-in-the-Blanks Template</h4>
                  <p class="text-sm text-yellow-700 mb-3">Use <code class="bg-yellow-200 px-1 rounded">_____</code> (5 underscores) for each blank in your question.</p>
                  <div class="bg-white border border-yellow-300 rounded p-3">
                    <p class="text-sm font-mono">Example: "The capital of France is _____ and it is located in _____."</p>
                  </div>
                </div>
                <label class="block text-sm font-semibold mb-2">Correct Answers (comma-separated, in order)</label>
                <input 
                  class="w-full px-4 py-3 border rounded-xl" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="Paris,Europe (comma-separated, in order)"
                />
                <p class="text-xs text-gray-500 mt-1">Enter answers separated by commas, in the same order as blanks appear in your question</p>
              </div>
            {:else if questionForm.question_type === 'matching_pairs'}
              <div>
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h4 class="font-semibold text-blue-800 mb-2">🔗 Matching Pairs Template</h4>
                  <p class="text-sm text-blue-700">Create pairs that students will match. Format: Left Item:Right Item</p>
                </div>
                <label class="block text-sm font-semibold mb-2">Correct Pairs (Left:Right format)</label>
                <textarea 
                  class="w-full px-4 py-3 border rounded-xl resize-none" 
                  rows="3" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="Python:Programming Language,HTML:Markup Language,MySQL:Database"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">Format: Item1:Match1,Item2:Match2,Item3:Match3</p>
              </div>
            {:else if questionForm.question_type === 'drag_drop_ordering'}
              <div>
                <label class="block text-sm font-semibold mb-2">Items in Correct Order (comma-separated)</label>
                <textarea 
                  class="w-full px-4 py-3 border rounded-xl resize-none" 
                  rows="4" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="First Step,Second Step,Third Step,Final Step"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">List items in the correct order, separated by commas</p>
              </div>
            {:else if questionForm.question_type === 'linear_scale'}
              <div>
                <label class="block text-sm font-semibold mb-2">Expected Rating (1-10)</label>
                <input 
                  class="w-full px-4 py-3 border rounded-xl" 
                  type="number" 
                  bind:value={questionForm.correct_answer} 
                  min="1" 
                  max="10" 
                  placeholder="Expected rating (1-10)"
                />
                <p class="text-xs text-gray-500 mt-1">Enter the expected or ideal rating for this question</p>
              </div>
            {:else if questionForm.question_type === 'code_writing'}
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-semibold mb-2">Programming Language</label>
                  <select class="w-full px-4 py-3 border rounded-xl" bind:value={questionForm.programming_language}>
                    <option value="python">Python</option>
                    <option value="c">C</option>
                    <option value="cpp">C++</option>
                    <option value="javascript">JavaScript</option>
                    <option value="html">HTML</option>
                    <option value="java">Java</option>
                    <option value="other">Other (Specify in question)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-semibold mb-2">Expected Code Solution</label>
                  <textarea 
                    class="w-full px-4 py-3 border rounded-xl resize-none font-mono" 
                    rows="6" 
                    bind:value={questionForm.correct_answer} 
                    placeholder={questionForm.programming_language === 'python' ? 'def function_name():\n    return result' : questionForm.programming_language === 'javascript' ? 'function functionName() {\n    return result;\n}' : 'Enter expected code solution'}
                  ></textarea>
                </div>
              </div>
            {:else if questionForm.question_type === 'sql_query'}
              <div>
                <label class="block text-sm font-semibold mb-2">Expected SQL Query</label>
                <textarea 
                  class="w-full px-4 py-3 border rounded-xl resize-none font-mono" 
                  rows="4" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="SELECT * FROM table_name WHERE condition;"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">Enter the expected SQL query solution</p>
              </div>
            {:else if questionForm.question_type === 'multi_grid'}
              <div class="space-y-4">
                <div class="bg-rose-50 border border-rose-200 rounded-lg p-4">
                  <h4 class="font-semibold text-rose-800 mb-2">📊 Multi-Grid Matrix Table</h4>
                  <p class="text-sm text-rose-700">Create a table where students select one answer per row from multiple columns.</p>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-semibold mb-2">Row Items (one per line)</label>
                    <textarea 
                      class="w-full px-4 py-3 border rounded-xl resize-none" 
                      rows="4" 
                      bind:value={questionForm.grid_rows}
                      placeholder="User Interface\nPerformance\nDocumentation\nSupport"
                    ></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-semibold mb-2">Column Options (one per line)</label>
                    <textarea 
                      class="w-full px-4 py-3 border rounded-xl resize-none" 
                      rows="4" 
                      bind:value={questionForm.grid_columns}
                      placeholder="Excellent\nGood\nFair\nPoor"
                    ></textarea>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-semibold mb-2">Correct Answers (Row:Column format, one per line)</label>
                  <textarea 
                    class="w-full px-4 py-3 border rounded-xl resize-none" 
                    rows="4" 
                    bind:value={questionForm.correct_answer} 
                    placeholder="User Interface:Excellent\nPerformance:Good\nDocumentation:Fair\nSupport:Good"
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">Specify the correct answer for each row in "Row:Column" format</p>
                </div>
              </div>
            {/if}

            <div>
              <label class="block text-sm font-semibold mb-2">Correct Answer</label>
              {#if questionForm.question_type === 'mcq' || questionForm.question_type === 'dropdown_select'}
                <select bind:value={questionForm.correct_answer} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select correct answer</option>
                  {#each questionForm.options.filter(o => o.trim()) as option}
                    <option value={option}>{option}</option>
                  {/each}
                </select>
              {:else if questionForm.question_type === 'true_false'}
                <select bind:value={questionForm.correct_answer} class="w-full px-4 py-3 border rounded-xl">
                  <option value="">Select answer</option>
                  <option value="True">True</option>
                  <option value="False">False</option>
                </select>
              {:else if questionForm.question_type === 'multiple_select'}
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p class="text-sm text-blue-700">💡 Selected correct answers: {questionForm.correct_answer || 'None selected'}</p>
                  <p class="text-xs text-blue-600 mt-1">Use the checkboxes above to select multiple correct answers</p>
                </div>
              {:else if questionForm.question_type === 'fill_in_blanks' || questionForm.question_type === 'matching_pairs' || questionForm.question_type === 'drag_drop_ordering' || questionForm.question_type === 'code_writing' || questionForm.question_type === 'sql_query' || questionForm.question_type === 'multi_grid'}
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p class="text-sm text-gray-700">✅ Answer configured above in the question-specific section</p>
                </div>
              {:else if questionForm.question_type === 'linear_scale'}
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p class="text-sm text-gray-700">✅ Expected rating configured above</p>
                </div>
              {:else}
                <input 
                  bind:value={questionForm.correct_answer}
                  class="w-full px-4 py-3 border rounded-xl"
                  placeholder="Enter correct answer"
                />
              {/if}
            </div>

            <div class="flex justify-end space-x-4 pt-6">
              <button 
                on:click={() => activeTab = 'questions'}
                class="px-6 py-3 border rounded-xl hover:bg-gray-50 transition-all"
              >
                Cancel
              </button>
              <button 
                on:click={saveQuestion}
                disabled={loading}
                class="bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-all font-semibold"
              >
                {loading ? ' Saving...' : ' Save Question'}
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Question Form Modal -->
{#if showQuestionForm}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl my-8">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold">{editingQuestion ? 'Edit' : 'Create'} Question</h3>
          <button on:click={() => showQuestionForm = false} class="text-gray-500 hover:text-gray-700 text-2xl"></button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold mb-2">Question Type</label>
            <select bind:value={questionForm.question_type} class="w-full px-4 py-3 border rounded-xl">
              {#each Object.entries(questionTypes) as [value, label]}
                <option {value}>{label}</option>
              {/each}
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Question Text</label>
            <textarea 
              bind:value={questionForm.question_text}
              rows="3"
              class="w-full px-4 py-3 border rounded-xl"
              placeholder="Enter your question..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold mb-2">Department</label>
              <select bind:value={questionForm.department} class="w-full px-4 py-3 border rounded-xl">
                <option value="">Select Department</option>
                {#each departments as dept}
                  <option value={dept}>{dept}</option>
                {/each}
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold mb-2">Level</label>
              <select bind:value={questionForm.level} class="w-full px-4 py-3 border rounded-xl">
                <option value="">Select Level</option>
                {#each levels as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Lesson</label>
            <select bind:value={questionForm.lesson_id} class="w-full px-4 py-3 border rounded-xl">
              <option value={null}>Select Lesson</option>
              {#if questionForm.department && questionForm.level}
                {#each lessons.filter(l => l.department === questionForm.department && l.level === questionForm.level) as lesson}
                  <option value={lesson.id}>{lesson.title} ({lesson.code})</option>
                {/each}
              {:else}
                <option disabled>Select Department & Level first</option>
              {/if}
            </select>
          </div>

          {#if questionForm.question_type === 'mcq'}
            <div>
              <label class="block text-sm font-semibold mb-2">Options</label>
              {#each questionForm.options as option, i}
                <div class="flex space-x-2 mb-2">
                  <input 
                    bind:value={questionForm.options[i]}
                    class="flex-1 px-4 py-2 border rounded-lg"
                    placeholder={`Option ${String.fromCharCode(65 + i)}`}
                  />
                  {#if questionForm.options.length > 2}
                    <button on:click={() => removeOption(i)} class="px-3 py-2 bg-red-100 text-red-800 rounded-lg">
                      🗑️
                    </button>
                  {/if}
                </div>
              {/each}
              <button on:click={addOption} class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                ➕ Add Option
              </button>
            </div>
          {:else if questionForm.question_type === 'multiple_select'}
            <div>
              <label class="block text-sm font-semibold mb-2">Options (Check all correct answers)</label>
              {#each questionForm.options as option, i}
                <div class="flex items-center space-x-3 p-2 border border-gray-200 rounded-lg mb-2">
                  <input 
                    type="checkbox" 
                    value={option}
                    checked={questionForm.correct_answer.split(',').includes(option)}
                    on:change={(e) => {
                      let correctAnswers = questionForm.correct_answer ? questionForm.correct_answer.split(',').filter(a => a.trim()) : [];
                      if (e.target.checked) {
                        if (!correctAnswers.includes(option)) correctAnswers.push(option);
                      } else {
                        correctAnswers = correctAnswers.filter(a => a !== option);
                      }
                      questionForm.correct_answer = correctAnswers.join(',');
                    }}
                    class="w-4 h-4 text-blue-600"
                  />
                  <input 
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg" 
                    bind:value={questionForm.options[i]} 
                    placeholder="Option {i + 1}"
                  />
                </div>
              {/each}
              <button on:click={addOption} class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                ➕ Add Option
              </button>
            </div>
          {:else if questionForm.question_type === 'dropdown_select'}
            <div>
              <label class="block text-sm font-semibold mb-2">Dropdown Options</label>
              {#each questionForm.options as option, i}
                <div class="flex items-center space-x-3 p-2 border border-gray-200 rounded-lg mb-2">
                  <input 
                    type="radio" 
                    name="correct_answer_dropdown_modal" 
                    value={option} 
                    bind:group={questionForm.correct_answer}
                    class="w-4 h-4 text-blue-600"
                  />
                  <input 
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg" 
                    bind:value={questionForm.options[i]} 
                    placeholder="Option {i + 1}"
                  />
                </div>
              {/each}
              <button on:click={addOption} class="mt-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                ➕ Add Option
              </button>
            </div>
          {:else if questionForm.question_type === 'fill_in_blanks'}
            <div>
              <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                <p class="text-sm text-yellow-700">Use _____ (5 underscores) for each blank in your question.</p>
              </div>
              <label class="block text-sm font-semibold mb-2">Correct Answers (comma-separated)</label>
              <input 
                class="w-full px-4 py-3 border rounded-xl" 
                bind:value={questionForm.correct_answer} 
                placeholder="Paris,Europe (comma-separated, in order)"
              />
            </div>
          {:else if questionForm.question_type === 'matching_pairs'}
            <div>
              <label class="block text-sm font-semibold mb-2">Correct Pairs (Left:Right format)</label>
              <textarea 
                class="w-full px-4 py-3 border rounded-xl resize-none" 
                rows="3" 
                bind:value={questionForm.correct_answer} 
                placeholder="Python:Programming Language,HTML:Markup Language"
              ></textarea>
            </div>
          {:else if questionForm.question_type === 'drag_drop_ordering'}
            <div>
              <label class="block text-sm font-semibold mb-2">Items in Correct Order</label>
              <textarea 
                class="w-full px-4 py-3 border rounded-xl resize-none" 
                rows="3" 
                bind:value={questionForm.correct_answer} 
                placeholder="First Step,Second Step,Third Step"
              ></textarea>
            </div>
          {:else if questionForm.question_type === 'linear_scale'}
            <div>
              <label class="block text-sm font-semibold mb-2">Expected Rating (1-10)</label>
              <input 
                class="w-full px-4 py-3 border rounded-xl" 
                type="number" 
                bind:value={questionForm.correct_answer} 
                min="1" 
                max="10" 
                placeholder="Expected rating"
              />
            </div>
          {:else if questionForm.question_type === 'code_writing'}
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-semibold mb-2">Programming Language</label>
                <select class="w-full px-4 py-3 border rounded-xl" bind:value={questionForm.programming_language}>
                  <option value="python">Python</option>
                  <option value="c">C</option>
                  <option value="cpp">C++</option>
                  <option value="javascript">JavaScript</option>
                  <option value="html">HTML</option>
                  <option value="java">Java</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Expected Code Solution</label>
                <textarea 
                  class="w-full px-4 py-3 border rounded-xl resize-none font-mono" 
                  rows="4" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="Enter expected code solution"
                ></textarea>
              </div>
            </div>
          {:else if questionForm.question_type === 'sql_query'}
            <div>
              <label class="block text-sm font-semibold mb-2">Expected SQL Query</label>
              <textarea 
                class="w-full px-4 py-3 border rounded-xl resize-none font-mono" 
                rows="3" 
                bind:value={questionForm.correct_answer} 
                placeholder="SELECT * FROM table_name;"
              ></textarea>
            </div>
          {:else if questionForm.question_type === 'multi_grid'}
            <div class="space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-sm font-semibold mb-2">Rows (one per line)</label>
                  <textarea 
                    class="w-full px-3 py-2 border rounded-xl resize-none" 
                    rows="3" 
                    bind:value={questionForm.grid_rows}
                    placeholder="Row 1\nRow 2\nRow 3"
                  ></textarea>
                </div>
                <div>
                  <label class="block text-sm font-semibold mb-2">Columns (one per line)</label>
                  <textarea 
                    class="w-full px-3 py-2 border rounded-xl resize-none" 
                    rows="3" 
                    bind:value={questionForm.grid_columns}
                    placeholder="Option A\nOption B\nOption C"
                  ></textarea>
                </div>
              </div>
              <div>
                <label class="block text-sm font-semibold mb-2">Correct Answers (Row:Column format)</label>
                <textarea 
                  class="w-full px-3 py-2 border rounded-xl resize-none" 
                  rows="3" 
                  bind:value={questionForm.correct_answer} 
                  placeholder="Row 1:Option A\nRow 2:Option B"
                ></textarea>
              </div>
            </div>
          {/if}

          <div>
            <label class="block text-sm font-semibold mb-2">Correct Answer</label>
            {#if questionForm.question_type === 'mcq' || questionForm.question_type === 'dropdown_select'}
              <select bind:value={questionForm.correct_answer} class="w-full px-4 py-3 border rounded-xl">
                <option value="">Select correct answer</option>
                {#each questionForm.options.filter(o => o.trim()) as option}
                  <option value={option}>{option}</option>
                {/each}
              </select>
            {:else if questionForm.question_type === 'true_false'}
              <select bind:value={questionForm.correct_answer} class="w-full px-4 py-3 border rounded-xl">
                <option value="True">True</option>
                <option value="False">False</option>
              </select>
            {:else if questionForm.question_type === 'multiple_select'}
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p class="text-sm text-blue-700">💡 Selected: {questionForm.correct_answer || 'None'}</p>
              </div>
            {:else if questionForm.question_type === 'fill_in_blanks' || questionForm.question_type === 'matching_pairs' || questionForm.question_type === 'drag_drop_ordering' || questionForm.question_type === 'code_writing' || questionForm.question_type === 'sql_query' || questionForm.question_type === 'multi_grid' || questionForm.question_type === 'linear_scale'}
              <div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <p class="text-sm text-gray-700">✅ Answer configured above</p>
              </div>
            {:else}
              <input 
                bind:value={questionForm.correct_answer}
                class="w-full px-4 py-3 border rounded-xl"
                placeholder="Enter correct answer"
              />
            {/if}
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Points</label>
            <input 
              type="number"
              bind:value={questionForm.points}
              min="1"
              class="w-full px-4 py-3 border rounded-xl"
            />
          </div>

          <div class="flex space-x-4 pt-4">
            <button 
              on:click={saveQuestion}
              disabled={loading}
              class="flex-1 bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? ' Saving...' : ' Save Question'}
            </button>
            <button 
              on:click={() => showQuestionForm = false}
              class="px-6 py-3 border rounded-xl hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}


