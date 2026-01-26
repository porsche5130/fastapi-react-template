-- 建立 notification_closedates 資料表
-- 用途：記錄使用者關閉系統通知的日期

-- 1. 建立新表
CREATE TABLE IF NOT EXISTS notification_closedates (
    id SERIAL PRIMARY KEY,
    closed_at DATE NOT NULL DEFAULT CURRENT_DATE,
    edit_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 確保每個使用者每天只有一筆記錄
    UNIQUE(edit_by, closed_at)
);

-- 2. 建立索引以提升查詢效能
CREATE INDEX idx_notification_closedates_edit_by ON notification_closedates(edit_by);
CREATE INDEX idx_notification_closedates_closed_at ON notification_closedates(closed_at);
CREATE INDEX idx_notification_closedates_edit_by_closed_at ON notification_closedates(edit_by, closed_at);

-- 3. 新增註解
COMMENT ON TABLE notification_closedates IS '系統通知關閉日期記錄表';
COMMENT ON COLUMN notification_closedates.id IS '資料編號（自動編號）';
COMMENT ON COLUMN notification_closedates.closed_at IS '不顯示訊息日期（預設今日）';
COMMENT ON COLUMN notification_closedates.edit_by IS '資料建立者（users.id）';
COMMENT ON COLUMN notification_closedates.created_at IS '資料建立時間（預設現在時間）';

-- 4. 刪除舊表（如果需要保留資料請先備份）
-- DROP TABLE IF EXISTS notification_read_today CASCADE;
