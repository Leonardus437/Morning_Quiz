<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to admin panel with quiz dashboard tab
    goto('/admin?tab=quiz-dashboard');
  });
</script>

<div style="text-align: center; padding: 50px;">
  <p>Redirecting to Quiz Dashboard...</p>
</div>