# Transaction Token 問題修復完成報告

## 問題描述

登入後 `localStorage.getItem('txn_token')` 回傳 `null`,儘管:
- 後端成功建立 token 到 Redis ✅
- 後端 log 顯示 "✅ 建立交易令牌" ✅
- 前端程式碼有儲存邏輯 ✅

## 根本原因

**Pydantic Response Model 過濾了 `txn_token` 欄位!**

在 `app/schemas/auth.py` 的 `Token` 模型中,**只定義了 `access_token` 和 `token_type` 兩個欄位**:

```python
class Token(BaseModel):
    """Token 回應"""

    access_token: str = Field(..., description="存取 Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    # ❌ 缺少 txn_token 欄位!
```

**執行流程:**
1. 後端 `auth.py` 建立 `txn_token` 並回傳:
   ```python
   return {
       "access_token": access_token,
       "token_type": "bearer",
       "txn_token": txn_token  # ✅ 有回傳
   }
   ```

2. FastAPI 使用 `response_model=Token` 過濾回應:
   ```python
   @router.post("/login", response_model=Token, ...)  # ❌ Token 模型沒有 txn_token
   ```

3. FastAPI 自動移除 `Token` 模型中未定義的欄位 `txn_token` ❌

4. 前端收到的回應:
   ```json
   {
       "access_token": "...",
       "token_type": "bearer"
       // ❌ txn_token 被過濾掉了!
   }
   ```

## 修復內容

### 檔案: `app/schemas/auth.py` (Line 24-28)

**修改前:**
```python
class Token(BaseModel):
    """Token 回應"""

    access_token: str = Field(..., description="存取 Token")
    token_type: str = Field(default="bearer", description="Token 類型")
```

**修改後:**
```python
class Token(BaseModel):
    """Token 回應"""

    access_token: str = Field(..., description="存取 Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    txn_token: str = Field(..., description="交易令牌")  # ✅ 新增欄位
```

## 驗證步驟

### 1. 重啟後端
後端會自動載入修改後的 schema:
```bash
# 後端應該已經在運作,會自動重新載入
# 如果沒有自動重新載入,請手動重啟
```

### 2. 清空瀏覽器快取
- 按 `Ctrl+Shift+R` 強制重新載入
- 或開啟無痕模式

### 3. 重新登入並檢查
在 Console 執行:
```javascript
fetch('http://localhost:10181/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    account: 'porsche@lab.taipei',
    password: '您的密碼'
  })
})
.then(r => r.json())
.then(data => {
  console.log('完整回應:', data);
  console.log('txn_token:', data.txn_token);
  console.log('所有欄位:', Object.keys(data));
});
```

**預期結果:**
```javascript
完整回應: {
  access_token: "eyJhbGci...",
  token_type: "bearer",
  txn_token: "abc123..."  // ✅ 應該有值!
}
txn_token: "abc123..."
所有欄位: ["access_token", "token_type", "txn_token"]  // ✅ 三個欄位!
```

### 4. 正常登入並檢查 Console
應該看到:
```
🔍 Login API Response: {access_token: "...", token_type: "bearer", txn_token: "..."}
🔍 txn_token in response: <token_string>  // ✅ 不是 undefined!
✅ Saved access_token
✅ Saved txn_token: <token_string>  // ✅ 不是警告訊息!
🔍 localStorage txn_token: <token_string>  // ✅ 不是 null!
```

### 5. 檢查 localStorage
```javascript
localStorage.getItem('txn_token')  // ✅ 應該回傳 token 字串
```

## 相關修改

### 之前已完成的修改:

1. **Frontend Type Definition** (`types/index.ts`):
   ```typescript
   export interface TokenResponse {
     access_token: string;
     token_type: string;
     txn_token: string;  // ✅ 已新增
   }
   ```

2. **Auth Service** (`api/authService.ts`):
   ```typescript
   saveTxnToken: (txnToken: string): void => {
     localStorage.setItem('txn_token', txnToken);
   }  // ✅ 已新增
   ```

3. **Login Page** (`pages/LoginPage.tsx`):
   ```typescript
   if (response.txn_token) {
     authService.saveTxnToken(response.txn_token);
   }  // ✅ 已新增
   ```

4. **Axios Interceptor** (`api/axios.ts`):
   ```typescript
   const txnToken = localStorage.getItem('txn_token');
   if (txnToken) {
     config.headers['X-Txn-Token'] = txnToken;
   }  // ✅ 已新增
   ```

5. **Auth Context** (`contexts/AuthContext.tsx`):
   ```typescript
   catch (error) {
     // 只清除 access_token,保留 txn_token
     localStorage.removeItem('access_token');
   }  // ✅ 已修改
   ```

### 本次修改:

6. **Backend Schema** (`app/schemas/auth.py`):
   ```python
   class Token(BaseModel):
       access_token: str
       token_type: str
       txn_token: str  # ✅ 新增欄位
   ```

## 修復後的完整流程

1. **使用者登入** → POST `/api/auth/login`
2. **後端建立 Session 到 Redis** ✅
3. **後端建立 Transaction Token 到 Redis** ✅
4. **後端回傳 JSON** ✅
   ```json
   {
     "access_token": "...",
     "token_type": "bearer",
     "txn_token": "..."  // ✅ 不會被過濾!
   }
   ```
5. **前端接收回應** ✅
6. **前端儲存 access_token 到 localStorage** ✅
7. **前端儲存 txn_token 到 localStorage** ✅
8. **後續 API 請求自動帶上 X-Txn-Token header** ✅

## 成功標準

✅ **修復成功**,如果:
1. Console 顯示 `txn_token in response: <token_string>` (不是 undefined)
2. Console 顯示 `✅ Saved txn_token: <token_string>` (不是 ⚠️ 警告)
3. `localStorage.getItem('txn_token')` 回傳 token 字串 (不是 null)
4. API 請求 headers 包含 `X-Txn-Token: <token_string>`
5. Users 頁面成功載入使用者列表 (不會顯示 "等待交易令牌...")

## 教訓

**FastAPI Response Model 會過濾未定義的欄位!**

當使用 `response_model` 參數時:
- Pydantic 只會序列化模型中定義的欄位
- 其他欄位會被自動過濾掉
- 即使後端程式碼有回傳該欄位

**解決方案:**
- 在 Response Model 中明確定義所有要回傳的欄位
- 或者不使用 `response_model` 參數 (不推薦)

## 相關檔案

**後端:**
- ✅ `app/schemas/auth.py` - **本次修改**
- ✅ `app/routes/auth.py` - 登入 endpoint (已正確)
- ✅ `app/core/transaction_token_redis.py` - Token 建立邏輯 (已正確)
- ✅ `app/services/session_service.py` - Session 管理 (已正確)

**前端:**
- ✅ `types/index.ts` - Token 型別定義 (已修改)
- ✅ `api/authService.ts` - Auth service (已修改)
- ✅ `pages/LoginPage.tsx` - 登入頁面 (已修改)
- ✅ `api/axios.ts` - Axios 攔截器 (已修改)
- ✅ `contexts/AuthContext.tsx` - Auth context (已修改)

## 下一步

1. 重啟後端 (如果沒有自動重新載入)
2. 清空瀏覽器快取並重新登入
3. 驗證 `txn_token` 正確儲存到 localStorage
4. 測試 Users 頁面功能
5. 測試其他需要 Transaction Token 的功能

---

**修復完成時間:** 2026-01-27
**問題持續時間:** 從 Token v2.0 實作開始
**根本原因:** Pydantic Response Model 缺少 txn_token 欄位定義
