<script>
  import { goto } from '$app/navigation';
  import { api } from '$lib/api.js';

  let selectedType = 'mcq';
  let showQuickUpload = false;
  let selectedFile = null;
  let uploadingFile = false;
  let error = '';
  let lessons = [];
  let loading = false;

  const departments = ['Software Development', 'Computer System and Architecture', 'Land Surveying', 'Building Construction'];
  const levels = ['Level 3', 'Level 4', 'Level 5'];

  const questionTypes = [
    { id: 'mcq', title: 'Multiple choice', icon: 'radio-button', desc: 'Choose one from a list' },
    { id: 'multiple_select', title: 'Checkboxes', icon: 'check-square', desc: 'Choose multiple from a list' },
    { id: 'dropdown_select', title: 'Dropdown', icon: 'chevron-down', desc: 'Choose from a dropdown' },
    { id: 'short_answer', title: 'Short answer', icon: 'minus', desc: 'Brief text response' },
    { id: 'essay', title: 'Paragraph', icon: 'align-left', desc: 'Long text response' },
    { id: 'linear_scale', title: 'Linear scale', icon: 'sliders', desc: 'Rate on a scale' },
    { id: 'multi_grid', title: 'Multiple choice grid', icon: 'grid', desc: 'Grid of radio buttons' },
    { id: 'fill_in_blanks', title: 'Fill in the blanks', icon: 'type', desc: 'Complete missing words' },
    { id: 'matching_pairs', title: 'Matching', icon: 'link', desc: 'Match items together' },
    { id: 'drag_drop_ordering', title: 'Ordering', icon: 'list-ordered', desc: 'Arrange in sequence' },
    { id: 'code_writing', title: 'Code', icon: 'code', desc: 'Write programming code' },
    { id: 'sql_query', title: 'SQL Query', icon: 'database', desc: 'Write database queries' },
    { id: 'true_false', title: 'True/False', icon: 'check-circle', desc: 'Binary choice' }
  ];

  let form = {
    question_text: '',
    options: ['', '', '', ''],
    correct_answer: '',
    correct_answers: [],
    blanks: ['', ''],
    pairs: [{left: '', right: ''}, {left: '', right: ''}],
    items: ['', '', ''],
    rows: ['', ''],
    columns: ['', '', ''],
    scale_min: 1,
    scale_max: 10,
    code_language: 'Python',
    points: 1,
    department: '',
    level: '',
    lesson_id: null
  };

  const codeLanguages = [
    { id: 'Python', snippet: 'def function_name():\n    # Your code here\n    return result' },
    { id: 'JavaScript', snippet: 'function functionName() {\n    // Your code here\n    return result;\n}' },
    { id: 'C', snippet: '#include <stdio.h>\n\nint main() {\n    // Your code here\n    return 0;\n}' },
    { id: 'C++', snippet: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}' },
    { id: 'Java', snippet: 'public class Main {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}' },
    { id: 'HTML', snippet: '<!DOCTYPE html>\n<html>\n<head>\n    <title>Page Title</title>\n</head>\n<body>\n    <!-- Your code here -->\n</body>\n</html>' },
    { id: 'Solidity', snippet: 'pragma solidity ^0.8.0;\n\ncontract MyContract {\n    // Your code here\n}' },
    { id: 'Dart', snippet: 'void main() {\n  // Your code here\n}' },
    { id: 'Other', snippet: '// Write your code here' }
  ];

  $: codeSnippet = codeLanguages.find(l => l.id === form.code_language)?.snippet || '';

  function selectType(typeId) {
    selectedType = typeId;
    resetForm();
  }

  function resetForm() {
    form = {
      question_text: '',
      options: ['', '', '', ''],
      correct_answer: '',
      correct_answers: [],
      blanks: ['', ''],
      pairs: [{left: '', right: ''}, {left: '', right: ''}],
      items: ['', '', ''],
      rows: ['', ''],
      columns: ['', '', ''],
      scale_min: 1,
      scale_max: 10,
      code_language: 'Python',
      points: 1,
      department: form.department,
      level: form.level,
      lesson_id: form.lesson_id
    };
  }

  async function loadLessons() {
    try {
      const response = await fetch(`${api.baseURL}/lessons`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) lessons = await response.json();
    } catch (err) {
      console.error('Failed to load lessons:', err);
    }
  }

  async function createQuestion() {
    loading = true;
    error = '';
    try {
      let payload = {
        question_text: form.question_text.trim(),
        question_type: selectedType,
        points: parseInt(form.points) || 1,
        department: form.department,
        level: form.level,
        lesson_id: parseInt(form.lesson_id)
      };

      if (selectedType === 'mcq' || selectedType === 'dropdown_select') {
        payload.options = form.options.filter(o => o.trim());
        payload.correct_answer = form.correct_answer;
      } else if (selectedType === 'multiple_select') {
        payload.options = form.options.filter(o => o.trim());
        payload.correct_answer = form.correct_answers.join(',');
      } else if (selectedType === 'true_false') {
        payload.options = [];
        payload.correct_answer = form.correct_answer;
      } else {
        payload.options = [];
        payload.correct_answer = form.correct_answer || 'Manual grading';
      }

      const response = await fetch(`${api.baseURL}/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Failed to create question');
      
      alert('✅ Question created successfully!');
      resetForm();
      
      // Redirect to My Questions page with reload flag
      window.location.href = '/teacher?tab=questions&reload=1';
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function handleFileUpload(event) {
    selectedFile = event.target.files[0];
  }

  async function uploadQuestions() {
    if (!selectedFile) return;
    uploadingFile = true;
    error = '';
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('department', form.department || '');
      formData.append('level', form.level || '');
      
      const response = await fetch(`${api.baseURL}/upload-questions`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Upload failed');
      }
      const result = await response.json();
      alert(`✅ Extracted ${result.count || 0} questions!`);
      selectedFile = null;
      showQuickUpload = false;
      
      // Redirect to My Questions page with reload flag
      window.location.href = '/teacher?tab=questions&reload=1';
    } catch (err) {
      error = err.message;
      alert('❌ Upload failed: ' + err.message);
    } finally {
      uploadingFile = false;
    }
  }

  function addOption() {
    form.options = [...form.options, ''];
  }

  function addPair() {
    form.pairs = [...form.pairs, {left: '', right: ''}];
  }

  function addItem() {
    form.items = [...form.items, ''];
  }

  loadLessons();
</script>

<svelte:head>
  <link rel="stylesheet" href="https://unpkg.com/lucide-static@latest/font/lucide.css">
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-gray-200 sticky top-0 z-10">
    <div class="px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <button on:click={() => goto('/teacher')} class="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <i class="lucide lucide-arrow-left w-5 h-5 text-gray-700"></i>
        </button>
        <h1 class="text-xl font-normal text-gray-800">Question types</h1>
      </div>
      <div class="flex items-center space-x-3">
        <button on:click={() => showQuickUpload = !showQuickUpload} class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors text-sm font-medium flex items-center space-x-2">
          <i class="lucide lucide-upload w-4 h-4"></i>
          <span>Quick upload</span>
        </button>
        <button on:click={() => goto('/teacher')} class="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm font-medium">
          Done
        </button>
      </div>
    </div>
  </header>

  <!-- Quick Upload Panel -->
  {#if showQuickUpload}
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Quick upload</h3>
          <button on:click={() => showQuickUpload = false} class="text-gray-400 hover:text-gray-600">
            <i class="lucide lucide-x w-5 h-5"></i>
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
            <div class="flex items-start space-x-3">
              <div class="p-2 bg-blue-50 rounded-lg">
                <i class="lucide lucide-sparkles w-5 h-5 text-blue-600"></i>
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 mb-1">AI Document Parser</h4>
                <p class="text-sm text-gray-600 mb-3">Upload Word/PDF to extract questions</p>
                <input type="file" accept=".doc,.docx,.pdf" on:change={handleFileUpload} class="hidden" id="aiUpload" />
                <label for="aiUpload" class="inline-block px-4 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded-lg cursor-pointer text-sm transition-colors">
                  {selectedFile ? selectedFile.name : 'Choose file'}
                </label>
                {#if selectedFile}
                  <button on:click={uploadQuestions} disabled={uploadingFile} class="ml-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm disabled:opacity-50">
                    {uploadingFile ? 'Processing...' : 'Extract'}
                  </button>
                {/if}
              </div>
            </div>
          </div>
          <div class="border border-gray-200 rounded-lg p-4 hover:border-green-500 transition-colors">
            <div class="flex items-start space-x-3">
              <div class="p-2 bg-green-50 rounded-lg">
                <i class="lucide lucide-package w-5 h-5 text-green-600"></i>
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 mb-1">LUMI H5P Integration</h4>
                <p class="text-sm text-gray-600 mb-3">Import interactive H5P content</p>
                <a href="https://lumi.education" target="_blank" class="inline-block px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
                  Open LUMI Editor
                </a>
              </div>
            </div>
          </div>
        </div>
        {#if error}
          <div class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- SPA Layout -->
  <div class="flex h-[calc(100vh-73px)]">
    <!-- Left Sidebar -->
    <div class="w-80 bg-white border-r border-gray-200 overflow-y-auto">
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-sm font-medium text-gray-700">Question types</h2>
        <p class="text-xs text-gray-500 mt-1">13 professional formats</p>
      </div>
      <div class="p-2">
        {#each questionTypes as type}
          <button
            on:click={() => selectType(type.id)}
            class="w-full text-left p-3 rounded-lg mb-1 transition-all flex items-center space-x-3 {selectedType === type.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'}"
          >
            <div class="p-2 bg-gray-50 rounded-lg {selectedType === type.id ? 'bg-blue-100' : ''}">
              <i class="lucide lucide-{type.icon} w-5 h-5 {selectedType === type.id ? 'text-blue-600' : 'text-gray-600'}"></i>
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{type.title}</div>
              <div class="text-xs text-gray-500">{type.desc}</div>
            </div>
          </button>
        {/each}
      </div>
    </div>

    <!-- Right Content -->
    <div class="flex-1 overflow-y-auto bg-white">
      <div class="max-w-3xl mx-auto p-8">
        <h2 class="text-2xl font-normal text-gray-900 mb-2">
          {questionTypes.find(t => t.id === selectedType)?.title}
        </h2>
        <p class="text-sm text-gray-600 mb-6">{questionTypes.find(t => t.id === selectedType)?.desc}</p>

        <form on:submit|preventDefault={createQuestion} class="space-y-6">
          <!-- Question Text -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Question</label>
            <textarea bind:value={form.question_text} class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" rows="3" placeholder="Enter your question" required></textarea>
          </div>

          <!-- MCQ Form -->
          {#if selectedType === 'mcq'}
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p class="text-sm text-blue-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see radio buttons and select ONE answer</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Options (Radio buttons)</label>
              <div class="space-y-2">
                {#each form.options as option, i}
                  <div class="flex items-center space-x-2">
                    <input type="radio" disabled class="w-4 h-4 text-blue-600" />
                    <input bind:value={form.options[i]} class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Option {i + 1}" />
                  </div>
                {/each}
                <button type="button" on:click={addOption} class="text-sm text-blue-600 hover:text-blue-700">+ Add option</button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Correct answer</label>
              <select bind:value={form.correct_answer} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" required>
                <option value="">Select correct answer</option>
                {#each form.options as option}
                  {#if option.trim()}<option value={option}>{option}</option>{/if}
                {/each}
              </select>
            </div>

          <!-- Multiple Select Form -->
          {:else if selectedType === 'multiple_select'}
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
              <p class="text-sm text-green-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see checkboxes and can select MULTIPLE answers</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Options (Checkboxes)</label>
              <div class="space-y-2">
                {#each form.options as option, i}
                  <div class="flex items-center space-x-2">
                    <input type="checkbox" disabled class="w-4 h-4 text-green-600 rounded" />
                    <input bind:value={form.options[i]} class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="Option {i + 1}" />
                  </div>
                {/each}
                <button type="button" on:click={addOption} class="text-sm text-green-600 hover:text-green-700">+ Add option</button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Correct answers (Select all that apply)</label>
              <div class="space-y-2 border border-gray-300 rounded-lg p-3">
                {#each form.options as option}
                  {#if option.trim()}
                    <label class="flex items-center space-x-2">
                      <input type="checkbox" value={option} bind:group={form.correct_answers} class="w-4 h-4 text-green-600 rounded" />
                      <span class="text-sm">{option}</span>
                    </label>
                  {/if}
                {/each}
              </div>
            </div>

          <!-- Dropdown Form -->
          {:else if selectedType === 'dropdown_select'}
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p class="text-sm text-purple-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a dropdown menu to select ONE answer</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Dropdown options</label>
              <div class="space-y-2">
                {#each form.options as option, i}
                  <input bind:value={form.options[i]} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" placeholder="Option {i + 1}" />
                {/each}
                <button type="button" on:click={addOption} class="text-sm text-purple-600 hover:text-purple-700">+ Add option</button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Correct answer</label>
              <select bind:value={form.correct_answer} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" required>
                <option value="">Select correct answer</option>
                {#each form.options as option}
                  {#if option.trim()}<option value={option}>{option}</option>{/if}
                {/each}
              </select>
            </div>

          <!-- True/False Form -->
          {:else if selectedType === 'true_false'}
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p class="text-sm text-yellow-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see two radio buttons: True and False</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Correct answer</label>
              <div class="space-y-2">
                <label class="flex items-center space-x-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input type="radio" bind:group={form.correct_answer} value="True" class="w-4 h-4 text-blue-600" required />
                  <span>True</span>
                </label>
                <label class="flex items-center space-x-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input type="radio" bind:group={form.correct_answer} value="False" class="w-4 h-4 text-blue-600" required />
                  <span>False</span>
                </label>
              </div>
            </div>

          <!-- Short Answer Form -->
          {:else if selectedType === 'short_answer'}
            <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <p class="text-sm text-indigo-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a single-line text input field</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Expected answer (for reference)</label>
              <input bind:value={form.correct_answer} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" placeholder="Sample correct answer" />
            </div>

          <!-- Essay Form -->
          {:else if selectedType === 'essay'}
            <div class="bg-pink-50 border border-pink-200 rounded-lg p-4">
              <p class="text-sm text-pink-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a large text area for detailed responses</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Grading notes (optional)</label>
              <textarea bind:value={form.correct_answer} class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none" rows="4" placeholder="Key points to look for when grading..."></textarea>
            </div>

          <!-- Linear Scale Form -->
          {:else if selectedType === 'linear_scale'}
            <div class="bg-teal-50 border border-teal-200 rounded-lg p-4">
              <p class="text-sm text-teal-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see clickable number buttons from {form.scale_min} to {form.scale_max}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Minimum value</label>
                <input type="number" bind:value={form.scale_min} min="0" max="5" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Maximum value</label>
                <input type="number" bind:value={form.scale_max} min="5" max="10" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent" />
              </div>
            </div>
            <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              {#each Array(form.scale_max - form.scale_min + 1) as _, i}
                <button type="button" class="w-10 h-10 rounded-full border-2 border-gray-300 hover:border-teal-500 hover:bg-teal-50 transition-colors">{form.scale_min + i}</button>
              {/each}
            </div>

          <!-- Fill in Blanks Form -->
          {:else if selectedType === 'fill_in_blanks'}
            <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p class="text-sm text-orange-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Use ___ in your question text. Students will see input fields for each blank</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Correct answers for blanks (comma-separated)</label>
              <input bind:value={form.correct_answer} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent" placeholder="answer1, answer2, answer3" />
              <p class="text-xs text-gray-500 mt-1">Example: "Python is a ___ language" → Answer: "programming"</p>
            </div>

          <!-- Matching Pairs Form -->
          {:else if selectedType === 'matching_pairs'}
            <div class="bg-cyan-50 border border-cyan-200 rounded-lg p-4">
              <p class="text-sm text-cyan-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see dropdown menus to match left items with right items</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Matching pairs</label>
              <div class="space-y-3">
                {#each form.pairs as pair, i}
                  <div class="grid grid-cols-2 gap-3">
                    <input bind:value={form.pairs[i].left} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent" placeholder="Left item {i + 1}" />
                    <input bind:value={form.pairs[i].right} class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent" placeholder="Right item {i + 1}" />
                  </div>
                {/each}
                <button type="button" on:click={addPair} class="text-sm text-cyan-600 hover:text-cyan-700">+ Add pair</button>
              </div>
            </div>

          <!-- Drag Drop Ordering Form -->
          {:else if selectedType === 'drag_drop_ordering'}
            <div class="bg-violet-50 border border-violet-200 rounded-lg p-4">
              <p class="text-sm text-violet-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see up/down buttons to arrange items in correct order</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Items in correct order</label>
              <div class="space-y-2">
                {#each form.items as item, i}
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-500 w-6">{i + 1}.</span>
                    <input bind:value={form.items[i]} class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent" placeholder="Item {i + 1}" />
                    <i class="lucide lucide-grip-vertical w-5 h-5 text-gray-400"></i>
                  </div>
                {/each}
                <button type="button" on:click={addItem} class="text-sm text-violet-600 hover:text-violet-700">+ Add item</button>
              </div>
            </div>

          <!-- Code Writing Form -->
          {:else if selectedType === 'code_writing'}
            <div class="bg-gray-800 text-white rounded-lg p-4">
              <p class="text-sm mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a professional code editor with syntax highlighting</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Programming Language</label>
              <select bind:value={form.code_language} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent bg-white">
                {#each codeLanguages as lang}
                  <option value={lang.id}>{lang.id}</option>
                {/each}
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Code snippet example for {form.code_language}</label>
              <div class="bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
                <div class="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center space-x-2">
                  <div class="flex space-x-2">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <span class="text-xs text-gray-400 ml-4">{form.code_language} Editor</span>
                </div>
                <div class="p-4 font-mono text-sm">
                  <pre class="text-green-400">{codeSnippet}</pre>
                </div>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Expected solution (for reference)</label>
              <div class="bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
                <div class="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center space-x-2">
                  <div class="flex space-x-2">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <span class="text-xs text-gray-400 ml-4">solution.{form.code_language === 'Python' ? 'py' : form.code_language === 'JavaScript' ? 'js' : form.code_language === 'C' ? 'c' : form.code_language === 'C++' ? 'cpp' : form.code_language === 'Java' ? 'java' : form.code_language === 'HTML' ? 'html' : form.code_language === 'Solidity' ? 'sol' : form.code_language === 'Dart' ? 'dart' : 'txt'}</span>
                </div>
                <textarea bind:value={form.correct_answer} class="w-full p-4 bg-gray-900 text-green-400 font-mono text-sm border-0 focus:ring-0 focus:outline-none" rows="10" placeholder={codeSnippet} style="resize: vertical;"></textarea>
              </div>
            </div>

          <!-- SQL Query Form -->
          {:else if selectedType === 'sql_query'}
            <div class="bg-blue-900 text-white rounded-lg p-4">
              <p class="text-sm mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a SQL editor for writing database queries</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Expected SQL query</label>
              <textarea bind:value={form.correct_answer} class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm bg-gray-50" rows="4" placeholder="SELECT * FROM students WHERE grade > 80;"></textarea>
            </div>

          <!-- Multi Grid Form -->
          {:else if selectedType === 'multi_grid'}
            <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
              <p class="text-sm text-emerald-800 mb-3"><i class="lucide lucide-info w-4 h-4 inline"></i> Students will see a table with radio buttons for each row/column combination</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Row labels (comma-separated)</label>
              <input bind:value={form.correct_answer} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent" placeholder="Quality, Service, Value" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Column labels (comma-separated)</label>
              <input value="Poor, Good, Excellent" class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50" readonly />
            </div>
          {/if}

          <!-- Common Fields -->
          <div class="grid grid-cols-3 gap-4 pt-4 border-t">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Department</label>
              <select bind:value={form.department} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" required>
                <option value="">Select</option>
                {#each departments as dept}<option value={dept}>{dept}</option>{/each}
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Level</label>
              <select bind:value={form.level} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" required>
                <option value="">Select</option>
                {#each levels as level}<option value={level}>{level}</option>{/each}
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Lesson</label>
              <select bind:value={form.lesson_id} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" required>
                <option value={null}>Select</option>
                {#each lessons.filter(l => l.department === form.department && l.level === form.level) as lesson}
                  <option value={lesson.id}>{lesson.title}</option>
                {/each}
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Points</label>
            <input type="number" bind:value={form.points} min="1" max="10" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button type="button" on:click={() => goto('/teacher')} class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={loading} class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50">
              {loading ? 'Creating...' : 'Create question'}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<style>
  :global(body) {
    font-family: 'Google Sans', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
</style>
