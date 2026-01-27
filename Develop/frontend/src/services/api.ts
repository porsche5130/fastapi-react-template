/**
 * API 客戶端設定
 */

import axios from 'axios';

// 建立 axios 實例
const api = axios.create({
  baseURL: 'http://localhost:10181/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器 - 自動加入 Token
api.interceptors.request.use(
  (config) => {
    // 添加 Bearer Token (JWT)
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加 Transaction Token (v3.0)
    const txnToken = localStorage.getItem('txn_token');
    if (txnToken) {
      config.headers['X-Txn-Token'] = txnToken;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器 - 處理錯誤
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 失效，清除並導向登入頁
      localStorage.removeItem('access_token');
      localStorage.removeItem('txn_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
