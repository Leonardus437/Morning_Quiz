<script>
  export let variant = 'primary'; // primary, secondary, success, danger, warning
  export let size = 'md'; // sm, md, lg
  export let disabled = false;
  export let loading = false;
  export let icon = null;
  export let iconRight = false;
  export let fullWidth = false;
  
  const variants = {
    primary: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300',
    success: 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl',
    danger: 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white shadow-lg hover:shadow-xl',
    warning: 'bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white shadow-lg hover:shadow-xl'
  };
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };
</script>

<button
  class="
    {variants[variant]}
    {sizes[size]}
    {fullWidth ? 'w-full' : ''}
    rounded-xl font-semibold
    transition-all duration-300
    transform hover:scale-105
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
    flex items-center justify-center gap-2
    focus:outline-none focus:ring-4 focus:ring-blue-300
  "
  {disabled}
  on:click
>
  {#if loading}
    <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  {:else if icon && !iconRight}
    <svelte:component this={icon} class="w-5 h-5" />
  {/if}
  
  <slot />
  
  {#if icon && iconRight && !loading}
    <svelte:component this={icon} class="w-5 h-5" />
  {/if}
</button>
