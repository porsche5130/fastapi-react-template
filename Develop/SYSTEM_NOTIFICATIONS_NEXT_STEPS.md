# 系統通知功能 - 剩餘工作清單

**更新時間**：2026-01-23 18:35
**狀態**：後端完成 ✅ | Service層完成 ✅ | i18n完成 ✅ | 頁面待實作 ⏳

---

## ✅ 本次對話已完成

### 1. 後端完整實作（100%）
- ✅ 資料庫模型與 Migration
- ✅ API 路由（8個端點）
- ✅ 權限整合
- ✅ 日誌記錄
- ✅ 測試資料表建立成功

### 2. 前端 Service 層（100%）
- ✅ systemNotificationsService.ts
- ✅ 8個 API 函數
- ✅ TypeScript 型別定義

### 3. i18n 語系檔案（100%）
- ✅ translation.json 新增 system_notifications 區塊
- ✅ 45+ 翻譯項目

---

## ⏳ 下次對話需要完成

### 1. SystemNotificationsPage（優先）

#### 檔案位置
`Develop/frontend/src/pages/SystemNotificationsPage.tsx`

#### 參考檔案
- `Develop/frontend/src/pages/UsersPage.tsx` - CRUD 結構
- `Develop/frontend/src/pages/SysProfilePage.tsx` - 表格實作
- `Develop/frontend/src/pages/OrganizationPage.tsx` - 篩選功能

#### 實作需求

**基本結構**：
```typescript
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  getSystemNotifications,
  createSystemNotification,
  updateSystemNotification,
  deleteSystemNotification,
  toggleSystemNotificationActive,
  SystemNotification
} from '../services/systemNotificationsService';

// 主要元件
function SystemNotificationsPage() {
  // State 管理
  const [notifications, setNotifications] = useState<SystemNotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedNotification, setSelectedNotification] = useState<SystemNotification | null>(null);
  
  // 篩選狀態
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined);
  const [filterOrder, setFilterOrder] = useState<number | undefined>(undefined);
  const [searchText, setSearchText] = useState('');
  
  // ... 實作內容
}
```

**表格欄位**（依規格）：
1. id - 數字
2. [中文主旨, 英文主旨] - 組合顯示（中文大字，英文小字）
3. notice_start_at - 開始時間
4. notice_end_at - 結束時間
5. notice_order - 訊息次序
6. is_active - 啟用狀態（可點選切換）
7. actions - 操作按鈕（檢視、編輯、刪除）

**功能要求**：
- [x] 表格分頁與排序
- [x] 篩選：結束時間、次序、啟用狀態
- [x] 全文檢索：中英文主旨
- [x] 啟用狀態切換按鈕
- [x] 權限控制（Create/Read/Update/Delete）
- [x] 新增/編輯 Modal
  - 富文本編輯器（說明欄位）
  - 日期時間選擇器
  - 表單驗證
- [x] 刪除確認對話框
- [x] 成功/錯誤訊息提示

#### 富文本編輯器選項

**推薦方案 1：React-Quill**
```bash
npm install react-quill
```

**推薦方案 2：TinyMCE React**
```bash
npm install @tinymce/tinymce-react
```

**推薦方案 3：Draft.js + react-draft-wysiwyg**
```bash
npm install draft-js react-draft-wysiwyg
```

---

### 2. Home 頁面通知 Modal

#### 檔案位置
`Develop/frontend/src/pages/HomePage.tsx`

#### 實作重點

**新增內容**：
```typescript
// 1. 引入 Service
import { 
  getHomeNotifications, 
  markNotificationReadToday,
  SystemNotification 
} from '../services/systemNotificationsService';

// 2. State 管理
const [todayNotifications, setTodayNotifications] = useState<SystemNotification[]>([]);
const [currentNotificationIndex, setCurrentNotificationIndex] = useState(0);
const [showNotificationModal, setShowNotificationModal] = useState(false);
const [doNotShowToday, setDoNotShowToday] = useState(false);

// 3. 載入今日通知（useEffect）
useEffect(() => {
  loadTodayNotifications();
}, []);

const loadTodayNotifications = async () => {
  try {
    const response = await getHomeNotifications();
    if (response.notifications.length > 0) {
      setTodayNotifications(response.notifications);
      setShowNotificationModal(true);
    }
  } catch (error) {
    console.error('載入今日通知失敗:', error);
  }
};

// 4. Modal 顯示邏輯
// - 依照 notice_order 排序（API 已處理）
// - 依照語系顯示對應欄位
// - 支援 HTML 渲染
// - 「本日不再閱讀」勾選框
```

**Modal UI 結構**：
```jsx
<Modal show={showNotificationModal} onHide={handleCloseNotification}>
  <Modal.Header>
    <Modal.Title>
      {i18n.language === 'zh-TW' 
        ? currentNotification.notice_csubject 
        : currentNotification.notice_esubject}
    </Modal.Title>
  </Modal.Header>
  <Modal.Body>
    <div dangerouslySetInnerHTML={{
      __html: i18n.language === 'zh-TW' 
        ? currentNotification.notice_cdescription 
        : currentNotification.notice_edescription
    }} />
  </Modal.Body>
  <Modal.Footer>
    <Form.Check 
      type="checkbox"
      label={t('system_notifications.doNotShowToday')}
      checked={doNotShowToday}
      onChange={(e) => setDoNotShowToday(e.target.checked)}
    />
    <Button onClick={handleNextOrClose}>
      {currentNotificationIndex < todayNotifications.length - 1 
        ? t('common.next') 
        : t('common.close')}
    </Button>
  </Modal.Footer>
</Modal>
```

---

### 3. 路由註冊

**檔案位置**：`Develop/frontend/src/App.tsx`

需要新增：
```typescript
import SystemNotificationsPage from './pages/SystemNotificationsPage';

// 在 Routes 中新增
<Route 
  path="/system-notifications" 
  element={
    <ProtectedRoute requiredPermission="system_notifications">
      <MainLayout>
        <SystemNotificationsPage />
      </MainLayout>
    </ProtectedRoute>
  } 
/>
```

---

## 🧪 測試清單

### 後端 API 測試（可使用 Swagger UI）

1. **基本 CRUD**
   - [ ] POST /system_notifications - 建立通知
   - [ ] GET /system_notifications - 列表
   - [ ] GET /system_notifications/{id} - 單筆
   - [ ] PUT /system_notifications/{id} - 更新
   - [ ] DELETE /system_notifications/{id} - 刪除

2. **特殊功能**
   - [ ] PATCH /system_notifications/{id}/toggle-active - 切換狀態
   - [ ] GET /system_notifications/home/notifications - 今日通知
   - [ ] POST /system_notifications/read-today - 標記不再閱讀

3. **權限測試**
   - [ ] 無權限使用者收到 403
   - [ ] Read 權限只能查看
   - [ ] Create 權限可以新增
   - [ ] Update 權限可以修改
   - [ ] Delete 權限可以刪除

4. **日誌測試**
   - [ ] 檢查 user_logs 表是否正確記錄

### 前端功能測試

1. **SystemNotificationsPage**
   - [ ] 表格正確顯示資料
   - [ ] 分頁功能正常
   - [ ] 篩選功能運作
   - [ ] 搜尋功能運作
   - [ ] 排序功能運作
   - [ ] 啟用切換正常
   - [ ] 新增通知成功
   - [ ] 編輯通知成功
   - [ ] 刪除通知成功
   - [ ] 富文本編輯器正常
   - [ ] 權限控制正確

2. **Home 通知 Modal**
   - [ ] 登入後自動顯示今日通知
   - [ ] 依次序顯示多則通知
   - [ ] 語系切換正確
   - [ ] HTML 渲染正確
   - [ ] 本日不再閱讀功能正常
   - [ ] 重新登入後已標記的不再顯示

---

## 📚 參考資訊

### 已實作檔案位置

**後端**：
- Models: `Develop/backend/app/models/system_notification.py`
- Schemas: `Develop/backend/app/schemas/system_notification.py`
- Routes: `Develop/backend/app/routes/system_notifications.py`
- Migration: `Develop/backend/migrations/create_system_notifications.sql`

**前端**：
- Service: `Develop/frontend/src/services/systemNotificationsService.ts`
- i18n: `Develop/frontend/src/locales/zh-TW/translation.json`

### API 端點清單

```
GET    /api/system_notifications           # 列表
GET    /api/system_notifications/{id}      # 單筆
POST   /api/system_notifications           # 新增
PUT    /api/system_notifications/{id}      # 更新
DELETE /api/system_notifications/{id}      # 刪除
PATCH  /api/system_notifications/{id}/toggle-active  # 切換狀態
GET    /api/system_notifications/home/notifications  # 今日通知
POST   /api/system_notifications/read-today          # 標記不再閱讀
```

---

## 💡 實作建議

### 1. 先完成基本頁面
- 簡單的表格顯示
- 基本的 CRUD Modal
- 不用富文本編輯器（先用 textarea）

### 2. 測試基本功能
- 確認 API 連接正常
- 確認權限控制運作

### 3. 再加入進階功能
- 整合富文本編輯器
- 完善篩選排序
- Home Modal

### 4. 最後優化
- UI/UX 調整
- 錯誤處理完善
- 效能優化

---

**下次對話開始時**：
請直接告訴我「繼續實作系統通知頁面」，我會立即開始實作 SystemNotificationsPage。

**預估工作量**：
- SystemNotificationsPage：約 300-400 行程式碼
- Home Modal：約 100-150 行程式碼
- 測試與調整：視情況而定

---

**實作者**：Claude Sonnet 4.5  
**文件版本**：1.0  
**最後更新**：2026-01-23 18:35
