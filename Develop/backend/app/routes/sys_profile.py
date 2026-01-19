"""
System Profile Routes
系統設定相關路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.models.sys_profile import SysProfile
from app.models.user_detail import UserDetail
from app.schemas.sys_profile import SysProfileResponse, SysProfileUpdate

router = APIRouter()


@router.get("/", response_model=SysProfileResponse, summary="取得系統設定")
async def get_sys_profile(
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得系統設定（id=1）

    需要提供 Bearer Token 及 sys_profile 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sys_profile", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取系統設定"
        )

    profile = db.query(SysProfile).filter(SysProfile.id == 1).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系統設定不存在"
        )

    return profile


@router.put("/", response_model=SysProfileResponse, summary="更新系統設定")
async def update_sys_profile(
    profile_data: SysProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    更新系統設定（id=1）

    需要提供 Bearer Token 及 sys_profile 修改權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sys_profile", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改系統設定"
        )

    # 查詢系統設定
    profile = db.query(SysProfile).filter(SysProfile.id == 1).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系統設定不存在"
        )

    # 更新欄位
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.edit_by = current_user.id
    profile.updated_at = func.now()

    db.commit()
    db.refresh(profile)

    return profile
