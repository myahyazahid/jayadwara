Get-Process UnrealEditor,CrashReportClient,UnrealEditor-Cmd -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
$exe = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe"
$proj = "C:\repository\unreal_engine\jayadwara_hermes_combo\Jayadwara.uproject"
Write-Output (Test-Path $exe) (Test-Path $proj)
Start-Process -FilePath $exe -ArgumentList $proj
Write-Output "started"
