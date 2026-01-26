/**
 * Transaction Token Hook
 * 交易令牌 Hook - 管理功能級別的交易令牌
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  requestTransactionToken,
  revokeTransactionToken,
  getTokenInfo,
  TransactionTokenResponse
} from '../services/transactionService';

export interface UseTransactionTokenResult {
  txnToken: string | null;
  permissions: {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
    print: boolean;
    file: boolean;
  } | null;
  loading: boolean;
  error: string | null;
  remainingSeconds: number;
  requestToken: () => Promise<void>;
  revokeToken: () => Promise<void>;
  refreshToken: () => Promise<void>;
  extendToken: () => Promise<void>;
  showExtendPrompt: boolean;
  handleExtendResponse: (extend: boolean) => Promise<void>;
}

/**
 * 使用交易令牌 Hook
 *
 * @param funcCode 功能代碼
 * @param autoRequest 是否自動申請令牌(預設 true)
 * @param autoRevoke 是否在元件卸載時自動撤銷令牌(預設 true)
 * @returns 令牌管理物件
 */
export const useTransactionToken = (
  funcCode: string,
  autoRequest: boolean = true,
  autoRevoke: boolean = true
): UseTransactionTokenResult => {
  const [txnToken, setTxnToken] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<TransactionTokenResponse['permissions'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [showExtendPrompt, setShowExtendPrompt] = useState(false);

  const hasRequested = useRef(false);
  const checkIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const extendPromptShown = useRef(false);
  const extendTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 申請令牌
  const requestToken = useCallback(async () => {
    if (!funcCode) {
      setError('功能代碼不能為空');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await requestTransactionToken(funcCode);

      setTxnToken(response.txn_token);
      setPermissions(response.permissions);
      setRemainingSeconds(response.expires_in);

      console.log(`[useTransactionToken] 申請令牌成功: ${funcCode}`, response.permissions);

      // 開始定期檢查令牌狀態
      startTokenCheck(response.txn_token);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '申請令牌失敗';
      setError(errorMsg);
      console.error('[useTransactionToken] 申請令牌失敗:', err);
    } finally {
      setLoading(false);
    }
  }, [funcCode]);

  // 撤銷令牌
  const revokeToken = useCallback(async () => {
    if (!txnToken) return;

    try {
      await revokeTransactionToken(txnToken);
      setTxnToken(null);
      setPermissions(null);
      setRemainingSeconds(0);

      // 停止檢查
      stopTokenCheck();

      console.log(`[useTransactionToken] 撤銷令牌成功: ${funcCode}`);
    } catch (err: any) {
      console.error('[useTransactionToken] 撤銷令牌失敗:', err);
    }
  }, [txnToken, funcCode]);

  // 刷新令牌 (撤銷舊的,申請新的)
  const refreshToken = useCallback(async () => {
    await revokeToken();
    await requestToken();
  }, [revokeToken, requestToken]);

  // 延長令牌 (重新申請以延長有效期)
  const extendToken = useCallback(async () => {
    if (!funcCode) return;

    try {
      // 重新申請 token,後端會自動延長現有 token 的 TTL
      const response = await requestTransactionToken(funcCode);

      setTxnToken(response.txn_token);
      setPermissions(response.permissions);
      setRemainingSeconds(response.expires_in);
      setShowExtendPrompt(false);
      extendPromptShown.current = false;

      console.log(`[useTransactionToken] 延長令牌成功: ${funcCode}, 已延長 30 分鐘`);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '延長令牌失敗';
      setError(errorMsg);
      console.error('[useTransactionToken] 延長令牌失敗:', err);
    }
  }, [funcCode]);

  // 處理使用者延長回應
  const handleExtendResponse = useCallback(async (extend: boolean) => {
    // 清除自動取消計時器
    if (extendTimeoutRef.current) {
      clearTimeout(extendTimeoutRef.current);
      extendTimeoutRef.current = null;
    }

    if (extend) {
      // 使用者選擇延長
      await extendToken();
    } else {
      // 使用者選擇不延長,撤銷 token
      await revokeToken();
      setShowExtendPrompt(false);
      console.log(`[useTransactionToken] 使用者選擇不延長交易時間,已取消交易: ${funcCode}`);
    }
  }, [extendToken, revokeToken, funcCode]);

  // 定期檢查令牌狀態
  const startTokenCheck = (token: string) => {
    stopTokenCheck();

    checkIntervalRef.current = setInterval(async () => {
      try {
        const info = await getTokenInfo(token);
        setRemainingSeconds(info.remaining_seconds);

        // 如果剩餘時間少於 3 分鐘且尚未顯示提示,詢問使用者是否延長
        if (info.remaining_seconds < 180 && info.remaining_seconds > 0 && !extendPromptShown.current) {
          extendPromptShown.current = true;
          setShowExtendPrompt(true);

          console.warn(`[useTransactionToken] 交易時限將抵達 (剩餘 ${Math.floor(info.remaining_seconds / 60)} 分鐘),詢問使用者是否延長`);

          // 設定 3 分鐘後自動取消交易 (如果使用者沒有回應)
          extendTimeoutRef.current = setTimeout(async () => {
            console.warn(`[useTransactionToken] 使用者未回應或時限已超過,自動取消交易: ${funcCode}`);
            await revokeToken();
            setShowExtendPrompt(false);
            extendPromptShown.current = false;
          }, info.remaining_seconds * 1000); // 剩餘時間後自動取消
        }

        // 如果已過期,清除狀態
        if (info.remaining_seconds <= 0) {
          setTxnToken(null);
          setPermissions(null);
          setRemainingSeconds(0);
          setShowExtendPrompt(false);
          extendPromptShown.current = false;
          stopTokenCheck();
        }
      } catch (err) {
        // Token 可能已過期或被撤銷
        setTxnToken(null);
        setPermissions(null);
        setRemainingSeconds(0);
        setShowExtendPrompt(false);
        extendPromptShown.current = false;
        stopTokenCheck();
      }
    }, 30000); // 每 30 秒檢查一次
  };

  // 停止檢查
  const stopTokenCheck = () => {
    if (checkIntervalRef.current) {
      clearInterval(checkIntervalRef.current);
      checkIntervalRef.current = null;
    }
    if (extendTimeoutRef.current) {
      clearTimeout(extendTimeoutRef.current);
      extendTimeoutRef.current = null;
    }
  };

  // 自動申請令牌
  useEffect(() => {
    if (autoRequest && !hasRequested.current) {
      hasRequested.current = true;
      requestToken();
    }
  }, [autoRequest, requestToken]);

  // 元件卸載時自動撤銷令牌
  useEffect(() => {
    return () => {
      stopTokenCheck();

      if (autoRevoke && txnToken) {
        // 使用 navigator.sendBeacon 確保在頁面卸載時仍能發送請求
        const token = localStorage.getItem('access_token');
        if (token) {
          const url = `${window.location.origin}/api/transaction/revoke`;
          const data = new Blob(
            [JSON.stringify({ txn_token: txnToken })],
            { type: 'application/json' }
          );

          // 嘗試使用 fetch keepalive
          fetch(url, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'X-Txn-Token': txnToken,
              'Content-Type': 'application/json'
            },
            body: data,
            keepalive: true
          }).catch(() => {
            // 如果 fetch 失敗,使用 sendBeacon
            navigator.sendBeacon(url, data);
          });
        }

        console.log(`[useTransactionToken] 元件卸載,撤銷令牌: ${funcCode}`);
      }
    };
  }, [autoRevoke, txnToken, funcCode]);

  return {
    txnToken,
    permissions,
    loading,
    error,
    remainingSeconds,
    requestToken,
    revokeToken,
    refreshToken,
    extendToken,
    showExtendPrompt,
    handleExtendResponse
  };
};
