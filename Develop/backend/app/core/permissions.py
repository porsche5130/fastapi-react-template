"""
Permission Check
權限檢查工具
"""

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role_right import RoleRight
from app.models.user_detail import UserDetail


def check_permission(
    db: Session,
    user: UserDetail,
    func_code: str,
    permission_type: str
) -> bool:
    """
    檢查使用者是否擁有特定功能的特定權限

    Args:
        db: 資料庫 Session
        user: 使用者物件
        func_code: 功能代碼
        permission_type: 權限類型 (create/read/update/delete/print/file)

    Returns:
        bool: 是否有權限
    """
    # 取得使用者的所有角色ID
    role_ids: List[int] = user.user_role if isinstance(user.user_role, list) else []

    if not role_ids:
        return False

    # 查詢該使用者的角色是否有此功能的權限
    permission_field = f"is_{permission_type.lower()}"

    rights = db.query(RoleRight).filter(
        RoleRight.user_role_id.in_(role_ids),
        RoleRight.func_code == func_code
    ).all()

    # 只要有任一角色擁有權限即可
    for right in rights:
        if getattr(right, permission_field, False):
            return True

    return False


def require_permission(func_code: str, permission_type: str):
    """
    權限檢查裝飾器

    使用範例:
    @router.post("/organizations")
    @require_permission("organizations", "create")
    async def create_organization(...):
        ...

    Args:
        func_code: 功能代碼
        permission_type: 權限類型 (create/read/update/delete/print/file)

    Raises:
        HTTPException: 401 未授權 或 403 無權限
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            db: Session = kwargs.get('db')
            current_user: UserDetail = kwargs.get('current_user')

            if not db or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授權"
                )

            if not check_permission(db, current_user, func_code, permission_type):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"無權限執行此操作: {func_code} - {permission_type}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
