/**
 * 應用程式主元件
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SystemProvider } from './contexts/SystemContext';
import { AuthProvider } from './contexts/AuthContext';
import { useSystem } from './contexts/SystemContext';
import { useDocumentTitle } from './hooks/useDocumentTitle';
import MaintenancePage from './pages/MaintenancePage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import OrganizationsPage from './pages/OrganizationsPage';
import SysProfilePage from './pages/SysProfilePage';
import UserRolesPage from './pages/UserRolesPage';
import UsersPage from './pages/UsersPage';
import SysFunctionsPage from './pages/SysFunctionsPage';
import RoleRightPage from './pages/RoleRightPage';
import UserLogsPage from './pages/UserLogsPage';
import MainLayout from './components/MainLayout';
import PrivateRoute from './components/PrivateRoute';

/**
 * 應用程式路由
 * 根據系統維護狀態決定顯示內容
 */
const AppRoutes: React.FC = () => {
  const { isService, isLoading } = useSystem();

  // 更新網頁 title
  useDocumentTitle();

  // 載入中
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        系統載入中...
      </div>
    );
  }

  // 系統維護中
  if (!isService) {
    return <MaintenancePage />;
  }

  // 正常服務
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="organizations" element={<OrganizationsPage />} />
        <Route path="sys_profile" element={<SysProfilePage />} />
        <Route path="roles" element={<UserRolesPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="sysfunction" element={<SysFunctionsPage />} />
        <Route path="org_profile" element={<div>組織資料檔案</div>} />
        <Route path="role_right" element={<RoleRightPage />} />
        <Route path="user_logs" element={<UserLogsPage />} />
        {/* 保留舊路由以便向後兼容 */}
        <Route path="user_role" element={<Navigate to="/roles" replace />} />
        <Route path="user_detail" element={<Navigate to="/users" replace />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

/**
 * 應用程式主元件
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <SystemProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </SystemProvider>
    </BrowserRouter>
  );
};

export default App;
