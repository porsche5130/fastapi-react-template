-- =====================================================
-- 回滾腳本：將 module_code 還原為 func_module_name
-- =====================================================
-- 日期：2026-01-21
-- 說明：如果需要回滾遷移，使用此腳本將 module_code 改回 func_module_name
-- 警告：僅在確認需要回滾時才執行此腳本
-- =====================================================

-- 開始交易
BEGIN;

-- 1. 檢查欄位是否存在
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'module_code'
    ) THEN
        RAISE EXCEPTION 'Column module_code does not exist in table sysfunction';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'func_module_name'
    ) THEN
        RAISE EXCEPTION 'Column func_module_name already exists in table sysfunction';
    END IF;
END $$;

-- 2. 重新命名欄位（回滾）
ALTER TABLE sysfunction
RENAME COLUMN module_code TO func_module_name;

-- 3. 更新欄位註解（回滾）
COMMENT ON COLUMN sysfunction.func_module_name IS '功能模組名稱';

-- 4. 重新命名索引（如果有的話）
DO $$
DECLARE
    idx_name TEXT;
BEGIN
    FOR idx_name IN
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'sysfunction'
        AND indexdef LIKE '%module_code%'
    LOOP
        EXECUTE format('ALTER INDEX %I RENAME TO %I',
            idx_name,
            REPLACE(idx_name, 'module_code', 'func_module_name')
        );
        RAISE NOTICE 'Renamed index back: % to %',
            idx_name,
            REPLACE(idx_name, 'module_code', 'func_module_name');
    END LOOP;
END $$;

-- 5. 驗證回滾結果
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'func_module_name'
    ) THEN
        RAISE EXCEPTION 'Rollback failed: Column func_module_name was not restored';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'module_code'
    ) THEN
        RAISE EXCEPTION 'Rollback failed: Column module_code still exists';
    END IF;

    RAISE NOTICE 'Rollback validation passed!';
END $$;

-- 提交交易
COMMIT;

-- =====================================================
-- 回滾完成提示
-- =====================================================
-- 回滾成功！
--
-- 欄位已還原為 func_module_name
-- 請記得還原所有相關的程式碼變更
-- =====================================================
