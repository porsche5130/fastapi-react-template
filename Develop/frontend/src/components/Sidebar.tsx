/**
 * 側邊欄選單元件
 * 顯示系統功能選單（從 sysfunction 資料表）
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SystemFunction } from '../types';
import { systemService } from '../api/systemService';
import '../styles/Sidebar.css';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const [menuItems, setMenuItems] = useState<SystemFunction[]>([]);
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  const [hoveredItem, setHoveredItem] = useState<number | null>(null);
  const [popupPosition, setPopupPosition] = useState<{ top: number } | null>(null);

  // 從 API 載入選單項目
  useEffect(() => {
    const loadMenuItems = async () => {
      try {
        const functions = await systemService.getFunctions();
        console.log('Loaded menu functions:', functions);
        setMenuItems(functions);
      } catch (error) {
        console.error('Failed to load menu items:', error);
      }
    };

    loadMenuItems();
  }, []);

  const toggleExpand = (itemId: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const handleMouseEnter = (e: React.MouseEvent, itemId: number) => {
    if (isCollapsed) {
      const rect = e.currentTarget.getBoundingClientRect();
      setPopupPosition({ top: rect.top });
      setHoveredItem(itemId);
    }
  };

  const handleMouseLeave = () => {
    if (isCollapsed) {
      setHoveredItem(null);
      setPopupPosition(null);
    }
  };

  const renderMenuItem = (item: SystemFunction, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);
    const isHovered = hoveredItem === item.id;
    const mainPath = item.func_module_name ? `/${item.func_module_name}` : '#';

    // 根據當前語言選擇顯示文字
    const displayName = i18n.language === 'en' ? item.func_ename : item.func_cname;

    return (
      <div
        key={item.id}
        className={`menu-item level-${level}`}
      >
        {hasChildren ? (
          <div className="menu-item-wrapper">
            <div
              className={`menu-link ${isExpanded ? 'expanded' : ''}`}
              onClick={() => !isCollapsed && toggleExpand(item.id)}
              onMouseEnter={(e) => handleMouseEnter(e, item.id)}
              onMouseLeave={handleMouseLeave}
              title={isCollapsed ? displayName : ''}
            >
              <span className="menu-icon">{item.func_icon || '📁'}</span>
              {!isCollapsed && (
                <>
                  <span className="menu-text">{displayName}</span>
                  <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                </>
              )}
            </div>
            {/* 展開狀態的子選單 */}
            {isExpanded && !isCollapsed && item.children && (
              <div className="submenu">
                {item.children.map((child) => renderMenuItem(child, level + 1))}
              </div>
            )}
            {/* 收合狀態的懸浮子選單 */}
            {isCollapsed && isHovered && item.children && item.children.length > 0 && popupPosition && (
              <div
                className="popup-submenu"
                style={{ top: `${popupPosition.top}px` }}
                onMouseEnter={(e) => handleMouseEnter(e, item.id)}
                onMouseLeave={handleMouseLeave}
              >
                <div className="popup-submenu-header">{displayName}</div>
                {item.children.map((child) => {
                  const childPath = child.func_module_name ? `/${child.func_module_name}` : '#';
                  const childName = i18n.language === 'en' ? child.func_ename : child.func_cname;
                  return (
                    <Link
                      key={child.id}
                      to={childPath}
                      className={`popup-menu-link ${isActive(childPath) ? 'active' : ''}`}
                    >
                      <span className="menu-icon">{child.func_icon || '📄'}</span>
                      <span className="menu-text">{childName}</span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <Link
            to={mainPath}
            className={`menu-link ${isActive(mainPath) ? 'active' : ''}`}
            title={isCollapsed ? displayName : ''}
          >
            <span className="menu-icon">{item.func_icon || '📄'}</span>
            {!isCollapsed && <span className="menu-text">{displayName}</span>}
          </Link>
        )}
      </div>
    );
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!isCollapsed && <h2 className="sidebar-title">{t('sidebar.menu')}</h2>}
        <button className="toggle-button" onClick={onToggle}>
          {isCollapsed ? '☰' : '«'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => renderMenuItem(item))}
      </nav>
    </aside>
  );
};

export default Sidebar;
