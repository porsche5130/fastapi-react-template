/**
 * System Notifications Service
 * 系統通知相關 API
 */

import axios from '../api/axios';
import {
  SystemNotification,
  SystemNotificationCreate,
  SystemNotificationUpdate,
  UnreadNotificationsResponse,
  GetNotificationsParams
} from '../types/systemNotifications';

// Re-export types for convenience
export type {
  SystemNotification,
  SystemNotificationCreate,
  SystemNotificationUpdate,
  UnreadNotificationsResponse,
  GetNotificationsParams
};

/**
 * 取得系統通知列表（管理功能）
 */
export const getSystemNotifications = async (params?: GetNotificationsParams): Promise<SystemNotification[]> => {
  const response = await axios.get('/api/system_notifications/', { params });
  return response.data;
};

/**
 * 取得當前使用者應該看到的有效通知
 */
export const getActiveNotifications = async (): Promise<SystemNotification[]> => {
  const response = await axios.get('/api/system_notifications/active');
  return response.data;
};

/**
 * 取得當前使用者的未讀通知
 */
export const getUnreadNotifications = async (): Promise<UnreadNotificationsResponse> => {
  const response = await axios.get('/api/system_notifications/unread');
  return response.data;
};

/**
 * 取得單一系統通知
 */
export const getSystemNotification = async (notificationId: number): Promise<SystemNotification> => {
  const response = await axios.get(`/api/system_notifications/${notificationId}`);
  return response.data;
};

/**
 * 建立系統通知
 */
export const createSystemNotification = async (data: SystemNotificationCreate): Promise<SystemNotification> => {
  const response = await axios.post('/api/system_notifications/', data);
  return response.data;
};

/**
 * 更新系統通知
 */
export const updateSystemNotification = async (
  notificationId: number,
  data: SystemNotificationUpdate
): Promise<SystemNotification> => {
  const response = await axios.put(`/api/system_notifications/${notificationId}`, data);
  return response.data;
};

/**
 * 刪除系統通知
 */
export const deleteSystemNotification = async (notificationId: number): Promise<void> => {
  await axios.delete(`/api/system_notifications/${notificationId}`);
};

/**
 * 標記通知為已讀
 */
export const markNotificationAsRead = async (notificationId: number): Promise<void> => {
  await axios.post('/api/system_notifications/mark-as-read', {
    notification_id: notificationId
  });
};

/**
 * 標記所有通知為已讀
 */
export const markAllNotificationsAsRead = async (): Promise<void> => {
  await axios.post('/api/system_notifications/mark-all-as-read');
};
