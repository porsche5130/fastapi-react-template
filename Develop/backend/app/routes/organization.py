"""
Organization Routes
組織單位相關路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.organization import Organization
from app.models.user_detail import UserDetail
from app.schemas.organization import OrganizationResponse, OrganizationCreate, OrganizationUpdate

router = APIRouter()


@router.get("/", response_model=List[OrganizationResponse], summary="取得組織單位列表")
async def get_organizations(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得組織單位列表

    - **skip**: 略過筆數
    - **limit**: 限制筆數
    - **is_active**: 是否啟用 (可選)
    - **search**: 搜尋關鍵字 (組織代碼或名稱)

    需要提供 Bearer Token
    """
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得組織單位資訊

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token
    """
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    建立組織單位

    需要提供 Bearer Token
    """
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    更新組織單位

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token
    """
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

    # 更新欄位
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
    current_user: UserDetail = Depends(get_current_user)
):
    """
    刪除組織單位（軟刪除，設定 is_active = False）

    - **organization_id**: 組織單位 ID

    需要提供 Bearer Token
    """
    # 查詢組織單位
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到組織單位"
        )

    # 檢查是否有使用者使用此組織
    users_count = db.query(UserDetail).filter(
        UserDetail.organization_id == organization_id,
        UserDetail.is_active == True
    ).count()

    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法刪除：此組織單位仍有 {users_count} 位啟用中的使用者"
        )

    # 軟刪除
    organization.is_active = False
    organization.edit_by = current_user.id
    organization.updated_at = func.now()

    db.commit()

    return None
