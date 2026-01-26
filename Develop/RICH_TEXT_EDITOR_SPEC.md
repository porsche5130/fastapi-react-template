# 富文本編輯器規格文件
## Rich Text Editor Specification

---

## 一、功能需求

### 1.1 適用欄位
- **中文說明** (notice_cdescription)
- **英文說明** (notice_edescription)

### 1.2 編輯器類型
- **採用**: React Quill
- **版本**: 最新穩定版 (^2.0.0)
- **授權**: BSD 3-Clause License (免費商用)

---

## 二、工具列功能 (Toolbar)

### 2.1 文字格式化
| 功能 | 圖示 | HTML 標籤 | 說明 |
|------|------|-----------|------|
| 粗體 | **B** | `<strong>` | 文字加粗 |
| 斜體 | *I* | `<em>` | 文字傾斜 |
| 底線 | <u>U</u> | `<u>` | 文字加底線 |
| 刪除線 | ~~S~~ | `<s>` | 文字加刪除線 |

### 2.2 標題格式
| 功能 | HTML 標籤 | 說明 |
|------|-----------|------|
| 標題 1 | `<h1>` | 最大標題 |
| 標題 2 | `<h2>` | 次級標題 |
| 標題 3 | `<h3>` | 第三級標題 |
| 標題 4 | `<h4>` | 第四級標題 |
| 標題 5 | `<h5>` | 第五級標題 |
| 標題 6 | `<h6>` | 第六級標題 |
| 一般文字 | `<p>` | 段落文字 |

### 2.3 顏色設定
| 功能 | 屬性 | 說明 |
|------|------|------|
| 文字顏色 | `color` | 選擇文字顏色 |
| 背景顏色 | `background-color` | 選擇背景顏色 |

**預設色盤**：
- 黑色、深灰、灰色、淺灰、白色
- 紅色、橙色、黃色、綠色、藍色、紫色
- 支援自訂顏色 (Color Picker)

### 2.4 列表格式
| 功能 | HTML 標籤 | 說明 |
|------|-----------|------|
| 項目符號列表 | `<ul><li>` | 無序列表（圓點） |
| 編號列表 | `<ol><li>` | 有序列表（數字） |

### 2.5 對齊方式
| 功能 | CSS 屬性 | 說明 |
|------|----------|------|
| 靠左對齊 | `text-align: left` | 預設對齊 |
| 置中對齊 | `text-align: center` | 文字置中 |
| 靠右對齊 | `text-align: right` | 文字靠右 |
| 兩端對齊 | `text-align: justify` | 文字平均分布 |

### 2.6 插入功能
| 功能 | HTML 標籤 | 說明 |
|------|-----------|------|
| 超連結 | `<a href="">` | 插入網址連結 |
| 圖片 | `<img src="">` | 插入圖片 URL |
| 水平線 | `<hr>` | 插入分隔線 |

**圖片插入方式**：僅支援圖片 URL（不提供上傳功能）

### 2.7 其他功能
| 功能 | 說明 |
|------|------|
| 清除格式 | 移除所有格式，還原為純文字 |
| 原始碼編輯 | 不提供（安全性考量） |

---

## 三、技術規格

### 3.1 工具列配置 (Toolbar Modules)

```typescript
const modules = {
  toolbar: [
    // 第一列：標題
    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],

    // 第二列：文字格式
    ['bold', 'italic', 'underline', 'strike'],

    // 第三列：顏色
    [{ 'color': [] }, { 'background': [] }],

    // 第四列：列表與對齊
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    [{ 'align': [] }],

    // 第五列：插入功能
    ['link', 'image'],

    // 第六列：清除格式
    ['clean']
  ]
};
```

### 3.2 格式設定 (Formats)

```typescript
const formats = [
  'header',
  'bold', 'italic', 'underline', 'strike',
  'color', 'background',
  'list', 'bullet',
  'align',
  'link', 'image'
];
```

### 3.3 樣式設定

```css
/* Quill 編輯器容器 */
.quill-editor {
  height: 300px;
  border: 1px solid #ced4da;
  border-radius: 6px;
}

/* 工具列 */
.ql-toolbar {
  background: #f8f9fa;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
}

/* 編輯區域 */
.ql-container {
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 6px;
  font-size: 14px;
  min-height: 250px;
}

/* 檢視模式（唯讀） */
.ql-editor[contenteditable="false"] {
  background: #f5f5f5;
  cursor: not-allowed;
}
```

---

## 四、安全性規範

### 4.1 允許的 HTML 標籤
- 文字: `<p>`, `<span>`, `<br>`
- 格式: `<strong>`, `<em>`, `<u>`, `<s>`
- 標題: `<h1>` ~ `<h6>`
- 列表: `<ul>`, `<ol>`, `<li>`
- 其他: `<a>`, `<img>`, `<hr>`

### 4.2 禁止的 HTML 標籤
- 腳本: `<script>`, `<iframe>`, `<object>`, `<embed>`
- 表單: `<form>`, `<input>`, `<button>`
- 樣式: `<style>` (僅允許 inline style)

### 4.3 屬性白名單
- `<a>`: `href`, `target`, `rel`
- `<img>`: `src`, `alt`, `width`, `height`
- 所有標籤: `style` (限定允許的 CSS 屬性)

### 4.4 XSS 防護
- 後端儲存前進行 HTML 淨化處理
- 使用 `DOMPurify` 或類似工具清理惡意程式碼
- 前端顯示時使用 `dangerouslySetInnerHTML` 並確保內容已淨化

---

## 五、使用者介面

### 5.1 編輯模式
```
┌────────────────────────────────────────┐
│ [H1▼] [B] [I] [U] [S] [A▼] [色] [●▼] │ ← 工具列
├────────────────────────────────────────┤
│                                        │
│  請輸入通知內容...                      │
│                                        │
│                                        │
│                                        │ ← 編輯區域 (300px 高)
│                                        │
│                                        │
│                                        │
└────────────────────────────────────────┘
```

### 5.2 檢視模式
- 工具列隱藏
- 編輯區域背景變灰
- 滑鼠游標顯示為 `not-allowed`
- 內容唯讀 (`contenteditable="false"`)

### 5.3 錯誤狀態
- 必填欄位未填寫時，編輯器邊框變紅色 (`border-color: #e74c3c`)
- 下方顯示錯誤訊息 (紅色文字)

---

## 六、資料處理

### 6.1 儲存格式
- **格式**: HTML 字串
- **編碼**: UTF-8
- **最大長度**: 無限制（資料庫欄位為 TEXT 型別）

### 6.2 輸入範例
```html
<h2>重要通知</h2>
<p>親愛的使用者您好：</p>
<p>系統將於 <strong>2026/01/25</strong> 進行維護，預計停機時間為：</p>
<ul>
  <li>開始時間：2026/01/25 02:00</li>
  <li>結束時間：2026/01/25 06:00</li>
</ul>
<p style="color: red;">維護期間將無法登入系統，敬請見諒。</p>
<p>如有疑問，請洽 <a href="mailto:support@example.com">客服中心</a>。</p>
```

### 6.3 輸出顯示
- 使用 React 的 `dangerouslySetInnerHTML` 渲染 HTML
- 首頁通知 Modal 使用相同方式顯示

---

## 七、相容性

### 7.1 瀏覽器支援
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

### 7.2 響應式設計
- 桌面版：完整工具列
- 平板/手機：工具列自動換行或隱藏部分功能

---

## 八、效能考量

### 8.1 載入優化
- React Quill 使用 CDN 或 npm 安裝
- 編輯器僅在 Modal 打開時初始化

### 8.2 資料大小限制
- 建議單篇通知說明不超過 10,000 字元
- 圖片僅支援 URL（不儲存 Base64）

---

## 九、測試項目

### 9.1 功能測試
- [ ] 文字格式化（粗體、斜體、底線、刪除線）
- [ ] 標題設定（H1-H6）
- [ ] 文字顏色與背景色
- [ ] 項目符號與編號列表
- [ ] 文字對齊（左、中、右、兩端）
- [ ] 插入超連結
- [ ] 插入圖片 URL
- [ ] 插入水平線
- [ ] 清除格式
- [ ] 檢視模式（唯讀）

### 9.2 安全性測試
- [ ] XSS 攻擊防護 (輸入 `<script>alert('test')</script>`)
- [ ] HTML 標籤過濾
- [ ] 惡意 CSS 過濾

### 9.3 使用者體驗測試
- [ ] 編輯器高度適中（300px）
- [ ] 工具列易於操作
- [ ] 錯誤提示清晰
- [ ] 響應式設計正常

---

## 十、套件資訊

### 10.1 安裝指令
```bash
npm install react-quill
```

### 10.2 相依套件
```json
{
  "react-quill": "^2.0.0",
  "quill": "^1.3.7"
}
```

### 10.3 匯入方式
```typescript
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
```

---

## 十一、參考資源

- **React Quill 官方文件**: https://github.com/zenoamaro/react-quill
- **Quill 官方文件**: https://quilljs.com/
- **工具列自訂**: https://quilljs.com/docs/modules/toolbar/
- **格式支援**: https://quilljs.com/docs/formats/

---

**文件版本**: 1.0
**建立日期**: 2026-01-23
**作者**: Claude Sonnet 4.5
