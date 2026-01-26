/**
 * 組織成員維護服務層
 * Tenant Users Service
 */

import axios from '../api/axios';
import { TenantUser, TenantUserCreate, TenantUserUpdate } from '../types/tenantUsers';

const API_BASE = '/api/users';

/**
 * 取得組織成員列表（自動過濾為當前使用者所屬組織）
 */
export const getTenantUsers = async (organizationId: number): Promise<TenantUser[]> => {
  const response = await axios.get<TenantUser[]>(API_BASE, {
    params: { organization_id: organizationId }
  });
  return response.data;
};

/**
 * 取得單一組織成員資料
 */
export const getTenantUser = async (id: number): Promise<TenantUser> => {
  const response = await axios.get<TenantUser>(`${API_BASE}/${id}`);
  return response.data;
};

/**
 * 新增組織成員
 */
export const createTenantUser = async (data: TenantUserCreate): Promise<TenantUser> => {
  const response = await axios.post<TenantUser>(API_BASE, data);
  return response.data;
};

/**
 * 更新組織成員資料
 */
export const updateTenantUser = async (id: number, data: TenantUserUpdate): Promise<TenantUser> => {
  const response = await axios.put<TenantUser>(`${API_BASE}/${id}`, data);
  return response.data;
};

/**
 * 刪除組織成員
 */
export const deleteTenantUser = async (id: number): Promise<void> => {
  await axios.delete(`${API_BASE}/${id}`);
};

/**
 * 重設使用者密碼（發送郵件通知）
 */
export const resetUserPassword = async (userId: number): Promise<void> => {
  await axios.post(`${API_BASE}/${userId}/reset-password`);
};

/**
 * 切換使用者啟用狀態
 */
export const toggleUserStatus = async (id: number, isActive: boolean): Promise<TenantUser> => {
  const response = await axios.put<TenantUser>(`${API_BASE}/${id}`, { is_active: isActive });
  return response.data;
};

/**
 * 檢查帳號唯一性（用於編輯時驗證）
 */
export const checkAccountUniqueness = async (account: string, organizationId: number, excludeId?: number): Promise<boolean> => {
  try {
    const users = await getTenantUsers(organizationId);
    const existingUser = users.find(u => u.account === account && u.id !== excludeId);
    return !existingUser; // true = 唯一，false = 已存在
  } catch (error) {
    console.error('[tenantUsersService] Failed to check account uniqueness:', error);
    return false;
  }
};
