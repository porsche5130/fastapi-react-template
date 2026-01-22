"""
System Notifications Routes
系統通知管理路由
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.system_notification import SystemNotification, NotificationReadStatus
from app.schemas.system_notification import (
    SystemNotificationCreate,
    SystemNotificationUpdate,
    SystemNotificationResponse,
    NotificationReadStatusCreate,
    UnreadNotificationsResponse
)

router = APIRouter()


@router.get("/", response_model=List[SystemNotificationResponse])
async def get_notifications(
    is_active: Optional[bool] = Query(None, description="是否啟用"),
    notification_type: Optional[str] = Query(None, description="通知類型"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得系統通知列表（管理功能）
    """
    query = db.query(SystemNotification)

    if is_active is not None:
        query = query.filter(SystemNotification.is_active == is_active)

    if notification_type:
        query = query.filter(SystemNotification.notification_type == notification_type)

    # 按優先級和建立時間排序
    query = query.order_by(
        SystemNotification.priority.desc(),
        SystemNotification.created_at.desc()
    )

    notifications = query.offset(skip).limit(limit).all()

    # 查詢當前使用者的已讀狀態
    result = []
    for notification in notifications:
        read_status = db.query(NotificationReadStatus).filter(
            and_(
                NotificationReadStatus.notification_id == notification.id,
                NotificationReadStatus.user_id == current_user.id
            )
        ).first()

        notification_dict = {
            **notification.__dict__,
            "is_read": read_status is not None,
            "read_at": read_status.read_at if read_status else None
        }
        result.append(SystemNotificationResponse(**notification_dict))

    return result


@router.get("/active", response_model=List[SystemNotificationResponse])
async def get_active_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得當前使用者應該看到的有效通知
    - 啟用中的通知
    - 在時間範圍內的通知
    - 符合目標對象的通知
    """
    now = datetime.now()

    # 基本條件：啟用且在時間範圍內
    query = db.query(SystemNotification).filter(
        and_(
            SystemNotification.is_active == True,
            SystemNotification.start_time <= now,
            or_(
                SystemNotification.end_time == None,
                SystemNotification.end_time > now
            )
        )
    )

    # 目標對象過濾
    # 1. 全部使用者
    # 2. 特定角色（使用者的角色在目標角色列表中）
    # 3. 特定使用者（使用者ID在目標使用者列表中）
    notifications = []
    for notification in query.all():
        if notification.target_type == 'all':
            notifications.append(notification)
        elif notification.target_type == 'role' and current_user.role_id:
            if current_user.role_id in notification.target_roles:
                notifications.append(notification)
        elif notification.target_type == 'user':
            if current_user.id in notification.target_users:
                notifications.append(notification)

    # 按優先級排序
    notifications.sort(key=lambda x: (x.priority, x.created_at), reverse=True)

    # 查詢已讀狀態
    result = []
    for notification in notifications:
        read_status = db.query(NotificationReadStatus).filter(
            and_(
                NotificationReadStatus.notification_id == notification.id,
                NotificationReadStatus.user_id == current_user.id
            )
        ).first()

        notification_dict = {
            **notification.__dict__,
            "is_read": read_status is not None,
            "read_at": read_status.read_at if read_status else None
        }
        result.append(SystemNotificationResponse(**notification_dict))

    return result


@router.get("/unread", response_model=UnreadNotificationsResponse)
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得當前使用者的未讀通知
    """
    now = datetime.now()

    # 取得所有有效通知
    query = db.query(SystemNotification).filter(
        and_(
            SystemNotification.is_active == True,
            SystemNotification.start_time <= now,
            or_(
                SystemNotification.end_time == None,
                SystemNotification.end_time > now
            )
        )
    )

    # 過濾目標對象
    all_notifications = []
    for notification in query.all():
        if notification.target_type == 'all':
            all_notifications.append(notification)
        elif notification.target_type == 'role' and current_user.role_id:
            if current_user.role_id in notification.target_roles:
                all_notifications.append(notification)
        elif notification.target_type == 'user':
            if current_user.id in notification.target_users:
                all_notifications.append(notification)

    # 取得已讀的通知ID
    read_notification_ids = db.query(NotificationReadStatus.notification_id).filter(
        NotificationReadStatus.user_id == current_user.id
    ).all()
    read_ids = [id[0] for id in read_notification_ids]

    # 過濾未讀通知
    unread_notifications = [n for n in all_notifications if n.id not in read_ids]

    # 按優先級排序
    unread_notifications.sort(key=lambda x: (x.priority, x.created_at), reverse=True)

    # 構建回應
    result = []
    for notification in unread_notifications:
        notification_dict = {
            **notification.__dict__,
            "is_read": False,
            "read_at": None
        }
        result.append(SystemNotificationResponse(**notification_dict))

    return UnreadNotificationsResponse(
        unread_count=len(result),
        notifications=result
    )


@router.get("/{notification_id}", response_model=SystemNotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得單一系統通知
    """
    notification = db.query(SystemNotification).filter(
        SystemNotification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # 查詢已讀狀態
    read_status = db.query(NotificationReadStatus).filter(
        and_(
            NotificationReadStatus.notification_id == notification.id,
            NotificationReadStatus.user_id == current_user.id
        )
    ).first()

    notification_dict = {
        **notification.__dict__,
        "is_read": read_status is not None,
        "read_at": read_status.read_at if read_status else None
    }

    return SystemNotificationResponse(**notification_dict)


@router.post("/", response_model=SystemNotificationResponse, status_code=201)
async def create_notification(
    notification_data: SystemNotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    建立系統通知
    """
    # 驗證時間範圍
    if notification_data.end_time and notification_data.end_time <= notification_data.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    # 建立通知
    notification = SystemNotification(
        **notification_data.model_dump(),
        created_by=current_user.id
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    notification_dict = {
        **notification.__dict__,
        "is_read": False,
        "read_at": None
    }

    return SystemNotificationResponse(**notification_dict)


@router.put("/{notification_id}", response_model=SystemNotificationResponse)
async def update_notification(
    notification_id: int,
    notification_data: SystemNotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新系統通知
    """
    notification = db.query(SystemNotification).filter(
        SystemNotification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # 更新欄位
    update_data = notification_data.model_dump(exclude_unset=True)

    # 驗證時間範圍
    start_time = update_data.get('start_time', notification.start_time)
    end_time = update_data.get('end_time', notification.end_time)
    if end_time and end_time <= start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    for key, value in update_data.items():
        setattr(notification, key, value)

    notification.updated_at = datetime.now()

    db.commit()
    db.refresh(notification)

    # 查詢已讀狀態
    read_status = db.query(NotificationReadStatus).filter(
        and_(
            NotificationReadStatus.notification_id == notification.id,
            NotificationReadStatus.user_id == current_user.id
        )
    ).first()

    notification_dict = {
        **notification.__dict__,
        "is_read": read_status is not None,
        "read_at": read_status.read_at if read_status else None
    }

    return SystemNotificationResponse(**notification_dict)


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刪除系統通知
    """
    notification = db.query(SystemNotification).filter(
        SystemNotification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()

    return None


@router.post("/mark-as-read", status_code=204)
async def mark_notification_as_read(
    read_data: NotificationReadStatusCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    標記通知為已讀
    """
    # 檢查通知是否存在
    notification = db.query(SystemNotification).filter(
        SystemNotification.id == read_data.notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # 檢查是否已標記為已讀
    existing_status = db.query(NotificationReadStatus).filter(
        and_(
            NotificationReadStatus.notification_id == read_data.notification_id,
            NotificationReadStatus.user_id == current_user.id
        )
    ).first()

    if existing_status:
        # 已經標記過，不需重複標記
        return None

    # 建立已讀記錄
    read_status = NotificationReadStatus(
        notification_id=read_data.notification_id,
        user_id=current_user.id
    )

    db.add(read_status)
    db.commit()

    return None


@router.post("/mark-all-as-read", status_code=204)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    標記所有通知為已讀
    """
    now = datetime.now()

    # 取得所有有效通知
    query = db.query(SystemNotification).filter(
        and_(
            SystemNotification.is_active == True,
            SystemNotification.start_time <= now,
            or_(
                SystemNotification.end_time == None,
                SystemNotification.end_time > now
            )
        )
    )

    # 過濾目標對象
    all_notifications = []
    for notification in query.all():
        if notification.target_type == 'all':
            all_notifications.append(notification)
        elif notification.target_type == 'role' and current_user.role_id:
            if current_user.role_id in notification.target_roles:
                all_notifications.append(notification)
        elif notification.target_type == 'user':
            if current_user.id in notification.target_users:
                all_notifications.append(notification)

    # 取得已讀的通知ID
    read_notification_ids = db.query(NotificationReadStatus.notification_id).filter(
        NotificationReadStatus.user_id == current_user.id
    ).all()
    read_ids = [id[0] for id in read_notification_ids]

    # 標記未讀通知為已讀
    for notification in all_notifications:
        if notification.id not in read_ids:
            read_status = NotificationReadStatus(
                notification_id=notification.id,
                user_id=current_user.id
            )
            db.add(read_status)

    db.commit()

    return None
