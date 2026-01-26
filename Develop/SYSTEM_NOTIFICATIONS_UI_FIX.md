# 系統通知 UI 修正報告

## 修正日期
2026-01-23

## 修正項目

### 1. 新增按鈕文字
**修正前**: `+ 新增通知` (createNotification)
**修正後**: `新增` (common.create)

**位置**: [SystemNotificationsPage.tsx:360-363](Develop/frontend/src/pages/SystemNotificationsPage.tsx#L360-L363)

```tsx
// 修正前
<button className="btn-primary" onClick={handleCreate}>
  + {t('system_notifications.createNotification')}
</button>

// 修正後
<button className="btn-primary" onClick={handleCreate}>
  {t('common.create')}
</button>
```

---

### 2. Modal 標題格式
**修正前**:
- 新增: `新增通知`
- 編輯: `編輯通知`
- 檢視: `檢視通知`

**修正後**:
- 新增: `{功能名稱} - 新增作業`
- 編輯: `{功能名稱} - 編輯作業`
- 檢視: `{功能名稱} - 檢視作業`

**位置**: [SystemNotificationsPage.tsx:527-531](Develop/frontend/src/pages/SystemNotificationsPage.tsx#L527-L531)

```tsx
// 修正前
<h2>
  {isViewMode
    ? t('system_notifications.viewNotification')
    : editingNotification
    ? t('system_notifications.editNotification')
    : t('system_notifications.createNotification')}
</h2>

// 修正後
<h2>
  {pageTitle} - {isViewMode ? t('common.viewOperation') : (editingNotification ? t('common.editOperation') : t('common.createOperation'))}
</h2>
```

---

### 3. 啟用狀態切換位置
**修正前**: 在 actions 欄位下有「啟用」按鈕
**修正後**: 在「啟用狀態」欄位直接點擊狀態標籤切換

**位置**: [SystemNotificationsPage.tsx:421-441](Develop/frontend/src/pages/SystemNotificationsPage.tsx#L421-L441)

```tsx
// 修正前
<td>
  <span className={`status-badge ${notification.is_active ? 'active' : 'inactive'}`}>
    {notification.is_active ? t('system_notifications.active') : t('system_notifications.inactive')}
  </span>
</td>
<td className="actions">
  {hasPermission('system_notifications', 'update') && (
    <button className="btn-edit" onClick={() => handleToggleActive(notification)}>
      {t('common.enable')}
    </button>
  )}
  ...
</td>

// 修正後
<td>
  <span
    className={`status-badge ${notification.is_active ? 'active' : 'inactive'}`}
    onClick={() => hasPermission('system_notifications', 'update') && handleToggleActive(notification)}
    style={{ cursor: hasPermission('system_notifications', 'update') ? 'pointer' : 'default' }}
  >
    {notification.is_active ? t('common.active') : t('common.inactive')}
  </span>
</td>
<td className="actions">
  {/* 移除了啟用按鈕 */}
  {hasPermission('system_notifications', 'update') && (
    <button className="btn-edit" onClick={() => handleEdit(notification)}>
      {t('common.edit')}
    </button>
  )}
  ...
</td>
```

---

## UI 佈局一致性

現在系統通知頁面的 UI 佈局已與使用者資料維護頁面完全一致：

### 共同特徵
1. ✅ 新增按鈕顯示「新增」文字
2. ✅ Modal 標題格式：`{功能名稱} - {操作類型}`
3. ✅ 啟用狀態在狀態欄位直接點擊切換
4. ✅ 操作欄位只包含：編輯、檢視（無編輯權限時）、刪除
5. ✅ 使用深綠色表頭 (table-header-dark-green)
6. ✅ 分頁控制一致
7. ✅ 權限檢查邏輯一致

---

## 翻譯鍵值使用

### common 區段（共用翻譯）
- `common.create` - 新增
- `common.edit` - 編輯
- `common.view` - 檢視
- `common.delete` - 刪除
- `common.active` - 啟用
- `common.inactive` - 停用
- `common.createOperation` - 新增作業
- `common.editOperation` - 編輯作業
- `common.viewOperation` - 檢視作業

### system_notifications 區段（功能專用）
- `system_notifications.noticeCSubject` - 中文主旨
- `system_notifications.noticeESubject` - 英文主旨
- `system_notifications.noticeCDescription` - 中文說明
- `system_notifications.noticeEDescription` - 英文說明
- ... 其他功能專用翻譯

---

## 編譯狀態
✅ **編譯成功** (Compiled successfully!)
✅ **無 TypeScript 錯誤**
✅ **無 ESLint 警告**（最新編譯）

---

## 測試檢查表

### 功能測試
- [ ] 新增通知 - Modal 標題顯示「{功能名稱} - 新增作業」
- [ ] 編輯通知 - Modal 標題顯示「{功能名稱} - 編輯作業」
- [ ] 檢視通知 - Modal 標題顯示「{功能名稱} - 檢視作業」
- [ ] 點擊啟用狀態標籤可以切換啟用/停用
- [ ] 無更新權限時，啟用狀態不可點擊
- [ ] 新增按鈕顯示「新增」文字
- [ ] actions 欄位不包含「啟用」按鈕

### 權限測試
- [ ] 有 create 權限時顯示「新增」按鈕
- [ ] 有 update 權限時顯示「編輯」按鈕
- [ ] 無 update 但有 read 權限時顯示「檢視」按鈕
- [ ] 有 delete 權限時顯示「刪除」按鈕
- [ ] 有 update 權限時可以點擊狀態標籤切換

---

## 參考頁面
與 [UsersPage.tsx](Develop/frontend/src/pages/UsersPage.tsx) 保持一致的 UI 佈局和互動模式。

---

**修正完成時間**: 2026-01-23
**開發者**: Claude Sonnet 4.5
