/**
 * 組織資料維護服務
 */

import axios from '../api/axios';
import { TenantProfile, TenantProfileUpdate } from '../types/tenantProfile';

const API_BASE = '/api/organizations';

/**
 * 取得當前使用者所屬組織資料
 */
export const getMyTenantProfile = async (): Promise<TenantProfile> => {
  try {
    // 先取得組織列表（會自動過濾為當前使用者的組織）
    const response = await axios.get<TenantProfile[]>(API_BASE);

    if (response.data && response.data.length > 0) {
      return response.data[0];
    }

    throw new Error('找不到組織資料');
  } catch (error) {
    console.error('[TenantProfileService] Failed to get my tenant profile:', error);
    throw error;
  }
};

/**
 * 更新組織資料
 */
export const updateTenantProfile = async (
  id: number,
  data: TenantProfileUpdate
): Promise<TenantProfile> => {
  try {
    const response = await axios.put<TenantProfile>(`${API_BASE}/${id}`, data);
    return response.data;
  } catch (error) {
    console.error('[TenantProfileService] Failed to update tenant profile:', error);
    throw error;
  }
};
