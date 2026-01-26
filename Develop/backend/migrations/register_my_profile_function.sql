-- Register my_profile system function
-- This function allows users to view and update their own profile information

-- Only insert if not exists
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
    is_mana,
    is_active,
    edit_by
)
SELECT
    'my_profile',           -- func_code
    0,                      -- upper_func_id (root level, not in menu)
    '個人資料',              -- func_cname
    'My Profile',           -- func_ename
    2,                      -- func_type (2=Function)
    0,                      -- func_order
    'AccountCircle',        -- func_icon
    'my_profile',           -- module_code
    '["Read", "Update"]',   -- module_item (can read and update own profile)
    false,                  -- is_mana (not admin-only)
    true,                   -- is_active
    1                       -- edit_by (system user)
WHERE NOT EXISTS (
    SELECT 1 FROM system_functions WHERE func_code = 'my_profile'
);
