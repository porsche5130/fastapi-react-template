# 交易令牌問題診斷指南

## 問題描述
Session 中有組織資訊和可使用功能編號，但點選功能後沒有產生 Transaction Token。

## 診斷步驟

### 1. 檢查後端服務是否正常運行

```bash
cd Develop/backend
python check_transaction_api.py
```

### 2. 檢查 Redis 連線

```bash
cd Develop/backend
python diagnose_token_issue.py
```

### 3. 檢查前端錯誤

開啟瀏覽器開發者工具：

#### Chrome/Edge:
- 按 F12 開啟 DevTools
- 切換到 **Console** 標籤
- 切換到 **Network** 標籤

#### 要檢查的項目:

1. **Console 標籤**：
   - 查看是否有紅色錯誤訊息
   - 特別注意以下錯誤：
     - `Failed to fetch`
     - `401 Unauthorized`
     - `403 Forbidden`
     - `CORS error`
     - `[useTransactionToken]` 相關訊息

2. **Network 標籤**：
   - 點擊功能按鈕
   - 查找 `transaction/request` 請求
   - 點擊該請求查看：
     - **Request Headers**: 檢查 `Authorization` header 是否存在
     - **Request Payload**: 檢查 `func_code` 是否正確
     - **Response**: 查看回應內容
     - **Status Code**: 應該是 200，如果不是，查看錯誤訊息

### 4. 常見問題診斷

#### 問題 A: 沒有看到 `transaction/request` 請求

**可能原因：**
1. 前端沒有呼叫 `useTransactionToken` hook
2. `autoRequest` 設為 `false`
3. 頁面載入時發生錯誤

**檢查方法：**
```typescript
// 在頁面中確認有使用 useTransactionToken
const { txnToken, permissions } = useTransactionToken('your_func_code', {
  autoRequest: true  // 確保是 true
});
```

**檢查 Console 是否有：**
```
[useTransactionToken] 申請令牌成功: your_func_code
```

#### 問題 B: 看到請求但回應 401 Unauthorized

**可能原因：**
1. Bearer Token 過期或無效
2. 使用者未登入

**檢查方法：**
1. 查看 Network → transaction/request → Request Headers
2. 確認有 `Authorization: Bearer xxx` header
3. 確認 localStorage 有 `access_token`

**解決方法：**
- 重新登入
- 清除 localStorage 後重新登入

#### 問題 C: 看到請求但回應 403 Forbidden

**可能原因：**
1. 使用者沒有該功能的任何權限
2. `func_code` 不存在於 `system_functions` 表

**檢查方法：**
```sql
-- 檢查 func_code 是否存在
SELECT * FROM system_functions WHERE func_code = 'your_func_code';

-- 檢查使用者權限
SELECT rr.*
FROM role_rights rr
JOIN user_roles ur ON ur.id = rr.user_role_id
WHERE rr.func_code = 'your_func_code'
  AND ur.id IN (SELECT unnest(role_ids) FROM users WHERE id = your_user_id);
```

**解決方法：**
```bash
cd Develop/backend
# 註冊功能並授予權限（參考 migrations 腳本）
```

#### 問題 D: 請求成功但前端沒有儲存 Token

**可能原因：**
1. 前端 state 沒有更新
2. Hook 初始化問題

**檢查方法：**
```javascript
// 在 Console 執行
console.log('Token:', localStorage.getItem('txn_token_your_func_code'));
```

**注意：** Transaction Token 應該儲存在元件 state 中，不是 localStorage

#### 問題 E: Token 建立但無法使用

**可能原因：**
1. Token 在 Redis 中已過期
2. Token 格式錯誤
3. API 請求沒有帶 `X-Txn-Token` header

**檢查方法：**
```bash
# 檢查 Redis 中的 token
cd Develop/backend
python check_redis_tokens.py
```

**確認 API 請求有帶 header：**
```typescript
// 正確的用法
await axios.post('/api/some-endpoint', data, {
  headers: {
    'X-Txn-Token': txnToken
  }
});
```

### 5. 使用診斷工具

#### 工具 1: 後端令牌診斷
```bash
cd Develop/backend
python diagnose_token_issue.py
```

這會測試：
- Redis 連線
- 資料庫連線
- Session 建立
- Token 建立
- Token 儲存到 Redis
- Token 資訊查詢

#### 工具 2: API 端點檢查
```bash
cd Develop/backend
python check_transaction_api.py
```

這會測試：
- 後端服務是否運行
- 登入 API
- 申請 Token API
- 查詢 Token 資訊 API
- 撤銷 Token API
- Redis 儲存驗證

#### 工具 3: 列出 Redis 中的所有 Token
```bash
cd Develop/backend
python list_redis_tokens.py
```

### 6. 逐步檢查清單

- [ ] **後端服務正常運行** (http://localhost:10181/docs 可訪問)
- [ ] **Redis 連線正常** (diagnose_token_issue.py 通過)
- [ ] **資料庫連線正常** (list_users.py 能列出使用者)
- [ ] **使用者已登入** (localStorage 有 access_token)
- [ ] **Bearer Token 有效** (未過期)
- [ ] **功能已註冊** (system_functions 表有該 func_code)
- [ ] **使用者有權限** (role_rights 表有對應權限)
- [ ] **前端正確使用 Hook** (useTransactionToken 有呼叫)
- [ ] **API 請求正常發送** (Network 標籤看到請求)
- [ ] **API 回應成功** (Status 200)
- [ ] **Token 儲存到 State** (Console 有成功訊息)
- [ ] **API 請求帶 Token** (X-Txn-Token header 存在)

### 7. 前端完整檢查範例

```typescript
// 在頁面元件中
import { useTransactionToken } from '../hooks/useTransactionToken';

const YourPage = () => {
  // 使用 Hook
  const {
    txnToken,           // Token 字串
    permissions,        // 權限物件
    loading,           // 載入狀態
    error,             // 錯誤訊息
    remainingSeconds,  // 剩餘秒數
    showExtendPrompt   // 是否顯示延長對話框
  } = useTransactionToken('your_func_code', {
    autoRequest: true,  // 自動請求
    autoRevoke: true    // 自動撤銷
  });

  // 監控狀態變化
  useEffect(() => {
    console.log('[YourPage] Token:', txnToken);
    console.log('[YourPage] Permissions:', permissions);
    console.log('[YourPage] Error:', error);
  }, [txnToken, permissions, error]);

  // 檢查是否有 Token
  if (!txnToken) {
    return <div>正在取得交易令牌...</div>;
  }

  // 使用 Token 發送請求
  const handleSubmit = async () => {
    try {
      await axios.post('/api/your-endpoint', data, {
        headers: {
          'X-Txn-Token': txnToken  // ← 必須帶這個 header
        }
      });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      {/* 你的頁面內容 */}
    </div>
  );
};
```

### 8. 後端完整檢查範例

```python
# 路由定義
@router.post("/your-endpoint")
async def your_endpoint(
    data: YourModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("your_func_code", "update"))  # ← Token 驗證
):
    # 這裡的程式碼只有在 Token 驗證通過後才會執行
    ...
```

### 9. 完整測試流程

1. **啟動後端**
   ```bash
   cd Develop/backend
   uvicorn app.main:app --reload --port 10181
   ```

2. **開啟瀏覽器 DevTools**
   - 按 F12
   - 切換到 Console 和 Network 標籤

3. **登入系統**
   - 輸入帳號密碼
   - 確認 Console 沒有錯誤
   - 確認 localStorage 有 access_token

4. **點擊功能頁面**
   - 查看 Console 是否有 `[useTransactionToken] 申請令牌成功`
   - 查看 Network 是否有 `transaction/request` 請求
   - 查看請求 Status 是否為 200
   - 查看回應是否包含 `txn_token`

5. **執行操作**
   - 點擊需要 Token 的按鈕（如：儲存、更新、刪除）
   - 查看 Network 該請求是否有 `X-Txn-Token` header
   - 確認操作成功

### 10. 如果所有檢查都通過但還是沒有 Token

請提供以下資訊：

1. **Console 截圖**：包含所有錯誤訊息
2. **Network 截圖**：
   - transaction/request 請求的 Headers
   - transaction/request 請求的 Payload
   - transaction/request 請求的 Response
3. **程式碼片段**：
   - 使用 useTransactionToken 的程式碼
   - 頁面元件的程式碼

## 快速診斷命令

```bash
# 1. 檢查後端是否運行
curl http://localhost:10181/docs

# 2. 檢查 Redis
cd Develop/backend && python diagnose_token_issue.py

# 3. 檢查 API
cd Develop/backend && python check_transaction_api.py

# 4. 列出使用者
cd Develop/backend && python list_users.py
```

## 常用 Redis 命令

```bash
# 連線到 Redis (如果有 redis-cli)
redis-cli -a "!DC1qaz2wsx"

# 列出所有 session
KEYS session:*

# 列出所有 token
KEYS txn_token:*

# 查看 session 內容
GET session:your_session_id

# 查看 token 內容
GET txn_token:your_token

# 清除所有 token (測試用)
KEYS txn_token:* | xargs redis-cli -a "!DC1qaz2wsx" DEL
```
