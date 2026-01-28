# Transaction Token 使用狀況總覽

## 目前已整合交易令牌的功能

以下功能的所有寫入操作（Create, Update, Delete）都已要求交易令牌驗證：

### 1. organizations（組織管理）
**檔案：** `app/routes/organization.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/organizations | 列表查詢 | read | 一般 |
| GET /api/organizations/{id} | 詳細查詢 | read | 一般 |
| POST /api/organizations | 新增組織 | create | 一般 |
| PUT /api/organizations/{id} | 更新組織 | update | 一般 |
| DELETE /api/organizations/{id} | 刪除組織 | delete | **一次性** |

### 2. users（使用者管理）
**檔案：** `app/routes/user.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/users | 列表查詢 | read | 一般 |
| GET /api/users/{id} | 詳細查詢 | read | 一般 |
| POST /api/users | 新增使用者 | create | 一般 |
| PUT /api/users/{id} | 更新使用者 | update | 一般 |
| DELETE /api/users/{id} | 刪除使用者 | delete | **一次性** |
| PUT /api/users/me | 更新個人資料 | update | 一般 (my_profile) |
| POST /api/users/{id}/change-password | 變更密碼 | update | 一般 (change_password) |

### 3. user_roles（使用者角色管理）
**檔案：** `app/routes/userrole.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/user_roles | 列表查詢 | read | 一般 |
| GET /api/user_roles/{id} | 詳細查詢 | read | 一般 |
| POST /api/user_roles | 新增角色 | create | 一般 |
| PUT /api/user_roles/{id} | 更新角色 | update | 一般 |
| DELETE /api/user_roles/{id} | 刪除角色 | delete | **一次性** |

### 4. role_rights（角色權限設定）
**檔案：** `app/routes/roleright.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/role_rights | 列表查詢 | read | 一般 |
| GET /api/role_rights/{id} | 詳細查詢 | read | 一般 |
| PUT /api/role_rights/batch | 批次更新權限 | update | 一般 |
| DELETE /api/role_rights/{id} | 刪除權限 | delete | **一次性** |

### 5. system_codes（系統代碼管理）
**檔案：** `app/routes/systemcode.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/system_codes | 列表查詢 | read | 一般 |
| GET /api/system_codes/{id} | 詳細查詢 | read | 一般 |
| GET /api/system_codes/type/{type_code} | 依類型查詢 | read | 一般 |
| POST /api/system_codes | 新增代碼 | create | 一般 |
| PUT /api/system_codes/{id} | 更新代碼 | update | 一般 |
| DELETE /api/system_codes/{id} | 刪除代碼 | delete | **一次性** |

### 6. system_functions（系統功能管理）
**檔案：** `app/routes/systemfunction.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/system_functions | 列表查詢 | read | 一般 |
| GET /api/system_functions/{id} | 詳細查詢 | read | 一般 |
| GET /api/system_functions/tree | 樹狀結構 | read | 一般 |
| GET /api/system_functions/user/authorized | 授權功能 | read | 一般 |
| POST /api/system_functions | 新增功能 | create | 一般 |
| PUT /api/system_functions/{id} | 更新功能 | update | 一般 |
| DELETE /api/system_functions/{id} | 刪除功能 | delete | **一次性** |

### 7. system_notifications（系統通知管理）
**檔案：** `app/routes/systemnotification.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/system_notifications | 列表查詢 | read | 一般 |
| GET /api/system_notifications/{id} | 詳細查詢 | read | 一般 |
| POST /api/system_notifications | 新增通知 | create | 一般 |
| PUT /api/system_notifications/{id} | 更新通知 | update | 一般 |
| DELETE /api/system_notifications/{id} | 刪除通知 | delete | **一次性** |
| PUT /api/system_notifications/{id}/close | 關閉通知 | update | 一般 |

### 8. sys_profile（系統設定）
**檔案：** `app/routes/sysprofile.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| PUT /api/sys_profiles/update | 更新系統設定 | update | 一般 |

### 9. user_logs（使用者日誌）
**檔案：** `app/routes/userlog.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/user_logs | 列表查詢 | read | 一般 |
| GET /api/user_logs/{id} | 詳細查詢 | read | 一般 |
| GET /api/user_logs/user/{user_id} | 依使用者查詢 | read | 一般 |
| GET /api/user_logs/function/{function_id} | 依功能查詢 | read | 一般 |
| POST /api/user_logs | 新增日誌 | create | 一般 |

### 10. numbering_rules（編號規則設定）
**檔案：** `app/routes/numberingrule.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| GET /api/numbering-rules | 列表查詢 | read | 一般 |
| GET /api/numbering-rules/{id} | 詳細查詢 | read | 一般 |
| POST /api/numbering-rules | 新增規則 | create | 一般 |
| PUT /api/numbering-rules/{id} | 更新規則 | update | 一般 |
| DELETE /api/numbering-rules/{id} | 刪除規則 | delete | 一般 |
| GET /api/numbering-rules/generate/{rule_id} | 產生編號 | read | 一般 |
| PUT /api/numbering-rules/{id}/reset | 重設序號 | update | 一般 |
| GET /api/numbering-rules/preview/{rule_id} | 預覽編號 | read | 一般 |

### 11. file_attachments（檔案附件管理）
**檔案：** `app/routes/fileattachment.py`

| 端點 | 操作 | 權限要求 | Token 類型 |
|------|------|----------|-----------|
| POST /api/file-attachments/upload | 上傳檔案 | create | 一般 |
| POST /api/file-attachments/upload-multiple | 批次上傳 | create | 一般 |
| GET /api/file-attachments | 列表查詢 | read | 一般 |
| GET /api/file-attachments/{id} | 詳細查詢 | read | 一般 |
| PUT /api/file-attachments/{id} | 更新資訊 | update | 一般 |
| DELETE /api/file-attachments/{id} | 刪除檔案 | delete | 一般 |
| DELETE /api/file-attachments/batch | 批次刪除 | delete | 一般 |

## 令牌類型說明

### 一般令牌 (General Token)
- **有效期限：** 30 分鐘
- **可重複使用：** 是
- **自動延長：** 是（每次使用延長 30 分鐘）
- **適用場景：** 一般的 CRUD 操作

### 一次性令牌 (One-time Use Token)
- **有效期限：** 30 分鐘
- **可重複使用：** 否（使用後立即失效）
- **自動延長：** 否
- **適用場景：** 敏感的刪除操作
- **標記：** `one_time_use=True`

**目前使用一次性令牌的操作：**
1. 刪除組織 (DELETE /api/organizations/{id})
2. 刪除使用者 (DELETE /api/users/{id})
3. 刪除角色 (DELETE /api/user_roles/{id})
4. 刪除權限 (DELETE /api/role_rights/{id})
5. 刪除系統代碼 (DELETE /api/system_codes/{id})
6. 刪除系統功能 (DELETE /api/system_functions/{id})
7. 刪除系統通知 (DELETE /api/system_notifications/{id})

## User Logs 記錄內容

**user_logs 表會記錄：**

1. **瀏覽紀錄（Read）：**
   - 功能代碼：透過 `logRead()` 記錄
   - 記錄時機：進入頁面時
   - 記錄內容：查看的資料 ID、時間戳

2. **交易令牌使用紀錄：**
   - 功能代碼：交易令牌驗證時記錄
   - 記錄時機：每次使用令牌執行操作時
   - 記錄內容：
     - 使用者 ID
     - 功能 ID (system_functions.id)
     - 操作類型 (create/read/update/delete)
     - 原始資料（update 時）
     - 更新資料（update 時）
     - 時間戳

3. **操作成功/失敗：**
   - 成功：記錄完整操作資訊
   - 失敗：記錄錯誤訊息

## 交易令牌驗證流程

```
1. 前端進入頁面
   └─> useTransactionToken('func_code', { autoRequest: true })
       └─> POST /api/transaction/request { func_code }
           └─> 後端驗證權限
               ├─> 有權限：建立 Token 並儲存到 Redis
               │   └─> 回傳：{ txn_token, expires_in, permissions }
               └─> 無權限：回傳 403 Forbidden

2. 前端執行操作（如：儲存、更新、刪除）
   └─> POST/PUT/DELETE /api/xxx { data }
       └─> Headers: { 'X-Txn-Token': txn_token }
           └─> 後端 require_txn_token() 驗證
               ├─> Token 有效：執行操作 + 記錄 user_log
               ├─> Token 無效：回傳 401 Unauthorized
               ├─> Token 過期：回傳 401 Unauthorized
               └─> 權限不足：回傳 403 Forbidden

3. 令牌即將過期（剩餘 < 3 分鐘）
   └─> 前端顯示 TransactionExtendDialog
       ├─> 使用者選擇延長
       │   └─> POST /api/transaction/request { func_code }
       │       └─> 延長有效期 30 分鐘
       └─> 使用者選擇取消
           └─> POST /api/transaction/revoke
               └─> 撤銷令牌

4. 離開頁面
   └─> useTransactionToken cleanup
       └─> POST /api/transaction/revoke
           └─> 撤銷令牌
```

## Redis 儲存結構

### Session 資料
```json
{
  "key": "session:{session_id}",
  "value": {
    "user_id": 1,
    "role_ids": [1, 2],
    "organization_id": 5,
    "username": "使用者",
    "account": "user@example.com",
    "authorized_function_ids": [10, 15, 20],
    "created_at": "2026-01-26T18:00:00+08:00",
    "last_access": "2026-01-26T18:30:00+08:00"
  },
  "ttl": 3600
}
```

### Transaction Token 資料
```json
{
  "key": "txn_token:{token_hash}",
  "value": {
    "session_id": "uuid",
    "system_functions_id": 16,
    "func_code": "role_rights",
    "module_code": "role_rights",
    "permissions": {
      "create": true,
      "read": true,
      "update": true,
      "delete": false,
      "print": false,
      "file": false
    },
    "created_at": "2026-01-26T18:30:00+08:00",
    "last_access": "2026-01-26T18:35:00+08:00"
  },
  "ttl": 1800
}
```

### Session-Function Mapping
```json
{
  "key": "session_func_token:{session_id}:{system_functions_id}",
  "value": "{token_hash}",
  "ttl": 1800
}
```

## 安全機制

### 三層驗證

1. **Bearer Token (JWT)**
   - 驗證使用者身份
   - 有效期限：30 分鐘
   - 儲存位置：localStorage

2. **Transaction Token**
   - 驗證功能授權
   - 綁定 session_id
   - 有效期限：30 分鐘
   - 儲存位置：Redis

3. **Permission Check**
   - 驗證具體權限（create/read/update/delete）
   - 從 Token 中讀取
   - 不需再查資料庫

### 資料隔離

- **組織級隔離：** Session 包含 organization_id
- **功能級隔離：** Token 綁定 func_code
- **權限級隔離：** Token 包含 permissions

## 統計資料

- **已整合功能數：** 11 個模組
- **總端點數：** 約 70+ 個
- **需要 Token 的端點：** 約 50+ 個
- **一次性 Token 端點：** 7 個（刪除操作）
- **單純查詢端點：** 約 20+ 個（需 read 權限）
- **寫入操作端點：** 約 30+ 個（需 create/update 權限）

## 未整合的功能

以下功能目前**不需要**交易令牌：

1. **auth (認證)** - 登入/登出不需要
2. **home (首頁)** - 公開資訊
3. **permissions (權限查詢)** - 僅查詢使用者權限，不涉及資料修改
4. **transaction (交易令牌本身)** - 令牌管理 API

## 診斷工具

1. **檢查 Token 是否建立：**
   ```bash
   cd Develop/backend
   python diagnose_token_issue.py
   ```

2. **檢查 API 端點：**
   ```bash
   cd Develop/backend
   python check_transaction_api.py
   ```

3. **列出使用者：**
   ```bash
   cd Develop/backend
   python list_users.py
   ```

## 問題排查

請參考：[TRANSACTION_TOKEN_TROUBLESHOOT.md](./TRANSACTION_TOKEN_TROUBLESHOOT.md)
