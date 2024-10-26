@rem Run this script if you're using windows.

setlocal
@echo off

set "python_exe=python.exe"
set "pytest_exe=pytest.exe"

where %python_exe% > nul 2>&1
if %errorlevel% neq 0 (
    echo Please install python in your system.
    exit /b 1
)
where %pytest_exe% > nul 2>&1
if %errorlevel% neq 0 (
    echo Please install pytest in your system.
    exit /b 1
)

@rem The directory where this script exists.
set "script_dir=%~dp0"

if "%~1"=="test" (
    @rem Run the tests
    %pytest_exe% -s %script_dir%
) else (
    @rem Default behavior: Run the application
    %python_exe% %script_dir%\app.py
)

endlocal
@rem End of line.
@rem DO NOT WRITE BEYOND HERE.