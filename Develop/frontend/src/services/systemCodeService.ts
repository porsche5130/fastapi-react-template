/**
 * 系統代碼服務
 */

import api from './api';

export interface SystemCode {
  id: number;
  code_etype: string;
  code_ctype: string;
  code: string;
  code_cname: string;
  code_ename?: string;
  order: number;
  is_active: boolean;
  note1?: string;
  note2?: string;
  note3?: string;
  note4?: string;
  note5?: string;
  edit_by: number;
  created_at: string;
  updated_at: string;
}

export interface SystemCodeCreate {
  code_etype: string;
  code_ctype: string;
  code: string;
  code_cname: string;
  code_ename?: string;
  order?: number;
  is_active?: boolean;
  note1?: string;
  note2?: string;
  note3?: string;
  note4?: string;
  note5?: string;
}

export interface SystemCodeUpdate {
  code_etype?: string;
  code_ctype?: string;
  code?: string;
  code_cname?: string;
  code_ename?: string;
  order?: number;
  is_active?: boolean;
  note1?: string;
  note2?: string;
  note3?: string;
  note4?: string;
  note5?: string;
}

/**
 * 取得系統代碼列表
 */
export const getSystemCodes = async (params?: {
  code_etype?: string;
  code_ctype?: string;
  code?: string;
  code_cname?: string;
  code_ename?: string;
  is_active?: boolean;
  search?: string;
}): Promise<SystemCode[]> => {
  const response = await api.get<SystemCode[]>('/system_codes', { params });
  return response.data;
};

/**
 * 取得系統代碼資訊
 */
export const getSystemCode = async (codeId: number): Promise<SystemCode> => {
  const response = await api.get<SystemCode>(`/system_codes/${codeId}`);
  return response.data;
};

/**
 * 建立系統代碼
 */
export const createSystemCode = async (data: SystemCodeCreate): Promise<SystemCode> => {
  const response = await api.post<SystemCode>('/system_codes', data);
  return response.data;
};

/**
 * 更新系統代碼
 */
export const updateSystemCode = async (
  codeId: number,
  data: SystemCodeUpdate
): Promise<SystemCode> => {
  const response = await api.put<SystemCode>(`/system_codes/${codeId}`, data);
  return response.data;
};

/**
 * 刪除系統代碼
 */
export const deleteSystemCode = async (codeId: number): Promise<void> => {
  await api.delete(`/system_codes/${codeId}`);
};

/**
 * 根據代碼類別查詢
 */
export const getSystemCodesByType = async (
  codeEtype: string,
  codeCtype?: string,
  activeOnly: boolean = true
): Promise<SystemCode[]> => {
  const params = new URLSearchParams({ active_only: String(activeOnly) });
  if (codeCtype) {
    params.append('code_ctype', codeCtype);
  }
  const response = await api.get<SystemCode[]>(`/system_codes/type/${codeEtype}?${params.toString()}`);
  return response.data;
};
