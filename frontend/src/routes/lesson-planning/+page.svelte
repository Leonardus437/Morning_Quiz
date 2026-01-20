<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';

  let user = null;
  let lessons = [];
  let sessionPlans = [];
  let schemesOfWork = [];
  let loading = false;
  let showGenerateModal = false;
  let generationType = 'session_plan';
  let generateForm = {
    lesson_title: '',
    department: '',
    level: '',
    duration_minutes: 90,
    academic_year: '2024-2025',
    term: 'Term 1',
    total_weeks: 12,
    additional_requirements: ''
  };
  let generatedContent = null;
  let generating = false;

  const departments = [
    'Software Development',
    'Computer System and Architecture', 
    'Land Surveying',
    'Building Construction'
  ];

  const levels = ['Level 3', 'Level 4', 'Level 5'];

  onMount(async () => {
    if (browser) {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      if (!token || !userData) {
        goto('/');
        return;
      }

      try {
        user = JSON.parse(userData);
        if (user.role !== 'teacher' && user.role !== 'admin') {
          goto('/');
          return;
        }

        await loadData();
      } catch (error) {
        console.error('Error loading user data:', error);
        goto('/');
      }
    }
  });

  async function loadData() {
    loading = true;
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Load lessons
      const lessonsResponse = await fetch('/api/lessons', { headers });
      if (lessonsResponse.ok) {
        lessons = await lessonsResponse.json();
      }

      // Load session plans
      const plansResponse = await fetch('/api/session-plans', { headers });
      if (plansResponse.ok) {
        sessionPlans = await plansResponse.json();
      }

      // Load schemes of work
      const schemesResponse = await fetch('/api/schemes-of-work', { headers });
      if (schemesResponse.ok) {
        schemesOfWork = await schemesResponse.json();
      }

    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      loading = false;
    }
  }

  async function generateDocument() {
    if (!generateForm.lesson_title || !generateForm.department || !generateForm.level) {
      alert('Please fill in all required fields');
      return;
    }

    generating = true;
    try {
      const token = localStorage.getItem('token');
      const endpoint = generationType === 'session_plan' 
        ? '/api/ai/generate-session-plan'
        : '/api/ai/generate-scheme-of-work';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          generation_type: generationType,
          lesson_title: generateForm.lesson_title,
          department: generateForm.department,
          level: generateForm.level,
          duration_minutes: generateForm.duration_minutes,
          academic_year: generateForm.academic_year,
          term: generateForm.term,
          total_weeks: generateForm.total_weeks,
          additional_requirements: generateForm.additional_requirements
        })
      });

      if (response.ok) {
        const result = await response.json();
        generatedContent = result;
        showGenerateModal = false;
        
        // Show success message
        alert(`${generationType === 'session_plan' ? 'Session Plan' : 'Scheme of Work'} generated successfully! Processing time: ${result.processing_time.toFixed(2)}s`);
        
        // Reload data to show new documents
        await loadData();
      } else {
        const error = await response.json();
        alert(`Generation failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error generating document:', error);
      alert('Failed to generate document. Please try again.');
    } finally {
      generating = false;
    }
  }

  async function exportDocument(type, id) {
    try {
      const token = localStorage.getItem('token');
      const endpoint = type === 'session_plan' 
        ? `/api/session-plans/${id}/export/pdf`
        : `/api/schemes-of-work/${id}/export/pdf`;

      const response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to export document');
      }
    } catch (error) {
      console.error('Error exporting document:', error);
      alert('Failed to export document');
    }
  }

  function openGenerateModal(type) {
    generationType = type;
    showGenerateModal = true;
    generatedContent = null;
  }

  function closeGenerateModal() {
    showGenerateModal = false;
    generateForm = {
      lesson_title: '',
      department: '',
      level: '',
      duration_minutes: 90,
      academic_year: '2024-2025',
      term: 'Term 1',
      total_weeks: 12,
      additional_requirements: ''
    };
  }
</script>

<svelte:head>
  <title>Lesson Planning Portal - Morning Quiz System</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
  <!-- Header -->
  <div class="bg-white shadow-lg border-b-4 border-blue-600">
    <div class="max-w-7xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-xl"></span>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Lesson Planning Portal</h1>
            <p class="text-gray-600">AI-Powered RTB Compliant Document Generation</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">Welcome, {user?.full_name || user?.username}</span>
          <button 
            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            on:click={() => goto('/teacher')}
          >
             Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-6 py-8">
    <!-- Quick Actions -->
    <div class="mb-8">
      <h2 class="text-xl font-bold text-gray-900 mb-4"> Quick Generate</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span class="text-green-600 text-2xl"></span>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Session Plan Generator</h3>
              <p class="text-gray-600 text-sm">Generate detailed lesson session plans in under 1 minute</p>
            </div>
          </div>
          <div class="space-y-2 mb-4">
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              RTB compliant templates
            </div>
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              Learning objectives & assessments
            </div>
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              Professional PDF export
            </div>
          </div>
          <button 
            class="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors"
            on:click={() => openGenerateModal('session_plan')}
          >
             Generate Session Plan
          </button>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span class="text-purple-600 text-2xl"></span>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Scheme of Work Generator</h3>
              <p class="text-gray-600 text-sm">Create comprehensive term/semester planning documents</p>
            </div>
          </div>
          <div class="space-y-2 mb-4">
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              12-week structured breakdown
            </div>
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              Assessment scheduling
            </div>
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              Resource planning
            </div>
          </div>
          <button 
            class="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            on:click={() => openGenerateModal('scheme_of_work')}
          >
             Generate Scheme of Work
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Documents -->
    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Session Plans -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-gray-900"> Recent Session Plans</h3>
          <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            {sessionPlans.length} Plans
          </span>
        </div>

        {#if loading}
          <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        {:else if sessionPlans.length === 0}
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2"></div>
            <p>No session plans yet</p>
            <p class="text-sm">Generate your first session plan above</p>
          </div>
        {:else}
          <div class="space-y-4">
            {#each sessionPlans.slice(0, 5) as plan}
              <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900">{plan.title}</h4>
                    <div class="flex items-center gap-4 mt-1 text-sm text-gray-600">
                      <span> {plan.department}</span>
                      <span> {plan.level}</span>
                      <span> {plan.duration_minutes}min</span>
                    </div>
                    <p class="text-xs text-gray-500 mt-2">
                      Created: {new Date(plan.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button 
                    class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                    on:click={() => exportDocument('session_plan', plan.id)}
                  >
                     Export PDF
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Schemes of Work -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-gray-900"> Recent Schemes of Work</h3>
          <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
            {schemesOfWork.length} Schemes
          </span>
        </div>

        {#if loading}
          <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        {:else if schemesOfWork.length === 0}
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2"></div>
            <p>No schemes of work yet</p>
            <p class="text-sm">Generate your first scheme above</p>
          </div>
        {:else}
          <div class="space-y-4">
            {#each schemesOfWork.slice(0, 5) as scheme}
              <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900">{scheme.title}</h4>
                    <div class="flex items-center gap-4 mt-1 text-sm text-gray-600">
                      <span> {scheme.department}</span>
                      <span> {scheme.level}</span>
                      <span> {scheme.academic_year}</span>
                    </div>
                    <div class="flex items-center gap-4 mt-1 text-sm text-gray-600">
                      <span> {scheme.term}</span>
                      <span> {scheme.total_weeks} weeks</span>
                    </div>
                    <p class="text-xs text-gray-500 mt-2">
                      Created: {new Date(scheme.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button 
                    class="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700 transition-colors"
                    on:click={() => exportDocument('scheme_of_work', scheme.id)}
                  >
                     Export PDF
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- Features Overview -->
    <div class="mt-12 bg-white rounded-xl shadow-lg p-8">
      <h3 class="text-xl font-bold text-gray-900 mb-6 text-center"> Why Use Our AI Lesson Planning System?</h3>
      <div class="grid md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-blue-600 text-2xl"></span>
          </div>
          <h4 class="font-semibold text-gray-900 mb-2">Lightning Fast</h4>
          <p class="text-gray-600 text-sm">Generate professional documents in under 60 seconds with our AI engine</p>
        </div>
        <div class="text-center">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-green-600 text-2xl"></span>
          </div>
          <h4 class="font-semibold text-gray-900 mb-2">RTB Compliant</h4>
          <p class="text-gray-600 text-sm">100% compliant with Rwanda Training Board standards and templates</p>
        </div>
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-purple-600 text-2xl"></span>
          </div>
          <h4 class="font-semibold text-gray-900 mb-2">Professional Output</h4>
          <p class="text-gray-600 text-sm">Beautiful, print-ready PDFs that look exactly like official RTB documents</p>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Generate Modal -->
{#if showGenerateModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">
            {generationType === 'session_plan' ? ' Generate Session Plan' : ' Generate Scheme of Work'}
          </h3>
          <button 
            class="text-gray-400 hover:text-gray-600"
            on:click={closeGenerateModal}
          >
            
          </button>
        </div>
        <p class="text-gray-600 mt-2">
          Fill in the details below and our AI will generate a professional, RTB-compliant document for you.
        </p>
      </div>

      <div class="p-6 space-y-6">
        <!-- Lesson Title -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Lesson/Subject Title *</label>
          <input
            type="text"
            bind:value={generateForm.lesson_title}
            placeholder="e.g., Introduction to Python Programming"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Department and Level -->
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Department *</label>
            <select 
              bind:value={generateForm.department}
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select Department</option>
              {#each departments as dept}
                <option value={dept}>{dept}</option>
              {/each}
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Level *</label>
            <select 
              bind:value={generateForm.level}
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select Level</option>
              {#each levels as level}
                <option value={level}>{level}</option>
              {/each}
            </select>
          </div>
        </div>

        {#if generationType === 'session_plan'}
          <!-- Session Plan Specific Fields -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Duration (minutes)</label>
            <input
              type="number"
              bind:value={generateForm.duration_minutes}
              min="30"
              max="180"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        {:else}
          <!-- Scheme of Work Specific Fields -->
          <div class="grid md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Academic Year</label>
              <input
                type="text"
                bind:value={generateForm.academic_year}
                placeholder="2024-2025"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Term</label>
              <select 
                bind:value={generateForm.term}
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Term 1">Term 1</option>
                <option value="Term 2">Term 2</option>
                <option value="Term 3">Term 3</option>
                <option value="Semester 1">Semester 1</option>
                <option value="Semester 2">Semester 2</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Total Weeks</label>
              <input
                type="number"
                bind:value={generateForm.total_weeks}
                min="8"
                max="16"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        {/if}

        <!-- Additional Requirements -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Additional Requirements (Optional)</label>
          <textarea
            bind:value={generateForm.additional_requirements}
            placeholder="Any specific requirements, focus areas, or special considerations..."
            rows="3"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>

        <!-- AI Features Info -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 class="font-semibold text-blue-900 mb-2"> AI Will Generate:</h4>
          <div class="grid md:grid-cols-2 gap-2 text-sm text-blue-800">
            {#if generationType === 'session_plan'}
              <div> Learning objectives</div>
              <div> Teaching methods</div>
              <div> Resource requirements</div>
              <div> Lesson structure & timing</div>
              <div> Assessment methods</div>
              <div> Homework assignments</div>
            {:else}
              <div> Course overview</div>
              <div> Learning outcomes</div>
              <div> Weekly breakdown</div>
              <div> Assessment schedule</div>
              <div> Resource planning</div>
              <div> Evaluation criteria</div>
            {/if}
          </div>
        </div>
      </div>

      <div class="p-6 border-t border-gray-200 flex gap-4">
        <button 
          class="flex-1 bg-gray-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          on:click={closeGenerateModal}
          disabled={generating}
        >
          Cancel
        </button>
        <button 
          class="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
          on:click={generateDocument}
          disabled={generating || !generateForm.lesson_title || !generateForm.department || !generateForm.level}
        >
          {#if generating}
            <div class="flex items-center justify-center gap-2">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Generating...
            </div>
          {:else}
             Generate Document
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}