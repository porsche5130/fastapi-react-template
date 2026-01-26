/**
 * File Upload Component
 * 檔案上傳元件
 */

import React, { useState, useRef } from 'react';
import fileAttachmentsService, { FileUploadParams } from '../services/fileAttachmentsService';
import '../styles/FileUpload.css';

interface FileUploadProps {
  txnToken: string;
  category: 'image' | 'document' | 'archive' | 'video' | 'audio' | 'other';
  businessType?: string;
  relatedTable?: string;
  relatedId?: number;
  accessLevel?: 'public' | 'private' | 'restricted';
  isPublic?: boolean;
  onUploadSuccess?: (fileId: number, fileName: string) => void;
  onUploadError?: (error: any) => void;
  maxSizeMB?: number;
  accept?: string;
  multiple?: boolean;
  autoConfirm?: boolean;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  fileId?: number;
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  txnToken,
  category,
  businessType,
  relatedTable,
  relatedId,
  accessLevel = 'private',
  isPublic = false,
  onUploadSuccess,
  onUploadError,
  maxSizeMB = 50,
  accept,
  multiple = false,
  autoConfirm = true,
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const fileArray = Array.from(files);
    const newUploadingFiles: UploadingFile[] = fileArray.map((file) => ({
      file,
      progress: 0,
      status: 'uploading',
    }));

    setUploadingFiles((prev) => [...prev, ...newUploadingFiles]);

    // 逐一上傳檔案
    fileArray.forEach((file, index) => {
      uploadFile(file, uploadingFiles.length + index);
    });
  };

  const uploadFile = async (file: File, index: number) => {
    // 檢查檔案大小
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      updateFileStatus(index, 'error', 0, undefined, `檔案大小超過 ${maxSizeMB} MB`);
      if (onUploadError) {
        onUploadError({ message: `檔案大小超過 ${maxSizeMB} MB` });
      }
      return;
    }

    try {
      const params: FileUploadParams = {
        file,
        category,
        business_type: businessType,
        related_table: relatedTable,
        related_id: relatedId,
        access_level: accessLevel,
        is_public: isPublic,
      };

      const result = await fileAttachmentsService.upload(params, txnToken, (progress) => {
        updateFileStatus(index, 'uploading', progress);
      });

      // 上傳成功
      updateFileStatus(index, 'success', 100, result.file_id);

      // 自動確認
      if (autoConfirm) {
        await fileAttachmentsService.confirm(result.file_id, txnToken);
      }

      if (onUploadSuccess) {
        onUploadSuccess(result.file_id, file.name);
      }
    } catch (error: any) {
      updateFileStatus(index, 'error', 0, undefined, error.response?.data?.detail || '上傳失敗');
      if (onUploadError) {
        onUploadError(error);
      }
    }
  };

  const updateFileStatus = (
    index: number,
    status: 'uploading' | 'success' | 'error',
    progress: number,
    fileId?: number,
    error?: string
  ) => {
    setUploadingFiles((prev) => {
      const newFiles = [...prev];
      if (newFiles[index]) {
        newFiles[index] = {
          ...newFiles[index],
          status,
          progress,
          fileId,
          error,
        };
      }
      return newFiles;
    });
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    handleFileSelect(files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index: number) => {
    setUploadingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearCompleted = () => {
    setUploadingFiles((prev) => prev.filter((f) => f.status === 'uploading'));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-component">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={(e) => handleFileSelect(e.target.files)}
          style={{ display: 'none' }}
        />
        <div className="upload-icon">📁</div>
        <p className="upload-text">拖曳檔案到此處或點擊上傳</p>
        <p className="upload-hint">
          最大檔案大小: {maxSizeMB} MB {accept && `| 允許格式: ${accept}`}
        </p>
      </div>

      {uploadingFiles.length > 0 && (
        <div className="uploading-files">
          <div className="files-header">
            <h3>上傳檔案 ({uploadingFiles.length})</h3>
            {uploadingFiles.some((f) => f.status === 'success' || f.status === 'error') && (
              <button className="btn-clear" onClick={clearCompleted}>
                清除已完成
              </button>
            )}
          </div>

          <div className="files-list">
            {uploadingFiles.map((uploadingFile, index) => (
              <div key={index} className={`file-item ${uploadingFile.status}`}>
                <div className="file-info">
                  <div className="file-icon">
                    {uploadingFile.status === 'success' ? '✓' : uploadingFile.status === 'error' ? '✗' : '↑'}
                  </div>
                  <div className="file-details">
                    <div className="file-name">{uploadingFile.file.name}</div>
                    <div className="file-size">{formatFileSize(uploadingFile.file.size)}</div>
                    {uploadingFile.error && (
                      <div className="file-error">{uploadingFile.error}</div>
                    )}
                  </div>
                </div>

                <div className="file-actions">
                  {uploadingFile.status === 'uploading' && (
                    <div className="progress-container">
                      <div
                        className="progress-bar"
                        style={{ width: `${uploadingFile.progress}%` }}
                      />
                      <span className="progress-text">{uploadingFile.progress}%</span>
                    </div>
                  )}
                  {(uploadingFile.status === 'success' || uploadingFile.status === 'error') && (
                    <button className="btn-remove" onClick={() => removeFile(index)}>
                      移除
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
