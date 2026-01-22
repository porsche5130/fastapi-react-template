-- 將 sys_profile 資料表重新命名為 sys_profiles
-- 符合 system_functions 中的 module_code 命名規範

-- 檢查舊資料表是否存在，如果存在則重新命名
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sys_profile'
    ) THEN
        ALTER TABLE sys_profile RENAME TO sys_profiles;
        RAISE NOTICE '資料表 sys_profile 已重新命名為 sys_profiles';
    ELSE
        RAISE NOTICE '資料表 sys_profile 不存在，無需重新命名';
    END IF;
END $$;

-- 如果 sys_profiles 資料表是空的，插入初始資料
INSERT INTO sys_profiles (
    id,
    is_service,
    sys_url,
    sys_ctitle,
    sys_etitle,
    sys_ccopyright,
    sys_ecopyright,
    sys_organization,
    sys_mana_email,
    edit_by,
    created_at
) VALUES (
    1,
    true,
    'http://localhost:10181',
    '碳排專案活動申請系統',
    'Article 6.4 Management System',
    '© 2026 碳排專案活動申請系統',
    '© 2026 Article 6.4 Management System',
    1,
    'admin@example.com',
    1,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;
