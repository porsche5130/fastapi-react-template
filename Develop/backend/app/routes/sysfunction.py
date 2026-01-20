"""
System Function Routes
系統功能設定相關路由
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.models.sysfunction import SysFunction
from app.models.user_detail import UserDetail
from app.schemas.sysfunction import SysFunctionResponse, SysFunctionCreate, SysFunctionUpdate
from app.services.userlog_service import UserLogService

logger = logging.getLogger(__name__)
router = APIRouter()


def sysfunction_to_dict(func: SysFunction) -> dict:
    """將 SysFunction 物件轉換為完整資料字典"""
    return {
        "id": func.id,
        "func_code": func.func_code,
        "func_cname": func.func_cname,
        "func_ename": func.func_ename,
        "func_type": func.func_type,
        "func_order": func.func_order,
        "func_icon": func.func_icon,
        "func_module_name": func.func_module_name,
        "upper_func_id": func.upper_func_id,
        "module_item": func.module_item,
        "description": func.description,
        "is_mana": func.is_mana,
        "is_active": func.is_active,
        "edit_by": func.edit_by,
        "created_at": func.created_at.isoformat() if func.created_at else None,
        "updated_at": func.updated_at.isoformat() if func.updated_at else None
    }


@router.get("/", response_model=List[SysFunctionResponse], summary="取得系統功能列表")
async def get_functions(
    skip: int = 0,
    limit: int = 1000,
    is_active: Optional[bool] = None,
    func_type: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得系統功能列表

    需要提供 Bearer Token 及 sysfunction 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sysfunction", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取系統功能"
        )

    query = db.query(SysFunction)

    if is_active is not None:
        query = query.filter(SysFunction.is_active == is_active)

    if func_type is not None:
        query = query.filter(SysFunction.func_type == func_type)

    if search:
        query = query.filter(
            (SysFunction.func_code.ilike(f"%{search}%")) |
            (SysFunction.func_cname.ilike(f"%{search}%")) |
            (SysFunction.func_ename.ilike(f"%{search}%"))
        )

    functions = query.order_by(SysFunction.func_order).offset(skip).limit(limit).all()

    return functions


@router.get("/{function_id}", response_model=SysFunctionResponse, summary="取得系統功能資訊")
async def get_function(
    function_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得系統功能資訊

    需要提供 Bearer Token 及 sysfunction 讀取權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sysfunction", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取系統功能"
        )

    function = db.query(SysFunction).filter(SysFunction.id == function_id).first()
    if not function:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到系統功能")

    return new_function


@router.put("/{function_id}", response_model=SysFunctionResponse, summary="更新系統功能")
async def update_function(
    function_id: int,
    function_data: SysFunctionUpdate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    更新系統功能

    需要提供 Bearer Token 及 sysfunction 修改權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sysfunction", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改系統功能"
        )

    function = db.query(SysFunction).filter(SysFunction.id == function_id).first()
    if not function:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到系統功能")

    # 保存原始資料用於日誌
    original_data = sysfunction_to_dict(function)

    if function_data.func_code and function_data.func_code != function.func_code:
        existing = db.query(SysFunction).filter(SysFunction.func_code == function_data.func_code).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="功能代碼已存在")

    update_data = function_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(function, field, value)
    function.edit_by = current_user.id

    db.commit()
    db.refresh(function)

    return function


@router.delete("/{function_id}", status_code=status.HTTP_204_NO_CONTENT, summary="刪除系統功能")
async def delete_function(
    function_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    刪除系統功能

    需要提供 Bearer Token 及 sysfunction 刪除權限
    """
    # 檢查權限
    if not check_permission(db, current_user, "sysfunction", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除系統功能"
        )

    function = db.query(SysFunction).filter(SysFunction.id == function_id).first()
    if not function:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到系統功能")

    # 保存刪除前資料用於日誌
    deleted_data = sysfunction_to_dict(function)

    db.delete(function)
    db.commit()

    return None
