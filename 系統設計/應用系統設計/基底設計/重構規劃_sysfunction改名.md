# 重構規劃：sysfunction 改名為 system_functions

## 變更概述

將系統中的 `sysfunction` 相關命名統一改為 `system_functions`（複數形式），同時將 `func_module_name` 改為 `module_code`。

## 變更原因

根據路由架構設計的命名規範：
- **操作多筆物件時用複數**：sysfunction 是管理多個系統功能的模組，應使用複數 `system_functions`
- **語意清晰**：`system_functions` 比 `sysfunction` 更符合 RESTful 命名慣例
- **欄位名稱優化**：`module_code` 比 `func_module_name` 更清楚表達「模組代碼」的意義

## 變更範圍

### 1. 資料庫層

#### 資料表改名
```sql
-- 從
sysfunction

-- 改為
system_functions
```

#### 欄位改名
```sql
-- 從
func_module_name

-- 改為
module_code
```

#### 約束和索引
- 更新所有包含 `sysfunction` 的約束名稱
- 更新所有包含 `func_module_name` 的約束名稱
- 更新所有相關索引

### 2. 後端程式碼

#### 檔案改名

| 舊檔案名稱 | 新檔案名稱 |
|-----------|-----------|
| app/models/sysfunction.py | app/models/system_functions.py |
| app/schemas/sysfunction.py | app/schemas/system_functions.py |
| app/routes/sysfunction.py | app/routes/system_functions.py |
| app/services/sysfunction_service.py | app/services/system_functions_service.py |

#### Model 類別改名

```python
# 從
class SysFunction(Base):
    __tablename__ = "sysfunction"

# 改為
class SystemFunction(Base):
    __tablename__ = "system_functions"
```

#### Schema 類別改名

```python
# 從
SysFunctionBase
SysFunctionCreate
SysFunctionUpdate
SysFunctionResponse

# 改為
SystemFunctionBase
SystemFunctionCreate
SystemFunctionUpdate
SystemFunctionResponse
```

#### 欄位名稱

所有檔案中的 `func_module_name` 改為 `module_code`

#### API 路由

```python
# 從
/api/sysfunction

# 改為
/api/system_functions
```

#### func_code 變更

所有使用 `"sysfunction"` 作為權限檢查的地方改為 `"system_functions"`：
```python
# 從
check_permission(db, current_user, "sysfunction", "read")

# 改為
check_permission(db, current_user, "system_functions", "read")
```

### 3. 前端程式碼

#### 檔案改名

| 舊檔案名稱 | 新檔案名稱 |
|-----------|-----------|
| src/services/sysfunctionService.ts | src/services/systemFunctionsService.ts |
| src/pages/SysFunctionsPage.tsx | src/pages/SystemFunctionsPage.tsx |

#### TypeScript 介面改名

```typescript
// 從
interface SysFunction {
  ...
  func_module_name?: string;
}

// 改為
interface SystemFunction {
  ...
  module_code?: string;
}
```

#### API 路徑

```typescript
// 從
/api/sysfunction

// 改為
/api/system_functions
```

#### 前端路由

```typescript
// 從
<Route path="sysfunction" element={<SysFunctionsPage />} />

// 改為
<Route path="system_functions" element={<SystemFunctionsPage />} />
```

#### func_code 變更

所有使用 `"sysfunction"` 作為權限檢查的地方改為 `"system_functions"`：
```typescript
// 從
hasPermission('sysfunction', 'read')

// 改為
hasPermission('system_functions', 'read')
```

### 4. 資料庫資料

#### sysfunction 表自身記錄

```sql
-- 需要更新 sysfunction 表中描述自己的那筆記錄
UPDATE system_functions
SET
  func_code = 'system_functions',
  module_code = 'system_functions',
  func_cname = '系統功能設定',
  func_ename = 'System Functions'
WHERE func_code = 'sysfunction';
```

#### role_right 表

```sql
-- 更新所有引用 sysfunction 的權限記錄
UPDATE role_right
SET func_code = 'system_functions'
WHERE func_code = 'sysfunction';
```

#### userlogs 表

```sql
-- 更新歷史日誌中的 func_code（如果有的話）
UPDATE userlogs
SET func_code = 'system_functions'
WHERE func_code = 'sysfunction';
```

## 影響檔案清單

### 後端檔案

#### 核心檔案（需要改名）
- ✅ app/models/sysfunction.py → system_functions.py
- ✅ app/schemas/sysfunction.py → system_functions.py
- ✅ app/routes/sysfunction.py → system_functions.py
- ✅ app/services/sysfunction_service.py → system_functions_service.py (如果有)

#### 需要更新引用的檔案
- app/main.py (路由註冊)
- app/core/permissions.py (可能有引用)
- app/routes/*.py (所有使用 SysFunction model 的路由)
- app/services/*.py (所有使用 SysFunction model 的服務)
- tests/ (所有測試檔案)

### 前端檔案

#### 核心檔案（需要改名）
- ✅ src/services/sysfunctionService.ts → systemFunctionsService.ts
- ✅ src/pages/SysFunctionsPage.tsx → SystemFunctionsPage.tsx

#### 需要更新引用的檔案
- src/types/index.ts 或 src/types/sysfunction.ts
- src/services/systemService.ts
- src/components/Sidebar.tsx
- src/App.tsx (路由設定)
- src/hooks/usePermission.ts (可能有引用)
- src/contexts/AuthContext.tsx (可能有引用)

### 資料庫檔案

- migrations/ (所有初始化腳本)
- seeds/ (測試資料)
- docs/ (資料庫文件)

### 文件檔案

- ✅ 系統設計/應用系統設計/路由架構設計.md
- ✅ 系統設計/應用系統設計/共用資料表設計.md
- ✅ 系統設計/資料庫設計/共用資料表設計.md (如果有)
- README.md
- API 文件

## 執行步驟

### 第一階段：規劃與文件（已完成部分）

- [x] 建立重構規劃文件
- [x] 更新路由架構設計文件（已更新 func_module_name → module_code）
- [x] 更新共用資料表設計文件
- [ ] 更新所有文件中的 sysfunction 為 system_functions

### 第二階段：資料庫遷移腳本

1. [ ] 建立完整的遷移腳本（包含資料表改名和欄位改名）
2. [ ] 建立回滾腳本
3. [ ] 建立資料更新腳本（更新 role_right, userlogs 等）

### 第三階段：後端程式碼

1. [ ] 重新命名 Model 檔案和類別
2. [ ] 重新命名 Schema 檔案和類別
3. [ ] 重新命名 Router 檔案和更新路由
4. [ ] 更新 Service 檔案（如果有）
5. [ ] 更新 main.py 中的路由註冊
6. [ ] 搜尋並更新所有 `"sysfunction"` func_code 引用
7. [ ] 搜尋並更新所有 `func_module_name` 欄位引用
8. [ ] 更新所有 import 語句

### 第四階段：前端程式碼

1. [ ] 重新命名 Service 檔案
2. [ ] 重新命名 Page 檔案
3. [ ] 更新 TypeScript 介面定義
4. [ ] 更新 App.tsx 路由設定
5. [ ] 搜尋並更新所有 `"sysfunction"` func_code 引用
6. [ ] 搜尋並更新所有 `func_module_name` 欄位引用
7. [ ] 更新所有 import 語句
8. [ ] 更新 API 路徑

### 第五階段：測試與驗證

1. [ ] 執行資料庫遷移
2. [ ] 驗證資料庫結構
3. [ ] 驗證資料完整性
4. [ ] 後端單元測試
5. [ ] 後端整合測試
6. [ ] 前端功能測試
7. [ ] E2E 測試
8. [ ] 權限功能測試

### 第六階段：部署與監控

1. [ ] 建立部署檢查清單
2. [ ] 準備回滾計畫
3. [ ] 執行部署
4. [ ] 監控系統狀態
5. [ ] 確認無誤後清理備份

## 搜尋指令

### 後端搜尋

```bash
# 搜尋 sysfunction（檔名和內容）
cd Develop/backend
find . -name "*sysfunction*"
grep -r "sysfunction" app/
grep -r "SysFunction" app/
grep -r "func_module_name" app/

# 搜尋權限檢查
grep -r '"sysfunction"' app/
```

### 前端搜尋

```bash
# 搜尋 sysfunction（檔名和內容）
cd Develop/frontend
find . -name "*sysfunction*" -o -name "*SysFunction*"
grep -r "sysfunction" src/
grep -r "SysFunction" src/
grep -r "func_module_name" src/

# 搜尋權限檢查
grep -r "'sysfunction'" src/
grep -r '"sysfunction"' src/
```

## 風險評估

### 高風險項目

1. **資料表改名**
   - 影響：所有使用該表的查詢都會失效
   - 緩解：完整的測試和回滾方案

2. **權限系統**
   - 影響：func_code 改變可能導致權限失效
   - 緩解：必須同步更新 role_right 表資料

3. **日誌系統**
   - 影響：歷史日誌中的 func_code 會不一致
   - 緩解：可以選擇更新或保留歷史資料

### 中風險項目

1. **API 路徑變更**
   - 影響：前端需要同步更新
   - 緩解：前後端同時部署

2. **Import 路徑**
   - 影響：大量檔案需要更新
   - 緩解：使用 IDE 重構工具

### 低風險項目

1. **檔案改名**
   - 影響：需要更新 import
   - 緩解：自動化工具處理

2. **變數改名**
   - 影響：局部影響
   - 緩解：逐一檢查

## 建議

### 策略選擇

**方案 A：漸進式重構（推薦）**
1. 先建立新的 system_functions 表（複製 sysfunction）
2. 新功能使用新表和新命名
3. 舊功能保持不變
4. 逐步遷移功能
5. 確認穩定後刪除舊表

優點：風險低，可逐步驗證
缺點：過渡期維護兩套系統

**方案 B：一次性重構（快速但風險較高）**
1. 停機維護
2. 執行完整遷移腳本
3. 同時更新所有程式碼
4. 完整測試後上線

優點：快速完成，無過渡期
缺點：風險高，需要長時間停機

### 建議採用方案 A

考慮到系統穩定性和風險控管，建議採用漸進式重構方式。

## 檢查清單

### 資料庫
- [ ] 資料表已改名
- [ ] 欄位已改名
- [ ] 索引已更新
- [ ] 約束已更新
- [ ] 資料完整性已驗證
- [ ] role_right 資料已更新
- [ ] userlogs 資料已更新（可選）

### 後端
- [ ] Model 檔案已改名
- [ ] Schema 檔案已改名
- [ ] Router 檔案已改名
- [ ] Service 檔案已改名（如果有）
- [ ] main.py 已更新
- [ ] 所有 import 已更新
- [ ] 所有 func_code 引用已更新
- [ ] 所有 func_module_name 已改為 module_code
- [ ] API 路徑已更新

### 前端
- [ ] Service 檔案已改名
- [ ] Page 檔案已改名
- [ ] TypeScript 介面已更新
- [ ] App.tsx 路由已更新
- [ ] 所有 import 已更新
- [ ] 所有 func_code 引用已更新
- [ ] 所有 func_module_name 已改為 module_code
- [ ] API 路徑已更新

### 測試
- [ ] 單元測試通過
- [ ] 整合測試通過
- [ ] E2E 測試通過
- [ ] 權限測試通過
- [ ] 日誌測試通過

### 文件
- [ ] API 文件已更新
- [ ] 系統設計文件已更新
- [ ] README 已更新
- [ ] 部署文件已更新

## 更新紀錄

- 2026-01-21: 建立重構規劃文件
