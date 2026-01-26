"""
User Detail Routes
使用者設定相關路由
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission  # 保留用於資料層級安全控制
from app.core.security import get_password_hash, verify_password
from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.models.organization import Organization
from app.routes.transaction import require_txn_token
from app.schemas.user_detail import (
    UserDetailResponse,
    UserDetailCreate,
    UserDetailUpdate,
    PasswordChange
)
from app.services.userlog_service import UserLogService

logger = logging.getLogger(__name__)
router = APIRouter()

# 台北時區 (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))


def user_detail_to_dict(user: User) -> dict:
    """將 User 物件轉換為完整資料字典 (不含密碼)"""
    return {
        "id": user.id,
        "account": user.account,  # account 欄位儲存的是電子郵件
        "email": user.account,     # 為了日誌清晰，也對應到 email
        "username": user.username,
        "organization_id": user.organization_id,
        "department": user.department,
        "job_title": user.job_title,
        "phone": user.phone,
        "user_role": user.user_role,
        "is_active": user.is_active,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "last_login_ip": user.last_login_ip,
        "edit_by": user.edit_by,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


@router.get("/", response_model=List[UserDetailResponse], summary="取得使用者列表")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    organization_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("users", "read"))
):
    """
    取得使用者列表

    需要 users 功能的 read 權限

    資料層級安全控制:一般使用者只能查看自己組織的使用者

    - **skip**: 略過筆數
    - **limit**: 限制筆數
    - **is_active**: 是否啟用 (可選)
    - **organization_id**: 組織單位ID (可選)
    - **search**: 搜尋關鍵字 (帳號或名稱)

    需要提供 Bearer Token 及 X-Txn-Token Header
    """
    # Token 已驗證 read 權限
    query = db.query(User)

    # 資料層級安全控制:檢查使用者是否有完整的 users 管理權限
    # 如果沒有,只能查看自己組織的使用者
    # 注意:這裡不是檢查 Token,而是檢查使用者的角色權限範圍
    has_full_permission = check_permission(db, current_user, "users", "read")
    if not has_full_permission:
        # 只能查看自己組織的使用者
        query = query.filter(User.organization_id == current_user.organization_id)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if organization_id is not None:
        query = query.filter(User.organization_id == organization_id)

    if search:
        query = query.filter(
            (User.account.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    users = query.order_by(User.id).offset(skip).limit(limit).all()

    return users


@router.get("/me", response_model=UserDetailResponse, summary="取得我的個人資料")
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得當前登入使用者的個人資料

    無需特殊權限 - 返回已驗證使用者的資料

    需要提供 Bearer Token
    """
    return current_user


@router.put("/me", response_model=UserDetailResponse, summary="更新我的個人資料")
async def update_my_profile(
    profile_data: UserDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("my_profile", "update"))
):
    """
    更新當前登入使用者的個人資料

    步驟:
    1. 交易令牌已由依賴項驗證
    2. 儲存原始資料用於日誌記錄
    3. 驗證組織 ID（如有變更）
    4. 防止帳號變更（安全性）
    5. 僅更新允許的欄位
    6. 記錄更新
    7. 返回更新後的個人資料

    允許更新的欄位:
    - account (帳號，需確保唯一性)
    - username (使用者名稱)
    - department (部門)
    - job_title (職稱)
    - phone (電話)

    禁止變更的欄位:
    - organization_id (組織)
    - user_role (角色權限)
    - is_active (啟用狀態)
    - password (密碼，請使用密碼變更功能)

    需要提供 Bearer Token 及 my_profile 更新權限的交易令牌
    """
    # 儲存原始資料用於日誌記錄
    original_data = user_detail_to_dict(current_user)

    # 如果要變更帳號，檢查新帳號是否已存在
    if profile_data.account and profile_data.account != current_user.account:
        existing_user = db.query(User).filter(User.account == profile_data.account).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="此帳號已被使用，請使用其他帳號"
            )

    # 安全性:無法變更組織
    if profile_data.organization_id and profile_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法變更組織"
        )

    # 安全性:無法變更角色權限
    if profile_data.user_role and profile_data.user_role != current_user.user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法變更角色權限"
        )

    # 安全性:無法變更啟用狀態
    if profile_data.is_active is not None and profile_data.is_active != current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法變更啟用狀態"
        )

    # 僅取得允許的欄位
    update_data = profile_data.model_dump(exclude_unset=True)
    allowed_fields = ['account', 'username', 'department', 'job_title', 'phone']
    update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    # 更新欄位
    for field, value in update_data.items():
        setattr(current_user, field, value)

    # 更新系統欄位
    current_user.edit_by = current_user.id
    current_user.updated_at = func.now()

    # 持久化
    db.commit()
    db.refresh(current_user)

    # 記錄更新
    UserLogService.log_update(
        db=db,
        user_id=current_user.id,
        function_id=UserLogService.get_function_id_by_code(db, "my_profile"),
        original_data=original_data,
        updated_data=user_detail_to_dict(current_user),
        current_user=current_user
    )

    return current_user


@router.get("/{user_id}", response_model=UserDetailResponse, summary="取得使用者資訊")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("users", "read"))
):
    """
    取得使用者資訊

    需要 users 功能的 read 權限

    資料層級安全控制:一般使用者只能查看自己組織的使用者

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 X-Txn-Token Header
    """
    # Token 已驗證 read 權限
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 資料層級安全控制:檢查是否有權限查看此使用者
    has_full_permission = check_permission(db, current_user, "users", "read")
    if not has_full_permission and user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取此使用者資訊"
        )

    return user


@router.post("/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED, summary="建立使用者")
async def create_user(
    user_data: UserDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("users", "create"))
):
    """
    建立使用者

    需要 users 功能的 create 權限

    需要提供 Bearer Token 及 X-Txn-Token Header
    """
    # Token 已驗證 create 權限，不需要再次檢查

    # 檢查帳號是否已存在
    existing = db.query(User).filter(User.account == user_data.account).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="帳號已存在"
        )

    # 檢查組織單位是否存在
    organization = db.query(Organization).filter(
        Organization.id == user_data.organization_id,
        Organization.is_active == True
    ).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="組織單位不存在或未啟用"
        )

    # 建立使用者（密碼需加密）
    user_dict = user_data.model_dump()
    password = user_dict.pop('password')
    hashed_password = get_password_hash(password)

    user = User(
        **user_dict,
        password=hashed_password,
        edit_by=current_user.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}", response_model=UserDetailResponse, summary="更新使用者")
async def update_user(
    user_id: int,
    user_data: UserDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("users", "update"))
):
    """
    更新使用者

    需要 users 功能的 update 權限

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 X-Txn-Token Header
    """
    # Token 已驗證 update 權限，不需要再次檢查

    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 保存原始資料用於日誌
    original_data = user_detail_to_dict(user)

    # 如果更新帳號，檢查是否重複
    if user_data.account and user_data.account != user.account:
        existing = db.query(User).filter(
            User.account == user_data.account,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="帳號已存在"
            )

    # 如果更新組織單位，檢查是否存在
    if user_data.organization_id and user_data.organization_id != user.organization_id:
        organization = db.query(Organization).filter(
            Organization.id == user_data.organization_id,
            Organization.is_active == True
        ).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="組織單位不存在或未啟用"
            )

    # 更新欄位
    update_data = user_data.model_dump(exclude_unset=True)

    # 如果更新密碼，需要加密
    if 'password' in update_data:
        password = update_data.pop('password')
        update_data['password'] = get_password_hash(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    user.edit_by = current_user.id
    user.updated_at = func.now()

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="刪除使用者")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("users", "delete", one_time_use=True))
):
    """
    刪除使用者（軟刪除，設定 is_active = False）

    需要 users 功能的 delete 權限
    此操作為一次性使用，Token 使用後立即失效

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 X-Txn-Token Header
    """
    # Token 已驗證 delete 權限，且使用後立即失效

    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 保存刪除前資料用於日誌
    deleted_data = user_detail_to_dict(user)

    # 不能刪除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能刪除自己的帳號"
        )

    # 軟刪除
    user.is_active = False
    user.edit_by = current_user.id
    user.updated_at = func.now()

    db.commit()

    return None


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT, summary="變更密碼")
async def change_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("change_password", "update"))
):
    """
    變更當前使用者的密碼

    步驟:
    1. 交易令牌已由依賴項驗證
    2. 驗證使用者只能變更自己的密碼
    3. 驗證舊密碼是否正確
    4. 雜湊並更新新密碼
    5. 記錄密碼變更（不記錄實際密碼）
    6. 返回 204 No Content

    - **user_id**: 使用者 ID
    - **old_password**: 舊密碼
    - **new_password**: 新密碼

    需要提供 Bearer Token 及 change_password 更新權限的交易令牌，且只能修改自己的密碼
    """
    # 安全性:只能修改自己的密碼
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密碼"
        )

    # 驗證舊密碼
    if not verify_password(password_data.old_password, current_user.password):
        # 記錄失敗嘗試
        UserLogService.log_error(
            db=db,
            user_id=current_user.id,
            function_id=UserLogService.get_function_id_by_code(db, "change_password"),
            module_item="Update",
            error_message="舊密碼錯誤"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="舊密碼錯誤"
        )

    # 更新密碼
    current_user.password = get_password_hash(password_data.new_password)
    current_user.updated_at = func.now()
    current_user.edit_by = current_user.id

    # 持久化
    db.commit()

    # 記錄成功的密碼變更（不記錄實際密碼）
    UserLogService.log_update(
        db=db,
        user_id=current_user.id,
        function_id=UserLogService.get_function_id_by_code(db, "change_password"),
        original_data={"user_id": current_user.id, "action": "password_change"},
        updated_data={
            "user_id": current_user.id,
            "action": "password_changed",
            "timestamp": datetime.now(TAIPEI_TZ).isoformat()
        },
        current_user=current_user
    )

    return None
