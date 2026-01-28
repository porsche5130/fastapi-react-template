# 錯誤處理機制改善 - 結構化錯誤訊息

## 問題描述

**使用者反饋**:
1. "目前使用者交易的失敗的交易訊息有點薄弱，無法確實知道發生甚麼事"
2. "希望後端傳送過來的是錯誤代碼跟錯誤訊息"
3. "儲存失敗，這個原因太籠統了~查日誌希望把後端發生錯誤的原因寫入讓使用者日誌查詢時可以有效知道"

**原有問題**:
- 前端只顯示「儲存失敗」等簡單訊息,無法得知具體錯誤原因
- 後端錯誤訊息沒有結構化,只有純文字描述
- 使用者日誌中沒有記錄詳細的錯誤資訊,無法追蹤問題

## 解決方案

### 1. 後端結構化錯誤訊息格式

**新的錯誤回應格式**:
```json
{
  "detail": {
    "error_code": "ERROR_CODE",
    "message": "使用者友善的錯誤訊息",
    "details": "技術細節和堆疊追蹤"
  }
}
```

**錯誤代碼規範**:
- `NUMBERING_RULE_CREATE_FAILED`: 建立編號規則失敗
- `NUMBERING_RULE_UPDATE_FAILED`: 更新編號規則失敗
- `NUMBERING_RULE_DELETE_FAILED`: 刪除編號規則失敗
- `UNKNOWN_ERROR`: 未知錯誤

### 2. 後端修改 - 編號規則 API

**檔案**: `backend/app/routes/numberingrule.py`

#### 2.1 建立編號規則錯誤處理

```python
# 建立規則
try:
    # 排除 org_id,因為要使用 current_user 的組織ID
    rule_dict = rule_data.model_dump(exclude={'org_id'})
    new_rule = SequenceRule(
        **rule_dict,
        org_id=current_user.organization_id,
        created_by=current_user.id
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    logger.info(f"[NumberingRules] 建立編號規則: {new_rule.rule_code} (id={new_rule.id})")

    return new_rule
except Exception as e:
    db.rollback()
    error_msg = str(e)
    logger.error(f"[NumberingRules] 建立編號規則失敗: {error_msg}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error_code": "NUMBERING_RULE_CREATE_FAILED",
            "message": f"建立編號規則失敗: {error_msg}",
            "details": error_msg
        }
    )
```

#### 2.2 更新編號規則錯誤處理

```python
# 更新欄位
try:
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    rule.updated_by = current_user.id

    db.commit()
    db.refresh(rule)
except Exception as e:
    db.rollback()
    error_msg = str(e)
    logger.error(f"[NumberingRules] 更新編號規則失敗: rule_id={rule_id}, error={error_msg}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error_code": "NUMBERING_RULE_UPDATE_FAILED",
            "message": f"更新編號規則失敗: {error_msg}",
            "details": error_msg
        }
    )
```

#### 2.3 刪除編號規則錯誤處理

```python
# 檢查是否有關聯的流水號記錄
try:
    value_count = db.query(SequenceValue).filter(SequenceValue.rule_id == rule_id).count()
    if value_count > 0:
        logger.warning(f"[NumberingRules] 刪除編號規則將同時刪除 {value_count} 筆流水號記錄")

    db.delete(rule)
    db.commit()
except Exception as e:
    db.rollback()
    error_msg = str(e)
    logger.error(f"[NumberingRules] 刪除編號規則失敗: rule_id={rule_id}, error={error_msg}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error_code": "NUMBERING_RULE_DELETE_FAILED",
            "message": f"刪除編號規則失敗: {error_msg}",
            "details": error_msg
        }
    )
```

### 3. 前端修改 - 編號規則頁面

**檔案**: `frontend/src/pages/NumberingRulesPage.tsx`

#### 3.1 儲存錯誤處理 (建立/更新)

```typescript
} catch (error: any) {
  console.error('Save numbering rule failed:', error);

  // 解析後端錯誤訊息
  let errorMsg = t('message.saveFailed');
  let errorCode = 'UNKNOWN_ERROR';
  let errorDetails = '';

  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'object') {
      // 結構化錯誤訊息 (新格式)
      errorCode = detail.error_code || 'UNKNOWN_ERROR';
      errorMsg = detail.message || t('message.saveFailed');
      errorDetails = detail.details || '';
      console.error(`Error Code: ${errorCode}`, errorDetails);
    } else {
      // 簡單字串錯誤訊息 (舊格式)
      errorMsg = detail;
    }
  }

  alert(`儲存失敗\n\n錯誤代碼: ${errorCode}\n錯誤訊息: ${errorMsg}`);

  // 記錄失敗日誌 (包含完整錯誤資訊)
  const fullErrorMsg = errorDetails
    ? `[${errorCode}] ${errorMsg}\n詳細資訊: ${errorDetails}`
    : `[${errorCode}] ${errorMsg}`;

  try {
    if (editingRule) {
      await logUpdate('numbering_rules', editingRule, {}, fullErrorMsg);
    } else {
      await logCreate('numbering_rules', {}, fullErrorMsg);
    }
  } catch (logErr) {
    console.error('[NumberingRulesPage] Failed to log error:', logErr);
  }
}
```

#### 3.2 刪除錯誤處理

```typescript
} catch (error: any) {
  console.error('Delete numbering rule failed:', error);

  // 解析後端錯誤訊息
  let errorMsg = t('message.deleteFailed');
  let errorCode = 'UNKNOWN_ERROR';
  let errorDetails = '';

  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'object') {
      // 結構化錯誤訊息 (新格式)
      errorCode = detail.error_code || 'UNKNOWN_ERROR';
      errorMsg = detail.message || t('message.deleteFailed');
      errorDetails = detail.details || '';
      console.error(`Error Code: ${errorCode}`, errorDetails);
    } else {
      // 簡單字串錯誤訊息 (舊格式)
      errorMsg = detail;
    }
  }

  alert(`刪除失敗\n\n錯誤代碼: ${errorCode}\n錯誤訊息: ${errorMsg}`);

  // 記錄失敗日誌 (包含完整錯誤資訊)
  const fullErrorMsg = errorDetails
    ? `[${errorCode}] ${errorMsg}\n詳細資訊: ${errorDetails}`
    : `[${errorCode}] ${errorMsg}`;

  try {
    await logDelete('numbering_rules', rule, fullErrorMsg);
  } catch (logErr) {
    console.error('[NumberingRulesPage] Failed to log error:', logErr);
  }
}
```

## 改善效果

### 1. 使用者介面改善

**原有訊息**:
```
儲存失敗
```

**新訊息格式**:
```
儲存失敗

錯誤代碼: NUMBERING_RULE_CREATE_FAILED
錯誤訊息: 建立編號規則失敗: duplicate key value violates unique constraint
```

### 2. 使用者日誌改善

**原有日誌**:
```json
{
  "err_detail": "儲存失敗"
}
```

**新日誌格式**:
```json
{
  "err_detail": "[NUMBERING_RULE_CREATE_FAILED] 建立編號規則失敗: duplicate key value violates unique constraint\n詳細資訊: duplicate key value violates unique constraint \"numberingrule_rule_code_org_id_key\""
}
```

### 3. 開發者除錯改善

**Console Log 輸出**:
```javascript
Error Code: NUMBERING_RULE_CREATE_FAILED duplicate key value violates unique constraint "numberingrule_rule_code_org_id_key"
```

## 優點

### 1. 使用者體驗改善
- ✅ 錯誤訊息更明確,使用者能快速了解問題
- ✅ 錯誤代碼提供標準化的錯誤識別方式
- ✅ 使用者可以根據錯誤代碼查詢解決方案

### 2. 系統維護性提升
- ✅ 使用者日誌包含完整錯誤資訊,方便問題追蹤
- ✅ 錯誤代碼統一,便於統計和分析
- ✅ 詳細的技術資訊幫助開發者快速定位問題

### 3. 向後相容性
- ✅ 前端同時支援舊格式 (純文字) 和新格式 (結構化)
- ✅ 不影響現有功能運作
- ✅ 可以逐步遷移其他 API

## 測試驗證

### 測試步驟

1. **測試建立編號規則失敗**:
   - 進入「編號規則設定」頁面
   - 點擊「新增」,輸入資料
   - 故意輸入已存在的規則代碼
   - 點擊「儲存」
   - **預期結果**:
     - 顯示「錯誤代碼: NUMBERING_RULE_CREATE_FAILED」
     - 顯示具體錯誤原因 (例如: 規則代碼已存在)
     - 使用者日誌記錄完整錯誤資訊

2. **測試更新編號規則失敗**:
   - 選擇一個編號規則
   - 點擊「編輯」
   - 修改為無效的資料 (例如: 流水號長度為負數)
   - 點擊「儲存」
   - **預期結果**: 顯示錯誤代碼和詳細錯誤訊息

3. **查詢使用者日誌**:
   - 進入「使用者日誌查詢」頁面
   - 查詢剛才的錯誤操作
   - **預期結果**: `err_detail` 欄位包含 `[錯誤代碼] 錯誤訊息\n詳細資訊: ...`

## 後續建議

### 1. 擴展到其他 API

將此錯誤處理機制應用到其他 API:
- ✅ 編號規則 API (已完成)
- ⬜ 組織管理 API
- ⬜ 使用者管理 API
- ⬜ 角色權限 API
- ⬜ 系統功能 API

### 2. 建立錯誤代碼字典

建立一個中央化的錯誤代碼字典:
```python
# backend/app/core/error_codes.py
class ErrorCode:
    # 編號規則相關
    NUMBERING_RULE_CREATE_FAILED = "NUMBERING_RULE_CREATE_FAILED"
    NUMBERING_RULE_UPDATE_FAILED = "NUMBERING_RULE_UPDATE_FAILED"
    NUMBERING_RULE_DELETE_FAILED = "NUMBERING_RULE_DELETE_FAILED"
    NUMBERING_RULE_NOT_FOUND = "NUMBERING_RULE_NOT_FOUND"
    NUMBERING_RULE_CODE_DUPLICATE = "NUMBERING_RULE_CODE_DUPLICATE"

    # 組織管理相關
    ORGANIZATION_CREATE_FAILED = "ORGANIZATION_CREATE_FAILED"
    # ... 更多錯誤代碼
```

### 3. 前端錯誤處理共用元件

建立一個共用的錯誤處理 utility:
```typescript
// frontend/src/utils/errorHandler.ts
export const parseError = (error: any) => {
  let errorMsg = '操作失敗';
  let errorCode = 'UNKNOWN_ERROR';
  let errorDetails = '';

  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'object') {
      errorCode = detail.error_code || 'UNKNOWN_ERROR';
      errorMsg = detail.message || '操作失敗';
      errorDetails = detail.details || '';
    } else {
      errorMsg = detail;
    }
  }

  return { errorCode, errorMsg, errorDetails };
};

export const formatErrorMessage = (errorCode: string, errorMsg: string) => {
  return `操作失敗\n\n錯誤代碼: ${errorCode}\n錯誤訊息: ${errorMsg}`;
};

export const formatErrorForLog = (errorCode: string, errorMsg: string, errorDetails: string) => {
  return errorDetails
    ? `[${errorCode}] ${errorMsg}\n詳細資訊: ${errorDetails}`
    : `[${errorCode}] ${errorMsg}`;
};
```

### 4. 錯誤訊息國際化

支援多語言錯誤訊息:
```typescript
// frontend/src/locales/zh-TW/errors.json
{
  "NUMBERING_RULE_CREATE_FAILED": "建立編號規則失敗",
  "NUMBERING_RULE_UPDATE_FAILED": "更新編號規則失敗",
  "NUMBERING_RULE_DELETE_FAILED": "刪除編號規則失敗"
}
```

## 相關檔案

### 後端
- `backend/app/routes/numberingrule.py` - 編號規則 API (已修改)

### 前端
- `frontend/src/pages/NumberingRulesPage.tsx` - 編號規則頁面 (已修改)

### 文件
- `Develop/FIX_NUMBERING_RULE_CREATE_ISSUE.md` - 原始問題修正文件
- `Develop/ERROR_HANDLING_IMPROVEMENT.md` - 本文件

## 修正日期

- **日期**: 2026-01-28
- **修正者**: Claude Code
- **版本**: v1.1.0

## 備註

這次改善是基於使用者的實際反饋進行的系統性改進,目標是:
1. 讓使用者能清楚知道發生什麼錯誤
2. 讓日誌系統能記錄完整的錯誤資訊
3. 讓開發者能快速定位和解決問題

這是一個**向後相容**的改進,不會影響現有功能,且可以逐步推廣到整個系統。
