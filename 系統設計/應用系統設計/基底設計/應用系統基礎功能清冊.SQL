-- ==========================================
-- system_functions 資料備份
-- 備份時間: 2026-01-21 18:21:11
-- 資料筆數: 22
-- ==========================================

-- 使用方式：執行 restore_system_functions.py

-- 清空現有資料（小心使用！）
-- TRUNCATE system_functions RESTART IDENTITY CASCADE;

-- 插入資料
INSERT INTO system_functions (
    id, func_code, upper_func_id, func_cname, func_ename, func_type,
    func_order, func_icon, module_code, module_item, description,
    is_mana, is_active, edit_by, created_at
) VALUES
(1, 'login', 0, '使用者登入', 'User Login', 2, 1, '📥', 'login', '["Read"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(2, 'logout', 0, '使用者登出', 'User Logout', 2, 2, '🚪', 'logout', '["read"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(3, 'change_password', 0, '密碼變更', 'Change Password', 2, 3, '🔑', 'change_password', '["update"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(4, 'user_profile', 0, '個人資料變更', 'User Profile', 2, 4, '👤', 'user_profile', '["read", "update"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(5, 'dashboard', 0, '儀表板', 'Dashboard', 2, 5, NULL, 'home', '[]'::jsonb, '系統儀表板首頁', False, True, 1, CURRENT_TIMESTAMP),
(10, 'system_mana', 0, '系統管理後台', 'System Management', 1, 90, '🖥️', NULL, '[]'::jsonb, '111', True, True, 1, CURRENT_TIMESTAMP),
(11, 'sys_profile', 10, '系統基本資料', 'System Profile', 2, 9010, '⚙️', 'sys_profiles', '["Read", "Update"]'::jsonb, '', True, True, 1, CURRENT_TIMESTAMP),
(12, 'organizations', 10, '組織資料維護', 'Organizations', 2, 9020, '🏢', 'organizations', '["Create", "Read", "Update", "Delete"]'::jsonb, '', True, True, 1, CURRENT_TIMESTAMP),
(13, 'user_roles', 10, '角色資料維護', 'User Roles', 2, 9030, '🗝️', 'user_roles', '["Create", "Read", "Update", "Delete", "Print", "File"]'::jsonb, '', True, True, 1, CURRENT_TIMESTAMP),
(14, 'users', 10, '使用者資料維護', 'User Details', 2, 9040, '👨🏻‍👨🏻‍👧🏻‍👦🏻', 'users', '["Create", "Read", "Update", "Delete", "Print", "File"]'::jsonb, '', True, True, 1, CURRENT_TIMESTAMP),
(15, 'system_functions', 10, '系統功能資料維護', 'System Function', 2, 9050, '📚', 'system_functions', '["Create", "Read", "Update", "Delete", "Print", "File"]'::jsonb, NULL, True, True, 1, CURRENT_TIMESTAMP),
(16, 'role_rights', 10, '角色權限設定作業', 'Role Permission Settings', 2, 9060, '🔑', 'role_rights', '["Create", "Read", "Update", "Delete"]'::jsonb, '為不同角色配置功能存取權限，支援新增、讀取、修改、刪除等細粒度權限控制', True, True, 1, CURRENT_TIMESTAMP),
(17, 'user_logs', 10, '使用者日誌紀錄', 'User Logs', 2, 9070, '⏱️', 'user_logs', '["Read"]'::jsonb, NULL, True, True, 1, CURRENT_TIMESTAMP),
(18, 'system_notifications', 10, '系統通知管理', 'System Notifications', 2, 9080, NULL, 'system_notifications', '["Create", "Read", "Update", "Delete"]'::jsonb, '系統公告通知管理，可發布重要訊息給使用者', True, True, 1, CURRENT_TIMESTAMP),
(19, 'standard_settings', 0, '標準化設定', 'Standard Settings', 1, 80, '💻', NULL, '[]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(20, 'system_codes', 19, '系統代碼維護', 'system code setting', 2, 8010, '🔖', 'system_codes', '["Create", "Read", "Update", "Delete"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(21, 'numbering_rules', 19, '編號規則設定', 'Numbering Rules', 2, 8020, NULL, 'numbering_rules', '["Create", "Read", "Update", "Delete"]'::jsonb, '單據編號規則設定，支援各種單據的自動編號格式', False, True, 1, CURRENT_TIMESTAMP),
(22, 'file_attachments', 19, '檔案附件管理', 'File Attachments', 2, 8030, NULL, 'file_attachments', '["Create", "Read", "Update", "Delete"]'::jsonb, '檔案上傳與附件管理，支援各種檔案類型的上傳與下載', False, True, 1, CURRENT_TIMESTAMP),
(23, 'system_parameters', 10, '系統參數設定', 'System Parameters', 2, 9090, NULL, 'system_parameters', '["Create", "Read", "Update", "Delete"]'::jsonb, '系統全域參數設定，如語言、時區、頁面大小等', True, True, 1, CURRENT_TIMESTAMP),
(24, 'tenants', 0, '組織管理作業', 'Organ Management', 1, 70, '🏢', NULL, '[]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP),
(25, 'tenant_profile', 24, '組織資料管理', 'Tenant Profile', 2, 7010, '📝', 'organizations', '["Update", "Read"]'::jsonb, '', False, True, 1, CURRENT_TIMESTAMP),
(26, 'tenant_users', 24, '組織成員管理', 'Tenant Users', 2, 7020, '🪪', 'users', '["Create", "Read", "Update", "Delete"]'::jsonb, NULL, False, True, 1, CURRENT_TIMESTAMP);

-- 驗證匯入結果
SELECT COUNT(*) as total_records FROM system_functions;

-- 顯示所有功能
SELECT id, func_code, func_cname, module_code, func_order
FROM system_functions
ORDER BY func_order, id;