# 兩階段權限驗證架構

## 設計理念

系統採用兩階段權限驗證機制，結合 Redis Session 快速檢查與資料庫精確控制：

1. **階段一 (Redis)**: 檢查功能存取權 (Function Access)
2. **階段二 (Database)**: 檢查操作權限 (Operation Permission)

---

## 階段一：Redis 功能權限檢查

### 目的
快速驗證使用者是否有權限「進入」某個功能。

### 資料來源
從 **Redis Session** 的 `authorized_function_ids` 欄位檢查。

### Session 結構
```json
{
  "session:53c9b56a-5ac9-4989-a3d9-aaa94fb43885": {
    "user_id": 1,
    "role_ids": [1],
    "organization_id": 1,
    "username": "Porsche.chen",
    "account": "porsche@lab.taipei",
    "authorized_function_ids": [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "created_at": "2026-01-25T10:30:00",
    "last_access": "2026-01-25T10:35:00"
  }
}
```

### 檢查邏輯
```python
# 從 role_rights 查詢使用者所有有 read 權限的功能
# 在登入時儲存到 Session 的 authorized_function_ids

# 執行階段快速檢查
if system_function.id in session.authorized_function_ids:
    # 有功能權，進入階段二
else:
    # 無功能權，直接拒絕
```

### 優點
- **快速**: Redis 記憶體存取，無需查詢資料庫
- **即時同步**: 當角色權限更新時，自動更新所有活躍 Session
- **減輕負載**: 大部分無權限請求在 Redis 階段就被攔截

---

## 階段二：Database 操作權限檢查

### 目的
精確控制使用者在該功能內可以執行的「具體操作」。

### 資料來源
1. **role_rights 表**: 檢查使用者是否有特定操作權限
2. **system_functions.module_item**: 取得該功能允許設定的權限項目

### 檢查邏輯
```python
# 1. 檢查 role_rights
role_rights = db.query(RoleRight).filter(
    RoleRight.user_role_id.in_(user.user_role),
    RoleRight.func_code == "organizations"
).all()

# 檢查是否有 create 權限
has_create = any(rr.is_create for rr in role_rights)

# 2. 取得 module_item
system_function = db.query(SystemFunction).filter(
    SystemFunction.func_code == "organizations"
).first()

module_item = system_function.module_item
# 例如: ["create", "read", "update", "delete", "print", "file"]
```

### module_item 說明
`module_item` 是**功能呈現的基本要求**，定義了該功能「應該提供」哪些操作項目。

**重要概念**:
- `module_item` 決定前端要顯示哪些 UI 元件（按鈕、選單等）
- 使用者必須「有權限 + 有 txn_token」才能使用功能
- 前端根據 `module_item` 和使用者權限決定 UI 呈現

**範例**:
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

如果使用者只有 read 和 update 權限，則前端只顯示「查詢」和「修改」按鈕。

---

## Transaction Token 自動管理

### 綁定機制
Token 綁定 `session_id` + `system_functions_id`。

### 自動延長機制
```python
# 檢查 Redis 是否已有該 session + function 的 token
mapping_key = f"session_func_token:{session_id}:{system_functions_id}"
existing_token = redis.get(mapping_key)

if existing_token and is_valid(existing_token):
    # 延長有效期到 30 分鐘
    redis.expire(token_key, 1800)
else:
    # 建立新 token
    new_token = create_token(session_id, system_functions_id)
    redis.setex(token_key, 1800, token_data)
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

## API 整合範例

### 方式 1: 直接呼叫
```python
@router.post("/organizations")
async def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 檢查權限並自動管理 Token
    result = check_permission_and_manage_token(
        db, current_user, "organizations", "create"
    )

    # result = {
    #     "txn_token": "abc123...",
    #     "module_item": ["create", "read", "update", "delete"],
    #     "has_permission": True
    # }

    txn_token = result["txn_token"]
    module_item = result["module_item"]

    # 執行業務邏輯
    organization = Organization(**data.model_dump())
    db.add(organization)
    db.commit()

    return organization
```

### 方式 2: 使用裝飾器
```python
@router.post("/organizations")
@require_permission("organizations", "create")
async def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # current_user.current_txn_token 已自動設定
    # current_user.current_module_item 已自動設定

    organization = Organization(**data.model_dump())
    db.add(organization)
    db.commit()

    return organization
```

---

## Session 同步機制

### 角色權限更新時自動同步
當管理員修改角色權限時，系統會自動更新所有擁有該角色的使用者的活躍 Session：

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
- **即時生效**: 權限修改後立即同步到所有活躍 Session
- **無需重新登入**: 使用者不需要重新登入即可獲得新權限
- **安全性**: 權限撤銷也會立即生效

---

## 完整流程圖

```
使用者請求 API
    ↓
[JWT Token 驗證]
    ↓
[取得 Redis Session]
    ↓
[階段一: 檢查 authorized_function_ids]
    ↓ 有功能權
[階段二: 檢查 role_rights 特定操作權限]
    ↓ 有操作權限
[取得/建立/延長 Transaction Token]
    ↓
[查詢 system_functions.module_item]
    ↓
[回傳完整權限資訊]
    ↓
執行業務邏輯
```

---

## 安全層級總結

### 第一層：JWT Token
- 包含: `session_id`
- 有效期: 1 小時
- 用途: 識別使用者身份

### 第二層：Redis Session
- 包含: `user_id`, `role_ids`, `organization_id`, `authorized_function_ids`
- 有效期: 1 小時 (自動延長)
- 用途: 快速權限檢查

### 第三層：Transaction Token
- 包含: `session_id` + `system_functions_id`
- 有效期: 30 分鐘 (自動延長)
- 用途: 防止 CSRF 攻擊，綁定功能操作

### 第四層：Database 權限
- 來源: `role_rights` 表
- 用途: 精確控制操作權限

---

## 最佳實務

### 1. 功能級別 API (列表查詢)
使用 `check_permission(db, user, func_code, "read")` 即可。

### 2. 操作級別 API (新增/修改/刪除)
使用 `check_permission_and_manage_token(db, user, func_code, permission_type)`。

### 3. 前端權限控制與 UI 呈現

**核心概念**: 有了權限 + 有了 txn_token 才能使用功能

```typescript
// 在功能頁面載入時 (例如 OrganizationsPage.tsx)
useEffect(() => {
  const initializeFunction = async () => {
    try {
      // 1. 檢查權限並取得 txn_token
      const result = await transactionService.requestToken("organizations");

      // result = {
      //   txn_token: "abc123...",
      //   expires_in: 1800,
      //   func_code: "organizations",
      //   permissions: {
      //     create: false,
      //     read: true,
      //     update: true,
      //     delete: false,
      //     print: false,
      //     file: false
      //   }
      // }

      setTxnToken(result.txn_token);
      setPermissions(result.permissions);

      // 2. 取得 system_functions 的 module_item (從後端 API)
      const functionInfo = await api.getSystemFunction("organizations");
      // functionInfo.module_item = ["create", "read", "update", "delete"]

      setModuleItem(functionInfo.module_item);

    } catch (error) {
      // 沒有權限或無法取得 token，無法使用此功能
      navigate("/unauthorized");
    }
  };

  initializeFunction();
}, []);

// 3. 根據 module_item 和 permissions 決定 UI 呈現
return (
  <div>
    {/* 只有 module_item 包含 create 才顯示新增按鈕 */}
    {moduleItem.includes("create") && (
      <Button
        disabled={!permissions.create}  // 使用者沒有 create 權限則停用
        onClick={handleCreate}
      >
        新增
      </Button>
    )}

    {/* 只有 module_item 包含 update 才顯示修改按鈕 */}
    {moduleItem.includes("update") && (
      <Button
        disabled={!permissions.update}
        onClick={handleUpdate}
      >
        修改
      </Button>
    )}

    {/* 只有 module_item 包含 delete 才顯示刪除按鈕 */}
    {moduleItem.includes("delete") && (
      <Button
        disabled={!permissions.delete}
        onClick={handleDelete}
      >
        刪除
      </Button>
    )}

    {/* 列表永遠顯示（因為能進入此頁面就有 read 權限） */}
    <DataTable data={organizations} />
  </div>
);

// 4. 所有 API 呼叫都帶 txn_token
const handleCreate = async () => {
  try {
    await api.createOrganization(data, {
      headers: { "X-Txn-Token": txnToken }
    });
  } catch (error) {
    if (error.status === 401) {
      // Token 過期，重新申請
      const result = await transactionService.requestToken("organizations");
      setTxnToken(result.txn_token);
    }
  }
};
```

**重點說明**:
1. **module_item** = 功能的基本要求（該功能「應該」提供哪些操作）
2. **permissions** = 使用者實際擁有的權限（該使用者「可以」執行哪些操作）
3. **UI 呈現邏輯** = `moduleItem.includes(operation) && permissions[operation]`
4. **txn_token** = 執行操作的必要憑證（所有 API 呼叫都必須帶）

### 4. 記得處理權限不足
```python
try:
    result = check_permission_and_manage_token(db, user, "organizations", "create")
except HTTPException as e:
    # e.status_code = 403
    # e.detail = "無權限執行此操作: organizations - create"
    raise
```

---

## 效能優化

### Redis 快取
- 功能權限存在 Session，無需每次查詢
- Token 自動延長，減少重複建立

### 批次更新
- 角色權限修改時，批次更新所有相關 Session

### TTL 管理
- Session: 1 小時，每次存取自動延長
- Token: 30 分鐘，每次存取自動延長

---

## 檢查工具

### 檢查 Redis Session
```bash
# 命令列
cd Develop\backend
python check_redis_sessions.py

# GUI
cd Develop
start-redis-commander.bat
# 瀏覽 http://localhost:8081
```

### 檢查 Transaction Token
```python
# 在 Redis Commander 搜尋
session_func_token:*
txn_token:*
```

---

## 常見問題

### Q1: 為什麼需要兩階段驗證？
**A**:
- Redis 階段提供快速檢查，攔截大部分無權限請求
- Database 階段提供精確控制，確保操作權限正確

### Q2: authorized_function_ids 何時更新？
**A**:
- 使用者登入時建立
- 角色權限修改時自動同步所有 Session

### Q3: Transaction Token 何時建立？
**A**:
- 呼叫 `check_permission_and_manage_token()` 時自動建立
- 如果已存在則自動延長到 30 分鐘

### Q4: module_item 的用途？
**A**:
- **功能呈現的基本要求**: 定義該功能應該提供哪些操作項目
- **UI 元件設計依據**: 前端根據 module_item 設計 UI（例如：有 create 就設計新增按鈕）
- **權限設定範圍**: 管理員在設定角色權限時，只能設定 module_item 包含的項目
- **前後端一致性**: 確保前端 UI 與後端權限檢查邏輯一致

### Q5: 為什麼說「有了權限 + 有了 txn_token 才能使用功能」？
**A**:
1. **權限 (permissions)**: 決定使用者「能不能」執行某個操作
2. **Transaction Token**: 證明使用者已通過權限檢查，是執行操作的「憑證」
3. **兩者缺一不可**:
   - 沒有權限 → 無法取得 txn_token → 無法呼叫 API
   - 有權限但沒有 txn_token → API 會拒絕請求 (401/403 錯誤)
   - 有權限且有 txn_token → 可以正常使用功能

---

## 總結

兩階段權限驗證架構結合了效能與安全性：

✅ **快速**: Redis 快取減少資料庫查詢
✅ **精確**: Database 確保權限正確
✅ **即時**: Session 同步機制保證權限變更立即生效
✅ **安全**: 三層 Token + 權限檢查防止未授權存取
✅ **靈活**: module_item 支援不同功能的個別化權限設定
