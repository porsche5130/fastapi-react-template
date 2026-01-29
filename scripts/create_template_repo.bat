@echo off
REM =========================================
REM 從 PA6.4 建立範本倉庫的自動化腳本
REM =========================================

echo.
echo ========================================
echo 建立 FastAPI-React-Template 範本倉庫
echo ========================================
echo.

REM 檢查目標目錄是否存在
if exist "W:\FastAPI-React-Template" (
    echo [警告] 目標目錄已存在: W:\FastAPI-React-Template
    set /p confirm="是否要刪除並重新建立? (yes/no): "
    if /i "%confirm%"=="yes" (
        echo 刪除現有目錄...
        rmdir /s /q "W:\FastAPI-React-Template"
    ) else (
        echo 已取消
        exit /b 1
    )
)

echo.
echo [步驟 1/5] 複製專案檔案...
echo.

REM 建立目標目錄
mkdir "W:\FastAPI-React-Template"

REM 複製主要目錄 (排除不需要的)
xcopy "W:\P-PA6.4" "W:\FastAPI-React-Template\" /E /I /H /Y /EXCLUDE:W:\P-PA6.4\scripts\xcopy_exclude_list.txt

echo.
echo [步驟 2/5] 清理不需要的檔案和目錄...
echo.

REM 刪除 .git 目錄
if exist "W:\FastAPI-React-Template\.git" rmdir /s /q "W:\FastAPI-React-Template\.git"

REM 刪除 node_modules
if exist "W:\FastAPI-React-Template\Develop\frontend\node_modules" rmdir /s /q "W:\FastAPI-React-Template\Develop\frontend\node_modules"

REM 刪除 Python cache
for /d /r "W:\FastAPI-React-Template" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM 刪除 .env 檔案 (保留 .env.example)
if exist "W:\FastAPI-React-Template\Develop\backend\.env" del "W:\FastAPI-React-Template\Develop\backend\.env"
if exist "W:\FastAPI-React-Template\Develop\frontend\.env" del "W:\FastAPI-React-Template\Develop\frontend\.env"

REM 刪除 venv
if exist "W:\FastAPI-React-Template\Develop\backend\venv" rmdir /s /q "W:\FastAPI-React-Template\Develop\backend\venv"

echo.
echo [步驟 3/5] 執行轉換腳本 (測試模式)...
echo.

cd /d "W:\FastAPI-React-Template"
python scripts\create_template.py --dry-run

echo.
set /p confirm="轉換預覽完成。確定要執行正式轉換? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo 已取消。您可以手動檢查 W:\FastAPI-React-Template 目錄
    exit /b 0
)

echo.
echo [步驟 4/5] 執行正式轉換...
echo.

python scripts\create_template.py

echo.
echo [步驟 5/5] 初始化 Git 倉庫...
echo.

git init
git add .
git commit -m "Initial commit: Multi-tenant template based on PA6.4"

echo.
echo ========================================
echo 完成!
echo ========================================
echo.
echo 範本倉庫已建立在: W:\FastAPI-React-Template
echo.
echo 下一步:
echo 1. 手動檢查轉換結果
echo 2. 在 GitHub 建立新倉庫 (建議名稱: fastapi-react-template)
echo 3. 關聯並推送:
echo.
echo    cd W:\FastAPI-React-Template
echo    git remote add origin https://github.com/你的帳號/fastapi-react-template.git
echo    git push -u origin main
echo.
pause
