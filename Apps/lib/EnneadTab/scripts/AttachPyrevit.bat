@echo off
setlocal enabledelayedexpansion

echo [INFO] Attaching pyRevit to all installed Revit versions...

REM Check if pyRevit clones exist first
echo [INFO] Checking available pyRevit clones...
pyrevit clones
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to check pyRevit clones. pyRevit CLI may not be properly installed.
    goto :error
)

REM Get user's Revit addins directory
set "USER_ADDINS_DIR=%APPDATA%\Autodesk\Revit\Addins"
echo [INFO] User addins directory: %USER_ADDINS_DIR%

REM Create user-level pyRevit addin files for each installed Revit version
for %%v in (2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030) do (
    if exist "%USER_ADDINS_DIR%\%%v" (
        echo [INFO] Creating pyRevit installation for Revit %%v...
        call :CreateUserAddin %%v
    )
)

echo [INFO] Checking final installation status...
pyrevit attached

goto :end

:CreateUserAddin
set "REVIT_YEAR=%1"
set "ADDIN_DIR=%USER_ADDINS_DIR%\%REVIT_YEAR%"
set "ADDIN_FILE=%ADDIN_DIR%\pyRevit.addin"

echo [INFO] Creating pyRevit addin for Revit %REVIT_YEAR%...

REM Create the pyRevit addin file (will overwrite if exists)
echo ^<?xml version="1.0" encoding="utf-8"?^> > "%ADDIN_FILE%"
echo ^<RevitAddIns^> >> "%ADDIN_FILE%"
echo   ^<AddIn Type="Application"^> >> "%ADDIN_FILE%"
echo     ^<Name^>pyRevit^</Name^> >> "%ADDIN_FILE%"
echo     ^<Assembly^>C:\pyRevit-Master\bin\netfx\engines\IPY2712PR\pyRevitLoader.dll^</Assembly^> >> "%ADDIN_FILE%"
echo     ^<AddInId^>B39107C3-A1D7-47F4-A5A1-532DDF6EDB5D^</AddInId^> >> "%ADDIN_FILE%"
echo     ^<FullClassName^>PyRevitLoader.PyRevitLoaderApplication^</FullClassName^> >> "%ADDIN_FILE%"
echo     ^<VendorId^>pyRevit^</VendorId^> >> "%ADDIN_FILE%"
echo     ^<VendorDescription^>pyRevit^</VendorDescription^> >> "%ADDIN_FILE%"
echo   ^</AddIn^> >> "%ADDIN_FILE%"
echo ^</RevitAddIns^> >> "%ADDIN_FILE%"

if exist "%ADDIN_FILE%" (
    echo [SUCCESS] pyRevit attached to Revit %REVIT_YEAR%
) else (
    echo [ERROR] Failed to create pyRevit addin for Revit %REVIT_YEAR%
)

exit /b 0

:error
echo [FINAL] Process completed with errors. Exit code: 1
goto :pause

:end
echo [FINAL] pyRevit attachment completed successfully!
echo [NOTE] pyRevit is now available for your user account.
echo [NOTE] You may need to restart Revit to see the pyRevit ribbon.

:pause
pause

