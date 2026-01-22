"""
Organization Routes
組織單位相關路由
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse, OrganizationCreate, OrganizationUpdate
from app.services.userlog_service import UserLogService

logger = logging.getLogger(__name__)
router = APIRouter()


def organization_to_dict(org: Organization) -> dict:
    """將組織單位物件轉換為完整字典"""
    return {
        "id": org.id,
        "org_code": org.org_code,
        "org_name": org.org_name,
        "org_type": org.org_type,
        "contact_person": org.contact_person,
        "contact_email": org.contact_email,
        "contact_phone": org.contact_phone,
        "address": org.address,
        "phone": org.phone,
        "is_mana": org.is_mana,
        "is_active": org.is_active,
        "memo": org.memo,
        "edit_by": org.edit_by,
        "created_at": org.created_at.isoformat() if org.created_at else None,
        "updated_at": org.updated_at.isoformat() if org.updated_at else None
    }


@router.get("/", response_model=List[OrganizationResponse], summary="取得組織單位列表")
async def get_organizations(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得組織單位列表

    - **skip**: 略過筆數
    - **limit**: 限制筆數
    - **is_active**: 是否啟用 (可選)
    - **search**: 搜尋關鍵字 (組織代碼或名稱)

    需要提供 Bearer Token 及 organizations 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "organizations", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取組織設定"
        )

    query = db.query(Organization)

    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)

    if search:
        query = query.filter(
            (Organization.org_code.ilike(f"%{search}%")) |
            (Organization.org_name.ilike(f"%{search}%"))
        )

    organizations = query.order_by(Organization.id).offset(skip).limit(limit).all()

    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse, summary="取得組織單位資訊")
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得組織單位資訊

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token 及 organizations 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "organizations", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取組織設定"
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到組織單位"
        )

    return organization


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED, summary="建立組織單位")
async def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    建立組織單位

    需要提供 Bearer Token 及 organizations 新增權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "organizations", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限新增組織設定"
        )

    # 檢查組織代碼是否已存在
    existing = db.query(Organization).filter(Organization.org_code == organization_data.org_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="組織代碼已存在"
        )

    # 建立組織單位
    organization = Organization(
        **organization_data.model_dump(),
        edit_by=current_user.id
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse, summary="更新組織單位")
async def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新組織單位

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token 及 organizations 修改權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "organizations", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改組織設定"
        )

    # 查詢組織單位
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到組織單位"
        )

    # 如果更新組織代碼，檢查是否重複
    if organization_data.org_code and organization_data.org_code != organization.org_code:
        existing = db.query(Organization).filter(
            Organization.org_code == organization_data.org_code,
            Organization.id != organization_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="組織代碼已存在"
            )

    # 更新組織單位資料
    update_data = organization_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.edit_by = current_user.id
    organization.updated_at = func.now()

    db.commit()
    db.refresh(organization)

    return organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT, summary="刪除組織單位")
async def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    刪除組織單位（軟刪除，設定 is_active = False）

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token 及 organizations 刪除權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "organizations", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除組織設定"
        )

    # 查詢組織單位
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到組織單位"
        )

    # 檢查是否有使用者使用此組織（包含已停用的）
    users_count = db.query(User).filter(
        User.organization_id == organization_id
    ).count()

    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法刪除：此組織單位仍有 {users_count} 位使用者"
        )

    # 真正刪除
    db.delete(organization)
    db.commit()

    return None
