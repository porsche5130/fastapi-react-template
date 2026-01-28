# 功能開發 Prompt 範本

## 使用說明

將此範本複製後，填入具體需求，即可讓 AI 一次完成所有開發工作。

---

## Prompt 範本

```
請完成以下功能開發，包含資料庫、後端、前端的完整實作：

## 功能名稱
[功能中文名稱] / [Function Code]

例如：個人資料變更 / my_profile

## 功能說明
[詳細說明此功能的用途、使用者情境]

例如：
- 使用者可以查看和修改自己的個人資料
- 可修改欄位：姓名、部門、職稱、電話
- 不可修改欄位：帳號、組織、角色、啟用狀態

## 資料庫需求

### 1. 系統功能註冊
- func_code: [功能代碼]
- func_cname: [中文名稱]
- func_ename: [英文名稱]
- module_code: [模組代碼，例如：users, organizations]
- module_item: [模組項目，JSON 格式，例如：["Read", "Update"]]
- func_type: [功能類型，1=選單, 2=功能]
- upper_func_id: [上層功能 ID，0=根目錄]
- is_mana: [是否為管理功能，true/false]

### 2. 權限設定
- 哪些角色需要此功能？[all / 指定角色]
- 預設權限：[read, create, update, delete, print, file 各為 true/false]

### 3. 資料表變更（如果需要）
- 新增資料表：[表名及欄位]
- 修改現有資料表：[表名及變更內容]

## 後端 API 需求

### API 端點
列出所有需要的 API 端點：

1. **[HTTP Method] [Path]**
   - 說明：[端點功能說明]
   - 需要交易令牌：[是/否]
   - 需要權限：[read/create/update/delete/print/file]
   - 請求參數：[參數說明]
   - 回應格式：[回應說明]

例如：
1. **GET /api/users/me**
   - 說明：取得當前使用者個人資料
   - 需要交易令牌：否（只讀取）
   - 需要權限：read
   - 請求參數：無
   - 回應格式：UserDetail

2. **PUT /api/users/me**
   - 說明：更新當前使用者個人資料
   - 需要交易令牌：是
   - 需要權限：update
   - 請求參數：UserDetailUpdate (username, department, job_title, phone)
   - 回應格式：UserDetail

### 資料驗證規則
- [欄位名稱]: [驗證規則]

例如：
- username: 必填，最大長度 200
- department: 選填，最大長度 200
- phone: 選填，最大長度 200

### 安全限制
列出此功能的安全限制：

例如：
- 使用者只能修改自己的資料
- 不可修改帳號、組織、角色
- 所有更新需記錄使用者日誌

### 使用者日誌
- 需要記錄的操作：[read/create/update/delete]
- 記錄內容：[原始資料/新資料/差異]

## 前端需求

### 頁面資訊
- 頁面路徑：[例如：/my_profile]
- 頁面中文標題：[使用 useFunctionName hook 從 system_functions 取得]
- 頁面類型：[列表頁/表單頁/詳細頁]

### UI 元件
描述頁面需要的 UI 元件：

例如：
1. 表單欄位：
   - 帳號（唯讀）
   - 組織（唯讀）
   - 使用者名稱（可編輯）
   - 部門（可編輯）
   - 職稱（可編輯）
   - 電話（可編輯）

2. 按鈕：
   - 編輯按鈕（需要 update 權限）
   - 儲存按鈕（編輯模式）
   - 取消按鈕（編輯模式）
   - 返回按鈕

### 互動流程
描述使用者操作流程：

例如：
1. 進入頁面 → 載入個人資料 → 顯示唯讀模式
2. 點擊編輯 → 請求交易令牌 → 進入編輯模式
3. 修改欄位 → 點擊儲存 → 呼叫 API → 顯示成功訊息
4. 令牌即將過期 → 顯示延長對話框 → 使用者選擇延長或取消

### 權限控制
- 讀取權限：[誰可以看到此頁面]
- 編輯權限：[誰可以編輯]
- UI 元件顯示規則：[根據權限顯示/隱藏哪些元件]

### 多語言支援
需要的翻譯 key（zh-TW / en）：

例如：
```json
{
  "myProfile": {
    "accountInfo": "帳號資訊 / Account Information",
    "personalInfo": "個人資訊 / Personal Information",
    "username": "使用者名稱 / Username",
    "updateSuccess": "更新成功 / Update successful"
  }
}
```

## 開發要求

### 必須遵守的規範
1. ✅ 使用現有的 Hooks：
   - useTransactionToken: 交易令牌管理
   - usePermission: 權限檢查
   - useFunctionName: 取得功能名稱
   - useAuth: 使用者資訊

2. ✅ 資料安全：
   - 所有寫入操作需要交易令牌
   - 使用 require_txn_token 依賴項驗證
   - 支援多 func_code（如果共用 API）

3. ✅ 使用者日誌：
   - 使用 logRead(), logUpdate(), logCreate(), logDelete()
   - 記錄原始資料與更新資料
   - 錯誤也要記錄

4. ✅ 錯誤處理：
   - 後端：HTTPException 回傳明確錯誤訊息
   - 前端：try-catch 顯示使用者友善訊息

5. ✅ 時區：
   - 統一使用台北時區 (UTC+8)
   - 使用 taipei_tz 和 get_taipei_now()

### 檔案結構
請依照以下結構建立/修改檔案：

**資料庫遷移：**
- `Develop/backend/migrations/register_[func_code]_function.sql`
- `Develop/backend/migrations/grant_[func_code]_permissions.sql`
- `Develop/backend/run_[func_code]_migration.py`

**後端：**
- `Develop/backend/app/routes/[module].py` (修改現有或新增)
- `Develop/backend/app/schemas/[module].py` (如需要)
- `Develop/backend/app/models/[module].py` (如需要)
- `Develop/backend/app/services/[module]_service.py` (如需要)

**前端：**
- `Develop/frontend/src/pages/[PageName]Page.tsx`
- `Develop/frontend/src/services/[module]Service.ts` (修改現有或新增)
- `Develop/frontend/src/types/[module].ts` (如需要)
- `Develop/frontend/src/styles/[PageName]Page.css`
- `Develop/frontend/src/App.tsx` (新增路由)
- `Develop/frontend/src/locales/zh-TW/translation.json` (新增翻譯)
- `Develop/frontend/src/locales/en/translation.json` (新增翻譯)

**測試：**
- `Develop/backend/test_[func_code].py` (功能測試)

**文件：**
- `Develop/[FEATURE_NAME]_IMPLEMENTATION.md` (實作說明)

## 測試需求

### 後端測試項目
列出需要測試的項目：

例如：
- [ ] GET /api/users/me 回傳當前使用者資料
- [ ] PUT /api/users/me 成功更新允許的欄位
- [ ] PUT /api/users/me 拒絕修改帳號
- [ ] PUT /api/users/me 拒絕修改組織
- [ ] 沒有交易令牌時回傳 401
- [ ] 使用者日誌正確記錄

### 前端測試項目
列出需要測試的項目：

例如：
- [ ] 頁面載入顯示個人資料
- [ ] 唯讀欄位無法編輯
- [ ] 編輯模式啟動時請求交易令牌
- [ ] 儲存成功顯示成功訊息
- [ ] 沒有權限時隱藏編輯按鈕
- [ ] 令牌延長對話框正常運作

### 整合測試
- [ ] 完整流程測試（進入頁面 → 編輯 → 儲存 → 驗證）
- [ ] 權限測試（不同角色的存取限制）
- [ ] 交易令牌測試（延長、過期、撤銷）
- [ ] 多語言測試（zh-TW / en 切換）

## 特殊需求
[任何特殊的業務邏輯、驗證規則、或例外情況]

例如：
- 密碼欄位需要加密儲存
- 特定欄位需要格式驗證（email, phone）
- 某些操作需要額外的確認對話框

## 完成標準
完成以下所有項目才算完成：

- [ ] 資料庫遷移腳本建立並執行成功
- [ ] 系統功能已註冊到 system_functions
- [ ] 權限已授予指定角色
- [ ] 後端 API 端點實作完成
- [ ] 前端頁面實作完成
- [ ] 路由已新增到 App.tsx
- [ ] 多語言翻譯已新增
- [ ] 所有測試項目通過
- [ ] 使用者日誌正確記錄
- [ ] 文件已建立
- [ ] 程式碼已遵守專案規範
```

---

## 使用範例

### 範例 1：個人資料變更功能

```
請完成以下功能開發，包含資料庫、後端、前端的完整實作：

## 功能名稱
個人資料變更 / my_profile

## 功能說明
- 使用者可以查看和修改自己的個人資料
- 可修改欄位：使用者名稱、部門、職稱、電話
- 不可修改欄位：帳號、組織、角色、啟用狀態
- 從頁首下拉選單的「個人資料變更」進入

## 資料庫需求

### 1. 系統功能註冊
- func_code: my_profile
- func_cname: 個人資料
- func_ename: My Profile
- module_code: my_profile
- module_item: ["Read", "Update"]
- func_type: 2 (功能)
- upper_func_id: 0 (不在選單中)
- is_mana: false

### 2. 權限設定
- 所有啟用的角色都需要此功能
- 預設權限：read=true, update=true, 其他=false

### 3. 資料表變更
無需新增或修改資料表，使用現有 users 表

## 後端 API 需求

### API 端點

1. **GET /api/users/me**
   - 說明：取得當前使用者個人資料
   - 需要交易令牌：否
   - 需要權限：read
   - 請求參數：無
   - 回應格式：UserDetail

2. **PUT /api/users/me**
   - 說明：更新當前使用者個人資料
   - 需要交易令牌：是
   - 需要權限：update
   - 請求參數：UserDetailUpdate (username, department, job_title, phone)
   - 回應格式：UserDetail

### 資料驗證規則
- username: 必填，最大長度 200
- department: 選填，最大長度 200
- job_title: 選填，最大長度 200
- phone: 選填，最大長度 200

### 安全限制
- 使用者只能查看和修改自己的資料
- 不可修改：account, organization_id, user_role, is_active, password
- 所有更新操作需要交易令牌
- 更新需記錄使用者日誌

### 使用者日誌
- 需要記錄的操作：read, update
- 記錄內容：原始資料與更新後資料的差異

## 前端需求

### 頁面資訊
- 頁面路徑：/my_profile
- 頁面中文標題：使用 useFunctionName('my_profile')
- 頁面類型：表單頁

### UI 元件

1. 唯讀資訊區：
   - 帳號（唯讀，灰色背景）
   - 組織（唯讀，灰色背景）

2. 可編輯欄位（編輯模式才能修改）：
   - 使用者名稱（必填）
   - 部門
   - 職稱
   - 電話

3. 按鈕：
   - 返回按鈕（檢視模式）
   - 編輯按鈕（檢視模式，需要 update 權限）
   - 取消按鈕（編輯模式）
   - 儲存按鈕（編輯模式，需要交易令牌）

### 互動流程
1. 進入頁面 → 呼叫 GET /api/users/me → 顯示資料（檢視模式）
2. 點擊編輯 → 請求交易令牌 → 進入編輯模式
3. 修改欄位 → 點擊儲存 → 呼叫 PUT /api/users/me → 顯示成功訊息 → 回到檢視模式
4. 點擊取消 → 還原資料 → 回到檢視模式
5. 令牌即將過期 → 顯示 TransactionExtendDialog → 使用者選擇延長或取消

### 權限控制
- 讀取權限：所有登入使用者都可以看到自己的資料
- 編輯權限：需要 my_profile.update 權限
- 沒有 update 權限時不顯示編輯按鈕

### 多語言支援
```json
{
  "myProfile": {
    "accountInfo": "帳號資訊 / Account Information",
    "personalInfo": "個人資訊 / Personal Information",
    "account": "帳號 / Account",
    "accountNote": "帳號無法變更 / Account cannot be changed",
    "organization": "組織 / Organization",
    "organizationNote": "組織無法變更 / Organization cannot be changed",
    "username": "使用者名稱 / Username",
    "department": "部門 / Department",
    "jobTitle": "職稱 / Job Title",
    "phone": "電話 / Phone",
    "loadError": "載入個人資料失敗 / Failed to load profile",
    "updateSuccess": "個人資料更新成功 / Profile updated successfully",
    "updateError": "更新個人資料失敗 / Failed to update profile",
    "noToken": "請先取得交易令牌 / Please obtain transaction token first"
  }
}
```

## 開發要求
[使用範本中的標準要求]

## 測試需求

### 後端測試項目
- [ ] GET /api/users/me 回傳當前使用者資料
- [ ] PUT /api/users/me 成功更新 username, department, job_title, phone
- [ ] PUT /api/users/me 拒絕修改 account
- [ ] PUT /api/users/me 拒絕修改 organization_id
- [ ] PUT /api/users/me 拒絕修改 user_role
- [ ] PUT /api/users/me 拒絕修改 is_active
- [ ] 沒有交易令牌時回傳 401
- [ ] 交易令牌無效時回傳 401
- [ ] 使用者日誌正確記錄查看和更新操作

### 前端測試項目
- [ ] 頁面載入顯示個人資料
- [ ] 唯讀欄位（帳號、組織）無法編輯
- [ ] 編輯按鈕在有 update 權限時顯示
- [ ] 點擊編輯進入編輯模式並請求交易令牌
- [ ] 可編輯欄位在編輯模式可修改
- [ ] 儲存成功顯示成功訊息
- [ ] 取消按鈕還原修改
- [ ] 沒有 update 權限時不顯示編輯按鈕
- [ ] 令牌延長對話框正常運作
- [ ] 表單驗證正確（必填欄位）
- [ ] 多語言切換正常

### 整合測試
- [ ] 完整流程：進入頁面 → 編輯 → 儲存 → 驗證資料已更新
- [ ] 權限測試：不同角色的使用者都能修改自己的資料
- [ ] 交易令牌測試：延長、過期、撤銷
- [ ] 使用者日誌測試：確認操作被記錄

## 特殊需求
無

## 完成標準
- [ ] 資料庫遷移腳本建立並執行成功
- [ ] my_profile 功能已註冊到 system_functions
- [ ] 所有角色都有 my_profile 的 read 和 update 權限
- [ ] GET /api/users/me 端點實作完成
- [ ] PUT /api/users/me 端點實作完成
- [ ] MyProfilePage.tsx 實作完成
- [ ] 路由已新增到 App.tsx
- [ ] zh-TW 和 en 翻譯已新增
- [ ] MyProfilePage.css 樣式已建立
- [ ] userService.ts 新增相關函數
- [ ] 所有測試項目通過
- [ ] 使用者日誌正確記錄
- [ ] MY_PROFILE_IMPLEMENTATION.md 文件已建立
```

---

## 範例 2：密碼重設功能（管理員功能）

```
請完成以下功能開發，包含資料庫、後端、前端的完整實作：

## 功能名稱
密碼重設 / reset_password

## 功能說明
- 管理員可以重設使用者密碼為該使用者所屬組織的代碼
- 重設後密碼 = organizations.org_code
- 此功能在使用者管理頁面中作為操作按鈕
- 需要記錄操作日誌（但不記錄實際密碼）

## 資料庫需求

### 1. 系統功能註冊
- func_code: reset_password
- func_cname: 密碼重設
- func_ename: Reset Password
- module_code: users
- module_item: ["Update"]
- func_type: 2 (功能)
- upper_func_id: users 功能的 ID
- is_mana: true (管理功能)

### 2. 權限設定
- 只有系統管理員角色需要此功能
- 預設權限：update=true, 其他=false

### 3. 資料表變更
無需新增或修改資料表

## 後端 API 需求

### API 端點

1. **POST /api/users/{user_id}/reset-password**
   - 說明：重設使用者密碼為組織代碼
   - 需要交易令牌：是
   - 需要權限：update
   - 請求參數：user_id (路徑參數)
   - 回應格式：204 No Content

### 資料驗證規則
- user_id: 必須存在
- 該使用者必須屬於某個組織
- 該組織必須有 org_code

### 安全限制
- 只有管理員可以執行此操作
- 需要交易令牌
- 密碼使用 bcrypt 加密
- 不可重設自己的密碼（防止意外）
- 使用者日誌不記錄實際密碼

### 使用者日誌
- 需要記錄的操作：update
- 記錄內容：操作者、被重設的使用者 ID、時間戳
- 不記錄：實際密碼

## 前端需求

### 頁面資訊
- 不需要獨立頁面
- 在 UsersPage 中新增「重設密碼」按鈕

### UI 元件

在 UsersPage 的操作欄新增：
- 重設密碼按鈕（需要 reset_password.update 權限）
- 確認對話框（確認是否要重設密碼）

### 互動流程
1. 在使用者列表點擊「重設密碼」按鈕
2. 顯示確認對話框：「確定要將使用者 XXX 的密碼重設為組織代碼嗎？」
3. 確認 → 請求交易令牌（如果沒有）→ 呼叫 API
4. 成功 → 顯示「密碼已重設為組織代碼」
5. 失敗 → 顯示錯誤訊息

### 權限控制
- 只有擁有 reset_password.update 權限的使用者才能看到重設按鈕
- 使用 hasPermission('reset_password', 'update') 檢查

### 多語言支援
```json
{
  "users": {
    "resetPassword": "重設密碼 / Reset Password",
    "resetPasswordConfirm": "確定要將使用者 {username} 的密碼重設為組織代碼嗎？ / Reset password for {username} to organization code?",
    "resetPasswordSuccess": "密碼已重設為組織代碼 / Password reset to organization code",
    "resetPasswordError": "密碼重設失敗 / Failed to reset password"
  }
}
```

## 開發要求
[使用範本中的標準要求]

## 測試需求

### 後端測試項目
- [ ] POST /api/users/{user_id}/reset-password 成功重設密碼
- [ ] 重設後的密碼 = bcrypt(org_code)
- [ ] 沒有交易令牌時回傳 401
- [ ] 使用者不存在時回傳 404
- [ ] 組織沒有 org_code 時回傳 400
- [ ] 使用者日誌正確記錄（不含實際密碼）
- [ ] 不可重設自己的密碼

### 前端測試項目
- [ ] 重設密碼按鈕在有權限時顯示
- [ ] 點擊按鈕顯示確認對話框
- [ ] 確認後呼叫 API
- [ ] 成功顯示成功訊息
- [ ] 失敗顯示錯誤訊息
- [ ] 沒有權限時不顯示按鈕

### 整合測試
- [ ] 完整流程：點擊重設 → 確認 → API 呼叫 → 密碼已變更
- [ ] 權限測試：只有管理員可以執行
- [ ] 驗證重設後可以用新密碼登入

## 特殊需求
- 密碼重設後，使用者應該在下次登入時被提示修改密碼（未來功能，目前不實作）

## 完成標準
- [ ] reset_password 功能已註冊到 system_functions
- [ ] 管理員角色有 reset_password 的 update 權限
- [ ] POST /api/users/{user_id}/reset-password 端點實作完成
- [ ] UsersPage 新增重設密碼按鈕
- [ ] userService.ts 新增 resetUserPassword 函數
- [ ] 確認對話框實作完成
- [ ] zh-TW 和 en 翻譯已新增
- [ ] 所有測試項目通過
- [ ] 使用者日誌正確記錄
- [ ] RESET_PASSWORD_IMPLEMENTATION.md 文件已建立
```

---

## 提示

1. **越詳細越好**：提供的資訊越詳細，AI 的產出越精確
2. **使用檢查清單**：確保不遺漏任何開發項目
3. **明確說明權限**：清楚定義誰可以使用此功能
4. **包含測試需求**：確保功能品質
5. **參考現有程式碼**：如果有類似功能，可以要求參考其實作方式

## 常用補充說明

如果開發過程中需要調整，可以追加說明：

```
請注意：
- 此功能與 XXX 功能類似，請參考其實作方式
- 此功能需要與現有的 YYY API 整合
- 資料表已存在，只需新增權限
- 前端頁面已存在，只需新增按鈕
```
