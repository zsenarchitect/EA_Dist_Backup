@echo off
REM Remove any existing task with the same name (ignore errors)
schtasks /delete /tn "NightRunner" /f >nul 2>&1

REM Register the new task to run every day at midnight
schtasks /create ^
  /tn "NightRunner" ^
  /tr "powershell.exe -ExecutionPolicy Bypass -File \"L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\NightRunner.ps\"" ^
  /sc daily ^
  /st 00:00 ^
  /rl LIMITED ^
  /f ^
  /ru %USERNAME% >nul 2>&1

REM Remove any existing hourly pin connection task
schtasks /delete /tn "PinConnection" /f >nul 2>&1

REM Register the new hourly task
schtasks /create ^
  /tn "PinConnection" ^
  /tr "powershell.exe -ExecutionPolicy Bypass -File \"L:\4b_Applied Computing\EnneadTab-DB\PinConnection.ps1\"" ^
  /sc hourly ^
  /rl LIMITED ^
  /f ^
  /ru %USERNAME% >nul 2>&1

echo All register suscefful. You may close this window
pause