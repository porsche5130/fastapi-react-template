# PA6.4 Backend API

Paris Agreement Article 6.4 管理系統後端 API

## 專案資訊

- **專案名稱**: PA6.4 Management System
- **技術棧**: Python 3.11+ | FastAPI | PostgreSQL | Redis
- **API 文件**: http://localhost:10181/docs
- **版本**: 1.0.0

---

## 快速開始

### 1. 環境需求

- Python 3.11+
- PostgreSQL 16+ (本機執行)
- Redis 7+ (本機執行)

### 2. 安裝依賴

```bash
cd W:\P-PA6.4\Develop\backend
pip install fastapi uvicorn sqlalchemy python-jose python-dotenv pydantic-settings redis passlib python-multipart bcrypt
```

### 3. 初始化資料庫

```bash
cd W:\P-PA6.4
python testarea\init_database.py
```

### 4. 啟動開發伺服器

#### 方法 1: 使用啟動腳本

```bash
cd W:\P-PA6.4\Develop\backend
start_dev.bat
```

#### 方法 2: 直接執行

```bash
cd W:\P-PA6.4\Develop\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
```

### 5. 存取 API

- **根路徑**: http://localhost:10181
- **API 文件 (Swagger)**: http://localhost:10181/docs
- **API 文件 (ReDoc)**: http://localhost:10181/redoc
- **健康檢查**: http://localhost:10181/api/health

---

## API 端點

### 認證相關 (`/api/auth`)

#### POST `/api/auth/login` - 使用者登入

**請求**:
```json
{
  "account": "admin@pa64.system",
  "password": "admin123"
}
```

**說明**: `account` 欄位必須為有效的電子郵件格式

**回應**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/me` - 取得當前使用者資訊

**Headers**:
```
Authorization: Bearer <access_token>
```

**回應**:
```json
{
  "id": 1,
  "account": "admin",
  "username": "系統管理員",
  "organization_id": 1,
  "department": "資訊部",
  "job_title": "系統管理員",
  "phone": "0910326333",
  "user_role": [1]
}
```

#### POST `/api/auth/logout` - 使用者登出

**Headers**:
```
Authorization: Bearer <access_token>
```

**回應**:
```json
{
  "message": "登出成功"
}
```

### 系統管理 (`/api/system`)

#### GET `/api/system/profile` - 取得系統設定

**回應**:
```json
{
  "id": 1,
  "is_service": true,
  "sys_url": "http://localhost:10180",
  "sys_ctitle": "Paris Agreement Article 6.4 管理系統",
  "sys_etitle": "Paris Agreement Article 6.4 Management System",
  "sys_ccopyright": "Copyright © 2026 匠耘有限公司",
  "sys_ecopyright": "Copyright © 2026 JiangYun Co., Ltd.",
  "sys_organization": 1,
  "sys_mana_email": "porsche@lab.taipei"
}
```

#### GET `/api/system/check` - 系統健康檢查

**回應**:
```json
{
  "status": "ok",
  "message": "系統運作正常",
  "is_service": true
}
```

---

## 靜態資源

### 圖片資源
- **URL**: `/images/`
- **目錄**: `sharedata/images/`
- **範例**: http://localhost:10181/images/logo.svg

### 上傳檔案
- **URL**: `/uploads/`
- **目錄**: `sharedata/uploads/`
- **範例**: http://localhost:10181/uploads/document.pdf

### 語系檔案
- **URL**: `/locales/{lang}/`
- **目錄**: `sharedata/locales/`
- **範例**: http://localhost:10181/locales/zh-TW/common.json

---

## 目錄結構

```
backend/
├── app/
│   ├── core/                 # 核心功能
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 資料庫連線
│   │   ├── redis.py          # Redis 連線
│   │   ├── security.py       # 安全性工具 (JWT, bcrypt)
│   │   └── deps.py           # 依賴注入
│   │
│   ├── models/               # SQLAlchemy Models
│   │   ├── organization.py
│   │   ├── user_role.py
│   │   ├── user_detail.py
│   │   ├── sysfuction.py
│   │   ├── sys_profile.py
│   │   └── userlog.py
│   │
│   ├── schemas/              # Pydantic Schemas
│   │   ├── auth.py
│   │   └── user.py
│   │
│   ├── routes/               # API 路由
│   │   ├── auth.py           # 認證相關
│   │   └── system.py         # 系統管理
│   │
│   └── main.py               # FastAPI 主應用程式
│
├── sharedata/                # 共用資料目錄
│   ├── images/
│   ├── uploads/
│   └── locales/
│       ├── en/
│       ├── zh-TW/
│       └── zh-CN/
│
├── .env                      # 環境變數 (開發)
├── requirements.txt          # Python 依賴
├── start_dev.bat             # 啟動腳本
└── README.md                 # 本文件
```

---

## 環境變數

**檔案**: `.env`

```bash
# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
PORT=10181

# Database
DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev

# Redis
REDIS_URL=redis://:!DC1qaz2wsx@localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production-2026-pa64-system
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:10180"]
```

---

## 測試

### API 測試腳本

```bash
cd W:\P-PA6.4
python testarea\test_backend_api.py
```

### 使用 Swagger UI

1. 啟動後端伺服器
2. 開啟瀏覽器: http://localhost:10181/docs
3. 點擊「Try it out」測試 API

### 使用 curl

```bash
# 登入
curl -X POST http://localhost:10181/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account":"admin","password":"admin123"}'

# 取得使用者資訊
curl http://localhost:10181/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 預設帳號

| 帳號 | 密碼 | 角色 |
|------|------|------|
| admin | admin123 | 系統管理員 |

⚠️ **警告**: 正式部署前請務必修改預設密碼！

---

## 開發說明

### 新增 API 路由

1. 在 `app/routes/` 建立新的路由檔案
2. 在 `app/main.py` 註冊路由:

```python
from app.routes import new_route

app.include_router(new_route.router, prefix="/api/new", tags=["新功能"])
```

### 新增資料庫 Model

1. 在 `app/models/` 建立新的 Model
2. 在 `app/models/__init__.py` 匯出
3. 執行資料庫遷移 (如使用 Alembic)

### 新增 Pydantic Schema

1. 在 `app/schemas/` 建立新的 Schema
2. 用於請求驗證和回應序列化

---

## 相關文件

- [資料庫設計](../../系統設計/應用系統設計/基礎資訊管理後台設計.md)
- [資料庫初始化說明](README_DATABASE.md)
- [開發環境設定](../../系統設計/架構設計/開發環境/開發測試環境.md)
- [環境部署策略](../../系統設計/架構設計/部署環境/環境區分與部署策略.md)

---

## 故障排除

### 1. 資料庫連線失敗

```bash
# 檢查 PostgreSQL 是否執行
psql -h localhost -U dev -d pa64_dev -c "SELECT version();"

# 檢查連線字串
# DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev
```

### 2. Redis 連線失敗

```bash
# 檢查 Redis 是否執行
redis-cli -a "!DC1qaz2wsx" ping

# 檢查連線字串
# REDIS_URL=redis://:!DC1qaz2wsx@localhost:6379/0
```

### 3. Port 被佔用

```bash
# 檢查 Port 10181 是否被佔用
netstat -ano | findstr :10181

# 終止佔用的程式
taskkill /PID <PID> /F
```

### 4. 模組匯入錯誤

```bash
# 確保在正確的目錄執行
cd W:\P-PA6.4\Develop\backend

# 檢查 Python 版本
python --version  # 應為 3.11+

# 重新安裝依賴
pip install --upgrade fastapi uvicorn sqlalchemy
```

---

## 更新記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-01-18 | 1.0.0 | 建立初始後端 API，實作認證與系統管理功能 |
