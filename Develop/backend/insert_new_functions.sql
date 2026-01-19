-- 新增使用者角色設定、使用者設定、系統功能設定到選單
-- 假設系統管理的節點 ID 為 2，請根據實際情況調整

-- 首先查詢系統管理節點的 ID（假設 func_code 為 'SYS_MANAGE'）
-- 如果沒有系統管理節點，請先建立

-- 方案1: 如果系統管理節點已存在，找出最大的 func_order
DO $$
DECLARE
    v_sys_manage_id INTEGER;
    v_max_order INTEGER;
    v_edit_by INTEGER := 1; -- 請改為實際的管理員 user_id
BEGIN
    -- 查找系統管理節點 ID
    SELECT id INTO v_sys_manage_id
    FROM sysfuction
    WHERE func_type = 1 AND func_cname LIKE '%系統管理%'
    LIMIT 1;

    -- 如果找不到，創建系統管理節點
    IF v_sys_manage_id IS NULL THEN
        INSERT INTO sysfuction (
            func_code, upper_func_id, func_cname, func_ename,
            func_type, func_order, func_icon, func_module_name,
            module_item, is_mana, is_active, edit_by
        ) VALUES (
            'SYS_MANAGE', 0, '系統管理', 'System Management',
            1, 100, '⚙️', NULL,
            '[]'::jsonb, true, true, v_edit_by
        ) RETURNING id INTO v_sys_manage_id;
    END IF;

    -- 查找系統管理節點下的最大 order
    SELECT COALESCE(MAX(func_order), 0) INTO v_max_order
    FROM sysfuction
    WHERE upper_func_id = v_sys_manage_id OR id = v_sys_manage_id;

    -- 插入使用者角色設定
    INSERT INTO sysfuction (
        func_code, upper_func_id, func_cname, func_ename,
        func_type, func_order, func_icon, func_module_name,
        module_item, description, is_mana, is_active, edit_by
    ) VALUES (
        'USER_ROLE_MANAGE', v_sys_manage_id, '使用者角色設定', 'User Roles',
        2, v_max_order + 1, '👥', 'UserRoles',
        '[{"path": "/user_roles", "name": "UserRoles"}]'::jsonb,
        '管理使用者角色權限', true, true, v_edit_by
    );

    -- 插入使用者設定
    INSERT INTO sysfuction (
        func_code, upper_func_id, func_cname, func_ename,
        func_type, func_order, func_icon, func_module_name,
        module_item, description, is_mana, is_active, edit_by
    ) VALUES (
        'USER_MANAGE', v_sys_manage_id, '使用者設定', 'User Management',
        2, v_max_order + 2, '👤', 'Users',
        '[{"path": "/users", "name": "Users"}]'::jsonb,
        '管理系統使用者帳號', true, true, v_edit_by
    );

    -- 插入系統功能設定
    INSERT INTO sysfuction (
        func_code, upper_func_id, func_cname, func_ename,
        func_type, func_order, func_icon, func_module_name,
        module_item, description, is_mana, is_active, edit_by
    ) VALUES (
        'SYS_FUNCTION_MANAGE', v_sys_manage_id, '系統功能設定', 'System Functions',
        2, v_max_order + 3, '🔧', 'SysFunctions',
        '[{"path": "/sysfunctions", "name": "SysFunctions"}]'::jsonb,
        '管理系統功能選單', true, true, v_edit_by
    );

    RAISE NOTICE 'Successfully inserted 3 new functions under system management (ID: %)', v_sys_manage_id;
END $$;
