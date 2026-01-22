"""
Authentication Routes
認證相關路由
"""

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user, session_id_ctx
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserProfile
from app.services.userlog_service import UserLogService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=Token, summary="使用者登入")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    使用者登入

    - **account**: 登入帳號
    - **password**: 密碼

    回傳 JWT Token
    """
    # 查詢使用者
    user = db.query(User).filter(User.account == login_data.account).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )

    # 驗證密碼
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )

    # 檢查帳號是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已停用"
        )

    # 更新最後登入時間與 IP
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    db.commit()

    # 產生 Session ID (UUID)
    session_id = str(uuid.uuid4())

    # 設定 session_id 到 context (用於記錄日誌)
    session_id_ctx.set(session_id)

    # 建立 JWT Token (sub 必須是字串，加入 session_id)
    access_token = create_access_token(data={
        "sub": str(user.id),
        "session_id": session_id
    })

    # 記錄登入日誌
    try:
        function_id = UserLogService.get_function_id_by_code(db, "login")
        if function_id:
            logger.info(f"Recording login log with session_id: {session_id}")
            UserLogService.log_login(
                db=db,
                user_id=user.id,
                function_id=function_id,
                login_info={
                    "account": user.account,
                    "username": user.username,
                    "login_ip": user.last_login_ip,
                    "login_time": user.last_login_at.isoformat() if user.last_login_at else None,
                    "session_id": session_id
                }
            )
            logger.info(f"Login log recorded successfully for user {user.id}")
    except Exception as e:
        # 日誌記錄失敗不影響登入
        logger.error(f"登入日誌記錄失敗: {e}")
        import traceback
        traceback.print_exc()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile, summary="取得當前使用者資訊")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    取得當前登入使用者的個人資料

    需要提供 Bearer Token
    """
    return current_user


@router.post("/logout", summary="使用者登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    使用者登出

    需要提供 Bearer Token
    （前端應清除儲存的 Token）
    """
    return {"message": "登出成功"}
