/**
 * Numbering Rules Service
 * 編號規則設定服務
 */

import axios from '../api/axios';

export interface SequenceRule {
  id: number;
  rule_code: string;
  rule_name: string;
  description?: string;
  prefix?: string;
  date_format?: string;
  sequence_length: number;
  suffix?: string;
  separator: string;
  reset_mode: 'never' | 'yearly' | 'monthly' | 'daily';
  example?: string;
  is_active: boolean;
  org_id: number;
  created_by: number;
  updated_by?: number;
  created_at: string;
  updated_at?: string;
}

export interface SequenceRuleCreate {
  rule_code: string;
  rule_name: string;
  description?: string;
  prefix?: string;
  date_format?: string;
  sequence_length?: number;
  suffix?: string;
  separator?: string;
  reset_mode?: 'never' | 'yearly' | 'monthly' | 'daily';
  example?: string;
  is_active?: boolean;
  org_id?: number;
}

export interface SequenceRuleUpdate {
  rule_name?: string;
  description?: string;
  prefix?: string;
  date_format?: string;
  sequence_length?: number;
  suffix?: string;
  separator?: string;
  reset_mode?: 'never' | 'yearly' | 'monthly' | 'daily';
  example?: string;
  is_active?: boolean;
}

export interface GenerateNumberRequest {
  rule_code: string;
  custom_date?: string;
}

export interface GenerateNumberResponse {
  number: string;
  rule_code: string;
  sequence_value: number;
  period: string;
  generated_at: string;
}

export interface SequenceValue {
  id: number;
  rule_id: number;
  period: string;
  current_value: number;
  last_generated_at?: string;
  org_id: number;
  created_at: string;
  updated_at?: string;
}

const numberingRulesService = {
  /**
   * 取得編號規則列表
   */
  getAll: async (
    skip = 0,
    limit = 20,
    is_active?: boolean,
    search?: string,
    txnToken?: string
  ) => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (is_active !== undefined) params.append('is_active', is_active.toString());
    if (search) params.append('search', search);

    const headers: any = {};
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.get(`/api/numbering-rules?${params}`, {
      headers,
    });
    return response.data;
  },

  /**
   * 取得單一編號規則
   */
  getById: async (id: number, txnToken?: string) => {
    const headers: any = {};
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.get(`/api/numbering-rules/${id}`, {
      headers,
    });
    return response.data;
  },

  /**
   * 建立編號規則
   */
  create: async (data: SequenceRuleCreate, txnToken: string) => {
    const response = await axios.post(`/api/numbering-rules`, data, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('session_id')}`,
        'X-Txn-Token': txnToken,
      },
    });
    return response.data;
  },

  /**
   * 更新編號規則
   */
  update: async (id: number, data: SequenceRuleUpdate, txnToken: string) => {
    const response = await axios.put(`/api/numbering-rules/${id}`, data, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('session_id')}`,
        'X-Txn-Token': txnToken,
      },
    });
    return response.data;
  },

  /**
   * 刪除編號規則
   */
  delete: async (id: number, txnToken: string) => {
    const response = await axios.delete(`/api/numbering-rules/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('session_id')}`,
        'X-Txn-Token': txnToken,
      },
    });
    return response.data;
  },

  /**
   * 產生編號
   */
  generateNumber: async (request: GenerateNumberRequest): Promise<GenerateNumberResponse> => {
    const response = await axios.post(
      `/api/numbering-rules/generate`,
      request,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('session_id')}`,
        },
      }
    );
    return response.data;
  },

  /**
   * 預覽下一個編號
   */
  previewNumber: async (ruleCode: string, txnToken: string) => {
    const response = await axios.get(
      `/api/numbering-rules/preview/${ruleCode}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('session_id')}`,
          'X-Txn-Token': txnToken,
        },
      }
    );
    return response.data;
  },

  /**
   * 重置流水號
   */
  resetSequence: async (ruleCode: string, period?: string, txnToken?: string) => {
    const params = period ? `?period=${period}` : '';
    const headers: any = {};
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.post(
      `/api/numbering-rules/reset/${ruleCode}${params}`,
      {},
      { headers }
    );
    return response.data;
  },

  /**
   * 取得流水號記錄
   */
  getSequenceValues: async (ruleCode: string, txnToken: string): Promise<SequenceValue[]> => {
    const response = await axios.get(
      `/api/numbering-rules/${ruleCode}/values`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('session_id')}`,
          'X-Txn-Token': txnToken,
        },
      }
    );
    return response.data;
  },
};

export default numberingRulesService;
