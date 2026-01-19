# PA6.4 資料庫初始化說明

## 專案資訊
- **專案名稱**: Paris Agreement Article 6.4 管理系統
- **專案代碼**: PA6.4
- **資料庫**: pa64_dev
- **版本**: 1.0.0
- **最後更新**: 2026-01-18

---

## 資料庫概覽

### 連線資訊

| 項目 | 值 |
|------|-----|
| 主機 | localhost |
| Port | 5432 |
| 資料庫 | pa64_dev |
| 使用者 | dev |
| 密碼 | dev123 |
| 連線字串 | `postgresql://dev:dev123@localhost:5432/pa64_dev` |

### 資料表總覽

| 資料表名稱 | 用途 | 記錄數 |
|-----------|------|--------|
| organizations | 組織單位明細檔 | 1 筆 (系統管理公司) |
| user_role | 使用者角色明細檔 | 1 筆 (系統管理員) |
| user_detail | 使用者明細檔 | 1 筆 (admin) |
| sysfuction | 系統功能明細檔 | 5 筆 (系統選單) |
| sys_profile | 系統設定檔 | 1 筆 (唯一) |
| userlogs | 作業紀錄表 | 0 筆 |

---

## 初始化腳本

### 執行方式

#### 方法 1: 使用 Python 腳本（推薦）

```bash
# 位置：W:\P-PA6.4\testarea
cd W:\P-PA6.4
python testarea\init_database.py
```

**輸出結果：**
```
============================================================
PA6.4 系統管理後台資料庫初始化
============================================================

正在執行 SQL 檔案: W:\P-PA6.4\Develop\backend\init_db_fixed.sql

[OK] SQL 腳本執行成功

已建立的資料表:
  - organizations
  - sys_profile
  - sysfuction
  - user_detail
  - user_role
  - userlogs

資料表記錄數:
  - organizations: 1 筆
  - sys_profile: 1 筆
  - sysfuction: 5 筆
  - user_detail: 1 筆
  - user_role: 1 筆
  - userlogs: 0 筆
```

#### 方法 2: 直接執行 SQL 檔案

```bash
# 使用 psql 指令（如果已安裝）
psql -h localhost -U dev -d pa64_dev -f W:\P-PA6.4\Develop\backend\init_db_fixed.sql
```

### SQL 檔案位置

- **主要腳本**: `W:\P-PA6.4\Develop\backend\init_db_fixed.sql`
- **測試腳本**: `W:\P-PA6.4\testarea\init_database.py`
- **驗證腳本**: `W:\P-PA6.4\testarea\verify_database.py`

---

## 初始資料

### 1. 系統管理公司 (organizations)

```sql
id: 1
org_code: 82871784
org_name: 匠耘有限公司
org_type: 2 (公司行號)
contact_person: 陳琦
contact_email: porsche@lab.taipei
contact_phone: 0910326333
is_mana: TRUE (系統管理公司)
is_active: TRUE
```

### 2. 系統管理員角色 (user_role)

```sql
id: 1
role_cname: 系統管理員
role_ename: System Administrator
description: 擁有所有系統權限
is_active: TRUE
```

### 3. 系統管理員帳號 (user_detail)

```sql
id: 1
organization_id: 1
account: admin
username: 系統管理員
password: (bcrypt hash)
user_role: [1]
is_active: TRUE
```

**預設登入帳號：**
- 帳號：`admin`
- 密碼：`admin123`

⚠️ **重要提醒：正式部署時請務必修改預設密碼！**

### 4. 系統功能選單 (sysfuction)

| ID | func_code | 功能名稱 | 類型 | 上層功能 |
|----|-----------|----------|------|----------|
| 1 | system_mana | 系統管理後台 | 節點 | 0 (根節點) |
| 2 | sys_profile | 系統設定資料 | 功能 | 1 |
| 3 | organizations | 組織設定 | 功能 | 1 |
| 4 | user_role | 使用者角色設定作業 | 功能 | 1 |
| 5 | user_detail | 使用者設定作業 | 功能 | 1 |

### 5. 系統設定 (sys_profile)

```sql
id: 1
is_service: TRUE (系統正常)
sys_url: http://localhost:10180
sys_ctitle: Paris Agreement Article 6.4 管理系統
sys_etitle: Paris Agreement Article 6.4 Management System
sys_ccopyright: Copyright © 2026 匠耘有限公司
sys_ecopyright: Copyright © 2026 JiangYun Co., Ltd.
sys_organization: 1
sys_mana_email: porsche@lab.taipei
```

---

## 資料庫驗證

執行驗證腳本以確認資料庫狀態：

```bash
cd W:\P-PA6.4
python testarea\verify_database.py
```

**驗證項目：**
1. 資料表檢查（6 張表）
2. 外鍵約束檢查（9 個外鍵）
3. 初始資料檢查（5 張表有初始資料）
4. JSONB 欄位檢查（user_role, module_item）
5. 特殊約束檢查（sys_profile 唯一性、is_mana 唯一性）
6. 資料庫資訊（版本、大小）

---

## 外鍵關聯

```
organizations (1) ──┬──< (N) user_detail
                    │
                    └──< (1) sys_profile

user_detail (1) ────┬──< (N) userlogs
                    │
                    └──< (N) user_detail (self-reference, edit_by)
                    │
                    └──< (N) organizations (edit_by)
                    │
                    └──< (N) user_role (edit_by)
                    │
                    └──< (N) sysfuction (edit_by)
                    │
                    └──< (N) sys_profile (edit_by)

user_role (1) ──────< (N) user_detail.user_role (JSONB array)

sysfuction (1) ─────┬──< (N) userlogs
                    │
                    └──< (N) sysfuction (self-reference, upper_func_id)
```

---

## 特殊設計說明

### 1. 循環依賴處理

資料表之間存在循環依賴關係（user_detail ↔ organizations），初始化腳本採用以下策略：

1. **第一階段**：建立所有表格結構，但不加入外鍵約束
2. **第二階段**：插入初始資料（organizations → user_role → user_detail → sysfuction → sys_profile）
3. **第三階段**：新增所有外鍵約束

### 2. sys_profile 唯一性

`sys_profile` 表格使用 `CHECK (id = 1)` 約束，確保只有一筆資料。

```sql
id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1)
```

### 3. organizations.is_mana 唯一性

只允許一家組織設為系統管理公司（`is_mana = TRUE`），需在應用層確保唯一性。

### 4. JSONB 欄位

- `user_detail.user_role`: `[user_role.id]` - 使用者所屬角色 ID 陣列
- `sysfuction.module_item`: `["Create","Read","Update","Delete","Print","File"]` - 模組項目陣列
- `userlogs.look_data`: `{欄位名稱: 資料內容}` - 檢視資料
- `userlogs.change_data`: `{before: {}, after: {}}` - 異動前後資料

---

## 重建資料庫

如需完全重建資料庫：

```sql
-- 警告：這會刪除所有資料！
DROP TABLE IF EXISTS userlogs CASCADE;
DROP TABLE IF EXISTS sys_profile CASCADE;
DROP TABLE IF EXISTS sysfuction CASCADE;
DROP TABLE IF EXISTS user_detail CASCADE;
DROP TABLE IF EXISTS user_role CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
```

然後重新執行初始化腳本。

---

## 開發環境設定

### Backend .env

```bash
# W:\P-PA6.4\Develop\backend\.env
DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev
```

### Python 連線範例

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='dev',
    password='dev123',
    database='pa64_dev'
)
```

### FastAPI 設定範例

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://dev:dev123@localhost:5432/pa64_dev"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## 常見問題

### Q1: 外鍵約束錯誤

**問題**：執行 SQL 時出現 `foreign key constraint violation`

**解決**：使用 `init_db_fixed.sql`，該腳本已處理循環依賴問題。

### Q2: 密碼 Hash

**問題**：如何生成新的密碼 Hash？

**解決**：使用 bcrypt

```python
import bcrypt

password = "your_password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```

### Q3: 重置序列編號

**問題**：刪除資料後，ID 序列未重置

**解決**：

```sql
SELECT setval('organizations_id_seq', (SELECT MAX(id) FROM organizations));
SELECT setval('user_role_id_seq', (SELECT MAX(id) FROM user_role));
SELECT setval('user_detail_id_seq', (SELECT MAX(id) FROM user_detail));
SELECT setval('sysfuction_id_seq', (SELECT MAX(id) FROM sysfuction));
```

---

## 更新記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-01-18 | 1.0.0 | 建立資料庫初始化腳本與說明文件 |
