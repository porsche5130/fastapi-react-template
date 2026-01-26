/**
 * Numbering Rules Page
 * 編號規則設定頁面
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import transactionService from '../services/transactionService';
import numberingRulesService, {
  SequenceRule,
  SequenceRuleCreate,
  SequenceRuleUpdate,
} from '../services/numberingRulesService';
import { useFunctionName } from '../hooks/useFunctionName';
import { logView, logCreate, logUpdate, logDelete } from '../utils/userLogHelper';
import '../styles/DataTable.css';

const NumberingRulesPage: React.FC = () => {
  const { t } = useTranslation();
  const pageTitle = useFunctionName('numbering_rules');
  const [txnToken, setTxnToken] = useState<string>('');
  const [permissions, setPermissions] = useState<any>({});
  const [rules, setRules] = useState<SequenceRule[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(true);

  // 分頁狀態
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // 表單狀態
  const [showModal, setShowModal] = useState(false);
  const [editingRule, setEditingRule] = useState<SequenceRule | null>(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [formData, setFormData] = useState<SequenceRuleCreate>({
    rule_code: '',
    rule_name: '',
    description: '',
    prefix: '',
    date_format: '',
    sequence_length: 6,
    suffix: '',
    separator: '-',
    reset_mode: 'never',
    example: '',
    is_active: true,
  });

  // 預覽狀態
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);

  // 生成編號測試
  const [showGenerateTest, setShowGenerateTest] = useState(false);
  const [generatedNumbers, setGeneratedNumbers] = useState<string[]>([]);

  useEffect(() => {
    const initPage = async () => {
      try {
        const response = await transactionService.requestTransactionToken('numbering_rules');
        setTxnToken(response.txn_token);
        setPermissions(response.permissions);

        // 取得 token 後立即載入資料
        if (response.permissions.read) {
          const rulesResponse = await numberingRulesService.getAll(
            0,
            100,
            showActiveOnly ? true : undefined,
            searchTerm || undefined,
            response.txn_token
          );
          setRules(rulesResponse.items);
          setTotal(rulesResponse.total);

          // 記錄瀏覽日誌
          await logView('numbering_rules', {
            filters: {
              skip: 0,
              limit: 100,
              is_active: showActiveOnly ? true : undefined,
              search: searchTerm || undefined
            }
          });
        }
      } catch (error: any) {
        console.error('Init page failed:', error);
        alert(t('common.error'));
      }
    };

    initPage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 自動產生範例的函數
  const generateExample = (
    prefix: string | undefined,
    date_format: string | undefined,
    sequence_length: number | undefined,
    suffix: string | undefined,
    separator: string | undefined
  ) => {
    let example = '';

    // 添加前綴
    if (prefix) {
      example += prefix;
    }

    // 添加分隔符號（如果有前綴）
    if (example && separator) {
      example += separator;
    }

    // 添加日期格式
    if (date_format) {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');

      switch (date_format) {
        case 'YYYY':
          example += year;
          break;
        case 'YYYYMM':
          example += `${year}${month}`;
          break;
        case 'YYYYMMDD':
          example += `${year}${month}${day}`;
          break;
      }

      // 添加分隔符號（如果有日期）
      if (separator) {
        example += separator;
      }
    }

    // 添加流水號
    const length = sequence_length || 6;
    const sequenceNumber = '0'.repeat(Math.max(0, length - 1));
    example += sequenceNumber + '1';

    // 添加後綴
    if (suffix) {
      if (separator) {
        example += separator;
      }
      example += suffix;
    }

    return example;
  };

  // 自動產生範例（僅在新增模式）
  useEffect(() => {
    if (showModal && !isViewMode && !editingRule) {
      const { prefix, date_format, sequence_length, suffix, separator } = formData;
      const newExample = generateExample(prefix, date_format, sequence_length, suffix, separator);

      // 更新範例（只在範例不同時更新，避免無限循環）
      if (newExample !== formData.example) {
        setFormData(prev => ({ ...prev, example: newExample }));
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.prefix, formData.date_format, formData.sequence_length, formData.suffix, formData.separator, showModal, isViewMode, editingRule]);

  const loadRules = async () => {
    if (!txnToken) return;

    setLoading(true);
    try {
      const response = await numberingRulesService.getAll(
        0,
        100,
        showActiveOnly ? true : undefined,
        searchTerm || undefined,
        txnToken
      );
      setRules(response.items);
      setTotal(response.total);
    } catch (error: any) {
      alert(t('message.loadFailed'));
      console.error('Load rules failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadRules();
  };

  const handleCreate = () => {
    setEditingRule(null);
    setIsViewMode(false);
    setFormData({
      rule_code: '',
      rule_name: '',
      description: '',
      prefix: '',
      date_format: '',
      sequence_length: 6,
      suffix: '',
      separator: '-',
      reset_mode: 'never',
      example: '',
      is_active: true,
    });
    setShowModal(true);
  };

  const handleEdit = (rule: SequenceRule, viewMode = false) => {
    // 使用批次狀態更新，先設定資料再開啟 Modal
    setEditingRule(rule);
    setIsViewMode(viewMode);

    // 確保所有可選欄位都轉換為字串，避免 null 值
    const editFormData = {
      rule_code: rule.rule_code || '',
      rule_name: rule.rule_name || '',
      description: rule.description || '',
      prefix: rule.prefix || '',
      date_format: rule.date_format || '',
      sequence_length: rule.sequence_length || 6,
      suffix: rule.suffix || '',
      separator: rule.separator || '',
      reset_mode: rule.reset_mode || 'never',
      example: rule.example || '',
      is_active: rule.is_active ?? true,
    };

    setFormData(editFormData);

    // 延遲開啟 Modal，確保所有狀態都已更新
    requestAnimationFrame(() => {
      setShowModal(true);
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingRule) {
        // 更新操作
        const updated = await numberingRulesService.update(editingRule.id, formData, txnToken);
        alert(t('message.saveSuccess'));

        // 記錄更新日誌
        try {
          await logUpdate('numbering_rules', editingRule, updated);
        } catch (logErr) {
          console.error('[NumberingRulesPage] Failed to log update:', logErr);
        }
      } else {
        // 新增操作
        const created = await numberingRulesService.create(formData, txnToken);
        alert(t('message.createSuccess'));

        // 記錄新增日誌
        try {
          await logCreate('numbering_rules', created);
        } catch (logErr) {
          console.error('[NumberingRulesPage] Failed to log create:', logErr);
        }
      }
      setShowModal(false);
      loadRules();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || t('message.saveFailed');
      alert(errorMsg);

      // 記錄失敗日誌
      try {
        if (editingRule) {
          await logUpdate('numbering_rules', editingRule, {}, errorMsg);
        } else {
          await logCreate('numbering_rules', {}, errorMsg);
        }
      } catch (logErr) {
        console.error('[NumberingRulesPage] Failed to log error:', logErr);
      }
    }
  };

  const handleDelete = async (rule: SequenceRule) => {
    if (!window.confirm(t('common.confirmDelete'))) return;

    try {
      await numberingRulesService.delete(rule.id, txnToken);
      alert(t('message.deleteSuccess'));
      loadRules();

      // 記錄刪除日誌
      try {
        await logDelete('numbering_rules', rule);
      } catch (logErr) {
        console.error('[NumberingRulesPage] Failed to log delete:', logErr);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || t('message.deleteFailed');
      alert(errorMsg);

      // 記錄失敗日誌
      try {
        await logDelete('numbering_rules', rule, errorMsg);
      } catch (logErr) {
        console.error('[NumberingRulesPage] Failed to log error:', logErr);
      }
    }
  };

  const handlePreview = async (ruleCode: string) => {
    try {
      const data = await numberingRulesService.previewNumber(ruleCode, txnToken);
      setPreviewData(data);
      setShowPreview(true);
    } catch (error: any) {
      alert(error.response?.data?.detail || '預覽失敗');
    }
  };

  const handleGenerateTest = async (ruleCode: string) => {
    try {
      const result = await numberingRulesService.generateNumber({ rule_code: ruleCode });
      setGeneratedNumbers([result.number, ...generatedNumbers]);
      setShowGenerateTest(true);
    } catch (error: any) {
      alert(error.response?.data?.detail || '產生失敗');
    }
  };

  // 等待 token 取得
  if (!txnToken) {
    return (
      <div className="page-container">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  // 檢查讀取權限
  if (!permissions.read) {
    return (
      <div className="page-container">
        <div className="error-message">{t('common.noPermission')}</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>{pageTitle}</h1>
        {permissions.create && (
          <button className="btn-primary" onClick={handleCreate}>
            {t('common.create')}
          </button>
        )}
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder={t('numberingRules.searchPlaceholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn-secondary" onClick={handleSearch}>
          {t('common.search')}
        </button>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={showActiveOnly}
            onChange={(e) => {
              setShowActiveOnly(e.target.checked);
              setCurrentPage(1);
              // 延遲執行以確保狀態已更新
              setTimeout(() => loadRules(), 0);
            }}
          />
          {t('numberingRules.showActiveOnly')}
        </label>
      </div>

      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead className="table-header-dark-green">
              <tr>
                <th>{t('numberingRules.ruleCode')}</th>
                <th>{t('numberingRules.ruleName')}</th>
                <th>{t('numberingRules.formatExample')}</th>
                <th>{t('numberingRules.resetMode')}</th>
                <th>{t('common.status')}</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {rules
                .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                .map((rule) => (
                  <tr key={rule.id}>
                    <td>
                      <code>{rule.rule_code}</code>
                    </td>
                    <td>{rule.rule_name}</td>
                    <td>
                      <code className="example">{rule.example}</code>
                    </td>
                    <td>
                      <span className={`reset-mode ${rule.reset_mode}`}>
                        {rule.reset_mode === 'never'
                          ? t('numberingRules.resetModeNever')
                          : rule.reset_mode === 'yearly'
                          ? t('numberingRules.resetModeYearly')
                          : rule.reset_mode === 'monthly'
                          ? t('numberingRules.resetModeMonthly')
                          : t('numberingRules.resetModeDaily')}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${rule.is_active ? 'active' : 'inactive'}`}>
                        {rule.is_active ? t('common.active') : t('common.inactive')}
                      </span>
                    </td>
                    <td className="actions">
                      {permissions.update && (
                        <button className="btn-edit" onClick={() => handleEdit(rule, false)} style={{ marginRight: '12px' }}>
                          {t('common.edit')}
                        </button>
                      )}
                      {!permissions.update && permissions.read && (
                        <button className="btn-secondary" onClick={() => handleEdit(rule, true)} style={{ marginRight: '12px' }}>
                          {t('common.view')}
                        </button>
                      )}
                      {permissions.delete && (
                        <button className="btn-delete" onClick={() => handleDelete(rule)}>
                          {t('common.delete')}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>

          {rules.length === 0 && (
            <div className="no-data">{t('message.noData')}</div>
          )}

          {rules.length > 0 && (
            <div className="pagination-container">
              <div className="pagination-info">
                <label>
                  {t('common.itemsPerPage')}：
                  <select
                    value={itemsPerPage}
                    onChange={(e) => {
                      setItemsPerPage(Number(e.target.value));
                      setCurrentPage(1);
                    }}
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                  {t('numberingRules.items')}
                </label>
                <span className="pagination-text">
                  {t('numberingRules.totalRecords', {
                    total: rules.length,
                    current: currentPage,
                    totalPages: Math.ceil(rules.length / itemsPerPage)
                  })}
                </span>
              </div>
              <div className="pagination-buttons">
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                >
                  ⟪
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                >
                  ‹
                </button>
                <button className="btn-pagination active">
                  {currentPage}
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, Math.ceil(rules.length / itemsPerPage)))}
                  disabled={currentPage === Math.ceil(rules.length / itemsPerPage)}
                >
                  ›
                </button>
                <button
                  className="btn-pagination"
                  onClick={() => setCurrentPage(Math.ceil(rules.length / itemsPerPage))}
                  disabled={currentPage === Math.ceil(rules.length / itemsPerPage)}
                >
                  ⟫
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 新增/編輯 Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                📋 {pageTitle} - {isViewMode
                  ? t('common.viewOperation')
                  : (editingRule ? t('common.editOperation') : t('common.createOperation'))}
              </h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label>{t('numberingRules.ruleCode')} *</label>
                    <input
                      type="text"
                      value={formData.rule_code}
                      onChange={(e) => setFormData({ ...formData, rule_code: e.target.value })}
                      required
                      disabled={!!editingRule || isViewMode}
                      placeholder={t('numberingRules.ruleCodePlaceholder')}
                    />
                  </div>
                  <div className="form-group">
                    <label>{t('numberingRules.ruleName')} *</label>
                    <input
                      type="text"
                      value={formData.rule_name}
                      onChange={(e) => setFormData({ ...formData, rule_name: e.target.value })}
                      required
                      disabled={isViewMode}
                      placeholder={t('numberingRules.ruleNamePlaceholder')}
                    />
                  </div>

                  <div className="form-group full-width">
                    <label>{t('numberingRules.description')}</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder={t('numberingRules.descriptionPlaceholder')}
                      rows={2}
                      disabled={isViewMode}
                    />
                  </div>

                  <div className="form-group">
                    <label>{t('numberingRules.prefix')}</label>
                    <input
                      type="text"
                      value={formData.prefix}
                      onChange={(e) => setFormData({ ...formData, prefix: e.target.value })}
                      placeholder={t('numberingRules.prefixPlaceholder')}
                      disabled={isViewMode}
                    />
                  </div>
                  <div className="form-group">
                    <label>{t('numberingRules.dateFormat')}</label>
                    <select
                      value={formData.date_format}
                      onChange={(e) => setFormData({ ...formData, date_format: e.target.value })}
                      disabled={isViewMode}
                    >
                      <option value="">{t('numberingRules.dateFormatNone')}</option>
                      <option value="YYYY">{t('numberingRules.dateFormatYear')}</option>
                      <option value="YYYYMM">{t('numberingRules.dateFormatYearMonth')}</option>
                      <option value="YYYYMMDD">{t('numberingRules.dateFormatYearMonthDay')}</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>{t('numberingRules.sequenceLength')} *</label>
                    <input
                      type="number"
                      value={formData.sequence_length}
                      onChange={(e) =>
                        setFormData({ ...formData, sequence_length: parseInt(e.target.value) })
                      }
                      min={1}
                      max={20}
                      required
                      disabled={isViewMode}
                    />
                  </div>
                  <div className="form-group">
                    <label>{t('numberingRules.separator')}</label>
                    <input
                      type="text"
                      value={formData.separator}
                      onChange={(e) => setFormData({ ...formData, separator: e.target.value })}
                      placeholder={t('numberingRules.separatorPlaceholder')}
                      maxLength={5}
                      disabled={isViewMode}
                    />
                  </div>

                  <div className="form-group">
                    <label>{t('numberingRules.suffix')}</label>
                    <input
                      type="text"
                      value={formData.suffix}
                      onChange={(e) => setFormData({ ...formData, suffix: e.target.value })}
                      placeholder={t('numberingRules.suffixPlaceholder')}
                      disabled={isViewMode}
                    />
                  </div>
                  <div className="form-group">
                    <label>{t('numberingRules.resetMode')} *</label>
                    <select
                      value={formData.reset_mode}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          reset_mode: e.target.value as any,
                        })
                      }
                      required
                      disabled={isViewMode}
                    >
                      <option value="never">{t('numberingRules.resetModeNever')}</option>
                      <option value="yearly">{t('numberingRules.resetModeYearly')}</option>
                      <option value="monthly">{t('numberingRules.resetModeMonthly')}</option>
                      <option value="daily">{t('numberingRules.resetModeDaily')}</option>
                    </select>
                  </div>

                  <div className="form-group full-width">
                    <label>{t('numberingRules.exampleAutoGenerated')}</label>
                    <input
                      type="text"
                      value={formData.example}
                      readOnly
                      placeholder={t('numberingRules.examplePlaceholder')}
                      style={{ backgroundColor: '#f0f0f0', cursor: 'default' }}
                    />
                  </div>

                  <div className="form-group full-width">
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
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
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

      {/* 預覽 Modal */}
      {showPreview && previewData && (
        <div className="modal-overlay" onClick={() => setShowPreview(false)}>
          <div className="modal-content preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{t('numberingRules.previewNextNumber')}</h2>
              <button className="close-btn" onClick={() => setShowPreview(false)}>
                ×
              </button>
            </div>
            <div className="preview-content">
              <div className="preview-number">
                <code>{previewData.preview_number}</code>
              </div>
              <div className="preview-details">
                <p>
                  <strong>{t('numberingRules.ruleCode')}:</strong> {previewData.rule_code}
                </p>
                <p>
                  <strong>{t('numberingRules.nextSequenceValue')}:</strong> {previewData.next_sequence_value}
                </p>
                <p>
                  <strong>{t('numberingRules.period')}:</strong> {previewData.period}
                </p>
                <p>
                  <strong>{t('numberingRules.currentValue')}:</strong> {previewData.current_value}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 測試產生 Modal */}
      {showGenerateTest && (
        <div className="modal-overlay" onClick={() => setShowGenerateTest(false)}>
          <div className="modal-content test-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{t('numberingRules.generatedNumbers')}</h2>
              <button className="close-btn" onClick={() => setShowGenerateTest(false)}>
                ×
              </button>
            </div>
            <div className="generated-numbers">
              {generatedNumbers.map((num, idx) => (
                <div key={idx} className="generated-number">
                  <code>{num}</code>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NumberingRulesPage;
