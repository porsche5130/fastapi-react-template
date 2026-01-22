"""
Dependencies
FastAPI 依賴注入函數
"""

import uuid
import logging
from contextvars import ContextVar
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

logger = logging.getLogger(__name__)

# Context variable for session_id
session_id_ctx: ContextVar[Optional[str]] = ContextVar("session_id", default=None)

# HTTP Bearer Token 驗證
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    取得當前登入使用者

    Args:
        credentials: HTTP Bearer Token
        db: 資料庫 Session

    Returns:
        User: 使用者物件

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

    # 從 payload 提取 session_id 並存入 context
    session_id = payload.get("session_id")
    logger.info(f"Token payload session_id: {session_id}")
    if session_id:
        session_id_ctx.set(session_id)
        logger.info(f"Set session_id to context: {session_id}")
    else:
        # 如果 token 中沒有 session_id（舊 token），產生臨時的 session_id
        temp_session_id = f"legacy-{uuid.uuid4()}"
        session_id_ctx.set(temp_session_id)
        logger.warning(f"JWT token 中沒有 session_id, 使用臨時 session_id: {temp_session_id}")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # 從資料庫查詢使用者
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已停用"
        )

    # 將 session_id 附加到 user 物件上（作為臨時屬性，方便後續日誌記錄使用）
    user.current_session_id = session_id_ctx.get()
    logger.info(f"Attached session_id to user object: {user.current_session_id}")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    取得當前啟用的使用者（已在 get_current_user 驗證）

    Args:
        current_user: 當前使用者

    Returns:
        User: 使用者物件
    """
    return current_user
