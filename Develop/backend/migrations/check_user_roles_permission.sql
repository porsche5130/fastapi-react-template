-- 檢查 user_roles 功能的權限設定

-- 1. 檢查 system_functions 中是否有 user_roles
SELECT
    id,
    func_code,
    func_cname,
    module_code,
    is_active
FROM system_functions
WHERE func_code = 'user_roles';

-- 2. 檢查當前使用者（假設是 id=1）的角色
SELECT
    id,
    account,
    username,
    user_role
FROM users
WHERE id = 1;

-- 3. 檢查角色 1 對 user_roles 的權限設定
SELECT
    rr.id,
    rr.user_role_id,
    rr.system_function_id,
    rr.func_code,
    rr.is_create,
    rr.is_read,
    rr.is_update,
    rr.is_delete,
    sf.func_cname
FROM role_rights rr
JOIN system_functions sf ON rr.system_function_id = sf.id
WHERE rr.user_role_id = 1
  AND rr.func_code = 'user_roles';

-- 4. 如果沒有權限，插入預設權限（給角色 1 完整權限）
-- 先取得 user_roles 的 function_id
DO $$
DECLARE
    func_id INTEGER;
BEGIN
    SELECT id INTO func_id FROM system_functions WHERE func_code = 'user_roles';

    IF func_id IS NOT NULL THEN
        -- 檢查是否已有權限設定
        IF NOT EXISTS (
            SELECT 1 FROM role_rights
            WHERE user_role_id = 1 AND func_code = 'user_roles'
        ) THEN
            -- 插入完整權限
            INSERT INTO role_rights (
                user_role_id,
                system_function_id,
                func_code,
                is_create,
                is_read,
                is_update,
                is_delete,
                is_print,
                is_file,
                edit_by,
                created_at
            ) VALUES (
                1,
                func_id,
                'user_roles',
                true,
                true,
                true,
                true,
                false,
                false,
                1,
                CURRENT_TIMESTAMP
            );
            RAISE NOTICE '已為角色 1 新增 user_roles 的完整權限';
        ELSE
            RAISE NOTICE '角色 1 已有 user_roles 的權限設定';
        END IF;
    ELSE
        RAISE NOTICE 'system_functions 中找不到 user_roles';
    END IF;
END $$;
