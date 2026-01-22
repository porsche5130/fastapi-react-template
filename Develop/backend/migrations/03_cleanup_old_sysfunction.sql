-- =====================================================
-- 清理舊表：移除 sysfunction 表
-- =====================================================
-- 日期：2026-01-21
-- 說明：確認新系統穩定後，移除舊的 sysfunction 表
-- 警告：執行前請確保：
--   1. 新的 system_functions 表運作正常
--   2. 所有程式碼已改為使用 system_functions
--   3. 已完整測試所有功能
--   4. 已備份資料庫
-- =====================================================

-- 開始交易
BEGIN;

-- 1. 安全檢查
DO $$
DECLARE
    old_count INTEGER;
    new_count INTEGER;
BEGIN
    -- 檢查新表是否存在
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
    ) THEN
        RAISE EXCEPTION 'New table system_functions does not exist. Cannot proceed with cleanup.';
    END IF;

    -- 檢查舊表是否存在
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
    ) THEN
        RAISE EXCEPTION 'Old table sysfunction does not exist. Already cleaned up?';
    END IF;

    -- 檢查資料數量
    SELECT COUNT(*) INTO old_count FROM sysfunction;
    SELECT COUNT(*) INTO new_count FROM system_functions;

    IF new_count = 0 THEN
        RAISE EXCEPTION 'New table system_functions is empty. Cannot proceed with cleanup.';
    END IF;

    RAISE NOTICE 'Pre-cleanup check passed. Old records: %, New records: %', old_count, new_count;
END $$;

-- 2. 最後備份（建立備份表）
DROP TABLE IF EXISTS sysfunction_backup_final;
CREATE TABLE sysfunction_backup_final AS
SELECT * FROM sysfunction;

RAISE NOTICE 'Final backup created: sysfunction_backup_final';

-- 3. 檢查是否有其他表引用 sysfunction
DO $$
DECLARE
    fk_record RECORD;
    has_references BOOLEAN := FALSE;
BEGIN
    FOR fk_record IN
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND ccu.table_name = 'sysfunction'
        AND tc.table_schema = 'public'
    LOOP
        has_references := TRUE;
        RAISE WARNING 'Foreign key reference found: %.% references sysfunction.%',
            fk_record.table_name,
            fk_record.column_name,
            fk_record.foreign_column_name;
    END LOOP;

    IF has_references THEN
        RAISE EXCEPTION 'Cannot drop sysfunction: foreign key references exist. Please update or remove these references first.';
    END IF;
END $$;

-- 4. 刪除舊表
DROP TABLE IF EXISTS sysfunction CASCADE;

RAISE NOTICE 'Old table sysfunction has been dropped';

-- 5. 驗證清理結果
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
    ) THEN
        RAISE EXCEPTION 'Failed to drop table sysfunction';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
    ) THEN
        RAISE EXCEPTION 'New table system_functions does not exist after cleanup';
    END IF;

    RAISE NOTICE 'Cleanup validation passed!';
END $$;

-- 提交交易
COMMIT;

-- =====================================================
-- 清理完成提示
-- =====================================================
-- 舊表 sysfunction 已成功移除！
--
-- 已完成：
-- 1. 建立最後備份表：sysfunction_backup_final
-- 2. 檢查外鍵引用
-- 3. 刪除舊表 sysfunction
-- 4. 驗證新表 system_functions 存在
--
-- 備份表保留：
-- - sysfunction_backup_final
--
-- 如需還原，請使用：
-- CREATE TABLE sysfunction AS SELECT * FROM sysfunction_backup_final;
--
-- 確認系統穩定運作一段時間後，可刪除備份表：
-- DROP TABLE sysfunction_backup_final;
-- DROP TABLE sysfunction_backup_20260121; (如果還存在)
-- =====================================================
