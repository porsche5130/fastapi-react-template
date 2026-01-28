# 後端 API 多租戶架構正確分析

**分析日期**: 2026-01-26
**更新**: 根據正確的架構設計重新分析

---

## 架構設計原則

### 多租戶與個人化功能的 API 共用模式

本系統採用**功能代碼分離，後端 API 共用**的設計模式：

1. **前端功能代碼** - 用於權限檢查和 Transaction Token 驗證
2. **後端 API** - 實際的資料存取端點
3. **設計原則** - 一個後端 API 可以支援多個前端功能

---

## 正確的功能代碼與後端 API 對應

### 結構說明

| 前端功能 | 功能代碼 | 共用後端 API | 作業目的 |
|---------|---------|------------|---------|
| **tenant_profile** | `tenant_profile` | `/api/organizations` | 維護**所屬組織**的資料 (CRUD) |
| **organizations** | `organizations` | `/api/organizations` | 管理**所有組織**的資料 (CRUD) - 管理員功能 |
| **tenant_users** | `tenant_users` | `/api/users` | 維護**所屬組織成員**的資料 (CRUD) + 重置密碼 |
| **users** | `users` | `/api/users` | 管理**所有使用者**的資料 (CRUD) - 管理員功能 |
| **my_profile** | `my_profile` | `/api/users/me` | 維護**個人資料** (Read + Update) |
| **change_password** | `change_password` | `/api/users/{id}/change-password` | 變更**自己的密碼** |
| **reset_password** | `reset_password` | `/api/users/{id}/reset-password` | 重置**組織成員密碼**（組織管理者功能） |

### 關鍵設計概念

#### 1. organizations API 的雙重角色

**後端**: `/api/organizations`

**支援的前端功能**:

##### A. tenant_profile (一般使用者)
- **功能代碼**: `tenant_profile`
- **權限範圍**: 只能存取**自己所屬組織**的資料
- **資料過濾**:
  ```python
  # 後端資料層級控制 (organization.py lines 75-78)
  if not has_full_permission:
      query = query.filter(Organization.id == current_user.organization_id)
  ```
- **使用場景**: 組織成員查看和維護自己組織的基本資料

##### B. organizations (管理員)
- **功能代碼**: `organizations`
- **權限範圍**: 可以存取**所有組織**的資料
- **資料過濾**: 無限制（有完整權限）
- **使用場景**: 系統管理員管理所有組織

**設計優勢**:
- 一個 API 端點，兩種使用模式
- 透過**功能代碼**區分權限範圍
- 透過**資料層級控制**確保安全性

#### 2. users API 的四重角色

**後端**: `/api/users`

**支援的前端功能**:

##### A. tenant_users (組織管理者)
- **功能代碼**: `tenant_users`
- **權限範圍**: 只能存取**自己組織的成員**
- **資料過濾**:
  ```python
  # 後端資料層級控制 (user.py lines 87-90)
  if not has_full_permission:
      query = query.filter(User.organization_id == current_user.organization_id)
  ```
- **使用場景**: 組織管理者維護組織成員資料
- **額外功能**: 重置成員密碼 → `reset_password` 功能代碼

##### B. users (系統管理員)
- **功能代碼**: `users`
- **權限範圍**: 可以存取**所有使用者**的資料
- **資料過濾**: 無限制（有完整權限）
- **使用場景**: 系統管理員管理所有使用者

##### C. my_profile (個人)
- **功能代碼**: `my_profile`（僅 update 需要）
- **端點**: `/api/users/me`
- **權限範圍**: 只能存取**自己**的資料
- **使用場景**: 使用者維護個人資料

##### D. change_password (個人)
- **功能代碼**: `change_password`
- **端點**: `/api/users/{id}/change-password`
- **權限範圍**: 只能修改**自己**的密碼
- **使用場景**: 使用者變更自己的密碼

---

## 詳細檢查結果

### 1. organizations API 支援 tenant_profile ✅

#### 前端需求 (tenant_profile)

**檔案**: `Develop/frontend/src/pages/TenantProfilePage.tsx`

**功能代碼**: `tenant_profile`

**使用的 API**:
- `GET /api/organizations` - 取得所屬組織資料（自動過濾）
- `PUT /api/organizations/{id}` - 更新所屬組織資料

**權限檢查** (TenantProfilePage.tsx):
```typescript
const canRead = hasPermission('tenant_profile', 'read');
const canUpdate = hasPermission('tenant_profile', 'update');
```

#### 後端支援檢查

**檔案**: `Develop/backend/app/routes/organization.py`

##### ✅ GET /organizations/ (支援)
```python
@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    ...
    _token: None = Depends(require_txn_token("organizations", "read"))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `organizations` 功能代碼
- ✅ 資料層級控制正確（過濾為 current_user.organization_id）

**修正需求**:
- 後端需要支援 `tenant_profile` 功能代碼的 Token

##### ✅ PUT /organizations/{id} (支援)
```python
@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    ...
    _token: None = Depends(require_txn_token("organizations", "update"))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `organizations` 功能代碼
- ✅ 功能完整（更新、驗證、記錄）

**修正需求**:
- 後端需要支援 `tenant_profile` 功能代碼的 Token

#### 結論

| 項目 | 狀態 | 說明 |
|-----|------|------|
| GET 功能 | ✅ 支援 | 資料過濾正確 |
| PUT 功能 | ✅ 支援 | CRUD 完整 |
| Transaction Token | ❌ 需修正 | 需支援 `tenant_profile` 功能代碼 |
| 資料層級控制 | ✅ 正確 | 自動過濾為所屬組織 |

---

### 2. users API 支援 tenant_users ✅ (缺 reset_password)

#### 前端需求 (tenant_users)

**檔案**: `Develop/frontend/src/pages/TenantUsersPage.tsx`

**功能代碼**: `tenant_users`

**使用的 API**:
- `GET /api/users` (with organization_id) - 取得所屬組織成員列表
- `GET /api/users/{id}` - 取得成員資料
- `POST /api/users` - 新增成員
- `PUT /api/users/{id}` - 更新成員資料
- `DELETE /api/users/{id}` - 刪除成員
- ❌ `POST /api/users/{id}/reset-password` - 重置成員密碼（缺失）

#### 後端支援檢查

**檔案**: `Develop/backend/app/routes/user.py`

##### ✅ GET /users/ (支援)
```python
@router.get("/", response_model=List[UserDetailResponse])
async def get_users(
    organization_id: Optional[int] = None,  # ✅ 支援組織過濾
    ...
    _token: None = Depends(require_txn_token("users", "read"))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `users` 功能代碼
- ✅ 資料層級控制正確（過濾為 current_user.organization_id）
- ✅ 支援 organization_id 參數

**修正需求**:
- 後端需要支援 `tenant_users` 功能代碼的 Token

##### ✅ POST /users/ (支援)
```python
@router.post("/", response_model=UserDetailResponse)
async def create_user(
    ...
    _token: None = Depends(require_txn_token("users", "create"))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `users` 功能代碼
- ✅ 功能完整（驗證、密碼加密）

##### ✅ PUT /users/{id} (支援)
```python
@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    ...
    _token: None = Depends(require_txn_token("users", "update"))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `users` 功能代碼
- ✅ 功能完整（驗證、更新）

##### ✅ DELETE /users/{id} (支援)
```python
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    ...
    _token: None = Depends(require_txn_token("users", "delete", one_time_use=True))
):
```

**問題分析**:
- ❌ Transaction Token 要求 `users` 功能代碼
- ✅ 功能完整（一次性 Token、防刪自己）

##### ❌ POST /users/{id}/reset-password (缺失)

**前端需求** (tenantUsersService.ts line 55):
```typescript
export const resetUserPassword = async (userId: number): Promise<void> => {
  await axios.post(`${API_BASE}/${userId}/reset-password`);
};
```

**設計需求**:
- 功能代碼: `reset_password`
- 作用: 組織管理者重置組織成員密碼
- 重置規則: **密碼改為組織代碼** (`organizations.org_code`)
- 通知: 不需要發送郵件（使用者已知組織代碼）

**需要實作**: ❌ 完全缺失

#### 結論

| 項目 | 狀態 | 說明 |
|-----|------|------|
| GET 功能 | ✅ 支援 | 資料過濾正確 |
| POST 功能 | ✅ 支援 | 新增完整 |
| PUT 功能 | ✅ 支援 | 更新完整 |
| DELETE 功能 | ✅ 支援 | 刪除完整 |
| Transaction Token | ❌ 需修正 | 需支援 `tenant_users` 功能代碼 |
| reset_password | ❌ 缺失 | 需新增端點 |

---

### 3. users API 支援 my_profile ✅

#### 檢查結果

**端點**: `GET /users/me`, `PUT /users/me`

**功能代碼**: `my_profile` (僅 PUT 需要)

**後端實作**:
```python
# GET - 無需 Transaction Token (user.py lines 109-121)
@router.get("/me", response_model=UserDetailResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

# PUT - 需要 my_profile Token (user.py lines 124-219)
@router.put("/me", response_model=UserDetailResponse)
async def update_my_profile(
    profile_data: UserDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("my_profile", "update"))  # ✅ 正確
):
```

**結論**: ✅ 完全支援，功能代碼正確

---

### 4. users API 支援 change_password ✅

#### 檢查結果

**端點**: `POST /users/{id}/change-password`

**功能代碼**: `change_password`

**後端實作**:
```python
@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("change_password", "update"))  # ✅ 正確
):
```

**結論**: ✅ 完全支援，功能代碼正確

---

## Transaction Token 功能代碼修正需求

### 問題根源

後端目前**硬編碼**功能代碼在 `require_txn_token()` 中：
```python
# 範例：organization.py
_token: None = Depends(require_txn_token("organizations", "read"))
```

這導致：
- `tenant_profile` 無法使用（Token 被拒絕）
- `tenant_users` 無法使用（Token 被拒絕）

### 解決方案

#### 方案 A: 修改 require_txn_token 支援多功能代碼（推薦）

**修改檔案**: `Develop/backend/app/routes/transaction.py`

**新增功能**: 允許一個端點接受多個功能代碼

**實作概念**:
```python
def require_txn_token(
    func_codes: Union[str, List[str]],  # ← 改為支援多個
    permission_type: str,
    one_time_use: bool = False
):
    """
    驗證 Transaction Token

    Args:
        func_codes: 功能代碼（字串或字串列表）
        permission_type: 權限類型
        one_time_use: 是否一次性使用
    """
    if isinstance(func_codes, str):
        func_codes = [func_codes]

    async def dependency(request: Request, ...):
        # ... 驗證邏輯
        # 檢查 Token 的 func_code 是否在 func_codes 列表中
        if token_data["func_code"] not in func_codes:
            raise HTTPException(...)

    return dependency
```

**修改端點**:
```python
# organizations.py
@router.get("/")
async def get_organizations(
    ...
    _token: None = Depends(require_txn_token(
        ["organizations", "tenant_profile"],  # ← 支援兩個功能代碼
        "read"
    ))
):

# user.py
@router.get("/")
async def get_users(
    ...
    _token: None = Depends(require_txn_token(
        ["users", "tenant_users"],  # ← 支援兩個功能代碼
        "read"
    ))
):
```

**優點**:
- 一次修改，全面解決
- 保持向後相容
- 清晰表達端點支援的功能

**缺點**:
- 需要修改核心驗證邏輯

---

#### 方案 B: 新增專用端點（不推薦）

為 `tenant_profile` 和 `tenant_users` 新增專用的 API 端點。

**缺點**:
- 重複程式碼
- 維護困難
- 違反 DRY 原則

---

## reset_password 功能實作需求

### 功能規格

**功能代碼**: `reset_password`

**使用場景**: 組織管理者在 tenant_users 頁面重置組織成員密碼

**重置規則**:
- 密碼重置為**組織代碼** (`organizations.org_code`)
- 不發送郵件通知（因為密碼即為組織代碼，使用者已知）

**權限要求**:
- 功能代碼: `reset_password`
- 權限類型: `update`
- 資料範圍: 只能重置同組織成員的密碼

### 後端實作

**檔案**: `Develop/backend/app/routes/user.py`

**新增端點**:
```python
@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT, summary="重置使用者密碼")
async def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("reset_password", "update"))
):
    """
    重置組織成員密碼為組織代碼

    組織管理者功能：
    - 重置密碼為所屬組織的組織代碼
    - 僅能重置同組織成員的密碼
    - 不發送郵件通知

    步驟:
    1. 驗證 Transaction Token (reset_password 功能)
    2. 檢查目標使用者存在
    3. 檢查目標使用者與當前使用者在同一組織
    4. 取得組織代碼
    5. 將密碼重置為組織代碼
    6. 記錄操作日誌
    7. 返回 204 No Content

    - **user_id**: 要重置密碼的使用者 ID

    需要提供 Bearer Token 及 reset_password 更新權限的交易令牌
    """
    # 查詢目標使用者
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 安全性:只能重置同組織成員的密碼
    if target_user.organization_id != current_user.organization_id:
        # 記錄非法嘗試
        UserLogService.log_error(
            db=db,
            user_id=current_user.id,
            function_id=UserLogService.get_function_id_by_code(db, "reset_password"),
            module_item="Update",
            error_message=f"嘗試重置其他組織成員密碼: user_id={user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能重置同組織成員的密碼"
        )

    # 防止重置自己的密碼（應使用 change_password）
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法重置自己的密碼，請使用密碼變更功能"
        )

    # 取得組織代碼
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="找不到組織資料"
        )

    # 重置密碼為組織代碼
    new_password = organization.org_code
    target_user.password = get_password_hash(new_password)
    target_user.updated_at = func.now()
    target_user.edit_by = current_user.id

    # 持久化
    db.commit()

    # 記錄成功的密碼重置（不記錄實際密碼）
    UserLogService.log_update(
        db=db,
        user_id=current_user.id,
        function_id=UserLogService.get_function_id_by_code(db, "reset_password"),
        original_data={
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "action": "password_reset"
        },
        updated_data={
            "target_user_id": target_user.id,
            "target_username": target_user.username,
            "action": "password_reset_completed",
            "reset_by": current_user.id,
            "reset_by_username": current_user.username,
            "timestamp": datetime.now(TAIPEI_TZ).isoformat()
        },
        current_user=current_user
    )

    return None
```

### 前端整合

**檔案**: `Develop/frontend/src/services/tenantUsersService.ts`

**現有程式碼** (line 55-57):
```typescript
export const resetUserPassword = async (userId: number): Promise<void> => {
  await axios.post(`${API_BASE}/${userId}/reset-password`);
};
```

✅ **前端已準備好**，只需後端實作

### Schema 定義

**檔案**: `Develop/backend/app/schemas/user_detail.py`

**無需新增** Schema（reset-password 不需要 request body）

### system_functions 註冊

需要在 `system_functions` 表中註冊 `reset_password` 功能：

```sql
INSERT INTO system_functions (
    func_code,
    upper_func_id,
    func_cname,
    func_ename,
    func_type,
    func_order,
    func_icon,
    module_code,
    module_item,
    is_mana,
    is_active,
    edit_by
) VALUES (
    'reset_password',
    0,
    '重置密碼',
    'Reset Password',
    2,
    0,
    'LockReset',
    'reset_password',
    '["Update"]',
    false,
    true,
    1
);
```

---

## 實作優先順序

### 高優先級（必須完成）

1. ✅ **修改 require_txn_token 支援多功能代碼**
   - 影響: tenant_profile 和 tenant_users 無法使用
   - 檔案: `app/routes/transaction.py`
   - 工作量: 中

2. ✅ **實作 reset_password 端點**
   - 影響: tenant_users 重置密碼功能無法使用
   - 檔案: `app/routes/user.py`
   - 工作量: 中

3. ✅ **註冊 reset_password 功能代碼**
   - 影響: 權限檢查和 Token 生成
   - 工作: 執行 SQL
   - 工作量: 低

4. ✅ **更新端點的 require_txn_token 調用**
   - 檔案: `app/routes/organization.py`, `app/routes/user.py`
   - 工作量: 低

### 中優先級（建議完成）

5. ✅ **註冊 tenant_profile 和 tenant_users 功能代碼**
   - 目的: 完整的權限管理
   - 工作: 執行 SQL
   - 工作量: 低

6. ✅ **為所有角色設定對應權限**
   - 目的: 確保使用者可以使用功能
   - 工作: 執行 SQL
   - 工作量: 低

### 低優先級（可選）

7. ✅ **更新文件**
   - API 文件
   - 架構設計文件
   - 工作量: 低

---

## 總結

### 架構設計評估 ✅

您的多租戶 API 共用架構設計**非常優秀**：

1. ✅ **高效**: 一個 API 支援多個功能，減少重複程式碼
2. ✅ **安全**: 資料層級控制確保資料隔離
3. ✅ **彈性**: 透過功能代碼區分不同使用場景
4. ✅ **清晰**: 權限管理獨立於 API 實作

### 當前問題

| 問題 | 影響 | 解決方案 | 優先級 |
|-----|------|---------|-------|
| Transaction Token 不支援多功能代碼 | tenant_profile/tenant_users 無法使用 | 修改 require_txn_token | 🔴 高 |
| 缺少 reset_password 端點 | 無法重置成員密碼 | 新增端點 | 🔴 高 |
| 功能代碼未註冊 | 無法生成 Token | 執行 SQL 註冊 | 🟡 中 |

### 修正後的架構圖

```
前端功能                功能代碼              後端 API
┌────────────────┐     ┌──────────┐         ┌─────────────────┐
│ tenant_profile │────→│ tenant_  │────┐    │                 │
│ (組織資料維護)  │     │ profile  │    │    │  organizations  │
└────────────────┘     └──────────┘    ├───→│      API        │
┌────────────────┐     ┌──────────┐    │    │                 │
│ organizations  │────→│ organiza-│────┘    └─────────────────┘
│ (組織管理)      │     │ tions    │
└────────────────┘     └──────────┘

┌────────────────┐     ┌──────────┐         ┌─────────────────┐
│ tenant_users   │────→│ tenant_  │────┐    │                 │
│ (成員維護)      │     │ users    │    │    │                 │
└────────────────┘     └──────────┘    │    │                 │
┌────────────────┐     ┌──────────┐    │    │                 │
│ users          │────→│ users    │────┤    │     users       │
│ (使用者管理)    │     └──────────┘    │    │      API        │
└────────────────┘                      ├───→│                 │
┌────────────────┐     ┌──────────┐    │    │                 │
│ my_profile     │────→│ my_      │────┤    │                 │
│ (個人資料)      │     │ profile  │    │    │                 │
└────────────────┘     └──────────┘    │    └─────────────────┘
┌────────────────┐     ┌──────────┐    │
│ change_        │────→│ change_  │────┤
│ password       │     │ password │    │
└────────────────┘     └──────────┘    │
┌────────────────┐     ┌──────────┐    │
│ reset_password │────→│ reset_   │────┘
│ (重置密碼)      │     │ password │
└────────────────┘     └──────────┘
```

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
**相關文件**:
- `Develop/I18N_TRANSLATIONS_COMPLETE.md`
- `DevTools/checklist_report_20260126_144355.md`
