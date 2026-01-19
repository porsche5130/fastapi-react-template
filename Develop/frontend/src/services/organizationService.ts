/**
 * 組織單位服務
 */

import api from './api';

export interface Organization {
  id: number;
  org_code: string;
  org_name: string;
  org_type: number;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  address?: string;
  phone?: string;
  is_mana: boolean;
  is_active: boolean;
  memo?: string;
  edit_by: number;
  created_at: string;
  updated_at?: string;
}

export interface OrganizationCreate {
  org_code: string;
  org_name: string;
  org_type: number;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  address?: string;
  phone?: string;
  is_mana?: boolean;
  is_active?: boolean;
  memo?: string;
}

export interface OrganizationUpdate {
  org_code?: string;
  org_name?: string;
  org_type?: number;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  phone?: string;
  is_mana?: boolean;
  is_active?: boolean;
  memo?: string;
}

/**
 * 取得組織單位列表
 */
export const getOrganizations = async (params?: {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  search?: string;
}): Promise<Organization[]> => {
  const response = await api.get<Organization[]>('/organizations', { params });
  return response.data;
};

/**
 * 取得組織單位資訊
 */
export const getOrganization = async (organizationId: number): Promise<Organization> => {
  const response = await api.get<Organization>(`/organizations/${organizationId}`);
  return response.data;
};

/**
 * 建立組織單位
 */
export const createOrganization = async (data: OrganizationCreate): Promise<Organization> => {
  const response = await api.post<Organization>('/organizations', data);
  return response.data;
};

/**
 * 更新組織單位
 */
export const updateOrganization = async (
  organizationId: number,
  data: OrganizationUpdate
): Promise<Organization> => {
  const response = await api.put<Organization>(`/organizations/${organizationId}`, data);
  return response.data;
};

/**
 * 刪除組織單位
 */
export const deleteOrganization = async (organizationId: number): Promise<void> => {
  await api.delete(`/organizations/${organizationId}`);
};
