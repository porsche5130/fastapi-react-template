/**
 * File Attachments Service
 * 檔案附件管理服務
 */

import axios from '../api/axios';

export interface FileAttachment {
  id: number;
  original_name: string;
  storage_path: string;
  file_size: number;
  mime_type: string;
  file_hash: string;
  category: 'image' | 'document' | 'archive' | 'video' | 'audio' | 'other';
  business_type?: string;
  related_table?: string;
  related_id?: number;
  access_level: 'public' | 'private' | 'restricted';
  is_public: boolean;
  allowed_roles?: string[];
  allowed_users?: number[];
  is_temp: boolean;
  confirmed_at?: string;
  download_count: number;
  last_downloaded_at?: string;
  version: number;
  previous_version_id?: number;
  thumbnail_path?: string;
  file_metadata?: any;
  description?: string;
  tags?: string[];
  expires_at?: string;
  org_id: number;
  uploaded_by: number;
  created_at: string;
  updated_at?: string;
  download_url?: string;
  thumbnail_url?: string;
}

export interface FileUploadParams {
  file: File;
  category: 'image' | 'document' | 'archive' | 'video' | 'audio' | 'other';
  business_type?: string;
  related_table?: string;
  related_id?: number;
  access_level?: 'public' | 'private' | 'restricted';
  is_public?: boolean;
  description?: string;
}

export interface FileUploadResponse {
  file_id: number;
  original_name: string;
  file_size: number;
  mime_type: string;
  file_hash: string;
  is_duplicate: boolean;
  download_url: string;
  thumbnail_url?: string;
  is_temp: boolean;
  expires_at?: string;
}

const fileAttachmentsService = {
  /**
   * 上傳檔案
   */
  upload: async (
    params: FileUploadParams,
    txnToken: string,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);
    formData.append('category', params.category);
    if (params.business_type) formData.append('business_type', params.business_type);
    if (params.related_table) formData.append('related_table', params.related_table);
    if (params.related_id) formData.append('related_id', params.related_id.toString());
    if (params.access_level) formData.append('access_level', params.access_level);
    if (params.is_public !== undefined)
      formData.append('is_public', params.is_public.toString());
    if (params.description) formData.append('description', params.description);

    const response = await axios.post(`/api/file-attachments/upload`, formData, {
      headers: {
          'X-Txn-Token': txnToken,
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  /**
   * 確認檔案
   */
  confirm: async (fileId: number, txnToken: string) => {
    const response = await axios.post(
      `/api/file-attachments/${fileId}/confirm`,
      {},
      {
        headers: {
              'X-Txn-Token': txnToken,
        },
      }
    );
    return response.data;
  },

  /**
   * 取得檔案列表
   */
  getAll: async (
    skip = 0,
    limit = 20,
    category?: string,
    business_type?: string,
    related_table?: string,
    related_id?: number,
    is_temp?: boolean,
    search?: string,
    txnToken?: string
  ) => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (category) params.append('category', category);
    if (business_type) params.append('business_type', business_type);
    if (related_table) params.append('related_table', related_table);
    if (related_id) params.append('related_id', related_id.toString());
    if (is_temp !== undefined) params.append('is_temp', is_temp.toString());
    if (search) params.append('search', search);

    const headers: any = {
    };
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.get(`/api/file-attachments?${params}`, {
      headers,
    });
    return response.data;
  },

  /**
   * 取得單一檔案資訊
   */
  getById: async (id: number, txnToken?: string): Promise<FileAttachment> => {
    const headers: any = {
    };
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.get(`/api/file-attachments/${id}`, {
      headers,
    });
    return response.data;
  },

  /**
   * 更新檔案資訊
   */
  update: async (id: number, data: Partial<FileAttachment>, txnToken: string) => {
    const response = await axios.put(`/api/file-attachments/${id}`, data, {
      headers: {
          'X-Txn-Token': txnToken,
      },
    });
    return response.data;
  },

  /**
   * 刪除檔案
   */
  delete: async (id: number, physical_delete = false, txnToken?: string) => {
    const params = physical_delete ? '?physical_delete=true' : '';
    const headers: any = {
    };
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.delete(
      `/api/file-attachments/${id}${params}`,
      { headers }
    );
    return response.data;
  },

  /**
   * 下載檔案
   */
  download: async (id: number) => {
    const response = await axios.get(`/api/file-attachments/download/${id}`, {
      headers: {
        },
      responseType: 'blob',
    });

    // 從 Content-Disposition header 取得檔名
    const contentDisposition = response.headers['content-disposition'];
    let filename = `file_${id}`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // 觸發下載
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  /**
   * 清理過期臨時檔案
   */
  cleanup: async (hours = 24, txnToken?: string) => {
    const headers: any = {
    };
    if (txnToken) headers['X-Txn-Token'] = txnToken;

    const response = await axios.post(
      `/api/file-attachments/cleanup?hours=${hours}`,
      {},
      { headers }
    );
    return response.data;
  },
};

export default fileAttachmentsService;
