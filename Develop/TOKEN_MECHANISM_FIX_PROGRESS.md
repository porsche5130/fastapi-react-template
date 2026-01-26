# 交易令牌機制修正進度報告

## 修正目標

根據**交易安全機制設計 v2.0**,所有 API 端點都需要加上正確的 Token 驗證:

1. **GET** → `require_txn_token(func_code, "read")`
2. **POST** → `require_txn_token(func_code, "create")`
3. **PUT** → `require_txn_token(func_code, "update")`
4. **DELETE** → `require_txn_token(func_code, "delete", one_time_use=True)`

## 修正進度

### ✅ 已完成 (4 個檔案, 25 個端點)

| 檔案 | func_code | 端點數 | 狀態 |
|------|-----------|--------|------|
| userrole.py | user_roles | 5 | ✅ 完成 (範例檔案) |
| user.py | users | 8 | ✅ 完成 |
| organization.py | organizations | 5 | ✅ 完成 |
| systemfunction.py | system_functions | 7 | ✅ 完成 |

**修正內容:**
- 加入 `from app.routes.transaction import require_txn_token`
- 所有端點加上 `_token: None = Depends(require_txn_token(...))`
- 移除手動的 `check_permission()` 呼叫 (保留用於資料層級安全控制的除外)
- 更新 docstring 說明需要的權限
- DELETE 端點加上 `one_time_use=True`

### ⏳ 進行中 (8 個檔案, 44 個端點)

| 檔案 | func_code | 端點數 | 狀態 |
|------|-----------|--------|------|
| roleright.py | role_rights | 4 | ⏳ 待修正 |
| systemcode.py | system_codes | 6 | ⏳ 待修正 |
| userlog.py | user_logs | 5 | ⏳ 待修正 |
| systemnotification.py | system_notifications | 7 | ⏳ 待修正 |
| sysprofile.py | sys_profile | 2 | ⏳ 待修正 |
| fileattachment.py | file_attachments | 8 | ⏳ 待修正 |
| numberingrule.py | numbering_rules | 9 | ⏳ 待修正 |
| home.py | dashboard | 3 | ⏳ 待修正 |

## 特殊案例處理

### 1. check_permission() 保留的情況

在以下情況,`check_permission()` 仍然保留:

- **資料層級安全控制**: 判斷使用者是否可以查看/修改跨組織的資料
  - 例如: `user.py` 中判斷使用者是否可以查看所有組織的使用者
  - 例如: `organization.py` 中判斷使用者是否可以管理其他組織

這與 Token 驗證是不同的:
- **Token 驗證**: 檢查使用者是否有該功能的存取權 (功能級別)
- **資料層級控制**: 檢查使用者可以存取哪些資料範圍 (資料級別)

### 2. 特殊端點

- `/me` (my_profile) - 使用 `my_profile` func_code
- `/{user_id}/change-password` (change_password) - 使用 `change_password` func_code

這兩個端點已正確實作 Token 機制。

## 核心概念

### Token 機制 v2.0

**有使用權 = 需要建立 Token**

1. Token 包含使用者對該功能的**所有權限資訊**
2. 前端根據權限決定顯示哪些按鈕
3. 所有操作 (包括 GET) 都需要 Token
4. Token 驗證時直接從 Redis 讀取權限,不需要再查資料庫

### 三層安全防護

1. **Session Token** (Bearer Token) - 驗證身份
2. **Transaction Token** (X-Txn-Token) - 驗證功能存取權
3. **Permission Check** (Token 內權限) - 驗證操作權限

## 下一步

1. 繼續修正剩餘 8 個檔案
2. 測試所有端點的 Token 驗證
3. 確認錯誤處理正確 (401, 403)
4. 文件更新完成

---

**最後更新**: 2026-01-26
**負責人**: 開發團隊
