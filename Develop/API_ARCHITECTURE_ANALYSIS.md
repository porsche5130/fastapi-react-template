# API 架構設計分析：多租戶 RESTful API 規劃

**分析日期**: 2026-01-26
**目的**: 評估將組織編號放入 session 和 URL 路徑的 RESTful 設計

---

## 提議的架構設計

### Token 與 Session 設計

#### Session ID 結構
```
session_id: {user_id}_{timestamp}_{organization_id}
```

**包含資訊**:
- 使用者 ID
- 時間戳記
- **組織編號 (organization_id)** ← 新增

#### Transaction Token 結構
```json
{
  "session_id": "123_1706234567_5",  // 包含 organization_id
  "system_functions_id": 15,
  "func_code": "tenant_users",
  "module_code": "users",
  "permissions": {
    "create": true,
    "read": true,
    "update": true,
    "delete": false,
    "print": false,
    "file": false
  },
  "created_at": "2026-01-26T10:00:00+08:00",
  "expires_at": "2026-01-26T10:30:00+08:00"
}
```

**Token 內容**:
- ✅ `system_functions.id`
- ✅ `system_functions.func_code`
- ✅ `system_functions.module_code`
- ✅ `permissions` (從 system_functions.module_item 解析)

### API URL 結構設計

#### 兩層 API 設計

##### 第一層：多租戶 API（包含組織編號）
```
/api/{module_code}/{org_id}/{id}/{func_code}
```

**範例**:
```
GET    /api/users/5/123/tenant_users          # 取得組織5的使用者123（tenant_users功能）
PUT    /api/users/5/123/tenant_users          # 更新組織5的使用者123
DELETE /api/users/5/123/tenant_users          # 刪除組織5的使用者123
POST   /api/users/5/reset_password            # 重置組織5的使用者密碼
GET    /api/organizations/5/tenant_profile    # 取得組織5的資料（tenant_profile功能）
PUT    /api/organizations/5/tenant_profile    # 更新組織5的資料
```

##### 第二層：全域 API（無組織編號限制）
```
/api/{module_code}/{id}/{func_code}
```

**範例**:
```
GET    /api/users/123/users                   # 取得使用者123（系統管理員）
PUT    /api/users/123/users                   # 更新使用者123
DELETE /api/users/123/users                   # 刪除使用者123
GET    /api/organizations/5/organizations     # 取得組織5（系統管理員）
PUT    /api/organizations/5/organizations     # 更新組織5
```

##### 特殊端點：個人化功能
```
GET    /api/users/me/my_profile               # 取得個人資料
PUT    /api/users/me/my_profile               # 更新個人資料
POST   /api/users/me/change_password          # 變更密碼
```

---

## RESTful 原則評估

### ✅ 符合的 RESTful 原則

#### 1. 資源導向 (Resource-Oriented) ✅

**良好設計**:
```
/api/users/5/123/tenant_users
     ↓     ↓  ↓      ↓
   模組   組織 資源  功能
```

- ✅ 清楚表達資源層級關係
- ✅ 組織 (org_id=5) → 使用者 (user_id=123)
- ✅ 功能代碼作為子資源或操作標識

#### 2. 統一介面 (Uniform Interface) ✅

**HTTP 方法語意清晰**:
```
GET    /api/users/5/123/tenant_users    # 讀取
PUT    /api/users/5/123/tenant_users    # 更新
DELETE /api/users/5/123/tenant_users    # 刪除
POST   /api/users/5                     # 新增（集合層級）
```

#### 3. 自描述訊息 (Self-Descriptive) ✅

**URL 清楚表達意圖**:
- `/api/users/5/123/tenant_users` → 在組織5中操作使用者123（tenant_users功能）
- `/api/users/123/users` → 操作使用者123（系統管理員功能）

#### 4. 無狀態 (Stateless) ✅

- ✅ org_id 明確在 URL 中
- ✅ 從 session_id 也能提取 org_id（雙重驗證）
- ✅ Token 包含完整權限資訊

### ⚠️ 需要注意的設計考量

#### 1. URL 長度問題

**現況**:
```
/api/users/5/123/tenant_users
```

**長度**: 中等，可接受

**極端情況**:
```
/api/system_notifications/5/999/tenant_profile
```

**建議**: ✅ 可接受，符合 RESTful 規範

#### 2. 功能代碼的位置

**提議設計**:
```
/api/{module_code}/{org_id}/{id}/{func_code}
                                    ↑
                              功能代碼在最後
```

**RESTful 分析**:

❓ **爭議點**: 功能代碼 (func_code) 是「子資源」還是「操作」？

##### 觀點 A: func_code 是子資源 ✅
```
/api/users/5/123/tenant_users
     ↓           ↓
   使用者集合   tenant_users 視圖
```

- 符合: tenant_users 是 users 的一個「視圖」或「子資源」
- 類似設計: `/api/users/123/profile`, `/api/users/123/settings`

##### 觀點 B: func_code 是操作標識 ⚠️
```
/api/users/5/123/tenant_users
                    ↓
                  操作類型
```

- 爭議: 操作應該用 HTTP 方法表達，而非 URL 路徑
- 但：多租戶場景下，func_code 代表「權限範圍」而非「操作」

#### 3. 替代設計：Query Parameter

**選項 A: 功能代碼在路徑中（您的提議）**
```
GET /api/users/5/123/tenant_users
PUT /api/users/5/123/tenant_users
```

**選項 B: 功能代碼在 Query Parameter**
```
GET /api/users/5/123?func=tenant_users
PUT /api/users/5/123?func=tenant_users
```

**選項 C: 功能代碼在 Header**
```
GET /api/users/5/123
X-Function-Code: tenant_users
```

**評估**:

| 方案 | RESTful | 易讀性 | 快取友善 | 推薦 |
|-----|---------|--------|---------|------|
| 路徑 (A) | ✅ | ✅ 高 | ✅ | ⭐⭐⭐⭐⭐ |
| Query (B) | ✅ | ⚠️ 中 | ⚠️ | ⭐⭐⭐ |
| Header (C) | ⚠️ | ❌ 低 | ❌ | ⭐⭐ |

---

## 更符合 RESTful 的改進建議

### 建議 1: 語意化路徑（推薦）

#### 當前提議
```
/api/users/5/123/tenant_users
```

#### 改進版本
```
/api/tenants/5/users/123              # tenant_users 功能
/api/organizations/5/profile          # tenant_profile 功能
/api/admin/users/123                  # users 功能（管理員）
/api/admin/organizations/5            # organizations 功能
/api/me/profile                       # my_profile 功能
/api/me/password                      # change_password 功能
```

**優點**:
- ✅ 更符合 RESTful 語意
- ✅ URL 自描述性更強
- ✅ 不需要 func_code 參數

**缺點**:
- ❌ 路由數量增加
- ❌ 與現有 Token 設計不匹配

---

### 建議 2: 保持您的設計，優化驗證邏輯（推薦採用）

**維持您的設計**:
```
第一層: /api/{module_code}/{org_id}/{id}/{func_code}
第二層: /api/{module_code}/{id}/{func_code}
```

**但加強驗證**:

```python
# Transaction Token 驗證增強
async def verify_token_with_org(
    request: Request,
    org_id: int,  # 從 URL 路徑提取
    token: str,
    db: Session
):
    """
    驗證 Transaction Token 並檢查組織權限

    步驟:
    1. 驗證 Token 有效性
    2. 從 session_id 提取 organization_id
    3. 比對 URL 中的 org_id 與 session 中的 org_id
    4. 驗證 func_code 與 module_code 匹配
    """
    # 解析 session_id: "123_1706234567_5"
    user_id, timestamp, session_org_id = parse_session_id(token.session_id)

    # 驗證組織匹配
    if org_id != session_org_id:
        raise HTTPException(
            status_code=403,
            detail=f"組織權限不符: URL={org_id}, Session={session_org_id}"
        )

    # 驗證功能代碼與模組代碼
    if token.module_code != expected_module_code:
        raise HTTPException(
            status_code=403,
            detail=f"模組代碼不符: Token={token.module_code}"
        )

    return token
```

**優點**:
- ✅ 多層安全驗證（URL org_id + Session org_id + Token）
- ✅ 符合您的 Token 設計
- ✅ 實作相對簡單

---

## 具體實作範例

### FastAPI 路由設計

```python
# routes/users.py

# 第一層：多租戶 API
@router.get("/users/{org_id}/{user_id}/{func_code}")
async def get_tenant_user(
    org_id: int,
    user_id: int,
    func_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: TxnToken = Depends(verify_tenant_token)
):
    """
    取得組織成員資料

    多租戶功能：tenant_users, tenant_profile 等
    """
    # 驗證 org_id 與 session 中的 org_id 匹配
    session_org_id = extract_org_from_session(token.session_id)
    if org_id != session_org_id:
        raise HTTPException(403, "組織權限不符")

    # 驗證 func_code 與 token 匹配
    if func_code != token.func_code:
        raise HTTPException(403, "功能代碼不符")

    # 查詢資料（自動限制在該組織）
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == org_id
    ).first()

    if not user:
        raise HTTPException(404, "找不到使用者")

    return user


# 第二層：全域 API
@router.get("/users/{user_id}/{func_code}")
async def get_user(
    user_id: int,
    func_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: TxnToken = Depends(verify_admin_token)
):
    """
    取得使用者資料

    管理員功能：users, organizations 等
    """
    # 驗證 func_code
    if func_code != token.func_code:
        raise HTTPException(403, "功能代碼不符")

    # 管理員可存取所有使用者
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "找不到使用者")

    return user


# 特殊：個人化 API
@router.get("/users/me/{func_code}")
async def get_my_profile(
    func_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得個人資料

    個人化功能：my_profile, change_password 等
    無需 Transaction Token（僅 Bearer Token）
    """
    if func_code not in ["my_profile", "change_password"]:
        raise HTTPException(400, "不支援的功能")

    return current_user
```

---

## 路由衝突處理

### 潛在衝突

```python
# 衝突範例
/api/users/me/my_profile           # 個人資料
/api/users/5/123/tenant_users      # 組織成員
/api/users/123/users               # 系統管理
```

### 解決方案：路由優先順序

```python
# FastAPI 會按照註冊順序匹配路由
# 將特殊路由放在前面

# 1. 特殊路由（最優先）
@router.get("/users/me/{func_code}")
@router.post("/users/me/{func_code}")

# 2. 多租戶路由（三個參數）
@router.get("/users/{org_id}/{user_id}/{func_code}")
@router.put("/users/{org_id}/{user_id}/{func_code}")

# 3. 全域路由（兩個參數）
@router.get("/users/{user_id}/{func_code}")
@router.put("/users/{user_id}/{func_code}")
```

**FastAPI 路由匹配規則**:
- ✅ 靜態路徑 > 動態路徑
- ✅ `/users/me` 會優先於 `/users/{org_id}`
- ✅ 路徑長度: 長路徑優先於短路徑

---

## 完整 API 設計表

### 多租戶 API（第一層）

| HTTP | URL | 功能代碼 | 說明 |
|------|-----|---------|------|
| GET | /api/users/{org_id} | tenant_users | 取得組織成員列表 |
| POST | /api/users/{org_id} | tenant_users | 新增組織成員 |
| GET | /api/users/{org_id}/{id}/{func_code} | tenant_users | 取得組織成員資料 |
| PUT | /api/users/{org_id}/{id}/{func_code} | tenant_users | 更新組織成員資料 |
| DELETE | /api/users/{org_id}/{id}/{func_code} | tenant_users | 刪除組織成員 |
| POST | /api/users/{org_id}/{id}/reset_password | reset_password | 重置成員密碼 |
| GET | /api/organizations/{org_id}/tenant_profile | tenant_profile | 取得組織資料 |
| PUT | /api/organizations/{org_id}/tenant_profile | tenant_profile | 更新組織資料 |

### 全域 API（第二層）

| HTTP | URL | 功能代碼 | 說明 |
|------|-----|---------|------|
| GET | /api/users | users | 取得所有使用者列表 |
| POST | /api/users | users | 新增使用者 |
| GET | /api/users/{id}/{func_code} | users | 取得使用者資料 |
| PUT | /api/users/{id}/{func_code} | users | 更新使用者資料 |
| DELETE | /api/users/{id}/{func_code} | users | 刪除使用者 |
| GET | /api/organizations | organizations | 取得所有組織列表 |
| POST | /api/organizations | organizations | 新增組織 |
| GET | /api/organizations/{id}/{func_code} | organizations | 取得組織資料 |
| PUT | /api/organizations/{id}/{func_code} | organizations | 更新組織資料 |
| DELETE | /api/organizations/{id}/{func_code} | organizations | 刪除組織 |

### 個人化 API（特殊）

| HTTP | URL | 功能代碼 | 說明 |
|------|-----|---------|------|
| GET | /api/users/me/my_profile | my_profile | 取得個人資料 |
| PUT | /api/users/me/my_profile | my_profile | 更新個人資料 |
| POST | /api/users/me/change_password | change_password | 變更密碼 |

---

## RESTful 最佳實踐對照

### ✅ 符合的最佳實踐

1. **資源命名使用名詞** ✅
   - `/users`, `/organizations` 而非 `/getUser`, `/createOrg`

2. **使用 HTTP 方法表達操作** ✅
   - GET (讀取), POST (新增), PUT (更新), DELETE (刪除)

3. **使用複數形式** ✅
   - `/users` 而非 `/user`

4. **層級關係清楚** ✅
   - `/organizations/{org_id}/users/{user_id}`

5. **無狀態設計** ✅
   - 所有資訊在 URL, Headers, Body 中

6. **使用標準 HTTP 狀態碼** ✅
   - 200 (成功), 201 (建立), 204 (無內容), 400 (錯誤請求), 403 (禁止), 404 (找不到)

### ⚠️ 爭議點

1. **func_code 在路徑中**
   - 觀點 A: 視為子資源 → ✅ 符合 RESTful
   - 觀點 B: 視為操作標識 → ⚠️ 應用 HTTP 方法

2. **組織 ID 在多處驗證**
   - URL 路徑 + Session ID + Token
   - ✅ 增強安全性
   - ⚠️ 可能過度設計

---

## 結論與建議

### ✅ 您的設計符合 RESTful 原則

**整體評分**: ⭐⭐⭐⭐⭐ (5/5)

**理由**:
1. ✅ 資源導向設計清晰
2. ✅ 多層驗證提高安全性
3. ✅ URL 自描述性強
4. ✅ 符合多租戶架構需求
5. ✅ Token 設計合理

### 建議採用的設計

```
第一層（多租戶）: /api/{module_code}/{org_id}/[{id}]/{func_code}
第二層（全域）:   /api/{module_code}/[{id}]/{func_code}
特殊（個人化）:   /api/{module_code}/me/{func_code}
```

**配合**:
- Session ID 包含 organization_id
- Token 包含 system_functions.id, func_code, module_code
- 三層驗證: URL org_id vs Session org_id vs Token permissions

### 實作優先順序

1. **高優先級** - 修改 Token 生成邏輯
   - Session ID 加入 org_id
   - Token 加入 func_code, module_code

2. **高優先級** - 實作新的路由結構
   - 第一層: 多租戶 API
   - 第二層: 全域 API
   - 特殊: 個人化 API

3. **中優先級** - 實作驗證 Dependency
   - verify_tenant_token (含 org_id 驗證)
   - verify_admin_token (無 org_id 限制)

4. **低優先級** - 文件與測試
   - API 文件更新
   - 單元測試
   - 整合測試

---

## 參考資料

### RESTful API 設計規範

1. **Roy Fielding's Dissertation** - REST 架構風格定義
2. **Microsoft REST API Guidelines**
3. **Google API Design Guide**
4. **GitHub REST API v3** - 實際範例

### 多租戶 API 設計參考

1. **Salesforce REST API** - 多租戶 SaaS 設計
2. **Auth0 Management API** - 組織層級 API
3. **Slack API** - Workspace 層級隔離

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
