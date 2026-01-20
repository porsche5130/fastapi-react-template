/**
 * 系統功能設定頁面
 * 系統功能的 CRUD 管理
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  SysFunction,
  SysFunctionCreate,
  getSysFunctions,
  createSysFunction,
  updateSysFunction,
  deleteSysFunction
} from '../services/sysFunctionService';
import { usePermission } from '../hooks/usePermission';
import { useFunctionName } from '../hooks/useFunctionName';
import { logView, logCreate, logRead, logUpdate, logDelete } from '../utils/userLogHelper';
import '../styles/DataTable.css';

const SysFunctionsPage: React.FC = () => {
  const { t } = useTranslation();
  const { hasPermission, loading: permissionLoading } = usePermission();
  const pageTitle = useFunctionName('sysfunction');
  const hasInitialized = useRef(false);
  const [functions, setFunctions] = useState<SysFunction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filterUpperFunc, setFilterUpperFunc] = useState<number | ''>('');
  const [filterFuncType, setFilterFuncType] = useState<number | ''>('');
  const [showOnlyMana, setShowOnlyMana] = useState(false);
  const [sortBy, setSortBy] = useState<'id' | 'func_order'>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showModal, setShowModal] = useState(false);
  const [editingFunction, setEditingFunction] = useState<SysFunction | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [isViewMode, setIsViewMode] = useState(false);
  const [moduleItemActions, setModuleItemActions] = useState<string[]>([]);
  const [formData, setFormData] = useState<SysFunctionCreate>({
    func_code: '',
    upper_func_id: 0,
    func_cname: '',
    func_ename: '',
    func_type: 2,
    func_order: 0,
    func_icon: '',
    func_module_name: '',
    module_item: [],
    description: '',
    is_mana: false,
    is_active: true
  });

  const loadFunctions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSysFunctions({ search: search || undefined });
      setFunctions(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 等待權限載入完成後再檢查權限並載入資料
    if (!permissionLoading && hasPermission('sysfunction', 'read') && !hasInitialized.current) {
      hasInitialized.current = true;
      const initPage = async () => {
        try {
          await loadFunctions();
          await logView('sysfunction', { search: search || undefined }, null);
        } catch (err: any) {
          const errorMsg = err.response?.data?.detail || err.message || t('message.loadFailed');
          await logView('sysfunction', { search: search || undefined }, errorMsg);
        }
      };
      initPage();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [permissionLoading]);

  const handleSearch = () => {
    setCurrentPage(1);
    loadFunctions();
  };

  const handleSort = (field: 'id' | 'func_order') => {
    if (sortBy === field) {
      // 如果點選同一欄位，切換排序順序
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // 如果點選不同欄位，設定新欄位並預設升序
      setSortBy(field);
      setSortOrder('asc');
    }
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    setFilterUpperFunc('');
    setFilterFuncType('');
    setShowOnlyMana(false);
    setSortBy('id');
    setSortOrder('asc');
    setCurrentPage(1);
  };

  // 取得所有唯一的上層功能選項
  const getUpperFuncOptions = () => {
    const uniqueUpperFuncs = Array.from(new Set(functions.map(f => f.upper_func_id)));
    return uniqueUpperFuncs.sort((a, b) => a - b);
  };

  // 篩選和排序
  const filteredFunctions = functions
    .filter(func => {
      // 上層功能篩選
      if (filterUpperFunc !== '' && func.upper_func_id !== filterUpperFunc) {
        return false;
      }
      // 功能類型篩選
      if (filterFuncType !== '' && func.func_type !== filterFuncType) {
        return false;
      }
      // 只顯示管理功能
      if (showOnlyMana && !func.is_mana) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      // 排序
      let comparison = 0;
      if (sortBy === 'id') {
        comparison = a.id - b.id;
      } else if (sortBy === 'func_order') {
        comparison = a.func_order - b.func_order;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const totalPages = Math.ceil(filteredFunctions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentFunctions = filteredFunctions.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setItemsPerPage(parseInt(e.target.value));
    setCurrentPage(1);
  };

  const openModal = async (func?: SysFunction, viewMode: boolean = false) => {
    setIsViewMode(viewMode);
    if (func) {
      setEditingFunction(func);
      setFormData({
        func_code: func.func_code,
        upper_func_id: func.upper_func_id,
        func_cname: func.func_cname,
        func_ename: func.func_ename,
        func_type: func.func_type,
        func_order: func.func_order,
        func_icon: func.func_icon || '',
        func_module_name: func.func_module_name || '',
        module_item: func.module_item || [],
        description: func.description || '',
        is_mana: func.is_mana,
        is_active: func.is_active
      });
      // 解析 module_item - 直接從陣列中取得操作類型字串
      if (func.module_item && func.module_item.length > 0) {
        setModuleItemActions(func.module_item);
      } else {
        setModuleItemActions([]);
      }

      // 如果是查看模式，記錄 Read 日誌
      if (viewMode) {
        try {
          await logRead('sysfunction', { id: func.id, func_code: func.func_code, func_cname: func.func_cname });
        } catch (err) {
          console.error('[SysFunctionsPage] Failed to log Read:', err);
        }
      }
    } else {
      setEditingFunction(null);
      setFormData({
        func_code: '',
        upper_func_id: 0,
        func_cname: '',
        func_ename: '',
        func_type: 2,
        func_order: 0,
        func_icon: '',
        func_module_name: '',
        module_item: [],
        description: '',
        is_mana: false,
        is_active: true
      });
      setModuleItemActions([]);
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingFunction(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // module_item 直接使用選中的操作類型字串陣列
    const submitData = {
      ...formData,
      module_item: moduleItemActions,
      // 如果是節點類型 (func_type=1)，func_module_name 必須是 null 或 undefined
      // 如果是功能類型 (func_type=2)，func_module_name 不能是空字串
      func_module_name: formData.func_type === 1
        ? undefined
        : (formData.func_module_name || undefined),
      // 空字串的欄位轉為 undefined
      func_icon: formData.func_icon || undefined,
      description: formData.description || undefined
    };

    try {
      if (editingFunction) {
        const updatedFunc = await updateSysFunction(editingFunction.id, submitData);
        await logUpdate('sysfunction', editingFunction as any, updatedFunc as any);
        alert(t('message.saveSuccess'));
      } else {
        const newFunc = await createSysFunction(submitData);
        await logCreate('sysfunction', newFunc as any);
        alert(t('message.createSuccess'));
      }
      closeModal();
      loadFunctions();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('common.error');

      try {
        if (editingFunction) {
          await logUpdate('sysfunction', editingFunction as any, submitData, errorMsg);
        } else {
          await logCreate('sysfunction', submitData, errorMsg);
        }
      } catch (logErr) {
        console.error('[SysFunctionsPage] Failed to log error:', logErr);
      }

      alert(errorMsg);
    }
  };

  const handleDelete = async (func: SysFunction) => {
    if (!window.confirm(t('common.confirmDelete'))) return;

    try {
      await deleteSysFunction(func.id);
      await logDelete('sysfunction', { id: func.id, func_code: func.func_code, func_cname: func.func_cname });
      alert(t('message.deleteSuccess'));
      loadFunctions();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('common.error');

      try {
        await logDelete('sysfunction', { id: func.id, func_code: func.func_code, func_cname: func.func_cname }, errorMsg);
      } catch (logErr) {
        console.error('[SysFunctionsPage] Failed to log error:', logErr);
      }

      alert(errorMsg);
    }
  };

  const handleStatusToggle = async (func: SysFunction) => {
    try {
      const oldData = { ...func };
      const newData = {
        ...func,
        is_active: !func.is_active
      };

      const updatedFunc = await updateSysFunction(func.id, newData);
      await logUpdate('sysfunction', oldData as any, updatedFunc as any);
      loadFunctions();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || t('common.error');

      try {
        await logUpdate('sysfunction', func as any, { ...func, is_active: !func.is_active }, errorMsg);
      } catch (logErr) {
        console.error('[SysFunctionsPage] Failed to log error:', logErr);
      }

      alert(errorMsg);
    }
  };

  const getFuncTypeText = (type: number) => {
    return type === 1 ? t('sysFunctions.types.node') : t('sysFunctions.types.function');
  };

  const getParentName = (parentId: number) => {
    if (parentId === 0) return t('sysFunctions.root');
    const parent = functions.find(f => f.id === parentId);
    return parent ? parent.func_cname : parentId.toString();
  };

  // 檢查權限
  if (permissionLoading) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (!hasPermission('sysfunction', 'read')) {
    return (
      <div className="page-container">
        <div className="error-message">{t('common.noPermission')}</div>
      </div>
    );
  }

  const canCreate = hasPermission('sysfunction', 'create');
  const canUpdate = hasPermission('sysfunction', 'update');
  const canDelete = hasPermission('sysfunction', 'delete');

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{pageTitle}</h1>
        {canCreate && (
          <button className="btn-primary" onClick={() => openModal()}>
            {t('common.create')}
          </button>
        )}
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder={t('sysFunctions.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn-secondary" onClick={handleSearch}>
          {t('common.search')}
        </button>
      </div>

      {/* 篩選條件 */}
      <div className="search-bar" style={{ marginTop: '12px' }}>
        <select
          value={filterUpperFunc}
          onChange={(e) => {
            setFilterUpperFunc(e.target.value === '' ? '' : parseInt(e.target.value));
            setCurrentPage(1);
          }}
          style={{ flex: '0 0 200px', padding: '10px 16px', border: '1px solid #dfe1e6', borderRadius: '6px', fontSize: '14px' }}
        >
          <option value="">所有上層功能</option>
          {getUpperFuncOptions().map(upperId => (
            <option key={upperId} value={upperId}>
              {getParentName(upperId)}
            </option>
          ))}
        </select>

        <select
          value={filterFuncType}
          onChange={(e) => {
            setFilterFuncType(e.target.value === '' ? '' : parseInt(e.target.value));
            setCurrentPage(1);
          }}
          style={{ flex: '0 0 200px', padding: '10px 16px', border: '1px solid #dfe1e6', borderRadius: '6px', fontSize: '14px' }}
        >
          <option value="">所有功能類型</option>
          <option value="1">{t('sysFunctions.types.node')}</option>
          <option value="2">{t('sysFunctions.types.function')}</option>
        </select>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', border: '1px solid #dfe1e6', borderRadius: '6px', fontSize: '14px', background: 'white', cursor: 'pointer', userSelect: 'none' }}>
          <input
            type="checkbox"
            checked={showOnlyMana}
            onChange={(e) => {
              setShowOnlyMana(e.target.checked);
              setCurrentPage(1);
            }}
            style={{ cursor: 'pointer' }}
          />
          只顯示管理功能
        </label>

        <button className="btn-secondary" onClick={handleResetFilters}>
          重置篩選
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
                  <th
                    onClick={() => handleSort('id')}
                    style={{ cursor: 'pointer', userSelect: 'none' }}
                  >
                    ID {sortBy === 'id' && (sortOrder === 'asc' ? '▲' : '▼')}
                  </th>
                  <th>{t('sysFunctions.funcCode')}</th>
                  <th>{t('sysFunctions.funcCname')}</th>
                  <th>{t('sysFunctions.funcEname')}</th>
                  <th>{t('sysFunctions.funcType')}</th>
                  <th>{t('sysFunctions.parent')}</th>
                  <th
                    onClick={() => handleSort('func_order')}
                    style={{ cursor: 'pointer', userSelect: 'none' }}
                  >
                    {t('sysFunctions.funcOrder')} {sortBy === 'func_order' && (sortOrder === 'asc' ? '▲' : '▼')}
                  </th>
                  <th>{t('sysFunctions.funcIcon')}</th>
                  <th>{t('common.status')}</th>
                  <th>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {currentFunctions.map((func) => (
                  <tr key={func.id}>
                    <td>{func.id}</td>
                    <td>{func.func_code}</td>
                    <td>{func.func_cname}</td>
                    <td>{func.func_ename}</td>
                    <td>{getFuncTypeText(func.func_type)}</td>
                    <td>{getParentName(func.upper_func_id)}</td>
                    <td>{func.func_order}</td>
                    <td>{func.func_icon || '-'}</td>
                    <td>
                      <span
                        className={`status-badge ${func.is_active ? 'active' : 'inactive'}`}
                        onClick={() => handleStatusToggle(func)}
                        style={{ cursor: 'pointer' }}
                      >
                        {func.is_active ? t('common.active') : t('common.inactive')}
                      </span>
                    </td>
                    <td className="actions">
                      {canUpdate && (
                        <button className="btn-edit" onClick={() => openModal(func, false)}>
                          {t('common.edit')}
                        </button>
                      )}
                      {!canUpdate && hasPermission('sysfunction', 'read') && (
                        <button className="btn-secondary" onClick={() => openModal(func, true)}>
                          {t('common.view')}
                        </button>
                      )}
                      {canDelete && (
                        <button className="btn-delete" onClick={() => handleDelete(func)}>
                          {t('common.delete')}
                        </button>
                      )}
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
                共 {filteredFunctions.length} 筆資料，第 {currentPage} / {totalPages} 頁
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
              <h2>
                {isViewMode ? t('common.view') : (editingFunction ? t('common.edit') : t('common.create'))}
              </h2>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>{t('sysFunctions.funcCode')} *</label>
                  <input
                    type="text"
                    value={formData.func_code}
                    onChange={(e) => setFormData({ ...formData, func_code: e.target.value })}
                    required
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcCname')} *</label>
                  <input
                    type="text"
                    value={formData.func_cname}
                    onChange={(e) => setFormData({ ...formData, func_cname: e.target.value })}
                    required
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcEname')} *</label>
                  <input
                    type="text"
                    value={formData.func_ename}
                    onChange={(e) => setFormData({ ...formData, func_ename: e.target.value })}
                    required
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcType')} *</label>
                  <select
                    value={formData.func_type}
                    onChange={(e) => setFormData({ ...formData, func_type: parseInt(e.target.value) })}
                    required
                    disabled={isViewMode}
                  >
                    <option value={1}>{t('sysFunctions.types.node')}</option>
                    <option value={2}>{t('sysFunctions.types.function')}</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.parent')}</label>
                  <select
                    value={formData.upper_func_id}
                    onChange={(e) => setFormData({ ...formData, upper_func_id: parseInt(e.target.value) })}
                    disabled={isViewMode}
                  >
                    <option value={0}>{t('sysFunctions.root')}</option>
                    {functions.filter(f => f.func_type === 1).map(f => (
                      <option key={f.id} value={f.id}>{f.func_cname}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcOrder')} *</label>
                  <input
                    type="number"
                    value={formData.func_order}
                    onChange={(e) => setFormData({ ...formData, func_order: parseInt(e.target.value) })}
                    required
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcIcon')}</label>
                  <input
                    type="text"
                    value={formData.func_icon}
                    onChange={(e) => setFormData({ ...formData, func_icon: e.target.value })}
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>{t('sysFunctions.funcModuleName')} {formData.func_type === 2 ? '*' : ''}</label>
                  <input
                    type="text"
                    value={formData.func_module_name}
                    onChange={(e) => setFormData({ ...formData, func_module_name: e.target.value })}
                    placeholder={formData.func_type === 2 ? t('sysFunctions.funcModuleNamePlaceholder') : t('sysFunctions.funcModuleNameDisabled')}
                    disabled={isViewMode || formData.func_type === 1}
                    required={formData.func_type === 2}
                    style={(isViewMode || formData.func_type === 1) ? { backgroundColor: '#f5f5f5', cursor: 'not-allowed' } : {}}
                  />
                </div>
                <div className="form-group full-width">
                  <label>{t('sysFunctions.moduleItem')}</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', padding: '10px 0' }}>
                    {['Create', 'Read', 'Update', 'Delete', 'Print', 'File'].map(action => (
                      <label
                        key={action}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          marginRight: '15px',
                          cursor: (isViewMode || formData.func_type === 1) ? 'not-allowed' : 'pointer',
                          opacity: (isViewMode || formData.func_type === 1) ? 0.5 : 1
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={moduleItemActions.includes(action)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setModuleItemActions([...moduleItemActions, action]);
                            } else {
                              setModuleItemActions(moduleItemActions.filter(a => a !== action));
                            }
                          }}
                          disabled={isViewMode || formData.func_type === 1}
                          style={{ marginRight: '5px' }}
                        />
                        {t(`sysFunctions.permissions.${action.toLowerCase()}`)}
                      </label>
                    ))}
                  </div>
                  <small style={{ color: '#6c757d', fontSize: '12px' }}>
                    {formData.func_type === 1
                      ? t('sysFunctions.permissionDisabledHint')
                      : t('sysFunctions.permissionHint')}
                  </small>
                </div>
                <div className="form-group full-width">
                  <label>{t('sysFunctions.description')}</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    disabled={isViewMode}
                  />
                </div>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_mana}
                      onChange={(e) => setFormData({ ...formData, is_mana: e.target.checked })}
                      disabled={isViewMode}
                    />
                    {t('sysFunctions.isMana')}
                  </label>
                </div>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      disabled={isViewMode}
                    />
                    {t('common.active')}
                  </label>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  {isViewMode ? t('common.close') : t('common.cancel')}
                </button>
                {!isViewMode && (
                  <button type="submit" className="btn-primary">
                    {t('common.save')}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SysFunctionsPage;
