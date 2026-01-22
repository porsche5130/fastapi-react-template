/**
 * 主要佈局元件
 * 包含：左側選單、上方使用者資訊、中間內容區、下方版權
 */

import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useSystem } from '../contexts/SystemContext';
import Sidebar from './Sidebar';
import LanguageSwitcher from './LanguageSwitcher';
import Breadcrumb from './Breadcrumb';
import '../styles/MainLayout.css';

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const { systemProfile, getCopyright } = useSystem();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('登出失敗:', error);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="main-layout">
      {/* 左側選單 */}
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />

      {/* 右側內容區 */}
      <div className={`main-content ${isSidebarCollapsed ? 'expanded' : ''}`}>
        {/* 上方使用者資訊列 */}
        <header className="top-header">
          <div className="header-left">
            <h1 className="page-title">
              {i18n.language === 'en'
                ? (systemProfile?.sys_etitle || 'Paris Agreement Article 6.4 Management System')
                : (systemProfile?.sys_ctitle || '巴黎協定 減碳活動申請系統(Article 6.4)')}
            </h1>
          </div>
          <div className="header-right">
            <LanguageSwitcher />
            <div className="user-info">
              <div className="user-avatar">
                {user?.username?.charAt(0) || 'U'}
              </div>
              <div className="user-details">
                <div className="user-name">{user?.username || t('common.loading')}</div>
                <div className="user-role">
                  {user?.job_title || user?.department || t('header.userInfo')}
                </div>
              </div>
              <button className="logout-button" onClick={handleLogout}>
                {t('auth.logout')}
              </button>
            </div>
          </div>
        </header>

        {/* 中間內容區域 */}
        <main className="content-area">
          <div className="content-wrapper">
            <Breadcrumb />
            <Outlet />
          </div>
        </main>

        {/* 下方版權宣告 */}
        <footer className="bottom-footer">
          <div className="footer-content">
            <p className="copyright-text">
              {getCopyright() || (i18n.language === 'en'
                ? 'Copyright © 2026 JiangYun Co., Ltd.'
                : 'Copyright © 2026 匠耘有限公司')}
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default MainLayout;
