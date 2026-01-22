-- 移除 user_logs 表的 system_function_id 外鍵約束
-- 日誌記錄應該保留歷史事實,不應該被功能刪除所限制

-- 移除外鍵約束
ALTER TABLE user_logs
DROP CONSTRAINT IF EXISTS user_logs_system_function_id_fkey;

-- 驗證約束已移除
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table
FROM pg_constraint
WHERE conrelid = 'user_logs'::regclass
  AND contype = 'f'
  AND conname = 'user_logs_system_function_id_fkey';
