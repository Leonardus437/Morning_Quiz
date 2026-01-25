<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let selectedQuestionType = 'mcq';

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
      example: 'Explain the importance of responsive web design.',
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
      example: 'Rate the importance of code documentation:\n1 ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩ 10',
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
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
  <div class="max-w-7xl mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">🎨 Advanced Question Types</h1>
          <p class="text-gray-600 mt-1">13 Professional Question Types - More than Google Forms!</p>
        </div>
        <div class="flex space-x-3">
          <button 
            on:click={() => goto('/teacher/questions')}
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all"
          >
            📁 Question Bank
          </button>
          <button 
            on:click={() => goto('/teacher')}
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all"
          >
            🏠 Dashboard
          </button>
        </div>
      </div>
    </div>

    <!-- SPA Layout: Sidebar + Content -->
    <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
      <div class="flex h-[800px]">
        <!-- Left Sidebar: Question Types -->
        <div class="w-80 bg-gray-50 border-r border-gray-200 overflow-y-auto">
          <div class="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
            <h2 class="text-lg font-bold text-white">📊 Question Types (13)</h2>
            <p class="text-blue-100 text-sm">Click to explore each type</p>
          </div>
          
          <div class="p-2">
            {#each Object.entries(questionTypes) as [type, label], index}
              <button
                on:click={() => selectedQuestionType = type}
                class="w-full text-left p-3 rounded-lg mb-2 transition-all hover:bg-blue-50 {selectedQuestionType === type ? 'bg-blue-100 border-l-4 border-blue-600 shadow-md' : 'hover:shadow-sm'}"
              >
                <div class="flex items-center space-x-3">
                  <span class="text-2xl">{questionTypeDetails[type]?.icon || '📝'}</span>
                  <div class="flex-1">
                    <div class="font-semibold text-gray-900 text-sm">{label}</div>
                    <div class="text-xs text-gray-500 mt-1">
                      {type === 'mcq' ? 'Radio buttons' : 
                       type === 'multiple_select' ? 'Checkboxes' :
                       type === 'fill_in_blanks' ? 'Input fields' :
                       type === 'code_writing' ? 'Code editor' :
                       type === 'multi_grid' ? 'Matrix table' : 'Interactive'}
                    </div>
                  </div>
                  <div class="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">
                    {index + 1}
                  </div>
                </div>
              </button>
            {/each}
          </div>
          
          <div class="p-4 border-t border-gray-200 bg-green-50">
            <div class="text-center">
              <div class="text-2xl mb-2">🏆</div>
              <div class="text-sm font-semibold text-green-800">13 Question Types</div>
              <div class="text-xs text-green-600">More than Google Forms!</div>
            </div>
          </div>
        </div>

        <!-- Right Content: Question Type Details -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6">
            {#if questionTypeDetails[selectedQuestionType]}
              {@const details = questionTypeDetails[selectedQuestionType]}
              
              <!-- Question Type Header -->
              <div class="mb-6">
                <div class="flex items-center space-x-4 mb-4">
                  <div class="text-4xl">{details.icon}</div>
                  <div>
                    <h3 class="text-2xl font-bold text-gray-900">{details.title}</h3>
                    <p class="text-gray-600">{details.description}</p>
                  </div>
                </div>
              </div>

              <!-- Features -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">✨ Key Features</h4>
                <div class="grid grid-cols-2 gap-3">
                  {#each details.features as feature}
                    <div class="flex items-center space-x-2 p-2 bg-blue-50 rounded-lg">
                      <span class="text-blue-600">✓</span>
                      <span class="text-sm text-gray-700">{feature}</span>
                    </div>
                  {/each}
                </div>
              </div>

              <!-- Example -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">📝 Example</h4>
                <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <pre class="text-sm text-gray-800 whitespace-pre-wrap font-mono">{details.example}</pre>
                </div>
              </div>

              <!-- Student Interface Preview -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">📱 Student Interface</h4>
                <div class="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6">
                  {#if selectedQuestionType === 'mcq'}
                    <div class="space-y-3">
                      <p class="font-medium">What is the capital of France?</p>
                      <div class="space-y-2">
                        <label class="flex items-center space-x-2">
                          <input type="radio" name="demo" class="text-blue-600" />
                          <span>London</span>
                        </label>
                        <label class="flex items-center space-x-2">
                          <input type="radio" name="demo" class="text-blue-600" checked />
                          <span class="text-green-600 font-semibold">Paris ✓</span>
                        </label>
                        <label class="flex items-center space-x-2">
                          <input type="radio" name="demo" class="text-blue-600" />
                          <span>Berlin</span>
                        </label>
                      </div>
                    </div>
                  {:else if selectedQuestionType === 'multiple_select'}
                    <div class="space-y-3">
                      <p class="font-medium">Select all programming languages:</p>
                      <div class="space-y-2">
                        <label class="flex items-center space-x-2">
                          <input type="checkbox" class="text-blue-600" checked />
                          <span class="text-green-600 font-semibold">Python ✓</span>
                        </label>
                        <label class="flex items-center space-x-2">
                          <input type="checkbox" class="text-blue-600" />
                          <span>HTML</span>
                        </label>
                        <label class="flex items-center space-x-2">
                          <input type="checkbox" class="text-blue-600" checked />
                          <span class="text-green-600 font-semibold">JavaScript ✓</span>
                        </label>
                      </div>
                    </div>
                  {:else if selectedQuestionType === 'fill_in_blanks'}
                    <div class="space-y-3">
                      <p class="font-medium">Python is a _____ language and HTML is a _____ language.</p>
                      <div class="flex space-x-4">
                        <div>
                          <label class="block text-sm text-gray-600 mb-1">Blank 1:</label>
                          <input type="text" value="programming" class="px-3 py-2 border rounded-lg bg-green-50" readonly />
                        </div>
                        <div>
                          <label class="block text-sm text-gray-600 mb-1">Blank 2:</label>
                          <input type="text" value="markup" class="px-3 py-2 border rounded-lg bg-green-50" readonly />
                        </div>
                      </div>
                    </div>
                  {:else if selectedQuestionType === 'code_writing'}
                    <div class="space-y-3">
                      <p class="font-medium">Write a Python function to calculate factorial:</p>
                      <div class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                        <div>def factorial(n):</div>
                        <div>    if n &lt;= 1:</div>
                        <div>        return 1</div>
                        <div>    return n * factorial(n-1)</div>
                      </div>
                    </div>
                  {:else if selectedQuestionType === 'multi_grid'}
                    <div class="space-y-3">
                      <p class="font-medium">Rate each aspect:</p>
                      <div class="overflow-x-auto">
                        <table class="w-full border border-gray-300">
                          <thead>
                            <tr class="bg-gray-100">
                              <th class="border border-gray-300 px-3 py-2 text-left">Aspect</th>
                              <th class="border border-gray-300 px-3 py-2">Poor</th>
                              <th class="border border-gray-300 px-3 py-2">Good</th>
                              <th class="border border-gray-300 px-3 py-2">Excellent</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td class="border border-gray-300 px-3 py-2 font-medium">Quality</td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="quality" class="text-blue-600" />
                              </td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="quality" class="text-blue-600" />
                              </td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="quality" class="text-blue-600" checked />
                              </td>
                            </tr>
                            <tr>
                              <td class="border border-gray-300 px-3 py-2 font-medium">Service</td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="service" class="text-blue-600" />
                              </td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="service" class="text-blue-600" checked />
                              </td>
                              <td class="border border-gray-300 px-3 py-2 text-center">
                                <input type="radio" name="service" class="text-blue-600" />
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  {:else}
                    <div class="text-center py-8 text-gray-500">
                      <div class="text-4xl mb-2">{details.icon}</div>
                      <p>Interactive preview for <strong>{details.title}</strong></p>
                      <p class="text-sm mt-2">Click "Create Question" to build this type</p>
                    </div>
                  {/if}
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex space-x-4">
                <button 
                  on:click={() => goto('/teacher/questions')}
                  class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all font-semibold"
                >
                  📝 Create {details.title} Question
                </button>
                <button 
                  on:click={() => goto('/teacher/questions')}
                  class="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-all"
                >
                  📁 View All Questions
                </button>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>