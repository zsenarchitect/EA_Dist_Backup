# write to desk top  as a proove that the nitrunner is working.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$testFile = Join-Path -Path $env:USERPROFILE\Desktop -ChildPath "TestTemp.txt"
$testFileContent = "TestTemp.txt"

# write to the test file
Set-Content -Path $testFile -Value $testFileContent

# read from the test file
$testFileContent = Get-Content -Path $testFile

# print the test file content
Write-Output $testFileContent

