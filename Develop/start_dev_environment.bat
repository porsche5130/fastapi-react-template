@echo off
REM ========================================
REM PA6.4 開發環境快速啟動腳本
REM ========================================

echo ========================================
echo PA6.4 開發環境啟動中...
echo ========================================
echo.

REM 檢查並停止舊的 Python 進程
echo [1/5] 檢查舊的執行序...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":10181" ^| findstr "LISTENING"') do (
    echo 發現舊的後端進程,正在停止...
    taskkill /PID %%a /F >nul 2>&1
)

REM 等待 Port 釋放
timeout /t 2 >nul

REM 檢查環境
echo [2/5] 檢查環境配置...
if not exist "backend\.env" (
    echo [ERROR] 找不到 backend\.env 檔案!
    echo 請先複製 .env.example 並設定環境變數
    pause
    exit /b 1
)

REM 檢查 Python 虛擬環境
echo [3/5] 檢查 Python 環境...
if exist "backend\venv" (
    echo 使用虛擬環境: backend\venv
    call backend\venv\Scripts\activate.bat
) else (
    echo 未找到虛擬環境,使用系統 Python
)

REM 啟動後端
echo [4/5] 啟動後端服務...
cd backend
start "PA6.4 Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload"
cd ..

REM 等待後端啟動
echo 等待後端啟動...
timeout /t 5 >nul

REM 啟動前端
echo [5/5] 啟動前端服務...
cd frontend
start "PA6.4 Frontend" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo 啟動完成!
echo ========================================
echo.
echo 後端: http://localhost:10181
echo API 文件: http://localhost:10181/docs
echo 前端: http://localhost:10180
echo.
echo 按任意鍵開啟瀏覽器...
pause >nul

REM 開啟瀏覽器
start http://localhost:10180

echo.
echo 如需停止服務,請關閉對應的命令視窗
echo.
