# 環境區分與部署策略

## 專案資訊
- **專案名稱**: Paris Agreement Article 6.4 管理系統
- **專案代碼**: PA6.4
- **文件版本**: 1.1.0
- **最後更新**: 2026-01-18

---

## 環境分類

### 三層環境架構

| 環境 | 用途 | 原始碼狀態 | 部署方式 | Port 配置 |
|------|------|-----------|----------|----------|
| **開發環境 (Development)** | 本機開發、即時修改 | 完整原始碼 | 直接執行 | Frontend: 10180<br>Backend: 10181 |
| **測試環境 (Testing/Staging)** | 功能測試、整合測試 | 完整原始碼或編譯碼 | Docker 部署 | 依需求設定 |
| **營運環境 (Production)** | 正式上線服務 | **原始碼遮蔽** | Docker 部署 | 80/443 (Nginx) |

---

## 開發環境 (Development)

### 特性

- **完整原始碼**: 保留 `.py`、`.ts`、`.tsx` 等源碼檔案
- **即時熱重載**: 修改後自動重啟
- **除錯模式**: 開啟 Debug、詳細日誌
- **本機資料庫**: 使用本機 PostgreSQL 和 Redis

### 目錄結構

```
W:\P-PA6.4\
├── Develop/              # 開發環境目錄
│   ├── frontend/
│   │   ├── src/              # React 原始碼
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── backend/
│       ├── app/              # Python 原始碼
│       │   ├── main.py
│       │   ├── models/
│       │   ├── routes/
│       │   └── services/
│       ├── sharedata/        # 共用資料目錄
│       │   ├── images/
│       │   ├── uploads/
│       │   └── locales/
│       ├── tests/
│       ├── requirements.txt
│       └── .env
│
├── 系統設計/              # 設計文檔
└── testarea/             # 測試腳本
```

### 環境變數 (.env)

**位置**: `W:\P-PA6.4\Develop\backend\.env`

```bash
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
PORT=10181
DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev
REDIS_URL=redis://:!DC1qaz2wsx@localhost:6379/0
```

---

## 測試環境 (Testing/Staging)

### 特性

- **完整原始碼**: 保留源碼以便測試時修改
- **Docker 容器化**: 部署到 NAS 或測試伺服器
- **對外存取**: 提供測試人員和客戶試用
- **掛載原始碼**: 直接掛載 `W:\P-PA6.4\Develop` 目錄

### 部署方式 A：直接掛載開發環境原始碼（推薦）

**同步原始碼到 NAS**:
```bash
# 方法 1: 使用 rsync
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  W:/P-PA6.4/Develop/ admin@nas-ip:/volume1/docker/pa64/

# 方法 2: 使用 Git（推薦）
cd /volume1/docker/pa64
git clone https://your-repo.git .
git pull  # 更新
```

**docker-compose.staging.yml** (在 NAS 上執行):
```yaml
version: '3.8'

services:
  frontend:
    image: node:20-alpine
    working_dir: /app
    ports:
      - "10180:10180"
    volumes:
      # 掛載開發環境原始碼
      - /volume1/docker/pa64/frontend:/app
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0 --port 10180"
    environment:
      - NODE_ENV=staging

  backend:
    image: python:3.11-slim
    working_dir: /app
    ports:
      - "10181:10181"
    volumes:
      # 掛載開發環境原始碼
      - /volume1/docker/pa64/backend:/app
    command: sh -c "pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload"
    environment:
      - ENVIRONMENT=staging
      - DEBUG=True
      - DATABASE_URL=postgresql://test_user:test_pass@db:5432/pa64_staging
      - REDIS_URL=redis://:test_pass@redis:6379/1

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=pa64_staging
      - POSTGRES_USER=test_user
      - POSTGRES_PASSWORD=test_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass test_pass

volumes:
  postgres_data:
```

### 環境變數 (.env.staging)

**位置**: `W:\P-PA6.4\Develop\backend\.env.staging`

```bash
ENVIRONMENT=staging
DEBUG=True  # 測試環境保留 Debug 方便追蹤
LOG_LEVEL=INFO
DATABASE_URL=postgresql://test_user:test_pass@db:5432/pa64_staging
REDIS_URL=redis://:test_pass@redis:6379/1
```

---

## 營運環境 (Production)

### 特性

- **原始碼遮蔽**: 不包含 `.py`、`.ts` 源碼
- **編譯/打包**: 使用編譯後的檔案
- **高安全性**: 移除所有開發工具
- **效能最佳化**: 啟用快取、壓縮

### 原始碼保護策略

#### 1. 前端 (React)

**建置流程**：
```bash
# 建置生產版本
cd frontend
npm run build

# 產生 dist/ 目錄，包含：
# - 壓縮的 JavaScript
# - 最小化的 CSS
# - 最佳化的資源檔案
```

**部署內容**：
```
frontend/dist/              # 只部署這個目錄
├── index.html
├── assets/
│   ├── index-abc123.js    # 編譯、壓縮、混淆後的 JS
│   ├── index-def456.css
│   └── logo-xyz789.svg
└── locales/
```

**Dockerfile.production** (Frontend):
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage - 只保留建置後的檔案
FROM nginx:alpine

# 複製建置產物（無原始碼）
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 後端 (Python FastAPI)

**方案 A：Python 字節碼 (.pyc)**

優點：簡單快速
缺點：可被反編譯

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼並編譯為 .pyc
COPY app ./app
RUN python -m compileall -b app && \
    find app -name "*.py" -type f -delete

# 啟動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**方案 B：Cython 編譯為 .so (推薦)**

優點：高度保護、難以反編譯
缺點：需要編譯步驟

**Dockerfile.production** (Backend):

**位置**: `W:\P-PA6.4\Develop\backend\Dockerfile.production`

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# 安裝編譯工具
RUN apt-get update && apt-get install -y gcc build-essential

# 複製程式碼
COPY app ./app
COPY requirements.txt setup.py ./

# 使用 Cython 編譯為 .so
RUN pip install cython
RUN python setup.py build_ext --inplace

# 刪除原始碼，只保留 .so
RUN find app -name "*.py" ! -name "__init__.py" -type f -delete

# Production stage
FROM python:3.11-slim

WORKDIR /app

# 複製依賴和編譯後的 .so 檔案
COPY --from=builder /app/app ./app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製共用資料目錄
COPY sharedata ./sharedata

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**setup.py** (Cython 編譯設定):

**位置**: `W:\P-PA6.4\Develop\backend\setup.py`
```python
from setuptools import setup, Extension
from Cython.Build import cythonize
import glob

# 找出所有 .py 檔案（除了 __init__.py）
py_files = []
for file in glob.glob("app/**/*.py", recursive=True):
    if not file.endswith("__init__.py"):
        py_files.append(file)

extensions = [
    Extension(
        file.replace("/", ".").replace(".py", ""),
        [file]
    ) for file in py_files
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"}
    )
)
```

**方案 C：PyInstaller / Nuitka (最高保護)**

優點：編譯為單一執行檔
缺點：檔案較大、部署複雜

```bash
# 使用 Nuitka 編譯
python -m nuitka --standalone --onefile app/main.py
```

---

## 環境變數管理

### 開發環境

**檔案**: `.env` (本地檔案，**不可提交到 Git**)

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev
SECRET_KEY=dev-secret-key
```

### 測試環境

**檔案**: `.env.staging` (或透過 CI/CD 注入)

```bash
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://staging_user:***@db-staging:5432/pa64_staging
SECRET_KEY=***
```

### 營運環境

**方式**: **環境變數注入** (透過 Docker Secrets 或 K8s ConfigMap)

```bash
# 透過 docker-compose 或 Kubernetes 注入
docker run -e ENVIRONMENT=production \
           -e DATABASE_URL=postgresql://prod_user:***@db-prod:5432/pa64_prod \
           -e SECRET_KEY=*** \
           pa64-backend:latest
```

**絕對不要**：
- ❌ 將生產環境的 `.env` 檔案打包進 Docker Image
- ❌ 在程式碼中硬編碼密碼或金鑰
- ❌ 提交含有敏感資訊的設定檔到 Git

---

## 部署檢查清單

### 營運環境部署前檢查

**安全性**：
- [ ] 已移除所有 `.py` 原始碼（或編譯為 .so）
- [ ] 已移除所有 `.ts`、`.tsx` 原始碼
- [ ] 沒有 `.env` 檔案在 Docker Image 中
- [ ] 敏感資訊透過環境變數注入
- [ ] DEBUG 模式已關閉
- [ ] 日誌級別設為 WARNING 或 ERROR

**效能**：
- [ ] Frontend 已建置壓縮版本
- [ ] Backend 已編譯或最佳化
- [ ] 啟用 Gzip 壓縮
- [ ] 啟用靜態檔案快取

**監控**：
- [ ] 設定日誌收集
- [ ] 設定錯誤追蹤 (Sentry)
- [ ] 設定效能監控 (APM)

---

## 環境識別方式

### 透過環境變數

**app/config.py**:
```python
import os
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings:
    ENVIRONMENT: Environment = Environment(
        os.getenv("ENVIRONMENT", "development")
    )

    DEBUG: bool = ENVIRONMENT == Environment.DEVELOPMENT

    # 根據環境調整設定
    if ENVIRONMENT == Environment.PRODUCTION:
        LOG_LEVEL = "WARNING"
        ALLOWED_HOSTS = ["api.pa64.com"]
    elif ENVIRONMENT == Environment.STAGING:
        LOG_LEVEL = "INFO"
        ALLOWED_HOSTS = ["staging-api.pa64.com"]
    else:
        LOG_LEVEL = "DEBUG"
        ALLOWED_HOSTS = ["*"]

settings = Settings()
```

### 使用範例

```python
from app.config import settings

if settings.ENVIRONMENT == "production":
    # 營運環境特殊處理
    print("Running in production mode")
else:
    # 開發/測試環境
    print("Running in development/staging mode")
```

---

## 部署流程

### 開發環境 → 測試環境

#### 方法 1：同步到 NAS（推薦）

```bash
# 在本機 W:\P-PA6.4\Develop 開發完成後

# 1. 同步到 NAS
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  W:/P-PA6.4/Develop/ admin@nas-ip:/volume1/docker/pa64/

# 2. 在 NAS 上重啟 Docker
ssh admin@nas-ip
cd /volume1/docker/pa64
docker-compose -f docker-compose.staging.yml restart
```

#### 方法 2：使用 Git

```bash
# 1. 提交程式碼
cd W:\P-PA6.4\Develop
git add .
git commit -m "Feature: Add user authentication"
git push origin develop

# 2. 在 NAS 上拉取最新程式碼
ssh admin@nas-ip
cd /volume1/docker/pa64
git pull origin develop
docker-compose -f docker-compose.staging.yml restart
```

### 測試環境 → 營運環境

```bash
# 1. 合併到 main 分支
cd W:\P-PA6.4\Develop
git checkout main
git merge develop
git push origin main

# 2. 建立版本標籤
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 3. 建置營運版本（原始碼遮蔽）
cd W:\P-PA6.4\Develop

# Frontend 建置
cd frontend
docker build -f Dockerfile.production -t pa64-frontend:1.0.0 .

# Backend 建置（Cython 編譯）
cd ../backend
docker build -f Dockerfile.production -t pa64-backend:1.0.0 .

# 4. 部署到營運環境
docker-compose -f docker-compose.production.yml up -d
```

---

## 原始碼保護程度比較

| 方案 | 保護程度 | 效能影響 | 實作難度 | 建議使用環境 |
|------|----------|----------|----------|-------------|
| **原始碼** | ⭐ | 無 | 簡單 | 開發環境 |
| **Python .pyc** | ⭐⭐ | 微小 | 簡單 | 測試環境 |
| **Cython .so** | ⭐⭐⭐⭐ | 微小 | 中等 | **營運環境（推薦）** |
| **Nuitka** | ⭐⭐⭐⭐⭐ | 微小 | 複雜 | 高安全需求環境 |
| **React Build** | ⭐⭐⭐ | 提升 | 簡單 | **營運環境（標準）** |

---

## 更新記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-01-18 | 1.0.0 | 建立環境區分與部署策略文檔，定義三層環境架構與原始碼保護方案 |
| 2026-01-18 | 1.1.0 | 更新目錄結構，所有開發環境統一放在 W:\P-PA6.4\Develop；測試環境直接掛載開發環境原始碼 |
