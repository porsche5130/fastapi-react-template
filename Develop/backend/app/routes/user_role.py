"""
User Role Routes
使用者角色相關路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user_role import UserRole
from app.models.user_detail import UserDetail
from app.schemas.user_role import UserRoleResponse, UserRoleCreate, UserRoleUpdate

router = APIRouter()


@router.get("/", response_model=List[UserRoleResponse], summary="取得使用者角色列表")
async def get_user_roles(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得使用者角色列表

    - **skip**: 略過筆數
    - **limit**: 限制筆數
    - **is_active**: 是否啟用 (可選)
    - **search**: 搜尋關鍵字 (角色中英文名稱)

    需要提供 Bearer Token
    """
    query = db.query(UserRole)

    if is_active is not None:
        query = query.filter(UserRole.is_active == is_active)

    if search:
        query = query.filter(
            (UserRole.role_cname.ilike(f"%{search}%")) |
            (UserRole.role_ename.ilike(f"%{search}%"))
        )

    roles = query.order_by(UserRole.id).offset(skip).limit(limit).all()

    return roles


@router.get("/{role_id}", response_model=UserRoleResponse, summary="取得使用者角色資訊")
async def get_user_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得使用者角色資訊

    - **role_id**: 角色 ID

    需要提供 Bearer Token
    """
    role = db.query(UserRole).filter(UserRole.id == role_id).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者角色"
        )

    return role


@router.post("/", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED, summary="建立使用者角色")
async def create_user_role(
    role_data: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    建立使用者角色

    需要提供 Bearer Token
    """
    # 檢查角色名稱是否已存在
    existing = db.query(UserRole).filter(
        (UserRole.role_cname == role_data.role_cname) |
        (UserRole.role_ename == role_data.role_ename)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名稱已存在"
        )

    # 建立角色
    role = UserRole(
        **role_data.model_dump(),
        edit_by=current_user.id
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.put("/{role_id}", response_model=UserRoleResponse, summary="更新使用者角色")
async def update_user_role(
    role_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    更新使用者角色

    - **role_id**: 角色 ID

    需要提供 Bearer Token
    """
    # 查詢角色
    role = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者角色"
        )

    # 如果更新角色名稱，檢查是否重複
    if role_data.role_cname or role_data.role_ename:
        existing = db.query(UserRole).filter(
            UserRole.id != role_id,
            (
                (UserRole.role_cname == (role_data.role_cname or role.role_cname)) |
                (UserRole.role_ename == (role_data.role_ename or role.role_ename))
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名稱已存在"
            )

    # 更新欄位
    update_data = role_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    role.edit_by = current_user.id
    role.updated_at = func.now()

    db.commit()
    db.refresh(role)

    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, summary="刪除使用者角色")
async def delete_user_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    刪除使用者角色（軟刪除，設定 is_active = False）

    - **role_id**: 角色 ID

    需要提供 Bearer Token
    """
    # 查詢角色
    role = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到使用者角色"
        )

    # 檢查是否有使用者使用此角色
    users_with_role = db.query(UserDetail).filter(
        UserDetail.user_role.contains([role_id]),
        UserDetail.is_active == True
    ).count()

    if users_with_role > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法刪除：此角色仍有 {users_with_role} 位啟用中的使用者使用"
        )

    # 軟刪除
    role.is_active = False
    role.edit_by = current_user.id
    role.updated_at = func.now()

    db.commit()

    return None
