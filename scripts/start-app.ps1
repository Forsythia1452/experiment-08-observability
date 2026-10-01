$Root=Split-Path -Parent $PSScriptRoot;$Python=Join-Path $Root '.venv\Scripts\python.exe';if(-not(Test-Path -LiteralPath $Python)){throw '请先安装 requirements.txt'}
$Run=Join-Path $Root '.runtime';New-Item -ItemType Directory -Force -Path $Run|Out-Null
$P=Start-Process -FilePath $Python -ArgumentList @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8008') -WorkingDirectory $Root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Run 'app.log') -RedirectStandardError (Join-Path $Run 'app-error.log');$P.Id|Set-Content -LiteralPath (Join-Path $Run 'app.pid');Write-Host '指标应用：http://127.0.0.1:8008  metrics：http://127.0.0.1:8008/metrics'

