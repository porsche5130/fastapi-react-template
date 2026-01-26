/**
 * 組織成員維護頁面
 * Tenant Users Page
 *
 * 功能說明：
 * 1. 讀取權限：檢視組織成員列表（唯讀模式）
 * 2. 新增權限：新增組織成員（含密碼確認）
 * 3. 修改權限：修改成員資料（帳號可修改但需檢查唯一性）
 * 4. 刪除權限：刪除組織成員（含確認對話框）
 * 5. 重設密碼：發送密碼重設郵件
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { TenantUser, TenantUserCreate, TenantUserUpdate } from '../types/tenantUsers';
import {
  getTenantUsers,
  createTenantUser,
  updateTenantUser,
  deleteTenantUser,
  resetUserPassword,
  toggleUserStatus,
  checkAccountUniqueness
} from '../services/tenantUsersService';
import { useAuth } from '../contexts/AuthContext';
import { usePermission } from '../hooks/usePermission';
import { useFunctionName } from '../hooks/useFunctionName';
import { logView, logCreate, logUpdate, logDelete } from '../utils/userLogHelper';
import '../styles/DataTable.css';

const TenantUsersPage: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { hasPermission, loading: permissionLoading } = usePermission();
  const pageTitle = useFunctionName('tenant_users');
  const hasInitialized = useRef(false);

  const [users, setUsers] = useState<TenantUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [currentUser, setCurrentUser] = useState<TenantUser | null>(null);

  // Form states
  const [createForm, setCreateForm] = useState<TenantUserCreate & { confirmPassword: string }>({
    account: '',
    username: '',
    password: '',
    confirmPassword: '',
    department: '',
    job_title: '',
    phone: '',
    user_role: [],
    is_active: true
  });

  const [editForm, setEditForm] = useState<TenantUserUpdate>({
    account: '',
    username: '',
    department: '',
    job_title: '',
    phone: '',
    user_role: [],
    is_active: true
  });

  // 檢查權限
  const canRead = hasPermission('tenant_users', 'read');
  const canCreate = hasPermission('tenant_users', 'create');
  const canUpdate = hasPermission('tenant_users', 'update');
  const canDelete = hasPermission('tenant_users', 'delete');

  // 載入組織成員列表
  const loadUsers = async () => {
    if (!user?.organization_id) {
      setError(t('common.error'));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getTenantUsers(user.organization_id);
      setUsers(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!permissionLoading && canRead && !hasInitialized.current) {
      hasInitialized.current = true;
      const initPage = async () => {
        try {
          await loadUsers();
          await logView('tenant_users', {}, null);
        } catch (err: any) {
          const errorMsg = err.response?.data?.detail || err.message || t('message.loadFailed');
          await logView('tenant_users', {}, errorMsg);
        }
      };
      initPage();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [permissionLoading, canRead]);

  // 開啟新增視窗
  const handleOpenCreate = () => {
    if (!canCreate) {
      alert(t('message.noPermission'));
      return;
    }
    setCreateForm({
      account: '',
      username: '',
      password: '',
      confirmPassword: '',
      department: '',
      job_title: '',
      phone: '',
      user_role: [],
      is_active: true
    });
    setShowCreateModal(true);
  };

  // 新增成員
  const handleCreate = async () => {
    // 驗證必填欄位
    if (!createForm.account || !createForm.username || !createForm.password) {
      alert(t('message.pleaseComplete'));
      return;
    }

    // 驗證 Email 格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(createForm.account)) {
      alert(t('tenantUsers.invalidEmail'));
      return;
    }

    // 驗證密碼確認
    if (createForm.password !== createForm.confirmPassword) {
      alert(t('tenantUsers.passwordMismatch'));
      return;
    }

    // 檢查帳號唯一性
    if (!user?.organization_id) {
      alert(t('common.error'));
      return;
    }
    const isUnique = await checkAccountUniqueness(createForm.account, user.organization_id);
    if (!isUnique) {
      alert(t('tenantUsers.accountExists'));
      return;
    }

    try {
      setLoading(true);
      const { confirmPassword, ...dataToSend } = createForm;
      const newUser = await createTenantUser(dataToSend);
      setUsers([...users, newUser]);
      setShowCreateModal(false);
      alert(t('message.createSuccess'));

      // 記錄日誌
      try {
        await logCreate('tenant_users', newUser);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log create:', logErr);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('message.createFailed');
      alert(errorMsg);

      // 記錄錯誤日誌
      try {
        await logCreate('tenant_users', createForm, errorMsg);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log error:', logErr);
      }
    } finally {
      setLoading(false);
    }
  };

  // 開啟編輯視窗
  const handleOpenEdit = (user: TenantUser) => {
    if (!canUpdate) {
      alert(t('message.noPermission'));
      return;
    }
    setCurrentUser(user);
    setEditForm({
      account: user.account,
      username: user.username,
      department: user.department,
      job_title: user.job_title,
      phone: user.phone,
      user_role: user.user_role,
      is_active: user.is_active
    });
    setShowEditModal(true);
  };

  // 更新成員
  const handleUpdate = async () => {
    if (!currentUser) return;

    // 驗證必填欄位
    if (!editForm.account || !editForm.username) {
      alert(t('message.pleaseComplete'));
      return;
    }

    // 驗證 Email 格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(editForm.account)) {
      alert(t('tenantUsers.invalidEmail'));
      return;
    }

    // 檢查帳號唯一性（如果帳號有變更）
    if (editForm.account !== currentUser.account) {
      if (!user?.organization_id) {
        alert(t('common.error'));
        return;
      }
      const isUnique = await checkAccountUniqueness(editForm.account, user.organization_id, currentUser.id);
      if (!isUnique) {
        alert(t('tenantUsers.accountExists'));
        return;
      }
    }

    try {
      setLoading(true);
      const originalData = { ...currentUser };
      const updatedUser = await updateTenantUser(currentUser.id, editForm);
      setUsers(users.map(u => (u.id === currentUser.id ? updatedUser : u)));
      setShowEditModal(false);
      alert(t('message.updateSuccess'));

      // 記錄日誌
      try {
        await logUpdate('tenant_users', originalData, updatedUser);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log update:', logErr);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('message.updateFailed');
      alert(errorMsg);

      // 記錄錯誤日誌
      try {
        await logUpdate('tenant_users', currentUser, editForm, errorMsg);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log error:', logErr);
      }
    } finally {
      setLoading(false);
    }
  };

  // 刪除成員
  const handleDelete = async (user: TenantUser) => {
    if (!canDelete) {
      alert(t('message.noPermission'));
      return;
    }

    if (!window.confirm(t('tenantUsers.confirmDelete', { username: user.username }))) {
      return;
    }

    try {
      setLoading(true);
      await deleteTenantUser(user.id);
      setUsers(users.filter(u => u.id !== user.id));
      alert(t('message.deleteSuccess'));

      // 記錄日誌
      try {
        await logDelete('tenant_users', user);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log delete:', logErr);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('message.deleteFailed');
      alert(errorMsg);

      // 記錄錯誤日誌
      try {
        await logDelete('tenant_users', user, errorMsg);
      } catch (logErr) {
        console.error('[TenantUsersPage] Failed to log error:', logErr);
      }
    } finally {
      setLoading(false);
    }
  };

  // 重設密碼
  const handleResetPassword = async (user: TenantUser) => {
    if (!canUpdate) {
      alert(t('message.noPermission'));
      return;
    }

    if (!window.confirm(t('tenantUsers.confirmResetPassword', { username: user.username }))) {
      return;
    }

    try {
      setLoading(true);
      await resetUserPassword(user.id);
      alert(t('tenantUsers.resetPasswordSuccess'));
    } catch (err: any) {
      alert(err.response?.data?.detail || t('tenantUsers.resetPasswordFailed'));
    } finally {
      setLoading(false);
    }
  };

  // 切換啟用狀態
  const handleToggleStatus = async (user: TenantUser) => {
    if (!canUpdate) {
      alert(t('message.noPermission'));
      return;
    }

    try {
      setLoading(true);
      const updatedUser = await toggleUserStatus(user.id, !user.is_active);
      setUsers(users.map(u => (u.id === user.id ? updatedUser : u)));
      alert(t('message.updateSuccess'));
    } catch (err: any) {
      alert(err.response?.data?.detail || t('message.updateFailed'));
    } finally {
      setLoading(false);
    }
  };

  if (permissionLoading) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (!canRead) {
    return (
      <div className="page-container">
        <div className="error-message">{t('common.noPermission')}</div>
      </div>
    );
  }

  // Calculate pagination
  const totalPages = Math.ceil(users.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentUsers = users.slice(startIndex, endIndex);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{pageTitle}</h1>
        {canCreate && (
          <button className="btn-primary" onClick={handleOpenCreate}>
            {t('common.create')}
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && users.length === 0 ? (
        <p>{t('common.loading')}</p>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead className="table-header-dark-green">
              <tr>
                <th>{t('tenantUsers.jobTitle')}</th>
                <th>{t('tenantUsers.account')}</th>
                <th>{t('tenantUsers.username')}</th>
                <th>{t('tenantUsers.phone')}</th>
                <th>{t('tenantUsers.lastLoginAt')}</th>
                <th>{t('tenantUsers.isActive')}</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {currentUsers.map((user) => (
                <tr key={user.id}>
                  <td>{user.job_title || '-'}</td>
                  <td>{user.account}</td>
                  <td>{user.username}</td>
                  <td>{user.phone || '-'}</td>
                  <td>{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : '-'}</td>
                  <td>
                    <button
                      className={user.is_active ? 'status-active' : 'status-inactive'}
                      onClick={() => handleToggleStatus(user)}
                      disabled={!canUpdate || loading}
                    >
                      {user.is_active ? t('common.active') : t('common.inactive')}
                    </button>
                  </td>
                  <td className="actions">
                    {canUpdate && (
                      <>
                        <button
                          className="btn-edit"
                          onClick={() => handleOpenEdit(user)}
                          disabled={loading}
                          style={{ marginRight: '12px' }}
                        >
                          {t('common.edit')}
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={() => handleResetPassword(user)}
                          disabled={loading}
                          style={{ marginRight: '12px' }}
                        >
                          {t('tenantUsers.resetPassword')}
                        </button>
                      </>
                    )}
                    {canDelete && (
                      <button
                        className="btn-delete"
                        onClick={() => handleDelete(user)}
                        disabled={loading}
                      >
                        {t('common.delete')}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {users.length === 0 && (
            <div className="no-data">{t('message.noData')}</div>
          )}

          {users.length > 0 && (
            <div className="pagination-container">
              <div className="pagination-info">
                <label>
                  {t('systemCodes.itemsPerPage')}：
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
                    total: users.length,
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
                <button className={`btn-pagination active`}>
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

      {/* 新增成員 Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{t('tenantUsers.createUser')}</h2>
            <div className="form-grid">
              <div className="form-group">
                <label>{t('tenantUsers.account')} *</label>
                <input
                  type="email"
                  value={createForm.account}
                  onChange={(e) => setCreateForm({ ...createForm, account: e.target.value })}
                  placeholder="user@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.username')} *</label>
                <input
                  type="text"
                  value={createForm.username}
                  onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.password')} *</label>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.confirmPassword')} *</label>
                <input
                  type="password"
                  value={createForm.confirmPassword}
                  onChange={(e) => setCreateForm({ ...createForm, confirmPassword: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.department')}</label>
                <input
                  type="text"
                  value={createForm.department}
                  onChange={(e) => setCreateForm({ ...createForm, department: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.jobTitle')}</label>
                <input
                  type="text"
                  value={createForm.job_title}
                  onChange={(e) => setCreateForm({ ...createForm, job_title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.phone')}</label>
                <input
                  type="tel"
                  value={createForm.phone}
                  onChange={(e) => setCreateForm({ ...createForm, phone: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={createForm.is_active}
                    onChange={(e) => setCreateForm({ ...createForm, is_active: e.target.checked })}
                  />
                  {t('tenantUsers.isActive')}
                </label>
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn-primary" onClick={handleCreate} disabled={loading}>
                {t('common.confirm')}
              </button>
              <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 編輯成員 Modal */}
      {showEditModal && currentUser && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{t('tenantUsers.editUser')}</h2>
            <div className="form-grid">
              <div className="form-group">
                <label>{t('tenantUsers.account')} *</label>
                <input
                  type="email"
                  value={editForm.account}
                  onChange={(e) => setEditForm({ ...editForm, account: e.target.value })}
                  placeholder="user@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.username')} *</label>
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.department')}</label>
                <input
                  type="text"
                  value={editForm.department}
                  onChange={(e) => setEditForm({ ...editForm, department: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.jobTitle')}</label>
                <input
                  type="text"
                  value={editForm.job_title}
                  onChange={(e) => setEditForm({ ...editForm, job_title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.phone')}</label>
                <input
                  type="tel"
                  value={editForm.phone}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.lastLoginAt')}</label>
                <input
                  type="text"
                  value={currentUser.last_login_at ? new Date(currentUser.last_login_at).toLocaleString() : '-'}
                  disabled
                />
              </div>
              <div className="form-group">
                <label>{t('tenantUsers.lastLoginIp')}</label>
                <input
                  type="text"
                  value={currentUser.last_login_ip || '-'}
                  disabled
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={editForm.is_active}
                    onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                  />
                  {t('tenantUsers.isActive')}
                </label>
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn-primary" onClick={handleUpdate} disabled={loading}>
                {t('common.confirm')}
              </button>
              <button className="btn-secondary" onClick={() => setShowEditModal(false)}>
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TenantUsersPage;
