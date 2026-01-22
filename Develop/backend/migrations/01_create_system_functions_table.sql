-- =====================================================
-- 建立新表：system_functions
-- =====================================================
-- 日期：2026-01-21
-- 說明：建立新的 system_functions 表（正名化版本）
-- 策略：先建後拆 - 先建立新表，保留舊表 sysfunction
-- =====================================================

-- 開始交易
BEGIN;

-- 1. 檢查新表是否已存在
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
    ) THEN
        RAISE EXCEPTION 'Table system_functions already exists';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'sysfunction'
    ) THEN
        RAISE EXCEPTION 'Source table sysfunction does not exist';
    END IF;
END $$;

-- 2. 建立新表 system_functions（使用新的欄位名稱）
CREATE TABLE system_functions (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 功能資訊
    func_code VARCHAR(200) NOT NULL,
    upper_func_id INTEGER NOT NULL DEFAULT 0,
    func_cname VARCHAR(200) NOT NULL,
    func_ename VARCHAR(200) NOT NULL,
    func_type INTEGER NOT NULL,  -- 1:節點, 2:功能
    func_order INTEGER NOT NULL,
    func_icon VARCHAR(200),

    -- 模組資訊（新欄位名稱）
    module_code VARCHAR(200),  -- 原 func_module_name
    module_item JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- 說明與狀態
    description TEXT,
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- 系統欄位
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 約束
    CONSTRAINT chk_system_functions_type CHECK (func_type IN (1, 2)),
    CONSTRAINT chk_system_functions_module CHECK (
        (func_type = 1 AND module_code IS NULL) OR
        (func_type = 2 AND module_code IS NOT NULL)
    )
);

-- 3. 建立索引
CREATE INDEX idx_system_functions_code ON system_functions(func_code);
CREATE INDEX idx_system_functions_upper ON system_functions(upper_func_id);
CREATE INDEX idx_system_functions_type ON system_functions(func_type);
CREATE INDEX idx_system_functions_active ON system_functions(is_active);
CREATE INDEX idx_system_functions_order ON system_functions(func_order);
CREATE INDEX idx_system_functions_module ON system_functions(module_code);

-- 4. 建立外鍵（假設 user_detail 表存在）
ALTER TABLE system_functions
ADD CONSTRAINT fk_system_functions_editor
FOREIGN KEY (edit_by) REFERENCES user_detail(id);

-- 5. 加入註解
COMMENT ON TABLE system_functions IS '系統功能設定表（正名化版本）';
COMMENT ON COLUMN system_functions.id IS '功能ID';
COMMENT ON COLUMN system_functions.func_code IS '功能代碼，用於權限識別、前端路由、日誌記錄';
COMMENT ON COLUMN system_functions.upper_func_id IS '上層功能ID（0表示根節點）';
COMMENT ON COLUMN system_functions.func_cname IS '功能中文名稱';
COMMENT ON COLUMN system_functions.func_ename IS '功能英文名稱';
COMMENT ON COLUMN system_functions.func_type IS '功能類型（1:節點/選單, 2:功能）';
COMMENT ON COLUMN system_functions.func_order IS '排序順序';
COMMENT ON COLUMN system_functions.func_icon IS '圖示';
COMMENT ON COLUMN system_functions.module_code IS '模組代碼，用於 API 路由識別，可對應單一或多個資料表';
COMMENT ON COLUMN system_functions.module_item IS '可設定權限項目 (create/read/update/delete/print/file)';
COMMENT ON COLUMN system_functions.description IS '功能說明';
COMMENT ON COLUMN system_functions.is_mana IS '是否為管理功能';
COMMENT ON COLUMN system_functions.is_active IS '是否啟用';
COMMENT ON COLUMN system_functions.edit_by IS '最後編輯者ID';
COMMENT ON COLUMN system_functions.created_at IS '建立時間';
COMMENT ON COLUMN system_functions.updated_at IS '更新時間';

-- 6. 驗證表建立成功
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
    ) THEN
        RAISE EXCEPTION 'Failed to create table system_functions';
    END IF;

    -- 檢查 module_code 欄位是否存在
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'system_functions'
        AND column_name = 'module_code'
    ) THEN
        RAISE EXCEPTION 'Column module_code was not created';
    END IF;

    RAISE NOTICE 'Table system_functions created successfully with module_code column';
END $$;

-- 提交交易
COMMIT;

-- =====================================================
-- 建立完成提示
-- =====================================================
-- 新表 system_functions 建立成功！
--
-- 下一步：
-- 1. 執行資料遷移腳本（02_migrate_data_to_system_functions.sql）
-- 2. 更新後端程式碼以支援新表
-- 3. 測試新表功能
-- 4. 逐步停用舊表 sysfunction
-- 5. 確認無誤後刪除舊表
-- =====================================================
