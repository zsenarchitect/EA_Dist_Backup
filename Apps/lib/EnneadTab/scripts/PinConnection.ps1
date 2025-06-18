$sharedFolder = "L:\4b_Applied Computing\EnneadTab-DB\Shared Data Dump"
$user = $env:USERNAME
$pc = $env:COMPUTERNAME
$file = "PINCONNECTION_${user}_${pc}.DuckPin"
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$content = "Last check-in: $date"

try {
    Set-Content -Path (Join-Path $sharedFolder $file) -Value $content -ErrorAction Stop
}
catch {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("Your L drive is disconnected, please reconnect.", "Network Connection Error", "OK", "Error")
} 