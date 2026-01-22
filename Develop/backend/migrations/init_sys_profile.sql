-- 初始化 sys_profiles 資料表
-- 系統設定檔案（單筆資料，id=1）

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
