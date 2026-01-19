/**
 * 登入頁面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useSystem } from '../contexts/SystemContext';
import { authService } from '../api/authService';
import LanguageSwitcher from '../components/LanguageSwitcher';
import '../styles/LoginPage.css';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const { systemProfile } = useSystem();

  const [formData, setFormData] = useState({
    account: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // 呼叫登入 API
      const response = await authService.login(formData);

      // 儲存 Token 並載入使用者資料
      await login(response.access_token);

      // 導向主頁面
      navigate('/dashboard');
    } catch (err: any) {
      console.error('登入失敗:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(t('auth.loginFailed'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="header-lang-switcher">
          <LanguageSwitcher />
        </div>

        <div className="login-header">
          <h1 className="system-title">
            {i18n.language === 'en'
              ? (systemProfile?.sys_etitle || 'Paris Agreement Article 6.4 Management System')
              : (systemProfile?.sys_ctitle || '巴黎協定 減碳活動申請系統')}
          </h1>
        </div>

        <div className="login-form-container">
          <h3 className="login-form-title">{t('auth.login')}</h3>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="account">{t('auth.email')}</label>
              <input
                type="email"
                id="account"
                name="account"
                value={formData.account}
                onChange={handleChange}
                placeholder={t('auth.emailPlaceholder')}
                required
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">{t('auth.password')}</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder={t('auth.passwordPlaceholder')}
                required
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="error-message">
                <span>⚠️</span> {error}
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? t('auth.loggingIn') : t('auth.loginButton')}
            </button>
          </form>
        </div>

        <div className="login-footer">
          <p>
            {i18n.language === 'en'
              ? (systemProfile?.sys_ecopyright || 'Copyright © 2026 JiangYun Co., Ltd.')
              : (systemProfile?.sys_ccopyright || t('common.copyright'))}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
