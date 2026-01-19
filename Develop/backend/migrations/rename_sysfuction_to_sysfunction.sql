-- 重新命名 sysfuction 資料表為 sysfunction
-- 執行日期: 2026-01-20

BEGIN;

-- 1. 重新命名資料表
ALTER TABLE sysfuction RENAME TO sysfunction;

-- 2. 更新索引名稱
ALTER INDEX idx_sysfuction_code RENAME TO idx_sysfunction_code;
ALTER INDEX idx_sysfuction_upper RENAME TO idx_sysfunction_upper;
ALTER INDEX idx_sysfuction_type RENAME TO idx_sysfunction_type;
ALTER INDEX idx_sysfuction_active RENAME TO idx_sysfunction_active;
ALTER INDEX idx_sysfuction_order RENAME TO idx_sysfunction_order;

-- 3. 更新序列名稱（如果存在）
ALTER SEQUENCE IF EXISTS sysfuction_id_seq RENAME TO sysfunction_id_seq;

-- 4. 注意：外鍵約束會自動跟隨表名更新，不需要手動修改

COMMIT;

-- 驗證
-- SELECT tablename FROM pg_tables WHERE tablename LIKE '%function%';
