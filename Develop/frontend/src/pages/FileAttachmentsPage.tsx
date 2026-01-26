/**
 * 檔案附件管理頁面
 * File Attachments Management Page
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import fileAttachmentsService, { FileAttachment, FileUploadParams } from '../services/fileAttachmentsService';
import transactionService from '../services/transactionService';
import { useFunctionName } from '../hooks/useFunctionName';
import { logView, logCreate, logUpdate, logDelete } from '../utils/userLogHelper';
import '../styles/DataTable.css';

const FileAttachmentsPage: React.FC = () => {
  const { t } = useTranslation();
  const pageTitle = useFunctionName('file_attachments');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 交易令牌與權限
  const [txnToken, setTxnToken] = useState<string>('');
  const [permissions, setPermissions] = useState({
    read: false,
    create: false,
    update: false,
    delete: false,
    file: false
  });

  // 資料狀態
  const [files, setFiles] = useState<FileAttachment[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  // 搜尋與篩選
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterIsTemp, setFilterIsTemp] = useState<boolean | undefined>(undefined);

  // 分頁
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Modal 狀態
  const [showModal, setShowModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isViewMode, setIsViewMode] = useState(false);
  const [editingFile, setEditingFile] = useState<FileAttachment | null>(null);

  // 表單資料
  const [formData, setFormData] = useState({
    description: '',
    tags: [] as string[],
    access_level: 'private' as 'public' | 'private' | 'restricted',
    is_public: false,
  });

  // 上傳相關
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadParams, setUploadParams] = useState<Partial<FileUploadParams>>({
    category: 'document',
    access_level: 'private',
    is_public: false,
  });

  // 初始化:取得交易令牌和權限
  useEffect(() => {
    const initPage = async () => {
      try {
        const response = await transactionService.requestTransactionToken('file_attachments');
        setTxnToken(response.txn_token);
        setPermissions(response.permissions);

        // 取得資料
        if (response.permissions.read) {
          await loadFiles(response.txn_token);

          // 記錄瀏覽日誌
          await logView('file_attachments', {
            filters: {
              skip: 0,
              limit: 100,
              category: filterCategory || undefined,
              is_temp: filterIsTemp,
              search: searchTerm || undefined
            }
          });
        }
      } catch (error: any) {
        console.error('Init page failed:', error);
        alert(t('common.error'));
      }
    };

    initPage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadFiles = async (token?: string) => {
    const currentToken = token || txnToken;
    if (!currentToken) return;

    setLoading(true);
    try {
      const response = await fileAttachmentsService.getAll(
        0,
        100,
        filterCategory || undefined,
        undefined,
        undefined,
        undefined,
        filterIsTemp,
        searchTerm || undefined,
        currentToken
      );
      setFiles(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      console.error('Load files failed:', error);
      alert(t('message.loadFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadFiles();
  };

  const handleUploadClick = () => {
    setShowUploadModal(true);
    setUploadFile(null);
    setUploadProgress(0);
    setUploadParams({
      category: 'document',
      access_level: 'private',
      is_public: false,
    });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadFile(file);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadParams.category) {
      alert(t('fileAttachments.pleaseSelectFile'));
      return;
    }

    try {
      const params: FileUploadParams = {
        file: uploadFile,
        category: uploadParams.category as any,
        business_type: uploadParams.business_type,
        related_table: uploadParams.related_table,
        related_id: uploadParams.related_id,
        access_level: uploadParams.access_level,
        is_public: uploadParams.is_public,
        description: uploadParams.description,
      };

      const uploaded = await fileAttachmentsService.upload(params, txnToken, setUploadProgress);
      alert(t('message.createSuccess'));
      setShowUploadModal(false);
      await loadFiles();

      // 記錄上傳日誌
      try {
        await logCreate('file_attachments', uploaded);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log create:', logErr);
      }
    } catch (error: any) {
      console.error('Upload failed:', error);
      const errorMsg = error.response?.data?.detail || t('message.saveFailed');
      alert(errorMsg);

      // 記錄失敗日誌
      try {
        await logCreate('file_attachments', {}, errorMsg);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log error:', logErr);
      }
    }
  };

  const handleEdit = (file: FileAttachment, viewMode = false) => {
    setEditingFile(file);
    setIsViewMode(viewMode);
    setFormData({
      description: file.description || '',
      tags: file.tags || [],
      access_level: file.access_level,
      is_public: file.is_public,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!editingFile) return;

    try {
      const updated = await fileAttachmentsService.update(editingFile.id, formData, txnToken);
      alert(t('message.saveSuccess'));
      setShowModal(false);
      await loadFiles();

      // 記錄更新日誌
      try {
        await logUpdate('file_attachments', editingFile, updated);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log update:', logErr);
      }
    } catch (error: any) {
      console.error('Update failed:', error);
      const errorMsg = error.response?.data?.detail || t('message.saveFailed');
      alert(errorMsg);

      // 記錄失敗日誌
      try {
        await logUpdate('file_attachments', editingFile, {}, errorMsg);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log error:', logErr);
      }
    }
  };

  const handleDelete = async (file: FileAttachment) => {
    if (!window.confirm(t('common.confirmDelete'))) return;

    try {
      await fileAttachmentsService.delete(file.id, false, txnToken);
      alert(t('message.deleteSuccess'));
      await loadFiles();

      // 記錄刪除日誌
      try {
        await logDelete('file_attachments', file);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log delete:', logErr);
      }
    } catch (error: any) {
      console.error('Delete failed:', error);
      const errorMsg = error.response?.data?.detail || t('message.deleteFailed');
      alert(errorMsg);

      // 記錄失敗日誌
      try {
        await logDelete('file_attachments', file, errorMsg);
      } catch (logErr) {
        console.error('[FileAttachmentsPage] Failed to log error:', logErr);
      }
    }
  };

  const handleDownload = async (file: FileAttachment) => {
    try {
      await fileAttachmentsService.download(file.id);
    } catch (error: any) {
      console.error('Download failed:', error);
      alert(t('fileAttachments.downloadFailed'));
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getCategoryIcon = (category: string): string => {
    const icons: Record<string, string> = {
      image: '🖼️',
      document: '📄',
      archive: '📦',
      video: '🎥',
      audio: '🎵',
      other: '📁',
    };
    return icons[category] || icons.other;
  };

  // 等待權限載入
  if (!txnToken) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  // 檢查權限
  if (!permissions.read) {
    return (
      <div className="page-container">
        <div className="error-message">{t('common.noPermission')}</div>
      </div>
    );
  }

  const filteredFiles = files;
  const totalPages = Math.ceil(filteredFiles.length / itemsPerPage);
  const displayedFiles = filteredFiles.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{pageTitle}</h1>
        {permissions.create && (
          <button className="btn-primary" onClick={handleUploadClick}>
            {t('fileAttachments.upload')}
          </button>
        )}
      </div>

      {/* 搜尋列 */}
      <div className="search-bar">
        <input
          type="text"
          placeholder={t('fileAttachments.searchPlaceholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <select
          value={filterCategory}
          onChange={(e) => {
            setFilterCategory(e.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="">{t('fileAttachments.allCategories')}</option>
          <option value="image">{t('fileAttachments.categoryImage')}</option>
          <option value="document">{t('fileAttachments.categoryDocument')}</option>
          <option value="archive">{t('fileAttachments.categoryArchive')}</option>
          <option value="video">{t('fileAttachments.categoryVideo')}</option>
          <option value="audio">{t('fileAttachments.categoryAudio')}</option>
          <option value="other">{t('fileAttachments.categoryOther')}</option>
        </select>
        <button className="btn-secondary" onClick={handleSearch}>
          {t('common.search')}
        </button>
      </div>

      {/* 資料表 */}
      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead className="table-header-dark-green">
              <tr>
                <th>{t('fileAttachments.fileName')}</th>
                <th>{t('fileAttachments.category')}</th>
                <th>{t('fileAttachments.fileSize')}</th>
                <th>{t('fileAttachments.uploadTime')}</th>
                <th>{t('fileAttachments.downloadCount')}</th>
                <th>{t('common.status')}</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {displayedFiles.map((file) => (
                <tr key={file.id}>
                  <td>
                    <span>{getCategoryIcon(file.category)}</span> {file.original_name}
                  </td>
                  <td>{t(`fileAttachments.category${file.category.charAt(0).toUpperCase() + file.category.slice(1)}`)}</td>
                  <td>{formatFileSize(file.file_size)}</td>
                  <td>{new Date(file.created_at).toLocaleString('zh-TW')}</td>
                  <td>{file.download_count}</td>
                  <td>
                    <span className={`status-badge ${file.is_temp ? 'inactive' : 'active'}`}>
                      {file.is_temp ? t('fileAttachments.temporary') : t('fileAttachments.confirmed')}
                    </span>
                  </td>
                  <td className="actions">
                    <button
                      className="btn-secondary"
                      onClick={() => handleDownload(file)}
                      style={{ marginRight: '12px' }}
                    >
                      {t('fileAttachments.download')}
                    </button>
                    {permissions.update && (
                      <button className="btn-edit" onClick={() => handleEdit(file, false)}>
                        {t('common.edit')}
                      </button>
                    )}
                    {!permissions.update && permissions.read && (
                      <button className="btn-secondary" onClick={() => handleEdit(file, true)}>
                        {t('common.view')}
                      </button>
                    )}
                    {permissions.delete && (
                      <button className="btn-delete" onClick={() => handleDelete(file)}>
                        {t('common.delete')}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredFiles.length === 0 && (
            <div className="no-data">{t('message.noData')}</div>
          )}

          {/* 分頁 */}
          {filteredFiles.length > 0 && (
            <div className="pagination-container">
              <div className="pagination-info">
                <label>
                  {t('common.itemsPerPage')}：
                  <select
                    value={itemsPerPage}
                    onChange={(e) => {
                      setItemsPerPage(Number(e.target.value));
                      setCurrentPage(1);
                    }}
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                  {t('systemCodes.items')}
                </label>
                <span className="pagination-text">
                  {t('systemCodes.totalRecords', {
                    total: filteredFiles.length,
                    current: currentPage,
                    totalPages: totalPages
                  })}
                </span>
              </div>
              <div className="pagination-buttons">
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                >
                  ⟪
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                >
                  ‹
                </button>
                <button className="btn-pagination active">
                  {currentPage}
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                >
                  ›
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                >
                  ⟫
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 上傳 Modal */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📤 {t('fileAttachments.upload')}</h2>
              <button className="modal-close" onClick={() => setShowUploadModal(false)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>{t('fileAttachments.selectFile')} *</label>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                  />
                  {uploadFile && (
                    <div style={{ marginTop: '10px', color: '#666' }}>
                      {t('fileAttachments.selectedFile')}: {uploadFile.name} ({formatFileSize(uploadFile.size)})
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>{t('fileAttachments.category')} *</label>
                  <select
                    value={uploadParams.category}
                    onChange={(e) => setUploadParams({ ...uploadParams, category: e.target.value as any })}
                    required
                  >
                    <option value="document">{t('fileAttachments.categoryDocument')}</option>
                    <option value="image">{t('fileAttachments.categoryImage')}</option>
                    <option value="archive">{t('fileAttachments.categoryArchive')}</option>
                    <option value="video">{t('fileAttachments.categoryVideo')}</option>
                    <option value="audio">{t('fileAttachments.categoryAudio')}</option>
                    <option value="other">{t('fileAttachments.categoryOther')}</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>{t('fileAttachments.accessLevel')}</label>
                  <select
                    value={uploadParams.access_level}
                    onChange={(e) => setUploadParams({ ...uploadParams, access_level: e.target.value as any })}
                  >
                    <option value="private">{t('fileAttachments.accessPrivate')}</option>
                    <option value="public">{t('fileAttachments.accessPublic')}</option>
                    <option value="restricted">{t('fileAttachments.accessRestricted')}</option>
                  </select>
                </div>

                <div className="form-group full-width">
                  <label>{t('fileAttachments.description')}</label>
                  <textarea
                    value={uploadParams.description || ''}
                    onChange={(e) => setUploadParams({ ...uploadParams, description: e.target.value })}
                    rows={3}
                    placeholder={t('fileAttachments.descriptionPlaceholder')}
                  />
                </div>

                {uploadProgress > 0 && uploadProgress < 100 && (
                  <div className="form-group full-width">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${uploadProgress}%` }}>
                        {uploadProgress}%
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-actions">
              <button
                className="btn-primary"
                onClick={handleUpload}
                disabled={!uploadFile || uploadProgress > 0}
              >
                {t('fileAttachments.upload')}
              </button>
              <button className="btn-secondary" onClick={() => setShowUploadModal(false)}>
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 編輯 Modal */}
      {showModal && editingFile && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                📝 {pageTitle} - {isViewMode ? t('common.viewOperation') : t('common.editOperation')}
              </h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group full-width">
                    <label>{t('fileAttachments.fileName')}</label>
                    <input
                      type="text"
                      value={editingFile.original_name}
                      disabled
                      style={{ backgroundColor: '#f0f0f0' }}
                    />
                  </div>

                  <div className="form-group">
                    <label>{t('fileAttachments.fileSize')}</label>
                    <input
                      type="text"
                      value={formatFileSize(editingFile.file_size)}
                      disabled
                      style={{ backgroundColor: '#f0f0f0' }}
                    />
                  </div>

                  <div className="form-group">
                    <label>{t('fileAttachments.category')}</label>
                    <input
                      type="text"
                      value={t(`fileAttachments.category${editingFile.category.charAt(0).toUpperCase() + editingFile.category.slice(1)}`)}
                      disabled
                      style={{ backgroundColor: '#f0f0f0' }}
                    />
                  </div>

                  <div className="form-group">
                    <label>{t('fileAttachments.accessLevel')}</label>
                    <select
                      value={formData.access_level}
                      onChange={(e) => setFormData({ ...formData, access_level: e.target.value as any })}
                      disabled={isViewMode}
                    >
                      <option value="private">{t('fileAttachments.accessPrivate')}</option>
                      <option value="public">{t('fileAttachments.accessPublic')}</option>
                      <option value="restricted">{t('fileAttachments.accessRestricted')}</option>
                    </select>
                  </div>

                  <div className="form-group full-width">
                    <label>
                      <input
                        type="checkbox"
                        checked={formData.is_public}
                        onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                        disabled={isViewMode}
                      />
                      {t('fileAttachments.isPublic')}
                    </label>
                  </div>

                  <div className="form-group full-width">
                    <label>{t('fileAttachments.description')}</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                      disabled={isViewMode}
                      placeholder={t('fileAttachments.descriptionPlaceholder')}
                    />
                  </div>
                </div>
              </div>
              {!isViewMode && (
                <div className="modal-actions">
                  <button type="submit" className="btn-primary">
                    {t('common.save')}
                  </button>
                  <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                    {t('common.cancel')}
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileAttachmentsPage;
