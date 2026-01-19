"""
User Detail Routes
使用者設定相關路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.core.security import get_password_hash, verify_password
from app.models.user_detail import UserDetail
from app.models.organization import Organization
from app.schemas.user_detail import (
    UserDetailResponse,
    UserDetailCreate,
    UserDetailUpdate,
    PasswordChange
)

router = APIRouter()


@router.get("/", response_model=List[UserDetailResponse], summary="取得使用者列表")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    organization_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得使用者列表

    - **skip**: 略過筆數
    - **limit**: 限制筆數
    - **is_active**: 是否啟用 (可選)
    - **organization_id**: 組織單位ID (可選)
    - **search**: 搜尋關鍵字 (帳號或名稱)

    需要提供 Bearer Token 及 user_detail 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "user_detail", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取使用者"
        )

    query = db.query(UserDetail)

    if is_active is not None:
        query = query.filter(UserDetail.is_active == is_active)

    if organization_id is not None:
        query = query.filter(UserDetail.organization_id == organization_id)

    if search:
        query = query.filter(
            (UserDetail.account.ilike(f"%{search}%")) |
            (UserDetail.username.ilike(f"%{search}%"))
        )

    users = query.order_by(UserDetail.id).offset(skip).limit(limit).all()

    return users


@router.get("/{user_id}", response_model=UserDetailResponse, summary="取得使用者資訊")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得使用者資訊

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 user_detail 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "user_detail", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取使用者"
        )

    user = db.query(UserDetail).filter(UserDetail.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    return user


@router.post("/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED, summary="建立使用者")
async def create_user(
    user_data: UserDetailCreate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    建立使用者

    需要提供 Bearer Token 及 user_detail 新增權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "user_detail", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限新增使用者"
        )

    # 檢查帳號是否已存在
    existing = db.query(UserDetail).filter(UserDetail.account == user_data.account).first()
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

    user = UserDetail(
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    更新使用者

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 user_detail 修改權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "user_detail", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改使用者"
        )

    # 查詢使用者
    user = db.query(UserDetail).filter(UserDetail.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

    # 如果更新帳號，檢查是否重複
    if user_data.account and user_data.account != user.account:
        existing = db.query(UserDetail).filter(
            UserDetail.account == user_data.account,
            UserDetail.id != user_id
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    刪除使用者（軟刪除，設定 is_active = False）

    - **user_id**: 使用者 ID

    需要提供 Bearer Token 及 user_detail 刪除權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "user_detail", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除使用者"
        )

    # 查詢使用者
    user = db.query(UserDetail).filter(UserDetail.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者"
        )

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


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT, summary="修改密碼")
async def change_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    修改密碼

    - **user_id**: 使用者 ID
    - **old_password**: 舊密碼
    - **new_password**: 新密碼

    需要提供 Bearer Token，且只能修改自己的密碼
    """
    # 只能修改自己的密碼
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密碼"
        )

    # 驗證舊密碼
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="舊密碼錯誤"
        )

    # 更新密碼
    current_user.password = get_password_hash(password_data.new_password)
    current_user.updated_at = func.now()

    db.commit()

    return None
