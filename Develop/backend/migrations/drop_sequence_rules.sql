-- ============================================================
-- 刪除編號規則設定功能
-- 原因: 編號規則屬於客製化功能,每個客戶需求差異大,
--       不適合作為通用功能,應該在訪談後直接在程式碼中實現
-- ============================================================

-- 1. 先刪除 role_rights 中的相關權限
DELETE FROM role_rights
WHERE system_function_id IN (
    SELECT id FROM system_functions WHERE func_code = 'numbering_rules'
);

-- 2. 刪除 system_functions 中的編號規則功能
DELETE FROM system_functions WHERE func_code = 'numbering_rules';

-- 3. 刪除資料表 (先刪除子表,再刪除主表)
DROP TABLE IF EXISTS sequence_values CASCADE;
DROP TABLE IF EXISTS sequence_rules CASCADE;

-- 執行結果說明
DO $$
BEGIN
    RAISE NOTICE '編號規則功能已刪除:';
    RAISE NOTICE '  - system_functions 記錄已刪除';
    RAISE NOTICE '  - sequence_values 資料表已刪除';
    RAISE NOTICE '  - sequence_rules 資料表已刪除';
END $$;
