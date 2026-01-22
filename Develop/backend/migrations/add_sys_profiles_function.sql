-- 新增 sys_profiles 功能定義到 system_functions
-- 並為角色 1 設定完整權限

DO $$
DECLARE
    func_id INTEGER;
    system_module_id INTEGER;
BEGIN
    -- 檢查是否已存在
    SELECT id INTO func_id FROM system_functions WHERE func_code = 'sys_profiles';

    IF func_id IS NULL THEN
        -- 找到「系統管理」模組的 ID (假設存在，如果不存在需要先建立)
        SELECT id INTO system_module_id FROM system_functions
        WHERE func_type = 1 AND func_cname LIKE '%系統%'
        ORDER BY func_order LIMIT 1;

        -- 如果找不到父模組，使用 0 (根節點)
        IF system_module_id IS NULL THEN
            system_module_id := 0;
        END IF;

        -- 新增 sys_profiles 功能
        INSERT INTO system_functions (
            func_code,
            upper_func_id,
            func_cname,
            func_ename,
            func_type,
            func_order,
            func_icon,
            module_code,
            module_item,
            description,
            is_mana,
            is_active,
            edit_by,
            created_at
        ) VALUES (
            'sys_profiles',
            system_module_id,
            '系統基本資料',
            'System Profile',
            2,  -- 功能類型
            100,
            '⚙️',
            'sys_profiles',
            '["read", "update"]'::jsonb,
            '系統基本設定資料（單筆）',
            true,  -- 管理功能
            true,
            1,
            CURRENT_TIMESTAMP
        ) RETURNING id INTO func_id;

        RAISE NOTICE '已新增 sys_profiles 功能，ID: %', func_id;
    ELSE
        RAISE NOTICE 'sys_profiles 功能已存在，ID: %', func_id;
    END IF;

    -- 為角色 1 設定權限
    IF NOT EXISTS (
        SELECT 1 FROM role_rights
        WHERE user_role_id = 1 AND func_code = 'sys_profiles'
    ) THEN
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
            'sys_profiles',
            false,  -- 不需要新增
            true,   -- 讀取
            true,   -- 修改
            false,  -- 不需要刪除
            false,
            false,
            1,
            CURRENT_TIMESTAMP
        );

        RAISE NOTICE '已為角色 1 設定 sys_profiles 權限';
    ELSE
        RAISE NOTICE '角色 1 已有 sys_profiles 權限';
    END IF;
END $$;

-- 驗證結果
SELECT
    sf.id,
    sf.func_code,
    sf.func_cname,
    sf.module_code,
    sf.is_active
FROM system_functions sf
WHERE sf.func_code = 'sys_profiles';

SELECT
    rr.id,
    rr.user_role_id,
    rr.func_code,
    rr.is_read,
    rr.is_update
FROM role_rights rr
WHERE rr.func_code = 'sys_profiles' AND rr.user_role_id = 1;
