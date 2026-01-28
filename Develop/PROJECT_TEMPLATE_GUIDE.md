# Python 專案標準範本指南

基於 PA6.4 專案的標準化開發架構

## 專案架構概覽

```
Project/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── core/              # 核心模組 (config, database, redis, security)
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routes/            # API 路由
│   │   ├── services/          # 業務邏輯層
│   │   └── main.py           # 應用程式入口
│   ├── .env                   # 環境變數 (不提交到 Git)
│   ├── .env.example          # 環境變數範本
│   ├── requirements.txt       # Python 依賴
│   └── alembic/              # 資料庫遷移
│
├── frontend/                  # React 前端
│   ├── public/
│   ├── src/
│   │   ├── components/       # React 元件
│   │   ├── pages/            # 頁面元件
│   │   ├── services/         # API 呼叫
│   │   ├── types/            # TypeScript 類型
│   │   ├── locales/          # 多語系檔案
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
└── 系統設計/
    └── 架構設計/
        └── 開發環境/
            └── 開發測試環境.md
```

## 技術棧

### 後端
- **框架**: FastAPI 0.115+
- **資料庫**: PostgreSQL 16+ (遠端)
- **快取**: Redis 8.4+ (遠端)
- **ORM**: SQLAlchemy 2.0+
- **驗證**: JWT + Session-based
- **API 文件**: Swagger UI (自動生成)

### 前端
- **框架**: React 19+
- **語言**: TypeScript 5.7+
- **UI 框架**: Material-UI 7+
- **路由**: React Router 7+
- **HTTP 客戶端**: Axios 1.13+
- **國際化**: i18next 25+

### 開發工具
- **版本控制**: Git
- **IDE**: VSCode / PyCharm
- **API 測試**: Postman / Swagger UI
- **資料庫管理**: pgAdmin 4 / DBeaver
- **Redis 管理**: Redis Commander

## 核心功能模組

### 1. 認證與授權系統
- JWT Token 機制
- Session 管理 (Redis)
- Transaction Token 機制 (v3.0)
  - 一個 Session 一個 Token
  - Token 內嵌權限資訊
  - 30 分鐘有效期,自動延長

### 2. 權限管理系統
- 組織 (Organizations)
- 使用者 (Users)
- 角色 (User Roles)
- 功能 (System Functions)
- 角色權限 (Role Rights)
- 六種權限類型: Create, Read, Update, Delete, Print, File

### 3. 系統管理功能
- 系統參數 (System Codes)
- 系統通知 (System Notifications)
- 使用者日誌 (User Logs)
- 檔案附件管理 (File Attachments)
- 編號規則 (Numbering Rules)

## 環境配置標準

### 後端 .env 配置範本

```env
# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
PORT=10181

# Database (遠端 PostgreSQL)
DATABASE_URL=postgresql://admin:password@10.1.0.20:5433/dbname

# Redis (遠端 Redis, 專用 DB)
REDIS_HOST=10.1.0.20
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:10180"]

# File Upload
MAX_UPLOAD_SIZE_MB=50
ALLOWED_IMAGE_TYPES=["image/png","image/jpeg","image/jpg","image/gif","image/svg+xml"]
ALLOWED_DOCUMENT_TYPES=["application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

# Shared Data Directory
SHAREDATA_DIR=sharedata
```

### 前端環境變數

```env
REACT_APP_API_BASE_URL=http://localhost:10181
```

## 資料庫設計原則

### 標準欄位
所有資料表都應包含:
```sql
id SERIAL PRIMARY KEY
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
edit_by INTEGER REFERENCES users(id)
is_active BOOLEAN DEFAULT TRUE
```

### 命名規範
- 資料表: 小寫單數名詞,單字間用底線 (user_roles)
- 欄位: 小寫,單字間用底線 (first_name)
- 外鍵: {關聯表名}_id (organization_id)
- 布林值: is_{狀態} (is_active, is_mana)

### 索引策略
- 主鍵自動建立索引
- 外鍵欄位建立索引
- 常用查詢欄位建立索引
- 複合查詢建立複合索引

## API 設計規範

### RESTful 路由結構
```
GET    /api/{resource}              # 列表 (支援分頁、篩選、排序)
GET    /api/{resource}/{id}         # 取得單筆
POST   /api/{resource}              # 新增
PUT    /api/{resource}/{id}         # 完整更新
PATCH  /api/{resource}/{id}         # 部分更新
DELETE /api/{resource}/{id}         # 刪除
```

### 標準回應格式
```json
// 成功
{
  "id": 1,
  "name": "Example",
  ...
}

// 錯誤
{
  "detail": "錯誤訊息"
}

// 列表 (分頁)
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

### 權限檢查
所有需要權限的 API 都使用 Transaction Token 驗證:
```python
@router.post("/resource")
async def create_resource(
    data: ResourceCreate,
    current_user: dict = Depends(get_current_user),
    txn_token: str = Header(..., alias="X-Transaction-Token")
):
    # 驗證權限
    verify_txn_token(
        txn_token=txn_token,
        session_id=current_user["session_id"],
        func_code="resource",
        module_item="create"
    )
    ...
```

## 前端開發規範

### 元件結構
```typescript
// 每個頁面包含:
// 1. 類型定義 (types/)
// 2. API 服務 (services/)
// 3. 頁面元件 (pages/)
// 4. 共用元件 (components/)

// 範例: UserManagementPage.tsx
import { User, UserCreate } from '../types/user';
import { getUsers, createUser } from '../services/userService';
```

### 狀態管理
- 使用 React Hooks (useState, useEffect)
- 表單狀態獨立管理
- API 呼叫使用 async/await

### 多語系
- 所有文字都使用 i18next
- 支援中文 (zh-TW) 和英文 (en)
- 翻譯檔案放在 locales/ 目錄

### API 呼叫標準
```typescript
// services/userService.ts
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:10181';

export const getUsers = async (params?: any) => {
  const token = localStorage.getItem('token');
  const txnToken = localStorage.getItem('txnToken');

  const response = await axios.get(`${API_BASE}/api/users`, {
    params,
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Transaction-Token': txnToken
    }
  });

  return response.data;
};
```

## 開發流程

### 1. 新功能開發流程
1. 設計資料表結構
2. 建立 SQLAlchemy 模型
3. 建立 Pydantic Schemas
4. 實作 Service 層業務邏輯
5. 實作 API Routes
6. 前端建立 Types
7. 前端建立 Service
8. 前端建立頁面元件
9. 測試功能
10. 更新文件

### 2. 資料庫遷移
```bash
# 建立遷移腳本
alembic revision --autogenerate -m "描述"

# 執行遷移
alembic upgrade head

# 回滾
alembic downgrade -1
```

### 3. 測試流程
- 單元測試: pytest (後端)
- API 測試: Swagger UI / Postman
- 整合測試: 前後端整合測試
- 瀏覽器測試: Chrome DevTools

## 部署準備

### 1. 環境區分
- **開發環境 (Development)**: 本機開發,DEBUG=True
- **測試環境 (Staging)**: 遠端測試,模擬正式環境
- **正式環境 (Production)**: 正式服務,DEBUG=False

### 2. 安全性檢查清單
- [ ] .env 檔案不提交到 Git
- [ ] SECRET_KEY 使用強密碼
- [ ] 資料庫密碼使用強密碼
- [ ] Redis 設定密碼
- [ ] CORS 設定正確的 ALLOWED_ORIGINS
- [ ] 檔案上傳大小限制
- [ ] 檔案類型白名單
- [ ] SQL Injection 防護 (使用 ORM)
- [ ] XSS 防護 (前端適當跳脫)
- [ ] CSRF 防護 (Token 機制)

### 3. 效能優化
- [ ] 資料庫索引優化
- [ ] Redis 快取策略
- [ ] API 回應壓縮
- [ ] 前端程式碼分割
- [ ] 靜態資源 CDN
- [ ] 圖片壓縮與優化

## 監控與維護

### 1. 日誌管理
- 使用 Python logging 模組
- 區分 DEBUG, INFO, WARNING, ERROR 級別
- 記錄關鍵操作 (登入、權限變更、資料異動)
- 定期清理舊日誌

### 2. 備份策略
- PostgreSQL: 每日自動備份
- Redis: AOF 持久化
- 程式碼: Git 版本控制
- 檔案: 定期備份 sharedata/

### 3. 健康檢查
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": db_health_check(),
        "redis": redis_health_check(),
        "version": "1.0.0"
    }
```

## 常見問題與解決方案

### 1. Redis 連線問題
**問題**: 看不到 Session/Token 資料
**解決**:
- 檢查 REDIS_HOST, REDIS_DB 配置
- 確認沒有多個後端進程運行
- 重新啟動後端載入新配置

### 2. 權限檢查失敗
**問題**: 403 Forbidden
**解決**:
- 檢查 Transaction Token 是否傳送
- 檢查使用者角色權限設定
- 檢查 func_code 是否正確

### 3. CORS 錯誤
**問題**: 前端無法呼叫 API
**解決**:
- 檢查 ALLOWED_ORIGINS 設定
- 確認前端 URL 在白名單中
- 檢查 preflight request

### 4. 資料庫連線失敗
**問題**: 無法連接到 PostgreSQL
**解決**:
- 檢查 DATABASE_URL 配置
- 確認遠端資料庫服務運行
- 檢查防火牆設定
- 測試網路連通性

## 專案啟動檢查清單

### 新專案初始化
- [ ] 複製專案範本
- [ ] 修改專案名稱和描述
- [ ] 更新 .env.example
- [ ] 建立實際的 .env 檔案
- [ ] 修改 SECRET_KEY
- [ ] 設定資料庫連線
- [ ] 設定 Redis 連線
- [ ] 安裝後端依賴 (pip install -r requirements.txt)
- [ ] 安裝前端依賴 (npm install)
- [ ] 執行資料庫遷移
- [ ] 建立初始管理員帳號
- [ ] 測試登入功能
- [ ] 測試基本 CRUD 功能

### 開發前確認
- [ ] 停止所有舊的執行序
- [ ] 確認 Port 10180, 10181 未被佔用
- [ ] 確認資料庫連線正常
- [ ] 確認 Redis 連線正常
- [ ] 啟動後端 (python -m uvicorn app.main:app --reload)
- [ ] 啟動前端 (npm start)
- [ ] 檢查瀏覽器 Console 無錯誤

## 參考文件

- FastAPI 官方文檔: https://fastapi.tiangolo.com/
- React 官方文檔: https://react.dev/
- SQLAlchemy 文檔: https://docs.sqlalchemy.org/
- Redis 文檔: https://redis.io/docs/
- PostgreSQL 文檔: https://www.postgresql.org/docs/

## 版本記錄

- v1.0.0 (2026-01-28): 初始版本,基於 PA6.4 專案架構

---

**維護者**: [你的團隊名稱]
**最後更新**: 2026-01-28
