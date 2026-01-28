# 刪除編號規則功能

## 刪除原因

**業務需求評估**: 編號規則 (叫號功能) 屬於高度客製化功能,每個客戶的需求差異極大,無法用一個通用的設定介面滿足所有需求。

### 實際情況

1. **客製化程度高**: 每個組織的編號規則差異很大,需要深度訪談才能確定
2. **架構限制**: 目前的規則架構無法滿足所有可能的編號格式需求
3. **實施方式**: 實際上應該在訪談後直接在程式碼中實現,而不是透過設定介面

### 設計決策

- ❌ **不適合**: 作為通用功能提供設定介面
- ✅ **適合**: 在專案實施時依客戶需求客製化開發

## 刪除內容

### 1. 資料庫

**刪除的資料表**:
- `sequence_rules` (編號規則表)
- `sequence_values` (編號流水號表)

**刪除的資料**:
- `system_functions` 中的 func_code='numbering_rules' 記錄 (1筆)
- `role_rights` 中相關的權限記錄 (4筆)

**執行腳本**: `migrations/drop_sequence_rules.sql`

### 2. Backend 程式碼

**刪除的檔案**:
- `app/models/numberingrule.py` - Model 定義
- `app/schemas/numberingrule.py` - Schema 定義
- `app/routes/numberingrule.py` - API 路由

**修改的檔案**:
- `app/main.py` - 移除路由註冊和 import

### 3. Frontend 程式碼

**刪除的檔案**:
- `src/pages/NumberingRulesPage.tsx` - 頁面元件
- `src/services/numberingRulesService.ts` - API Service

**修改的檔案**:
- `src/App.tsx` - 移除路由和 import

### 4. 文件檔案

**刪除的文件**:
- `FIX_NUMBERING_RULE_CREATE_ISSUE.md` - 之前修正編號規則問題的文件

## 執行結果

### 資料庫清理
```
[OK] Deleted role_rights: 4 rows
[OK] Deleted system_functions: 1 rows
[OK] Table sequence_values dropped
[OK] Table sequence_rules dropped
```

### 程式碼清理
```
[OK] Deleted app/models/numberingrule.py
[OK] Deleted app/schemas/numberingrule.py
[OK] Deleted app/routes/numberingrule.py
[OK] Updated app/main.py
[OK] Deleted NumberingRulesPage.tsx
[OK] Deleted numberingRulesService.ts
[OK] Updated App.tsx
```

## 後續處理

### 如果未來需要編號規則功能

1. **評估需求**: 深入訪談客戶,了解具體的編號規則需求
2. **客製化開發**: 在程式碼中直接實現特定的編號邏輯
3. **實施方式**:
   - 選項 A: 在業務模組中內建編號邏輯
   - 選項 B: 建立客製化的編號生成服務
   - 選項 C: 使用資料庫 Sequence 或自訂 Function

### 注意事項

- 編號規則是**業務核心功能**,需要非常謹慎的設計
- 不同產業、不同公司對編號格式的要求差異極大
- 應該在專案實施階段根據實際需求設計,而不是預先建立通用功能

## 刪除時間

- **刪除日期**: 2026-01-29
- **執行者**: Claude Code
- **版本**: v1.0.0

## 相關決策記錄

### 討論記錄

**使用者觀點**:
> "每組叫號規則/編號規則，都是系統訪談後依照客戶需求進行該公司/組織標準化作業，規則的架構也不一定是我們的這樣設定就可以解決的規則"

**結論**: 移除通用編號規則功能,改為專案實施時客製化開發。

## 檔案歷史

- **建立日期**: 2026-01-29
- **建立者**: Claude Code
