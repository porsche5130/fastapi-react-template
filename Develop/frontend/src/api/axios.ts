/**
 * Axios 配置
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:10181';

// 建立 axios 實例
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器 - 自動加入 Token
axiosInstance.interceptors.request.use(
  (config) => {
    // 優先使用 session_id (新版)，降級使用 access_token (舊版)
    const token = localStorage.getItem('session_id') || localStorage.getItem('access_token');
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
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // 401 未授權 - 清除 Token 並跳轉登入頁
      if (error.response.status === 401) {
        localStorage.removeItem('session_id');
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
      // 403 禁止存取
      else if (error.response.status === 403) {
        console.error('禁止存取:', error.response.data.detail);
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
