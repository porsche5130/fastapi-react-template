# 後端 API 支援性分析報告

**分析日期**: 2026-01-26
**目的**: 驗證共用後端 API 是否完整支援所有使用它的前端功能

---

## 執行摘要

本報告針對共用後端 API 架構進行完整檢查，驗證：
1. **organizations API** 是否支援 tenant_profile 功能
2. **users API** 是否支援 my_profile、change_password、tenant_users 功能

### 檢查結果概覽

| 前端功能 | 共用後端 API | 支援狀態 | 缺失項目 |
|---------|------------|---------|---------|
| tenant_profile | /api/organizations | ⚠️ 部分支援 | Transaction Token 整合 |
| my_profile | /api/users | ✅ 完整支援 | 無 |
| change_password | /api/users | ✅ 完整支援 | 無 |
| tenant_users | /api/users | ❌ 部分缺失 | reset-password 端點 |

---

## 詳細分析

### 1. organizations API → tenant_profile

#### 前端需求 (tenant_profile)

**檔案**: `Develop/frontend/src/services/tenantProfileService.ts`

**使用的端點**:
- `GET /api/organizations` - 取得當前使用者所屬組織資料
- `PUT /api/organizations/{id}` - 更新組織資料

**功能描述**:
- 使用者檢視自己所屬組織的資料
- 使用者更新自己所屬組織的資料（需要 update 權限）

#### 後端支援 (organizations API)

**檔案**: `Develop/backend/app/routes/organization.py`

**提供的端點**:

1. ✅ **GET /organizations/** (lines 46-91)
   ```python
   @router.get("/", response_model=List[OrganizationResponse])
   async def get_organizations(
       skip: int = 0,
       limit: int = 100,
       is_active: Optional[bool] = None,
       search: Optional[str] = None,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("organizations", "read"))
   ):
   ```

   **功能**:
   - ✅ 資料層級安全控制：一般使用者只能查看自己的組織 (lines 75-78)
   - ✅ 需要 Transaction Token (`organizations` read 權限)
   - ✅ 支援篩選條件（is_active, search）

2. ✅ **GET /organizations/{organization_id}** (lines 94-129)
   ```python
   @router.get("/{organization_id}", response_model=OrganizationResponse)
   async def get_organization(
       organization_id: int,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("organizations", "read"))
   ):
   ```

   **功能**:
   - ✅ 資料層級安全控制：檢查使用者是否有權限查看此組織 (lines 122-127)
   - ✅ 需要 Transaction Token (`organizations` read 權限)

3. ⚠️ **PUT /organizations/{organization_id}** (lines 169-219)
   ```python
   @router.put("/{organization_id}", response_model=OrganizationResponse)
   async def update_organization(
       organization_id: int,
       organization_data: OrganizationUpdate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("organizations", "update"))
   ):
   ```

   **功能**:
   - ✅ 更新組織資料
   - ✅ 檢查組織代碼唯一性
   - ✅ 需要 Transaction Token (`organizations` update 權限)
   - ⚠️ **問題**: 前端 tenant_profile 期望使用 `tenant_profile` 功能代碼的 Token，但後端檢查的是 `organizations` 功能代碼

#### 支援性評估

| 需求 | 後端支援 | 問題 |
|-----|---------|------|
| 讀取自己組織資料 | ✅ 完整支援 | 無 |
| 更新自己組織資料 | ⚠️ 部分支援 | Transaction Token 功能代碼不一致 |
| 資料層級安全控制 | ✅ 完整支援 | 無 |

**問題說明**:
- 前端 tenant_profile 功能使用 `tenant_profile` 功能代碼來檢查權限和取得 Transaction Token
- 後端 organizations API 要求的是 `organizations` 功能代碼的 Token
- 這會導致權限不匹配，前端無法成功調用後端 API

**建議解決方案**:

**方案 A**: 前端改為使用 `organizations` 功能代碼（推薦）
- 修改 TenantProfilePage.tsx 中的權限檢查從 `tenant_profile` 改為 `organizations`
- 優點：不需要修改後端，簡單快速
- 缺點：tenant_profile 功能無法獨立管理權限

**方案 B**: 後端新增專用的 tenant_profile 端點
- 新增 `/api/tenant_profile` 端點專門處理組織資料維護
- 使用 `tenant_profile` 功能代碼進行權限檢查
- 優點：權限管理更清晰，功能獨立
- 缺點：需要額外的開發工作

**方案 C**: 後端支援多個功能代碼（最彈性）
- 修改 organizations API 接受 `organizations` 或 `tenant_profile` 功能代碼
- 根據不同功能代碼實施不同的資料層級控制
- 優點：支援兩種使用場景
- 缺點：實作較複雜

---

### 2. users API → my_profile

#### 前端需求 (my_profile)

**檔案**: `Develop/frontend/src/services/userService.ts`

**使用的端點**:
- `GET /api/users/me` - 取得當前使用者個人資料
- `PUT /api/users/me` - 更新當前使用者個人資料

#### 後端支援 (users API)

**檔案**: `Develop/backend/app/routes/user.py`

**提供的端點**:

1. ✅ **GET /users/me** (lines 109-121)
   ```python
   @router.get("/me", response_model=UserDetailResponse)
   async def get_my_profile(
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user)
   ):
   ```

   **功能**:
   - ✅ 返回當前登入使用者的個人資料
   - ✅ 無需特殊權限（只需 Bearer Token）
   - ✅ 符合前端需求

2. ✅ **PUT /users/me** (lines 124-219)
   ```python
   @router.put("/me", response_model=UserDetailResponse)
   async def update_my_profile(
       profile_data: UserDetailUpdate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _: None = Depends(require_txn_token("my_profile", "update"))
   ):
   ```

   **功能**:
   - ✅ 更新當前使用者的個人資料
   - ✅ 需要 Transaction Token (`my_profile` update 權限) ✅ 功能代碼一致
   - ✅ 安全控制：
     - 無法變更 organization_id (lines 172-176)
     - 無法變更 user_role (lines 178-183)
     - 無法變更 is_active (lines 185-190)
   - ✅ 允許更新欄位：account, username, department, job_title, phone (line 194)
   - ✅ 記錄更新日誌 (lines 210-217)
   - ✅ 檢查帳號唯一性 (lines 163-169)

#### 支援性評估

| 需求 | 後端支援 | 問題 |
|-----|---------|------|
| 讀取個人資料 | ✅ 完整支援 | 無 |
| 更新個人資料 | ✅ 完整支援 | 無 |
| Transaction Token 整合 | ✅ 完整支援 | 無 |
| 安全控制 | ✅ 完整支援 | 無 |
| 日誌記錄 | ✅ 完整支援 | 無 |

**結論**: ✅ 完全支援，無需修改

---

### 3. users API → change_password

#### 前端需求 (change_password)

**檔案**: `Develop/frontend/src/services/userService.ts`

**使用的端點**:
- `POST /api/users/{user_id}/change-password` - 變更當前使用者密碼

**功能描述**:
- 使用者變更自己的密碼
- 需要驗證舊密碼
- 需要 Transaction Token

#### 後端支援 (users API)

**檔案**: `Develop/backend/app/routes/user.py`

**提供的端點**:

1. ✅ **POST /users/{user_id}/change-password** (lines 434-501)
   ```python
   @router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
   async def change_password(
       user_id: int,
       password_data: PasswordChange,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _: None = Depends(require_txn_token("change_password", "update"))
   ):
   ```

   **功能**:
   - ✅ 變更當前使用者密碼
   - ✅ 需要 Transaction Token (`change_password` update 權限) ✅ 功能代碼一致
   - ✅ 安全性:只能修改自己的密碼 (lines 460-464)
   - ✅ 驗證舊密碼 (lines 467-479)
   - ✅ 記錄失敗嘗試日誌 (lines 469-475)
   - ✅ 記錄成功變更日誌 (lines 488-497)
   - ✅ 使用 bcrypt 雜湊密碼 (line 482)

#### 支援性評估

| 需求 | 後端支援 | 問題 |
|-----|---------|------|
| 變更密碼 | ✅ 完整支援 | 無 |
| 驗證舊密碼 | ✅ 完整支援 | 無 |
| Transaction Token 整合 | ✅ 完整支援 | 無 |
| 安全控制 | ✅ 完整支援 | 無 |
| 日誌記錄 | ✅ 完整支援 | 無 |

**結論**: ✅ 完全支援，無需修改

---

### 4. users API → tenant_users

#### 前端需求 (tenant_users)

**檔案**: `Develop/frontend/src/services/tenantUsersService.ts`

**使用的端點**:
- `GET /api/users` (with organization_id filter) - 取得組織成員列表
- `GET /api/users/{id}` - 取得單一組織成員資料
- `POST /api/users` - 新增組織成員
- `PUT /api/users/{id}` - 更新組織成員資料
- `DELETE /api/users/{id}` - 刪除組織成員
- ❌ `POST /api/users/{id}/reset-password` - 重設使用者密碼（缺失）

#### 後端支援 (users API)

**檔案**: `Develop/backend/app/routes/user.py`

**提供的端點**:

1. ✅ **GET /users/** (lines 55-106)
   ```python
   @router.get("/", response_model=List[UserDetailResponse])
   async def get_users(
       skip: int = 0,
       limit: int = 100,
       is_active: Optional[bool] = None,
       organization_id: Optional[int] = None,  # ✅ 支援組織過濾
       search: Optional[str] = None,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("users", "read"))
   ):
   ```

   **功能**:
   - ✅ 支援 organization_id 參數過濾 (lines 95-96)
   - ✅ 資料層級安全控制：一般使用者只能查看自己組織的使用者 (lines 87-90)
   - ✅ 需要 Transaction Token (`users` read 權限)

2. ✅ **GET /users/{user_id}** (lines 222-257)
   ```python
   @router.get("/{user_id}", response_model=UserDetailResponse)
   async def get_user(
       user_id: int,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("users", "read"))
   ):
   ```

   **功能**:
   - ✅ 取得單一使用者資料
   - ✅ 資料層級安全控制 (lines 250-255)
   - ✅ 需要 Transaction Token (`users` read 權限)

3. ✅ **POST /users/** (lines 260-312)
   ```python
   @router.post("/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
   async def create_user(
       user_data: UserDetailCreate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("users", "create"))
   ):
   ```

   **功能**:
   - ✅ 新增使用者
   - ✅ 檢查帳號唯一性 (lines 277-282)
   - ✅ 檢查組織存在性 (lines 285-293)
   - ✅ 密碼加密 (lines 296-298)
   - ✅ 需要 Transaction Token (`users` create 權限)

4. ✅ **PUT /users/{user_id}** (lines 315-398)
   ```python
   @router.put("/{user_id}", response_model=UserDetailResponse)
   async def update_user(
       user_id: int,
       user_data: UserDetailUpdate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("users", "update"))
   ):
   ```

   **功能**:
   - ✅ 更新使用者資料
   - ✅ 支援 is_active 欄位更新（可切換啟用狀態）
   - ✅ 檢查帳號唯一性（如果修改 account）
   - ✅ 檢查組織存在性（如果修改 organization_id）
   - ✅ 支援密碼更新（可選）
   - ✅ 需要 Transaction Token (`users` update 權限)

5. ✅ **DELETE /users/{user_id}** (lines 401-432)
   ```python
   @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
   async def delete_user(
       user_id: int,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user),
       _token: None = Depends(require_txn_token("users", "delete", one_time_use=True))
   ):
   ```

   **功能**:
   - ✅ 刪除使用者
   - ✅ 一次性 Token（使用後立即失效）
   - ✅ 防止刪除自己 (lines 407-411)
   - ✅ 需要 Transaction Token (`users` delete 權限)

6. ❌ **POST /users/{user_id}/reset-password** - **缺失**

   **前端期望**:
   ```typescript
   // tenantUsersService.ts line 55-57
   export const resetUserPassword = async (userId: number): Promise<void> => {
     await axios.post(`${API_BASE}/${userId}/reset-password`);
   };
   ```

   **問題**: 後端沒有此端點

#### 支援性評估

| 需求 | 後端支援 | 問題 |
|-----|---------|------|
| 取得組織成員列表 | ✅ 完整支援 | 無 |
| 取得單一成員資料 | ✅ 完整支援 | 無 |
| 新增組織成員 | ✅ 完整支援 | 無 |
| 更新組織成員資料 | ✅ 完整支援 | 無 |
| 切換啟用狀態 | ✅ 完整支援 | 無 |
| 刪除組織成員 | ✅ 完整支援 | 無 |
| 重設使用者密碼 | ❌ 不支援 | 後端缺少 reset-password 端點 |

**問題說明**:
- 前端 tenant_users 功能提供「重設密碼」功能，會發送郵件通知使用者新密碼
- 後端沒有對應的 `/users/{user_id}/reset-password` 端點

**建議解決方案**:

**方案 A**: 新增 reset-password 端點（推薦）
```python
@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("tenant_users", "update"))
):
    """
    重設使用者密碼並發送郵件通知

    管理員功能：為組織成員重設密碼
    """
    # 檢查權限、產生新密碼、更新資料庫、發送郵件
    pass
```

**方案 B**: 前端移除重設密碼功能
- 簡單但功能減少
- 不推薦

---

## 功能代碼對應表

### 正確的功能代碼對應

| 前端功能 | 前端使用功能代碼 | 後端要求功能代碼 | 是否一致 |
|---------|----------------|----------------|---------|
| tenant_profile (read) | `tenant_profile` | `organizations` | ❌ 不一致 |
| tenant_profile (update) | `tenant_profile` | `organizations` | ❌ 不一致 |
| my_profile (read) | 無 (僅 Bearer Token) | 無 (僅 Bearer Token) | ✅ 一致 |
| my_profile (update) | `my_profile` | `my_profile` | ✅ 一致 |
| change_password | `change_password` | `change_password` | ✅ 一致 |
| tenant_users (read) | `tenant_users` | `users` | ❌ 不一致 |
| tenant_users (create) | `tenant_users` | `users` | ❌ 不一致 |
| tenant_users (update) | `tenant_users` | `users` | ❌ 不一致 |
| tenant_users (delete) | `tenant_users` | `users` | ❌ 不一致 |

---

## 問題總結

### 高優先級問題

1. **tenant_users 缺少 reset-password 端點** ❌
   - **影響**: 前端無法執行重設密碼功能
   - **解決方案**: 新增後端端點
   - **工作量**: 中等（需要密碼生成、郵件發送邏輯）

2. **功能代碼不一致** ⚠️
   - **tenant_profile**: 前端用 `tenant_profile`，後端要 `organizations`
   - **tenant_users**: 前端用 `tenant_users`，後端要 `users`
   - **影響**: Transaction Token 驗證失敗，前端無法調用 API
   - **解決方案**: 統一功能代碼或後端支援多個功能代碼
   - **工作量**: 低（修改前端）或中（修改後端）

### 中優先級問題

3. **tenant_profile 權限獨立性** ℹ️
   - **現況**: tenant_profile 與 organizations 共用權限
   - **影響**: 無法為 tenant_profile 單獨設定權限
   - **建議**: 考慮是否需要獨立的權限管理

---

## 建議修正方案

### 方案 1: 最小修改（推薦快速上線）

**步驟**:
1. ✅ 前端修改 TenantProfilePage.tsx 權限檢查從 `tenant_profile` 改為 `organizations`
2. ✅ 前端修改 TenantUsersPage.tsx 權限檢查從 `tenant_users` 改為 `users`
3. ❌ 後端新增 `/users/{user_id}/reset-password` 端點
4. ✅ 前端移除或註解 resetUserPassword 功能（臨時方案）

**優點**:
- 快速上線
- 修改範圍小
- 風險低

**缺點**:
- 缺少重設密碼功能
- 權限管理不夠細緻

### 方案 2: 完整支援（推薦長期）

**步驟**:
1. ❌ 後端新增 `/users/{user_id}/reset-password` 端點
2. ❌ 後端 organizations API 支援 `tenant_profile` 功能代碼
3. ❌ 後端 users API 支援 `tenant_users` 功能代碼
4. ✅ 在 system_functions 表中註冊 `tenant_profile` 和 `tenant_users`
5. ✅ 為所有角色設定對應權限

**優點**:
- 功能完整
- 權限管理清晰
- 易於擴展

**缺點**:
- 開發工作量較大
- 需要測試較多

---

## 檢查清單

### tenant_profile
- [ ] 決定採用哪個方案
- [ ] 修改前端或後端功能代碼
- [ ] 在 system_functions 註冊 tenant_profile（如採用方案2）
- [ ] 設定角色權限
- [ ] 測試權限控制
- [ ] 測試 CRUD 功能

### my_profile
- [x] 後端完整支援
- [x] Transaction Token 整合
- [x] 安全控制
- [x] 日誌記錄
- [ ] 前端測試

### change_password
- [x] 後端完整支援
- [x] Transaction Token 整合
- [x] 安全控制
- [x] 日誌記錄
- [ ] 前端測試

### tenant_users
- [x] 後端基本 CRUD 完整支援
- [ ] 新增 reset-password 端點
- [ ] 決定採用哪個方案處理功能代碼
- [ ] 修改前端或後端功能代碼
- [ ] 在 system_functions 註冊 tenant_users（如採用方案2）
- [ ] 設定角色權限
- [ ] 測試重設密碼功能
- [ ] 測試其他 CRUD 功能

---

## 附錄：後端端點清單

### organizations API (`/api/organizations`)

| 方法 | 端點 | 功能代碼 | 權限 | 說明 |
|-----|------|---------|------|------|
| GET | / | organizations | read | 取得組織列表（含資料層級控制） |
| GET | /{id} | organizations | read | 取得單一組織資料 |
| POST | / | organizations | create | 建立組織 |
| PUT | /{id} | organizations | update | 更新組織 |
| DELETE | /{id} | organizations | delete | 刪除組織（一次性Token） |

### users API (`/api/users`)

| 方法 | 端點 | 功能代碼 | 權限 | 說明 |
|-----|------|---------|------|------|
| GET | / | users | read | 取得使用者列表（含資料層級控制） |
| GET | /me | - | - | 取得個人資料（僅需Bearer Token） |
| PUT | /me | my_profile | update | 更新個人資料 |
| GET | /{id} | users | read | 取得單一使用者資料 |
| POST | / | users | create | 建立使用者 |
| PUT | /{id} | users | update | 更新使用者 |
| DELETE | /{id} | users | delete | 刪除使用者（一次性Token） |
| POST | /{id}/change-password | change_password | update | 變更密碼 |
| POST | /{id}/reset-password | ❌ 缺失 | ❌ 缺失 | ❌ 需要新增 |

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
**相關文件**:
- `DevTools/checklist_report_20260126_144355.md`
- `Develop/I18N_TRANSLATIONS_COMPLETE.md`
- `Develop/SCHEMA_RENAMING_COMPLETE.md`
