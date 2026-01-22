"""
System Notification Models
系統通知模型
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SystemNotification(Base):
    """系統通知主表"""

    __tablename__ = "system_notifications"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 通知內容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default='info', index=True)

    # 顯示控制
    start_time = Column(TIMESTAMP, nullable=False, index=True)
    end_time = Column(TIMESTAMP, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_popup = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0, index=True)

    # 目標對象
    target_type = Column(String(50), nullable=False, default='all', index=True)
    target_roles = Column(JSONB, nullable=False, default=list)
    target_users = Column(JSONB, nullable=False, default=list)

    # 系統欄位
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP)

    # 約束
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('info', 'warning', 'error', 'success')",
            name="chk_notification_type"
        ),
        CheckConstraint(
            "target_type IN ('all', 'role', 'user')",
            name="chk_target_type"
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time > start_time",
            name="chk_time_range"
        ),
        Index("idx_notifications_active", "is_active"),
        Index("idx_notifications_time", "start_time", "end_time"),
        Index("idx_notifications_type", "notification_type"),
        Index("idx_notifications_target", "target_type"),
        Index("idx_notifications_priority", "priority"),
    )

    # 關聯
    creator = relationship("User", foreign_keys=[created_by])
    read_statuses = relationship("NotificationReadStatus", back_populates="notification", cascade="all, delete-orphan")


class NotificationReadStatus(Base):
    """通知已讀狀態追蹤表"""

    __tablename__ = "notification_read_status"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 外鍵
    notification_id = Column(Integer, ForeignKey("system_notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 已讀時間
    read_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), index=True)

    # 約束
    __table_args__ = (
        Index("idx_read_status_notification", "notification_id"),
        Index("idx_read_status_user", "user_id"),
        Index("idx_read_status_time", "read_at"),
        # 唯一約束：每個使用者對每則通知只能有一筆已讀記錄
        {"schema": "public"},
    )

    # 關聯
    notification = relationship("SystemNotification", back_populates="read_statuses")
    user = relationship("User")
