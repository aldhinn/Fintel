@rem Run this script if you're using windows.

setlocal
@echo off

set "python_exe=python.exe"
set "pytest_exe=pytest.exe"
set "flake8_exe=flake8"
set "gunicorn_exe=gunicorn"

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
where %gunicorn_exe% > nul 2>&1
if %errorlevel% neq 0 (
    echo Please install gunicorn in your system.
    exit /b 1
)

@rem The directory where this script exists.
set "script_dir=%~dp0"
@rem Change working directory to script_dir.
cd %script_dir%

if "%~1"=="test" (
    @rem Check syntax of scripts.
    %flake8_exe% --exclude ./venv --ignore=E252,E501,W292,E302,^
E231,E261,E302,E305,E502,E226,E402,E225,E227,E125,E128,^
E225,E122,E131,E127,E124
    @rem Run the tests
    %pytest_exe% -s
) else (
    @rem Get the number of CPU cores
    for /f "tokens=2 delims==" %%A in ('wmic cpu get NumberOfLogicalProcessors /value ^| find "="') do set NUM_CPUS=%%A
    @rem Calculate the number of workers (NUM_CPUS * 2 + 1)
    set /a WORKERS=%NUM_CPUS% * 2 + 1

    @rem Default behavior: Run the application
    %gunicorn_exe% -w %NUM_CPUS% -b 0.0.0.0:61000 'app:setup_app()'
)

endlocal
@rem End of line.
@rem DO NOT WRITE BEYOND HERE.