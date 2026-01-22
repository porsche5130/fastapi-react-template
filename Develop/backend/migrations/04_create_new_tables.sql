-- ==========================================
-- 建立新版資料表
-- 日期: 2026-01-21
-- 說明: 使用「先建後拆」策略建立新版資料表
-- ==========================================

-- 1. 建立 user_logs 資料表
CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    system_function_id INTEGER NOT NULL REFERENCES system_functions(id),
    module_item VARCHAR(50) NOT NULL CHECK (module_item IN ('Create', 'Read', 'Update', 'Delete', 'Print', 'File', 'Login')),
    data_id INTEGER,
    session_id VARCHAR(36),
    look_data JSONB NOT NULL DEFAULT '{}',
    change_data JSONB NOT NULL DEFAULT '{}',
    action_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    err_detail VARCHAR(2000)
);

-- 建立 user_logs 索引
CREATE INDEX IF NOT EXISTS idx_user_logs_user ON user_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_logs_function ON user_logs(system_function_id);
CREATE INDEX IF NOT EXISTS idx_user_logs_action_at ON user_logs(action_at);
CREATE INDEX IF NOT EXISTS idx_user_logs_module ON user_logs(module_item);
CREATE INDEX IF NOT EXISTS idx_user_logs_session ON user_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_user_logs_data_id ON user_logs(data_id);

-- 2. 建立 user_roles 資料表
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    role_cname VARCHAR(200) NOT NULL,
    role_ename VARCHAR(200) NOT NULL,
    description TEXT,
    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 建立 user_roles 索引
CREATE INDEX IF NOT EXISTS idx_user_roles_active ON user_roles(is_active);

-- 3. 建立 role_rights 資料表
CREATE TABLE IF NOT EXISTS role_rights (
    id SERIAL PRIMARY KEY,
    user_role_id INTEGER NOT NULL REFERENCES user_roles(id) ON DELETE CASCADE,
    system_function_id INTEGER NOT NULL REFERENCES system_functions(id) ON DELETE CASCADE,
    func_code VARCHAR(20) NOT NULL,
    is_create BOOLEAN NOT NULL DEFAULT FALSE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_update BOOLEAN NOT NULL DEFAULT FALSE,
    is_delete BOOLEAN NOT NULL DEFAULT FALSE,
    is_print BOOLEAN NOT NULL DEFAULT FALSE,
    is_file BOOLEAN NOT NULL DEFAULT FALSE,
    edit_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 建立 role_rights 索引
CREATE INDEX IF NOT EXISTS idx_role_rights_role ON role_rights(user_role_id);
CREATE INDEX IF NOT EXISTS idx_role_rights_function ON role_rights(system_function_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_role_rights_unique ON role_rights(user_role_id, system_function_id);

-- 驗證結果
SELECT 'user_logs' as table_name, COUNT(*) as record_count FROM user_logs
UNION ALL
SELECT 'user_roles' as table_name, COUNT(*) as record_count FROM user_roles
UNION ALL
SELECT 'role_rights' as table_name, COUNT(*) as record_count FROM role_rights;
