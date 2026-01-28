# Transaction Token 儲存問題修復驗證

## 問題描述
登入後 `localStorage.getItem('txn_token')` 回傳 `null`,儘管:
- 後端成功建立 token 到 Redis ✅
- 前端登入回應包含 txn_token ✅
- LoginPage 程式碼有儲存邏輯 ✅

## 根本原因
在 `AuthContext.tsx` 的 `loadUser()` 函式中,當發生錯誤時會呼叫 `authService.clearToken()`,這會刪除包括 `txn_token` 在內的所有 tokens。

登入流程:
1. LoginPage 儲存 `txn_token` 到 localStorage ✅
2. 呼叫 `login(response.access_token)` ✅
3. `login()` 呼叫 `loadUser()` ✅
4. `loadUser()` 發生錯誤時呼叫 `clearToken()` ❌ (刪除了 txn_token)

## 修復內容

### 修改檔案: `Develop/frontend/src/contexts/AuthContext.tsx` (Line 37)

**修改前:**
```typescript
catch (error) {
  console.error('載入使用者資料失敗:', error);
  authService.clearToken();  // ❌ 這會刪除 txn_token
  setUser(null);
  setIsAuthenticated(false);
}
```

**修改後:**
```typescript
catch (error) {
  console.error('載入使用者資料失敗:', error);
  // 只清除 access_token,保留 txn_token
  localStorage.removeItem('access_token');  // ✅ 只刪除 access_token
  setUser(null);
  setIsAuthenticated(false);
}
```

## 驗證步驟

### 步驟 1: 清空瀏覽器快取
1. 在瀏覽器按 `Ctrl+Shift+Delete`
2. 或按 `Ctrl+Shift+R` 強制重新載入頁面
3. 或開啟無痕模式視窗測試

### 步驟 2: 重新登入
1. 開啟瀏覽器開發者工具 (F12)
2. 切換到 Console 分頁
3. 清空控制台 (按 Ctrl+L 或點擊清除圖示)
4. 重新登入系統

### 步驟 3: 檢查 Console 輸出
應該看到以下除錯訊息:

```
🔍 Login API Response: {access_token: "...", token_type: "bearer", txn_token: "..."}
🔍 txn_token in response: <token_string>
✅ Saved access_token
✅ Saved txn_token: <token_string>
🔍 localStorage access_token: <token_string>
🔍 localStorage txn_token: <token_string>
🔄 Calling AuthContext.login()...
✅ AuthContext.login() completed
🔍 After login - localStorage txn_token: <token_string>  // ✅ 應該有值,不是 null
```

**關鍵檢查點:**
- 最後一行 `After login - localStorage txn_token:` 應該顯示 token 字串,而不是 `null`

### 步驟 4: 驗證 localStorage
在 Console 執行以下指令:

```javascript
console.log('access_token:', localStorage.getItem('access_token'));
console.log('txn_token:', localStorage.getItem('txn_token'));
```

**預期結果:**
- `access_token` 應該有值
- `txn_token` 應該有值 (不是 null)

### 步驟 5: 檢查 Network 請求
1. 切換到 Network 分頁
2. 重新整理頁面或執行一個 API 請求
3. 選擇任一 API 請求
4. 查看 Request Headers

**預期結果:**
應該看到以下 headers:
```
Authorization: Bearer <access_token>
X-Txn-Token: <txn_token>
```

### 步驟 6: 測試 Users 頁面
1. 導航到使用者設定頁面
2. 觀察是否成功載入使用者列表
3. 檢查 Console 是否有錯誤

**預期結果:**
- 使用者列表成功載入
- 沒有 401 或 403 錯誤
- Console 沒有 "等待交易令牌..." 訊息

## 成功標準

✅ **修復成功** 如果:
1. Console 顯示所有除錯訊息 (包括 🔍、✅、🔄 圖示)
2. `localStorage.getItem('txn_token')` 回傳 token 字串 (不是 null)
3. API 請求自動帶上 `X-Txn-Token` header
4. Users 頁面成功載入使用者列表

❌ **仍有問題** 如果:
1. Console 沒有顯示除錯訊息 → 可能需要清除瀏覽器快取
2. `txn_token` 仍然是 null → 檢查後端是否正常運作
3. API 請求沒有帶 `X-Txn-Token` header → 檢查 axios.ts 配置

## 後續測試

### 測試 Transaction Token 功能
1. 導航到使用者設定頁面
2. 點擊新增使用者
3. 觀察是否自動取得 transaction token
4. 填寫表單並儲存
5. 確認操作成功

### 測試 Token 延長功能
1. 在編輯模式等待約 25 分鐘
2. 應該出現 "是否延長令牌" 對話框
3. 點擊延長
4. 確認可以繼續操作

## Redis 驗證

在 Redis CLI 執行以下指令:

```bash
# 查看所有 keys
redis-cli KEYS "*"

# 應該看到:
# - session:<session_id>
# - txn_token:<token_string>
# - session_token_mapping:<session_id>
```

## 相關檔案

修改的檔案:
- `Develop/frontend/src/contexts/AuthContext.tsx` (Line 37)

相關檔案:
- `Develop/frontend/src/pages/LoginPage.tsx` (Lines 41-73)
- `Develop/frontend/src/api/authService.ts` (Lines 51-60)
- `Develop/frontend/src/api/axios.ts` (Lines 27-31)
- `Develop/frontend/src/types/index.ts` (Line 35)

## 問題回報

如果驗證後仍有問題,請提供以下資訊:
1. Console 完整輸出截圖
2. Network 分頁的 login API 回應
3. localStorage 內容截圖
4. Redis KEYS 輸出
