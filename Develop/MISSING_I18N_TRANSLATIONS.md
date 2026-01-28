# 缺少的 I18N 翻譯補充

**建立日期**: 2026-01-26

---

## 需要補充的翻譯

根據檢查清單報告，以下功能需要補充 I18N 翻譯:

### 1. roleRights (角色權限設定)

#### zh-TW 翻譯

在 `Develop/frontend/src/locales/zh-TW/translation.json` 中加入:

```json
  "roleRight": {
    "title": "角色權限設定",
    "selectRole": "選擇角色",
    "pleaseSelectRole": "請選擇角色",
    "functionName": "功能名稱",
    "create": "新增",
    "read": "檢視",
    "update": "修改",
    "delete": "刪除",
    "print": "列印",
    "file": "檔案",
    "saveSuccess": "權限設定已儲存",
    "saveFailed": "權限設定儲存失敗",
    "loadFailed": "載入權限設定失敗",
    "noPermissionToUpdate": "您沒有權限修改權限設定"
  },
```

#### en 翻譯

在 `Develop/frontend/src/locales/en/translation.json` 中加入:

```json
  "roleRight": {
    "title": "Role Permissions",
    "selectRole": "Select Role",
    "pleaseSelectRole": "Please Select Role",
    "functionName": "Function Name",
    "create": "Create",
    "read": "Read",
    "update": "Update",
    "delete": "Delete",
    "print": "Print",
    "file": "File",
    "saveSuccess": "Permissions saved successfully",
    "saveFailed": "Failed to save permissions",
    "loadFailed": "Failed to load permissions",
    "noPermissionToUpdate": "You don't have permission to update permissions"
  },
```

---

### 2. systemFunctions (系統功能設定)

**注意**: 前端已有 `sysFunctions` 翻譯，建議統一改為 `systemFunctions`。

#### zh-TW 翻譯更新

在 `Develop/frontend/src/locales/zh-TW/translation.json` 中，如果還沒有 `systemFunctions` 區塊，則加入:

```json
  "systemFunctions": {
    "title": "系統功能設定",
    "funcCode": "功能代碼",
    "funcName": "功能名稱",
    "funcCname": "功能中文名稱",
    "funcEname": "功能英文名稱",
    "funcType": "功能類型",
    "funcOrder": "排序順序",
    "funcIcon": "圖示",
    "upperFuncId": "上層功能",
    "moduleCode": "模組代碼",
    "moduleCodePlaceholder": "例如: users, settings, dashboard",
    "moduleCodeDisabled": "節點類型無需填寫",
    "moduleItem": "可設定權限",
    "description": "功能說明",
    "parent": "上層功能",
    "root": "根節點",
    "isMana": "管理功能",
    "showOnlyMana": "僅顯示管理功能",
    "allTypes": "全部類型",
    "allUpperFunctions": "全部上層節點",
    "rootLevel": "根層級 (0)",
    "searchPlaceholder": "搜尋功能代碼或名稱",
    "permissionHint": "勾選此功能允許設定的操作權限",
    "permissionDisabledHint": "節點類型無需設定操作權限",
    "types": {
      "node": "節點",
      "function": "功能"
    },
    "permissions": {
      "create": "新增",
      "read": "檢視",
      "update": "修改",
      "delete": "刪除",
      "print": "列印",
      "file": "檔案"
    },
    "action": {
      "Create": "新增",
      "Read": "檢視",
      "Update": "修改",
      "Delete": "刪除",
      "Print": "列印",
      "File": "檔案",
      "create": "新增",
      "read": "檢視",
      "update": "修改",
      "delete": "刪除",
      "print": "列印",
      "file": "檔案"
    }
  },
```

#### en 翻譯更新

在 `Develop/frontend/src/locales/en/translation.json` 中加入:

```json
  "systemFunctions": {
    "title": "System Functions",
    "funcCode": "Function Code",
    "funcName": "Function Name",
    "funcCname": "Chinese Name",
    "funcEname": "English Name",
    "funcType": "Function Type",
    "funcOrder": "Sort Order",
    "funcIcon": "Icon",
    "upperFuncId": "Parent Function",
    "moduleCode": "Module Code",
    "moduleCodePlaceholder": "eg: users, settings, dashboard",
    "moduleCodeDisabled": "Node type doesn't need module code",
    "moduleItem": "Available Permissions",
    "description": "Description",
    "parent": "Parent Function",
    "root": "Root",
    "isMana": "Management Function",
    "showOnlyMana": "Show Management Only",
    "allTypes": "All Types",
    "allUpperFunctions": "All Parent Nodes",
    "rootLevel": "Root Level (0)",
    "searchPlaceholder": "Search function code or name",
    "permissionHint": "Check the permissions allowed for this function",
    "permissionDisabledHint": "Node type doesn't need permissions",
    "types": {
      "node": "Node",
      "function": "Function"
    },
    "permissions": {
      "create": "Create",
      "read": "Read",
      "update": "Update",
      "delete": "Delete",
      "print": "Print",
      "file": "File"
    },
    "action": {
      "Create": "Create",
      "Read": "Read",
      "Update": "Update",
      "Delete": "Delete",
      "Print": "Print",
      "File": "File",
      "create": "Create",
      "read": "Read",
      "update": "Update",
      "delete": "Delete",
      "print": "Print",
      "file": "File"
    }
  },
```

---

### 3. system_notifications (系統通知管理)

✅ **已完成** - 前端翻譯檔案中已有完整的 `system_notifications` 翻譯。

---

## 實作建議

### 方式 1: 手動加入 (推薦)

1. 打開 `Develop/frontend/src/locales/zh-TW/translation.json`
2. 在適當位置加入 `roleRight` 區塊
3. 如果需要，加入 `systemFunctions` 區塊（或更新 `sysFunctions`）
4. 對英文翻譯檔案 `Develop/frontend/src/locales/en/translation.json` 做相同操作

### 方式 2: 使用腳本

建立一個 Python 腳本來自動合併翻譯:

```python
import json

# 讀取現有翻譯
with open('Develop/frontend/src/locales/zh-TW/translation.json', 'r', encoding='utf-8') as f:
    zh_tw = json.load(f)

# 加入 roleRight 翻譯
zh_tw['roleRight'] = {
    "title": "角色權限設定",
    # ... 其他翻譯
}

# 寫回檔案
with open('Develop/frontend/src/locales/zh-TW/translation.json', 'w', encoding='utf-8') as f:
    json.dump(zh_tw, f, ensure_ascii=False, indent=2)
```

---

## 檢查清單

- [ ] roleRight zh-TW 翻譯已加入
- [ ] roleRight en 翻譯已加入
- [ ] systemFunctions zh-TW 翻譯已確認（或從 sysFunctions 更新）
- [ ] systemFunctions en 翻譯已確認
- [ ] 前端測試翻譯顯示正常
- [ ] 更新檢查清單狀態

---

**維護者**: 開發團隊
**最後更新**: 2026-01-26
