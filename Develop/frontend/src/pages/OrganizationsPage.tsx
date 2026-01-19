/**
 * 組織設定頁面
 * 組織單位的 CRUD 管理
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Organization,
  OrganizationCreate,
  getOrganizations,
  createOrganization,
  updateOrganization,
  deleteOrganization
} from '../services/organizationService';
import '../styles/DataTable.css';

const OrganizationsPage: React.FC = () => {
  const { t } = useTranslation();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [formData, setFormData] = useState<OrganizationCreate>({
    org_code: '',
    org_name: '',
    org_type: 2,
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    phone: '',
    is_mana: false,
    is_active: true,
    memo: ''
  });

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getOrganizations({ search: search || undefined });
      setOrganizations(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrganizations();
  }, []);

  const handleSearch = () => {
    setCurrentPage(1);
    loadOrganizations();
  };

  // 分頁計算
  const filteredOrganizations = organizations;
  const totalPages = Math.ceil(filteredOrganizations.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentOrganizations = filteredOrganizations.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setItemsPerPage(parseInt(e.target.value));
    setCurrentPage(1);
  };

  const openModal = (org?: Organization) => {
    if (org) {
      setEditingOrg(org);
      setFormData({
        org_code: org.org_code,
        org_name: org.org_name,
        org_type: org.org_type,
        contact_person: org.contact_person,
        contact_email: org.contact_email,
        contact_phone: org.contact_phone,
        address: org.address || '',
        phone: org.phone || '',
        is_mana: org.is_mana,
        is_active: org.is_active,
        memo: org.memo || ''
      });
    } else {
      setEditingOrg(null);
      setFormData({
        org_code: '',
        org_name: '',
        org_type: 2,
        contact_person: '',
        contact_email: '',
        contact_phone: '',
        address: '',
        phone: '',
        is_mana: false,
        is_active: true,
        memo: ''
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingOrg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingOrg) {
        await updateOrganization(editingOrg.id, formData);
      } else {
        await createOrganization(formData);
      }
      closeModal();
      loadOrganizations();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('common.error'));
    }
  };

  const handleDelete = async (org: Organization) => {
    if (!window.confirm(t('common.confirmDelete'))) return;

    try {
      await deleteOrganization(org.id);
      loadOrganizations();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('common.error'));
    }
  };

  const getOrgTypeText = (type: number) => {
    const types: { [key: number]: string } = {
      1: t('organizations.types.government'),
      2: t('organizations.types.company'),
      3: t('organizations.types.individual')
    };
    return types[type] || type.toString();
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{t('organizations.title')}</h1>
        <button className="btn-primary" onClick={() => openModal()}>
          {t('common.create')}
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder={t('organizations.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn-secondary" onClick={handleSearch}>
          {t('common.search')}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : (
        <>
          <div className="data-table-container">
            <table className="data-table">
              <thead className="table-header-dark-green">
                <tr>
                  <th>{t('organizations.orgCode')}</th>
                  <th>{t('organizations.orgName')}</th>
                  <th>{t('organizations.orgType')}</th>
                  <th>{t('organizations.contactPerson')}</th>
                  <th>{t('organizations.contactEmail')}</th>
                  <th>{t('organizations.contactPhone')}</th>
                  <th>{t('common.status')}</th>
                  <th>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {currentOrganizations.map((org) => (
                  <tr key={org.id}>
                    <td>{org.org_code}</td>
                    <td>{org.org_name}</td>
                    <td>{getOrgTypeText(org.org_type)}</td>
                    <td>{org.contact_person}</td>
                    <td>{org.contact_email}</td>
                    <td>{org.contact_phone}</td>
                    <td>
                      <span className={`status-badge ${org.is_active ? 'active' : 'inactive'}`}>
                        {org.is_active ? t('common.active') : t('common.inactive')}
                      </span>
                    </td>
                    <td className="actions">
                      <button className="btn-edit" onClick={() => openModal(org)}>
                        {t('common.edit')}
                      </button>
                      <button className="btn-delete" onClick={() => handleDelete(org)}>
                        {t('common.delete')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 分頁控制 */}
          <div className="pagination-container">
            <div className="pagination-info">
              <label>
                每頁顯示：
                <select value={itemsPerPage} onChange={handleItemsPerPageChange}>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
                筆
              </label>
              <span className="pagination-text">
                共 {filteredOrganizations.length} 筆資料，第 {currentPage} / {totalPages} 頁
              </span>
            </div>

            <div className="pagination-buttons">
              <button
                className="btn-pagination"
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
              >
                ⟪
              </button>
              <button
                className="btn-pagination"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                ‹
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(page => {
                  if (totalPages <= 7) return true;
                  if (page === 1 || page === totalPages) return true;
                  if (page >= currentPage - 1 && page <= currentPage + 1) return true;
                  return false;
                })
                .map((page, index, array) => {
                  if (index > 0 && array[index - 1] !== page - 1) {
                    return (
                      <React.Fragment key={`ellipsis-${page}`}>
                        <span className="pagination-ellipsis">...</span>
                        <button
                          className={`btn-pagination ${currentPage === page ? 'active' : ''}`}
                          onClick={() => handlePageChange(page)}
                        >
                          {page}
                        </button>
                      </React.Fragment>
                    );
                  }
                  return (
                    <button
                      key={page}
                      className={`btn-pagination ${currentPage === page ? 'active' : ''}`}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </button>
                  );
                })}

              <button
                className="btn-pagination"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                ›
              </button>
              <button
                className="btn-pagination"
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages}
              >
                ⟫
              </button>
            </div>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingOrg ? t('common.edit') : t('common.create')}</h2>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>{t('organizations.orgCode')} *</label>
                  <input
                    type="text"
                    value={formData.org_code}
                    onChange={(e) => setFormData({ ...formData, org_code: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.orgName')} *</label>
                  <input
                    type="text"
                    value={formData.org_name}
                    onChange={(e) => setFormData({ ...formData, org_name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.orgType')} *</label>
                  <select
                    value={formData.org_type}
                    onChange={(e) => setFormData({ ...formData, org_type: parseInt(e.target.value) })}
                    required
                  >
                    <option value={1}>{t('organizations.types.government')}</option>
                    <option value={2}>{t('organizations.types.company')}</option>
                    <option value={3}>{t('organizations.types.individual')}</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>{t('organizations.contactPerson')} *</label>
                  <input
                    type="text"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.contactEmail')} *</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.contactPhone')} *</label>
                  <input
                    type="text"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.address')}</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>{t('organizations.phone')}</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div className="form-group full-width">
                  <label>{t('common.memo')}</label>
                  <textarea
                    value={formData.memo}
                    onChange={(e) => setFormData({ ...formData, memo: e.target.value })}
                    rows={3}
                  />
                </div>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                    {t('common.active')}
                  </label>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  {t('common.cancel')}
                </button>
                <button type="submit" className="btn-primary">
                  {t('common.save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizationsPage;
