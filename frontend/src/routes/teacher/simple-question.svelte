<script>
  import { api } from '$lib/api.js';
  
  export let lessons = [];
  export let onQuestionCreated = () => {};
  
  let loading = false;
  let error = '';
  
  // Simple form data
  let questionText = '';
  let questionType = 'mcq';
  let department = 'Software Development';
  let level = 'Level 3';
  let lessonId = null;
  let correctAnswer = '';
  let points = 1;
  
  // Options for MCQ
  let option1 = '';
  let option2 = '';
  let option3 = '';
  let option4 = '';
  
  const departments = [
    'Software Development',
    'Computer System and Architecture', 
    'Land Surveying',
    'Building Construction'
  ];
  
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  
  async function createQuestion() {
    if (!questionText.trim()) {
      error = 'Question text is required';
      return;
    }
    
    if (!correctAnswer.trim()) {
      error = 'Correct answer is required';
      return;
    }
    
    if (!lessonId) {
      error = 'Please select a lesson';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      let options = [];
      
      if (questionType === 'mcq' || questionType === 'code_analysis') {
        options = [option1, option2, option3, option4].filter(opt => opt.trim());
        if (options.length < 2) {
          error = 'At least 2 options required for MCQ/Code Analysis';
          loading = false;
          return;
        }
        if (!options.includes(correctAnswer)) {
          error = 'Correct answer must be one of the options';
          loading = false;
          return;
        }
      }
      
      const questionData = {
        question_text: questionText.trim(),
        question_type: questionType,
        options: options,
        correct_answer: correctAnswer.trim(),
        points: parseInt(points) || 1,
        department: department,
        level: level,
        lesson_id: parseInt(lessonId)
      };
      
      await api.createQuestion(questionData);
      
      // Reset form
      questionText = '';
      option1 = '';
      option2 = '';
      option3 = '';
      option4 = '';
      correctAnswer = '';
      points = 1;
      
      alert(' Question created successfully!');
      onQuestionCreated();
      
    } catch (err) {
      error = err.message || 'Failed to create question';
    } finally {
      loading = false;
    }
  }
  
  $: availableLessons = lessons.filter(l => l.department === department && l.level === level);
  $: if (availableLessons.length > 0 && !lessonId) {
    lessonId = availableLessons[0].id;
  }
</script>

<div class="bg-white rounded-lg border p-6">
  <h3 class="text-xl font-bold mb-6 text-gray-900">Create New Question</h3>
  
  {#if error}
    <div class="bg-red-50 border border-red-200 rounded p-3 mb-4">
      <p class="text-red-700 text-sm">{error}</p>
    </div>
  {/if}
  
  <div class="space-y-4">
    <!-- Question Text -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Question Text</label>
      <textarea 
        bind:value={questionText}
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-20"
        placeholder="Enter your question here..."
      ></textarea>
    </div>
    
    <!-- Question Type -->
    <div class="grid grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
        <select bind:value={questionType} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <option value="mcq">Multiple Choice</option>
          <option value="true_false">True/False</option>
          <option value="short_answer">Short Answer</option>
          <option value="fill_blanks">Fill in the Blanks</option>
          <option value="code_analysis">Code Analysis</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Department</label>
        <select bind:value={department} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          {#each departments as dept}
            <option value={dept}>{dept}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Level</label>
        <select bind:value={level} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          {#each levels as lvl}
            <option value={lvl}>{lvl}</option>
          {/each}
        </select>
      </div>
    </div>
    
    <!-- Lesson Selection -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Lesson</label>
      <select bind:value={lessonId} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
        <option value={null}>Select lesson</option>
        {#each availableLessons as lesson}
          <option value={lesson.id}>{lesson.title}</option>
        {/each}
      </select>
    </div>
    
    <!-- Options for MCQ and Code Analysis -->
    {#if questionType === 'mcq' || questionType === 'code_analysis'}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Options</label>
        <div class="space-y-2">
          <input bind:value={option1} placeholder="Option 1" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <input bind:value={option2} placeholder="Option 2" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <input bind:value={option3} placeholder="Option 3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <input bind:value={option4} placeholder="Option 4" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
        </div>
      </div>
    {/if}
    
    <!-- Correct Answer -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Correct Answer</label>
        {#if questionType === 'true_false'}
          <select bind:value={correctAnswer} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <option value="">Select</option>
            <option value="True">True</option>
            <option value="False">False</option>
          </select>
        {:else if questionType === 'mcq' || questionType === 'code_analysis'}
          <select bind:value={correctAnswer} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <option value="">Select correct option</option>
            {#if option1.trim()}<option value={option1}>{option1}</option>{/if}
            {#if option2.trim()}<option value={option2}>{option2}</option>{/if}
            {#if option3.trim()}<option value={option3}>{option3}</option>{/if}
            {#if option4.trim()}<option value={option4}>{option4}</option>{/if}
          </select>
        {:else if questionType === 'fill_blanks'}
          <input bind:value={correctAnswer} placeholder="Enter answers separated by commas (e.g., answer1, answer2)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
        {:else}
          <input bind:value={correctAnswer} placeholder="Enter correct answer" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
        {/if}
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Points</label>
        <input type="number" bind:value={points} min="1" max="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
      </div>
    </div>
    
    <!-- Submit Button -->
    <div class="pt-4">
      <button 
        on:click={createQuestion}
        disabled={loading}
        class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? ' Creating...' : ' Create Question'}
      </button>
    </div>
  </div>
</div>