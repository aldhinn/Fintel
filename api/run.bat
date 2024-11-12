@rem Run this script if you're using windows.

setlocal
@echo off

set "python_exe=python.exe"
set "pytest_exe=pytest.exe"
set "flake8_exe=flake8"

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
where %flake8_exe% > nul 2>&1
if %errorlevel% neq 0 (
    echo Please install flake8 in your system.
    exit /b 1
)

@rem The directory where this script exists.
set "script_dir=%~dp0"

if "%~1"=="test" (
    @rem Check syntax of scripts.
    %flake8_exe% --exclude $script_dir/venv --ignore=E252,E501,W292,E302,^
        E231,E261,E302,E305,E502,E226,E402,E225,E227,E125,E128,^
        E225,E122,E131,E127,E124 %script_dir%
    @rem Run the tests
    %pytest_exe% -s %script_dir%
) else (
    @rem Default behavior: Run the application
    %python_exe% %script_dir%\app.py
)

endlocal
@rem End of line.
@rem DO NOT WRITE BEYOND HERE.