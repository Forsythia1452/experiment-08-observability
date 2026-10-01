$Root=Split-Path -Parent $PSScriptRoot;$F=Join-Path $Root '.runtime\app.pid';if(Test-Path -LiteralPath $F){Stop-Process -Id ([int](Get-Content -LiteralPath $F)) -ErrorAction SilentlyContinue;Remove-Item -LiteralPath $F -Force};Write-Host '指标应用已停止'

