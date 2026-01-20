Write-Host "Killing processes on port 3000..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object {
    $processId = $_.OwningProcess
    Write-Host "Killing process $processId" -ForegroundColor Red
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}
Write-Host "Done!" -ForegroundColor Green
Read-Host "Press Enter to continue"