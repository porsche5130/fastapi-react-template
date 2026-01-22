"""
System Profile Routes
系統設定相關路由
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.models.sys_profile import SysProfile
from app.models.user import User
from app.schemas.sys_profile import SysProfileResponse, SysProfileUpdate
from app.services.userlog_service import UserLogService

logger = logging.getLogger(__name__)
router = APIRouter()


def sys_profile_to_dict(profile: SysProfile) -> dict:
    """將 SysProfile 物件轉換為完整資料字典"""
    return {
        "id": profile.id,
        "is_service": profile.is_service,
        "sys_url": profile.sys_url,
        "sys_ctitle": profile.sys_ctitle,
        "sys_etitle": profile.sys_etitle,
        "sys_ccopyright": profile.sys_ccopyright,
        "sys_ecopyright": profile.sys_ecopyright,
        "sys_organization": profile.sys_organization,
        "sys_mana_email": profile.sys_mana_email,
        "edit_by": profile.edit_by,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    }


@router.get("/", response_model=SysProfileResponse, summary="取得系統設定")
async def get_sys_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得系統設定（id=1）

    需要提供 Bearer Token（所有已登入使用者都可讀取）
    """
    # 系統基本資料不需要權限檢查,所有登入使用者都可以讀取
    logger.info(f"使用者 {current_user.id} 正在讀取系統設定")

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
    current_user: User = Depends(get_current_user)
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

    # 保存原始資料用於日誌
    original_data = sys_profile_to_dict(profile)

    # 更新欄位
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.edit_by = current_user.id
    profile.updated_at = func.now()

    db.commit()
    db.refresh(profile)

    return profile
