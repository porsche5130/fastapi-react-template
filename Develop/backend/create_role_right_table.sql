-- ============================================
-- 角色權限設定檔 (role_right)
-- 功能: 角色權限設定作業 (Role_Right)
-- 版本: 1.0.0
-- 日期: 2026-01-19
-- ============================================

-- 建立資料表
CREATE TABLE IF NOT EXISTS role_right (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 關聯欄位
    user_role_id INTEGER NOT NULL,
    sysfuction_id INTEGER NOT NULL,
    func_code VARCHAR(20) NOT NULL,

    -- 權限設定
    is_create BOOLEAN NOT NULL DEFAULT FALSE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_update BOOLEAN NOT NULL DEFAULT FALSE,
    is_delete BOOLEAN NOT NULL DEFAULT FALSE,
    is_print BOOLEAN NOT NULL DEFAULT FALSE,
    is_file BOOLEAN NOT NULL DEFAULT FALSE,

    -- 系統欄位
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵約束
    FOREIGN KEY (user_role_id) REFERENCES user_role(id) ON DELETE CASCADE,
    FOREIGN KEY (sysfuction_id) REFERENCES sysfuction(id) ON DELETE CASCADE,
    FOREIGN KEY (edit_by) REFERENCES user_detail(id)
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_role_right_role ON role_right(user_role_id);
CREATE INDEX IF NOT EXISTS idx_role_right_function ON role_right(sysfuction_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_role_right_unique ON role_right(user_role_id, sysfuction_id);

-- 註解
COMMENT ON TABLE role_right IS '角色權限設定檔';
COMMENT ON COLUMN role_right.id IS '資料序號 (自動編號)';
COMMENT ON COLUMN role_right.user_role_id IS '角色編號';
COMMENT ON COLUMN role_right.sysfuction_id IS '功能編號';
COMMENT ON COLUMN role_right.func_code IS '細部功能代碼';
COMMENT ON COLUMN role_right.is_create IS '新增權限 (預設: false)';
COMMENT ON COLUMN role_right.is_read IS '讀取權限 (預設: false)';
COMMENT ON COLUMN role_right.is_update IS '修改權限 (預設: false)';
COMMENT ON COLUMN role_right.is_delete IS '刪除權限 (預設: false)';
COMMENT ON COLUMN role_right.is_print IS '列印權限 (預設: false)';
COMMENT ON COLUMN role_right.is_file IS '檔案權限 (預設: false)';
COMMENT ON COLUMN role_right.edit_by IS '編輯者';
COMMENT ON COLUMN role_right.created_at IS '資料建立時間';
COMMENT ON COLUMN role_right.updated_at IS '資料修改時間';

-- 完成
SELECT 'role_right 資料表建立完成' AS message;
