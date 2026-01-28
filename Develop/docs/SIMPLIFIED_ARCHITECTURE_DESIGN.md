# 簡化版多租戶架構設計

**設計日期**: 2026-01-26
**核心理念**: 通過 session_id 綁定實現組織資訊的自動傳遞

---

## 核心設計理念

### 資訊流動鏈

```
User Login
    ↓
Session (Redis) ← 包含 organization_id
    ↓
Transaction Token ← 綁定 session_id
    ↓
API Request ← 攜帶 Token
    ↓
驗證時取得 Session → 自動獲得 organization_id
```

### 關鍵優勢

✅ **Token 通過 session_id 間接包含組織資訊**
- Transaction Token 綁定 session_id
- Session 資料包含 organization_id
- 驗證 Token 時自動取得 organization_id

✅ **無需改變現有架構**
- Session 資料已經包含 organization_id
- 只需要增強 Token 內容和驗證邏輯

✅ **簡單且安全**
- Session 是單一真實來源（Single Source of Truth）
- Token 失效時 Session 一起失效
- 組織資訊集中管理

---

## 現有架構分析

### 1. Session 資料結構（已完成 ✅）

**儲存位置**: Redis `session:{session_id}`

**資料結構**:
```json
{
  "user_id": 123,
  "role_ids": [1, 2],
  "organization_id": 5,              // ✅ 已經存在
  "username": "張三",
  "account": "zhang@example.com",
  "authorized_function_ids": [10, 15, 20],
  "created_at": "2026-01-26T10:00:00+08:00",
  "last_access": "2026-01-26T10:15:00+08:00"
}
```

**建立時機**: 登入時
```python
# app/routes/auth.py (lines 90-98)
session_created = SessionService.create_session(
    session_id=session_id,
    user_id=user.id,
    role_ids=role_ids,
    organization_id=user.organization_id,  # ✅ 已傳入
    username=user.username,
    account=user.account,
    authorized_function_ids=authorized_function_ids
)
```

### 2. Transaction Token 結構（需增強 ⚠️）

**當前結構**:
```json
{
  "session_id": "3e4a7b2c-5d8f-4e1a-9c3b-7f2d8e1a4c6b",
  "system_functions_id": 15,
  "permissions": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "print": false,
    "file": false
  },
  "created_at": "2026-01-26T10:00:00+08:00",
  "last_access": "2026-01-26T10:15:00+08:00"
}
```

**需要增加**:
```json
{
  "session_id": "3e4a7b2c-5d8f-4e1a-9c3b-7f2d8e1a4c6b",
  "system_functions_id": 15,
  "func_code": "tenant_users",        // ← 新增：功能代碼
  "module_code": "users",             // ← 新增：模組代碼
  "permissions": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "print": false,
    "file": false
  },
  "created_at": "2026-01-26T10:00:00+08:00",
  "last_access": "2026-01-26T10:15:00+08:00"
}
```

**組織資訊的獲取**:
```python
# 通過 session_id 取得
token_data = get_token_from_redis(txn_token)
session_id = token_data["session_id"]

session_data = SessionService.get_session(session_id)
organization_id = session_data["organization_id"]  # ← 從 Session 取得
```

---

## 資訊流動示意圖

### 登入流程

```
┌─────────────┐
│   使用者     │
│  Login 登入  │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│  Backend: /api/auth/login       │
├─────────────────────────────────┤
│ 1. 驗證帳號密碼                  │
│ 2. 產生 session_id (UUID)       │
│ 3. 建立 Session (Redis)         │
│    - user_id: 123               │
│    - organization_id: 5  ✅     │
│    - role_ids: [1, 2]           │
│    - authorized_function_ids    │
│ 4. 產生 Bearer Token (JWT)      │
│    - 包含 session_id            │
└──────┬──────────────────────────┘
       │
       ↓
┌──────────────────┐
│  返回 Token      │
│  給前端          │
└──────────────────┘
```

### 請求 Transaction Token 流程

```
┌─────────────────────────────────┐
│  Frontend: 請求 Txn Token       │
│  POST /api/transaction/token    │
│  Header: Bearer {jwt_token}     │
│  Body: { func_code: "tenant_users" } │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Backend: 驗證並生成 Token      │
├─────────────────────────────────┤
│ 1. 驗證 Bearer Token            │
│ 2. 從 JWT 取得 session_id       │
│ 3. 從 Redis 取得 Session ✅     │
│    - organization_id: 5         │
│ 4. 查詢 system_functions        │
│    - 取得 func_code             │
│    - 取得 module_code           │
│    - 取得 permissions           │
│ 5. 建立 Txn Token (Redis)       │
│    - session_id (綁定)          │
│    - func_code ← 新增           │
│    - module_code ← 新增         │
│    - permissions                │
└──────┬──────────────────────────┘
       │
       ↓
┌──────────────────┐
│  返回 Txn Token  │
│  給前端          │
└──────────────────┘
```

### API 請求流程（多租戶）

```
┌─────────────────────────────────┐
│  Frontend: API 請求             │
│  GET /api/users/5/123/tenant_users │
│  Header:                        │
│    Bearer: {jwt_token}          │
│    X-Txn-Token: {txn_token}     │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Backend: 三層驗證              │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ 第一層：Bearer Token 驗證    │ │
│ │ - 驗證 JWT 有效性           │ │
│ │ - 取得 current_user         │ │
│ │ - user.organization_id: 5   │ │
│ └─────────────────────────────┘ │
│         ↓                       │
│ ┌─────────────────────────────┐ │
│ │ 第二層：Txn Token 驗證       │ │
│ │ 1. 驗證 Token 存在且有效     │ │
│ │ 2. 取得 Token 資料:         │ │
│ │    - session_id             │ │
│ │    - func_code: "tenant_users" │ │
│ │    - permissions            │ │
│ │ 3. 從 Session 取得 ✅:       │ │
│ │    - organization_id: 5     │ │
│ └─────────────────────────────┘ │
│         ↓                       │
│ ┌─────────────────────────────┐ │
│ │ 第三層：組織權限驗證         │ │
│ │ - URL org_id: 5             │ │
│ │ - User org_id: 5            │ │
│ │ - Session org_id: 5 ✅      │ │
│ │ - 三者一致 → 通過            │ │
│ └─────────────────────────────┘ │
└──────┬──────────────────────────┘
       │
       ↓
┌──────────────────┐
│  返回資料         │
└──────────────────┘
```

---

## 需要修改的地方（最小化）

### 修改 1: Transaction Token 加入 func_code 和 module_code

**檔案**: `app/core/transaction_token_redis.py`

**當前** (lines 89-96):
```python
token_info = {
    "session_id": session_id,
    "system_functions_id": system_functions_id,
    "permissions": permissions or {},
    "created_at": get_taipei_now().isoformat(),
    "last_access": get_taipei_now().isoformat()
}
```

**修改為**:
```python
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

---

### 修改 2: Token 生成端點傳入 func_code 和 module_code

**檔案**: `app/routes/transaction.py`

**當前邏輯**:
```python
@router.post("/token")
async def request_transaction_token(
    request: TransactionTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 查詢 system_functions
    system_function = db.query(SystemFunction).filter(
        SystemFunction.id == request.system_function_id
    ).first()

    # 取得權限
    permissions = get_user_permissions(...)

    # 建立 Token
    txn_token = get_or_create_function_token(
        session_id=session_id,
        system_functions_id=system_function.id,
        permissions=permissions
    )
```

**修改為**:
```python
@router.post("/token")
async def request_transaction_token(
    request: TransactionTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 查詢 system_functions
    system_function = db.query(SystemFunction).filter(
        SystemFunction.id == request.system_function_id
    ).first()

    # 取得權限
    permissions = get_user_permissions(...)

    # 建立 Token（傳入 func_code 和 module_code）
    txn_token = get_or_create_function_token(
        session_id=session_id,
        system_functions_id=system_function.id,
        func_code=system_function.func_code,      # ← 新增
        module_code=system_function.module_code,  # ← 新增
        permissions=permissions
    )
```

---

### 修改 3: require_txn_token 支援多功能代碼

**檔案**: `app/routes/transaction.py`

**新增工具函數**:
```python
def get_org_id_from_token(txn_token: str) -> Optional[int]:
    """
    從 Transaction Token 取得組織 ID

    步驟:
    1. 從 Redis 取得 Token 資料
    2. 取得 session_id
    3. 從 Session 取得 organization_id

    Args:
        txn_token: Transaction Token

    Returns:
        organization_id，如果失敗則返回 None
    """
    redis_client = get_redis()
    if not redis_client:
        return None

    try:
        # 取得 Token 資料
        token_key = f"txn_token:{txn_token}"
        token_json = redis_client.get(token_key)
        if not token_json:
            return None

        token_data = json.loads(token_json)
        session_id = token_data.get("session_id")

        # 取得 Session 資料
        session_data = SessionService.get_session(session_id)
        if not session_data:
            return None

        return session_data.get("organization_id")

    except Exception as e:
        logger.error(f"取得組織 ID 失敗: {e}")
        return None
```

**修改 require_txn_token**:
```python
def require_txn_token(
    func_codes: Union[str, List[str]],  # ← 支援多個功能代碼
    permission_type: str,
    one_time_use: bool = False
):
    """
    驗證 Transaction Token

    Args:
        func_codes: 功能代碼（字串或列表）
        permission_type: 權限類型
        one_time_use: 是否一次性使用

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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少交易令牌"
            )

        # 2. 驗證 Token
        token_data = verify_transaction_token(txn_token, db)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的交易令牌"
            )

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"無 {permission_type} 權限"
            )

        # 5. 一次性使用
        if one_time_use:
            revoke_transaction_token(txn_token)

        return None

    return Depends(dependency)
```

---

### 修改 4: API 路由加入組織驗證

**檔案**: `app/routes/user.py`

**範例：多租戶路由**

```python
@router.get("/users/{org_id}/{user_id}/tenant_users", response_model=UserDetailResponse)
async def get_tenant_user(
    org_id: int,                    # ← URL 中的組織 ID
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token(
        ["users", "tenant_users"],  # ← 支援兩個功能代碼
        "read"
    ))
):
    """
    取得組織成員資料

    支援功能代碼:
    - tenant_users: 組織管理者（限制在自己組織）
    - users: 系統管理員（無限制）

    三層驗證:
    1. Bearer Token → current_user
    2. Txn Token → func_code, permissions
    3. 組織權限 → org_id vs current_user.organization_id
    """
    # 第三層驗證：組織權限
    # 檢查 URL 中的 org_id 是否為使用者所屬組織
    has_full_permission = check_permission(db, current_user, "users", "read")
    if not has_full_permission:
        # tenant_users: 只能存取自己組織
        if org_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"無權限存取組織 {org_id} 的資料"
            )

    # 查詢使用者（限制在指定組織）
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == org_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    return user
```

---

## 組織權限驗證流程

### 三層驗證機制

```python
# API 端點範例
@router.get("/users/{org_id}/{user_id}/tenant_users")
async def get_tenant_user(
    org_id: int,                    # ← 從 URL 取得
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ← 第一層：Bearer Token
    _: None = Depends(require_txn_token(...))        # ← 第二層：Txn Token
):
    # 第三層：組織權限驗證
    if org_id != current_user.organization_id:
        # 從 current_user 直接比對
        raise HTTPException(403, "組織權限不符")

    # 繼續處理...
```

### 驗證邏輯說明

#### 1. Bearer Token (JWT) → current_user
- 驗證使用者身份
- 取得 `current_user.organization_id`

#### 2. Transaction Token → 功能權限
- 驗證功能代碼 (func_code)
- 驗證操作權限 (permissions)
- 通過 session_id 連結到 Session（包含 organization_id）

#### 3. 組織權限 → 資料隔離
- URL 中的 `org_id` vs `current_user.organization_id`
- 確保使用者只能存取自己組織的資料

### 資料流示意圖

```
┌─────────────────┐
│  URL: org_id=5  │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│  Bearer Token (JWT)         │
│  ↓                          │
│  current_user:              │
│    - user_id: 123           │
│    - organization_id: 5  ✅ │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Txn Token                  │
│  ↓                          │
│  session_id                 │
│  ↓                          │
│  Session (Redis):           │
│    - user_id: 123           │
│    - organization_id: 5  ✅ │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  驗證:                      │
│  URL org_id == User org_id  │
│  5 == 5  ✅                 │
└─────────────────────────────┘
```

---

## 優勢總結

### 1. 簡單性 ✅
- Session 資料**已經包含** organization_id
- 不需要修改 Session 結構
- 只需要在 Token 中加入 func_code 和 module_code

### 2. 自動傳遞 ✅
- Token 綁定 session_id
- Session 包含 organization_id
- **Token 等於間接包含組織資訊**

### 3. 單一真實來源 ✅
- Session 是組織資訊的唯一來源
- Token 通過 session_id 引用
- 避免資料不一致

### 4. 安全性 ✅
- 三層驗證：JWT + Txn Token + 組織檢查
- 資料隔離：多租戶自動限制
- 集中管理：Session 統一控制

### 5. 向後相容 ✅
- Session 結構不變
- 現有 Token 機制保持
- 只增加欄位，不破壞現有功能

---

## 實作檢查清單

### 階段 1: Token 增強
- [ ] 修改 `get_or_create_function_token()` 函數簽名
- [ ] Token 資料加入 `func_code` 和 `module_code`
- [ ] 修改 Token 生成端點傳入新參數
- [ ] 測試 Token 生成

### 階段 2: 驗證邏輯
- [ ] 新增 `get_org_id_from_token()` 工具函數
- [ ] 修改 `require_txn_token()` 支援多功能代碼
- [ ] 測試 Token 驗證

### 階段 3: API 路由
- [ ] 新增多租戶路由（包含 org_id）
- [ ] 實作組織權限驗證
- [ ] 實作 reset_password 端點
- [ ] 測試 API 功能

### 階段 4: 前端適配
- [ ] 更新 API Service URL 格式
- [ ] 測試前端功能

### 階段 5: 部署
- [ ] 註冊 reset_password 功能代碼
- [ ] 設定角色權限
- [ ] 整合測試
- [ ] 文件更新

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
**關鍵理念**: Token 通過 session_id 綁定，間接包含組織資訊 ✨
