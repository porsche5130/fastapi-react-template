-- 刪除舊的 sysfunction 資料表
-- 已完全遷移到 system_functions，不再需要舊資料表

-- 檢查舊資料表是否存在，如果存在則刪除
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
    ) THEN
        DROP TABLE sysfunction CASCADE;
        RAISE NOTICE '已刪除舊資料表 sysfunction';
    ELSE
        RAISE NOTICE '舊資料表 sysfunction 不存在，無需刪除';
    END IF;
END $$;
