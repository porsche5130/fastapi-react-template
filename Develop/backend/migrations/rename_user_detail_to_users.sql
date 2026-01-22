-- ==========================================
-- 資料表重新命名: user_detail → users
-- ==========================================
-- 說明: 將 user_detail 表重新命名為 users，以符合 RESTful API 命名慣例
-- 執行日期: 2026-01-21
-- 影響範圍: user_detail 表、所有相關的索引和外鍵約束

-- 1. 重新命名資料表
ALTER TABLE user_detail RENAME TO users;

-- 2. 重新命名索引
ALTER INDEX idx_user_detail_account RENAME TO idx_users_account;
ALTER INDEX idx_user_detail_org RENAME TO idx_users_org;
ALTER INDEX idx_user_detail_active RENAME TO idx_users_active;

-- 3. 重新命名主鍵約束（如果需要）
-- ALTER TABLE users RENAME CONSTRAINT user_detail_pkey TO users_pkey;

-- 4. 驗證結果
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE tablename = 'users'
ORDER BY indexname;

-- 5. 顯示資料表資訊
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

COMMENT ON TABLE users IS '使用者資料表';
