-- =====================================================
-- 資料庫遷移腳本：將 func_module_name 改名為 module_code
-- =====================================================
-- 日期：2026-01-21
-- 說明：將 sysfunction 資料表中的 func_module_name 欄位改名為 module_code
--
-- 設計變更說明：
-- - func_code：功能代碼，用於權限、前端路由、日誌
-- - module_code（舊名 func_module_name）：模組代碼，用於 API 路由、模組物件識別
-- - module_code 可以對應單一或多個資料表
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
        AND column_name = 'func_module_name'
    ) THEN
        RAISE EXCEPTION 'Column func_module_name does not exist in table sysfunction';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'module_code'
    ) THEN
        RAISE EXCEPTION 'Column module_code already exists in table sysfunction';
    END IF;
END $$;

-- 2. 備份原始資料（建立備份表）
DROP TABLE IF EXISTS sysfunction_backup_20260121;
CREATE TABLE sysfunction_backup_20260121 AS
SELECT * FROM sysfunction;

-- 3. 重新命名欄位
ALTER TABLE sysfunction
RENAME COLUMN func_module_name TO module_code;

-- 4. 更新欄位註解（如果有的話）
COMMENT ON COLUMN sysfunction.module_code IS '模組代碼，用於 API 路由和模組物件識別，可對應單一或多個資料表';

-- 5. 檢查是否有索引需要重新命名
DO $$
DECLARE
    idx_name TEXT;
BEGIN
    -- 查找包含 func_module_name 的索引
    FOR idx_name IN
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'sysfunction'
        AND indexdef LIKE '%func_module_name%'
    LOOP
        -- 重新命名索引（如果有的話）
        EXECUTE format('ALTER INDEX %I RENAME TO %I',
            idx_name,
            REPLACE(idx_name, 'func_module_name', 'module_code')
        );
        RAISE NOTICE 'Renamed index: % to %',
            idx_name,
            REPLACE(idx_name, 'func_module_name', 'module_code');
    END LOOP;
END $$;

-- 6. 驗證遷移結果
DO $$
DECLARE
    old_count INTEGER;
    new_count INTEGER;
BEGIN
    -- 檢查備份表的記錄數
    SELECT COUNT(*) INTO old_count FROM sysfunction_backup_20260121;

    -- 檢查當前表的記錄數
    SELECT COUNT(*) INTO new_count FROM sysfunction;

    IF old_count <> new_count THEN
        RAISE EXCEPTION 'Data count mismatch! Backup: %, Current: %', old_count, new_count;
    END IF;

    -- 檢查新欄位是否存在
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'module_code'
    ) THEN
        RAISE EXCEPTION 'Column module_code was not created successfully';
    END IF;

    -- 檢查舊欄位是否已刪除
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
        AND column_name = 'func_module_name'
    ) THEN
        RAISE EXCEPTION 'Old column func_module_name still exists';
    END IF;

    RAISE NOTICE 'Migration validation passed! Records in backup: %, Records in current: %', old_count, new_count;
END $$;

-- 提交交易
COMMIT;

-- =====================================================
-- 遷移完成提示
-- =====================================================
-- 遷移成功！
--
-- 後續步驟：
-- 1. 更新後端程式碼（Models, Schemas, Routers, Services）
-- 2. 更新前端程式碼（Types, Services, Components）
-- 3. 測試所有功能是否正常運作
-- 4. 確認無誤後，可以刪除備份表：
--    DROP TABLE sysfunction_backup_20260121;
-- =====================================================
