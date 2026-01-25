<script>
  export let question;
  export let answer = '';
  export let disabled = false;
  
  let selectedOptions = [];
  let blanks = [];
  let matches = [];
  let order = [];
  let code = '';
  let gridAnswers = {};
  
  $: if (question.question_type === 'multiple_select') {
    selectedOptions = answer ? answer.split(',') : [];
  }
  
  $: if (question.question_type === 'fill_blanks') {
    blanks = answer ? answer.split('|||') : Array((question.question_config?.blanks || []).length).fill('');
  }
  
  $: if (question.question_type === 'drag_drop_match') {
    matches = answer ? answer.split('|||') : Array((question.question_config?.pairs || []).length).fill('');
  }
  
  $: if (question.question_type === 'drag_drop_order') {
    order = answer ? answer.split(',').map(Number) : (question.question_config?.items || []).map((_, i) => i);
  }
  
  $: if (question.question_type === 'multi_grid') {
    try {
      gridAnswers = answer ? JSON.parse(answer) : {};
    } catch {
      gridAnswers = {};
    }
  }
  
  function handleMultipleSelect(option) {
    if (disabled) return;
    const idx = selectedOptions.indexOf(option);
    if (idx > -1) {
      selectedOptions = selectedOptions.filter(o => o !== option);
    } else {
      selectedOptions = [...selectedOptions, option];
    }
    answer = selectedOptions.join(',');
  }
  
  function handleBlankChange(index, value) {
    blanks[index] = value;
    answer = blanks.join('|||');
  }
  
  function handleMatchChange(index, value) {
    matches[index] = value;
    answer = matches.join('|||');
  }
  
  function moveUp(index) {
    if (index === 0) return;
    [order[index], order[index - 1]] = [order[index - 1], order[index]];
    order = [...order];
    answer = order.join(',');
  }
  
  function moveDown(index) {
    if (index === order.length - 1) return;
    [order[index], order[index + 1]] = [order[index + 1], order[index]];
    order = [...order];
    answer = order.join(',');
  }
  
  function getGridAnswer(rowIndex) {
    return gridAnswers[rowIndex] || '';
  }
  
  function handleGridChange(rowIndex, columnValue) {
    if (disabled) return;
    gridAnswers[rowIndex] = columnValue;
    gridAnswers = {...gridAnswers};
    answer = JSON.stringify(gridAnswers);
  }
</script>

{#if question.question_type === 'multiple_choice' || question.question_type === 'true_false'}
  <div class="options">
    {#each question.options || [] as option}
      <label class="option">
        <input type="radio" bind:group={answer} value={option} {disabled} />
        <span>{option}</span>
      </label>
    {/each}
  </div>

{:else if question.question_type === 'multiple_select'}
  <div class="options">
    {#each question.options || [] as option}
      <label class="option checkbox">
        <input 
          type="checkbox" 
          checked={selectedOptions.includes(option)}
          on:change={() => handleMultipleSelect(option)}
          {disabled}
        />
        <span>{option}</span>
      </label>
    {/each}
  </div>

{:else if question.question_type === 'dropdown'}
  <select bind:value={answer} {disabled} class="dropdown">
    <option value="">-- Select Answer --</option>
    {#each question.options || [] as option}
      <option value={option}>{option}</option>
    {/each}
  </select>

{:else if question.question_type === 'fill_blanks'}
  <div class="fill-blanks">
    {#each (question.question_config?.blanks || []) as blank, i}
      <div class="blank-item">
        <label>Blank {i + 1}:</label>
        <input 
          type="text" 
          value={blanks[i] || ''} 
          on:input={(e) => handleBlankChange(i, e.target.value)}
          {disabled}
          placeholder="Enter answer..."
        />
      </div>
    {/each}
  </div>

{:else if question.question_type === 'drag_drop_match'}
  <div class="matching">
    {#each (question.question_config?.pairs || []) as pair, i}
      <div class="match-row">
        <span class="left">{pair.left}</span>
        <select 
          value={matches[i] || ''} 
          on:change={(e) => handleMatchChange(i, e.target.value)}
          {disabled}
        >
          <option value="">-- Match --</option>
          {#each (question.question_config?.pairs || []) as p}
            <option value={p.right}>{p.right}</option>
          {/each}
        </select>
      </div>
    {/each}
  </div>

{:else if question.question_type === 'drag_drop_order'}
  <div class="ordering">
    {#each order as idx, i}
      <div class="order-item">
        <span class="number">{i + 1}</span>
        <span class="text">{(question.question_config?.items || [])[idx]}</span>
        <div class="controls">
          <button on:click={() => moveUp(i)} {disabled} type="button">↑</button>
          <button on:click={() => moveDown(i)} {disabled} type="button">↓</button>
        </div>
      </div>
    {/each}
  </div>

{:else if question.question_type === 'linear_scale'}
  <div class="linear-scale">
    <div class="scale-labels">
      <span>{question.question_config?.min_label || 'Low'}</span>
      <span>{question.question_config?.max_label || 'High'}</span>
    </div>
    <div class="scale-options">
      {#each Array(question.question_config?.max_value || 10) as _, i}
        <label class="scale-option">
          <input type="radio" bind:group={answer} value={String(i + 1)} {disabled} />
          <span>{i + 1}</span>
        </label>
      {/each}
    </div>
  </div>

{:else if question.question_type === 'code_writing'}
  <div class="code-editor">
    <div class="language-badge">{question.question_config?.language || 'python'}</div>
    <textarea 
      bind:value={answer} 
      {disabled}
      placeholder="Write your code here..."
      rows="15"
      spellcheck="false"
    ></textarea>
  </div>

{:else if question.question_type === 'sql_query'}
  <div class="sql-editor">
    <div class="schema-info">
      <strong>Schema:</strong> {question.question_config?.schema || 'N/A'}
    </div>
    <textarea 
      bind:value={answer} 
      {disabled}
      placeholder="Write your SQL query here..."
      rows="8"
      spellcheck="false"
    ></textarea>
  </div>

{:else if question.question_type === 'multi_grid'}
  <div class="multi-grid">
    {#if question.question_config?.rows && question.question_config?.columns}
      <div class="grid-table">
        <table>
          <thead>
            <tr>
              <th class="row-header">Items</th>
              {#each question.question_config.columns as column}
                <th class="column-header">{column}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each question.question_config.rows as row, rowIndex}
              <tr>
                <td class="row-label">{row}</td>
                {#each question.question_config.columns as column, colIndex}
                  <td class="grid-cell">
                    <input 
                      type="radio" 
                      name="grid_row_{rowIndex}" 
                      value={column}
                      checked={getGridAnswer(rowIndex) === column}
                      on:change={() => handleGridChange(rowIndex, column)}
                      {disabled}
                    />
                  </td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="error">Multi-grid configuration missing</p>
    {/if}
  </div>

{:else if question.question_type === 'short_answer'}
  <input type="text" bind:value={answer} {disabled} placeholder="Enter your answer..." />

{:else if question.question_type === 'essay'}
  <textarea bind:value={answer} {disabled} placeholder="Write your essay here..." rows="8"></textarea>

{:else}
  <p class="error">Unknown question type: {question.question_type}</p>
{/if}

<style>
  .options { display: flex; flex-direction: column; gap: 12px; }
  .option { display: flex; align-items: center; gap: 10px; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
  .option:hover { border-color: #4CAF50; background: #f9f9f9; }
  .option input { width: 20px; height: 20px; cursor: pointer; }
  .option span { font-size: 16px; }
  
  .dropdown { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; }
  
  .fill-blanks { display: flex; flex-direction: column; gap: 15px; }
  .blank-item { display: flex; flex-direction: column; gap: 5px; }
  .blank-item label { font-weight: 600; color: #333; }
  .blank-item input { padding: 10px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 15px; }
  
  .matching { display: flex; flex-direction: column; gap: 12px; }
  .match-row { display: flex; align-items: center; gap: 15px; padding: 10px; background: #f5f5f5; border-radius: 6px; }
  .match-row .left { flex: 1; font-weight: 600; }
  .match-row select { flex: 1; padding: 8px; border: 2px solid #ddd; border-radius: 6px; }
  
  .ordering { display: flex; flex-direction: column; gap: 10px; }
  .order-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f9f9f9; border: 2px solid #e0e0e0; border-radius: 8px; }
  .order-item .number { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: #4CAF50; color: white; border-radius: 50%; font-weight: bold; }
  .order-item .text { flex: 1; font-size: 15px; }
  .order-item .controls { display: flex; gap: 5px; }
  .order-item button { padding: 5px 12px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
  .order-item button:hover { background: #1976D2; }
  .order-item button:disabled { background: #ccc; cursor: not-allowed; }
  
  .linear-scale { display: flex; flex-direction: column; gap: 15px; }
  .scale-labels { display: flex; justify-content: space-between; font-size: 14px; color: #666; }
  .scale-options { display: flex; gap: 8px; flex-wrap: wrap; }
  .scale-option { display: flex; flex-direction: column; align-items: center; gap: 5px; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; min-width: 50px; }
  .scale-option:hover { border-color: #4CAF50; background: #f9f9f9; }
  .scale-option input { display: none; }
  .scale-option:has(input:checked) { border-color: #4CAF50; background: #e8f5e9; }
  
  .code-editor, .sql-editor { position: relative; }
  .language-badge { position: absolute; top: 10px; right: 10px; padding: 4px 12px; background: #333; color: white; border-radius: 4px; font-size: 12px; text-transform: uppercase; z-index: 1; }
  .schema-info { margin-bottom: 10px; padding: 10px; background: #f5f5f5; border-radius: 6px; font-size: 14px; }
  textarea { width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 14px; resize: vertical; }
  
  input[type="text"] { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; }
  
  .error { color: #f44336; padding: 20px; background: #ffebee; border-radius: 8px; text-align: center; }
  
  .multi-grid { margin: 20px 0; }
  .grid-table { overflow-x: auto; }
  .grid-table table { width: 100%; border-collapse: collapse; border: 2px solid #e0e0e0; }
  .grid-table th, .grid-table td { padding: 12px; border: 1px solid #e0e0e0; text-align: center; }
  .grid-table th { background: #f5f5f5; font-weight: 600; }
  .row-header { background: #4CAF50; color: white; text-align: left; }
  .column-header { background: #2196F3; color: white; }
  .row-label { background: #f9f9f9; font-weight: 500; text-align: left; }
  .grid-cell { background: white; }
  .grid-cell input[type="radio"] { width: 20px; height: 20px; cursor: pointer; }
</style>
