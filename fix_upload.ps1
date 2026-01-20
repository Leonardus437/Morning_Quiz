$file = "frontend\src\routes\admin\+page.svelte"
$content = Get-Content $file -Raw

$old = "formData.append('file', uploadFile);"
$new = @"
formData.append('file', uploadFile);
      formData.append('department', uploadSelectedDepartment || 'General');
      formData.append('level', uploadSelectedLevel || 'Level 5');
"@

$content = $content.Replace($old, $new)
Set-Content $file -Value $content -NoNewline

Write-Host "Fixed upload form"
