/**
 * 系統通知服務
 * System Notifications Service
 */

import api from './api';

export interface SystemNotification {
  id: number;
  notice_csubject: string;
  notice_esubject: string;
  notice_cdescription: string;
  notice_edescription: string;
  notice_start_at: string;
  notice_end_at: string;
  notice_order: number;
  is_active: boolean;
  edit_by: number;
  created_at: string;
  updated_at?: string;
}

export interface SystemNotificationCreate {
  notice_csubject: string;
  notice_esubject: string;
  notice_cdescription: string;
  notice_edescription: string;
  notice_start_at: string;
  notice_end_at: string;
  notice_order?: number;
  is_active?: boolean;
}

export interface SystemNotificationUpdate {
  notice_csubject?: string;
  notice_esubject?: string;
  notice_cdescription?: string;
  notice_edescription?: string;
  notice_start_at?: string;
  notice_end_at?: string;
  notice_order?: number;
  is_active?: boolean;
}

export interface TodayNotificationsResponse {
  notifications: SystemNotification[];
}

/**
 * 取得系統通知列表
 */
export const getSystemNotifications = async (params?: {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  notice_order?: number;
  search?: string;
}): Promise<SystemNotification[]> => {
  const response = await api.get<SystemNotification[]>('/system_notifications', { params });
  return response.data;
};

/**
 * 取得單一系統通知
 */
export const getSystemNotification = async (notificationId: number): Promise<SystemNotification> => {
  const response = await api.get<SystemNotification>(`/system_notifications/${notificationId}`);
  return response.data;
};

/**
 * 建立系統通知
 */
export const createSystemNotification = async (data: SystemNotificationCreate): Promise<SystemNotification> => {
  const response = await api.post<SystemNotification>('/system_notifications', data);
  return response.data;
};

/**
 * 更新系統通知
 */
export const updateSystemNotification = async (
  notificationId: number,
  data: SystemNotificationUpdate
): Promise<SystemNotification> => {
  const response = await api.put<SystemNotification>(`/system_notifications/${notificationId}`, data);
  return response.data;
};

/**
 * 刪除系統通知
 */
export const deleteSystemNotification = async (notificationId: number): Promise<void> => {
  await api.delete(`/system_notifications/${notificationId}`);
};

/**
 * 切換通知啟用狀態
 */
export const toggleSystemNotificationActive = async (notificationId: number): Promise<SystemNotification> => {
  const response = await api.patch<SystemNotification>(`/system_notifications/${notificationId}/toggle-active`);
  return response.data;
};

/**
 * 取得今日應顯示的通知（用於 Home 頁面）
 */
export const getHomeNotifications = async (): Promise<TodayNotificationsResponse> => {
  const response = await api.get<TodayNotificationsResponse>('/system_notifications/home/notifications');
  return response.data;
};

/**
 * 標記今日不再顯示通知
 */
export const closeNotificationsToday = async (closedAt?: string): Promise<void> => {
  await api.post('/system_notifications/close-today', { closed_at: closedAt });
};
