/**
 * Transaction Token Service
 * 交易令牌服務
 */

import axios from '../api/axios';

export interface TransactionTokenRequest {
  func_code: string;
}

export interface TransactionTokenResponse {
  txn_token: string;
  expires_in: number;  // 秒數
  func_code: string;
  permissions: {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
    print: boolean;
    file: boolean;
  };
}

export interface TokenInfo {
  func_code: string;
  remaining_seconds: number;
  used: boolean;
}

/**
 * 申請功能交易令牌
 *
 * @param funcCode 功能代碼
 * @returns 交易令牌資訊
 */
export const requestTransactionToken = async (
  funcCode: string
): Promise<TransactionTokenResponse> => {
  const response = await axios.post('/api/transaction/request', {
    func_code: funcCode
  });
  return response.data;
};

/**
 * 查詢令牌資訊
 *
 * @param txnToken 交易令牌
 * @returns 令牌資訊
 */
export const getTokenInfo = async (txnToken: string): Promise<TokenInfo> => {
  const response = await axios.get('/api/transaction/info', {
    headers: {
      'X-Txn-Token': txnToken
    }
  });
  return response.data;
};

/**
 * 撤銷交易令牌
 *
 * @param txnToken 交易令牌
 */
export const revokeTransactionToken = async (txnToken: string): Promise<void> => {
  await axios.post(
    '/api/transaction/revoke',
    {},
    {
      headers: {
        'X-Txn-Token': txnToken
      }
    }
  );
};

/**
 * 為 axios 請求添加交易令牌 header
 *
 * @param txnToken 交易令牌
 * @returns axios 請求配置
 */
export const withTxnToken = (txnToken: string) => {
  return {
    headers: {
      'X-Txn-Token': txnToken
    }
  };
};
