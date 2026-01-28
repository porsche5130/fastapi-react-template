# 個人資料變更 - 編輯按鈕問題修正

## 問題描述

**現象**: 在個人資料變更頁面,點擊「編輯」按鈕後,立即顯示「儲存成功」的訊息,但實際上使用者還沒有修改任何資料。

**問題位置**: `frontend/src/pages/MyProfilePage.tsx`

## 根本原因分析

### 原始程式碼邏輯 (有問題)

```typescript
const handleEdit = async () => {
  setIsEditMode(true);  // ← 1. 先設定編輯模式
  await requestToken(); // ← 2. 然後請求令牌
};
```

### 問題流程

1. **使用者點擊「編輯」按鈕**
2. **立即執行 `setIsEditMode(true)`**
   - 觸發 React 重新渲染
   - 隱藏「編輯」按鈕,顯示「儲存」按鈕
   - 此時輸入欄位變為可編輯
3. **執行 `await requestToken()`**
   - 從 localStorage 讀取已存在的 `txn_token`
   - 幾乎瞬間完成 (因為只是讀取)
   - 設定 `txnToken` state
4. **潛在問題**:
   - 如果按鈕位置堆疊,使用者可能誤觸「儲存」按鈕
   - 或者在快速點擊時,「編輯」和「儲存」按鈕位置重疊
   - 導致表單在沒有修改的情況下被提交
5. **表單提交**:
   - `handleSubmit` 檢查 `txnToken` 存在 ✅
   - 呼叫 API 更新資料 (但資料沒變)
   - 顯示「儲存成功」訊息 ✅
   - 實際上沒有任何變更

## 解決方案

### 1. 調整執行順序

```typescript
const handleEdit = async () => {
  try {
    setIsRequestingToken(true);         // 顯示 loading 狀態
    await requestToken();                // 先請求令牌
    await new Promise(resolve => setTimeout(resolve, 100)); // 等待狀態更新
    setIsEditMode(true);                 // 令牌準備好後才進入編輯模式
  } catch (error) {
    console.error('取得交易令牌失敗:', error);
    alert(t('myProfile.tokenError', '無法取得交易令牌,請重新登入'));
  } finally {
    setIsRequestingToken(false);
  }
};
```

### 2. 新增 Loading 狀態

```typescript
const [isRequestingToken, setIsRequestingToken] = useState(false);
```

### 3. 按鈕禁用與文字提示

```typescript
<button
  type="button"
  onClick={handleEdit}
  className="btn-primary"
  disabled={isRequestingToken}  // 處理中時禁用按鈕
>
  {isRequestingToken ? t('common.loading', '處理中...') : t('common.edit', '編輯')}
</button>
```

## 修正後的流程

1. **使用者點擊「編輯」按鈕**
2. **設定 `isRequestingToken = true`**
   - 按鈕顯示「處理中...」
   - 按鈕被禁用,無法重複點擊
3. **執行 `await requestToken()`**
   - 請求並取得交易令牌
4. **等待 100ms**
   - 確保 React state 更新完成
5. **設定 `isEditMode = true`**
   - 切換到編輯模式
   - 顯示「儲存」和「取消」按鈕
   - 輸入欄位變為可編輯
6. **設定 `isRequestingToken = false`**
   - 完成整個流程

## 優點

### 1. 防止誤觸
- 按鈕切換前有明確的 loading 狀態
- 使用者不會在按鈕切換過程中誤觸

### 2. 更好的使用者體驗
- 按鈕顯示「處理中...」,使用者知道系統正在處理
- 按鈕被禁用,防止重複點擊

### 3. 狀態同步
- 等待 100ms 確保 React state 更新完成
- 避免狀態不一致的問題

### 4. 錯誤處理
- try-catch 包裹整個流程
- 如果取得令牌失敗,不會進入編輯模式
- 顯示明確的錯誤訊息

## 測試驗證

### 測試步驟

1. **正常編輯流程**:
   - 進入個人資料頁面
   - 點擊「編輯」按鈕
   - 應顯示「處理中...」然後切換到編輯模式
   - 修改資料
   - 點擊「儲存」
   - 應顯示「儲存成功」

2. **取消編輯**:
   - 進入編輯模式
   - 修改部分資料
   - 點擊「取消」
   - 資料應恢復為原始值

3. **快速點擊**:
   - 點擊「編輯」按鈕
   - 在切換過程中嘗試快速點擊多次
   - 應該不會有誤觸或重複提交的情況

4. **錯誤情況**:
   - 清除 localStorage 中的 `txn_token`
   - 點擊「編輯」按鈕
   - 應顯示錯誤訊息,不進入編輯模式

## 相關檔案

- **主要檔案**: `frontend/src/pages/MyProfilePage.tsx`
- **Hook**: `frontend/src/hooks/useTransactionToken.ts`
- **API Service**: `frontend/src/services/userService.ts`

## 修正日期

- **日期**: 2026-01-28
- **修正者**: Claude Code
- **版本**: v1.0.1

## 後續建議

1. **統一處理**: 檢查其他頁面是否有類似的問題 (如組織管理、使用者管理等)
2. **共用元件**: 考慮建立一個共用的「編輯/儲存」按鈕元件,統一處理這類邏輯
3. **測試案例**: 建立自動化測試,確保編輯流程正常運作
4. **使用者回饋**: 收集使用者反饋,確認問題已解決

## 備註

此問題的關鍵在於 **React 狀態更新的異步性** 和 **按鈕切換的時機**。通過明確的 loading 狀態和正確的執行順序,可以有效避免使用者誤操作。
