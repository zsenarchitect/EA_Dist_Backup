# This script is used to run the NightRunner.ps1 script every day at midnight.
# if not action needed, do nothing.
# show no console by default, unless specifically asked to open console by the ps.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$actionScripts = Get-ChildItem -Path $scriptDir -Filter 'NightRunnerAction_*.ps1' -File

if ($actionScripts.Count -eq 0) {
    # do nothing if no NightRunnerAction_xxxx.ps1 is found.
    return
}

foreach ($script in $actionScripts) {
    try {
        # Run each script, skip if any fails, always hidden
        Start-Process -FilePath 'powershell.exe' -ArgumentList "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `\"$($script.FullName)`\"" -WindowStyle Hidden -NoNewWindow -Wait
    } catch {
        # Skip failed script
        continue
    }
}