-- =====================================================
-- 測試資料：system_functions 表
-- =====================================================
-- 日期：2026-01-21
-- 說明：建立測試資料以驗證新系統功能
-- 注意：僅用於測試環境
-- =====================================================

-- 清除測試資料（如果存在）
DELETE FROM system_functions WHERE func_code IN ('test_module', 'test_function', 'test_master_detail');

-- 插入測試節點
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
    edit_by
) VALUES (
    'test_module',          -- func_code
    0,                      -- upper_func_id (根節點)
    '測試模組',             -- func_cname
    'Test Module',          -- func_ename
    1,                      -- func_type (節點)
    9999,                   -- func_order
    '🧪',                   -- func_icon
    NULL,                   -- module_code (節點不需要)
    '[]'::jsonb,           -- module_item
    '測試用的模組節點',     -- description
    false,                  -- is_mana
    true,                   -- is_active
    1                       -- edit_by
);

-- 插入測試功能（單一資料表）
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
    edit_by
) VALUES (
    'test_function',
    (SELECT id FROM system_functions WHERE func_code = 'test_module'),
    '測試功能',
    'Test Function',
    2,                      -- func_type (功能)
    9999,
    '📝',
    'test_function',        -- module_code
    '["create", "read", "update", "delete"]'::jsonb,
    '測試用的單一資料表功能',
    false,
    true,
    1
);

-- 插入測試功能（Master-Detail）
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
    edit_by
) VALUES (
    'test_master_detail',
    (SELECT id FROM system_functions WHERE func_code = 'test_module'),
    '測試主從',
    'Test Master-Detail',
    2,
    10000,
    '📋',
    'test_master_detail',   -- module_code
    '["create", "read", "update", "delete"]'::jsonb,
    '測試用的 Master-Detail 功能，包含多個資料表',
    false,
    true,
    1
);

-- 驗證插入結果
SELECT
    id,
    func_code,
    func_cname,
    module_code,
    func_type,
    is_active
FROM system_functions
WHERE func_code IN ('test_module', 'test_function', 'test_master_detail')
ORDER BY func_order;

-- =====================================================
-- 測試資料建立完成
-- =====================================================
-- 已建立：
-- 1. test_module - 測試模組節點
-- 2. test_function - 測試功能（單一資料表）
-- 3. test_master_detail - 測試功能（Master-Detail）
--
-- 測試步驟：
-- 1. 前端存取 /system_functions 路由
-- 2. 測試 CRUD 操作
-- 3. 測試權限檢查
-- 4. 測試完成後執行清理腳本
--
-- 清理測試資料：
-- DELETE FROM system_functions
-- WHERE func_code IN ('test_module', 'test_function', 'test_master_detail');
-- =====================================================
