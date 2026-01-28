# Session ID 與 Transaction Token 重構計畫

**建立日期**: 2026-01-26
**目的**: 將 organization_id 整合到 session_id 中，實現多租戶 API 架構

---

## 執行摘要

### 當前架構問題

**現況**:
```
session_id: UUID 格式（隨機）
範例: "3e4a7b2c-5d8f-4e1a-9c3b-7f2d8e1a4c6b"

Session Data (Redis):
{
  "user_id": 123,
  "role_ids": [1, 2],
  "organization_id": 5,  ← 存在 Redis 中
  "username": "張三",
  ...
}

Transaction Token:
{
  "session_id": "3e4a7b2c-...",  ← 綁定 session_id
  "system_functions_id": 15,
  ...
}
```

**問題**:
1. ❌ session_id 不包含 organization_id → 無法從 URL 直接驗證組織權限
2. ❌ 需要額外查詢 Redis 才能取得 organization_id → 增加延遲
3. ❌ API URL 設計無法包含 org_id → 不符合多租戶 RESTful 規範

### 目標架構

**新設計**:
```
session_id: {user_id}_{timestamp}_{organization_id}
範例: "123_1706234567_5"

Session Data (Redis):
{
  "user_id": 123,
  "role_ids": [1, 2],
  "organization_id": 5,  ← 與 session_id 中的值一致
  "username": "張三",
  ...
}

Transaction Token:
{
  "session_id": "123_1706234567_5",  ← 包含 org_id
  "system_functions_id": 15,
  "func_code": "tenant_users",
  "module_code": "users",
  "permissions": {...}
}

API URL:
/api/users/5/123/tenant_users
           ↑
         從 session_id 提取並驗證
```

**優勢**:
1. ✅ session_id 包含 organization_id → 快速驗證
2. ✅ 三層安全驗證：URL org_id vs session_id org_id vs Redis org_id
3. ✅ 符合多租戶 RESTful 設計
4. ✅ 提高性能（減少 Redis 查詢）

---

## 影響範圍分析

### 1. Session ID 生成與解析

#### 1.1 Login 流程（生成 session_id）

**檔案**: `app/routes/auth.py`

**當前程式碼** (line 66-67):
```python
# 產生 Session ID (UUID)
session_id = str(uuid.uuid4())
```

**需要改為**:
```python
# 產生 Session ID: {user_id}_{timestamp}_{organization_id}
timestamp = int(datetime.now(timezone.utc).timestamp())
session_id = f"{user.id}_{timestamp}_{user.organization_id}"
```

**影響**:
- ✅ 簡單修改
- ⚠️ session_id 格式改變，需要確保舊 session 已過期

#### 1.2 Session ID 解析工具

**需要新增**: `app/core/session_utils.py`

```python
"""
Session ID 工具函數
"""

from typing import Tuple, Optional
import re


def parse_session_id(session_id: str) -> Tuple[int, int, int]:
    """
    解析 session_id

    Args:
        session_id: 格式為 {user_id}_{timestamp}_{organization_id}

    Returns:
        (user_id, timestamp, organization_id)

    Raises:
        ValueError: session_id 格式錯誤
    """
    parts = session_id.split('_')
    if len(parts) != 3:
        raise ValueError(f"Invalid session_id format: {session_id}")

    try:
        user_id = int(parts[0])
        timestamp = int(parts[1])
        organization_id = int(parts[2])
        return user_id, timestamp, organization_id
    except ValueError as e:
        raise ValueError(f"Invalid session_id format: {session_id}") from e


def validate_session_id(session_id: str) -> bool:
    """
    驗證 session_id 格式是否正確

    Args:
        session_id: Session ID

    Returns:
        是否有效
    """
    pattern = r'^\d+_\d+_\d+$'
    return re.match(pattern, session_id) is not None


def extract_org_id_from_session(session_id: str) -> Optional[int]:
    """
    從 session_id 提取 organization_id

    Args:
        session_id: Session ID

    Returns:
        organization_id，如果格式錯誤則返回 None
    """
    try:
        _, _, organization_id = parse_session_id(session_id)
        return organization_id
    except ValueError:
        return None


def generate_session_id(user_id: int, organization_id: int, timestamp: int = None) -> str:
    """
    生成 session_id

    Args:
        user_id: 使用者 ID
        organization_id: 組織 ID
        timestamp: Unix 時間戳（可選，預設為當前時間）

    Returns:
        session_id
    """
    if timestamp is None:
        from datetime import datetime, timezone
        timestamp = int(datetime.now(timezone.utc).timestamp())

    return f"{user_id}_{timestamp}_{organization_id}"
```

### 2. Transaction Token 修改

#### 2.1 Token 生成時加入 func_code 和 module_code

**檔案**: `app/core/transaction_token_redis.py`

**當前程式碼** (lines 89-96):
```python
# Token 資訊（包含權限）
token_info = {
    "session_id": session_id,
    "system_functions_id": system_functions_id,
    "permissions": permissions or {},
    "created_at": get_taipei_now().isoformat(),
    "last_access": get_taipei_now().isoformat()
}
```

**需要改為**:
```python
# Token 資訊（包含權限、func_code、module_code）
token_info = {
    "session_id": session_id,
    "system_functions_id": system_functions_id,
    "func_code": func_code,           # ← 新增
    "module_code": module_code,       # ← 新增
    "permissions": permissions or {},
    "created_at": get_taipei_now().isoformat(),
    "last_access": get_taipei_now().isoformat()
}
```

**函數簽名修改**:
```python
def get_or_create_function_token(
    session_id: str,
    system_functions_id: int,
    func_code: str,           # ← 新增參數
    module_code: str,         # ← 新增參數
    permissions: dict = None,
    valid_minutes: int = 30
) -> str:
```

#### 2.2 Token 驗證時檢查 org_id

**檔案**: `app/routes/transaction.py`

**需要新增**驗證邏輯：

```python
from app.core.session_utils import extract_org_id_from_session

def verify_org_id_match(token_session_id: str, url_org_id: int) -> bool:
    """
    驗證 Token 的 session_id 中的 org_id 與 URL 中的 org_id 是否匹配

    Args:
        token_session_id: Token 中的 session_id
        url_org_id: URL 路徑中的 org_id

    Returns:
        是否匹配

    Raises:
        HTTPException: 組織權限不符
    """
    session_org_id = extract_org_id_from_session(token_session_id)

    if session_org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID 格式錯誤"
        )

    if session_org_id != url_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"組織權限不符: URL org_id={url_org_id}, Session org_id={session_org_id}"
        )

    return True
```

#### 2.3 修改 require_txn_token 依賴

**當前**: 只驗證功能權限
**需要改為**: 支援多功能代碼 + 組織權限驗證

```python
def require_txn_token(
    func_codes: Union[str, List[str]],  # ← 改為支援多個
    permission_type: str,
    one_time_use: bool = False,
    verify_org_id: bool = False,        # ← 新增參數
    org_id: int = None                  # ← 新增參數（從路徑提取）
):
    """
    驗證 Transaction Token

    Args:
        func_codes: 功能代碼（字串或字串列表）
        permission_type: 權限類型 (create/read/update/delete/print/file)
        one_time_use: 是否一次性使用
        verify_org_id: 是否驗證組織 ID
        org_id: URL 路徑中的組織 ID（用於驗證）

    Returns:
        FastAPI Dependency
    """
    # 標準化為列表
    if isinstance(func_codes, str):
        func_codes = [func_codes]

    async def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # 1. 提取 Token
        txn_token = request.headers.get("X-Txn-Token")
        if not txn_token:
            raise HTTPException(...)

        # 2. 驗證 Token（從 Redis 取得資料）
        token_data = verify_transaction_token(txn_token, db)
        if not token_data:
            raise HTTPException(...)

        # 3. 驗證功能代碼（支援多個）
        token_func_code = token_data.get("func_code")
        if token_func_code not in func_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"功能代碼不符: 需要 {func_codes}，Token 為 {token_func_code}"
            )

        # 4. 驗證權限
        permissions = token_data.get("permissions", {})
        if not permissions.get(permission_type):
            raise HTTPException(...)

        # 5. 驗證組織 ID（如果需要）
        if verify_org_id and org_id is not None:
            session_id = token_data.get("session_id")
            verify_org_id_match(session_id, org_id)

        # 6. 一次性使用（如果需要）
        if one_time_use:
            revoke_transaction_token(txn_token)

        return None

    return Depends(dependency)
```

### 3. API 路由修改

#### 3.1 新增 org_id 參數到多租戶路由

**範例**: `app/routes/user.py`

**第一層：多租戶 API**

```python
# 新增：取得組織成員列表
@router.get("/users/{org_id}", response_model=List[UserDetailResponse])
async def get_tenant_users(
    org_id: int,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token(
        ["users", "tenant_users"],
        "read",
        verify_org_id=True,
        org_id=org_id  # ← 傳入進行驗證
    ))
):
    """
    取得組織成員列表

    多租戶功能: tenant_users
    系統管理員功能: users

    自動根據權限範圍過濾資料
    """
    query = db.query(User)

    # 資料層級控制
    has_full_permission = check_permission(db, current_user, "users", "read")
    if not has_full_permission:
        # tenant_users: 只能查看自己組織
        query = query.filter(User.organization_id == org_id)

        # 額外安全檢查：確保 org_id 是使用者所屬組織
        if org_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限存取此組織資料"
            )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if search:
        query = query.filter(
            (User.account.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    users = query.order_by(User.id).offset(skip).limit(limit).all()
    return users


# 新增：取得組織成員資料
@router.get("/users/{org_id}/{user_id}/{func_code}", response_model=UserDetailResponse)
async def get_tenant_user(
    org_id: int,
    user_id: int,
    func_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token(
        ["users", "tenant_users"],
        "read",
        verify_org_id=True,
        org_id=org_id
    ))
):
    """
    取得組織成員資料

    URL 格式: /api/users/{org_id}/{user_id}/{func_code}
    """
    # 驗證 func_code
    if func_code not in ["users", "tenant_users"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支援的功能代碼: {func_code}"
        )

    # 查詢使用者
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == org_id  # ← 限制在指定組織
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 資料層級控制
    has_full_permission = check_permission(db, current_user, "users", "read")
    if not has_full_permission:
        # tenant_users: 只能查看自己組織
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限讀取此使用者資訊"
            )

    return user


# 新增：更新組織成員資料
@router.put("/users/{org_id}/{user_id}/{func_code}", response_model=UserDetailResponse)
async def update_tenant_user(
    org_id: int,
    user_id: int,
    func_code: str,
    user_data: UserDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token(
        ["users", "tenant_users"],
        "update",
        verify_org_id=True,
        org_id=org_id
    ))
):
    """
    更新組織成員資料

    URL 格式: /api/users/{org_id}/{user_id}/{func_code}
    """
    # 查詢使用者
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == org_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 資料層級控制
    has_full_permission = check_permission(db, current_user, "users", "update")
    if not has_full_permission:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此使用者"
            )

    # 儲存原始資料
    original_data = user_detail_to_dict(user)

    # 更新邏輯（略）
    # ...

    return user


# 新增：重置組織成員密碼
@router.post("/users/{org_id}/{user_id}/reset_password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_tenant_user_password(
    org_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token(
        "reset_password",
        "update",
        verify_org_id=True,
        org_id=org_id
    ))
):
    """
    重置組織成員密碼為組織代碼

    URL 格式: /api/users/{org_id}/{user_id}/reset_password
    """
    # 查詢目標使用者
    target_user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == org_id
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 安全檢查
    if target_user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能重置同組織成員的密碼"
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法重置自己的密碼，請使用密碼變更功能"
        )

    # 取得組織代碼
    organization = db.query(Organization).filter(
        Organization.id == org_id
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

    db.commit()

    # 記錄日誌（略）
    # ...

    return None
```

**第二層：全域 API（保持不變）**

```python
# 既有：取得所有使用者列表（系統管理員）
@router.get("/users/", response_model=List[UserDetailResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    organization_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("users", "read"))
):
    """
    取得所有使用者列表

    系統管理員功能: users
    無組織限制
    """
    # 既有邏輯保持不變
    ...
```

#### 3.2 FastAPI 路由順序

**重要**: FastAPI 按照**註冊順序**匹配路由

```python
# routes/user.py

# 1. 特殊路由（最優先）
@router.get("/users/me/my_profile")
@router.put("/users/me/my_profile")
@router.post("/users/me/change_password")

# 2. 多租戶路由（包含 org_id，第一層）
@router.get("/users/{org_id}")
@router.get("/users/{org_id}/{user_id}/{func_code}")
@router.put("/users/{org_id}/{user_id}/{func_code}")
@router.delete("/users/{org_id}/{user_id}/{func_code}")
@router.post("/users/{org_id}/{user_id}/reset_password")

# 3. 全域路由（無 org_id，第二層）
@router.get("/users/")
@router.get("/users/{user_id}/{func_code}")
@router.put("/users/{user_id}/{func_code}")
@router.delete("/users/{user_id}/{func_code}")
```

### 4. 前端修改

#### 4.1 API Service 修改

**檔案**: `frontend/src/services/tenantUsersService.ts`

**當前**:
```typescript
export const getTenantUsers = async (organizationId: number): Promise<TenantUser[]> => {
  const response = await axios.get<TenantUser[]>(API_BASE, {
    params: { organization_id: organizationId }
  });
  return response.data;
};
```

**改為**:
```typescript
export const getTenantUsers = async (organizationId: number): Promise<TenantUser[]> => {
  // 新 URL 格式: /api/users/{org_id}
  const response = await axios.get<TenantUser[]>(`${API_BASE}/${organizationId}`);
  return response.data;
};

export const getTenantUser = async (organizationId: number, userId: number): Promise<TenantUser> => {
  // 新 URL 格式: /api/users/{org_id}/{user_id}/tenant_users
  const response = await axios.get<TenantUser>(`${API_BASE}/${organizationId}/${userId}/tenant_users`);
  return response.data;
};

export const updateTenantUser = async (
  organizationId: number,
  userId: number,
  data: TenantUserUpdate
): Promise<TenantUser> => {
  // 新 URL 格式: /api/users/{org_id}/{user_id}/tenant_users
  const response = await axios.put<TenantUser>(
    `${API_BASE}/${organizationId}/${userId}/tenant_users`,
    data
  );
  return response.data;
};

export const resetUserPassword = async (
  organizationId: number,
  userId: number
): Promise<void> => {
  // 新 URL 格式: /api/users/{org_id}/{user_id}/reset_password
  await axios.post(`${API_BASE}/${organizationId}/${userId}/reset_password`);
};
```

#### 4.2 Hook 修改

**檔案**: `frontend/src/hooks/useTransactionToken.ts`

**需要修改**: Token 請求時傳入 func_code 和 module_code

---

## 實作順序與步驟

### 階段 1: 基礎工具與 Session ID 改造（高優先級）

#### 步驟 1.1: 建立 Session ID 工具
- [ ] 建立 `app/core/session_utils.py`
- [ ] 實作 `parse_session_id()`, `generate_session_id()`, `extract_org_id_from_session()`
- [ ] 單元測試

#### 步驟 1.2: 修改 Login 流程
- [ ] 修改 `app/routes/auth.py` 的 session_id 生成邏輯
- [ ] 確保 session_id 格式為 `{user_id}_{timestamp}_{organization_id}`
- [ ] 測試登入功能

#### 步驟 1.3: 更新 SessionService
- [ ] `app/services/session_service.py` 保持不變（Redis 結構不變）
- [ ] 只改變 session_id 的格式

### 階段 2: Transaction Token 增強（高優先級）

#### 步驟 2.1: 修改 Token 資料結構
- [ ] 修改 `app/core/transaction_token_redis.py`
- [ ] Token 加入 `func_code` 和 `module_code`
- [ ] 更新 `get_or_create_function_token()` 簽名

#### 步驟 2.2: 修改 Token 驗證邏輯
- [ ] 修改 `app/routes/transaction.py`
- [ ] `require_txn_token` 支援多功能代碼
- [ ] 新增組織 ID 驗證邏輯 `verify_org_id_match()`

#### 步驟 2.3: 修改 Token 生成端點
- [ ] 修改 `POST /transaction/token` 端點
- [ ] 從 system_functions 查詢 func_code 和 module_code
- [ ] 測試 Token 生成與驗證

### 階段 3: API 路由重構（高優先級）

#### 步驟 3.1: 新增多租戶路由
- [ ] `app/routes/user.py` 新增第一層 API
- [ ] `app/routes/organization.py` 新增第一層 API
- [ ] 確保路由順序正確

#### 步驟 3.2: 保持全域路由
- [ ] 現有的第二層 API 保持不變
- [ ] 更新 `require_txn_token` 調用支援多功能代碼

#### 步驟 3.3: 實作 reset_password
- [ ] 新增 `POST /users/{org_id}/{user_id}/reset_password`
- [ ] 密碼重置為組織代碼邏輯
- [ ] 日誌記錄

### 階段 4: 前端適配（中優先級）

#### 步驟 4.1: 更新 API Service
- [ ] 修改 `tenantUsersService.ts`
- [ ] 修改 `tenantProfileService.ts`
- [ ] URL 格式改為新版

#### 步驟 4.2: 更新 Hook
- [ ] 修改 `useTransactionToken.ts`
- [ ] Token 請求傳入 module_code

#### 步驟 4.3: 測試前端功能
- [ ] tenant_users CRUD
- [ ] tenant_profile CRUD
- [ ] reset_password

### 階段 5: 註冊功能與測試（中優先級）

#### 步驟 5.1: 註冊功能代碼
- [ ] SQL: 註冊 `reset_password` 到 system_functions
- [ ] SQL: 確認 `tenant_profile` 和 `tenant_users` 已註冊

#### 步驟 5.2: 設定權限
- [ ] SQL: 為所有角色設定對應權限

#### 步驟 5.3: 整合測試
- [ ] 測試三層安全驗證
- [ ] 測試多租戶隔離
- [ ] 測試性能

---

## 向後相容性處理

### 問題：舊 Session 格式

**舊格式**: UUID `"3e4a7b2c-5d8f-4e1a-9c3b-7f2d8e1a4c6b"`
**新格式**: `"123_1706234567_5"`

**解決方案**:

#### 方案 A: 強制重新登入（推薦）
- Session 過期時間為 1 小時
- 部署新版本時，所有使用者會在 1 小時內自然過期
- 過期後重新登入，取得新格式 session_id

**實作**:
```python
# app/core/session_utils.py
def is_legacy_session_id(session_id: str) -> bool:
    """檢查是否為舊格式 session_id (UUID)"""
    return '-' in session_id


# app/routes/transaction.py
def verify_session_format(session_id: str):
    """驗證 session_id 格式"""
    if is_legacy_session_id(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session 格式過期，請重新登入"
        )
```

#### 方案 B: 支援雙格式（複雜，不推薦）
- 同時支援舊格式和新格式
- 增加程式複雜度

---

## 測試計畫

### 單元測試

#### 1. Session ID 工具測試
```python
# tests/test_session_utils.py
def test_parse_session_id():
    user_id, timestamp, org_id = parse_session_id("123_1706234567_5")
    assert user_id == 123
    assert timestamp == 1706234567
    assert org_id == 5

def test_generate_session_id():
    session_id = generate_session_id(123, 5, 1706234567)
    assert session_id == "123_1706234567_5"

def test_extract_org_id():
    org_id = extract_org_id_from_session("123_1706234567_5")
    assert org_id == 5
```

#### 2. Token 驗證測試
```python
# tests/test_transaction_token.py
def test_token_with_func_code():
    token = get_or_create_function_token(
        session_id="123_1706234567_5",
        system_functions_id=15,
        func_code="tenant_users",
        module_code="users",
        permissions={"read": True, "update": True}
    )
    assert token is not None

def test_verify_org_id_match():
    assert verify_org_id_match("123_1706234567_5", 5) == True

    with pytest.raises(HTTPException):
        verify_org_id_match("123_1706234567_5", 6)
```

### 整合測試

#### 1. 登入與 Session 測試
```python
def test_login_generates_new_session_id():
    response = client.post("/api/auth/login", json={
        "account": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # 解碼 JWT 取得 session_id
    # 驗證格式為 {user_id}_{timestamp}_{org_id}
```

#### 2. 多租戶 API 測試
```python
def test_get_tenant_users_with_org_id():
    response = client.get(
        "/api/users/5",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Txn-Token": txn_token
        }
    )
    assert response.status_code == 200

def test_cross_org_access_denied():
    # 嘗試存取其他組織的資料
    response = client.get(
        "/api/users/6/123/tenant_users",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Txn-Token": txn_token
        }
    )
    assert response.status_code == 403
```

---

## 檢查清單

### 階段 1: Session ID 改造
- [ ] 建立 session_utils.py
- [ ] 修改 Login 生成邏輯
- [ ] 測試登入功能
- [ ] 測試舊 Session 處理

### 階段 2: Token 增強
- [ ] Token 加入 func_code, module_code
- [ ] require_txn_token 支援多功能代碼
- [ ] 實作組織 ID 驗證
- [ ] 測試 Token 生成與驗證

### 階段 3: API 重構
- [ ] 新增多租戶路由（第一層）
- [ ] 保持全域路由（第二層）
- [ ] 實作 reset_password
- [ ] 測試路由衝突處理

### 階段 4: 前端適配
- [ ] 更新 API Service URL
- [ ] 更新 Hook
- [ ] 測試前端功能

### 階段 5: 部署
- [ ] 註冊功能代碼
- [ ] 設定權限
- [ ] 整合測試
- [ ] 上線部署

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
**相關文件**:
- `API_ARCHITECTURE_ANALYSIS.md`
- `BACKEND_API_CORRECT_ANALYSIS.md`
