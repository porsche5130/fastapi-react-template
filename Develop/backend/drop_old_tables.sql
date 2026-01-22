-- 刪除舊資料表
-- Drop old tables that have been replaced with new naming conventions

-- 刪除舊的資料表
DROP TABLE IF EXISTS role_right CASCADE;
DROP TABLE IF EXISTS user_role CASCADE;
DROP TABLE IF EXISTS userlogs CASCADE;

-- 確認刪除結果
SELECT 'Tables dropped successfully' AS status;
