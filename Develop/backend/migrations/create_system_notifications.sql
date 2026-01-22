-- 建立系統通知資料表
-- system_notifications: 系統通知主表

CREATE TABLE IF NOT EXISTS system_notifications (
    id SERIAL PRIMARY KEY,

    -- 通知內容
    title VARCHAR(200) NOT NULL,                          -- 通知標題
    content TEXT NOT NULL,                                 -- 通知內容
    notification_type VARCHAR(50) NOT NULL DEFAULT 'info', -- 通知類型: info, warning, error, success

    -- 顯示控制
    start_time TIMESTAMP NOT NULL,                         -- 開始顯示時間
    end_time TIMESTAMP,                                    -- 結束顯示時間（NULL表示永久）
    is_active BOOLEAN NOT NULL DEFAULT TRUE,              -- 是否啟用
    is_popup BOOLEAN NOT NULL DEFAULT FALSE,              -- 是否彈出顯示
    priority INTEGER NOT NULL DEFAULT 0,                   -- 優先級（數字越大越優先）

    -- 目標對象
    target_type VARCHAR(50) NOT NULL DEFAULT 'all',       -- 目標類型: all, role, user
    target_roles JSONB DEFAULT '[]'::jsonb,               -- 目標角色ID列表
    target_users JSONB DEFAULT '[]'::jsonb,               -- 目標使用者ID列表

    -- 系統欄位
    created_by INTEGER NOT NULL,                           -- 建立者
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- 外鍵
    CONSTRAINT fk_notification_creator FOREIGN KEY (created_by)
        REFERENCES user_detail(id) ON DELETE RESTRICT,

    -- 檢查約束
    CONSTRAINT chk_notification_type CHECK (notification_type IN ('info', 'warning', 'error', 'success')),
    CONSTRAINT chk_target_type CHECK (target_type IN ('all', 'role', 'user')),
    CONSTRAINT chk_time_range CHECK (end_time IS NULL OR end_time > start_time)
);

-- 建立索引
CREATE INDEX idx_notifications_active ON system_notifications(is_active);
CREATE INDEX idx_notifications_time ON system_notifications(start_time, end_time);
CREATE INDEX idx_notifications_type ON system_notifications(notification_type);
CREATE INDEX idx_notifications_target ON system_notifications(target_type);
CREATE INDEX idx_notifications_priority ON system_notifications(priority DESC);

-- 建立通知已讀狀態追蹤表
-- notification_read_status: 記錄每個使用者對每則通知的已讀狀態

CREATE TABLE IF NOT EXISTS notification_read_status (
    id SERIAL PRIMARY KEY,

    notification_id INTEGER NOT NULL,                      -- 通知ID
    user_id INTEGER NOT NULL,                             -- 使用者ID
    read_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 已讀時間

    -- 外鍵
    CONSTRAINT fk_read_notification FOREIGN KEY (notification_id)
        REFERENCES system_notifications(id) ON DELETE CASCADE,
    CONSTRAINT fk_read_user FOREIGN KEY (user_id)
        REFERENCES user_detail(id) ON DELETE CASCADE,

    -- 唯一約束：每個使用者對每則通知只能有一筆已讀記錄
    CONSTRAINT uq_notification_user UNIQUE (notification_id, user_id)
);

-- 建立索引
CREATE INDEX idx_read_status_notification ON notification_read_status(notification_id);
CREATE INDEX idx_read_status_user ON notification_read_status(user_id);
CREATE INDEX idx_read_status_time ON notification_read_status(read_at);

-- 註解
COMMENT ON TABLE system_notifications IS '系統通知主表';
COMMENT ON TABLE notification_read_status IS '通知已讀狀態追蹤表';

COMMENT ON COLUMN system_notifications.notification_type IS '通知類型: info(一般資訊), warning(警告), error(錯誤), success(成功)';
COMMENT ON COLUMN system_notifications.target_type IS '目標類型: all(所有人), role(特定角色), user(特定使用者)';
COMMENT ON COLUMN system_notifications.is_popup IS '是否在使用者登入時彈出顯示';
COMMENT ON COLUMN system_notifications.priority IS '優先級，數字越大越優先顯示';
