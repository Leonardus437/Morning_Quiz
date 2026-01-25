<script>
  export let onSave;
  export let departments = [];
  export let levels = [];
  
  let questionType = 'multiple_choice';
  let questionText = '';
  let options = ['', '', '', ''];
  let correctAnswer = '';
  let points = 1;
  let department = '';
  let level = '';
  
  // Advanced type configs
  let correctAnswers = [];
  let partialCredit = false;
  let blanks = [{answer: ''}];
  let pairs = [{left: '', right: ''}];
  let items = [''];
  let minValue = 1;
  let maxValue = 10;
  let minLabel = 'Low';
  let maxLabel = 'High';
  let language = 'python';
  let schema = '';
  
  const questionTypes = [
    {value: 'multiple_choice', label: 'Multiple Choice (Single)'},
    {value: 'multiple_select', label: 'Multiple Select (Checkboxes)'},
    {value: 'true_false', label: 'True/False'},
    {value: 'dropdown', label: 'Dropdown Select'},
    {value: 'fill_blanks', label: 'Fill in the Blanks'},
    {value: 'drag_drop_match', label: 'Matching Pairs'},
    {value: 'drag_drop_order', label: 'Drag & Drop Ordering'},
    {value: 'linear_scale', label: 'Linear Scale (Rating)'},
    {value: 'code_writing', label: 'Code Writing'},
    {value: 'sql_query', label: 'SQL Query'},
    {value: 'short_answer', label: 'Short Answer'},
    {value: 'essay', label: 'Essay/Paragraph'}
  ];
  
  function addOption() { options = [...options, '']; }
  function removeOption(i) { options = options.filter((_, idx) => idx !== i); }
  function addBlank() { blanks = [...blanks, {answer: ''}]; }
  function removeBlank(i) { blanks = blanks.filter((_, idx) => idx !== i); }
  function addPair() { pairs = [...pairs, {left: '', right: ''}]; }
  function removePair(i) { pairs = pairs.filter((_, idx) => idx !== i); }
  function addItem() { items = [...items, '']; }
  function removeItem(i) { items = items.filter((_, idx) => idx !== i); }
  
  function handleSave() {
    const config = {};
    
    if (questionType === 'multiple_select') {
      config.correct_answers = correctAnswers;
      config.partial_credit = partialCredit;
    } else if (questionType === 'fill_blanks') {
      config.question_config = {blanks: blanks.map((b, i) => ({position: i, answer: b.answer}))};
    } else if (questionType === 'drag_drop_match') {
      config.question_config = {pairs};
    } else if (questionType === 'drag_drop_order') {
      config.question_config = {items, correct_order: items.map((_, i) => i)};
    } else if (questionType === 'linear_scale') {
      config.question_config = {min_value: minValue, max_value: maxValue, min_label: minLabel, max_label: maxLabel};
    } else if (questionType === 'code_writing') {
      config.question_config = {language};
    } else if (questionType === 'sql_query') {
      config.question_config = {schema};
    }
    
    onSave({
      question_text: questionText,
      question_type: questionType,
      options: ['multiple_choice', 'multiple_select', 'true_false', 'dropdown'].includes(questionType) ? options.filter(o => o.trim()) : null,
      correct_answer: correctAnswer,
      points,
      department,
      level,
      ...config
    });
  }
</script>

<div class="creator">
  <h3>Create Question</h3>
  
  <div class="form-group">
    <label>Question Type</label>
    <select bind:value={questionType}>
      {#each questionTypes as type}
        <option value={type.value}>{type.label}</option>
      {/each}
    </select>
  </div>
  
  <div class="form-group">
    <label>Question Text</label>
    <textarea bind:value={questionText} rows="3" placeholder="Enter your question..."></textarea>
  </div>
  
  {#if ['multiple_choice', 'multiple_select', 'true_false', 'dropdown'].includes(questionType)}
    <div class="form-group">
      <label>Options</label>
      {#each options as option, i}
        <div class="option-row">
          <input type="text" bind:value={options[i]} placeholder="Option {i + 1}" />
          {#if options.length > 2}
            <button type="button" on:click={() => removeOption(i)}>✕</button>
          {/if}
        </div>
      {/each}
      <button type="button" on:click={addOption} class="add-btn">+ Add Option</button>
    </div>
    
    {#if questionType === 'multiple_select'}
      <div class="form-group">
        <label>Correct Answers (select multiple)</label>
        {#each options.filter(o => o.trim()) as option}
          <label class="checkbox-label">
            <input type="checkbox" bind:group={correctAnswers} value={option} />
            {option}
          </label>
        {/each}
        <label class="checkbox-label">
          <input type="checkbox" bind:checked={partialCredit} />
          Allow partial credit
        </label>
      </div>
    {:else}
      <div class="form-group">
        <label>Correct Answer</label>
        <select bind:value={correctAnswer}>
          <option value="">-- Select --</option>
          {#each options.filter(o => o.trim()) as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
    {/if}
  
  {:else if questionType === 'fill_blanks'}
    <div class="form-group">
      <label>Blanks</label>
      {#each blanks as blank, i}
        <div class="option-row">
          <input type="text" bind:value={blanks[i].answer} placeholder="Correct answer for blank {i + 1}" />
          {#if blanks.length > 1}
            <button type="button" on:click={() => removeBlank(i)}>✕</button>
          {/if}
        </div>
      {/each}
      <button type="button" on:click={addBlank} class="add-btn">+ Add Blank</button>
    </div>
  
  {:else if questionType === 'drag_drop_match'}
    <div class="form-group">
      <label>Matching Pairs</label>
      {#each pairs as pair, i}
        <div class="pair-row">
          <input type="text" bind:value={pairs[i].left} placeholder="Left item" />
          <span>→</span>
          <input type="text" bind:value={pairs[i].right} placeholder="Right item" />
          {#if pairs.length > 1}
            <button type="button" on:click={() => removePair(i)}>✕</button>
          {/if}
        </div>
      {/each}
      <button type="button" on:click={addPair} class="add-btn">+ Add Pair</button>
    </div>
  
  {:else if questionType === 'drag_drop_order'}
    <div class="form-group">
      <label>Items to Order (in correct sequence)</label>
      {#each items as item, i}
        <div class="option-row">
          <span class="order-num">{i + 1}</span>
          <input type="text" bind:value={items[i]} placeholder="Item {i + 1}" />
          {#if items.length > 2}
            <button type="button" on:click={() => removeItem(i)}>✕</button>
          {/if}
        </div>
      {/each}
      <button type="button" on:click={addItem} class="add-btn">+ Add Item</button>
    </div>
  
  {:else if questionType === 'linear_scale'}
    <div class="form-group">
      <label>Scale Range</label>
      <div class="scale-config">
        <input type="number" bind:value={minValue} min="1" placeholder="Min" />
        <span>to</span>
        <input type="number" bind:value={maxValue} max="10" placeholder="Max" />
      </div>
      <input type="text" bind:value={minLabel} placeholder="Min label (e.g., 'Poor')" />
      <input type="text" bind:value={maxLabel} placeholder="Max label (e.g., 'Excellent')" />
    </div>
  
  {:else if questionType === 'code_writing'}
    <div class="form-group">
      <label>Programming Language</label>
      <select bind:value={language}>
        <option value="python">Python</option>
        <option value="java">Java</option>
        <option value="cpp">C++</option>
        <option value="javascript">JavaScript</option>
        <option value="c">C</option>
      </select>
    </div>
    <div class="form-group">
      <label>Expected Answer/Solution</label>
      <textarea bind:value={correctAnswer} rows="8" placeholder="Enter expected code solution..."></textarea>
    </div>
  
  {:else if questionType === 'sql_query'}
    <div class="form-group">
      <label>Database Schema</label>
      <input type="text" bind:value={schema} placeholder="e.g., students(id, name, age, grade)" />
    </div>
    <div class="form-group">
      <label>Expected Query</label>
      <textarea bind:value={correctAnswer} rows="5" placeholder="Enter expected SQL query..."></textarea>
    </div>
  
  {:else}
    <div class="form-group">
      <label>Expected Answer</label>
      <textarea bind:value={correctAnswer} rows="4" placeholder="Enter expected answer..."></textarea>
    </div>
  {/if}
  
  <div class="form-row">
    <div class="form-group">
      <label>Department</label>
      <select bind:value={department}>
        <option value="">-- Select --</option>
        {#each departments as dept}
          <option value={dept}>{dept}</option>
        {/each}
      </select>
    </div>
    
    <div class="form-group">
      <label>Level</label>
      <select bind:value={level}>
        <option value="">-- Select --</option>
        {#each levels as lvl}
          <option value={lvl}>{lvl}</option>
        {/each}
      </select>
    </div>
    
    <div class="form-group">
      <label>Points</label>
      <input type="number" bind:value={points} min="1" max="100" />
    </div>
  </div>
  
  <button class="save-btn" on:click={handleSave}>Save Question</button>
</div>

<style>
  .creator { max-width: 800px; margin: 0 auto; padding: 20px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h3 { margin: 0 0 20px; color: #333; }
  .form-group { margin-bottom: 20px; }
  .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
  .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 15px; }
  .form-row { display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 15px; }
  .option-row, .pair-row { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
  .option-row input, .pair-row input { flex: 1; }
  .option-row button, .pair-row button { padding: 8px 12px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; }
  .order-num { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: #4CAF50; color: white; border-radius: 50%; font-weight: bold; }
  .pair-row span { color: #666; font-size: 20px; }
  .scale-config { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
  .scale-config input { width: 80px; }
  .add-btn { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
  .add-btn:hover { background: #1976D2; }
  .save-btn { width: 100%; padding: 15px; background: #4CAF50; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 20px; }
  .save-btn:hover { background: #45a049; }
  .checkbox-label { display: flex; align-items: center; gap: 8px; padding: 8px; }
  .checkbox-label input { width: auto; }
</style>
