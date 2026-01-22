-- ==========================================
-- 遷移資料到新版資料表
-- 日期: 2026-01-21
-- 說明: 將舊表資料複製到新表
-- ==========================================

-- 1. 遷移 user_role → user_roles
INSERT INTO user_roles (id, role_cname, role_ename, description, is_mana, is_active, edit_by, created_at, updated_at)
SELECT id, role_cname, role_ename, description, is_mana, is_active, edit_by, created_at, updated_at
FROM user_role
ON CONFLICT (id) DO NOTHING;

-- 更新 user_roles 的 sequence
SELECT setval('user_roles_id_seq', (SELECT MAX(id) FROM user_roles));

-- 2. 遷移 role_right → role_rights
-- 注意：需要將 sysfunction_id 轉換為 system_function_id
INSERT INTO role_rights (
    id, user_role_id, system_function_id, func_code,
    is_create, is_read, is_update, is_delete, is_print, is_file,
    edit_by, created_at, updated_at
)
SELECT
    rr.id,
    rr.user_role_id,
    sf_new.id as system_function_id,  -- 從新表取得對應的 id
    rr.func_code,
    rr.is_create,
    rr.is_read,
    rr.is_update,
    rr.is_delete,
    rr.is_print,
    rr.is_file,
    rr.edit_by,
    rr.created_at,
    rr.updated_at
FROM role_right rr
INNER JOIN sysfunction sf_old ON rr.sysfunction_id = sf_old.id
INNER JOIN system_functions sf_new ON sf_old.func_code = sf_new.func_code
ON CONFLICT (id) DO NOTHING;

-- 更新 role_rights 的 sequence
SELECT setval('role_rights_id_seq', (SELECT MAX(id) FROM role_rights));

-- 3. 遷移 userlogs → user_logs
-- 注意：需要將 user_detail_id 轉換為 user_id，sysfunction_id 轉換為 system_function_id
INSERT INTO user_logs (
    id, user_id, system_function_id, module_item, data_id, session_id,
    look_data, change_data, action_at, err_detail
)
SELECT
    ul.id,
    ul.user_detail_id as user_id,
    sf_new.id as system_function_id,  -- 從新表取得對應的 id
    ul.module_item,
    ul.data_id,
    ul.session_id,
    ul.look_data,
    ul.change_data,
    ul.action_at,
    ul.err_detail
FROM userlogs ul
LEFT JOIN sysfunction sf_old ON ul.sysfunction_id = sf_old.id
LEFT JOIN system_functions sf_new ON sf_old.func_code = sf_new.func_code
ON CONFLICT (id) DO NOTHING;

-- 更新 user_logs 的 sequence
SELECT setval('user_logs_id_seq', (SELECT MAX(id) FROM user_logs));

-- 驗證遷移結果
SELECT '舊表 → 新表 資料筆數比較' as description;

SELECT
    'user_role → user_roles' as migration,
    (SELECT COUNT(*) FROM user_role) as old_count,
    (SELECT COUNT(*) FROM user_roles) as new_count
UNION ALL
SELECT
    'role_right → role_rights' as migration,
    (SELECT COUNT(*) FROM role_right) as old_count,
    (SELECT COUNT(*) FROM role_rights) as new_count
UNION ALL
SELECT
    'userlogs → user_logs' as migration,
    (SELECT COUNT(*) FROM userlogs) as old_count,
    (SELECT COUNT(*) FROM user_logs) as new_count;
