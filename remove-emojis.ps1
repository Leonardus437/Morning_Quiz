# Remove all emojis from Svelte files
$files = Get-ChildItem -Path "frontend\src" -Filter "*.svelte" -Recurse

$emojiMap = @{
    '✅' = ''
    '❌' = ''
    '📚' = ''
    '👥' = ''
    '📊' = ''
    '📄' = ''
    '🎯' = ''
    '⚙️' = ''
    '📋' = ''
    '🔧' = ''
    '📤' = ''
    '📥' = ''
    '🚀' = ''
    '💾' = ''
    '🔍' = ''
    '➕' = ''
    '✏️' = ''
    '🗑️' = ''
    '📡' = ''
    '⏳' = ''
    '🔐' = ''
    '🔑' = ''
    '📝' = ''
    '🎓' = ''
    '🏆' = ''
    '⭐' = ''
    '🔔' = ''
    '📅' = ''
    '⏰' = ''
    '🤖' = ''
    '🎮' = ''
    '🔘' = ''
    '🎉' = ''
}

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $modified = $false
    
    foreach ($emoji in $emojiMap.Keys) {
        if ($content -match [regex]::Escape($emoji)) {
            $content = $content -replace [regex]::Escape($emoji), $emojiMap[$emoji]
            $modified = $true
        }
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "Cleaned: $($file.Name)"
    }
}

Write-Host "Done! All emojis removed."
