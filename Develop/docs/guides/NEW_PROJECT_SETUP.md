# 使用 PA6.4 範本建立新專案指南

## 專案資訊
- **範本版本**: v1.0.0
- **最後更新**: 2026-01-29

---

## 快速開始

是的,您可以複製整個 `P-PA6.4` 目錄來開發新專案。這個範本已經包含完整的架構、權限系統、多租戶設計和最佳實踐。

---

## 複製專案步驟

### 1. 複製目錄結構

```bash
# 複製整個專案目錄到新位置
xcopy W:\P-PA6.4 W:\新專案名稱 /E /I /H

# 或使用 Git (推薦)
cd W:\新專案名稱
git clone W:\P-PA6.4\.git .
git remote remove origin  # 移除原專案的 remote
```

---

## 必須修改的配置

### 2. 後端環境配置

**檔案**: `Develop/backend/.env`

```bash
# Application - 修改專案識別
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
PORT=10181  # 如果同時運行多個專案,需要改 port

# Database - 修改資料庫名稱
DATABASE_URL=postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/新專案資料庫名稱

# Redis - 修改 DB 編號 (避免與其他專案衝突)
REDIS_HOST=10.1.0.20
REDIS_PORT=6379
REDIS_DB=2  # 改為不同的 DB 編號 (PA6.4 使用 DB 1)
REDIS_PASSWORD=!DC1qaz2wsx

# Security - 修改密鑰
SECRET_KEY=新專案-secret-key-change-in-production-2026-新專案系統名稱
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - 修改前端端口 (如果有改)
ALLOWED_ORIGINS=["http://localhost:10180"]

# File Upload
MAX_UPLOAD_SIZE_MB=50
ALLOWED_IMAGE_TYPES=["image/png","image/jpeg","image/jpg","image/gif","image/svg+xml"]
ALLOWED_DOCUMENT_TYPES=["application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

# Shared Data Directory
SHAREDATA_DIR=sharedata
```

**重要**:
- `DATABASE_URL`: 必須修改資料庫名稱
- `REDIS_DB`: 必須改為不同的編號 (1-15)
- `SECRET_KEY`: 必須使用新的密鑰

### 3. 前端環境配置

**檔案**: `Develop/frontend/.env`

```bash
# 修改 API 端點 (如果後端 port 有改)
REACT_APP_API_URL=http://localhost:10181

# 修改前端 Port (如果需要同時運行多個專案)
PORT=10180
```

### 4. 建立新資料庫

```sql
-- 在 PostgreSQL 中建立新資料庫
CREATE DATABASE 新專案資料庫名稱;

-- 授權給使用者
GRANT ALL PRIVILEGES ON DATABASE 新專案資料庫名稱 TO admin;
```

### 5. 執行資料庫遷移

```bash
cd W:\新專案名稱\Develop\backend

# 執行 migrations
python -m alembic upgrade head

# 如果沒有使用 Alembic,直接執行建表腳本
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 6. 初始化系統資料

**修改檔案**: `Develop/backend/app/core/init_data.py`

```python
# 修改組織資訊
init_org = Organization(
    org_id="新專案代碼",  # 修改為新專案代碼 (如: NEW_PROJ)
    org_name="新專案名稱",
    org_code="新專案代碼",
    # ... 其他資訊
)

# 修改系統設定
init_settings = SystemSettings(
    org_id="新專案代碼",
    setting_key="system_name",
    setting_value="新專案系統名稱",
    # ...
)
```

**執行初始化**:
```bash
cd W:\新專案名稱\Develop\backend
python app/core/init_data.py
```

---

## 選擇性修改

### 7. 專案命名

**修改檔案**: `README.md`

```markdown
# 新專案名稱

新專案的簡短描述

## 專案資訊

- **專案名稱**: 新專案全名
- **專案代碼**: NEW_PROJ
- **版本**: v1.0.0
```

**修改檔案**: `CHANGELOG.md`

```markdown
# 新專案更新日誌

## [1.0.0] - 2026-01-29

### 初始版本
- 基於 PA6.4 範本建立
- 包含完整的權限系統
- 包含多租戶架構
```

### 8. 清理歷史資料

```bash
# 清空 Git 歷史 (選擇性)
cd W:\新專案名稱
rm -rf .git
git init
git add .
git commit -m "Initial commit based on PA6.4 template"

# 刪除 PA6.4 特定的文件
cd W:\新專案名稱\Develop\docs
rm PACKAGE_COMPLETE.md  # PA6.4 封裝完成報告
```

### 9. 清空 Redis (選擇性)

```bash
# 如果要清空新專案的 Redis DB
redis-cli -h 10.1.0.20 -a !DC1qaz2wsx
SELECT 2  # 選擇新專案的 DB
FLUSHDB  # 清空當前 DB
```

---

## 同時運行多個專案

如果需要同時運行 PA6.4 和新專案:

### 修改端口配置

**新專案 Backend** (`Develop/backend/.env`):
```bash
PORT=10281  # 改為不同的 port
```

**新專案 Frontend** (`Develop/frontend/.env`):
```bash
PORT=10280  # 改為不同的 port
REACT_APP_API_URL=http://localhost:10281  # 對應後端新 port
```

**新專案 Backend CORS** (`Develop/backend/.env`):
```bash
ALLOWED_ORIGINS=["http://localhost:10280"]  # 對應前端新 port
```

### 訪問方式

| 專案 | Frontend | Backend | API Docs |
|------|----------|---------|----------|
| PA6.4 | http://localhost:10180 | http://localhost:10181 | http://localhost:10181/docs |
| 新專案 | http://localhost:10280 | http://localhost:10281 | http://localhost:10281/docs |

---

## 不需要修改的部分

以下部分可以直接使用,不需要修改:

### ✅ 架構設計
- 雙層權限架構
- org_id 多租戶設計
- 交易令牌機制
- Schema 設計模式

### ✅ 核心功能
- 認證系統 (JWT + Redis Session)
- 權限控制 (RBAC)
- 系統設定管理
- 系統通知管理

### ✅ 技術元件
- FastAPI 框架設定
- React 專案結構
- Ant Design UI 元件
- i18next 多語系

### ✅ 工具腳本
- 重啟腳本 (`restart_backend.bat`)
- 測試腳本 (`scripts/test/`)
- 遷移腳本 (`scripts/migration/`)

---

## 新專案開發流程

### 1. 複製並配置

```bash
# 複製專案
xcopy W:\P-PA6.4 W:\新專案 /E /I /H

# 修改配置檔案
# - Develop/backend/.env
# - Develop/frontend/.env
```

### 2. 建立資料庫

```sql
CREATE DATABASE 新專案db;
```

### 3. 初始化資料

```bash
cd W:\新專案\Develop\backend
python app/core/init_data.py
```

### 4. 啟動服務

```bash
# Backend
cd W:\新專案\Develop\backend
.\restart_backend.bat

# Frontend
cd W:\新專案\Develop\frontend
npm start
```

### 5. 開發新功能

參考 [FEATURE_DEVELOPMENT_TEMPLATE.md](FEATURE_DEVELOPMENT_TEMPLATE.md) 開發新功能。

---

## 配置檢查清單

使用此檢查清單確保新專案配置正確:

### 必須修改
- [ ] `.env` 資料庫名稱 (DATABASE_URL)
- [ ] `.env` Redis DB 編號 (REDIS_DB)
- [ ] `.env` 密鑰 (SECRET_KEY)
- [ ] `init_data.py` 組織資訊 (org_id, org_name)
- [ ] `README.md` 專案名稱和描述

### 如果同時運行多個專案
- [ ] `.env` Backend Port (PORT)
- [ ] `.env` Frontend Port (PORT)
- [ ] `.env` API URL (REACT_APP_API_URL)
- [ ] `.env` CORS Origins (ALLOWED_ORIGINS)

### 選擇性
- [ ] Git 歷史清理
- [ ] `CHANGELOG.md` 更新
- [ ] PA6.4 特定文件刪除

---

## 範本優勢

使用 PA6.4 作為範本,您可以獲得:

1. **完整的權限系統**
   - 雙層權限架構 (功能權限 + 操作權限)
   - RBAC 實作
   - 交易令牌保護

2. **多租戶架構**
   - org_id 資料隔離
   - 完整的租戶管理

3. **最佳實踐**
   - Schema 設計指導
   - 命名規範
   - 錯誤處理

4. **完整文檔**
   - 架構設計文檔
   - 開發指南
   - 部署策略

5. **開發工具**
   - 測試腳本
   - 重啟腳本
   - 遷移腳本

---

## 常見問題

### Q1: 可以刪除 PA6.4 特定的功能嗎?

可以。如果新專案不需要某些功能,可以刪除:
- 對應的 Model (`backend/app/models/`)
- 對應的 Schema (`backend/app/schemas/`)
- 對應的 Route (`backend/app/routes/`)
- 對應的 Service (`frontend/src/services/`)
- 對應的 Page (`frontend/src/pages/`)

### Q2: 如何新增專案特定的功能?

參考 [FEATURE_DEVELOPMENT_TEMPLATE.md](FEATURE_DEVELOPMENT_TEMPLATE.md) 開發新功能。

### Q3: 資料庫結構需要修改嗎?

基礎表 (organizations, users, user_roles, permissions) 建議保留。您可以:
- 新增業務特定的資料表
- 修改或移除不需要的資料表

### Q4: 多語系檔案需要修改嗎?

需要。修改 `frontend/src/locales/` 中的翻譯檔案,替換為新專案的文字。

---

## 技術支援

如有問題,請參考:
- [SIMPLIFIED_ARCHITECTURE_DESIGN.md](../SIMPLIFIED_ARCHITECTURE_DESIGN.md) - 架構說明
- [FEATURE_DEVELOPMENT_TEMPLATE.md](FEATURE_DEVELOPMENT_TEMPLATE.md) - 開發指南
- [DEVELOPMENT_ENVIRONMENT.md](../DEVELOPMENT_ENVIRONMENT.md) - 環境設定

---

**最後更新**: 2026-01-29
**範本版本**: v1.0.0
