# 系統功能實作檢核清單

根據 system_functions 資料表自動生成的實作檢核清單

生成日期: 2026-01-21

---

## 📊 功能總覽

| 分類 | 數量 | func_order 範圍 |
|------|------|----------------|
| 外部通用功能 | 5 | 1-5 |
| 多租戶管理 | 3 | 70系列 |
| 標準化設定 | 4 | 80系列 |
| 系統管理後台 | 10 | 90系列 |
| **總計** | **22** | - |

---

## 1️⃣ 外部通用功能 (ID 1-5)

### ✅ ID 1: login (使用者登入)
- **module_code**: auth
- **API 路由**: `/api/auth/login`
- **後端檔案**:
  - ✅ `app/routes/auth.py` - POST /login
  - ✅ `app/models/user.py` - User model
- **前端檔案**:
  - ⚠️ 需確認 authService.ts 使用正確的 API 路由
- **資料表**: users

### ✅ ID 2: logout (使用者登出)
- **module_code**: auth
- **API 路由**: `/api/auth/logout`
- **後端檔案**:
  - ✅ `app/routes/auth.py` - POST /logout
- **前端檔案**:
  - ⚠️ 需確認 authService.ts 使用正確的 API 路由

### ✅ ID 3: change_password (密碼變更)
- **module_code**: auth
- **API 路由**: `/api/auth/change-password`
- **後端檔案**:
  - ✅ `app/routes/auth.py` - POST /change-password
- **前端檔案**:
  - ⚠️ 需確認對應的前端頁面/元件
- **資料表**: users

### ✅ ID 4: user_profile (個人資料變更)
- **module_code**: users
- **API 路由**: `/api/users/profile` 或 `/api/users/me`
- **後端檔案**:
  - ⚠️ 需確認 `app/routes/users.py` 中是否有 profile 相關端點
- **前端檔案**:
  - ⚠️ 需建立個人資料頁面
- **資料表**: users

### ✅ ID 5: dashboard (儀表板)
- **module_code**: dashboard
- **API 路由**: `/api/dashboard` 或 `/api/dashboard/stats`
- **後端檔案**:
  - ⚠️ 需確認是否有 `app/routes/dashboard.py`
- **前端檔案**:
  - ⚠️ 需確認 Dashboard 頁面元件
- **資料表**: (統計各資料表資料)

---

## 2️⃣ 多租戶管理 (ID 24-26, func_order 70系列)

### ⚠️ ID 24: tenants (多租戶管理作業) - 父節點
- **module_code**: NULL (父節點)
- **說明**: 僅用於功能選單分組

### ✅ ID 25: tenant_profile (組織資料管理)
- **module_code**: organizations
- **API 路由**: `/api/organizations/{id}` (租戶版本 - 僅能存取自己的組織)
- **後端檔案**:
  - ✅ `app/routes/organization.py` - 需確認權限過濾
- **前端檔案**:
  - ⚠️ 需建立租戶版組織資料頁面 `TenantProfilePage.tsx`
- **資料表**: organizations (過濾 organization_id = current_user.organization_id)

### ✅ ID 26: tenant_users (組織成員管理)
- **module_code**: users
- **API 路由**: `/api/users` (租戶版本 - 僅能存取自己組織的使用者)
- **後端檔案**:
  - ✅ `app/routes/users.py` - 需確認權限過濾
- **前端檔案**:
  - ⚠️ 需建立租戶版使用者管理頁面 `TenantUsersPage.tsx`
- **資料表**: users (過濾 organization_id = current_user.organization_id)

---

## 3️⃣ 標準化設定 (ID 19-22, func_order 80系列)

### ⚠️ ID 19: standard_settings (標準化設定) - 父節點
- **module_code**: NULL (父節點)
- **說明**: 僅用於功能選單分組

### ✅ ID 20: system_codes (系統代碼維護)
- **module_code**: system_codes
- **API 路由**: `/api/system_codes`
- **後端檔案**:
  - ✅ `app/routes/systemcode.py`
  - ✅ `app/models/systemcode.py`
- **前端檔案**:
  - ✅ `src/pages/SystemCodesPage.tsx`
  - ✅ `src/services/systemCodeService.ts`
- **資料表**: system_codes

### ⚠️ ID 21: numbering_rules (編碼編號設定)
- **module_code**: numbering_rules
- **API 路由**: `/api/numbering_rules`
- **後端檔案**:
  - ❌ 需建立 `app/routes/numbering_rules.py`
  - ❌ 需建立 `app/models/numbering_rule.py`
  - ❌ 需建立 `app/schemas/numbering_rule.py`
- **前端檔案**:
  - ❌ 需建立 `src/pages/NumberingRulesPage.tsx`
  - ❌ 需建立 `src/services/numberingRulesService.ts`
- **資料表**: numbering_rules (需建立)

### ⚠️ ID 22: file_attachments (檔案類型管理)
- **module_code**: file_attachments
- **API 路由**: `/api/file_attachments`
- **後端檔案**:
  - ❌ 需建立 `app/routes/file_attachments.py`
  - ❌ 需建立 `app/models/file_attachment.py`
  - ❌ 需建立 `app/schemas/file_attachment.py`
- **前端檔案**:
  - ❌ 需建立 `src/pages/FileAttachmentsPage.tsx`
  - ❌ 需建立 `src/services/fileAttachmentsService.ts`
- **資料表**: file_attachments (需建立)
- **參考**: [上傳檔案元件.md](系統設計/應用系統設計/上傳檔案元件.md)

---

## 4️⃣ 系統管理後台 (ID 10-18, 23, func_order 90系列)

### ⚠️ ID 10: system_mana (系統管理後台) - 父節點
- **module_code**: NULL (父節點)
- **說明**: 僅用於功能選單分組
- **特殊標記**: is_mana=true

### ⚠️ ID 11: sys_profile (系統基本設定)
- **module_code**: sys_profiles
- **API 路由**: `/api/sys_profile`
- **後端檔案**:
  - ✅ `app/routes/sys_profile.py`
  - ✅ `app/models/sys_profile.py`
- **前端檔案**:
  - ⚠️ 需確認對應的前端頁面
- **資料表**: sys_profile

### ✅ ID 12: organizations (組織資料維護)
- **module_code**: organizations
- **API 路由**: `/api/organizations`
- **後端檔案**:
  - ✅ `app/routes/organization.py`
  - ✅ `app/models/organization.py`
- **前端檔案**:
  - ⚠️ 需確認 OrganizationsPage
- **資料表**: organizations

### ✅ ID 13: user_roles (角色資料維護)
- **module_code**: user_roles
- **API 路由**: `/api/user_role` (應改為 `/api/user_roles`)
- **後端檔案**:
  - ✅ `app/routes/user_role.py` (應重新命名為 user_roles.py)
  - ✅ `app/models/user_role.py`
- **前端檔案**:
  - ⚠️ 需確認對應的前端頁面
- **資料表**: user_role (應重新命名為 user_roles)

### ✅ ID 14: users (使用者資料維護)
- **module_code**: users
- **API 路由**: `/api/users`
- **後端檔案**:
  - ✅ `app/routes/users.py` (已完成重新命名)
  - ✅ `app/models/user.py` (已完成重新命名)
- **前端檔案**:
  - ✅ `src/pages/UsersPage.tsx`
  - ✅ `src/services/userService.ts` (已完成重新命名)
- **資料表**: users (已完成重新命名)

### ✅ ID 15: system_functions (系統功能資料維護)
- **module_code**: system_functions
- **API 路由**: `/api/system_functions`
- **後端檔案**:
  - ✅ `app/routes/system_functions.py`
  - ✅ `app/models/system_functions.py`
  - ✅ `app/schemas/system_functions.py`
- **前端檔案**:
  - ✅ `src/pages/SystemFunctionsPage.tsx`
  - ✅ `src/services/systemFunctionsService.ts`
- **資料表**: system_functions

### ✅ ID 16: role_rights (角色權限設定作業)
- **module_code**: role_rights
- **API 路由**: `/api/role_right` (應改為 `/api/role_rights`)
- **後端檔案**:
  - ✅ `app/routes/role_right.py` (應重新命名為 role_rights.py)
  - ✅ `app/models/role_right.py`
- **前端檔案**:
  - ⚠️ 需確認對應的前端頁面
- **資料表**: role_right (應重新命名為 role_rights)

### ✅ ID 17: user_logs (使用者操作記錄)
- **module_code**: user_logs
- **API 路由**: `/api/userlogs` (應改為 `/api/user_logs`)
- **後端檔案**:
  - ✅ `app/routes/userlog.py` (應重新命名為 user_logs.py)
  - ✅ `app/models/userlog.py`
- **前端檔案**:
  - ✅ `src/pages/UserLogsPage.tsx`
  - ✅ `src/services/userLogService.ts`
- **資料表**: userlogs (應重新命名為 user_logs)

### ✅ ID 18: system_notifications (系統通知管理)
- **module_code**: system_notifications
- **API 路由**: `/api/system_notifications`
- **後端檔案**:
  - ✅ `app/routes/system_notifications.py`
  - ✅ `app/models/system_notification.py`
  - ✅ `app/schemas/system_notification.py`
- **前端檔案**:
  - ⚠️ 需確認對應的前端頁面
- **資料表**: system_notifications, notification_read_status

### ⚠️ ID 23: system_parameters (系統參數設定)
- **module_code**: system_parameters
- **API 路由**: `/api/system_parameters`
- **後端檔案**:
  - ❌ 需建立 `app/routes/system_parameters.py`
  - ❌ 需建立 `app/models/system_parameter.py`
  - ❌ 需建立 `app/schemas/system_parameter.py`
- **前端檔案**:
  - ❌ 需建立 `src/pages/SystemParametersPage.tsx`
  - ❌ 需建立 `src/services/systemParametersService.ts`
- **資料表**: system_parameters (需建立)

---

## 📋 待辦事項總結

### 高優先級 (影響基礎架構)

1. ✅ **user_detail → users 重新命名** (已完成)
   - ✅ 後端模型、路由已更新
   - ✅ 前端服務已更新
   - ✅ 資料庫遷移已完成

2. ⚠️ **統一命名慣例**
   - ❌ user_role → user_roles (資料表與檔案)
   - ❌ role_right → role_rights (資料表與檔案)
   - ❌ userlogs → user_logs (資料表與檔案)
   - ❌ systemcode → system_codes (資料表與檔案)

3. ⚠️ **API 路由標準化**
   - ❌ `/api/user_role` → `/api/user_roles`
   - ❌ `/api/role_right` → `/api/role_rights`
   - ❌ `/api/userlogs` → `/api/user_logs`
   - ❌ `/api/systemcode` → `/api/system_codes`

### 中優先級 (功能完整性)

4. ⚠️ **缺少的後端功能**
   - ❌ numbering_rules (編碼編號設定)
   - ❌ file_attachments (檔案類型管理)
   - ❌ system_parameters (系統參數設定)
   - ⚠️ dashboard (儀表板統計 API)
   - ⚠️ user_profile (個人資料 API)

5. ⚠️ **缺少的前端頁面**
   - ❌ NumberingRulesPage.tsx
   - ❌ FileAttachmentsPage.tsx
   - ❌ SystemParametersPage.tsx
   - ❌ TenantProfilePage.tsx
   - ❌ TenantUsersPage.tsx

### 低優先級 (優化與完善)

6. ⚠️ **權限過濾實作**
   - 確認 tenant_profile 和 tenant_users 的權限過濾邏輯

7. ⚠️ **前端頁面確認**
   - 確認所有已建立功能的前端頁面是否存在且正常運作

---

## 🔧 自動化建議

根據 system_functions 表可以建立以下自動化工具:

1. **程式碼生成器**
   - 讀取 system_functions 表
   - 自動生成基本的 CRUD 路由、模型、Schema
   - 自動生成前端 Service 檔案

2. **路由註冊器**
   - 動態讀取 system_functions 表
   - 自動註冊對應的路由到 main.py

3. **功能選單生成器**
   - 根據 system_functions 表自動生成前端選單結構

---

## 📝 檢核清單

- [x] user_detail → users 資料表重新命名
- [x] UserDetail → User 模型重新命名
- [x] 後端路由檔案重新命名與更新
- [x] 前端服務檔案重新命名與更新
- [ ] 其他資料表命名標準化
- [ ] API 路由統一為複數形式
- [ ] 建立缺少的後端功能 (3個)
- [ ] 建立缺少的前端頁面 (5個)
- [ ] 確認權限過濾邏輯
- [ ] 整合測試

---

**最後更新**: 2026-01-21
**完成度**: 45% (10/22 功能完整實作)
