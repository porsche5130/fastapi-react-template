-- PA6.4 系統管理後台資料庫初始化腳本
-- 專案：Paris Agreement Article 6.4 管理系統
-- 版本：1.0.0
-- 日期：2026-01-18

-- ============================================
-- 1. 組織單位明細檔 (organizations)
-- ============================================

CREATE TABLE IF NOT EXISTS organizations (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 組織資訊
    org_code VARCHAR(200) UNIQUE NOT NULL,
    org_name VARCHAR(200) NOT NULL,
    org_type INTEGER NOT NULL CHECK (org_type IN (1, 2, 3)),

    -- 聯絡資訊
    contact_person VARCHAR(200) NOT NULL,
    contact_email VARCHAR(200) NOT NULL,
    contact_phone VARCHAR(200) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(200),

    -- 系統欄位
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    memo VARCHAR(1000),
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_organizations_code ON organizations(org_code);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_organizations_mana ON organizations(is_mana);

-- 註解
COMMENT ON TABLE organizations IS '組織單位明細檔';
COMMENT ON COLUMN organizations.id IS '資料編號';
COMMENT ON COLUMN organizations.org_code IS '組織統編/代碼';
COMMENT ON COLUMN organizations.org_name IS '組織名稱';
COMMENT ON COLUMN organizations.org_type IS '組織型態 (1:政府機關, 2:公司行號, 3:個人)';
COMMENT ON COLUMN organizations.contact_person IS '連絡人';
COMMENT ON COLUMN organizations.contact_email IS '連絡人郵件';
COMMENT ON COLUMN organizations.contact_phone IS '連絡人電話';
COMMENT ON COLUMN organizations.address IS '組織地址';
COMMENT ON COLUMN organizations.phone IS '組織代表號';
COMMENT ON COLUMN organizations.is_mana IS '系統管理公司 (只有一家可設為 TRUE)';
COMMENT ON COLUMN organizations.is_active IS '啟用';
COMMENT ON COLUMN organizations.memo IS '備註';
COMMENT ON COLUMN organizations.edit_by IS '編輯者';
COMMENT ON COLUMN organizations.created_at IS '建立時間';
COMMENT ON COLUMN organizations.updated_at IS '修改時間';

-- 預設資料 (系統管理公司)
INSERT INTO organizations (
    id, org_code, org_name, org_type,
    contact_person, contact_email, contact_phone,
    address, phone, is_mana, is_active, memo, edit_by, created_at, updated_at
) VALUES (
    1, '82871784', '匠耘有限公司', 2,
    '陳琦', 'porsche@lab.taipei', '0910326333',
    '', '', TRUE, TRUE, '', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. 使用者角色明細檔 (user_role)
-- ============================================

CREATE TABLE IF NOT EXISTS user_role (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 角色資訊
    role_cname VARCHAR(200) NOT NULL,
    role_ename VARCHAR(200) NOT NULL,
    description TEXT,

    -- 系統欄位
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_user_role_active ON user_role(is_active);

-- 註解
COMMENT ON TABLE user_role IS '使用者角色明細檔';
COMMENT ON COLUMN user_role.id IS '資料編號';
COMMENT ON COLUMN user_role.role_cname IS '中文名稱';
COMMENT ON COLUMN user_role.role_ename IS '英文名稱';
COMMENT ON COLUMN user_role.description IS '說明 (富文本格式)';
COMMENT ON COLUMN user_role.is_active IS '啟用';
COMMENT ON COLUMN user_role.edit_by IS '編輯者';
COMMENT ON COLUMN user_role.created_at IS '建立時間';
COMMENT ON COLUMN user_role.updated_at IS '修改時間';

-- ============================================
-- 3. 使用者明細檔 (user_detail)
-- ============================================

CREATE TABLE IF NOT EXISTS user_detail (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 組織與帳號
    organization_id INTEGER NOT NULL,
    account VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,

    -- 職務資訊
    department VARCHAR(200),
    job_title VARCHAR(200),
    phone VARCHAR(200),

    -- 角色權限
    user_role JSONB NOT NULL DEFAULT '[]',

    -- 登入資訊
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(100),

    -- 系統欄位
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (edit_by) REFERENCES user_detail(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_user_detail_account ON user_detail(account);
CREATE INDEX IF NOT EXISTS idx_user_detail_org ON user_detail(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_detail_active ON user_detail(is_active);

-- 註解
COMMENT ON TABLE user_detail IS '使用者明細檔';
COMMENT ON COLUMN user_detail.id IS '資料編號';
COMMENT ON COLUMN user_detail.organization_id IS '組織編號';
COMMENT ON COLUMN user_detail.account IS '登入帳號';
COMMENT ON COLUMN user_detail.username IS '使用者名稱';
COMMENT ON COLUMN user_detail.password IS '使用者密碼 (bcrypt hash)';
COMMENT ON COLUMN user_detail.department IS '所屬部門';
COMMENT ON COLUMN user_detail.job_title IS '職稱';
COMMENT ON COLUMN user_detail.phone IS '連絡電話';
COMMENT ON COLUMN user_detail.user_role IS '所屬角色 JSON 陣列 [user_role.id]';
COMMENT ON COLUMN user_detail.last_login_at IS '最後登入時間';
COMMENT ON COLUMN user_detail.last_login_ip IS '最後登入IP';
COMMENT ON COLUMN user_detail.is_active IS '啟用';
COMMENT ON COLUMN user_detail.edit_by IS '編輯者';
COMMENT ON COLUMN user_detail.created_at IS '建立時間';
COMMENT ON COLUMN user_detail.updated_at IS '修改時間';

-- ============================================
-- 4. 系統功能明細檔 (sysfuction)
-- ============================================

CREATE TABLE IF NOT EXISTS sysfuction (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 功能資訊
    func_code VARCHAR(200) NOT NULL,
    upper_func_id INTEGER NOT NULL DEFAULT 0,
    func_cname VARCHAR(200) NOT NULL,
    func_ename VARCHAR(200) NOT NULL,
    func_type INTEGER NOT NULL CHECK (func_type IN (1, 2)),
    func_order INTEGER NOT NULL,
    func_icon VARCHAR(200),

    -- 模組資訊
    func_module_name VARCHAR(200),
    module_item JSONB NOT NULL DEFAULT '[]',

    -- 說明與狀態
    description TEXT,
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- 系統欄位
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    FOREIGN KEY (edit_by) REFERENCES user_detail(id),

    -- 約束
    CONSTRAINT chk_func_module CHECK (
        (func_type = 1 AND func_module_name IS NULL) OR
        (func_type = 2 AND func_module_name IS NOT NULL)
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_sysfuction_code ON sysfuction(func_code);
CREATE INDEX IF NOT EXISTS idx_sysfuction_upper ON sysfuction(upper_func_id);
CREATE INDEX IF NOT EXISTS idx_sysfuction_type ON sysfuction(func_type);
CREATE INDEX IF NOT EXISTS idx_sysfuction_active ON sysfuction(is_active);
CREATE INDEX IF NOT EXISTS idx_sysfuction_order ON sysfuction(func_order);

-- 註解
COMMENT ON TABLE sysfuction IS '系統功能明細檔';
COMMENT ON COLUMN sysfuction.id IS '資料編號';
COMMENT ON COLUMN sysfuction.func_code IS '功能代碼';
COMMENT ON COLUMN sysfuction.upper_func_id IS '上層功能 (0為根節點)';
COMMENT ON COLUMN sysfuction.func_cname IS '中文名稱';
COMMENT ON COLUMN sysfuction.func_ename IS '英文名稱';
COMMENT ON COLUMN sysfuction.func_type IS '功能類型 (1:節點, 2:功能)';
COMMENT ON COLUMN sysfuction.func_order IS '功能次序';
COMMENT ON COLUMN sysfuction.func_icon IS '功能圖示';
COMMENT ON COLUMN sysfuction.func_module_name IS '模組名稱';
COMMENT ON COLUMN sysfuction.module_item IS '模組項目 JSON 陣列 ["Create","Read","Update","Delete","Print","File"]';
COMMENT ON COLUMN sysfuction.description IS '說明 (富文本格式)';
COMMENT ON COLUMN sysfuction.is_mana IS '系統管理';
COMMENT ON COLUMN sysfuction.is_active IS '啟用';
COMMENT ON COLUMN sysfuction.edit_by IS '編輯者';
COMMENT ON COLUMN sysfuction.created_at IS '建立時間';
COMMENT ON COLUMN sysfuction.updated_at IS '修改時間';

-- 預設資料 (系統管理選單)
INSERT INTO sysfuction (
    id, func_code, upper_func_id, func_cname, func_ename, func_type, func_order,
    func_icon, func_module_name, module_item, description, is_mana, is_active, edit_by, created_at, updated_at
) VALUES
(1, 'system_mana', 0, '系統管理後台', 'System Management', 1, 10,
 'settings', NULL, '[]', '', TRUE, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(2, 'sys_profile', 1, '系統設定資料', 'System Profile', 2, 1010,
 'settings', 'sys_profile', '["Create","Read","Update","Delete","Print","File"]', '', TRUE, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(3, 'organizations', 1, '組織設定', 'Organizations', 2, 1020,
 'business', 'organizations', '["Create","Read","Update","Delete","Print","File"]', '', TRUE, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(4, 'user_role', 1, '使用者角色設定作業', 'User Roles', 2, 1030,
 'users', 'user_role', '["Create","Read","Update","Delete","Print","File"]', '', TRUE, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(5, 'user_detail', 1, '使用者設定作業', 'User Details', 2, 1040,
 'user', 'user_detail', '["Create","Read","Update","Delete","Print","File"]', '', TRUE, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. 系統設定檔 (sys_profile)
-- ============================================

CREATE TABLE IF NOT EXISTS sys_profile (
    -- 主鍵 (固定為 1)
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),

    -- 系統狀態
    is_service BOOLEAN NOT NULL DEFAULT TRUE,

    -- 系統資訊
    sys_url VARCHAR(200) NOT NULL,
    sys_ctitle VARCHAR(200) NOT NULL,
    sys_etitle VARCHAR(200) NOT NULL,
    sys_ccopyright VARCHAR(200) NOT NULL,
    sys_ecopyright VARCHAR(200) NOT NULL,

    -- 管理資訊
    sys_organization INTEGER NOT NULL DEFAULT 1,
    sys_mana_email VARCHAR(200) NOT NULL,

    -- 系統欄位
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    FOREIGN KEY (sys_organization) REFERENCES organizations(id),
    FOREIGN KEY (edit_by) REFERENCES user_detail(id)
);

-- 註解
COMMENT ON TABLE sys_profile IS '系統設定檔 (唯一一筆)';
COMMENT ON COLUMN sys_profile.id IS '資料編號 (固定為 1)';
COMMENT ON COLUMN sys_profile.is_service IS '系統狀態 (1:正常, 0:維護)';
COMMENT ON COLUMN sys_profile.sys_url IS '系統網址';
COMMENT ON COLUMN sys_profile.sys_ctitle IS '系統中文標題';
COMMENT ON COLUMN sys_profile.sys_etitle IS '系統英文標題';
COMMENT ON COLUMN sys_profile.sys_ccopyright IS '系統中文版權宣告';
COMMENT ON COLUMN sys_profile.sys_ecopyright IS '系統英文版權宣告';
COMMENT ON COLUMN sys_profile.sys_organization IS '系統管理公司';
COMMENT ON COLUMN sys_profile.sys_mana_email IS '系統管理員電子郵件';
COMMENT ON COLUMN sys_profile.edit_by IS '編輯者';
COMMENT ON COLUMN sys_profile.created_at IS '建立時間';
COMMENT ON COLUMN sys_profile.updated_at IS '修改時間';

-- ============================================
-- 6. 作業紀錄表 (userlogs)
-- ============================================

CREATE TABLE IF NOT EXISTS userlogs (
    -- 主鍵
    id SERIAL PRIMARY KEY,

    -- 作業資訊
    user_detail_id INTEGER NOT NULL,
    sysfuction_id INTEGER NOT NULL,
    module_item VARCHAR(50) NOT NULL CHECK (module_item IN ('Create', 'Read', 'Update', 'Delete', 'Print', 'File')),

    -- 資料記錄
    look_data JSONB NOT NULL DEFAULT '{}',
    change_data JSONB NOT NULL DEFAULT '{}',

    -- 時間與錯誤
    action_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    err_detail VARCHAR(2000),

    -- 外鍵
    FOREIGN KEY (user_detail_id) REFERENCES user_detail(id),
    FOREIGN KEY (sysfuction_id) REFERENCES sysfuction(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_userlogs_user ON userlogs(user_detail_id);
CREATE INDEX IF NOT EXISTS idx_userlogs_function ON userlogs(sysfuction_id);
CREATE INDEX IF NOT EXISTS idx_userlogs_action_at ON userlogs(action_at);
CREATE INDEX IF NOT EXISTS idx_userlogs_module ON userlogs(module_item);

-- 註解
COMMENT ON TABLE userlogs IS '作業紀錄表';
COMMENT ON COLUMN userlogs.id IS '資料編號';
COMMENT ON COLUMN userlogs.user_detail_id IS '作業人員';
COMMENT ON COLUMN userlogs.sysfuction_id IS '作業功能';
COMMENT ON COLUMN userlogs.module_item IS '模組項目 (Create/Read/Update/Delete/Print/File)';
COMMENT ON COLUMN userlogs.look_data IS '檢視資料 (JSON 格式: {欄位名稱: 資料內容})';
COMMENT ON COLUMN userlogs.change_data IS '異動資料 (JSON 格式: {欄位名稱: 資料內容})';
COMMENT ON COLUMN userlogs.action_at IS '作業時間';
COMMENT ON COLUMN userlogs.err_detail IS '異常紀錄';

-- ============================================
-- 完成
-- ============================================
