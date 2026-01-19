"""
Dependencies
FastAPI 依賴注入函數
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user_detail import UserDetail

# HTTP Bearer Token 驗證
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserDetail:
    """
    取得當前登入使用者

    Args:
        credentials: HTTP Bearer Token
        db: 資料庫 Session

    Returns:
        UserDetail: 使用者物件

    Raises:
        HTTPException: 401 未授權
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證認證資訊",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # 從資料庫查詢使用者
    user = db.query(UserDetail).filter(UserDetail.id == user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已停用"
        )

    return user


def get_current_active_user(
    current_user: UserDetail = Depends(get_current_user)
) -> UserDetail:
    """
    取得當前啟用的使用者（已在 get_current_user 驗證）

    Args:
        current_user: 當前使用者

    Returns:
        UserDetail: 使用者物件
    """
    return current_user
