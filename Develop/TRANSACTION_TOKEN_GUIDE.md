# 交易令牌機制使用指南

## 概述

本系統採用 **Session ID + Transaction Token** 的雙重驗證機制,確保 API 交易的安全性。

## 安全機制

### 1. Session ID (JWT Token)
- 使用者登入後取得
- 儲存在 localStorage: `access_token`
- 用於驗證使用者身份
- 每個 API 請求都需要攜帶

### 2. Transaction Token (Txn Token)
- 進入功能頁面時申請
- 綁定特定功能 (func_code)
- 有效期 15 分鐘
- 可設為一次性或多次使用
- 用於驗證功能權限

### 3. 雙重驗證流程

```
┌─────────────┐
│   使用者     │
└──────┬──────┘
       │ 1. 登入
       ▼
┌─────────────┐
│   後端 API   │ → 回傳 Session ID (JWT)
└──────┬──────┘
       │
       │ 2. 進入功能頁面,申請 Token
       │    帶著 Session ID
       ▼
┌─────────────┐
│   後端 API   │ → 驗證 Session ID
└──────┬──────┘ → 檢查功能權限
       │        → 生成 Txn Token
       │
       │ 3. 執行操作
       │    帶著 Session ID + Txn Token
       ▼
┌─────────────┐
│   後端 API   │ → 驗證 Session ID
└─────────────┘ → 驗證 Txn Token
                → 檢查時間是否過期
                → 檢查 Token 與 Session 是否匹配
                → 執行操作
```

## 後端實作

### 1. 申請 Token API

```python
POST /api/transaction/request
Headers: {
    "Authorization": "Bearer <session_id>"
}
Body: {
    "func_code": "role_rights"
}

Response: {
    "txn_token": "abc123...",
    "expires_in": 900,
    "func_code": "role_rights",
    "permissions": {
        "create": false,
        "read": true,
        "update": false,
        "delete": false,
        "print": false,
        "file": false
    }
}
```

### 2. 需要 Token 的 API 範例

```python
from app.routes.transaction import require_txn_token

@router.post("/role_rights/save")
async def save_role_rights(
    data: RoleRightsData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("role_rights", "update"))
):
    # Session ID 已驗證 (current_user)
    # Txn Token 已驗證 (require_txn_token)
    # 可以安全執行操作
    ...
```

### 3. Token 驗證邏輯

```python
def verify_txn_token(txn_token, user_id, func_code, one_time_use):
    # 1. Token 是否存在?
    # 2. Token 是否過期? (15 分鐘)
    # 3. Token 是否已使用? (如果是一次性)
    # 4. Token 的 user_id 是否匹配?
    # 5. Token 的 func_code 是否匹配?
    ...
```

## 前端實作

### 1. 使用 Hook 管理 Token

```typescript
import { useTransactionToken } from '../hooks/useTransactionToken';

const RoleRightsPage = () => {
  // 進入頁面自動申請 token
  const {
    txnToken,
    permissions,
    loading,
    error,
    remainingSeconds
  } = useTransactionToken('role_rights');

  // 根據 permissions 控制 UI
  const canUpdate = permissions?.update || false;

  // 執行操作時帶上 token
  const handleSave = async () => {
    await saveRoleRights(data, txnToken);
  };

  return (
    <div>
      {loading && <p>正在申請令牌...</p>}
      {error && <p>錯誤: {error}</p>}
      {remainingSeconds < 60 && <p>警告: 令牌即將過期</p>}

      <button disabled={!canUpdate} onClick={handleSave}>
        儲存
      </button>
    </div>
  );
};
```

### 2. Service 層帶上 Token

```typescript
import axios from '../api/axios';
import { withTxnToken } from '../services/transactionService';

export const saveRoleRights = async (
  roleId: number,
  rights: RoleRight[],
  txnToken: string
) => {
  const response = await axios.post(
    `/api/role_rights/${roleId}/save`,
    { rights },
    withTxnToken(txnToken)  // 自動添加 X-Txn-Token header
  );
  return response.data;
};
```

## 安全性分析

### ✅ 防範手動 API 呼叫

假設攻擊者嘗試手動呼叫 API:

```bash
# 攻擊者嘗試直接呼叫 API
curl -X POST http://localhost:10181/api/role_rights/6/save \
  -H "Authorization: Bearer <stolen_session_id>" \
  -H "Content-Type: application/json" \
  -d '{"rights": [...]}'
```

**結果**: ❌ 失敗!
- 缺少 `X-Txn-Token` header
- 後端回傳 `401 Unauthorized: Missing txn token`

---

```bash
# 攻擊者嘗試用舊的或偽造的 token
curl -X POST http://localhost:10181/api/role_rights/6/save \
  -H "Authorization: Bearer <stolen_session_id>" \
  -H "X-Txn-Token: <old_or_fake_token>" \
  -d '{"rights": [...]}'
```

**結果**: ❌ 失敗!
- Token 不存在、已過期或已使用
- 或 Token 的 user_id 與 session_id 不匹配
- 後端回傳 `401 Unauthorized: Invalid token`

### ✅ 時間限制

- Token 有效期只有 15 分鐘
- 攻擊者無法長期使用竊取的 token
- 即使攻擊者同時竊取 session_id 和 txn_token,也必須在 15 分鐘內使用

### ✅ 一次性使用 (可選)

如果設定為一次性使用:
- Token 使用後立即銷毀
- 攻擊者無法重複使用同一個 token

### ✅ 功能綁定

- 每個 token 只能用於特定功能
- `role_rights` 的 token 不能用於 `organizations`
- 即使攻擊者有 token,也只能操作該功能

### ✅ 權限檢查

Token 申請時就檢查權限:
1. Session ID 驗證使用者身份
2. 檢查使用者在該功能的所有權限
3. 將權限資訊放入 token response
4. 前端根據權限控制 UI
5. 後端執行操作時再次驗證權限

## 最佳實踐

### 1. 進入頁面立即申請 Token

```typescript
useEffect(() => {
  requestToken();
}, []);
```

### 2. 離開頁面撤銷 Token

```typescript
useEffect(() => {
  return () => {
    revokeToken();
  };
}, []);
```

### 3. Token 快過期時提醒使用者

```typescript
if (remainingSeconds < 60) {
  toast.warning('令牌即將過期,請盡快完成操作');
}
```

### 4. Token 過期後自動刷新

```typescript
if (remainingSeconds <= 0) {
  await refreshToken();
}
```

### 5. 關鍵操作使用一次性 Token

```python
# 刪除、匯出等關鍵操作使用一次性 token
_: None = Depends(require_txn_token("organizations", "delete", one_time_use=True))
```

## 效能考量

### Token 儲存

目前使用記憶體儲存 (`_token_store`),適合開發和小規模部署。

生產環境建議使用 **Redis**:
- 更高效能
- 支援分散式部署
- 自動過期機制
- 持久化選項

### Token 清理

系統會在以下時機清理過期 token:
1. 生成新 token 時
2. 定期背景任務 (可選)

## 測試範例

### 測試流程

1. 使用者登入取得 session_id
2. 進入角色權限頁面申請 token
3. 使用 token 執行儲存操作
4. 驗證操作成功

### 測試程式碼

```python
# test_transaction_token.py
def test_transaction_flow():
    # 1. 登入
    login_resp = client.post("/api/auth/login", json={
        "username": "test@example.com",
        "password": "password"
    })
    session_id = login_resp.json()["access_token"]

    # 2. 申請 token
    token_resp = client.post(
        "/api/transaction/request",
        json={"func_code": "role_rights"},
        headers={"Authorization": f"Bearer {session_id}"}
    )
    txn_token = token_resp.json()["txn_token"]

    # 3. 執行操作
    save_resp = client.post(
        "/api/role_rights/6/save",
        json={"rights": [...]},
        headers={
            "Authorization": f"Bearer {session_id}",
            "X-Txn-Token": txn_token
        }
    )

    assert save_resp.status_code == 200
```

## 常見問題

### Q: 為什麼需要兩個 token?

A: Session ID 驗證「你是誰」,Txn Token 驗證「你能做什麼」且「在什麼時間內」。

### Q: Token 過期怎麼辦?

A: 前端會定期檢查,過期前提醒使用者,過期後自動刷新或要求重新申請。

### Q: 可以同時開多個功能頁面嗎?

A: 可以,每個功能頁面有獨立的 token。

### Q: Token 儲存在哪裡?

A: Token 只存在前端的記憶體中 (React state),不存 localStorage,更安全。

### Q: 如果網路延遲導致操作超時?

A: 前端應該在操作前檢查 token 是否還有足夠的剩餘時間,不夠就先刷新。
