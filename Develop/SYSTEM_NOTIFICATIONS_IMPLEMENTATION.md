# 系統通知功能實作摘要

**實作日期**：2026-01-23  
**功能代碼**：system_notifications  
**狀態**：後端完成 ✅ | 前端 Service 完成 ✅ | 前端頁面待完成 ⏳

---

## ✅ 已完成項目

### 1. 後端實作（100% 完成）

#### 資料庫

**資料表**：
- ✅ `system_notifications` - 系統通知主表
- ✅ `notification_read_today` - 本日不再閱讀追蹤表

**Migration 檔案**：
- `Develop/backend/migrations/create_system_notifications.sql`
- 執行狀態：✅ 成功建立兩個資料表

#### Models（資料模型）

**檔案**：`Develop/backend/app/models/system_notification.py`

```python
class SystemNotification(Base):
    """系統通知主表"""
    - notice_csubject: 中文主旨
    - notice_esubject: 英文主旨
    - notice_cdescription: 中文說明（富文本）
    - notice_edescription: 英文說明（富文本）
    - notice_start_at: 開始時間
    - notice_end_at: 結束時間
    - notice_order: 訊息次序
    - is_active: 啟用狀態

class NotificationReadToday(Base):
    """本日不再閱讀追蹤表"""
    - user_id: 使用者ID
    - notification_id: 通知ID
    - read_date: 閱讀日期
```

#### Schemas（API 資料結構）

**檔案**：`Develop/backend/app/schemas/system_notification.py`

- `SystemNotificationCreate` - 建立通知
- `SystemNotificationUpdate` - 更新通知
- `SystemNotificationResponse` - 通知回應
- `NotificationReadTodayCreate` - 標記本日不再閱讀
- `TodayNotificationsResponse` - 今日通知回應

#### API Routes（路由）

**檔案**：`Develop/backend/app/routes/system_notifications.py`

**已實作端點**：

| 方法 | 路徑 | 功能 | 權限 | 日誌 |
|------|------|------|------|------|
| GET | `/` | 取得通知列表 | read | View ✅ |
| GET | `/{id}` | 取得單一通知 | read | Read ✅ |
| POST | `/` | 建立通知 | create | Create ✅ |
| PUT | `/{id}` | 更新通知 | update | Update ✅ |
| DELETE | `/{id}` | 刪除通知 | delete | Delete ✅ |
| PATCH | `/{id}/toggle-active` | 切換啟用狀態 | update | Update ✅ |
| GET | `/home/notifications` | 取得今日通知 | - | - |
| POST | `/read-today` | 標記本日不再閱讀 | - | - |

**功能特色**：
- ✅ 完整的 CRUD 操作
- ✅ 權限檢查整合
- ✅ 使用者日誌記錄（View/Read/Create/Update/Delete）
- ✅ 錯誤處理與日誌
- ✅ 時間範圍驗證
- ✅ 篩選功能（is_active, notice_order, search）
- ✅ 全文檢索（中英文主旨）

#### system_functions 設定

```
ID: 18
func_code: system_notifications
module_code: system_notifications
func_type: 2 (功能)
upper_func_id: 10 (system_mana)
module_item: ['Create', 'Read', 'Update', 'Delete']
is_active: true
```

---

### 2. 前端實作（Service 層完成）

#### Service 層

**檔案**：`Develop/frontend/src/services/systemNotificationsService.ts`

**已實作函數**：
- ✅ `getSystemNotifications()` - 取得通知列表
- ✅ `getSystemNotification(id)` - 取得單一通知
- ✅ `createSystemNotification(data)` - 建立通知
- ✅ `updateSystemNotification(id, data)` - 更新通知
- ✅ `deleteSystemNotification(id)` - 刪除通知
- ✅ `toggleSystemNotificationActive(id)` - 切換啟用狀態
- ✅ `getHomeNotifications()` - 取得今日通知
- ✅ `markNotificationReadToday(id)` - 標記本日不再閱讀

**TypeScript 介面**：
- `SystemNotification`
- `SystemNotificationCreate`
- `SystemNotificationUpdate`
- `TodayNotificationsResponse`

---

## ⏳ 待完成項目

### 3. 前端頁面

#### 需要實作：

1. **SystemNotificationsPage（管理頁面）**
   - 檔案位置：`Develop/frontend/src/pages/SystemNotificationsPage.tsx`
   - 功能需求：
     - DataTables 表格顯示
     - 欄位：id, [中文主旨,英文主旨], 開始時間, 結束時間, 次序, 啟用, actions
     - 篩選：結束時間、次序、啟用狀態
     - 全文檢索：中英文主旨
     - 排序：id, 開始時間, 結束時間, 次序
     - 啟用狀態可點選切換
     - Actions: 檢視、編輯、刪除
     - 富文本編輯器支援（說明欄位）
     - 支援 HTML 渲染（包含上下標 <sub></sub>）

2. **i18n 語系檔案**
   - 檔案位置：`Develop/frontend/src/locales/zh-TW/translation.json`
   - 需要新增：`system_notifications` 區塊
   - 語系項目：
     - 頁面標題、表格欄位名稱
     - 按鈕文字、訊息提示
     - 錯誤訊息、成功訊息

3. **Home 頁面通知 Modal**
   - 檔案位置：`Develop/frontend/src/pages/HomePage.tsx`
   - 功能需求：
     - 登入後自動檢查今日通知
     - Modal 顯示通知（依 notice_order 排序）
     - 依語系顯示主旨和說明
     - 「本日不再閱讀」勾選功能
     - 富文本內容渲染

---

## 📋 規格對應檢查表

| 規格項目 | 後端 | 前端 | 狀態 |
|---------|------|------|------|
| (1) CRUD DataTables | ✅ | ⏳ | 後端完成 |
| (2) 雙語顯示（中英文） | ✅ | ⏳ | 結構完成 |
| (3) Action 權限控制 | ✅ | ⏳ | 後端完成 |
| (4) HTML 渲染支援 | ✅ | ⏳ | 富文本儲存完成 |
| (5) 篩選欄位 | ✅ | ⏳ | API 完成 |
| (6) 全文檢索 | ✅ | ⏳ | API 完成 |
| (7) i18n 語系切換 | ✅ | ⏳ | 架構完成 |
| (8) 日誌記錄 | ✅ | - | 完整實作 |
| (9) 啟用切換 | ✅ | ⏳ | API 完成 |
| (10) 排序設定 | ✅ | ⏳ | API 完成 |
| (11) Home Modal | ✅ | ⏳ | API 完成 |
| (12) 本日不再閱讀 | ✅ | ⏳ | API 完成 |

---

## 🚀 下一步行動

### 立即可做：

1. **測試後端 API**
   ```bash
   # 啟動後端服務
   cd Develop/backend
   uvicorn app.main:app --reload --port 10181
   
   # 使用 Swagger UI 測試
   http://localhost:10181/docs
   ```

2. **實作前端頁面**
   - 建立 SystemNotificationsPage.tsx
   - 整合富文本編輯器
   - 實作 DataTables 表格

3. **實作 Home 通知 Modal**
   - 修改 HomePage.tsx
   - 實作通知彈窗邏輯

4. **新增 i18n 語系**
   - 更新 translation.json

---

## 📝 技術備註

### API 路徑前綴
- 後端定義：`/api/system_notifications`
- 前端 Service：自動加上 `/api` 前綴

### 權限代碼
- 模組：`system_notifications`
- 權限項目：`create`, `read`, `update`, `delete`

### 富文本格式
- 儲存格式：HTML
- 支援標籤：`<p>`, `<sub>`, `<sup>`, `<strong>`, `<em>` 等
- 前端需要：富文本編輯器（TinyMCE/Quill/CKEditor）

### 本日不再閱讀機制
- 使用 `notification_read_today` 表追蹤
- 每天重置（基於 read_date）
- 唯一約束：(user_id, notification_id, read_date)

---

**實作者**：Claude Sonnet 4.5  
**最後更新**：2026-01-23
