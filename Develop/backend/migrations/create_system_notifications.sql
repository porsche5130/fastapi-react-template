-- 建立系統通知明細檔
-- Migration: create_system_notifications
-- Date: 2026-01-23
-- Version: 2.0 - 根據新規格重新設計

-- 1. 刪除舊的資料表（如果存在）
DROP TABLE IF EXISTS notification_read_status CASCADE;
DROP TABLE IF EXISTS system_notifications CASCADE;

-- 2. 建立 system_notifications 資料表
CREATE TABLE system_notifications (
    id SERIAL PRIMARY KEY,
    notice_csubject VARCHAR(200) NOT NULL,
    notice_esubject VARCHAR(200) NOT NULL,
    notice_cdescription TEXT NOT NULL,
    notice_edescription TEXT NOT NULL,
    notice_start_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notice_end_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '3 days'),
    notice_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    edit_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 外鍵約束
    CONSTRAINT fk_system_notifications_edit_by
        FOREIGN KEY (edit_by)
        REFERENCES users(id)
        ON DELETE RESTRICT
);

-- 3. 建立索引
CREATE INDEX idx_notifications_active ON system_notifications(is_active);
CREATE INDEX idx_notifications_time ON system_notifications(notice_start_at, notice_end_at);
CREATE INDEX idx_notifications_order ON system_notifications(notice_order);

-- 4. 建立「本日不再閱讀」追蹤表
CREATE TABLE notification_read_today (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_id INTEGER NOT NULL,
    read_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 外鍵約束
    CONSTRAINT fk_notification_read_today_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notification_read_today_notification
        FOREIGN KEY (notification_id)
        REFERENCES system_notifications(id)
        ON DELETE CASCADE,

    -- 唯一約束：每個使用者對每則通知每天只能有一筆記錄
    CONSTRAINT uq_notification_read_today
        UNIQUE (user_id, notification_id, read_date)
);

-- 5. 建立追蹤表索引
CREATE INDEX idx_notification_read_today_user ON notification_read_today(user_id);
CREATE INDEX idx_notification_read_today_notification ON notification_read_today(notification_id);
CREATE INDEX idx_notification_read_today_date ON notification_read_today(read_date);

-- 6. 建立註解
COMMENT ON TABLE system_notifications IS '系統通知明細檔';
COMMENT ON COLUMN system_notifications.id IS '資料編號（自動編號）';
COMMENT ON COLUMN system_notifications.notice_csubject IS '通知中文主旨';
COMMENT ON COLUMN system_notifications.notice_esubject IS '通知英文主旨';
COMMENT ON COLUMN system_notifications.notice_cdescription IS '通知中文說明（富文本格式）';
COMMENT ON COLUMN system_notifications.notice_edescription IS '通知英文說明（富文本格式）';
COMMENT ON COLUMN system_notifications.notice_start_at IS '通知開始時間';
COMMENT ON COLUMN system_notifications.notice_end_at IS '通知結束時間';
COMMENT ON COLUMN system_notifications.notice_order IS '訊息次序';
COMMENT ON COLUMN system_notifications.is_active IS '啟用狀態';
COMMENT ON COLUMN system_notifications.edit_by IS '資料建立/修改人員ID';
COMMENT ON COLUMN system_notifications.created_at IS '資料建立時間';
COMMENT ON COLUMN system_notifications.updated_at IS '資料最新修改時間';

COMMENT ON TABLE notification_read_today IS '通知本日不再閱讀追蹤表';
COMMENT ON COLUMN notification_read_today.id IS '資料編號（自動編號）';
COMMENT ON COLUMN notification_read_today.user_id IS '使用者ID';
COMMENT ON COLUMN notification_read_today.notification_id IS '通知ID';
COMMENT ON COLUMN notification_read_today.read_date IS '閱讀日期';
COMMENT ON COLUMN notification_read_today.created_at IS '建立時間';

-- 7. 在 system_functions 中新增系統通知功能項（如果不存在）
-- 注意：system_notifications 功能項已存在，這裡的 INSERT 會被 ON CONFLICT DO NOTHING 略過

-- 8. 測試資料（可選）
-- INSERT INTO system_notifications (
--     notice_csubject,
--     notice_esubject,
--     notice_cdescription,
--     notice_edescription,
--     notice_start_at,
--     notice_end_at,
--     notice_order,
--     is_active,
--     edit_by
-- ) VALUES (
--     '系統維護通知',
--     'System Maintenance Notice',
--     '<p>系統將於 2026-01-25 進行定期維護，預計維護時間 2 小時。</p>',
--     '<p>The system will undergo scheduled maintenance on 2026-01-25, estimated duration: 2 hours.</p>',
--     CURRENT_TIMESTAMP,
--     CURRENT_TIMESTAMP + INTERVAL '7 days',
--     1,
--     TRUE,
--     1
-- );
