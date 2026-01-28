@echo off
echo ========================================
echo Restarting Backend Service
echo ========================================
echo.

echo Step 1: Finding backend process...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :10181 ^| findstr LISTENING') do (
    set PID=%%a
)

if defined PID (
    echo Found backend process: PID %PID%
    echo Stopping backend...
    taskkill /F /PID %PID%
    timeout /t 2 /nobreak >nul
    echo Backend stopped.
) else (
    echo No backend process found on port 10181.
)

echo.
echo Step 2: Starting backend...
echo Starting: uvicorn app.main:app --reload --port 10181
echo.
echo Press Ctrl+C to stop the backend service.
echo ========================================
echo.

cd /d "%~dp0"
uvicorn app.main:app --reload --port 10181
