# 前後端資料庫整合確認

## 資料庫資料確認

### 1. sys_profile 表 (系統設定)
```sql
SELECT id, is_service, sys_ctitle, sys_etitle, sys_ccopyright, sys_ecopyright, sys_organization
FROM sys_profile WHERE id = 1;
```

**資料庫實際資料：**
- id: 1
- is_service: true
- sys_ctitle: "Paris Agreement Article 6.4 管理系統"
- sys_etitle: "Paris Agreement Article 6.4 Management System"
- sys_ccopyright: "Copyright © 2026 匠耘有限公司"
- sys_ecopyright: "Copyright © 2026 JiangYun Co., Ltd."
- sys_organization: 1

### 2. organizations 表 (組織單位)
```sql
SELECT id, org_code, org_name, org_type, is_active
FROM organizations WHERE id = 1;
```

**資料庫實際資料：**
- id: 1
- org_code: "82871784"
- org_name: "匠耘有限公司"
- org_type: 2 (公司)
- is_active: true

### 3. user_detail 表 (使用者)
```sql
SELECT id, account, username, organization_id, is_active
FROM user_detail WHERE id = 1;
```

**資料庫實際資料：**
- id: 1
- account: "admin@pa64.system"
- username: "系統管理員"
- organization_id: 1
- is_active: true

---

## 後端 API 確認

### 1. 系統設定 API
**端點：** `GET /api/system/profile`

**後端實作：** `W:\P-PA6.4\Develop\backend\app\routes\system.py`
```python
@router.get("/profile", summary="取得系統設定")
async def get_system_profile(db: Session = Depends(get_db)):
    profile = db.query(SysProfile).filter(SysProfile.id == 1).first()
    # 從資料庫查詢並返回
```

**✅ 確認：** 後端從資料庫 `sys_profile` 表讀取資料

**測試結果：**
```bash
curl http://localhost:10181/api/system/profile
```
返回資料庫中的系統設定資料

---

### 2. 使用者認證 API
**端點：** `GET /api/auth/me`

**後端實作：** `W:\P-PA6.4\Develop\backend\app\routes\auth.py`
```python
@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserDetail = Depends(get_current_user)
):
    return current_user  # 從資料庫查詢的使用者資料
```

**後端依賴：** `W:\P-PA6.4\Develop\backend\app\core\deps.py`
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserDetail:
    user = db.query(UserDetail).filter(UserDetail.id == user_id).first()
    # 從資料庫查詢使用者
```

**✅ 確認：** 後端從資料庫 `user_detail` 表讀取使用者資料

---

### 3. 組織單位 API
**端點：** `GET /api/organizations/{organization_id}`

**後端實作：** `W:\P-PA6.4\Develop\backend\app\routes\organization.py`
```python
@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    return organization  # 從資料庫查詢並返回
```

**✅ 確認：** 後端從資料庫 `organizations` 表讀取組織資料

---

## 前端整合確認

### 1. 系統設定讀取
**前端服務：** `W:\P-PA6.4\Develop\frontend\src\api\systemService.ts`
```typescript
getProfile: async (): Promise<SystemProfile> => {
  const response = await axios.get('/api/system/profile');
  return response.data;  // 從後端 API 取得資料庫資料
}
```

**前端 Context：** `W:\P-PA6.4\Develop\frontend\src\contexts\SystemContext.tsx`
```typescript
const loadSystemProfile = async () => {
  const profile = await systemService.getProfile();  // 呼叫後端 API
  setSystemProfile(profile);  // 儲存到 state
  setIsService(profile.is_service);  // 使用資料庫的 is_service 欄位
};
```

**使用位置：**
- `App.tsx`: 檢查 `isService` 決定顯示維護頁面或登入頁面
- `useDocumentTitle` hook: 使用 `sys_ctitle` / `sys_etitle` 設定網頁標題
- `MainLayout.tsx`: 使用 `sys_ccopyright` / `sys_ecopyright` 顯示版權
- `LoginPage.tsx`: 使用 `sys_ccopyright` / `sys_ecopyright` 顯示版權

**✅ 確認：** 前端透過 API 從資料庫讀取系統設定

---

### 2. 使用者資料讀取
**前端服務：** `W:\P-PA6.4\Develop\frontend\src\api\authService.ts`
```typescript
getCurrentUser: async (): Promise<UserProfile> => {
  const response = await axios.get('/api/auth/me');
  return response.data;  // 從後端 API 取得資料庫的使用者資料
}
```

**前端 Context：** `W:\P-PA6.4\Develop\frontend\src\contexts\AuthContext.tsx`
```typescript
const loadUser = async () => {
  const userData = await authService.getCurrentUser();  // 呼叫後端 API
  setUser(userData);  // 儲存到 state
  setIsAuthenticated(true);
};
```

**使用位置：**
- `DashboardPage.tsx`: 顯示 `user.username`, `user.account`, `user.organization_id`
- `MainLayout.tsx`: 顯示使用者資訊
- `Sidebar.tsx`: 根據使用者權限顯示選單

**✅ 確認：** 前端透過 API 從資料庫讀取使用者資料

---

### 3. 組織資料讀取
**前端服務：** `W:\P-PA6.4\Develop\frontend\src\services\organizationService.ts`
```typescript
export const getOrganization = async (organizationId: number): Promise<Organization> => {
  const response = await api.get<Organization>(`/organizations/${organizationId}`);
  return response.data;  // 從後端 API 取得資料庫的組織資料
};
```

**使用位置：** `W:\P-PA6.4\Develop\frontend\src\pages\DashboardPage.tsx`
```typescript
useEffect(() => {
  const fetchOrganization = async () => {
    if (user?.organization_id) {
      const orgData = await getOrganization(user.organization_id);  // 呼叫後端 API
      setOrganization(orgData);  // 儲存到 state
    }
  };
  fetchOrganization();
}, [user?.organization_id]);

// 顯示組織名稱
<p className="card-value">
  {orgLoading ? t('common.loading') : (organization?.org_name || '-')}
</p>
```

**✅ 確認：** 前端透過 API 從資料庫讀取組織資料，顯示 `org_name` 而非 `organization_id`

---

## 資料流向總結

```
資料庫 (PostgreSQL)
    ↓
後端 API (FastAPI + SQLAlchemy)
    ↓
前端服務層 (Axios)
    ↓
前端 Context (React Context API)
    ↓
前端元件 (React Components)
    ↓
使用者介面
```

### 詳細流程：

1. **系統設定資料流：**
   ```
   sys_profile 表
   → /api/system/profile
   → systemService.getProfile()
   → SystemContext
   → App.tsx, MainLayout.tsx, LoginPage.tsx, useDocumentTitle
   ```

2. **使用者資料流：**
   ```
   user_detail 表
   → /api/auth/me
   → authService.getCurrentUser()
   → AuthContext
   → DashboardPage.tsx, MainLayout.tsx
   ```

3. **組織資料流：**
   ```
   organizations 表
   → /api/organizations/{id}
   → organizationService.getOrganization()
   → DashboardPage state
   → DashboardPage UI (顯示 org_name)
   ```

---

## ✅ 最終確認

- ✅ 後端所有 API 都從 PostgreSQL 資料庫讀取資料
- ✅ 前端所有資料都透過後端 API 獲取
- ✅ 沒有硬編碼的資料（除了預設的 fallback 值）
- ✅ 系統設定、使用者資訊、組織資料都來自資料庫
- ✅ 組織顯示已改為顯示 `org_name`（匠耘有限公司）而非 `organization_id`（1）

---

## 執行中的服務

- **資料庫：** PostgreSQL (Docker container: postgres-dev, Port: 5432)
- **後端：** FastAPI (Port: 10181)
- **前端：** React Development Server (Port: 10180)

所有服務都正常運行，前後端都正確連接到資料庫。
