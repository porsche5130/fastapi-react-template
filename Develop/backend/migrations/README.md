# 資料庫遷移說明

## 策略：先建後拆（推薦）

採用漸進式遷移策略，降低風險：
1. ✅ 建立新表 `system_functions`（包含 `module_code` 欄位）
2. ✅ 遷移資料從 `sysfunction` 到 `system_functions`
3. 🔄 開發並測試新系統（使用新表）
4. ⏳ 確認穩定後移除舊表 `sysfunction`

## 遷移概述

### 資料表正名化
- **舊表名**：`sysfunction`
- **新表名**：`system_functions`
- **原因**：複數形式符合 RESTful 慣例和路由架構設計規範

### 欄位正名化
- **舊欄位名**：`func_module_name`
- **新欄位名**：`module_code`
- **原因**：更清楚表達「模組代碼」的語意

### 設計原則

- **func_code**：功能代碼
  - 用於權限識別
  - 用於前端路由（`/{func_code}`）
  - 用於使用者日誌記錄
  - 用於前端頁面檔名（轉 PascalCase + Page.tsx）

- **module_code**：模組代碼
  - 用於後端 API 路由（`/api/{module_code}`）
  - 用於模組物件識別
  - 可對應單一資料表或多個資料表

## 遷移腳本清單

### 第一階段：建立新表和遷移資料

1. **01_create_system_functions_table.sql**
   - 建立新表 `system_functions`
   - 使用 `module_code` 欄位（取代 `func_module_name`）
   - 建立所有索引和約束
   - 舊表 `sysfunction` 保持不變

2. **02_migrate_data_to_system_functions.sql**
   - 將 `sysfunction` 的資料複製到 `system_functions`
   - 自動對應 `func_module_name` → `module_code`
   - 更新 `func_code` 從 `'sysfunction'` 改為 `'system_functions'`
   - 舊表資料保持不變

### 第二階段：清理舊表（開發完成後執行）

3. **03_cleanup_old_sysfunction.sql**
   - ⚠️ 僅在確認新系統穩定後執行
   - 建立最後備份
   - 檢查外鍵引用
   - 刪除舊表 `sysfunction`

### 輔助腳本（已廢棄，僅供參考）

- `rename_func_module_name_to_module_code.sql` - 原地改名方案（已不使用）
- `rollback_module_code_to_func_module_name.sql` - 回滾腳本（已不使用）

## 執行步驟

### 第一階段：建立新表並遷移資料

#### 1. 執行前的準備

確認以下事項：
- [ ] 已備份資料庫
- [ ] 已通知開發團隊
- [ ] 已確認沒有正在進行的交易
- [ ] 已檢查資料庫連線權限

#### 2. 執行遷移腳本

```bash
# 方法 1：使用 psql
psql -U your_username -d your_database_name

# 建立新表
\i 01_create_system_functions_table.sql

# 遷移資料
\i 02_migrate_data_to_system_functions.sql
```

或使用 Python 腳本執行：

```python
from sqlalchemy import text
from app.core.database import engine

# 建立新表
with engine.connect() as conn:
    with open('migrations/01_create_system_functions_table.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.execute(text(sql))
    conn.commit()

# 遷移資料
with engine.connect() as conn:
    with open('migrations/02_migrate_data_to_system_functions.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.execute(text(sql))
    conn.commit()
```

#### 3. 驗證遷移結果

```sql
-- 檢查兩個表是否都存在
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('sysfunction', 'system_functions');

-- 檢查新表結構
\d system_functions

-- 檢查 module_code 欄位
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'system_functions'
AND column_name = 'module_code';

-- 比較資料數量
SELECT 'sysfunction' as table_name, COUNT(*) FROM sysfunction
UNION ALL
SELECT 'system_functions' as table_name, COUNT(*) FROM system_functions;

-- 檢查資料內容（新表）
SELECT id, func_code, module_code, func_cname, func_ename
FROM system_functions
ORDER BY func_order
LIMIT 10;

-- 檢查 system_functions 自身記錄是否已更新
SELECT id, func_code, module_code, func_cname
FROM system_functions
WHERE func_code = 'system_functions';
```

### 第二階段：開發新系統

#### 4. 更新後端程式碼

建立新的檔案（與舊檔案並存）：

1. **建立新 Model**
   - 建立 `app/models/system_functions.py`
   - 定義 `SystemFunction` 類別
   - 使用 `__tablename__ = "system_functions"`
   - 使用 `module_code` 欄位

2. **建立新 Schema**
   - 建立 `app/schemas/system_functions.py`
   - 定義 `SystemFunctionBase`, `SystemFunctionCreate` 等
   - 使用 `module_code` 欄位

3. **建立新 Router**
   - 建立 `app/routes/system_functions.py`
   - 使用路由前綴 `/api/system_functions`
   - 權限檢查使用 `"system_functions"`

4. **建立新 Service（如需要）**
   - 建立 `app/services/system_functions_service.py`

5. **註冊新路由**
   - 在 `app/main.py` 中註冊新路由
   - 舊路由暫時保留

```python
# app/main.py
from app.routes import sysfunction, system_functions

# 新路由（優先使用）
app.include_router(
    system_functions.router,
    prefix="/api/system_functions",
    tags=["系統功能管理"]
)

# 舊路由（暫時保留，供舊系統使用）
app.include_router(
    sysfunction.router,
    prefix="/api/sysfunction",
    tags=["系統功能（舊）"]
)
```

#### 5. 更新前端程式碼

建立新的檔案（與舊檔案並存）：

1. **建立新 Service**
   - 建立 `src/services/systemFunctionsService.ts`
   - 使用 API 路徑 `/api/system_functions`
   - 使用 `module_code` 欄位

2. **建立新 Page 元件**
   - 建立 `src/pages/SystemFunctionsPage.tsx`
   - 使用新的 Service
   - 權限檢查使用 `'system_functions'`

3. **更新 TypeScript 介面**
   - 定義新的 `SystemFunction` 介面
   - 使用 `module_code` 欄位

4. **更新前端路由**
   - 在 `App.tsx` 中新增路由
   - 使用 `/system_functions` 路徑

```typescript
// src/App.tsx
import SysFunctionsPage from './pages/SysFunctionsPage';           // 舊
import SystemFunctionsPage from './pages/SystemFunctionsPage';     // 新

<Route path="sysfunction" element={<SysFunctionsPage />} />        {/* 舊 */}
<Route path="system_functions" element={<SystemFunctionsPage />} /> {/* 新 */}
```

#### 6. 更新 sysfunction 資料

更新資料庫中 sysfunction/system_functions 的記錄：

```sql
-- 在 system_functions 表中（已由遷移腳本完成）
UPDATE system_functions
SET func_code = 'system_functions', module_code = 'system_functions'
WHERE func_code = 'sysfunction' OR func_code = 'system_functions';

-- 如果需要，也在 sysfunction 表中更新（供舊系統使用）
UPDATE sysfunction
SET func_code = 'system_functions', func_module_name = 'system_functions'
WHERE func_code = 'sysfunction';

-- 更新權限表
UPDATE role_right
SET func_code = 'system_functions'
WHERE func_code = 'sysfunction';

-- 更新選單顯示（如果 upper_func_id 指向 sysfunction）
-- 這步驟視實際情況而定
```

#### 7. 測試新系統

- [ ] 測試新的 API 端點（`/api/system_functions`）
- [ ] 測試系統功能清單載入
- [ ] 測試選單顯示
- [ ] 測試權限檢查（使用 `'system_functions'`）
- [ ] 測試新增/編輯功能設定
- [ ] 測試日誌記錄
- [ ] 測試前端路由（`/system_functions`）
- [ ] 測試所有 CRUD 操作
- [ ] 測試與其他模組的整合

### 第三階段：清理舊系統（確認穩定後）

#### 8. 停用舊系統

當新系統運作穩定後：

1. **移除舊路由**
```python
# app/main.py
# 移除或註解掉舊路由
# app.include_router(sysfunction.router, ...)
```

2. **移除舊前端路由**
```typescript
// src/App.tsx
// 移除或註解掉舊路由
// <Route path="sysfunction" element={<SysFunctionsPage />} />
```

3. **刪除舊檔案**
   - 刪除 `app/models/sysfunction.py`
   - 刪除 `app/schemas/sysfunction.py`
   - 刪除 `app/routes/sysfunction.py`
   - 刪除 `src/services/sysfunctionService.ts`
   - 刪除 `src/pages/SysFunctionsPage.tsx`

#### 9. 執行清理腳本

```bash
# ⚠️ 確認新系統穩定運作至少一週後再執行
psql -U your_username -d your_database_name -f 03_cleanup_old_sysfunction.sql
```

#### 10. 最終驗證

```sql
-- 確認舊表已刪除
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'sysfunction';

-- 確認新表存在且有資料
SELECT COUNT(*) FROM system_functions;

-- 確認備份表存在
SELECT COUNT(*) FROM sysfunction_backup_final;
```

#### 11. 清理備份（穩定運作後）

確認系統穩定運作一段時間（建議 1 個月）後：

```sql
-- 刪除備份表
DROP TABLE IF EXISTS sysfunction_backup_final;
DROP TABLE IF EXISTS sysfunction_backup_20260121;
```

## 影響範圍

### 新建檔案

#### 後端
- ✅ `app/models/system_functions.py` (新建)
- ✅ `app/schemas/system_functions.py` (新建)
- ✅ `app/routes/system_functions.py` (新建)
- ✅ `app/services/system_functions_service.py` (新建，如需要)

#### 前端
- ✅ `src/services/systemFunctionsService.ts` (新建)
- ✅ `src/pages/SystemFunctionsPage.tsx` (新建)
- ✅ `src/types/systemFunctions.ts` (新建，或更新 types/index.ts)

### 需要更新的檔案

#### 後端
- `app/main.py` (註冊新路由)
- 其他使用 SysFunction 的 Router/Service (逐步遷移)

#### 前端
- `src/App.tsx` (新增路由)
- `src/components/Sidebar.tsx` (支援新的 func_code)
- 其他使用 sysfunction 的元件 (逐步遷移)

### 稍後刪除的檔案（確認穩定後）

#### 後端
- ❌ `app/models/sysfunction.py` (刪除)
- ❌ `app/schemas/sysfunction.py` (刪除)
- ❌ `app/routes/sysfunction.py` (刪除)
- ❌ `app/services/sysfunction_service.py` (刪除，如有)

#### 前端
- ❌ `src/services/sysfunctionService.ts` (刪除)
- ❌ `src/pages/SysFunctionsPage.tsx` (刪除)

## 搜尋指令

### 後端搜尋

```bash
cd Develop/backend

# 搜尋檔名
find . -name "*sysfunction*"

# 搜尋內容
grep -r "sysfunction" app/
grep -r "SysFunction" app/
grep -r "func_module_name" app/
grep -r '"sysfunction"' app/  # 權限檢查

# 搜尋 API 路徑
grep -r "/api/sysfunction" app/
```

### 前端搜尋

```bash
cd Develop/frontend

# 搜尋檔名
find . -name "*sysfunction*" -o -name "*SysFunction*"

# 搜尋內容
grep -r "sysfunction" src/
grep -r "SysFunction" src/
grep -r "func_module_name" src/
grep -r "'sysfunction'" src/  # 權限檢查
grep -r '"sysfunction"' src/

# 搜尋 API 路徑
grep -r "/api/sysfunction" src/
```

## 注意事項

### 關鍵提醒

1. **不要刪除舊表**：在新系統穩定前，絕不刪除 `sysfunction` 表
2. **並行運作**：新舊系統可以並行運作，透過不同的路由存取
3. **權限更新**：記得更新 `role_right` 表中的 `func_code`
4. **逐步遷移**：可以先讓部分使用者測試新系統
5. **充分測試**：確保所有功能都經過測試再清理舊系統

### 回滾計畫

如果新系統出現問題：

1. **前端回滾**：切換路由回舊的 `/sysfunction`
2. **後端回滾**：停用新路由，啟用舊路由
3. **資料同步**：如果新表有新增資料，需要手動同步回舊表

```sql
-- 緊急資料同步（如需要）
-- 將 system_functions 的新資料同步回 sysfunction
INSERT INTO sysfunction (
    func_code, upper_func_id, func_cname, func_ename,
    func_type, func_order, func_icon, func_module_name,
    module_item, description, is_mana, is_active,
    edit_by, created_at, updated_at
)
SELECT
    func_code, upper_func_id, func_cname, func_ename,
    func_type, func_order, func_icon, module_code,
    module_item, description, is_mana, is_active,
    edit_by, created_at, updated_at
FROM system_functions
WHERE id NOT IN (SELECT id FROM sysfunction)
ON CONFLICT (id) DO UPDATE SET
    func_code = EXCLUDED.func_code,
    func_module_name = EXCLUDED.func_module_name,
    -- ... 其他欄位
    updated_at = CURRENT_TIMESTAMP;
```

## 相關文件

- [路由架構設計.md](../../系統設計/應用系統設計/路由架構設計.md)
- [共用資料表設計.md](../../系統設計/應用系統設計/共用資料表設計.md)
- [Master-Detail設計.md](../../系統設計/應用系統設計/Master-Detail設計.md)
- [重構規劃_sysfunction改名.md](../../系統設計/應用系統設計/重構規劃_sysfunction改名.md)

## 檢查清單

### 資料庫遷移
- [ ] 01_create_system_functions_table.sql 執行成功
- [ ] 02_migrate_data_to_system_functions.sql 執行成功
- [ ] 新表 system_functions 建立成功
- [ ] 資料已完整遷移
- [ ] module_code 欄位存在且有值
- [ ] system_functions 記錄的 func_code 已更新

### 後端開發
- [ ] 新 Model 建立完成
- [ ] 新 Schema 建立完成
- [ ] 新 Router 建立完成
- [ ] 新路由已註冊到 main.py
- [ ] API 測試通過
- [ ] 權限檢查正常

### 前端開發
- [ ] 新 Service 建立完成
- [ ] 新 Page 元件建立完成
- [ ] 新路由已加入 App.tsx
- [ ] TypeScript 類型定義完成
- [ ] 前端功能測試通過

### 測試驗證
- [ ] 單元測試通過
- [ ] 整合測試通過
- [ ] E2E 測試通過
- [ ] 權限測試通過
- [ ] 日誌記錄正常

### 清理階段（穩定後）
- [ ] 舊路由已移除
- [ ] 舊檔案已刪除
- [ ] 03_cleanup_old_sysfunction.sql 執行成功
- [ ] 舊表已刪除
- [ ] 備份表存在
- [ ] 系統運作正常

## 更新紀錄

- 2026-01-21: 建立遷移腳本和說明文件
- 2026-01-21: 採用「先建後拆」策略，建立完整的漸進式遷移方案
