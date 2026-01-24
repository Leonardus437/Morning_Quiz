<script>
  import { onMount } from 'svelte';
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  let teachers = [];
  let classTeachers = [];
  let departments = ['Software Development', 'Computer System and Architecture', 'Building Construction', 'Land Surveying'];
  let levels = ['Level 3', 'Level 4', 'Level 5'];
  
  let selectedTeacher = '';
  let selectedDepartment = '';
  let selectedLevel = '';
  let loading = false;
  let message = '';

  onMount(async () => {
    await loadTeachers();
    await loadClassTeachers();
  });

  async function loadTeachers() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/teachers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        teachers = await response.json();
      }
    } catch (error) {
      console.error('Failed to load teachers:', error);
    }
  }

  async function loadClassTeachers() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/admin/class-teachers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        classTeachers = await response.json();
      }
    } catch (error) {
      console.error('Failed to load class teachers:', error);
    }
  }

  async function assignClassTeacher() {
    if (!selectedTeacher || !selectedDepartment || !selectedLevel) {
      message = 'Please select teacher, department, and level';
      return;
    }

    loading = true;
    message = '';

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/admin/assign-class-teacher`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          teacher_id: parseInt(selectedTeacher),
          department: selectedDepartment,
          level: selectedLevel
        })
      });

      if (response.ok) {
        message = 'Class teacher assigned successfully!';
        selectedTeacher = '';
        selectedDepartment = '';
        selectedLevel = '';
        await loadClassTeachers();
      } else {
        const error = await response.json();
        message = `Error: ${error.detail || 'Failed to assign'}`;
      }
    } catch (error) {
      message = `Error: ${error.message}`;
    } finally {
      loading = false;
    }
  }

  async function removeAssignment(assignmentId) {
    if (!confirm('Remove this class teacher assignment?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/admin/class-teacher/${assignmentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        message = 'Assignment removed successfully!';
        await loadClassTeachers();
      }
    } catch (error) {
      message = `Error: ${error.message}`;
    }
  }
</script>

<div class="class-teacher-manager">
  <h2>🎓 Class Teacher Assignments</h2>
  
  <div class="assign-section">
    <h3>Assign Class Teacher</h3>
    
    <div class="form-grid">
      <div class="form-group">
        <label>Teacher</label>
        <select bind:value={selectedTeacher}>
          <option value="">Select Teacher</option>
          {#each teachers as teacher}
            <option value={teacher.id}>{teacher.full_name}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label>Department</label>
        <select bind:value={selectedDepartment}>
          <option value="">Select Department</option>
          {#each departments as dept}
            <option value={dept}>{dept}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label>Level</label>
        <select bind:value={selectedLevel}>
          <option value="">Select Level</option>
          {#each levels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </div>
    </div>

    <button on:click={assignClassTeacher} disabled={loading} class="btn-primary">
      {loading ? 'Assigning...' : 'Assign Class Teacher'}
    </button>

    {#if message}
      <div class="message" class:error={message.includes('Error')}>
        {message}
      </div>
    {/if}
  </div>

  <div class="assignments-list">
    <h3>Current Assignments</h3>
    
    {#if classTeachers.length === 0}
      <p class="empty">No class teachers assigned yet</p>
    {:else}
      <table>
        <thead>
          <tr>
            <th>Teacher</th>
            <th>Department</th>
            <th>Level</th>
            <th>Assigned</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {#each classTeachers as assignment}
            <tr>
              <td>{assignment.teacher_name}</td>
              <td>{assignment.department}</td>
              <td>{assignment.level}</td>
              <td>{new Date(assignment.assigned_at).toLocaleDateString()}</td>
              <td>
                <button on:click={() => removeAssignment(assignment.id)} class="btn-danger">
                  Remove
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>
</div>

<style>
  .class-teacher-manager {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  h2 {
    color: #1a5490;
    margin-bottom: 30px;
  }

  h3 {
    color: #333;
    margin-bottom: 15px;
  }

  .assign-section {
    background: white;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 30px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 5px;
    color: #555;
  }

  select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .btn-primary {
    background: #1a5490;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
  }

  .btn-primary:hover {
    background: #134070;
  }

  .btn-primary:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .message {
    margin-top: 15px;
    padding: 12px;
    border-radius: 4px;
    background: #d4edda;
    color: #155724;
  }

  .message.error {
    background: #f8d7da;
    color: #721c24;
  }

  .assignments-list {
    background: white;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  thead {
    background: #f8f9fa;
  }

  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    font-weight: 600;
    color: #555;
  }

  .btn-danger {
    background: #dc3545;
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }

  .btn-danger:hover {
    background: #c82333;
  }

  .empty {
    text-align: center;
    color: #999;
    padding: 40px;
  }
</style>
