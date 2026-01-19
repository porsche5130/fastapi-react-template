/**
 * 系統設定服務
 */

import api from './api';

export interface SysProfile {
  id: number;
  is_service: boolean;
  sys_url: string;
  sys_ctitle: string;
  sys_etitle: string;
  sys_ccopyright: string;
  sys_ecopyright: string;
  sys_organization: number;
  sys_mana_email: string;
  edit_by: number;
  created_at: string;
  updated_at?: string;
}

export interface SysProfileUpdate {
  is_service?: boolean;
  sys_url?: string;
  sys_ctitle?: string;
  sys_etitle?: string;
  sys_ccopyright?: string;
  sys_ecopyright?: string;
  sys_organization?: number;
  sys_mana_email?: string;
}

/**
 * 取得系統設定
 */
export const getSysProfile = async (): Promise<SysProfile> => {
  const response = await api.get<SysProfile>('/sys_profile/');
  return response.data;
};

/**
 * 更新系統設定
 */
export const updateSysProfile = async (data: SysProfileUpdate): Promise<SysProfile> => {
  const response = await api.put<SysProfile>('/sys_profile/', data);
  return response.data;
};
