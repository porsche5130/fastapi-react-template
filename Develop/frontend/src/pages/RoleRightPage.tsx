/**
 * Role Right Page
 * 角色權限設定作業頁面
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  getFunctionsWithPermissions,
  getRoleRights,
  saveRoleRights,
  FunctionWithPermissions,
  RoleRight
} from '../services/roleRightService';
import { getUserRoles, UserRole } from '../services/userRoleService';
import '../styles/RoleRightPage.css';

const RoleRightPage: React.FC = () => {
  const { t } = useTranslation();

  // 狀態管理
  const [roles, setRoles] = useState<UserRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [functions, setFunctions] = useState<FunctionWithPermissions[]>([]);
  const [rights, setRights] = useState<Map<number, RoleRight>>(new Map());
  const [loading, setLoading] = useState(false);

  // 載入角色清單
  useEffect(() => {
    loadRoles();
    loadFunctions();
  }, []);

  // 載入角色清單
  const loadRoles = async () => {
    try {
      const data = await getUserRoles({ is_active: true });
      setRoles(data);
    } catch (error) {
      console.error('載入角色失敗', error);
    }
  };

  // 載入功能清單
  const loadFunctions = async () => {
    try {
      const data = await getFunctionsWithPermissions();
      setFunctions(data);
    } catch (error) {
      console.error('載入功能清單失敗', error);
    }
  };

  // 角色選擇變更
  const handleRoleChange = async (roleId: number) => {
    setSelectedRoleId(roleId);
    setLoading(true);

    try {
      const data = await getRoleRights(roleId);

      // 將權限資料轉為 Map
      const rightsMap = new Map<number, RoleRight>();
      data.rights.forEach(right => {
        rightsMap.set(right.sysfuction_id, right);
      });

      // 初始化所有功能的權限 (未設定的功能預設全為 false)
      functions.forEach(func => {
        if (!rightsMap.has(func.id)) {
          rightsMap.set(func.id, {
            sysfuction_id: func.id,
            func_code: func.func_code,
            is_create: false,
            is_read: false,
            is_update: false,
            is_delete: false,
            is_print: false,
            is_file: false
          });
        }
      });

      setRights(rightsMap);
    } catch (error) {
      console.error('載入角色權限失敗', error);
    } finally {
      setLoading(false);
    }
  };

  // 權限勾選變更
  const handlePermissionChange = (
    funcId: number,
    funcCode: string,
    permission: keyof Omit<RoleRight, 'sysfuction_id' | 'func_code' | 'id'>,
    value: boolean
  ) => {
    const newRights = new Map(rights);
    const right = newRights.get(funcId) || {
      sysfuction_id: funcId,
      func_code: funcCode,
      is_create: false,
      is_read: false,
      is_update: false,
      is_delete: false,
      is_print: false,
      is_file: false
    };

    right[permission] = value;
    newRights.set(funcId, right);
    setRights(newRights);
  };

  // 儲存權限設定
  const handleSave = async () => {
    if (!selectedRoleId) {
      alert(t('roleRight.pleaseSelectRole'));
      return;
    }

    try {
      setLoading(true);

      // 將 Map 轉為陣列
      const rightsArray = Array.from(rights.values());

      await saveRoleRights(selectedRoleId, rightsArray);
      alert(t('roleRight.saveSuccess'));
    } catch (error: any) {
      alert(error.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  // 渲染功能樹狀結構
  const renderFunctionTree = () => {
    // 建立樹狀結構
    const tree: { [key: number]: FunctionWithPermissions[] } = {};
    functions.forEach(func => {
      if (!tree[func.upper_func_id]) {
        tree[func.upper_func_id] = [];
      }
      tree[func.upper_func_id].push(func);
    });

    // 遞迴渲染
    const renderNode = (parentId: number, level: number = 0): React.ReactElement[] => {
      const children = tree[parentId] || [];
      return children.map(func => {
        const right = rights.get(func.id);
        const indent = '　'.repeat(level);

        return (
          <React.Fragment key={func.id}>
            <tr className={func.func_type === 1 ? 'node-row' : ''}>
              <td className="func-name">
                {indent}
                {func.func_type === 1 ? '└ ' : '├ '}
                {func.func_cname}
                {func.func_type === 1 && ' (節點)'}
              </td>

              {/* 新增權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_create || false}
                  disabled={!func.available_permissions.create || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_create',
                    e.target.checked
                  )}
                />
              </td>

              {/* 讀取權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_read || false}
                  disabled={!func.available_permissions.read || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_read',
                    e.target.checked
                  )}
                />
              </td>

              {/* 修改權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_update || false}
                  disabled={!func.available_permissions.update || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_update',
                    e.target.checked
                  )}
                />
              </td>

              {/* 刪除權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_delete || false}
                  disabled={!func.available_permissions.delete || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_delete',
                    e.target.checked
                  )}
                />
              </td>

              {/* 列印權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_print || false}
                  disabled={!func.available_permissions.print || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_print',
                    e.target.checked
                  )}
                />
              </td>

              {/* 產檔權限 */}
              <td className="permission-cell">
                <input
                  type="checkbox"
                  checked={right?.is_file || false}
                  disabled={!func.available_permissions.file || !selectedRoleId}
                  onChange={(e) => handlePermissionChange(
                    func.id,
                    func.func_code,
                    'is_file',
                    e.target.checked
                  )}
                />
              </td>
            </tr>

            {/* 遞迴渲染子功能 */}
            {renderNode(func.id, level + 1)}
          </React.Fragment>
        );
      });
    };

    return renderNode(0);
  };

  return (
    <div className="role-right-page">
      <h2>{t('roleRight.title')}</h2>

      {/* 角色選擇 */}
      <div className="role-selector">
        <label>{t('roleRight.selectRole')}: </label>
        <select
          value={selectedRoleId || ''}
          onChange={(e) => handleRoleChange(Number(e.target.value))}
          disabled={loading}
        >
          <option value="">{t('roleRight.pleaseSelectRole')}</option>
          {roles.map(role => (
            <option key={role.id} value={role.id}>
              {role.role_cname} ({role.role_ename})
            </option>
          ))}
        </select>
      </div>

      {/* 權限設定表格 */}
      {selectedRoleId && (
        <div className="permissions-table-container">
          <table className="permissions-table">
            <thead>
              <tr>
                <th>{t('roleRight.functionName')}</th>
                <th>{t('roleRight.create')}</th>
                <th>{t('roleRight.read')}</th>
                <th>{t('roleRight.update')}</th>
                <th>{t('roleRight.delete')}</th>
                <th>{t('roleRight.print')}</th>
                <th>{t('roleRight.file')}</th>
              </tr>
            </thead>
            <tbody>
              {renderFunctionTree()}
            </tbody>
          </table>
        </div>
      )}

      {/* 操作按鈕 */}
      {selectedRoleId && (
        <div className="action-buttons">
          <button onClick={handleSave} disabled={loading}>
            {loading ? t('common.saving') : t('common.save')}
          </button>
        </div>
      )}
    </div>
  );
};

export default RoleRightPage;
