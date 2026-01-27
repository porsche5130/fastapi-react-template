/**
 * 認證相關 API
 */

import axios from './axios';
import { LoginRequest, TokenResponse, UserProfile } from '../types';

export const authService = {
  /**
   * 使用者登入
   */
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await axios.post('/api/auth/login', data);
    return response.data;
  },

  /**
   * 取得當前使用者資訊
   */
  getCurrentUser: async (): Promise<UserProfile> => {
    const response = await axios.get('/api/auth/me');
    return response.data;
  },

  /**
   * 使用者登出
   */
  logout: async (): Promise<void> => {
    await axios.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('txn_token');
  },

  /**
   * 檢查是否已登入
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * 儲存 Token
   */
  saveToken: (token: string): void => {
    localStorage.setItem('access_token', token);
  },

  /**
   * 儲存 Transaction Token
   */
  saveTxnToken: (txnToken: string): void => {
    localStorage.setItem('txn_token', txnToken);
  },

  /**
   * 取得 Transaction Token
   */
  getTxnToken: (): string | null => {
    return localStorage.getItem('txn_token');
  },

  /**
   * 清除 Token
   */
  clearToken: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('txn_token');
  },
};
