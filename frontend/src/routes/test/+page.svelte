<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';

  let status = 'Testing...';
  let backendUrl = '';
  let healthCheck = '';
  let loginTest = '';

  onMount(async () => {
    // Test 1: Check API base URL
    backendUrl = api.baseURL;
    
    // Test 2: Health check
    try {
      const response = await fetch(`${api.baseURL}/health`);
      const data = await response.json();
      healthCheck = `✅ Backend healthy: ${data.status}`;
    } catch (err) {
      healthCheck = `❌ Health check failed: ${err.message}`;
    }
    
    // Test 3: Login test
    try {
      const result = await api.login('teacher001', 'teacher123');
      loginTest = `✅ Login successful: ${result.user.username} (${result.user.role})`;
    } catch (err) {
      loginTest = `❌ Login failed: ${err.message}`;
    }
    
    status = 'Tests completed';
  });
</script>

<div class="p-8">
  <h1 class="text-2xl font-bold mb-4">API Connection Test</h1>
  
  <div class="space-y-4">
    <div>
      <strong>Status:</strong> {status}
    </div>
    
    <div>
      <strong>Backend URL:</strong> {backendUrl}
    </div>
    
    <div>
      <strong>Health Check:</strong> {healthCheck}
    </div>
    
    <div>
      <strong>Login Test:</strong> {loginTest}
    </div>
  </div>
</div>