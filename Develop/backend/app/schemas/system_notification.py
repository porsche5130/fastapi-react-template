"""
System Notification Schemas
系統通知 API Schema
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class NotificationType(str, Enum):
    """通知類型"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class TargetType(str, Enum):
    """目標類型"""
    ALL = "all"           # 所有使用者
    ROLE = "role"         # 特定角色
    USER = "user"         # 特定使用者


class SystemNotificationBase(BaseModel):
    """系統通知基本資料"""
    title: str = Field(..., max_length=200, description="通知標題")
    content: str = Field(..., description="通知內容")
    notification_type: NotificationType = Field(NotificationType.INFO, description="通知類型")
    start_time: datetime = Field(..., description="開始顯示時間")
    end_time: Optional[datetime] = Field(None, description="結束顯示時間（NULL表示永久）")
    is_active: bool = Field(True, description="是否啟用")
    is_popup: bool = Field(False, description="是否彈出顯示")
    priority: int = Field(0, description="優先級（數字越大越優先）")
    target_type: TargetType = Field(TargetType.ALL, description="目標類型")
    target_roles: List[int] = Field(default_factory=list, description="目標角色ID列表")
    target_users: List[int] = Field(default_factory=list, description="目標使用者ID列表")


class SystemNotificationCreate(SystemNotificationBase):
    """建立系統通知"""
    pass


class SystemNotificationUpdate(BaseModel):
    """更新系統通知（所有欄位可選）"""
    title: Optional[str] = Field(None, max_length=200, description="通知標題")
    content: Optional[str] = Field(None, description="通知內容")
    notification_type: Optional[NotificationType] = Field(None, description="通知類型")
    start_time: Optional[datetime] = Field(None, description="開始顯示時間")
    end_time: Optional[datetime] = Field(None, description="結束顯示時間")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    is_popup: Optional[bool] = Field(None, description="是否彈出顯示")
    priority: Optional[int] = Field(None, description="優先級")
    target_type: Optional[TargetType] = Field(None, description="目標類型")
    target_roles: Optional[List[int]] = Field(None, description="目標角色ID列表")
    target_users: Optional[List[int]] = Field(None, description="目標使用者ID列表")


class SystemNotificationResponse(SystemNotificationBase):
    """系統通知回應資料"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_read: Optional[bool] = Field(None, description="是否已讀（針對當前使用者）")
    read_at: Optional[datetime] = Field(None, description="已讀時間（針對當前使用者）")

    class Config:
        from_attributes = True


class NotificationReadStatusCreate(BaseModel):
    """標記通知為已讀"""
    notification_id: int = Field(..., description="通知ID")


class NotificationReadStatusResponse(BaseModel):
    """已讀狀態回應"""
    id: int
    notification_id: int
    user_id: int
    read_at: datetime

    class Config:
        from_attributes = True


class UnreadNotificationsResponse(BaseModel):
    """未讀通知統計回應"""
    unread_count: int = Field(..., description="未讀通知數量")
    notifications: List[SystemNotificationResponse] = Field(..., description="未讀通知列表")
