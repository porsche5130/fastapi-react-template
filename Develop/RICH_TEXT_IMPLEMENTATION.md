# 富文本編輯器實作記錄
## Rich Text Editor Implementation Record

**實作日期**: 2026-01-23
**編輯器**: Lexical (Meta/Facebook)

---

## 技術選擇過程

### 嘗試過的方案
1. ❌ **React Quill** - React 19 不相容（使用已廢棄的 findDOMNode API）
2. ❌ **TinyMCE** - 需要授權金鑰（即使免費版本）
3. ✅ **Lexical** - Meta 開發，完全開源，React 19 相容

---

## 實作內容

### 1. 安裝套件
```bash
npm install lexical @lexical/react @lexical/html @lexical/selection --legacy-peer-deps
```

### 2. 建立檔案

#### [RichTextEditor.tsx](Develop/frontend/src/components/RichTextEditor.tsx)
- 主要富文本編輯器元件
- 支援 HTML 輸入/輸出
- 可啟用/停用模式
- 自訂佔位符

#### [ToolbarPlugin.tsx](Develop/frontend/src/components/ToolbarPlugin.tsx)
- 工具列外掛
- 支援功能：
  - 復原/重做
  - 標題格式（H1-H3）
  - 文字格式（粗體、斜體、底線、刪除線）
  - 對齊方式（左、中、右）
  - 列表（項目符號、編號）

#### [RichTextEditor.css](Develop/frontend/src/styles/RichTextEditor.css)
- 編輯器樣式
- 工具列樣式
- 停用狀態樣式
- 錯誤狀態樣式

### 3. 整合到系統通知頁面

修改 [SystemNotificationsPage.tsx](Develop/frontend/src/pages/SystemNotificationsPage.tsx):

**替換欄位**:
- `notice_cdescription` - 中文說明
- `notice_edescription` - 英文說明

**使用方式**:
```tsx
<RichTextEditor
  value={formData.notice_cdescription}
  onChange={(html) => setFormData({ ...formData, notice_cdescription: html })}
  disabled={isViewMode}
  placeholder={t('system_notifications.noticeCDescription')}
/>
```

---

## 功能特點

### 編輯模式
- ✅ 完整工具列
- ✅ 即時 HTML 輸出
- ✅ 300px 高度
- ✅ 自動捲軸

### 檢視模式
- ✅ 隱藏工具列
- ✅ 灰色背景
- ✅ 禁止編輯
- ✅ 游標顯示為 not-allowed

### 支援格式
| 功能 | HTML 標籤 |
|------|-----------|
| 段落 | `<p>` |
| 標題 1-3 | `<h1>`, `<h2>`, `<h3>` |
| 粗體 | `<strong>` |
| 斜體 | `<em>` |
| 底線 | `<u>` |
| 刪除線 | `<s>` |
| 項目符號列表 | `<ul><li>` |
| 編號列表 | `<ol><li>` |
| 超連結 | `<a>` |

---

## 資料處理

### 儲存格式
- **格式**: HTML 字串
- **編碼**: UTF-8
- **資料庫欄位**: TEXT

### 輸入/輸出
- **輸入**: 從資料庫讀取 HTML → 顯示在編輯器
- **輸出**: 編輯器內容 → 轉換為 HTML → 儲存到資料庫

---

## 編譯狀態
✅ **編譯成功** (Compiled successfully!)
✅ **無 TypeScript 錯誤**
✅ **無 ESLint 錯誤**（僅有未使用變數的警告，不影響功能）

---

## 瀏覽器相容性
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

---

**實作完成時間**: 2026-01-23
**開發者**: Claude Sonnet 4.5
