"""
System Management Routes
系統管理相關路由
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user_detail import UserDetail
from app.models.sys_profile import SysProfile
from app.models.sysfuction import SysFunction

router = APIRouter()


@router.get("/profile", summary="取得系統設定")
async def get_system_profile(db: Session = Depends(get_db)):
    """
    取得系統設定資訊

    不需要認證（用於檢查系統維護狀態）
    """
    profile = db.query(SysProfile).filter(SysProfile.id == 1).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系統設定不存在"
        )

    return {
        "id": profile.id,
        "is_service": profile.is_service,
        "sys_url": profile.sys_url,
        "sys_ctitle": profile.sys_ctitle,
        "sys_etitle": profile.sys_etitle,
        "sys_ccopyright": profile.sys_ccopyright,
        "sys_ecopyright": profile.sys_ecopyright,
        "sys_organization": profile.sys_organization,
        "sys_mana_email": profile.sys_mana_email
    }


@router.get("/check", summary="系統檢查")
async def system_check(db: Session = Depends(get_db)):
    """
    系統健康檢查

    檢查：
    - 資料庫連線
    - 系統服務狀態
    """
    try:
        # 檢查資料庫連線
        profile = db.query(SysProfile).filter(SysProfile.id == 1).first()

        if not profile:
            return {
                "status": "error",
                "message": "系統設定不存在",
                "is_service": False
            }

        return {
            "status": "ok",
            "message": "系統運作正常" if profile.is_service else "系統維護中",
            "is_service": profile.is_service
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "is_service": False
        }


@router.get("/functions", summary="取得系統功能選單")
async def get_system_functions(
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得系統功能選單（依照 func_order 排序）

    需要提供 Bearer Token
    """
    # 查詢所有啟用的功能，按 func_order 排序
    functions = db.query(SysFunction).filter(
        SysFunction.is_active == True
    ).order_by(SysFunction.func_order).all()

    # 建立功能字典和樹狀結構
    func_dict = {}
    root_functions = []

    # 第一次遍歷：建立字典
    for func in functions:
        func_dict[func.id] = {
            "id": func.id,
            "func_code": func.func_code,
            "func_cname": func.func_cname,
            "func_ename": func.func_ename,
            "func_type": func.func_type,
            "func_order": func.func_order,
            "func_icon": func.func_icon,
            "func_module_name": func.func_module_name,
            "module_item": func.module_item,
            "upper_func_id": func.upper_func_id,
            "is_mana": func.is_mana,
            "children": []
        }

    # 第二次遍歷：建立樹狀結構
    for func in functions:
        func_data = func_dict[func.id]
        if func.upper_func_id == 0:
            # 根節點
            root_functions.append(func_data)
        elif func.upper_func_id in func_dict:
            # 子節點
            func_dict[func.upper_func_id]["children"].append(func_data)

    return root_functions
