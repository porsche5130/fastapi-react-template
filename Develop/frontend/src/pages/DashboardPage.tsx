/**
 * 儀表板頁面
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { getOrganization, Organization } from '../services/organizationService';
import '../styles/DashboardPage.css';

const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [orgLoading, setOrgLoading] = useState(false);

  // 取得組織資料
  useEffect(() => {
    const fetchOrganization = async () => {
      console.log('DashboardPage - user:', user);
      console.log('DashboardPage - organization_id:', user?.organization_id);

      if (user?.organization_id) {
        try {
          console.log('Fetching organization data for ID:', user.organization_id);
          setOrgLoading(true);
          const orgData = await getOrganization(user.organization_id);
          console.log('Organization data received:', orgData);
          setOrganization(orgData);
        } catch (error) {
          console.error('Failed to fetch organization:', error);
        } finally {
          setOrgLoading(false);
        }
      } else {
        console.log('No organization_id found in user data');
      }
    };

    fetchOrganization();
  }, [user?.organization_id]);

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-title">{t('dashboard.title')}</h2>
      <p className="dashboard-subtitle">{t('dashboard.titleEn')}</p>

      <div className="dashboard-cards">
        <div className="dashboard-card">
          <div className="card-icon">👤</div>
          <div className="card-content">
            <h3>{t('dashboard.userInfo')}</h3>
            <p className="card-value">{user?.username || '-'}</p>
            <p className="card-label">{user?.job_title || user?.department || '-'}</p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">📧</div>
          <div className="card-content">
            <h3>{t('dashboard.email')}</h3>
            <p className="card-value">{user?.account || '-'}</p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">🏢</div>
          <div className="card-content">
            <h3>{t('dashboard.organization')}</h3>
            <p className="card-value">
              {orgLoading ? t('common.loading') : (organization?.org_name || '-')}
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">🔑</div>
          <div className="card-content">
            <h3>{t('dashboard.roles')}</h3>
            <p className="card-value">
              {t('dashboard.rolesCount', { count: user?.user_role?.length || 0 })}
            </p>
          </div>
        </div>
      </div>

      <div className="dashboard-info">
        <h3>{t('sidebar.dashboard')}</h3>
        <p>
          {t('dashboard.systemDescription')}
        </p>
      </div>
    </div>
  );
};

export default DashboardPage;
