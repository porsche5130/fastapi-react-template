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

// 是否正在重新整理 token 的旗標
let isRefreshing = false;
// 等待 token 重新整理完成的請求佇列
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

// 處理等待佇列
const processQueue = (error: any = null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// 請求攔截器 - 自動加入 Token
axiosInstance.interceptors.request.use(
  (config) => {
    // 添加 Bearer Token (JWT / session_id)
    const token = localStorage.getItem('session_id') || localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加 Transaction Token (從 localStorage 自動讀取)
    const txnToken = localStorage.getItem('txn_token');
    if (txnToken && !config.headers['X-Txn-Token']) {
      config.headers['X-Txn-Token'] = txnToken;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器 - 處理錯誤與自動重新申請 token
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response) {
      // 401 未授權 - 可能是 token 過期
      if (error.response.status === 401) {
        const errorDetail = error.response.data?.detail || '';

        // 判斷是否為 token 過期 (但 session 仍有效)
        if (errorDetail.includes('交易令牌無效或已過期') && !originalRequest._retry) {
          originalRequest._retry = true;

          // 如果正在重新整理 token,將此請求加入等待佇列
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            })
              .then(() => {
                // token 重新整理完成,重試原請求
                return axiosInstance(originalRequest);
              })
              .catch((err) => {
                return Promise.reject(err);
              });
          }

          isRefreshing = true;

          // 嘗試重新申請 token
          try {
            // 從 localStorage 取得 session_id
            const sessionId = localStorage.getItem('session_id') || localStorage.getItem('access_token');
            if (!sessionId) {
              throw new Error('無 session_id');
            }

            // 重新申請全域 token (使用 login 功能的 token)
            // 注意: 這裡應該呼叫一個專門的 API 來重新整理 token
            // 目前先導向重新登入
            throw new Error('Token 已過期,請重新登入');
          } catch (refreshError) {
            // token 重新整理失敗,清除所有 token 並導向登入頁
            processQueue(refreshError, null);
            localStorage.removeItem('session_id');
            localStorage.removeItem('access_token');
            localStorage.removeItem('txn_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            isRefreshing = false;
          }
        } else {
          // 其他 401 錯誤 (如 session 過期),直接導向登入頁
          localStorage.removeItem('session_id');
          localStorage.removeItem('access_token');
          localStorage.removeItem('txn_token');
          window.location.href = '/login';
        }
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
