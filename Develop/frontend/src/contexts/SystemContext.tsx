/**
 * 系統狀態管理 Context
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SystemProfile } from '../types';
import { systemService } from '../api/systemService';

interface SystemContextType {
  systemProfile: SystemProfile | null;
  isService: boolean;
  isLoading: boolean;
  refreshSystemProfile: () => Promise<void>;
}

const SystemContext = createContext<SystemContextType | undefined>(undefined);

interface SystemProviderProps {
  children: ReactNode;
}

export const SystemProvider: React.FC<SystemProviderProps> = ({ children }) => {
  const [systemProfile, setSystemProfile] = useState<SystemProfile | null>(null);
  const [isService, setIsService] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  // 載入系統設定
  const loadSystemProfile = async () => {
    setIsLoading(true);
    try {
      const profile = await systemService.getProfile();
      setSystemProfile(profile);
      setIsService(profile.is_service);
    } catch (error) {
      console.error('載入系統設定失敗:', error);
      setIsService(false);
    } finally {
      setIsLoading(false);
    }
  };

  // 重新載入系統設定
  const refreshSystemProfile = async () => {
    await loadSystemProfile();
  };

  // 初始化載入系統設定
  useEffect(() => {
    loadSystemProfile();
  }, []);

  return (
    <SystemContext.Provider
      value={{
        systemProfile,
        isService,
        isLoading,
        refreshSystemProfile,
      }}
    >
      {children}
    </SystemContext.Provider>
  );
};

// 自訂 Hook
export const useSystem = () => {
  const context = useContext(SystemContext);
  if (context === undefined) {
    throw new Error('useSystem must be used within a SystemProvider');
  }
  return context;
};
