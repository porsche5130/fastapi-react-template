-- ============================================================
-- 檔案附件管理資料表
-- ============================================================

-- 1. 建立檔案附件表
CREATE TABLE IF NOT EXISTS file_attachments (
    id SERIAL PRIMARY KEY,

    -- 檔案基本資訊
    original_name VARCHAR(500) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(200) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,

    -- 分類與業務關聯
    category VARCHAR(50) NOT NULL
        CHECK (category IN ('image', 'document', 'archive', 'video', 'audio', 'other')),
    business_type VARCHAR(50),
    related_table VARCHAR(100),
    related_id INTEGER,

    -- 存取控制
    access_level VARCHAR(20) NOT NULL DEFAULT 'private'
        CHECK (access_level IN ('public', 'private', 'restricted')),
    is_public BOOLEAN NOT NULL DEFAULT false,
    allowed_roles TEXT[],
    allowed_users INTEGER[],

    -- 檔案狀態
    is_temp BOOLEAN NOT NULL DEFAULT true,
    confirmed_at TIMESTAMP,
    download_count INTEGER NOT NULL DEFAULT 0,
    last_downloaded_at TIMESTAMP,

    -- 版本控制
    version INTEGER NOT NULL DEFAULT 1,
    previous_version_id INTEGER,

    -- 附加資訊
    thumbnail_path VARCHAR(1000),
    metadata JSONB,
    description TEXT,
    tags TEXT[],

    -- 有效期限
    expires_at TIMESTAMP,

    -- 組織與使用者
    org_id INTEGER NOT NULL DEFAULT 1,
    uploaded_by INTEGER NOT NULL,

    -- 系統欄位
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    CONSTRAINT fk_file_attachments_org FOREIGN KEY (org_id) REFERENCES organizations(id),
    CONSTRAINT fk_file_attachments_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES users(id),
    CONSTRAINT fk_file_attachments_previous FOREIGN KEY (previous_version_id) REFERENCES file_attachments(id) ON DELETE SET NULL
);

-- 2. 建立索引
CREATE INDEX IF NOT EXISTS idx_file_attachments_hash ON file_attachments(file_hash);
CREATE INDEX IF NOT EXISTS idx_file_attachments_category ON file_attachments(category);
CREATE INDEX IF NOT EXISTS idx_file_attachments_business ON file_attachments(business_type, related_id);
CREATE INDEX IF NOT EXISTS idx_file_attachments_uploader ON file_attachments(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_file_attachments_org ON file_attachments(org_id);
CREATE INDEX IF NOT EXISTS idx_file_attachments_temp ON file_attachments(is_temp, created_at);
CREATE INDEX IF NOT EXISTS idx_file_attachments_access ON file_attachments(access_level);
CREATE INDEX IF NOT EXISTS idx_file_attachments_expires ON file_attachments(expires_at) WHERE expires_at IS NOT NULL;

-- 3. 建立註解
COMMENT ON TABLE file_attachments IS '檔案附件管理表';

COMMENT ON COLUMN file_attachments.original_name IS '原始檔案名稱';
COMMENT ON COLUMN file_attachments.storage_path IS '儲存路徑 (相對於 uploads 目錄)';
COMMENT ON COLUMN file_attachments.file_size IS '檔案大小 (bytes)';
COMMENT ON COLUMN file_attachments.mime_type IS 'MIME 類型';
COMMENT ON COLUMN file_attachments.file_hash IS 'SHA-256 檔案雜湊 (用於去重)';

COMMENT ON COLUMN file_attachments.category IS '檔案分類';
COMMENT ON COLUMN file_attachments.business_type IS '業務類型 (如: contract, invoice, report)';
COMMENT ON COLUMN file_attachments.related_table IS '關聯的資料表名稱';
COMMENT ON COLUMN file_attachments.related_id IS '關聯的記錄 ID';

COMMENT ON COLUMN file_attachments.access_level IS '存取等級 (public, private, restricted)';
COMMENT ON COLUMN file_attachments.is_public IS '是否公開';
COMMENT ON COLUMN file_attachments.allowed_roles IS '允許存取的角色列表';
COMMENT ON COLUMN file_attachments.allowed_users IS '允許存取的使用者 ID 列表';

COMMENT ON COLUMN file_attachments.is_temp IS '是否為臨時檔案 (上傳後需確認)';
COMMENT ON COLUMN file_attachments.confirmed_at IS '確認時間';
COMMENT ON COLUMN file_attachments.version IS '檔案版本號';
COMMENT ON COLUMN file_attachments.previous_version_id IS '前一版本的檔案 ID';

COMMENT ON COLUMN file_attachments.thumbnail_path IS '縮圖路徑 (圖片檔案才有)';
COMMENT ON COLUMN file_attachments.metadata IS '其他中繼資料 (JSON)';
COMMENT ON COLUMN file_attachments.expires_at IS '過期時間';
