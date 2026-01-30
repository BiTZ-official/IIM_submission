@echo off
REM run_me.bat — creates venv, installs requirements, and launches services
setlocal
echo starting program . . .
REM --- Determine Python executable ---
where python >nul 2>&1
if %errorlevel%==0 (
    set PY=python
) else (
    where python3 >nul 2>&1
    if %errorlevel%==0 (
        set PY=python3
    ) else (
        echo Python not found. Install Python 3.8+ and re-run this script.
        pause
        exit /b 1
    )
)

REM --- Check Python version >= 3.8 ---
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)"
if %errorlevel% neq 0 (
    echo Python 3.8+ is required.
    %PY% -V
    pause
    exit /b 1
)

REM --- Create virtual environment if missing ---
if not exist .venv (
    %PY% -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM --- Activate venv and install requirements ---
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r code-files\requirements.txt

REM --- Run other services in new windows (start APIs first) ---
start "Process API" cmd /k "call .venv\Scripts\activate && python code-files\process.py && pause"
start "Simulated Data" cmd /k "call .venv\Scripts\activate && python code-files\simulated_data.py && pause"
echo Booting program . . .

REM --- Wait until both API ports are accepting connections ---
echo Waiting for services to start on ports 8080 and 8090...
powershell -Command "$t0=Get-Date; while(-not ((Test-NetConnection -ComputerName 127.0.0.1 -Port 8080).TcpTestSucceeded -and (Test-NetConnection -ComputerName 127.0.0.1 -Port 8090).TcpTestSucceeded)) { if((Get-Date) - $t0 -gt (New-TimeSpan -Seconds 30)) { exit 2 } ; Start-Sleep -Seconds 10 }"
echo Testing complete.
if %errorlevel% neq 0 (
    echo Timeout waiting for services. Continuing anyway.
)

REM --- Run main processor in current window ---
echo booting Ui
python code-files\main.processor.py

REM --- Keep this window open after finishing ---
echo Boot complete . . .
pause

endlocal
exit /b 0
