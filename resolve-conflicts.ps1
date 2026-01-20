$files = @(
    "frontend\src\routes\quiz\[id]\+page.svelte",
    "frontend\src\routes\results\[id]\+page.svelte",
    "frontend\src\routes\teacher\+page.svelte"
)

foreach ($file in $files) {
    $content = Get-Content $file -Encoding UTF8 | Out-String
    $content = $content -replace '(?s)<<<<<<< HEAD\r?\n', ''
    $content = $content -replace '(?s)=======\r?\n.*?>>>>>>> [a-f0-9]+\r?\n', ''
    [System.IO.File]::WriteAllText("$PWD\$file", $content)
    Write-Host "Fixed: $file"
}

Write-Host "`nAll conflicts resolved!"
