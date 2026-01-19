@echo off
echo ============================================================
echo PA6.4 Backend Development Server
echo ============================================================
echo.
echo Starting server on http://localhost:10181
echo API Docs: http://localhost:10181/docs
echo.
echo Press CTRL+C to stop
echo.

cd /d "%~dp0"
python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
