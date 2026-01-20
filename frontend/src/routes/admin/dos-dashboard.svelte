<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  import { user } from '$lib/stores.js';
  
  let loading = false;
  let error = '';
  let success = '';
  
  // Data
  let quizzes = [];
  let teachers = [];
  let students = [];
  let departments = [];
  let activeQuizzes = [];
  let quizResults = [];
  let currentQuizId = null;
  let selectedTeacher = null;
  let selectedDepartment = '';
  let selectedLevel = '';
  let realTimeData = {
    activeParticipants: 0,
    submissionRate: 0,
    averageScore: 0,
    completionTime: 0
  };
  
  // Refresh intervals
  let refreshInterval;
  let realTimeInterval;
  
  onMount(() => {
    loadData();
    
    // Set up refresh intervals
    refreshInterval = setInterval(loadData, 60000); // Refresh data every minute
    realTimeInterval = setInterval(loadRealTimeData, 10000); // Refresh real-time data every 10 seconds
    
    return () => {
      clearInterval(refreshInterval);
      clearInterval(realTimeInterval);
    };
  });
  
  async function loadData() {
    try {
      loading = true;
      
      const [quizzesData, teachersData, studentsData, departmentsData] = await Promise.all([
        api.getQuizzes().catch(() => []),
        api.getTeachers().catch(() => []),
        api.getStudents().catch(() => []),
        api.getDepartments().catch(() => [])
      ]);
      
      quizzes = quizzesData;
      teachers = teachersData;
      students = studentsData;
      departments = departmentsData || [
        'Software Development',
        'Computer System and Architecture', 
        'Land Surveying',
        'Building Construction'
      ];
      
      // Filter active quizzes
      activeQuizzes = quizzes.filter(quiz => quiz.is_active);
      
      // If we have a selected quiz, refresh its results
      if (currentQuizId) {
        await loadQuizResults(currentQuizId);
      }
      
    } catch (err) {
      console.error('Load data error:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function loadQuizResults(quizId) {
    try {
      loading = true;
      currentQuizId = quizId;
      
      quizResults = await api.getQuizResults(quizId);
      
      // Load real-time data for this quiz
      await loadRealTimeData();
      
    } catch (err) {
      console.error('Failed to load quiz results:', err);
      error = err.message;
      quizResults = [];
    } finally {
      loading = false;
    }
  }
  
  async function loadRealTimeData() {
    if (!currentQuizId) return;
    
    try {
      // This would be a real API call in a production environment
      // For now, we'll simulate real-time data
      const totalStudents = students.filter(s => {
        const quiz = quizzes.find(q => q.id === currentQuizId);
        return quiz && s.department === quiz.department && s.level === quiz.level;
      }).length;
      
      const submissions = quizResults.length;
      
      realTimeData = {
        activeParticipants: submissions,
        submissionRate: totalStudents > 0 ? Math.round((submissions / totalStudents) * 100) : 0,
        averageScore: quizResults.length > 0 
          ? Math.round(quizResults.reduce((sum, r) => sum + (r.score / r.total_questions * 100), 0) / quizResults.length) 
          : 0,
        completionTime: quizResults.length > 0
          ? Math.round(quizResults.reduce((sum, r) => sum + (r.completion_time || 0), 0) / quizResults.length)
          : 0
      };
    } catch (err) {
      console.error('Failed to load real-time data:', err);
    }
  }
  
  async function broadcastQuiz(quizId) {
    try {
      loading = true;
      error = '';
      
      await api.broadcastQuiz(quizId);
      
      success = 'Quiz broadcast successfully!';
      setTimeout(() => success = '', 3000);
      
      await loadData();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function activateQuiz(quizId) {
    try {
      loading = true;
      error = '';
      
      await api.activateQuiz(quizId);
      
      success = 'Quiz activated successfully!';
      setTimeout(() => success = '', 3000);
      
      await loadData();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function exportQuizExcel(quizId) {
    try {
      loading = true;
      
      const blob = await api.exportQuizExcel(quizId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Quiz_Results_${quizId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      success = 'Results exported to Excel successfully!';
      setTimeout(() => success = '', 3000);
    } catch (err) {
      error = 'Failed to export results: ' + err.message;
    } finally {
      loading = false;
    }
  }
  
  async function exportQuizPDF(quizId) {
    try {
      loading = true;
      
      const blob = await api.exportQuizPDF(quizId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Quiz_Results_${quizId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      success = 'Results exported to PDF successfully!';
      setTimeout(() => success = '', 3000);
    } catch (err) {
      error = 'Failed to export results: ' + err.message;
    } finally {
      loading = false;
    }
  }
  
  function filterQuizzes() {
    if (!selectedDepartment && !selectedLevel && !selectedTeacher) {
      return quizzes;
    }
    
    return quizzes.filter(quiz => {
      let match = true;
      
      if (selectedDepartment && quiz.department !== selectedDepartment) {
        match = false;
      }
      
      if (selectedLevel && quiz.level !== selectedLevel) {
        match = false;
      }
      
      if (selectedTeacher && quiz.created_by !== selectedTeacher.id) {
        match = false;
      }
      
      return match;
    });
  }
</script>

<div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
  <h2 class="text-2xl font-bold mb-6 flex items-center">
    <span class="text-3xl mr-3"></span>
    DOS Quiz Dashboard
  </h2>
  
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
  
  <!-- Real-time Overview -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-blue-100">Total Quizzes</p>
          <p class="text-3xl font-bold">{quizzes.length}</p>
        </div>
        <div class="text-4xl opacity-80"></div>
      </div>
    </div>
    <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-green-100">Active Quizzes</p>
          <p class="text-3xl font-bold">{activeQuizzes.length}</p>
        </div>
        <div class="text-4xl opacity-80"></div>
      </div>
    </div>
    <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-purple-100">Teachers</p>
          <p class="text-3xl font-bold">{teachers.length}</p>
        </div>
        <div class="text-4xl opacity-80"></div>
      </div>
    </div>
    <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-orange-100">Students</p>
          <p class="text-3xl font-bold">{students.length}</p>
        </div>
        <div class="text-4xl opacity-80"></div>
      </div>
    </div>
  </div>
  
  <!-- Filters -->
  <div class="bg-gray-50 rounded-xl p-4 mb-6">
    <h3 class="text-lg font-semibold mb-4">Filter Quizzes</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
        <select 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          bind:value={selectedDepartment}
        >
          <option value="">All Departments</option>
          {#each departments as dept}
            <option value={dept}>{dept}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Level</label>
        <select 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          bind:value={selectedLevel}
        >
          <option value="">All Levels</option>
          <option value="Level 3">Level 3</option>
          <option value="Level 4">Level 4</option>
          <option value="Level 5">Level 5</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Teacher</label>
        <select 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          bind:value={selectedTeacher}
        >
          <option value={null}>All Teachers</option>
          {#each teachers as teacher}
            <option value={teacher}>{teacher.full_name || teacher.username}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
  
  <!-- Quiz List -->
  <div class="mb-8">
    <h3 class="text-xl font-semibold mb-4">Quiz Management</h3>
    
    {#if filterQuizzes().length === 0}
      <div class="bg-white border border-gray-200 rounded-lg p-8 text-center">
        <div class="text-5xl mb-4"></div>
        <p class="text-gray-600 mb-2">No quizzes found matching your filters</p>
        <p class="text-sm text-gray-500">Try adjusting your filter criteria</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Title</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Department</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Level</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Teacher</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filterQuizzes() as quiz}
              <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-3 px-4 font-medium">{quiz.title}</td>
                <td class="py-3 px-4">{quiz.department}</td>
                <td class="py-3 px-4">{quiz.level}</td>
                <td class="py-3 px-4">
                  {teachers.find(t => t.id === quiz.created_by)?.full_name || 'Unknown'}
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-1 rounded-full text-xs font-medium {quiz.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    {quiz.is_active ? ' Active' : ' Draft'}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <div class="flex space-x-2">
                    <button 
                      class="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                      on:click={() => loadQuizResults(quiz.id)}
                    >
                       Results
                    </button>
                    
                    {#if !quiz.is_active}
                      <button 
                        class="bg-green-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-green-700 transition-colors"
                        on:click={() => activateQuiz(quiz.id)}
                      >
                         Activate
                      </button>
                    {/if}
                    
                    <button 
                      class="bg-purple-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-purple-700 transition-colors"
                      on:click={() => broadcastQuiz(quiz.id)}
                    >
                       Broadcast
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
  
  <!-- Real-time Quiz Monitoring -->
  {#if currentQuizId}
    <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-xl font-semibold">
          Real-time Quiz Monitoring: {quizzes.find(q => q.id === currentQuizId)?.title}
        </h3>
        <div class="flex space-x-2">
          <button 
            class="bg-green-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-green-700 transition-colors"
            on:click={() => exportQuizExcel(currentQuizId)}
          >
             Export Excel
          </button>
          <button 
            class="bg-red-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-red-700 transition-colors"
            on:click={() => exportQuizPDF(currentQuizId)}
          >
             Export PDF
          </button>
        </div>
      </div>
      
      <!-- Real-time Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
          <div class="text-sm text-blue-600 mb-1">Active Participants</div>
          <div class="text-2xl font-bold text-blue-800">{realTimeData.activeParticipants}</div>
        </div>
        <div class="bg-green-50 border border-green-100 rounded-xl p-4">
          <div class="text-sm text-green-600 mb-1">Submission Rate</div>
          <div class="text-2xl font-bold text-green-800">{realTimeData.submissionRate}%</div>
        </div>
        <div class="bg-purple-50 border border-purple-100 rounded-xl p-4">
          <div class="text-sm text-purple-600 mb-1">Average Score</div>
          <div class="text-2xl font-bold text-purple-800">{realTimeData.averageScore}%</div>
        </div>
        <div class="bg-orange-50 border border-orange-100 rounded-xl p-4">
          <div class="text-sm text-orange-600 mb-1">Avg. Completion Time</div>
          <div class="text-2xl font-bold text-orange-800">{realTimeData.completionTime} sec</div>
        </div>
      </div>
      
      <!-- Results Table -->
      {#if quizResults.length === 0}
        <div class="text-center py-8">
          <div class="text-5xl mb-4"></div>
          <p class="text-gray-600">No submissions yet for this quiz</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50 border-b border-gray-200">
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Rank</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Student</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Score</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Percentage</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Completion Time</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Submitted At</th>
              </tr>
            </thead>
            <tbody>
              {#each quizResults as result, index}
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
                    <span class="px-2 py-1 rounded-full text-sm font-medium {Math.round((result.score / result.total_questions) * 100) >= 80 ? 'bg-green-100 text-green-800' : (Math.round((result.score / result.total_questions) * 100) >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800')}">
                      {Math.round((result.score / result.total_questions) * 100)}%
                    </span>
                  </td>
                  <td class="py-3 px-4">{result.completion_time || '-'} sec</td>
                  <td class="py-3 px-4">{new Date(result.submitted_at).toLocaleString()}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
</div>