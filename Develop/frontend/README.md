# PA6.4 Frontend Application

Paris Agreement Article 6.4 管理系統前端應用程式

## 專案資訊

- **專案名稱**: PA6.4 Management System Frontend
- **技術棧**: React 18 | TypeScript | React Router | Axios
- **開發伺服器**: http://localhost:10180
- **後端 API**: http://localhost:10181

---

## 快速開始

### 1. 安裝依賴

```bash
cd W:\P-PA6.4\Develop\frontend
npm install
```

### 2. 啟動開發伺服器

```bash
npm start
```

瀏覽器會自動開啟 http://localhost:10180

### 3. 建置生產版本

```bash
npm run build
```

---

## 專案結構

```
frontend/
├── public/                 # 靜態資源
├── src/
│   ├── api/                # API 服務層
│   │   ├── axios.ts        # Axios 配置
│   │   ├── authService.ts  # 認證 API
│   │   └── systemService.ts # 系統 API
│   │
│   ├── components/         # React 元件
│   │   ├── MainLayout.tsx  # 主要佈局元件
│   │   ├── Sidebar.tsx     # 側邊欄選單
│   │   └── PrivateRoute.tsx # 路由保護
│   │
│   ├── contexts/           # Context 狀態管理
│   │   ├── AuthContext.tsx # 認證狀態
│   │   └── SystemContext.tsx # 系統狀態
│   │
│   ├── pages/              # 頁面元件
│   │   ├── MaintenancePage.tsx # 系統維護頁面
│   │   ├── LoginPage.tsx   # 登入頁面
│   │   └── DashboardPage.tsx # 儀表板頁面
│   │
│   ├── styles/             # CSS 樣式檔
│   │   ├── MaintenancePage.css
│   │   ├── LoginPage.css
│   │   ├── MainLayout.css
│   │   ├── Sidebar.css
│   │   └── DashboardPage.css
│   │
│   ├── types/              # TypeScript 類型定義
│   │   └── index.ts
│   │
│   ├── App.tsx             # 應用程式主元件
│   └── index.tsx           # 應用程式入口
│
├── .env                    # 環境變數
├── package.json
└── README.md
```

---

## 功能說明

### 1. 系統維護檢查

當使用者進入系統時，會自動檢查 `sys_profile.is_service` 狀態：

- **true**: 進入登入頁面
- **false**: 顯示系統維護頁面

### 2. 登入頁面

- 支援電子郵件格式登入
- 密碼驗證
- 自動儲存 JWT Token
- 登入成功後導向儀表板

**預設帳號**:
- Email: admin@pa64.system
- Password: admin123

### 3. 主要佈局

登入成功後顯示完整的系統介面：

#### (1) 左側選單
- 顯示系統功能模組
- 支援上下層級關係（來自 sysfuction 資料表）
- 可收合/展開
- 目前使用假資料，未來會從後端 API 載入

#### (2) 上方使用者資訊區
- 顯示使用者頭像
- 使用者名稱
- 職稱/部門
- 登出按鈕

#### (3) 中間內容區
- 顯示功能操作畫面
- 目前實作儀表板頁面
- 使用 React Router Outlet 動態載入

#### (4) 下方版權宣告
- 顯示中文版權資訊
- 顯示英文版權資訊
- 資料來自系統設定

---

## 狀態管理

### AuthContext (認證狀態)

```typescript
const { user, isAuthenticated, login, logout } = useAuth();
```

- **user**: 當前登入使用者資料
- **isAuthenticated**: 是否已登入
- **login(token)**: 登入並載入使用者資料
- **logout()**: 登出並清除資料

### SystemContext (系統狀態)

```typescript
const { systemProfile, isService, isLoading } = useSystem();
```

- **systemProfile**: 系統設定資料
- **isService**: 系統是否正常服務
- **isLoading**: 是否載入中

---

## API 服務

### authService

- `login(data)` - 使用者登入
- `getCurrentUser()` - 取得當前使用者資訊
- `logout()` - 使用者登出
- `isAuthenticated()` - 檢查是否已登入
- `saveToken(token)` - 儲存 Token
- `clearToken()` - 清除 Token

### systemService

- `getProfile()` - 取得系統設定
- `checkSystem()` - 系統健康檢查

---

## 路由配置

| 路徑 | 元件 | 說明 | 保護 |
|------|------|------|------|
| `/login` | LoginPage | 登入頁面 | 否 |
| `/` | MainLayout | 主要佈局 | 是 |
| `/dashboard` | DashboardPage | 儀表板 | 是 |

---

## 環境變數

**檔案**: `.env`

```bash
REACT_APP_API_URL=http://localhost:10181
PORT=10180
```

---

## 樣式設計

- 使用漸層色彩: `#667eea` → `#764ba2`
- 響應式設計支援
- 現代化 UI 介面
- 流暢的動畫效果

---

## 開發說明

### 新增頁面

1. 在 `src/pages/` 建立新的頁面元件
2. 在 `src/App.tsx` 註冊路由:

```typescript
<Route path="new-page" element={<NewPage />} />
```

### 新增 API 服務

1. 在 `src/api/` 建立新的服務檔案
2. 使用 axios 實例進行 API 呼叫
3. 在 `src/types/index.ts` 定義類型

### 新增選單項目

目前選單項目在 `Sidebar.tsx` 使用假資料。

未來會從後端 API 載入 sysfuction 資料表內容。

---

## 待辦事項

- [ ] 實作從後端 API 載入系統功能選單 (sysfuction)
- [ ] 新增使用者管理頁面
- [ ] 新增角色管理頁面
- [ ] 新增組織管理頁面
- [ ] 實作系統功能權限控制
- [ ] 新增多語系支援

---

## 相關文件

- [後端 API 文件](../backend/README.md)
- [資料庫設計](../../系統設計/應用系統設計/基礎資訊管理後台設計.md)
- [開發環境設定](../../系統設計/架構設計/開發環境/開發測試環境.md)

---

## 故障排除

### 1. API 連線失敗

檢查後端伺服器是否執行:
```bash
curl http://localhost:10181/api/health
```

### 2. CORS 錯誤

確認後端 `.env` 檔案的 `ALLOWED_ORIGINS` 包含前端網址:
```bash
ALLOWED_ORIGINS=["http://localhost:10180"]
```

### 3. Port 被佔用

修改 `.env` 檔案中的 PORT 設定:
```bash
PORT=3000
```

---

## 更新記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-01-18 | 1.0.0 | 建立初始前端應用程式，實作登入、系統維護檢查、主要佈局 |
