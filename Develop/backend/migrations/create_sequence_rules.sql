-- ============================================================
-- 編號規則設定資料表
-- ============================================================

-- 1. 建立編號規則設定表
CREATE TABLE IF NOT EXISTS sequence_rules (
    id SERIAL PRIMARY KEY,

    -- 規則識別
    rule_code VARCHAR(50) NOT NULL UNIQUE,
    rule_name VARCHAR(200) NOT NULL,
    description TEXT,

    -- 格式設定
    prefix VARCHAR(20),
    date_format VARCHAR(20),
    sequence_length INTEGER NOT NULL DEFAULT 6,
    suffix VARCHAR(20),
    separator VARCHAR(5) DEFAULT '-',

    -- 重置機制
    reset_mode VARCHAR(20) NOT NULL DEFAULT 'never'
        CHECK (reset_mode IN ('never', 'yearly', 'monthly', 'daily')),

    -- 範例與狀態
    example VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- 組織與權限
    org_id INTEGER NOT NULL DEFAULT 1,

    -- 系統欄位
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    CONSTRAINT fk_sequence_rules_org FOREIGN KEY (org_id) REFERENCES organizations(id),
    CONSTRAINT fk_sequence_rules_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_sequence_rules_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- 2. 建立編號規則當前值表
CREATE TABLE IF NOT EXISTS sequence_values (
    id SERIAL PRIMARY KEY,

    -- 關聯規則
    rule_id INTEGER NOT NULL,

    -- 期間識別
    period VARCHAR(20) NOT NULL,

    -- 當前值
    current_value INTEGER NOT NULL DEFAULT 0,
    last_generated_at TIMESTAMP,

    -- 組織
    org_id INTEGER NOT NULL DEFAULT 1,

    -- 系統欄位
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    CONSTRAINT fk_sequence_values_rule FOREIGN KEY (rule_id) REFERENCES sequence_rules(id) ON DELETE CASCADE,
    CONSTRAINT fk_sequence_values_org FOREIGN KEY (org_id) REFERENCES organizations(id),

    -- 唯一約束
    CONSTRAINT uk_sequence_values UNIQUE (rule_id, period, org_id)
);

-- 3. 建立索引
CREATE INDEX IF NOT EXISTS idx_sequence_rules_code ON sequence_rules(rule_code);
CREATE INDEX IF NOT EXISTS idx_sequence_rules_active ON sequence_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_sequence_rules_org ON sequence_rules(org_id);

CREATE INDEX IF NOT EXISTS idx_sequence_values_rule ON sequence_values(rule_id);
CREATE INDEX IF NOT EXISTS idx_sequence_values_period ON sequence_values(period);
CREATE INDEX IF NOT EXISTS idx_sequence_values_org ON sequence_values(org_id);

-- 4. 建立註解 (使用 COMMENT ON)
COMMENT ON TABLE sequence_rules IS '編號規則設定表';
COMMENT ON TABLE sequence_values IS '編號規則當前值表';

COMMENT ON COLUMN sequence_rules.rule_code IS '規則代碼';
COMMENT ON COLUMN sequence_rules.rule_name IS '規則名稱';
COMMENT ON COLUMN sequence_rules.prefix IS '前置字串';
COMMENT ON COLUMN sequence_rules.date_format IS '日期格式 (YYYY, YYYYMM, YYYYMMDD)';
COMMENT ON COLUMN sequence_rules.sequence_length IS '流水號長度';
COMMENT ON COLUMN sequence_rules.separator IS '分隔符號';
COMMENT ON COLUMN sequence_rules.reset_mode IS '重置模式 (never, yearly, monthly, daily)';

COMMENT ON COLUMN sequence_values.period IS '期間識別 (YYYY, YYYYMM, YYYYMMDD)';
COMMENT ON COLUMN sequence_values.current_value IS '當前流水號';

-- 5. 插入測試資料
INSERT INTO sequence_rules (
    rule_code, rule_name, description,
    prefix, date_format, sequence_length, suffix, separator,
    reset_mode, example, is_active,
    org_id, created_by
) VALUES
('ORDER_NO', '訂單編號', '訂單單號產生規則',
 'ORD', 'YYYYMMDD', 6, NULL, '-',
 'daily', 'ORD-20260124-000001', true,
 1, 1),

('INVOICE_NO', '發票編號', '發票號碼產生規則',
 'INV', 'YYYYMM', 6, NULL, '-',
 'monthly', 'INV-202601-000045', true,
 1, 1),

('CONTRACT_NO', '合約編號', '合約編號產生規則',
 'CTR', 'YYYY', 6, NULL, '-',
 'yearly', 'CTR-2026-000123', true,
 1, 1),

('QUOTATION_NO', '報價單編號', '報價單號產生規則',
 'QUO', 'YYYYMMDD', 3, NULL, '',
 'daily', 'QUO20260124001', true,
 1, 1)
ON CONFLICT (rule_code) DO NOTHING;
