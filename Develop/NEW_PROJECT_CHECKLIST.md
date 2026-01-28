# 新專案建立檢查清單

基於 PA6.4 範本建立新專案的完整步驟

## 階段 1: 專案初始化

### 1.1 複製專案範本
- [ ] 複製整個 `Develop/` 目錄到新專案位置
- [ ] 重新命名專案目錄為新專案名稱
- [ ] 刪除 `.git` 目錄 (如果存在)
- [ ] 初始化新的 Git Repository: `git init`

### 1.2 更新專案資訊
- [ ] 修改 `backend/app/main.py` 中的應用程式名稱和描述
- [ ] 修改 `frontend/package.json` 中的專案名稱和版本
- [ ] 修改 `frontend/public/index.html` 中的標題
- [ ] 建立新的 `README.md` 描述專案

### 1.3 清理不需要的檔案
- [ ] 刪除測試腳本 (*.py 在根目錄的測試檔案)
- [ ] 刪除 `REDIS_ISSUE_ROOT_CAUSE.md` 等除錯文件
- [ ] 保留 `PROJECT_TEMPLATE_GUIDE.md` 作為參考
- [ ] 保留 `NEW_PROJECT_CHECKLIST.md` (此檔案)

## 階段 2: 環境配置

### 2.1 後端環境
- [ ] 複製 `backend/.env.example` 為 `backend/.env`
- [ ] 修改 `.env` 中的資料庫連線資訊:
  - [ ] DATABASE_URL (使用者名稱、密碼、資料庫名稱)
- [ ] 修改 `.env` 中的 Redis 配置:
  - [ ] REDIS_HOST (如果需要)
  - [ ] REDIS_DB (為新專案分配專用的 DB 編號)
  - [ ] REDIS_PASSWORD
- [ ] 生成新的 SECRET_KEY:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```
- [ ] 修改其他配置 (PORT, CORS, 檔案上傳限制等)

### 2.2 前端環境
- [ ] 建立 `frontend/.env`
- [ ] 設定 API 位址:
  ```env
  REACT_APP_API_BASE_URL=http://localhost:10181
  ```

### 2.3 Git 配置
- [ ] 確認 `.gitignore` 包含:
  ```
  .env
  .env.local
  __pycache__/
  *.pyc
  node_modules/
  build/
  dist/
  .vscode/
  .idea/
  ```

## 階段 3: 資料庫設定

### 3.1 建立資料庫
```sql
-- 在 PostgreSQL 中執行
CREATE DATABASE your_project_name
  WITH OWNER = admin
  ENCODING = 'UTF8'
  LC_COLLATE = 'Chinese (Traditional)_Taiwan.950'
  LC_CTYPE = 'Chinese (Traditional)_Taiwan.950'
  TEMPLATE = template0;
```

### 3.2 執行資料庫遷移
- [ ] 清理舊的遷移記錄: 刪除 `backend/alembic/versions/*.py` (保留資料夾)
- [ ] 初始化 Alembic:
  ```bash
  cd backend
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

### 3.3 建立初始資料
- [ ] 建立系統管理員帳號
- [ ] 建立預設角色
- [ ] 建立基本系統功能
- [ ] 設定預設權限

可以參考 PA6.4 的初始化腳本或手動執行 SQL。

## 階段 4: Redis 配置

### 4.1 分配 Redis DB
- [ ] 確認 Redis DB 編號不與其他專案衝突
  - PA6.4 使用 DB 1
  - 建議: DB 2, 3, 4... 依序分配給新專案
- [ ] 更新 `.env` 中的 `REDIS_DB`

### 4.2 測試 Redis 連線
```python
# test_redis.py
import redis
r = redis.Redis(
    host='10.1.0.20',
    port=6379,
    db=2,  # 你的 DB 編號
    password='your_password',
    decode_responses=True
)
print("Redis Ping:", r.ping())
```

## 階段 5: 依賴安裝

### 5.1 後端依賴
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 5.2 前端依賴
```bash
cd frontend
npm install
```

## 階段 6: 功能調整

### 6.1 移除不需要的功能
根據新專案需求,可能需要移除某些模組:
- [ ] 刪除不需要的 models
- [ ] 刪除不需要的 routes
- [ ] 刪除不需要的 services
- [ ] 刪除不需要的前端頁面
- [ ] 更新 main.py 的 router 註冊
- [ ] 更新前端的路由配置

### 6.2 自訂專案特定功能
- [ ] 設計新的資料表結構
- [ ] 建立新的 Models
- [ ] 建立新的 API Routes
- [ ] 建立新的前端頁面
- [ ] 更新導航選單
- [ ] 更新多語系翻譯

## 階段 7: 測試驗證

### 7.1 後端測試
- [ ] 啟動後端: `python -m uvicorn app.main:app --reload`
- [ ] 檢查啟動日誌無錯誤
- [ ] 訪問 Swagger UI: http://localhost:10181/docs
- [ ] 測試健康檢查端點
- [ ] 測試資料庫連線
- [ ] 測試 Redis 連線

### 7.2 前端測試
- [ ] 啟動前端: `npm start`
- [ ] 檢查編譯無錯誤
- [ ] 訪問首頁: http://localhost:10180
- [ ] 測試登入功能
- [ ] 測試基本 CRUD 功能
- [ ] 檢查多語系切換

### 7.3 整合測試
- [ ] 測試完整的使用者流程
- [ ] 測試權限控制
- [ ] 測試 Session 管理
- [ ] 測試 Token 機制
- [ ] 檢查 Redis Commander 中的資料
- [ ] 檢查瀏覽器 Console 無錯誤

## 階段 8: 文件更新

### 8.1 專案文件
- [ ] 撰寫 README.md
  - 專案簡介
  - 功能列表
  - 技術棧
  - 安裝步驟
  - 啟動方式
- [ ] 更新 API 文件 (如果有額外的文件)
- [ ] 撰寫開發文件
- [ ] 撰寫部署文件

### 8.2 註解和 Docstring
- [ ] 檢查程式碼註解完整性
- [ ] 補充函數和類別的 Docstring
- [ ] 更新複雜邏輯的說明

## 階段 9: 版本控制

### 9.1 Git 提交
- [ ] 檢查 `.gitignore` 正確排除 `.env`
- [ ] 第一次提交:
  ```bash
  git add .
  git commit -m "Initial commit: Project setup based on PA6.4 template"
  ```
- [ ] 建立開發分支:
  ```bash
  git checkout -b develop
  ```

### 9.2 遠端倉庫 (如果需要)
- [ ] 建立 GitHub/GitLab Repository
- [ ] 加入 remote:
  ```bash
  git remote add origin <repository-url>
  git push -u origin main
  git push -u origin develop
  ```

## 階段 10: 開發規範

### 10.1 團隊規範
- [ ] 定義 Git Branch 策略 (Git Flow / GitHub Flow)
- [ ] 定義 Commit Message 格式
- [ ] 定義 Code Review 流程
- [ ] 定義測試要求

### 10.2 開發工具配置
- [ ] VSCode 工作區設定
- [ ] ESLint / Prettier 設定 (前端)
- [ ] Black / Flake8 設定 (後端)
- [ ] Pre-commit hooks

## 完成確認

### 最終檢查清單
- [ ] 所有測試通過
- [ ] 文件完整
- [ ] .env 檔案已排除在 Git 之外
- [ ] 敏感資訊已移除
- [ ] 程式碼已整理
- [ ] 團隊成員都能成功啟動專案

### 後續工作
- [ ] 設定 CI/CD Pipeline
- [ ] 設定測試環境
- [ ] 設定監控系統
- [ ] 規劃正式上線流程

---

## 常見問題

### Q1: 資料庫遷移失敗?
**A**: 檢查 `alembic/env.py` 中的資料庫連線設定是否正確。

### Q2: Redis 連線失敗?
**A**: 確認防火牆設定,測試網路連通性: `ping 10.1.0.20`

### Q3: 前端無法呼叫 API?
**A**: 檢查 CORS 設定,確認前端 URL 在 `ALLOWED_ORIGINS` 中。

### Q4: 多個進程衝突?
**A**: 使用 `netstat -ano | findstr ":10181"` 檢查並停止舊進程。

---

**建立日期**: 2026-01-28
**基於**: PA6.4 專案範本 v1.0.0
**維護者**: [你的名字/團隊]
