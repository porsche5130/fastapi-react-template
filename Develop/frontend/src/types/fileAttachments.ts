/**
 * File Attachments Types
 * 檔案附件管理相關類型定義
 */

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
  file_metadata?: Record<string, any>;
  description?: string;
  tags?: string[];

  expires_at?: string;

  org_id: number;
  uploaded_by: number;
  created_at: string;
  updated_at?: string;

  // 額外欄位 (前端用)
  download_url?: string;
  thumbnail_url?: string;
}

export interface FileAttachmentCreate {
  category: 'image' | 'document' | 'archive' | 'video' | 'audio' | 'other';
  business_type?: string;
  related_table?: string;
  related_id?: number;
  access_level?: 'public' | 'private' | 'restricted';
  is_public?: boolean;
  allowed_roles?: string[];
  allowed_users?: number[];
  description?: string;
  tags?: string[];
  expires_at?: string;
  org_id?: number;
}

export interface FileAttachmentUpdate {
  description?: string;
  tags?: string[];
  access_level?: 'public' | 'private' | 'restricted';
  is_public?: boolean;
  allowed_roles?: string[];
  allowed_users?: number[];
  expires_at?: string;
}

export interface FileAttachmentListResponse {
  total: number;
  items: FileAttachment[];
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

export interface FileConfirmResponse {
  message: string;
  file_id: number;
  confirmed_at: string;
}

export interface GetFileAttachmentsParams {
  skip?: number;
  limit?: number;
  category?: string;
  business_type?: string;
  related_table?: string;
  related_id?: number;
  is_temp?: boolean;
  search?: string;
}
