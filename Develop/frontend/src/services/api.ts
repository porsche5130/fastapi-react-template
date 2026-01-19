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
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
