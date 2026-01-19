-- ============================================
-- 新增角色權限設定功能至系統功能表
-- 功能代碼: Role_Right
-- 日期: 2026-01-19
-- ============================================

-- 檢查功能是否已存在，若不存在則新增
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sysfuction WHERE func_code = 'Role_Right') THEN
        INSERT INTO sysfuction (
            func_code,
            upper_func_id,
            func_cname,
            func_ename,
            func_type,
            func_order,
            func_icon,
            func_module_name,
            module_item,
            description,
            is_mana,
            is_active,
            edit_by,
            created_at,
            updated_at
        ) VALUES (
            'Role_Right',
            1,  -- 上層功能ID: system_mana (系統管理後台)
            '角色權限設定作業',
            'Role Permission Settings',
            2,  -- 功能類型: 2=功能
            1050,  -- 排序順序 (在使用者設定作業之後)
            'lock',  -- 圖示
            'role_right',  -- 模組名稱
            '["Create", "Read", "Update", "Delete"]',  -- 可設定權限
            '為不同角色配置功能存取權限，支援新增、讀取、修改、刪除等細粒度權限控制',
            TRUE,  -- 是否為管理功能
            TRUE,  -- 是否啟用
            1,  -- 編輯者ID
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    ELSE
        UPDATE sysfuction SET
            func_cname = '角色權限設定作業',
            func_ename = 'Role Permission Settings',
            func_order = 1050,
            func_icon = 'lock',
            func_module_name = 'role_right',
            module_item = '["Create", "Read", "Update", "Delete"]',
            description = '為不同角色配置功能存取權限，支援新增、讀取、修改、刪除等細粒度權限控制',
            updated_at = CURRENT_TIMESTAMP
        WHERE func_code = 'Role_Right';
    END IF;
END $$;

-- 完成
SELECT 'Role_Right 功能已新增至系統功能表' AS message;
