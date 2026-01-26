# 交易時間延長機制使用指南

## 概述

當使用者的交易令牌 (Transaction Token) 即將過期時，系統會自動顯示對話框詢問使用者是否延長交易時間。

## 功能特點

1. **自動提示**: 剩餘時間少於 3 分鐘時自動顯示延長確認對話框
2. **使用者選擇**:
   - 選擇「延長 30 分鐘」→ 自動延長 Session ID 和 Transaction Token 有效期至 30 分鐘
   - 選擇「取消交易」→ 撤銷令牌，使用者需要重新進行交易
3. **自動取消**: 如果使用者未回應或時限已超過，自動取消交易

## 使用方式

### 1. 在頁面中使用 Hook

```typescript
import { useTransactionToken } from '../hooks/useTransactionToken';
import TransactionExtendDialog from '../components/TransactionExtendDialog';

const YourPage: React.FC = () => {
  const {
    txnToken,
    permissions,
    loading,
    error,
    remainingSeconds,
    showExtendPrompt,
    handleExtendResponse
  } = useTransactionToken('your_func_code');

  return (
    <>
      {/* 您的頁面內容 */}
      <div>
        {/* ... */}
      </div>

      {/* 交易延長對話框 */}
      <TransactionExtendDialog
        open={showExtendPrompt}
        remainingSeconds={remainingSeconds}
        onExtend={() => handleExtendResponse(true)}
        onCancel={() => handleExtendResponse(false)}
      />
    </>
  );
};
```

### 2. 完整範例: 角色權限設定頁面

```typescript
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Alert
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useTransactionToken } from '../hooks/useTransactionToken';
import TransactionExtendDialog from '../components/TransactionExtendDialog';

const RoleRightsPage: React.FC = () => {
  const { t } = useTranslation();
  const {
    txnToken,
    permissions,
    loading,
    error,
    remainingSeconds,
    showExtendPrompt,
    handleExtendResponse
  } = useTransactionToken('role_rights');

  const [data, setData] = useState([]);

  useEffect(() => {
    if (txnToken) {
      loadData();
    }
  }, [txnToken]);

  const loadData = async () => {
    // 載入資料
  };

  const handleSave = async () => {
    if (!txnToken) {
      alert(t('message.tokenExpired', '交易令牌已過期，請重新載入頁面'));
      return;
    }

    // 使用 txnToken 執行儲存操作
    await saveData(data, txnToken);
  };

  // 如果沒有權限
  if (!permissions) {
    return <Alert severity="error">{t('common.noPermission')}</Alert>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {t('roleRights.title')}
        </Typography>

        {/* 顯示剩餘時間 (可選) */}
        {remainingSeconds > 0 && remainingSeconds < 300 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {t('transaction.remainingTime')}: {Math.floor(remainingSeconds / 60)} 分 {remainingSeconds % 60} 秒
          </Alert>
        )}

        {/* 您的頁面內容 */}
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={!permissions?.update}
        >
          {t('common.save')}
        </Button>
      </Box>

      {/* 交易延長對話框 */}
      <TransactionExtendDialog
        open={showExtendPrompt}
        remainingSeconds={remainingSeconds}
        onExtend={() => handleExtendResponse(true)}
        onCancel={() => handleExtendResponse(false)}
      />
    </Container>
  );
};

export default RoleRightsPage;
```

## 工作流程

```
使用者進入頁面
     ↓
自動申請 Transaction Token (30 分鐘有效)
     ↓
每 30 秒檢查 Token 狀態
     ↓
剩餘時間 < 3 分鐘
     ↓
顯示延長確認對話框
     ↓
   ┌─────┴─────┐
   ↓           ↓
使用者選擇    使用者選擇
「延長」      「取消」或未回應
   ↓           ↓
延長 Token    撤銷 Token
至 30 分鐘    清除頁面狀態
   ↓           ↓
顯示成功訊息  提示重新進行交易
```

## 後端處理

當使用者選擇延長時，前端會重新呼叫 `POST /api/transaction/request`：

```typescript
// 前端延長 Token
const extendToken = async () => {
  // 重新申請 token,後端會自動延長現有 token 的 TTL
  const response = await requestTransactionToken(funcCode);

  // 更新狀態
  setTxnToken(response.txn_token);
  setRemainingSeconds(response.expires_in); // 1800 秒 (30 分鐘)
};
```

後端檢測到同一 session + function 已有有效 token，會自動延長：

```python
# 後端自動延長機制
def get_or_create_function_token(
    session_id: str,
    system_functions_id: int,
    valid_minutes: int = 30
) -> str:
    # 檢查是否已有該 session + function 的 token
    mapping_key = f"session_func_token:{session_id}:{system_functions_id}"
    existing_token = redis_client.get(mapping_key)

    if existing_token:
        # Token 仍然有效，延長有效期至 30 分鐘
        redis_client.expire(token_key, valid_minutes * 60)
        redis_client.expire(mapping_key, valid_minutes * 60)
        return existing_token

    # 否則建立新 token
    # ...
```

## 時間設定參數

可以在 Hook 中調整以下參數：

```typescript
// useTransactionToken.ts

// 剩餘時間少於此秒數時顯示延長提示
// 預設: 180 秒 (3 分鐘)
if (info.remaining_seconds < 180 && info.remaining_seconds > 0) {
  setShowExtendPrompt(true);
}

// 自動取消時間 = 剩餘時間
// 即：從顯示提示開始，使用者有剩餘時間可以回應
extendTimeoutRef.current = setTimeout(async () => {
  // 自動取消交易
  await revokeToken();
}, info.remaining_seconds * 1000);
```

## 翻譯鍵值

### 中文 (zh-TW)

```json
{
  "transaction": {
    "extendTitle": "交易時限即將到期",
    "extendMessage": "您的交易時限即將到期。",
    "remainingTime": "剩餘時間",
    "extendQuestion": "是否延長交易等待時間 30 分鐘？",
    "extendWarning": "如果不延長或未回應，交易將自動取消，需要重新進行。",
    "extend": "延長 30 分鐘",
    "cancel": "取消交易",
    "minutes": "分鐘",
    "seconds": "秒",
    "extended": "已延長 30 分鐘交易時間",
    "cancelled": "交易已取消，請重新進行"
  }
}
```

### 英文 (en)

```json
{
  "transaction": {
    "extendTitle": "Transaction Time Limit Expiring",
    "extendMessage": "Your transaction time limit is about to expire.",
    "remainingTime": "Remaining Time",
    "extendQuestion": "Do you want to extend the transaction waiting time for 30 minutes?",
    "extendWarning": "If you do not extend or respond, the transaction will be automatically cancelled and you will need to start over.",
    "extend": "Extend 30 Minutes",
    "cancel": "Cancel Transaction",
    "minutes": "min",
    "seconds": "sec",
    "extended": "Transaction time extended for 30 minutes",
    "cancelled": "Transaction cancelled, please start over"
  }
}
```

## 注意事項

1. **使用者體驗**:
   - 提示時機設定在剩餘 3 分鐘，給使用者充足時間決定
   - 對話框不能透過 ESC 鍵關閉 (`disableEscapeKeyDown`)
   - 自動聚焦在「延長」按鈕，方便使用者快速回應

2. **安全性**:
   - Session ID 和 Token 同時延長，確保一致性
   - 自動取消機制防止過期 Token 持續佔用 Redis 空間

3. **效能**:
   - 延長機制複用現有 Token，不產生新的
   - 降低 Redis 空間使用率

## 測試案例

### 測試 1: 正常延長流程

1. 進入頁面，等待 27 分鐘
2. 對話框應該顯示：「剩餘時間: 3 分鐘 0 秒」
3. 點擊「延長 30 分鐘」
4. Token 有效期應該更新為 30 分鐘

### 測試 2: 取消交易流程

1. 進入頁面，等待 27 分鐘
2. 對話框顯示
3. 點擊「取消交易」
4. Token 應該被撤銷，頁面應該提示重新載入

### 測試 3: 未回應流程

1. 進入頁面，等待 27 分鐘
2. 對話框顯示
3. 不做任何操作，等待剩餘時間耗盡
4. Token 應該自動撤銷

## 相關檔案

- `Develop/frontend/src/hooks/useTransactionToken.ts` - Token 管理 Hook
- `Develop/frontend/src/components/TransactionExtendDialog.tsx` - 延長對話框元件
- `Develop/frontend/src/locales/zh-TW/translation.json` - 中文翻譯
- `Develop/frontend/src/locales/en/translation.json` - 英文翻譯
- `Develop/backend/app/core/transaction_token_redis.py` - 後端 Token 管理

## 版本資訊

- **版本**: 2.0.0
- **建立日期**: 2026-01-25
- **最後更新**: 2026-01-25
