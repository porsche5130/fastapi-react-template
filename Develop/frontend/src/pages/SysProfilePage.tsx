/**
 * 系統設定資料頁面
 * 顯示和修改系統設定（id=1）
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  SysProfile,
  SysProfileUpdate,
  getSysProfile,
  updateSysProfile
} from '../services/sysProfileService';
import { getOrganizations, Organization } from '../services/organizationService';
import { usePermission } from '../hooks/usePermission';
import '../styles/DataTable.css';

const SysProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const { hasPermission, loading: permissionLoading } = usePermission();
  const [profile, setProfile] = useState<SysProfile | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<SysProfileUpdate>({});

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSysProfile();
      setProfile(data);
      setFormData({
        is_service: data.is_service,
        sys_url: data.sys_url,
        sys_ctitle: data.sys_ctitle,
        sys_etitle: data.sys_etitle,
        sys_ccopyright: data.sys_ccopyright,
        sys_ecopyright: data.sys_ecopyright,
        sys_organization: data.sys_organization,
        sys_mana_email: data.sys_mana_email
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const loadOrganizations = async () => {
    try {
      const data = await getOrganizations();
      setOrganizations(data);
    } catch (err) {
      console.error('Failed to load organizations:', err);
    }
  };

  useEffect(() => {
    loadProfile();
    loadOrganizations();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateSysProfile(formData);
      alert(t('message.saveSuccess'));
      loadProfile();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('message.saveFailed'));
    } finally {
      setSaving(false);
    }
  };

  // 檢查讀取權限
  if (permissionLoading) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (!hasPermission('sys_profile', 'read')) {
    return (
      <div className="page-container">
        <div className="error-message">{t('common.noPermission')}</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  // 檢查修改權限
  const canUpdate = hasPermission('sys_profile', 'update');

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{t('sysProfile.title')}</h1>
      </div>

      <div className="data-table-container">
        <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
          <div className="form-grid">
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.is_service || false}
                  onChange={(e) => setFormData({ ...formData, is_service: e.target.checked })}
                  disabled={!canUpdate}
                />
                {t('sysProfile.isService')} 
                <span style={{ marginLeft: '8px', color: formData.is_service ? '#28a745' : '#dc3545' }}>
                  ({formData.is_service ? t('sysProfile.serviceEnabled') : t('sysProfile.serviceDisabled')})
                </span>
              </label>
            </div>

            <div className="form-group full-width">
              <label>{t('sysProfile.sysUrl')} *</label>
              <input
                type="url"
                value={formData.sys_url || ''}
                onChange={(e) => setFormData({ ...formData, sys_url: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysCTitle')} *</label>
              <input
                type="text"
                value={formData.sys_ctitle || ''}
                onChange={(e) => setFormData({ ...formData, sys_ctitle: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysETitle')} *</label>
              <input
                type="text"
                value={formData.sys_etitle || ''}
                onChange={(e) => setFormData({ ...formData, sys_etitle: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysCCopyright')} *</label>
              <input
                type="text"
                value={formData.sys_ccopyright || ''}
                onChange={(e) => setFormData({ ...formData, sys_ccopyright: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysECopyright')} *</label>
              <input
                type="text"
                value={formData.sys_ecopyright || ''}
                onChange={(e) => setFormData({ ...formData, sys_ecopyright: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysOrganization')} *</label>
              <select
                value={formData.sys_organization || 1}
                onChange={(e) => setFormData({ ...formData, sys_organization: parseInt(e.target.value) })}
                required
                disabled={!canUpdate}
              >
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.org_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>{t('sysProfile.sysManaEmail')} *</label>
              <input
                type="email"
                value={formData.sys_mana_email || ''}
                onChange={(e) => setFormData({ ...formData, sys_mana_email: e.target.value })}
                required
                disabled={!canUpdate}
              />
            </div>
          </div>

          <div className="modal-actions" style={{ marginTop: '24px' }}>
            {canUpdate && (
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? t('common.loading') : t('common.save')}
              </button>
            )}
            {!canUpdate && (
              <div style={{ color: '#dc3545', fontSize: '14px' }}>
                {t('common.noUpdatePermission')}
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default SysProfilePage;
