param(
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'
$taskName = 'religions-history-pipeline-supervisor'

if ($Remove) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $taskName"
    exit 0
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$supervisor = Join-Path $PSScriptRoot 'supervise-pipeline.py'
$pythonw = (Get-Command pythonw.exe -ErrorAction Stop).Source
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$supervisor`" 核心" -WorkingDirectory $projectRoot
$atLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$watchdog = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun:$false `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 10)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($atLogon, $watchdog) `
    -Settings $settings -Principal $principal `
    -Description 'Restarts the checkpointed religions-history supervisor after logon/sleep; locks prevent duplicate generation.' `
    -Force | Out-Null
Write-Host "Installed scheduled task: $taskName"
Write-Host 'HALT and quota/provider waiting states remain authoritative; this task cannot bypass them.'
