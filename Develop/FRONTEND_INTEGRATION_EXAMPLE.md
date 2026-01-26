# 前端整合範例 - 兩階段權限架構

## 核心概念

**有了權限 + 有了 txn_token 才能使用功能**

1. **module_item**: 功能呈現的基本要求（該功能應該提供哪些操作項目）
2. **permissions**: 使用者實際擁有的權限（該使用者可以執行哪些操作）
3. **txn_token**: 執行操作的必要憑證（所有 API 呼叫都必須帶）

---

## Step 1: 建立 API Service

### `src/services/systemFunctionService.ts`
```typescript
import axios from './axios';

export interface ModuleItem {
  func_code: string;
  module_item: string[];  // ["create", "read", "update", "delete", "print", "file"]
  func_cname: string;
  func_ename: string;
  // ... 其他欄位
}

/**
 * 根據 func_code 取得系統功能資訊（包含 module_item）
 */
export const getSystemFunctionByCode = async (funcCode: string): Promise<ModuleItem> => {
  const response = await axios.get(`/system-functions/by-code/${funcCode}`);
  return response.data;
};
```

### `src/services/transactionService.ts`
```typescript
import axios from './axios';

export interface TransactionTokenResponse {
  txn_token: string;
  expires_in: number;
  func_code: string;
  permissions: {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
    print: boolean;
    file: boolean;
  };
}

/**
 * 申請功能交易令牌
 */
export const requestToken = async (funcCode: string): Promise<TransactionTokenResponse> => {
  const response = await axios.post('/transaction/request', {
    func_code: funcCode
  });
  return response.data;
};

/**
 * 撤銷交易令牌（離開頁面時呼叫）
 */
export const revokeToken = async (txnToken: string): Promise<void> => {
  await axios.post('/transaction/revoke', null, {
    headers: {
      'X-Txn-Token': txnToken
    }
  });
};
```

---

## Step 2: 建立權限管理 Hook

### `src/hooks/useFunctionPermission.ts`
```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as transactionService from '../services/transactionService';
import * as systemFunctionService from '../services/systemFunctionService';

interface FunctionPermissionState {
  txnToken: string | null;
  permissions: {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
    print: boolean;
    file: boolean;
  } | null;
  moduleItem: string[];
  loading: boolean;
  error: string | null;
}

/**
 * 功能權限管理 Hook
 *
 * 使用範例:
 * const { txnToken, permissions, moduleItem, loading } = useFunctionPermission("organizations");
 */
export const useFunctionPermission = (funcCode: string) => {
  const navigate = useNavigate();
  const [state, setState] = useState<FunctionPermissionState>({
    txnToken: null,
    permissions: null,
    moduleItem: [],
    loading: true,
    error: null
  });

  useEffect(() => {
    const initialize = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));

        // 1. 申請交易令牌（包含權限檢查）
        const tokenResponse = await transactionService.requestToken(funcCode);

        // 2. 取得功能的 module_item
        const functionInfo = await systemFunctionService.getSystemFunctionByCode(funcCode);

        setState({
          txnToken: tokenResponse.txn_token,
          permissions: tokenResponse.permissions,
          moduleItem: functionInfo.module_item || [],
          loading: false,
          error: null
        });

      } catch (error: any) {
        console.error('功能權限初始化失敗:', error);

        if (error.response?.status === 403) {
          // 無權限存取此功能
          setState(prev => ({
            ...prev,
            loading: false,
            error: '您沒有權限使用此功能'
          }));
          navigate('/unauthorized');
        } else {
          setState(prev => ({
            ...prev,
            loading: false,
            error: '功能初始化失敗，請稍後再試'
          }));
        }
      }
    };

    initialize();

    // 離開頁面時撤銷 token
    return () => {
      if (state.txnToken) {
        transactionService.revokeToken(state.txnToken).catch(console.error);
      }
    };
  }, [funcCode, navigate]);

  return state;
};
```

---

## Step 3: 在頁面中使用

### `src/pages/OrganizationsPage.tsx` (完整範例)
```typescript
import React, { useState, useEffect } from 'react';
import { useFunctionPermission } from '../hooks/useFunctionPermission';
import * as organizationService from '../services/organizationService';

const OrganizationsPage: React.FC = () => {
  // 1. 使用權限管理 Hook
  const { txnToken, permissions, moduleItem, loading } = useFunctionPermission("organizations");

  // 2. 業務狀態
  const [organizations, setOrganizations] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);

  // 3. 載入資料
  useEffect(() => {
    if (txnToken && permissions?.read) {
      loadOrganizations();
    }
  }, [txnToken, permissions]);

  const loadOrganizations = async () => {
    try {
      const data = await organizationService.getOrganizations({
        headers: { 'X-Txn-Token': txnToken }
      });
      setOrganizations(data);
    } catch (error) {
      console.error('載入組織列表失敗:', error);
    }
  };

  // 4. 操作處理函數
  const handleCreate = async () => {
    if (!permissions?.create) {
      alert('您沒有新增權限');
      return;
    }

    try {
      await organizationService.createOrganization(newOrgData, {
        headers: { 'X-Txn-Token': txnToken }
      });
      await loadOrganizations();
    } catch (error) {
      console.error('新增組織失敗:', error);
    }
  };

  const handleUpdate = async () => {
    if (!permissions?.update) {
      alert('您沒有修改權限');
      return;
    }

    try {
      await organizationService.updateOrganization(selectedOrg.id, updateData, {
        headers: { 'X-Txn-Token': txnToken }
      });
      await loadOrganizations();
    } catch (error) {
      console.error('更新組織失敗:', error);
    }
  };

  const handleDelete = async () => {
    if (!permissions?.delete) {
      alert('您沒有刪除權限');
      return;
    }

    if (!confirm('確定要刪除此組織嗎？')) return;

    try {
      await organizationService.deleteOrganization(selectedOrg.id, {
        headers: { 'X-Txn-Token': txnToken }
      });
      await loadOrganizations();
    } catch (error) {
      console.error('刪除組織失敗:', error);
    }
  };

  // 5. 載入中
  if (loading) {
    return <div>載入中...</div>;
  }

  // 6. 沒有權限
  if (!permissions?.read) {
    return <div>您沒有權限查看此頁面</div>;
  }

  // 7. UI 渲染（根據 module_item 和 permissions）
  return (
    <div className="organizations-page">
      <h1>組織管理</h1>

      {/* 工具列：只顯示 module_item 包含的按鈕 */}
      <div className="toolbar">
        {moduleItem.includes("create") && (
          <button
            onClick={handleCreate}
            disabled={!permissions.create}
            className={!permissions.create ? 'disabled' : ''}
          >
            新增組織
          </button>
        )}

        {moduleItem.includes("update") && (
          <button
            onClick={handleUpdate}
            disabled={!permissions.update || !selectedOrg}
            className={(!permissions.update || !selectedOrg) ? 'disabled' : ''}
          >
            修改組織
          </button>
        )}

        {moduleItem.includes("delete") && (
          <button
            onClick={handleDelete}
            disabled={!permissions.delete || !selectedOrg}
            className={(!permissions.delete || !selectedOrg) ? 'disabled' : ''}
          >
            刪除組織
          </button>
        )}

        {moduleItem.includes("print") && (
          <button
            onClick={handlePrint}
            disabled={!permissions.print}
            className={!permissions.print ? 'disabled' : ''}
          >
            列印
          </button>
        )}
      </div>

      {/* 資料列表 */}
      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>組織代碼</th>
              <th>組織名稱</th>
              <th>聯絡人</th>
              <th>電話</th>
            </tr>
          </thead>
          <tbody>
            {organizations.map(org => (
              <tr
                key={org.id}
                onClick={() => setSelectedOrg(org)}
                className={selectedOrg?.id === org.id ? 'selected' : ''}
              >
                <td>{org.org_code}</td>
                <td>{org.org_name}</td>
                <td>{org.contact_person}</td>
                <td>{org.contact_phone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OrganizationsPage;
```

---

## Step 4: 錯誤處理

### 處理 Token 過期
```typescript
// 在 axios interceptor 中處理 token 過期
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && error.response?.data?.detail?.includes('令牌')) {
      // Token 過期，重新申請
      const funcCode = getCurrentFuncCode(); // 從 URL 或 context 取得
      try {
        const result = await transactionService.requestToken(funcCode);
        // 更新 token 並重試請求
        error.config.headers['X-Txn-Token'] = result.txn_token;
        return axios.request(error.config);
      } catch (retryError) {
        // 重新申請失敗，可能權限已被撤銷
        return Promise.reject(retryError);
      }
    }
    return Promise.reject(error);
  }
);
```

---

## Step 5: 權限狀態顯示

### 權限指示器組件
```typescript
interface PermissionIndicatorProps {
  moduleItem: string[];
  permissions: {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
    print: boolean;
    file: boolean;
  };
}

const PermissionIndicator: React.FC<PermissionIndicatorProps> = ({ moduleItem, permissions }) => {
  const permissionLabels = {
    create: '新增',
    read: '查詢',
    update: '修改',
    delete: '刪除',
    print: '列印',
    file: '檔案'
  };

  return (
    <div className="permission-indicator">
      <h4>您的權限:</h4>
      <div className="permission-badges">
        {moduleItem.map(item => (
          <span
            key={item}
            className={`badge ${permissions[item] ? 'active' : 'inactive'}`}
          >
            {permissionLabels[item]}
            {permissions[item] ? ' ✓' : ' ✗'}
          </span>
        ))}
      </div>
    </div>
  );
};
```

---

## 完整流程圖

```
使用者進入頁面 (OrganizationsPage)
    ↓
useFunctionPermission("organizations") Hook 啟動
    ↓
1. 呼叫 POST /api/transaction/request
   └─ 檢查權限 (階段一: Redis + 階段二: Database)
   └─ 建立/延長 Transaction Token
   └─ 回傳 { txn_token, permissions }
    ↓
2. 呼叫 GET /api/system-functions/by-code/organizations
   └─ 取得 { module_item: ["create", "read", "update", "delete"] }
    ↓
3. 設定 State
   └─ txnToken: "abc123..."
   └─ permissions: { create: false, read: true, update: true, delete: false }
   └─ moduleItem: ["create", "read", "update", "delete"]
    ↓
4. 根據 moduleItem 和 permissions 渲染 UI
   └─ moduleItem.includes("create") → 顯示新增按鈕
   └─ permissions.create → 啟用/停用新增按鈕
    ↓
5. 使用者點擊按鈕執行操作
   └─ 帶上 X-Txn-Token Header 呼叫 API
    ↓
6. 離開頁面時撤銷 Token
   └─ POST /api/transaction/revoke
```

---

## 最佳實務總結

### ✅ DO

1. **總是使用 useFunctionPermission Hook** 來管理功能權限
2. **根據 module_item 決定要顯示哪些 UI 元件**
3. **根據 permissions 決定 UI 元件的啟用/停用狀態**
4. **所有 API 呼叫都帶上 X-Txn-Token Header**
5. **離開頁面時撤銷 Transaction Token**
6. **處理權限不足和 Token 過期的情況**

### ❌ DON'T

1. **不要硬編碼按鈕顯示** - 必須根據 module_item 動態決定
2. **不要跳過權限檢查** - 即使前端隱藏按鈕，後端仍會檢查
3. **不要忘記帶 txn_token** - 所有操作 API 都需要
4. **不要在未取得 token 前呼叫 API** - 等待 loading 完成
5. **不要快取 module_item** - 功能設定可能會變更

---

## 測試檢查清單

### 功能初始化測試
- [ ] 有權限的使用者可以正常進入頁面
- [ ] 無權限的使用者會被導向到 unauthorized 頁面
- [ ] txn_token 正確取得並儲存

### UI 顯示測試
- [ ] 只顯示 module_item 包含的操作按鈕
- [ ] 使用者有權限的按鈕可點擊
- [ ] 使用者無權限的按鈕停用（灰色）

### 操作測試
- [ ] 點擊按鈕會正確帶上 X-Txn-Token Header
- [ ] 權限不足時顯示錯誤訊息
- [ ] Token 過期會自動重新申請

### 離開頁面測試
- [ ] 離開頁面時 token 被正確撤銷
- [ ] 重新進入頁面會建立新的 token

---

## 除錯技巧

### 檢查 txn_token
```typescript
console.log('Transaction Token:', txnToken);
// 應該是 64 位元的 hex 字串
```

### 檢查 permissions
```typescript
console.log('Permissions:', permissions);
// { create: false, read: true, update: true, delete: false, print: false, file: false }
```

### 檢查 module_item
```typescript
console.log('Module Item:', moduleItem);
// ["create", "read", "update", "delete"]
```

### 檢查 API 請求
```typescript
// 在 browser DevTools → Network → Headers
// 應該看到:
X-Txn-Token: abc123def456...
Authorization: Bearer eyJhbGc...
```
