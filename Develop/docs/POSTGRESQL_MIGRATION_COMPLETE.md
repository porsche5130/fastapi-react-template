# PostgreSQL 資料庫遷移完成記錄

## 遷移資訊
- **日期**: 2026-01-28
- **來源**: localhost:5432/pa64_dev (dev/dev123)
- **目標**: 10.1.0.20:5433/pa64_dev (admin/!DC1qaz2wsx)
- **狀態**: ✅ 成功完成

---

## 遷移概要

### 資料統計
- **資料表數量**: 14 個表
- **資料筆數**: 1,681 筆
- **序列數量**: 13 個序列
- **主鍵**: 14 個
- **外鍵**: 24 個
- **索引**: 55 個

### 主要資料表
| 表名 | 筆數 | 說明 |
|------|------|------|
| users | 7 | 使用者資料 |
| organizations | 3 | 組織資料 |
| user_roles | 6 | 角色定義 |
| role_rights | 77 | 角色權限 |
| system_functions | 22 | 系統功能 |
| user_logs | 1,554 | 使用者日誌 |
| sequence_rules | 4 | 單號規則 |
| file_attachments | 1 | 檔案附件 |
| notification_closedates | 2 | 通知關閉日期 |
| system_notifications | 2 | 系統通知 |
| system_codes | 1 | 系統代碼 |
| sys_profiles | 1 | 系統設定 |
| sequence_values | 1 | 序號值 |
| notification_read_today | 0 | 今日已讀通知 |

---

## 遷移步驟

### 1. 建立遠端資料庫
```bash
python create_remote_database.py
```
- ✅ 成功建立 pa64_dev 資料庫
- Owner: admin
- Encoding: UTF8
- Template: template0

### 2. 資料遷移
```bash
python migrate_db_complete.py
```

**遷移內容**:
1. ✅ 匯出本機 Schema (DDL)
   - 13 個序列
   - 14 個表結構
   - 14 個主鍵
   - 24 個外鍵
   - 55 個索引

2. ✅ 匯出本機資料
   - 1,681 筆資料

3. ✅ 還原 Schema 到遠端
   - 清除現有結構
   - 建立序列、表、約束、索引
   - 120 個 DDL 成功執行

4. ✅ 還原資料到遠端
   - 按照外鍵依賴順序插入
   - 處理 JSONB 類型轉換
   - 更新序列值

### 3. 驗證遷移結果
```bash
python verify_migration.py
```

**驗證結果**:
- ✅ 表數量一致: 本機 14 個 = 遠端 14 個
- ✅ 資料筆數一致: 所有表的筆數完全相同
- ✅ 序列值正確: 大部分序列值一致 (差異為已刪除記錄)
- ✅ JSONB 資料正確: user_role 等 JSONB 欄位正確儲存
- ✅ 外鍵關聯正常: user_logs 等關聯表查詢正常

---

## 後端配置更新

### config.py 更新
**檔案**: `Develop/backend/app/core/config.py`

```python
# 更新前 (本機)
DATABASE_URL: str = Field(
    default="postgresql://dev:dev123@localhost:5432/pa64_dev"
)

# 更新後 (遠端)
DATABASE_URL: str = Field(
    default="postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev"
)
```

### 後端重啟
```bash
cd Develop/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 10181
```

**啟動結果**:
- ✅ 成功連線到遠端 PostgreSQL
- ✅ 成功連線到遠端 Redis (10.1.0.20:6379 DB 1)
- ✅ 應用程式啟動完成

---

## 目前環境配置

### 完整架構
```
PA6.4 開發測試環境
├── PostgreSQL (遠端)
│   └── 10.1.0.20:5433/pa64_dev (admin/!DC1qaz2wsx)
│
├── Redis (遠端)
│   └── 10.1.0.20:6379 DB 1 (!DC1qaz2wsx)
│
└── 應用服務 (本機)
    ├── Backend: localhost:10181 (FastAPI)
    └── Frontend: localhost:10180 (React + Vite)
```

### 連線資訊

#### PostgreSQL
```
Host: 10.1.0.20
Port: 5433
Database: pa64_dev
User: admin
Password: !DC1qaz2wsx

Connection String:
postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev
```

#### Redis
```
Host: 10.1.0.20
Port: 6379
Database: 1
Password: !DC1qaz2wsx

Connection String:
redis://:!DC1qaz2wsx@10.1.0.20:6379/1
```

---

## 遷移工具

### 已建立的遷移腳本

1. **create_remote_database.py**
   - 在遠端伺服器建立 pa64_dev 資料庫

2. **migrate_db_complete.py**
   - 完整的資料庫遷移工具
   - 處理 Schema (序列、表、約束、索引)
   - 處理資料 (按依賴順序插入)
   - 處理特殊類型 (JSONB, ARRAY)
   - 更新序列值

3. **verify_migration.py**
   - 驗證遷移結果
   - 比對表數量
   - 比對資料筆數
   - 比對序列值
   - 測試範例查詢

### 測試腳本

- test_pg_admin.py - PostgreSQL 連線測試
- test_pg_simple.py - 簡易連線測試
- test_pg_info.py - 端口測試
- test_postgres_remote.py - 完整功能測試

---

## 注意事項

### 1. 序列值差異
以下序列在遠端的值略低於本機 (正常現象):
- organizations_id_seq: 本機 11 → 遠端 3 (已刪除 8 筆組織)
- system_functions_id_seq: 本機 28 → 遠端 26 (已刪除 2 個功能)
- user_roles_id_seq: 本機 7 → 遠端 6 (已刪除 1 個角色)

這些差異是因為本機有刪除記錄,序列值不會回退。遠端資料庫序列值已設定為當前最大 ID,後續新增資料不會有問題。

### 2. JSONB 資料類型
所有 JSONB 欄位 (如 user_role, module_item, module_actions) 都已正確遷移,可正常查詢和操作。

### 3. 外鍵約束
所有外鍵約束都已正確建立,資料完整性受到保護。

### 4. 本機資料庫
本機 PostgreSQL (localhost:5432) 的資料已完整保留,可作為備份使用。

---

## 遷移後測試

### 建議測試項目
- [ ] 使用者登入功能
- [ ] 組織資料查詢
- [ ] 角色權限檢查
- [ ] 單號規則運作
- [ ] 檔案上傳/下載
- [ ] 通知功能
- [ ] 使用者日誌記錄

### 測試方式
1. 啟動後端: `cd Develop/backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 10181`
2. 啟動前端: `cd Develop/frontend && npm run dev`
3. 開啟瀏覽器: http://localhost:10180
4. 執行各項功能測試

---

## 回滾方案

如果需要回滾到本機資料庫,執行以下步驟:

1. 停止後端服務
2. 修改 `config.py`:
   ```python
   DATABASE_URL: str = Field(
       default="postgresql://dev:dev123@localhost:5432/pa64_dev"
   )
   ```
3. 重新啟動後端服務

---

## 總結

✅ **資料庫遷移成功完成**

- 所有資料表、資料、序列、約束、索引都已成功遷移
- 後端已配置為使用遠端 PostgreSQL
- 驗證測試全部通過
- 系統可正常運作

**下一步**: 執行完整的功能測試,確認所有業務功能正常運作。
