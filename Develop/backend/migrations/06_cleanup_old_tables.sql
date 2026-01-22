-- ==========================================
-- 清理舊版資料表（確認穩定後執行）
-- 日期: 2026-01-21
-- 警告: 執行前請確保新系統運作穩定！
-- ==========================================

-- 重要：請在系統穩定運作至少一週後再執行此腳本！

-- 1. 備份舊資料表（以防萬一）
CREATE TABLE IF NOT EXISTS user_role_backup_final AS SELECT * FROM user_role;
CREATE TABLE IF NOT EXISTS role_right_backup_final AS SELECT * FROM role_right;
CREATE TABLE IF NOT EXISTS userlogs_backup_final AS SELECT * FROM userlogs;

-- 2. 刪除舊資料表
-- 注意：由於有外鍵約束，需要先刪除依賴關係

-- 刪除 role_right（依賴 user_role 和 sysfunction）
DROP TABLE IF EXISTS role_right CASCADE;

-- 刪除 userlogs（依賴 user_detail 和 sysfunction）
DROP TABLE IF EXISTS userlogs CASCADE;

-- 刪除 user_role
DROP TABLE IF EXISTS user_role CASCADE;

-- 3. 驗證清理結果
SELECT
    tablename,
    CASE
        WHEN tablename LIKE '%_backup_final' THEN '備份表（可在確認後刪除）'
        ELSE '一般表'
    END as table_type
FROM pg_tables
WHERE schemaname = 'public'
    AND (tablename IN ('user_role', 'role_right', 'userlogs',
                       'user_role_backup_final', 'role_right_backup_final', 'userlogs_backup_final',
                       'user_roles', 'role_rights', 'user_logs'))
ORDER BY tablename;

-- 4. 清理備份表（確認無誤後，一個月後執行）
-- DROP TABLE IF EXISTS user_role_backup_final;
-- DROP TABLE IF EXISTS role_right_backup_final;
-- DROP TABLE IF EXISTS userlogs_backup_final;
