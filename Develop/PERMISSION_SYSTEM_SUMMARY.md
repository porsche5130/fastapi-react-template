# 權限系統完整說明

## 系統架構概覽

本系統採用**三層安全防護 + 兩階段權限驗證**架構。

---

## 三層安全防護

### 第一層：JWT Token
- **包含**: `session_id` (UUID)
- **有效期**: 1 小時
- **用途**: 識別使用者身份
- **儲存位置**: 前端 localStorage

### 第二層：Redis Session
- **包含**:
  - `user_id`: 使用者 ID
  - `role_ids`: 角色 ID 陣列
  - `organization_id`: 組織 ID
  - `username`: 使用者名稱
  - `account`: 帳號
  - `authorized_function_ids`: 使用者有權限的功能 IDs (階段一權限快取)
- **有效期**: 1 小時（每次存取自動延長）
- **用途**: 快速權限檢查、使用者資訊快取

### 第三層：Transaction Token
- **包含**: `session_id` + `system_functions_id` 綁定
- **有效期**: 30 分鐘（每次存取自動延長）
- **用途**: 防止 CSRF 攻擊、綁定功能操作

---

## 兩階段權限驗證

### 階段一：Redis 功能權限檢查 (Function Access)

**目的**: 快速驗證使用者是否有權限「進入」某個功能

**資料來源**: Redis Session 的 `authorized_function_ids`

**檢查邏輯**:
```python
# authorized_function_ids 在登入時建立，包含所有有 read 權限的功能
if system_function.id in session.authorized_function_ids:
    # 有功能權，進入階段二
else:
    # 無功能權，直接拒絕 403
```

**優點**:
- ⚡ 快速：Redis 記憶體存取，無需查詢資料庫
- 🔄 即時同步：角色權限更新時自動更新所有活躍 Session
- 💪 減輕負載：大部分無權限請求在此階段就被攔截

### 階段二：Database 操作權限檢查 (Operation Permission)

**目的**: 精確控制使用者在該功能內可以執行的「具體操作」

**資料來源**:
1. `role_rights` 表：檢查使用者是否有特定操作權限 (create/read/update/delete/print/file)
2. `system_functions.module_item`：取得該功能允許設定的權限項目

**檢查邏輯**:
```python
# 1. 檢查 role_rights
role_rights = db.query(RoleRight).filter(
    RoleRight.user_role_id.in_(user.user_role),
    RoleRight.func_code == "organizations"
).all()

has_create = any(rr.is_create for rr in role_rights)

# 2. 取得 module_item
system_function = db.query(SystemFunction).filter(
    SystemFunction.func_code == "organizations"
).first()

module_item = system_function.module_item
# ["create", "read", "update", "delete"]
```

---

## module_item 的重要性

### 核心概念
**module_item 是功能呈現的基本要求**

### 定義
`module_item` 定義了該功能「應該提供」哪些操作項目。

### 用途
1. **UI 設計依據**: 前端根據 module_item 設計 UI 元件
2. **權限設定範圍**: 管理員只能設定 module_item 包含的權限
3. **前後端一致性**: 確保 UI 與權限檢查邏輯一致

### 範例
```json
{
  "func_code": "organizations",
  "module_item": ["create", "read", "update", "delete"]
}
```

這表示「組織管理」功能的基本要求包含：
- 新增按鈕 (create)
- 查詢/列表 (read)
- 修改按鈕 (update)
- 刪除按鈕 (delete)

**不包含** print 和 file，所以前端不需要設計列印和檔案上傳按鈕。

---

## Transaction Token 機制

### 綁定邏輯
Token 綁定 `session_id` + `system_functions_id`

### 自動延長機制
```python
# 檢查是否已有該 session + function 的 token
mapping_key = f"session_func_token:{session_id}:{system_functions_id}"
existing_token = redis.get(mapping_key)

if existing_token and is_valid(existing_token):
    # 延長有效期到 30 分鐘
    redis.expire(token_key, 1800)
    return existing_token
else:
    # 建立新 token
    new_token = create_token(session_id, system_functions_id)
    redis.setex(token_key, 1800, token_data)
    return new_token
```

### Redis 資料結構
```
# Token 資訊
txn_token:abc123... = {
  "session_id": "53c9b56a...",
  "system_functions_id": 5,
  "created_at": "2026-01-25T10:30:00",
  "last_access": "2026-01-25T10:35:00"
}

# 快速查找映射
session_func_token:53c9b56a...:5 = "abc123..."
```

---

## Session 同步機制

### 角色權限更新時自動同步
當管理員修改角色權限時，系統會自動更新所有擁有該角色的使用者的活躍 Session。

### 更新流程
```python
# 在 save_role_rights() 中
# 1. 找出所有擁有此角色的使用者
users_with_role = db.query(User).filter(
    User.user_role.contains([role_id])
).all()

# 2. 重新計算每個使用者的 authorized_function_ids
for user in users_with_role:
    role_rights = db.query(RoleRight).filter(
        RoleRight.user_role_id.in_(user.user_role),
        RoleRight.is_read == True
    ).all()

    authorized_function_ids = [rr.system_function_id for rr in role_rights]

    # 3. 更新該使用者的所有 Session
    SessionService.update_user_sessions_authorized_functions(
        user_id=user.id,
        authorized_function_ids=authorized_function_ids
    )
```

### 優點
- ✅ 即時生效：權限修改後立即同步到所有活躍 Session
- ✅ 無需重新登入：使用者不需要重新登入即可獲得新權限
- ✅ 安全性：權限撤銷也會立即生效

---

## 完整流程圖

```
使用者請求 API
    ↓
[JWT Token 驗證]
    ↓
[從 Redis 取得 Session]
    ↓
[階段一: 檢查 authorized_function_ids]
    ├─ 無功能權 → 403 Forbidden
    └─ 有功能權 ↓
[階段二: 查詢 role_rights 檢查特定操作權限]
    ├─ 無操作權限 → 403 Forbidden
    └─ 有操作權限 ↓
[取得/建立/延長 Transaction Token]
    ↓
[查詢 system_functions.module_item]
    ↓
[回傳完整權限資訊]
    ├─ txn_token
    ├─ module_item
    └─ has_permission
    ↓
執行業務邏輯
```

---

## 前端整合流程

```
使用者進入頁面 (OrganizationsPage)
    ↓
useFunctionPermission("organizations") Hook 啟動
    ↓
1. 呼叫 POST /api/transaction/request
   └─ Backend 執行兩階段驗證
   └─ 建立/延長 Transaction Token
   └─ 回傳 { txn_token, permissions }
    ↓
2. 呼叫 GET /api/system-functions/by-code/organizations
   └─ 取得 { module_item: ["create", "read", "update", "delete"] }
    ↓
3. 設定 State
   ├─ txnToken: "abc123..."
   ├─ permissions: { create: false, read: true, update: true, delete: false }
   └─ moduleItem: ["create", "read", "update", "delete"]
    ↓
4. 根據 moduleItem 和 permissions 渲染 UI
   ├─ moduleItem.includes("create") → 顯示新增按鈕
   └─ permissions.create → 啟用/停用新增按鈕
    ↓
5. 使用者點擊按鈕執行操作
   └─ 帶上 X-Txn-Token Header 呼叫 API
    ↓
6. 離開頁面時撤銷 Token
   └─ POST /api/transaction/revoke
```

---

## 核心 API 端點

### 認證相關
- `POST /api/auth/login` - 登入（建立 Session）
- `POST /api/auth/logout` - 登出（刪除 Session）

### Transaction Token 相關
- `POST /api/transaction/request` - 申請功能交易令牌
- `GET /api/transaction/info` - 查詢令牌資訊
- `POST /api/transaction/revoke` - 撤銷交易令牌

### 系統功能相關
- `GET /api/system-functions/` - 取得系統功能列表
- `GET /api/system-functions/tree` - 取得系統功能樹狀結構
- `GET /api/system-functions/by-code/{func_code}` - 根據 func_code 取得功能資訊（含 module_item）

---

## 關鍵程式碼位置

### Backend
- **Session 管理**: `app/services/session_service.py`
- **Transaction Token**: `app/core/transaction_token_redis.py`
- **權限檢查**: `app/core/permissions.py`
  - `check_permission()` - 基本權限檢查
  - `check_permission_and_manage_token()` - 兩階段驗證 + Token 管理
- **登入邏輯**: `app/routes/auth.py`
- **角色權限管理**: `app/routes/role_rights.py`

### Frontend (建議)
- **權限管理 Hook**: `src/hooks/useFunctionPermission.ts`
- **Transaction Service**: `src/services/transactionService.ts`
- **System Function Service**: `src/services/systemFunctionService.ts`

---

## 檢查工具

### 檢查 Redis Session
```bash
# 命令列
cd Develop\backend
python check_redis_sessions.py

# GUI (Redis Commander)
cd Develop
start-redis-commander.bat
# 瀏覽 http://localhost:8081
```

### 檢查資料
```
# Session 資料
Key: session:53c9b56a-5ac9-4989-a3d9-aaa94fb43885
Value: {
  "user_id": 1,
  "role_ids": [1],
  "organization_id": 1,
  "username": "Porsche.chen",
  "account": "porsche@lab.taipei",
  "authorized_function_ids": [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  "created_at": "2026-01-25T10:30:00",
  "last_access": "2026-01-25T10:35:00"
}

# Transaction Token
Key: txn_token:abc123def456...
Value: {
  "session_id": "53c9b56a-5ac9-4989-a3d9-aaa94fb43885",
  "system_functions_id": 5,
  "created_at": "2026-01-25T10:30:00",
  "last_access": "2026-01-25T10:35:00"
}

# Token 映射
Key: session_func_token:53c9b56a...:5
Value: abc123def456...
```

---

## 效能優化

### Redis 快取
- ✅ 功能權限存在 Session，無需每次查詢
- ✅ Token 自動延長，減少重複建立
- ✅ 使用 mapping key 加速 token 查找

### 批次更新
- ✅ 角色權限修改時，批次更新所有相關 Session
- ✅ 使用 scan_iter 避免 keys * 阻塞 Redis

### TTL 管理
- ✅ Session: 1 小時，每次存取自動延長
- ✅ Token: 30 分鐘，每次存取自動延長
- ✅ 自動過期機制，無需手動清理

---

## 安全性考量

### CSRF 防護
- ✅ Transaction Token 綁定 session_id
- ✅ 所有操作 API 都需要驗證 token

### 權限即時撤銷
- ✅ 角色權限修改立即同步到所有 Session
- ✅ 使用者被停用時可強制登出所有 Session

### 多層驗證
- ✅ JWT Token 驗證身份
- ✅ Redis Session 驗證功能權限
- ✅ Transaction Token 驗證操作合法性
- ✅ Database 驗證精確權限

---

## 常見問題 FAQ

### Q1: 為什麼需要兩階段驗證？
**A**: Redis 階段提供快速檢查，攔截大部分無權限請求；Database 階段提供精確控制，確保操作權限正確。

### Q2: authorized_function_ids 何時更新？
**A**: 使用者登入時建立，角色權限修改時自動同步所有 Session。

### Q3: Transaction Token 何時建立？
**A**: 呼叫 `check_permission_and_manage_token()` 時自動建立，如果已存在則自動延長到 30 分鐘。

### Q4: module_item 的用途？
**A**: 功能呈現的基本要求，定義該功能應該提供哪些操作項目，前端據此設計 UI。

### Q5: 為什麼說「有了權限 + 有了 txn_token 才能使用功能」？
**A**:
- 權限決定使用者「能不能」執行某個操作
- Transaction Token 證明使用者已通過權限檢查，是執行操作的「憑證」
- 兩者缺一不可

---

## 相關文件

- [兩階段權限驗證架構詳細說明](./TWO_TIER_PERMISSION_ARCHITECTURE.md)
- [前端整合範例](./FRONTEND_INTEGRATION_EXAMPLE.md)
- [Transaction Token 使用指南](./TRANSACTION_TOKEN_GUIDE.md)

---

## 總結

本權限系統提供：

✅ **多層安全防護**: JWT Token + Redis Session + Transaction Token + Database 權限
✅ **高效能**: Redis 快取減少資料庫查詢
✅ **即時同步**: 權限變更立即生效，無需重新登入
✅ **靈活設計**: module_item 支援不同功能的個別化權限設定
✅ **前後端一致**: 統一的權限檢查邏輯確保系統安全

**核心理念**: 有了權限 + 有了 txn_token 才能使用功能
