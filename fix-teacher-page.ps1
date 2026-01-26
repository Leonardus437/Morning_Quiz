# Fix teacher page - Add Review button
$file = "d:\Morning_Quiz-master\frontend\src\routes\teacher\+page.svelte.backup"
$output = "d:\Morning_Quiz-master\frontend\src\routes\teacher\+page.svelte"

$content = Get-Content $file -Raw

# Find the Students button and add Review button before it
$studentsButton = @"
          <button
            class="flex-1 px-6 py-3 rounded-lg font-medium transition-all {activeTab === 'students' ? 'bg-green-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}"
            on:click={() => activeTab = 'students'}
          >
            📚 Students
          </button>
"@

$reviewAndStudentsButtons = @"
          <a
            href="/teacher/reviews"
            class="flex-1 px-6 py-3 rounded-lg font-medium text-center transition-all text-gray-600 hover:text-gray-800 hover:bg-gray-50 no-underline"
          >
            📋 Review
          </a>
"@

$content = $content -replace [regex]::Escape($studentsButton), $reviewAndStudentsButtons

Set-Content -Path $output -Value $content -NoNewline

Write-Host 'Teacher page fixed with Review button added'
Write-Host 'File saved to:' $output
