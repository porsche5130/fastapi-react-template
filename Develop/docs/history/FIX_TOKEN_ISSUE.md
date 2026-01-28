# 修正 Token 格式問題

## 問題描述

Redis 中的 token 缺少 `func_code`、`module_code` 和 `permissions` 欄位。

## 原因

前端申請的 token 是用**舊版本**的後端程式碼建立的。

## 解決步驟

### 步驟 1: 清除舊的 Token（已完成 ✅）

```bash
cd Develop/backend
python clear_old_tokens.py
```

**結果：** 已刪除 2 個舊 token 和 2 個映射

### 步驟 2: 驗證新版本 Token 格式（已完成 ✅）

測試腳本確認新版本的 Token 包含所有必要欄位：
- ✅ session_id
- ✅ system_functions_id
- ✅ **func_code** (新增)
- ✅ **module_code** (新增)
- ✅ **permissions** (新增)

### 步驟 3: 重新啟動後端服務 ⚠️

**檢查後端是否正在運行：**
```bash
# 查看 uvicorn 進程
ps aux | grep uvicorn

# 或者在 Windows 上
tasklist | findstr python
```

**重新啟動後端：**

1. 如果後端正在運行，先停止它（Ctrl+C）

2. 重新啟動：
   ```bash
   cd Develop/backend
   uvicorn app.main:app --reload --port 10181
   ```

3. 確認啟動成功：
   - 看到 `Application startup complete` 訊息
   - 訪問 http://localhost:10181/docs 確認 API 文件可訪問

### 步驟 4: 清除瀏覽器快取

**Chrome/Edge:**
1. 按 `Ctrl + Shift + Delete`
2. 選擇「快取的圖片和檔案」
3. 點擊「清除資料」

**或者使用無痕模式：**
- 按 `Ctrl + Shift + N`

### 步驟 5: 重新測試

1. **登入系統**

2. **進入任一功能頁面**（例如：組織管理）

3. **開啟 Redis 檢查工具**，查看新建立的 token：
   - 應該要包含 `func_code`
   - 應該要包含 `module_code`
   - 應該要包含 `permissions`

4. **檢查瀏覽器 Console**：
   - 應該要看到 `[useTransactionToken] 申請令牌成功` 訊息

5. **檢查瀏覽器 Network**：
   - 找到 `transaction/request` 請求
   - 查看 Response，應該包含：
     ```json
     {
       "txn_token": "...",
       "expires_in": 1800,
       "func_code": "organizations",
       "permissions": {
         "create": true,
         "read": true,
         ...
       }
     }
     ```

## 驗證腳本

### 快速驗證 Token 格式

```bash
cd Develop/backend
python -c "
from app.core.redis_client import get_redis, init_redis
import json

init_redis(host='localhost', port=6379, db=0, password='!DC1qaz2wsx')
redis_client = get_redis()

# 列出所有 token
for key in redis_client.scan_iter(match='txn_token:*'):
    token_data = redis_client.get(key)
    if token_data:
        token_info = json.loads(token_data)
        print(f'Token: {key}')
        print(f'  func_code: {token_info.get(\"func_code\", \"❌ MISSING\")}')
        print(f'  module_code: {token_info.get(\"module_code\", \"❌ MISSING\")}')
        print(f'  permissions: {\"✅ OK\" if \"permissions\" in token_info else \"❌ MISSING\"}')
        print()
"
```

### 完整測試

```bash
cd Develop/backend
python diagnose_token_issue.py
```

## 前端整合狀況

### ✅ 已使用 useTransactionToken Hook 的頁面：
- ChangePasswordPage.tsx
- MyProfilePage.tsx

### ⚠️ 使用手動方式的頁面：
- NumberingRulesPage.tsx (使用 `transactionService.requestTransactionToken()`)
- FileAttachmentsPage.tsx (使用 `transactionService.requestTransactionToken()`)

### ❌ 尚未整合的頁面：
- OrganizationsPage.tsx
- UsersPage.tsx
- UserRolesPage.tsx
- RoleRightsPage.tsx
- SystemCodesPage.tsx
- SystemFunctionsPage.tsx
- SystemNotificationsPage.tsx
- SysProfilePage.tsx
- UserLogsPage.tsx
- TenantProfilePage.tsx
- TenantUsersPage.tsx

## 建議的前端整合方式

### 方式 1: 使用 useTransactionToken Hook（推薦）

```typescript
import { useTransactionToken } from '../hooks/useTransactionToken';

const YourPage: React.FC = () => {
  const {
    txnToken,
    permissions,
    loading,
    error,
    showExtendPrompt,
    handleExtendResponse
  } = useTransactionToken('your_func_code');

  // 使用 txnToken 發送請求
  const handleSubmit = async () => {
    await yourService.update(data, txnToken);
  };

  // 顯示延長對話框
  {showExtendPrompt && (
    <TransactionExtendDialog
      onExtend={() => handleExtendResponse(true)}
      onCancel={() => handleExtendResponse(false)}
    />
  )}
};
```

### 方式 2: 手動呼叫（NumberingRules 的方式）

```typescript
import transactionService from '../services/transactionService';

useEffect(() => {
  const init = async () => {
    const response = await transactionService.requestTransactionToken('your_func_code');
    setTxnToken(response.txn_token);
    setPermissions(response.permissions);
  };
  init();
}, []);
```

## 下一步工作

1. ✅ 清除舊 Token
2. ✅ 驗證新 Token 格式
3. ⚠️ 重新啟動後端服務（待確認）
4. ⏳ 清除瀏覽器快取
5. ⏳ 重新測試 Token 建立
6. ⏳ 整合所有前端頁面使用交易令牌

## 常見問題

### Q1: 為什麼舊的 Token 沒有 func_code？

**A:** 因為這些 Token 是在修改 `transaction_token_redis.py` 之前建立的。舊版本的程式碼沒有這些欄位。

### Q2: 清除 Token 後會影響已登入的使用者嗎？

**A:** 會。已登入的使用者需要：
1. 刷新頁面（重新申請 Token）
2. 或重新登入

### Q3: 如何確認後端程式碼已重新載入？

**A:**
1. 查看後端 terminal 是否有 `Reloading...` 訊息
2. 或重新啟動後端服務
3. 執行 `python clear_old_tokens.py` 驗證新格式

### Q4: 前端需要修改嗎？

**A:** 不需要。前端的 `transactionService.requestTransactionToken()` 會自動收到新格式的回應。但建議所有頁面都改用 `useTransactionToken` hook 以獲得更好的使用者體驗（自動延長、過期提示等）。

## 檢查清單

- [x] 清除舊的 Token
- [x] 驗證新 Token 格式正確
- [ ] 重新啟動後端服務
- [ ] 清除瀏覽器快取
- [ ] 重新登入測試
- [ ] 檢查 Redis 中的新 Token 格式
- [ ] 整合所有前端頁面

## 參考文件

- [TRANSACTION_TOKEN_ENHANCEMENT_COMPLETE.md](./TRANSACTION_TOKEN_ENHANCEMENT_COMPLETE.md) - Token 增強功能說明
- [TXN_TOKEN_USAGE_SUMMARY.md](./TXN_TOKEN_USAGE_SUMMARY.md) - Token 使用狀況總覽
- [TRANSACTION_TOKEN_TROUBLESHOOT.md](./TRANSACTION_TOKEN_TROUBLESHOOT.md) - 問題診斷指南
