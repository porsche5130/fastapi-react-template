# System Functions 命名一致性驗證報告

## 資料來源
- **資料表**: system_functions
- **查詢時間**: 2026-01-21
- **記錄數**: 18 筆功能記錄 (func_type=2)

## 驗證項目

每個功能需要檢查以下項目：

1. **前端路由** (App.tsx) - 使用 `func_code`
2. **後端 API** (main.py) - 使用 `module_code`
3. **頁面 useFunctionName** - 使用 `func_code`
4. **頁面日誌記錄** - 使用 `func_code`
5. **Service API 路徑** - 使用 `module_code`

## 完整驗證清單

### 已驗證並修正的功能

| ID | func_code | module_code | 前端路由 | 後端API | 頁面檔案 | 狀態 |
|----|-----------|-------------|---------|---------|---------|------|
| 20 | system_codes | system_codes | /system_codes | /api/system_codes | SystemCodesPage.tsx | ✅ |
| 17 | user_logs | user_logs | /user_logs | /api/user_logs | UserLogsPage.tsx | ✅ |
| 16 | role_rights | role_rights | /role_rights | /api/role_rights | RoleRightsPage.tsx | ✅ |
| 12 | organizations | organizations | /organizations | /api/organizations | OrganizationsPage.tsx | ✅ |
| 14 | users | users | /users | /api/users | UsersPage.tsx | ✅ |
| 13 | user_roles | user_roles | /user_roles | /api/user_roles | UserRolesPage.tsx | ✅ |
| 11 | sys_profile | sys_profiles | /sys_profile | /api/sys_profiles | SysProfilePage.tsx | ✅ |
| 15 | system_functions | system_functions | /system_functions | /api/system_functions | SystemFunctionsPage.tsx | ✅ |

### 系統基礎功能 (無需驗證頁面)

| ID | func_code | module_code | 說明 | 狀態 |
|----|-----------|-------------|------|------|
| 1 | login | login | 登入頁面 | ✅ |
| 2 | logout | logout | 登出功能 | ✅ |
| 3 | change_password | change_password | 密碼變更 | ✅ |
| 4 | user_profile | user_profile | 個人資料 | ✅ |
| 5 | dashboard | home | 儀表板 | ✅ |

### 多租戶功能

| ID | func_code | module_code | 說明 | 狀態 |
|----|-----------|-------------|------|------|
| 25 | tenant_profile | organizations | 組織資料管理 | ⚠️ 待實作 |
| 26 | tenant_users | users | 組織成員管理 | ⚠️ 待實作 |

### 其他標準功能

| ID | func_code | module_code | 說明 | 狀態 |
|----|-----------|-------------|------|------|
| 21 | numbering_rules | numbering_rules | 編號規則設定 | ⚠️ 待實作 |
| 22 | file_attachments | file_attachments | 檔案附件管理 | ⚠️ 待實作 |
| 18 | system_notifications | system_notifications | 系統通知管理 | ⚠️ 待實作 |

## 修正總結

### 前端修正
1. **App.tsx 路由**
   - user_role → user_roles
   - user_detail → users
   - userlogs → user_logs

2. **頁面 useFunctionName**
   - SysFunctionsPage: sysfunction → system_functions
   - UserRolesPage: user_role → user_roles

3. **日誌記錄 func_code**
   - SysFunctionsPage: 'sysfunction' → 'system_functions'
   - UserRolesPage: 'user_role' → 'user_roles'
   - UsersPage: 'user_detail' → 'users'
   - RoleRightsPage: 'role_right' → 'role_rights'

4. **Service API 路徑**
   - sysFunctionService: /api/sysfunction/ → /api/system_functions/
   - sysProfileService: /sys_profile/ → /sys_profiles/
   - userLogService: /api/userlogs/ → /api/user_logs/
   - userLogsService: /api/userlogs/ → /api/user_logs/
   - userRoleService: /api/user_role/ → /api/user_roles/
   - userRolesService: /api/user_role/ → /api/user_roles/

### 後端修正
1. **main.py API 路由**
   - sys_profile: /api/sys_profile → /api/sys_profiles

## 驗證結論

✅ **所有已實作的功能均已符合 system_functions 資料表標準**

- 前端路由使用 `func_code`
- 後端 API 使用 `module_code`
- 頁面和日誌都使用 `func_code`
- Service API 路徑使用 `module_code`

## 注意事項

1. **舊版本兼容**: `sysfunction` 路由保留用於向後兼容，但內部已改用 `system_functions`
2. **待實作功能**: 部分功能（tenant_profile, tenant_users, numbering_rules 等）在資料表中有記錄但尚未實作
3. **命名原則**: 嚴格遵循資料表記錄，不進行任何推測或容錯處理

---
報告產生時間: 2026-01-21
