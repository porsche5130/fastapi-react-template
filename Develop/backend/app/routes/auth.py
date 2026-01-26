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
from app.services.session_service import SessionService

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

    # 查詢使用者有權限的功能 IDs (is_read = true)
    from app.models.role_rights import RoleRight
    role_ids = user.user_role if isinstance(user.user_role, list) else []

    # 取得使用者所有有讀取權限的功能 IDs
    authorized_function_ids = []
    if role_ids:
        role_rights = db.query(RoleRight).filter(
            RoleRight.user_role_id.in_(role_ids),
            RoleRight.is_read == True
        ).all()

        # 收集所有有權限的 system_function_id (去重)
        authorized_function_ids = list(set([
            rr.system_function_id for rr in role_rights if rr.system_function_id
        ]))

    # 建立 Redis Session（儲存 user_id, role_ids, organization_id, authorized_function_ids 等資料）
    session_created = SessionService.create_session(
        session_id=session_id,
        user_id=user.id,
        role_ids=role_ids,
        organization_id=user.organization_id,
        username=user.username,
        account=user.account,
        authorized_function_ids=authorized_function_ids
    )

    if not session_created:
        logger.error(f"Redis Session 建立失敗: {session_id}")
        # Redis 失敗不影響登入，但記錄警告
        logger.warning("⚠️  Redis 無法使用，Session 將僅依賴 JWT Token")

    # 建立 JWT Token（只放 session_id，不放 user_id）
    access_token = create_access_token(data={
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用者登出

    需要提供 Bearer Token
    刪除 Redis 中的 Session，使 Token 立即失效
    """
    # 取得 session_id
    session_id = getattr(current_user, 'current_session_id', None)

    if session_id:
        # 刪除 Redis Session
        deleted = SessionService.delete_session(session_id)
        if deleted:
            logger.info(f"✅ 使用者登出成功: {current_user.username} (Session: {session_id})")

            # 記錄登出日誌
            try:
                function_id = UserLogService.get_function_id_by_code(db, "logout")
                if function_id:
                    UserLogService.log_logout(
                        db=db,
                        user_id=current_user.id,
                        function_id=function_id,
                        logout_info={
                            "account": current_user.account,
                            "username": current_user.username,
                            "session_id": session_id
                        }
                    )
            except Exception as e:
                logger.error(f"登出日誌記錄失敗: {e}")

            return {"message": "登出成功"}
        else:
            logger.warning(f"Session 刪除失敗或不存在: {session_id}")
            return {"message": "登出成功（Session 已過期）"}
    else:
        logger.warning(f"使用者登出但無 session_id: {current_user.username}")
        return {"message": "登出成功"}
