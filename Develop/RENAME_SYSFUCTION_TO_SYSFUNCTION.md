# 重新命名 sysfuction → sysfunction

## 修正日期
2026-01-20

## 修正原因
原始命名 `sysfuction` 拼寫錯誤，應為 `sysfunction`（包含 'n'）

## 資料庫變更

### 1. 資料表重新命名
```sql
ALTER TABLE sysfuction RENAME TO sysfunction;
```

### 2. 索引重新命名
```sql
ALTER INDEX idx_sysfuction_code RENAME TO idx_sysfunction_code;
ALTER INDEX idx_sysfuction_upper RENAME TO idx_sysfunction_upper;
ALTER INDEX idx_sysfuction_type RENAME TO idx_sysfunction_type;
ALTER INDEX idx_sysfuction_active RENAME TO idx_sysfunction_active;
ALTER INDEX idx_sysfuction_order RENAME TO idx_sysfunction_order;
```

### 3. 序列重新命名
```sql
ALTER SEQUENCE sysfuction_id_seq RENAME TO sysfunction_id_seq;
```

### 4. 欄位重新命名
```sql
-- 重新命名 role_right 表的外鍵欄位
ALTER TABLE role_right RENAME COLUMN sysfuction_id TO sysfunction_id;

-- 注意：userlog 表尚未建立，暫時跳過
-- ALTER TABLE userlog RENAME COLUMN sysfuction_id TO sysfunction_id;
```

### 5. 資料更新
```sql
-- 更新 sysfunction 表的 func_code
UPDATE sysfunction SET func_code = 'sysfunction' WHERE func_code = 'sysfuction';

-- 更新 role_right 表的 func_code
UPDATE role_right SET func_code = 'sysfunction' WHERE func_code = 'sysfuction';
```

## 後端變更

### 1. 檔案重新命名
- `app/models/sysfuction.py` → `app/models/sysfunction.py`
- `app/routes/sysfuction.py` → `app/routes/sysfunction.py`
- `app/schemas/sysfuction.py` → `app/schemas/sysfunction.py`

### 2. 程式碼全域替換
所有 `.py` 檔案中的 `sysfuction` 替換為 `sysfunction`

#### 主要影響的檔案：
- `app/main.py` - 路由導入和註冊
- `app/models/role_right.py` - 外鍵參照
- `app/models/userlog.py` - 外鍵參照
- `app/models/__init__.py` - 模型導入
- `app/routes/role_right.py` - 導入
- `add_permissions_batch.py` - 權限批次處理

### 3. API 端點變更
- `/api/sysfuction/` → `/api/sysfunction/`

## 前端變更

### 1. 程式碼全域替換
所有 `.ts` 和 `.tsx` 檔案中的 `sysfuction` 替換為 `sysfunction`

#### 主要影響的檔案：
- `src/App.tsx` - 路由路徑從 `/sysfuction` → `/sysfunction`
- `src/pages/SysFunctionsPage.tsx` - hasPermission 使用 'sysfunction'
- `src/services/sysFunctionService.ts` - API 路徑
- `src/services/roleRightService.ts` - 型別定義
- `src/pages/RoleRightPage.tsx` - 欄位名稱
- `src/components/Sidebar.tsx` - 註解

### 2. 權限 func_code 變更
- 原: `hasPermission('sysfuction', 'read')`
- 新: `hasPermission('sysfunction', 'read')`

## 驗證步驟

### 1. 後端驗證
```bash
# 測試 Python 導入
python -c "from app.models.sysfunction import SysFunction; print(SysFunction.__tablename__)"
# 輸出: sysfunction

# 測試 API
curl http://localhost:10181/api/sysfunction/
# 輸出: {"detail":"Not authenticated"}  (表示路由正常)
```

### 2. 前端驗證
1. 清除瀏覽器快取
2. 重新登入系統
3. 訪問「系統功能設定作業」頁面
4. 應該可以正常顯示並有完整的 CRUD 功能

### 3. 資料庫驗證
```sql
-- 檢查資料表存在
SELECT tablename FROM pg_tables WHERE tablename = 'sysfunction';

-- 檢查 func_code 已更新
SELECT func_code FROM sysfunction WHERE id = 9;
-- 預期: sysfunction

-- 檢查 role_right 的 func_code
SELECT DISTINCT func_code FROM role_right WHERE func_code LIKE '%function%';
-- 預期: sysfunction
```

## 回滾方案（如需要）

如果需要回滾，執行以下步驟（**不建議，僅供參考**）：

```sql
BEGIN;
ALTER TABLE sysfunction RENAME TO sysfuction;
ALTER INDEX idx_sysfunction_code RENAME TO idx_sysfuction_code;
ALTER INDEX idx_sysfunction_upper RENAME TO idx_sysfuction_upper;
ALTER INDEX idx_sysfunction_type RENAME TO idx_sysfuction_type;
ALTER INDEX idx_sysfunction_active RENAME TO idx_sysfuction_active;
ALTER INDEX idx_sysfunction_order RENAME TO idx_sysfuction_order;
ALTER SEQUENCE sysfunction_id_seq RENAME TO sysfuction_id_seq;
UPDATE sysfuction SET func_code = 'sysfuction' WHERE func_code = 'sysfunction';
UPDATE role_right SET func_code = 'sysfuction' WHERE func_code = 'sysfunction';
COMMIT;
```

然後還原所有程式碼變更。

## 影響評估
- ✅ 不影響現有數據
- ✅ 不影響系統功能
- ✅ 僅為命名規範化
- ✅ 需要重新登入以清除前端權限快取
- ✅ 外鍵約束自動跟隨表名更新

## 完成狀態
✅ 資料庫表名已更新
✅ 資料庫索引已更新
✅ 資料庫序列已更新
✅ 資料庫資料已更新
✅ 後端檔案已重新命名
✅ 後端程式碼已更新
✅ 前端程式碼已更新
✅ API 端點已更新
✅ 權限 func_code 已更新
✅ 所有導入測試通過
✅ API 端點測試通過
