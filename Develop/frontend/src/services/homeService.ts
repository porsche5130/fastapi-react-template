/**
 * Home Service
 * 首頁相關 API 服務
 */

import axios from 'axios';

const API_BASE = '/api/home';

/**
 * 首頁統計資訊介面
 */
export interface HomeStats {
  totalProjects: number;
  activeProjects: number;
  pendingTasks: number;
  completedTasks: number;
}

/**
 * 最近活動介面
 */
export interface RecentActivity {
  id: number;
  title: string;
  description: string;
  timestamp: string;
  type: 'create' | 'update' | 'delete' | 'login';
}

/**
 * 取得首頁統計資訊
 */
export const getHomeStats = async (): Promise<HomeStats> => {
  const response = await axios.get(`${API_BASE}/stats`);
  return response.data;
};

/**
 * 取得最近活動記錄
 */
export const getRecentActivities = async (limit: number = 10): Promise<RecentActivity[]> => {
  const response = await axios.get(`${API_BASE}/activities`, {
    params: { limit }
  });
  return response.data;
};

/**
 * 取得快速連結
 */
export const getQuickLinks = async () => {
  const response = await axios.get(`${API_BASE}/quick-links`);
  return response.data;
};
