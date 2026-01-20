<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';
  
  let departments = ['Computer Science', 'Land Surveying', 'Civil Engineering', 'Electrical Engineering'];
  let levels = ['L1', 'L2', 'L3', 'L4'];
  let reportTypes = ['daily', 'weekly', 'monthly'];
  
  let selectedDepartment = '';
  let selectedLevel = '';
  let selectedReportType = 'daily';
  let selectedDate = new Date().toISOString().split('T')[0];
  let loading = false;

  async function downloadReport(format) {
    if (!selectedDepartment || !selectedLevel) {
      alert('Please select department and level');
      return;
    }
    
    loading = true;
    try {
      const params = {
        department: selectedDepartment,
        level: selectedLevel,
        reportType: selectedReportType,
        date: selectedDate
      };
      
      if (format === 'pdf') {
        await api.downloadDepartmentReport(params);
      } else {
        await api.downloadDepartmentReportExcel(params);
      }
    } catch (error) {
      alert('Failed to download report');
    } finally {
      loading = false;
    }
  }
</script>

<div class="container mx-auto p-4">
  <h1 class="text-3xl font-bold mb-6">Department Reports</h1>
  
  <div class="bg-white rounded-lg shadow p-6 mb-6">
    <h2 class="text-xl font-semibold mb-4">Generate Report</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
      <div>
        <label class="block text-sm font-medium mb-2">Department</label>
        <select bind:value={selectedDepartment} class="w-full p-2 border rounded">
          <option value="">Select Department</option>
          {#each departments as dept}
            <option value={dept}>{dept}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-2">Level</label>
        <select bind:value={selectedLevel} class="w-full p-2 border rounded">
          <option value="">Select Level</option>
          {#each levels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-2">Report Type</label>
        <select bind:value={selectedReportType} class="w-full p-2 border rounded">
          {#each reportTypes as type}
            <option value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
          {/each}
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-2">Date</label>
        <input type="date" bind:value={selectedDate} class="w-full p-2 border rounded">
      </div>
    </div>
    
    <div class="flex gap-4">
      <button 
        on:click={() => downloadReport('pdf')}
        disabled={loading}
        class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Download PDF'}
      </button>
      
      <button 
        on:click={() => downloadReport('excel')}
        disabled={loading}
        class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Download Excel'}
      </button>
    </div>
  </div>
  
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <h3 class="font-semibold text-blue-800 mb-2">Report Information</h3>
    <ul class="text-sm text-blue-700 space-y-1">
      <li> Daily: Shows quiz results for the selected date</li>
      <li> Weekly: Shows quiz results for the week containing the selected date</li>
      <li> Monthly: Shows quiz results for the month containing the selected date</li>
      <li> Reports include student performance, rankings, and statistics</li>
    </ul>
  </div>
</div>