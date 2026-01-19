-- PA6.4 系統管理後台資料庫初始化腳本
-- 專案：Paris Agreement Article 6.4 管理系統
-- 版本：1.1.0
-- 日期：2026-01-18
-- 說明：處理外鍵循環依賴問題

-- ============================================
-- 步驟 1: 建立不含外鍵的表格結構
-- ============================================

-- 1.1 組織單位明細檔 (organizations) - 暫時不加 edit_by 外鍵
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    org_code VARCHAR(200) UNIQUE NOT NULL,
    org_name VARCHAR(200) NOT NULL,
    org_type INTEGER NOT NULL CHECK (org_type IN (1, 2, 3)),
    contact_person VARCHAR(200) NOT NULL,
    contact_email VARCHAR(200) NOT NULL,
    contact_phone VARCHAR(200) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(200),
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    memo VARCHAR(1000),
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_organizations_code ON organizations(org_code);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_organizations_mana ON organizations(is_mana);

COMMENT ON TABLE organizations IS '組織單位明細檔';

-- 1.2 使用者角色明細檔 (user_role) - 暫時不加 edit_by 外鍵
CREATE TABLE IF NOT EXISTS user_role (
    id SERIAL PRIMARY KEY,
    role_cname VARCHAR(200) NOT NULL,
    role_ename VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_role_active ON user_role(is_active);

COMMENT ON TABLE user_role IS '使用者角色明細檔';

-- 1.3 使用者明細檔 (user_detail) - 暫時不加外鍵
CREATE TABLE IF NOT EXISTS user_detail (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    account VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    job_title VARCHAR(200),
    phone VARCHAR(200),
    user_role JSONB NOT NULL DEFAULT '[]',
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_detail_account ON user_detail(account);
CREATE INDEX IF NOT EXISTS idx_user_detail_org ON user_detail(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_detail_active ON user_detail(is_active);

COMMENT ON TABLE user_detail IS '使用者明細檔';
COMMENT ON COLUMN user_detail.password IS '使用者密碼 (bcrypt hash)';

-- 1.4 系統功能明細檔 (sysfuction) - 暫時不加外鍵
CREATE TABLE IF NOT EXISTS sysfuction (
    id SERIAL PRIMARY KEY,
    func_code VARCHAR(200) NOT NULL,
    upper_func_id INTEGER NOT NULL DEFAULT 0,
    func_cname VARCHAR(200) NOT NULL,
    func_ename VARCHAR(200) NOT NULL,
    func_type INTEGER NOT NULL CHECK (func_type IN (1, 2)),
    func_order INTEGER NOT NULL,
    func_icon VARCHAR(200),
    func_module_name VARCHAR(200),
    module_item JSONB NOT NULL DEFAULT '[]',
    description TEXT,
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT chk_func_module CHECK (
        (func_type = 1 AND func_module_name IS NULL) OR
        (func_type = 2 AND func_module_name IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_sysfuction_code ON sysfuction(func_code);
CREATE INDEX IF NOT EXISTS idx_sysfuction_upper ON sysfuction(upper_func_id);
CREATE INDEX IF NOT EXISTS idx_sysfuction_type ON sysfuction(func_type);
CREATE INDEX IF NOT EXISTS idx_sysfuction_active ON sysfuction(is_active);
CREATE INDEX IF NOT EXISTS idx_sysfuction_order ON sysfuction(func_order);

COMMENT ON TABLE sysfuction IS '系統功能明細檔';

-- 1.5 系統設定檔 (sys_profile) - 暫時不加外鍵
CREATE TABLE IF NOT EXISTS sys_profile (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    is_service BOOLEAN NOT NULL DEFAULT TRUE,
    sys_url VARCHAR(200) NOT NULL,
    sys_ctitle VARCHAR(200) NOT NULL,
    sys_etitle VARCHAR(200) NOT NULL,
    sys_ccopyright VARCHAR(200) NOT NULL,
    sys_ecopyright VARCHAR(200) NOT NULL,
    sys_organization INTEGER NOT NULL DEFAULT 1,
    sys_mana_email VARCHAR(200) NOT NULL,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

COMMENT ON TABLE sys_profile IS '系統設定檔 (唯一一筆)';

-- 1.6 作業紀錄表 (userlogs) - 暫時不加外鍵
CREATE TABLE IF NOT EXISTS userlogs (
    id SERIAL PRIMARY KEY,
    user_detail_id INTEGER NOT NULL,
    sysfuction_id INTEGER NOT NULL,
    module_item VARCHAR(50) NOT NULL CHECK (module_item IN ('Create', 'Read', 'Update', 'Delete', 'Print', 'File')),
    look_data JSONB NOT NULL DEFAULT '{}',
    change_data JSONB NOT NULL DEFAULT '{}',
    action_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    err_detail VARCHAR(2000)
);

CREATE INDEX IF NOT EXISTS idx_userlogs_user ON userlogs(user_detail_id);
CREATE INDEX IF NOT EXISTS idx_userlogs_function ON userlogs(sysfuction_id);
CREATE INDEX IF NOT EXISTS idx_userlogs_action_at ON userlogs(action_at);
CREATE INDEX IF NOT EXISTS idx_userlogs_module ON userlogs(module_item);

COMMENT ON TABLE userlogs IS '作業紀錄表';

-- ============================================
-- 步驟 2: 插入初始資料
-- ============================================

-- 2.1 插入系統管理公司 (edit_by=1 會在稍後建立使用者時存在)
INSERT INTO organizations (
    id, org_code, org_name, org_type,
    contact_person, contact_email, contact_phone,
    address, phone, is_mana, is_active, memo, edit_by, created_at, updated_at
) VALUES (
    1, '82871784', '匠耘有限公司', 2,
    '陳琦', 'porsche@lab.taipei', '0910326333',
    '', '', TRUE, TRUE, '', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- 2.2 插入預設角色
INSERT INTO user_role (
    id, role_cname, role_ename, description, is_active, edit_by, created_at, updated_at
) VALUES (
    1, '系統管理員', 'System Administrator', '擁有所有系統權限', TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- 2.3 插入系統管理員帳號 (密碼: admin123, bcrypt hash)
-- 注意：實際部署時應改為更安全的密碼
INSERT INTO user_detail (
    id, organization_id, account, username, password,
    department, job_title, phone, user_role,
    is_active, edit_by, created_at, updated_at
) VALUES (
    1, 1, 'admin', '系統管理員', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eDWpNvF/jW5m',
    '資訊部', '系統管理員', '0910326333', '[1]',
    TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- 2.4 插入系統功能選單
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

-- 2.5 插入初始系統設定
INSERT INTO sys_profile (
    id, is_service, sys_url, sys_ctitle, sys_etitle, sys_ccopyright, sys_ecopyright,
    sys_organization, sys_mana_email, edit_by, created_at, updated_at
) VALUES (
    1, TRUE, 'http://localhost:10180',
    'Paris Agreement Article 6.4 管理系統',
    'Paris Agreement Article 6.4 Management System',
    'Copyright © 2026 匠耘有限公司',
    'Copyright © 2026 JiangYun Co., Ltd.',
    1, 'porsche@lab.taipei', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 步驟 3: 新增外鍵約束
-- ============================================

-- 3.1 organizations 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'organizations_edit_by_fkey'
    ) THEN
        ALTER TABLE organizations ADD CONSTRAINT organizations_edit_by_fkey
        FOREIGN KEY (edit_by) REFERENCES user_detail(id);
    END IF;
END $$;

-- 3.2 user_role 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_role_edit_by_fkey'
    ) THEN
        ALTER TABLE user_role ADD CONSTRAINT user_role_edit_by_fkey
        FOREIGN KEY (edit_by) REFERENCES user_detail(id);
    END IF;
END $$;

-- 3.3 user_detail 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_detail_organization_id_fkey'
    ) THEN
        ALTER TABLE user_detail ADD CONSTRAINT user_detail_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_detail_edit_by_fkey'
    ) THEN
        ALTER TABLE user_detail ADD CONSTRAINT user_detail_edit_by_fkey
        FOREIGN KEY (edit_by) REFERENCES user_detail(id);
    END IF;
END $$;

-- 3.4 sysfuction 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'sysfuction_edit_by_fkey'
    ) THEN
        ALTER TABLE sysfuction ADD CONSTRAINT sysfuction_edit_by_fkey
        FOREIGN KEY (edit_by) REFERENCES user_detail(id);
    END IF;
END $$;

-- 3.5 sys_profile 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'sys_profile_sys_organization_fkey'
    ) THEN
        ALTER TABLE sys_profile ADD CONSTRAINT sys_profile_sys_organization_fkey
        FOREIGN KEY (sys_organization) REFERENCES organizations(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'sys_profile_edit_by_fkey'
    ) THEN
        ALTER TABLE sys_profile ADD CONSTRAINT sys_profile_edit_by_fkey
        FOREIGN KEY (edit_by) REFERENCES user_detail(id);
    END IF;
END $$;

-- 3.6 userlogs 外鍵
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'userlogs_user_detail_id_fkey'
    ) THEN
        ALTER TABLE userlogs ADD CONSTRAINT userlogs_user_detail_id_fkey
        FOREIGN KEY (user_detail_id) REFERENCES user_detail(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'userlogs_sysfuction_id_fkey'
    ) THEN
        ALTER TABLE userlogs ADD CONSTRAINT userlogs_sysfuction_id_fkey
        FOREIGN KEY (sysfuction_id) REFERENCES sysfuction(id);
    END IF;
END $$;

-- ============================================
-- 完成
-- ============================================

-- 重設序列編號
SELECT setval('organizations_id_seq', (SELECT MAX(id) FROM organizations));
SELECT setval('user_role_id_seq', (SELECT MAX(id) FROM user_role));
SELECT setval('user_detail_id_seq', (SELECT MAX(id) FROM user_detail));
SELECT setval('sysfuction_id_seq', (SELECT MAX(id) FROM sysfuction));
