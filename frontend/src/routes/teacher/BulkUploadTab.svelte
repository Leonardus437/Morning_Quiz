<script>
  import { getApiUrl } from '$lib/api.js';
  
  export let lessons = [];
  export let loading = false;
  export let error = '';
  
  let uploadFile = null;
  let department = 'Software Development';
  let level = 'Level 3';
  let lessonId = null;
  let parsedQuestions = [];
  let showPreview = false;
  let uploading = false;
  
  const departments = ['Software Development', 'Computer System and Architecture', 'Land Surveying', 'Building Construction'];
  const levels = ['Level 3', 'Level 4', 'Level 5'];
  
  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
      const ext = file.name.toLowerCase().split('.').pop();
      if (['txt', 'xlsx', 'xls', 'docx', 'doc', 'pdf'].includes(ext)) {
        uploadFile = file;
        error = '';
      } else {
        error = ' Only Text, Excel, Word, and PDF files are supported';
        uploadFile = null;
      }
    }
  }
  
  async function parseFile() {
    if (!uploadFile || !lessonId) {
      error = 'Please select a file and lesson';
      return;
    }
    
    uploading = true;
    error = '';
    
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('department', department);
      formData.append('level', level);
      formData.append('lesson_id', lessonId);
      
      const token = localStorage.getItem('token');
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/upload-questions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const result = await response.json();
      
      if (result.success) {
        alert(` ${result.message || `Successfully uploaded ${result.created} questions!`}`);
        uploadFile = null;
        showPreview = false;
        window.location.reload();
      } else {
        throw new Error(result.message || 'Upload failed');
      }
      
    } catch (err) {
      error = err.message;
      parsedQuestions = [];
      showPreview = false;
    } finally {
      uploading = false;
    }
  }
</script>

<div>
  <h2 style="margin-bottom: 20px;"> Bulk Question Upload</h2>
  
  <div style="max-width: 800px;">
    {#if error}
      <div style="background: #fee; border: 1px solid #fcc; padding: 10px; margin-bottom: 20px; border-radius: 4px; color: #c00;">
        {error}
      </div>
    {/if}
    
    {#if !showPreview}
      <!-- Upload Form -->
      <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;">
        <h3 style="margin: 0 0 15px 0;">Step 1: Select File</h3>
        <p style="margin: 0 0 15px 0; color: #666; font-size: 14px;">
          Supported formats: Text (.txt), Excel (.xlsx, .xls), Word (.docx), PDF (.pdf)
        </p>
        
        <input 
          type="file" 
          accept=".txt,.xlsx,.xls,.docx,.doc,.pdf"
          on:change={handleFileSelect}
          style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;"
        />
        
        {#if uploadFile}
          <div style="margin-top: 10px; padding: 10px; background: #e7f3ff; border-radius: 4px; font-size: 14px;">
             Selected: {uploadFile.name} ({(uploadFile.size / 1024).toFixed(2)} KB)
          </div>
        {/if}
      </div>
      
      <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;">
        <h3 style="margin: 0 0 15px 0;">Step 2: Select Target</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
          <div>
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Department</label>
            <select bind:value={department} style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
              {#each departments as dept}
                <option value={dept}>{dept}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Level</label>
            <select bind:value={level} style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
              {#each levels as lvl}
                <option value={lvl}>{lvl}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Lesson</label>
            <select bind:value={lessonId} style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
              <option value={null}>Select lesson</option>
              {#each lessons.filter(l => l.department === department && l.level === level) as lesson}
                <option value={lesson.id}>{lesson.title}</option>
              {/each}
            </select>
          </div>
        </div>
      </div>
      
      <button 
        on:click={parseFile}
        disabled={!uploadFile || !lessonId || uploading}
        style="width: 100%; padding: 15px; background: #007cba; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; opacity: {(!uploadFile || !lessonId || uploading) ? '0.5' : '1'};"
      >
        {uploading ? ' Extracting with AI...' : ' Extract Questions with AI'}
      </button>
      
      <div style="margin-top: 15px; padding: 15px; background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 4px; font-size: 14px;">
         <strong>Enhanced AI Parser</strong><br>
        Automatically detects and saves all 5 question types:<br>
         Multiple Choice (MCQ)  True/False  Fill-in-the-Blanks  Short Answer  Code Analysis
      </div>
      
      <!-- Template Download -->
      <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;">
        <h4 style="margin: 0 0 10px 0;"> Need a template?</h4>
        <p style="margin: 0 0 10px 0; font-size: 14px;">Format your questions as: 1. Question text? A) Option B) Option Answer: A</p>
      </div>
    {/if}
  </div>
</div>
