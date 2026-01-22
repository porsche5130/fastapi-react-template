-- =====================================================
-- 資料遷移：從 sysfunction 遷移到 system_functions
-- =====================================================
-- 日期：2026-01-21
-- 說明：將舊表 sysfunction 的資料複製到新表 system_functions
-- 注意：func_module_name → module_code
-- =====================================================

-- 開始交易
BEGIN;

-- 1. 檢查兩個表是否都存在
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
    ) THEN
        RAISE EXCEPTION 'Source table sysfunction does not exist';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
    ) THEN
        RAISE EXCEPTION 'Target table system_functions does not exist';
    END IF;
END $$;

-- 2. 清空新表（如果已有資料）
TRUNCATE TABLE system_functions RESTART IDENTITY CASCADE;

-- 3. 遷移資料（欄位對應）
INSERT INTO system_functions (
    id,
    func_code,
    upper_func_id,
    func_cname,
    func_ename,
    func_type,
    func_order,
    func_icon,
    module_code,          -- 對應舊表的 func_module_name
    module_item,
    description,
    is_mana,
    is_active,
    edit_by,
    created_at,
    updated_at
)
SELECT
    id,
    func_code,
    upper_func_id,
    func_cname,
    func_ename,
    func_type,
    func_order,
    func_icon,
    func_module_name,     -- 從 func_module_name 遷移到 module_code
    module_item,
    description,
    is_mana,
    is_active,
    edit_by,
    created_at,
    updated_at
FROM sysfunction
ORDER BY id;

-- 4. 更新 sysfunction 自身的記錄
-- 將 func_code 和 module_code 從 'sysfunction' 改為 'system_functions'
UPDATE system_functions
SET
    func_code = 'system_functions',
    module_code = 'system_functions'
WHERE func_code = 'sysfunction';

-- 5. 重置序列（確保下一個 ID 正確）
SELECT setval('system_functions_id_seq', COALESCE((SELECT MAX(id) FROM system_functions), 1));

-- 6. 驗證遷移結果
DO $$
DECLARE
    old_count INTEGER;
    new_count INTEGER;
    sysfunction_record_count INTEGER;
BEGIN
    -- 檢查記錄數量
    SELECT COUNT(*) INTO old_count FROM sysfunction;
    SELECT COUNT(*) INTO new_count FROM system_functions;

    IF old_count <> new_count THEN
        RAISE EXCEPTION 'Data count mismatch! sysfunction: %, system_functions: %', old_count, new_count;
    END IF;

    -- 檢查 system_functions 自身的記錄是否已更新
    SELECT COUNT(*) INTO sysfunction_record_count
    FROM system_functions
    WHERE func_code = 'system_functions' AND module_code = 'system_functions';

    IF sysfunction_record_count = 0 THEN
        RAISE WARNING 'system_functions record not found. It may not exist in the source table.';
    ELSE
        RAISE NOTICE 'system_functions record updated successfully (func_code and module_code)';
    END IF;

    RAISE NOTICE 'Migration completed successfully! Records migrated: %', new_count;
END $$;

-- 提交交易
COMMIT;

-- =====================================================
-- 遷移完成提示
-- =====================================================
-- 資料遷移成功！
--
-- 已完成：
-- 1. 將 sysfunction 資料複製到 system_functions
-- 2. 將 func_module_name 對應到 module_code
-- 3. 更新 system_functions 記錄的 func_code 和 module_code
--
-- 下一步：
-- 1. 建立新的後端 Model/Schema/Router（使用 system_functions）
-- 2. 更新前端程式碼
-- 3. 測試新系統
-- 4. 逐步停用舊的 sysfunction 相關程式碼
-- 5. 確認無誤後執行 03_cleanup_old_sysfunction.sql
-- =====================================================
