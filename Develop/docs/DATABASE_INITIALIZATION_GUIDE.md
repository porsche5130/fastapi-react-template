# 資料庫初始化指南

> 這份指南說明如何在新專案中建立和初始化 PA6.4 資料庫

## 目錄

- [前置需求](#前置需求)
- [快速開始](#快速開始)
- [詳細步驟](#詳細步驟)
- [初始資料說明](#初始資料說明)
- [常見問題](#常見問題)

## 前置需求

### 軟體需求

- PostgreSQL 14+ (已安裝並運行)
- Python 3.13+
- psycopg2 套件

### 環境資訊

確認你已經有:
- PostgreSQL 伺服器位址和端口
- 具有建立資料庫權限的管理員帳號
- 新專案的資料庫名稱 (例如: `your_project_dev`)

## 快速開始

### 方法一: 使用 Python 腳本 (推薦)

```bash
# 1. 進入專案目錄
cd Develop/backend

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 設定資料庫連線資訊

# 4. 執行初始化腳本
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 5. 執行 Migration 腳本建立初始資料
cd migrations
python run_migration_auto.py
```

### 方法二: 使用 SQL 腳本

```bash
# 1. 建立資料庫
psql -U postgres -h localhost -c "CREATE DATABASE your_project_dev;"

# 2. 執行 Schema 腳本
psql -U postgres -h localhost -d your_project_dev -f ../../scripts/database_schema.sql

# 3. 執行初始資料腳本
psql -U postgres -h localhost -d your_project_dev -f migrations/init_sys_profile.sql
# ... 執行其他初始資料腳本
```

## 詳細步驟

### 步驟 1: 建立資料庫

#### 選項 A: 使用 psql

```bash
psql -U postgres -h localhost
```

```sql
-- 建立資料庫
CREATE DATABASE your_project_dev
    WITH OWNER = your_username
    ENCODING = 'UTF8'
    LC_COLLATE = 'zh_TW.UTF-8'
    LC_CTYPE = 'zh_TW.UTF-8';

-- 授予權限
GRANT ALL PRIVILEGES ON DATABASE your_project_dev TO your_username;
```

#### 選項 B: 使用 Python 腳本

參考 `/scripts/migration/create_remote_database.py`

### 步驟 2: 建立資料表結構

#### 使用 SQLAlchemy (推薦)

```python
# 在 Python 環境中
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
```

這會自動讀取所有 Model 並建立對應的資料表。

#### 或使用 SQL 腳本

```bash
psql -U your_username -h localhost -d your_project_dev -f scripts/database_schema.sql
```

### 步驟 3: 建立初始資料

#### 必要的初始資料

系統需要以下初始資料才能運作:

1. **組織資料** (organizations)
   - 至少需要一個管理組織

2. **管理員使用者** (users)
   - 系統需要一個初始管理員帳號

3. **使用者角色** (user_roles)
   - 至少需要一個管理員角色

4. **系統功能** (system_functions)
   - 定義所有功能模組和權限

5. **角色權限** (role_rights)
   - 設定管理員角色的權限

6. **系統設定檔** (sys_profiles)
   - 系統基本設定

#### 執行初始化腳本

```bash
cd Develop/backend/migrations

# 執行所有 migration 腳本
python run_migration_auto.py
```

或手動執行各個 SQL 腳本:

```bash
# 系統設定檔
psql -U user -d dbname -f init_sys_profile.sql

# 系統功能
psql -U user -d dbname -f 01_create_system_functions_table.sql
psql -U user -d dbname -f 02_migrate_data_to_system_functions.sql

# 其他功能
psql -U user -d dbname -f create_system_notifications.sql
psql -U user -d dbname -f create_file_attachments.sql
```

### 步驟 4: 驗證安裝

```python
# 測試資料庫連線和資料
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 檢查資料表
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """))
    tables = [row[0] for row in result]
    print(f"找到 {len(tables)} 個資料表:")
    for table in tables:
        print(f"  - {table}")

    # 檢查系統設定
    result = conn.execute(text("SELECT * FROM sys_profiles WHERE id = 1;"))
    profile = result.fetchone()
    if profile:
        print(f"\n系統名稱: {profile.sys_ctitle}")
    else:
        print("\n警告: 未找到系統設定檔！")
```

### 步驟 5: 啟動應用程式

```bash
# 啟動後端
cd Develop/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload

# 啟動前端
cd ../frontend
npm install
PORT=10180 npm start
```

## 初始資料說明

### 預設管理員帳號

```
帳號: admin@example.com
密碼: admin123
```

**重要**: 請在正式環境部署前變更此預設密碼！

### 資料表結構

系統包含以下核心資料表:

| 資料表 | 說明 | 依賴 |
|--------|------|------|
| `organizations` | 組織資料 | - |
| `users` | 使用者資料 | organizations |
| `user_roles` | 使用者角色 | users (edit_by) |
| `system_functions` | 系統功能定義 | - |
| `role_rights` | 角色權限對應 | user_roles, system_functions |
| `user_logs` | 使用者操作日誌 | users, system_functions |
| `sys_profiles` | 系統設定檔 | organizations, users |
| `system_codes` | 系統代碼 | - |
| `system_notifications` | 系統通知 | users |
| `notification_closedates` | 通知關閉日期 | system_notifications, users |
| `notification_read_today` | 今日已讀通知 | system_notifications, users |
| `file_attachments` | 檔案附件 | users |

### 外鍵依賴順序

建立資料時請注意依賴順序:

1. `organizations` (無依賴)
2. `users` (依賴 organizations)
3. `user_roles` (依賴 users)
4. `system_functions` (無依賴)
5. `role_rights` (依賴 user_roles, system_functions)
6. 其他資料表

## 常見問題

### Q1: 資料庫建立失敗

**問題**: `permission denied to create database`

**解決方案**:
```sql
-- 授予建立資料庫權限
ALTER USER your_username CREATEDB;
```

### Q2: 外鍵約束錯誤

**問題**: `violates foreign key constraint`

**解決方案**:
- 確認依照正確順序建立資料
- 檢查參照的資料是否存在
- 可以暫時停用外鍵檢查 (不建議)

### Q3: 編碼問題

**問題**: 中文亂碼

**解決方案**:
```sql
-- 確認資料庫編碼
SHOW SERVER_ENCODING;
SHOW CLIENT_ENCODING;

-- 設定正確編碼
SET CLIENT_ENCODING TO 'UTF8';
```

### Q4: 如何重新初始化資料庫

```bash
# 警告: 這會刪除所有資料！

# 方法 1: 刪除並重建資料庫
psql -U postgres -c "DROP DATABASE IF EXISTS your_project_dev;"
psql -U postgres -c "CREATE DATABASE your_project_dev;"

# 方法 2: 刪除所有資料表
psql -U user -d your_project_dev -c "DROP SCHEMA public CASCADE;"
psql -U user -d your_project_dev -c "CREATE SCHEMA public;"

# 然後重新執行初始化步驟
```

### Q5: 如何備份/還原資料庫

```bash
# 備份
pg_dump -U your_username -h localhost -d your_project_dev > backup_$(date +%Y%m%d).sql

# 還原
psql -U your_username -h localhost -d your_project_new < backup_20260129.sql
```

## 進階設定

### 使用 Alembic 進行 Migration

本範本系統提供手動 SQL migration，但你也可以使用 Alembic:

```bash
# 安裝 Alembic
pip install alembic

# 初始化 Alembic
alembic init alembic

# 建立 migration
alembic revision --autogenerate -m "Initial migration"

# 執行 migration
alembic upgrade head
```

### 環境變數設定

`.env` 檔案範例:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/your_project_dev

# Redis (選用)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security
SECRET_KEY=your-secret-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 相關文件

- [系統架構設計](../docs/SIMPLIFIED_ARCHITECTURE_DESIGN.md)
- [Schema 設計指導](../docs/SCHEMA_DESIGN_GUIDELINES.md)
- [命名規範](../docs/NAMING_STANDARDS.md)
- [Migration README](../backend/migrations/README.md)

## 問題回報

如果在初始化過程中遇到問題，請提供:
- PostgreSQL 版本
- Python 版本
- 錯誤訊息完整內容
- 執行的命令

---

**最後更新**: 2026-01-30
