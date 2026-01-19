"""
Role Right Routes
角色權限設定相關路由
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.role_right import RoleRight
from app.models.user_role import UserRole
from app.models.sysfuction import SysFunction
from app.models.user_detail import UserDetail
from app.schemas.role_right import (
    RoleRightResponse,
    RoleRightBatchCreate,
    FunctionWithPermissions,
    RoleRightsDetail
)

router = APIRouter()


@router.get("/functions", response_model=List[FunctionWithPermissions], summary="取得功能清單與可用權限")
async def get_functions_with_permissions(
    role_id: int = None,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得所有已啟用功能及其支援的權限項目

    - 回傳所有 is_active=true 的功能
    - 依 func_order 排序
    - 包含每個功能的 available_permissions
    - 若提供 role_id 且該角色為非系統管理角色(is_mana=false),則過濾掉系統管理功能(is_mana=true)
    """
    # 查詢功能清單
    query = db.query(SysFunction).filter(SysFunction.is_active == True)

    # 如果提供 role_id,檢查角色是否為系統管理角色
    if role_id:
        role = db.query(UserRole).filter(UserRole.id == role_id).first()
        if role and not role.is_mana:
            # 非系統管理角色,過濾掉系統管理功能
            query = query.filter(SysFunction.is_mana == False)

    functions = query.order_by(SysFunction.func_order).all()

    result = []
    for func in functions:
        # 判斷每個權限是否可用
        available_permissions = {
            "create": "Create" in func.module_item,
            "read": "Read" in func.module_item,
            "update": "Update" in func.module_item,
            "delete": "Delete" in func.module_item,
            "print": "Print" in func.module_item,
            "file": "File" in func.module_item,
        }

        result.append(FunctionWithPermissions(
            id=func.id,
            func_code=func.func_code,
            func_cname=func.func_cname,
            func_ename=func.func_ename,
            func_type=func.func_type,
            func_order=func.func_order,
            upper_func_id=func.upper_func_id,
            module_item=func.module_item,
            available_permissions=available_permissions
        ))

    return result


@router.get("/{role_id}", response_model=RoleRightsDetail, summary="取得角色權限設定")
async def get_role_rights(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得指定角色的權限設定

    Args:
        role_id: 角色ID

    Returns:
        角色權限詳情，包含角色資訊與權限列表
    """
    # 檢查角色是否存在
    role = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的角色"
        )

    # 查詢權限設定
    rights = db.query(RoleRight).filter(
        RoleRight.user_role_id == role_id
    ).all()

    return RoleRightsDetail(
        role_id=role.id,
        role_name=role.role_cname,
        rights=rights
    )


@router.post("/{role_id}", response_model=dict, summary="儲存角色權限設定")
async def save_role_rights(
    role_id: int,
    data: RoleRightBatchCreate,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    儲存角色權限設定 (先刪後增策略)

    步驟:
    1. 檢查角色是否存在且啟用
    2. 刪除該角色的所有現有權限
    3. 批次新增最新的權限設定

    Args:
        role_id: 角色ID
        data: 權限設定資料

    Returns:
        儲存結果訊息
    """
    # 檢查角色
    role = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的角色"
        )

    if not role.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="該角色已停用，無法設定權限"
        )

    try:
        # 1. 刪除舊資料
        deleted_count = db.query(RoleRight).filter(
            RoleRight.user_role_id == role_id
        ).delete()

        # 2. 批次新增新資料
        new_rights = []
        for right in data.rights:
            # 驗證功能是否存在
            function = db.query(SysFunction).filter(
                SysFunction.id == right.sysfuction_id
            ).first()
            if not function:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"找不到功能ID: {right.sysfuction_id}"
                )

            new_right = RoleRight(
                user_role_id=role_id,
                sysfuction_id=right.sysfuction_id,
                func_code=right.func_code,
                is_create=right.is_create,
                is_read=right.is_read,
                is_update=right.is_update,
                is_delete=right.is_delete,
                is_print=right.is_print,
                is_file=right.is_file,
                edit_by=current_user.id
            )
            new_rights.append(new_right)

        db.bulk_save_objects(new_rights)
        db.commit()

        return {
            "message": "權限設定儲存成功",
            "role_id": role_id,
            "total_rights": len(new_rights),
            "deleted_count": deleted_count
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"權限設定儲存失敗: {str(e)}"
        )


@router.delete("/{role_id}", status_code=status.HTTP_200_OK, summary="刪除角色權限設定")
async def delete_role_rights(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    刪除指定角色的所有權限設定

    Args:
        role_id: 角色ID

    Returns:
        刪除結果訊息
    """
    deleted_count = db.query(RoleRight).filter(
        RoleRight.user_role_id == role_id
    ).delete()

    db.commit()

    return {
        "message": "權限設定已刪除",
        "deleted_count": deleted_count
    }
