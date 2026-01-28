# PA6.4 命名規範標準文件

## 更新日期
2026-01-21

## 核心原則

### 1. 資料表命名
- **資料表名稱**: 使用**複數**形式
- **範例**: `system_functions`, `user_roles`, `user_logs`, `role_rights`

### 2. Model 類別命名
- **類別名稱**: 使用**單數** PascalCase
- **範例**: `SystemFunction`, `UserRole`, `UserLog`, `RoleRight`

### 3. 外鍵欄位命名
- **格式**: `{資料表單數名稱}_id`
- **範例**:
  - `system_function_id` → 指向 `system_functions.id`
  - `user_role_id` → 指向 `user_roles.id`
  - `user_id` → 指向 `users.id`

### 4. Relationship 變數命名
- **一對一關係**: 使用**單數**
- **一對多關係**: 使用**複數**
- **範例**:
  ```python
  # 在 RoleRight model 中
  system_function = relationship("SystemFunction")  # 一對一，單數
  
  # 在 SystemFunction model 中
  role_rights = relationship("RoleRight")  # 一對多，複數
  ```

## system_functions 資料表規範

### 資料表結構
```sql
CREATE TABLE system_functions (
    id SERIAL PRIMARY KEY,
    func_code VARCHAR(200),      -- 功能代碼（前端路由、權限、日誌使用）
    module_code VARCHAR(200),    -- 模組代碼（後端 API 路由使用）
    upper_func_id INTEGER,
    func_cname VARCHAR(200),
    func_ename VARCHAR(200),
    func_type INTEGER,           -- 1:節點, 2:功能
    func_order INTEGER,
    func_icon VARCHAR(200),
    module_item JSONB,           -- ["Create", "Read", "Update", "Delete", "Print", "File"]
    description TEXT,
    is_mana BOOLEAN,
    is_active BOOLEAN,
    edit_by INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### func_code vs module_code

#### func_code (功能代碼)
- **用途**: 
  - 前端路由路徑
  - 權限檢查標識
  - 日誌記錄標識
- **命名規則**: 
  - 操作多筆物件 → 複數 (例: `users`, `user_roles`)
  - 操作單一物件 → 單數 (例: `user_profile`)

#### module_code (模組代碼)
- **用途**:
  - 後端 API 路由前綴
  - 模組物件識別
  - 定義處理的資料表
- **命名規則**: 
  - 單一資料表 → 與資料表同名
  - 多資料表模組 → 模組名稱

#### 可以不同
- `func_code` 和 `module_code` **可以不同**
- 範例:
  ```
  func_code: tenant_users
  module_code: users
  ```

## 路由命名規範

### 前端路由 (使用 func_code)
```typescript
// App.tsx
<Route path="user_roles" element={<UserRolesPage />} />
<Route path="users" element={<UsersPage />} />
<Route path="role_rights" element={<RoleRightsPage />} />
```

### 後端 API 路由 (使用 module_code)
```python
# main.py
app.include_router(user_roles.router, prefix="/api/user_roles", tags=["角色管理"])
app.include_router(users.router, prefix="/api/users", tags=["使用者管理"])
app.include_router(role_rights.router, prefix="/api/role_rights", tags=["角色權限"])
```

### 頁面檔名 (根據 func_code)
- **規則**: `func_code` 去除底線，轉為 PascalCase + `Page.tsx`
- **範例**:
  - `user_roles` → `UserRolesPage.tsx`
  - `role_rights` → `RoleRightsPage.tsx`
  - `system_functions` → `SystemFunctionsPage.tsx`

## 完整對照表

| func_code | module_code | 資料表 | 前端路由 | 後端API | 頁面檔案 | 外鍵欄位 |
|-----------|-------------|--------|---------|---------|---------|---------|
| system_functions | system_functions | system_functions | /system_functions | /api/system_functions | SystemFunctionsPage.tsx | system_function_id |
| user_roles | user_roles | user_roles | /user_roles | /api/user_roles | UserRolesPage.tsx | user_role_id |
| users | users | users | /users | /api/users | UsersPage.tsx | user_id |
| role_rights | role_rights | role_rights | /role_rights | /api/role_rights | RoleRightsPage.tsx | - |
| user_logs | user_logs | user_logs | /user_logs | /api/user_logs | UserLogsPage.tsx | - |
| sys_profile | sys_profiles | sys_profiles | /sys_profile | /api/sys_profiles | SysProfilePage.tsx | - |

## 日誌記錄規範

### 使用 func_code
```typescript
// 前端
await logView('user_roles', data, null);
await logCreate('users', newUser);
await logUpdate('role_rights', oldData, newData);
```

```python
# 後端
await UserLogService.log_action(
    db=db,
    user_id=current_user.id,
    func_code='user_roles',  # 使用 func_code
    module_item='Update',
    action_desc='更新角色資料'
)
```

## 權限檢查規範

### 使用 func_code
```typescript
const { hasPermission } = usePermission();
const canCreate = hasPermission('user_roles', 'Create');
const canUpdate = hasPermission('users', 'Update');
```

## 禁止使用的命名

### ❌ 錯誤範例
- `system_functions_id` (外鍵不用複數_id)
- `SystemFunctions` (Model 類別不用複數)
- `user_detail_id` (舊欄位名，應為 user_id)
- `sysfunction_id` (舊欄位名，應為 system_function_id)
- `func_module_name` (舊欄位名，應為 module_code)

### ✅ 正確範例
- `system_function_id` (外鍵用單數_id)
- `SystemFunction` (Model 類別用單數)
- `user_id` (新欄位名)
- `system_function_id` (新欄位名)
- `module_code` (新欄位名)

## 檢查清單

開發新功能時，請確認：

- [ ] 資料表名稱使用複數
- [ ] Model 類別名稱使用單數 PascalCase
- [ ] 外鍵欄位使用 `{單數}_id` 格式
- [ ] 前端路由使用 func_code
- [ ] 後端 API 使用 module_code
- [ ] 頁面檔名符合 func_code 轉換規則
- [ ] 日誌記錄使用 func_code
- [ ] 權限檢查使用 func_code
- [ ] Relationship 變數根據關係類型使用單複數

---
版本: 1.0
最後更新: 2026-01-21
